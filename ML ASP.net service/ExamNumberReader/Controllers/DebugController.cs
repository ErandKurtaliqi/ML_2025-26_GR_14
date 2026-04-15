using ExamNumberReader.Models;
using ExamNumberReader.Services;
using Microsoft.AspNetCore.Mvc;

namespace ExamNumberReader.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DebugController : ControllerBase
{
    private readonly IYoloService _yoloService;
    private readonly IOcrService _ocrService;
    private readonly IAnswerKeyService _answerKeyService;
    private readonly ILogger<DebugController> _logger;

    public DebugController(
        IYoloService yoloService,
        IOcrService ocrService,
        IAnswerKeyService answerKeyService,
        ILogger<DebugController> logger)
    {
        _yoloService = yoloService;
        _ocrService = ocrService;
        _answerKeyService = answerKeyService;
        _logger = logger;
    }

    /// <summary>
    /// Step 1: Call only YOLO API to detect answers
    /// </summary>
    [HttpPost("yolo-detect")]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult<YoloDetectionResult>> YoloDetect(IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new YoloDetectionResult { Success = false, ErrorMessage = "No file uploaded" });

        using var stream = file.OpenReadStream();
        var result = await _yoloService.DetectAnswersAsync(stream);
        return Ok(result);
    }

    /// <summary>
    /// Step 2: Call only .NET OCR to extract student number
    /// </summary>
    [HttpPost("ocr-extract")]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult<OcrResult>> OcrExtract(IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new OcrResult { Success = false, ErrorMessage = "No file uploaded" });

        using var stream = file.OpenReadStream();
        var result = await _ocrService.ExtractNumberFromImageAsync(stream, file.FileName);
        return Ok(result);
    }

    /// <summary>
    /// Step 3: Compare detected answers with answer key
    /// </summary>
    [HttpPost("compare")]
    public ActionResult<ComparisonResult> Compare([FromBody] CompareRequest request)
    {
        var answerKey = request.AnswerKeyId != null
            ? _answerKeyService.GetAnswerKey(request.AnswerKeyId)
            : _answerKeyService.GetCurrentAnswerKey();

        if (answerKey == null)
        {
            return BadRequest(new ComparisonResult
            {
                Success = false,
                ErrorMessage = "No answer key found"
            });
        }

        var results = new List<QuestionComparison>();
        int correctCount = 0;

        foreach (var kvp in answerKey.Answers.OrderBy(k => k.Key))
        {
            var questionNum = kvp.Key;
            var correctAnswer = kvp.Value;
            var detectedAnswer = request.DetectedAnswers.GetValueOrDefault(questionNum);

            var isMatch = !string.IsNullOrEmpty(detectedAnswer) && 
                          detectedAnswer.Equals(correctAnswer, StringComparison.OrdinalIgnoreCase);

            if (isMatch) correctCount++;

            results.Add(new QuestionComparison
            {
                QuestionNumber = questionNum,
                DetectedAnswer = detectedAnswer ?? "-",
                CorrectAnswer = correctAnswer,
                IsMatch = isMatch
            });
        }

        return Ok(new ComparisonResult
        {
            Success = true,
            Comparisons = results,
            TotalQuestions = answerKey.Answers.Count,
            CorrectCount = correctCount,
            ScorePercentage = Math.Round((double)correctCount / answerKey.Answers.Count * 100, 2)
        });
    }

    /// <summary>
    /// Full pipeline: YOLO + OCR + Compare in one call, with individual results
    /// </summary>
    [HttpPost("full-pipeline")]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult<FullPipelineResult>> FullPipeline(IFormFile file, [FromQuery] string? answerKeyId = null)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new FullPipelineResult { Success = false, ErrorMessage = "No file uploaded" });

        var result = new FullPipelineResult { FileName = file.FileName };

        // Copy to memory for multiple reads
        using var memoryStream = new MemoryStream();
        await file.CopyToAsync(memoryStream);
        var imageBytes = memoryStream.ToArray();

        // Step 1: YOLO Detection
        _logger.LogInformation("Step 1: Calling YOLO API...");
        using var yoloStream = new MemoryStream(imageBytes);
        result.YoloResponse = await _yoloService.DetectAnswersAsync(yoloStream);
        _logger.LogInformation("YOLO returned {Count} answers", result.YoloResponse.Answers.Count);

        // Step 2: OCR
        _logger.LogInformation("Step 2: Calling OCR...");
        using var ocrStream = new MemoryStream(imageBytes);
        result.OcrResponse = await _ocrService.ExtractNumberFromImageAsync(ocrStream, file.FileName);
        _logger.LogInformation("OCR returned: {Number}", result.OcrResponse.ExtractedNumber);

        // Step 3: Comparison
        _logger.LogInformation("Step 3: Comparing answers...");
        var answerKey = answerKeyId != null
            ? _answerKeyService.GetAnswerKey(answerKeyId)
            : _answerKeyService.GetCurrentAnswerKey();

        if (answerKey == null)
        {
            result.ComparisonResponse = new ComparisonResult
            {
                Success = false,
                ErrorMessage = "No answer key available"
            };
        }
        else
        {
            var comparisons = new List<QuestionComparison>();
            int correctCount = 0;

            foreach (var kvp in answerKey.Answers.OrderBy(k => k.Key))
            {
                var questionNum = kvp.Key;
                var correctAnswer = kvp.Value;
                var detectedAnswer = result.YoloResponse.Answers.GetValueOrDefault(questionNum);

                var isMatch = !string.IsNullOrEmpty(detectedAnswer) &&
                              detectedAnswer.Equals(correctAnswer, StringComparison.OrdinalIgnoreCase);

                if (isMatch) correctCount++;

                comparisons.Add(new QuestionComparison
                {
                    QuestionNumber = questionNum,
                    DetectedAnswer = detectedAnswer ?? "-",
                    CorrectAnswer = correctAnswer,
                    IsMatch = isMatch
                });
            }

            result.ComparisonResponse = new ComparisonResult
            {
                Success = true,
                Comparisons = comparisons,
                TotalQuestions = answerKey.Answers.Count,
                CorrectCount = correctCount,
                ScorePercentage = Math.Round((double)correctCount / answerKey.Answers.Count * 100, 2)
            };
        }

        result.Success = true;
        return Ok(result);
    }
}

// Request/Response Models
public class CompareRequest
{
    public Dictionary<int, string> DetectedAnswers { get; set; } = new();
    public string? AnswerKeyId { get; set; }
}

public class QuestionComparison
{
    public int QuestionNumber { get; set; }
    public string DetectedAnswer { get; set; } = "";
    public string CorrectAnswer { get; set; } = "";
    public bool IsMatch { get; set; }
}

public class ComparisonResult
{
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public List<QuestionComparison> Comparisons { get; set; } = new();
    public int TotalQuestions { get; set; }
    public int CorrectCount { get; set; }
    public double ScorePercentage { get; set; }
}

public class FullPipelineResult
{
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public string? FileName { get; set; }
    public YoloDetectionResult? YoloResponse { get; set; }
    public OcrResult? OcrResponse { get; set; }
    public ComparisonResult? ComparisonResponse { get; set; }
}
