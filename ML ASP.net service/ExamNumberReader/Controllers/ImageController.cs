using ExamNumberReader.Models;
using ExamNumberReader.Services;
using Microsoft.AspNetCore.Mvc;

namespace ExamNumberReader.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ImageController : ControllerBase
{
    private readonly IOcrService _ocrService;
    private readonly ILogger<ImageController> _logger;

    private static readonly HashSet<string> AllowedExtensions =
        [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"];

    public ImageController(IOcrService ocrService, ILogger<ImageController> logger)
    {
        _ocrService = ocrService;
        _logger = logger;
    }

    /// <summary>
    /// Upload a single exam image and extract the 5-digit student number.
    /// </summary>
    [HttpPost("extract-number")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(OcrResult), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(OcrResult), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<OcrResult>> ExtractNumber(IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new OcrResult { Success = false, ErrorMessage = "No file uploaded." });

        if (!IsValidImage(file.FileName))
            return BadRequest(new OcrResult
            {
                Success = false,
                ErrorMessage = $"Invalid file type. Allowed: {string.Join(", ", AllowedExtensions)}"
            });

        _logger.LogInformation("Processing image: {FileName} ({Size} bytes)", file.FileName, file.Length);

        using var stream = file.OpenReadStream();
        var result = await _ocrService.ExtractNumberFromImageAsync(stream, file.FileName);

        return Ok(result);
    }

    /// <summary>
    /// Upload multiple exam images and extract 5-digit student numbers from each.
    /// </summary>
    [HttpPost("extract-numbers-batch")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(BatchOcrResult), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(BatchOcrResult), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<BatchOcrResult>> ExtractNumbersBatch(List<IFormFile> files)
    {
        if (files is null || files.Count == 0)
            return BadRequest(new BatchOcrResult { TotalProcessed = 0 });

        var invalidFiles = files.Where(f => !IsValidImage(f.FileName)).Select(f => f.FileName).ToList();
        if (invalidFiles.Count > 0)
        {
            return BadRequest(new BatchOcrResult
            {
                Results = invalidFiles.Select(f => new OcrResult
                {
                    Success = false, FileName = f,
                    ErrorMessage = "Invalid file type"
                }).ToList(),
                TotalProcessed = 0,
                FailedCount = invalidFiles.Count
            });
        }

        _logger.LogInformation("Processing batch of {Count} images", files.Count);

        var images = new List<(Stream Stream, string FileName)>();
        var streams = new List<Stream>();

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

            var result = await _ocrService.ExtractNumbersFromImagesAsync(images);
            return Ok(result);
        }
        finally
        {
            foreach (var s in streams) s.Dispose();
        }
    }

    private static bool IsValidImage(string fileName)
    {
        var ext = Path.GetExtension(fileName).ToLowerInvariant();
        return AllowedExtensions.Contains(ext);
    }
}
