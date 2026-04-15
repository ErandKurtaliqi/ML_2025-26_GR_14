using ExamNumberReader.Models;
using ExamNumberReader.Services;
using Microsoft.AspNetCore.Mvc;

namespace ExamNumberReader.Controllers;

[ApiController]
[Route("api/[controller]")]
public class GradingController : ControllerBase
{
    private readonly IGradingService _gradingService;
    private readonly IAnswerKeyService _answerKeyService;
    private readonly IExportService _exportService;
    private readonly ILogger<GradingController> _logger;

    private static readonly HashSet<string> AllowedImageExtensions =
        [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"];

    public GradingController(
        IGradingService gradingService,
        IAnswerKeyService answerKeyService,
        IExportService exportService,
        ILogger<GradingController> logger)
    {
        _gradingService = gradingService;
        _answerKeyService = answerKeyService;
        _exportService = exportService;
        _logger = logger;
    }

    #region Answer Key Endpoints

    /// <summary>
    /// Upload a CSV file containing the answer key.
    /// Expected format: question_number,answer (e.g., "1,A" or "2,B")
    /// </summary>
    [HttpPost("answer-key")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(AnswerKeyResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(AnswerKeyResponse), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<AnswerKeyResponse>> UploadAnswerKey(
        IFormFile file,
        [FromQuery] string? name = null)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new AnswerKeyResponse
            {
                Success = false,
                ErrorMessage = "No file uploaded."
            });

        var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
        if (ext != ".csv" && ext != ".txt")
            return BadRequest(new AnswerKeyResponse
            {
                Success = false,
                ErrorMessage = "File must be a CSV or TXT file."
            });

        _logger.LogInformation("Uploading answer key: {FileName}", file.FileName);

        using var stream = file.OpenReadStream();
        var result = await _answerKeyService.UploadFromCsvAsync(stream, name ?? file.FileName);

        return result.Success ? Ok(result) : BadRequest(result);
    }

    /// <summary>
    /// Get the current active answer key.
    /// </summary>
    [HttpGet("answer-key/current")]
    [ProducesResponseType(typeof(AnswerKey), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult<AnswerKey> GetCurrentAnswerKey()
    {
        var key = _answerKeyService.GetCurrentAnswerKey();
        if (key == null)
            return NotFound(new { message = "No answer key has been uploaded yet." });
        return Ok(key);
    }

    /// <summary>
    /// Get all uploaded answer keys.
    /// </summary>
    [HttpGet("answer-key")]
    [ProducesResponseType(typeof(List<AnswerKey>), StatusCodes.Status200OK)]
    public ActionResult<List<AnswerKey>> GetAllAnswerKeys()
    {
        return Ok(_answerKeyService.GetAllAnswerKeys());
    }

    /// <summary>
    /// Set an answer key as the current active one.
    /// </summary>
    [HttpPost("answer-key/{id}/activate")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult ActivateAnswerKey(string id)
    {
        var key = _answerKeyService.GetAnswerKey(id);
        if (key == null)
            return NotFound(new { message = "Answer key not found." });

        _answerKeyService.SetCurrentAnswerKey(id);
        return Ok(new { message = "Answer key activated.", id = id, name = key.Name });
    }

    /// <summary>
    /// Delete an answer key.
    /// </summary>
    [HttpDelete("answer-key/{id}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult DeleteAnswerKey(string id)
    {
        if (_answerKeyService.DeleteAnswerKey(id))
            return Ok(new { message = "Answer key deleted." });
        return NotFound(new { message = "Answer key not found." });
    }

    #endregion

    #region Grading Endpoints

    /// <summary>
    /// Grade a single exam image.
    /// </summary>
    [HttpPost("grade")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(GradingResult), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(GradingResult), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<GradingResult>> GradeExam(
        IFormFile file,
        [FromQuery] string? answerKeyId = null)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new GradingResult
            {
                Success = false,
                ErrorMessage = "No file uploaded."
            });

        if (!IsValidImage(file.FileName))
            return BadRequest(new GradingResult
            {
                Success = false,
                ErrorMessage = $"Invalid file type. Allowed: {string.Join(", ", AllowedImageExtensions)}"
            });

        _logger.LogInformation("Grading exam: {FileName}", file.FileName);

        using var stream = file.OpenReadStream();
        var result = await _gradingService.GradeExamAsync(stream, file.FileName, answerKeyId);

        return Ok(result);
    }

    /// <summary>
    /// Grade multiple exam images in batch.
    /// </summary>
    [HttpPost("grade/batch")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(BatchGradingResult), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(BatchGradingResult), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<BatchGradingResult>> GradeExamsBatch(
        List<IFormFile> files,
        [FromQuery] string? answerKeyId = null)
    {
        if (files is null || files.Count == 0)
            return BadRequest(new BatchGradingResult { TotalProcessed = 0 });

        var invalidFiles = files.Where(f => !IsValidImage(f.FileName)).Select(f => f.FileName).ToList();
        if (invalidFiles.Count > 0)
        {
            return BadRequest(new BatchGradingResult
            {
                Results = invalidFiles.Select(f => new GradingResult
                {
                    Success = false,
                    FileName = f,
                    ErrorMessage = "Invalid file type"
                }).ToList(),
                TotalProcessed = 0,
                FailedCount = invalidFiles.Count
            });
        }

        _logger.LogInformation("Grading batch of {Count} exams", files.Count);

        var images = new List<(Stream Stream, string FileName)>();
        var streams = new List<MemoryStream>();

        try
        {
            foreach (var file in files)
            {
                var ms = new MemoryStream();
                await file.CopyToAsync(ms);
                ms.Position = 0;
                streams.Add(ms);
                images.Add((ms, file.FileName));
            }

            var result = await _gradingService.GradeExamsBatchAsync(images, answerKeyId);
            return Ok(result);
        }
        finally
        {
            foreach (var s in streams) s.Dispose();
        }
    }

    #endregion

    #region Export Endpoints

    /// <summary>
    /// Export grading results to CSV.
    /// </summary>
    [HttpPost("export/csv")]
    [ProducesResponseType(typeof(FileContentResult), StatusCodes.Status200OK)]
    public ActionResult ExportToCsv([FromBody] ExportRequest request)
    {
        if (request.Results.Count == 0)
            return BadRequest(new { message = "No results to export." });

        var csvBytes = _exportService.ExportToCsv(request.Results);
        var fileName = $"exam_results_{DateTime.Now:yyyyMMdd_HHmmss}.csv";

        return File(csvBytes, "text/csv", fileName);
    }

    /// <summary>
    /// Export grading results to Excel format.
    /// </summary>
    [HttpPost("export/excel")]
    [ProducesResponseType(typeof(FileContentResult), StatusCodes.Status200OK)]
    public ActionResult ExportToExcel([FromBody] ExportRequest request)
    {
        if (request.Results.Count == 0)
            return BadRequest(new { message = "No results to export." });

        var excelBytes = _exportService.ExportToExcel(request.Results);
        var fileName = $"exam_results_{DateTime.Now:yyyyMMdd_HHmmss}.xls";

        return File(excelBytes, "application/vnd.ms-excel", fileName);
    }

    #endregion

    private static bool IsValidImage(string fileName)
    {
        var ext = Path.GetExtension(fileName).ToLowerInvariant();
        return AllowedImageExtensions.Contains(ext);
    }
}
