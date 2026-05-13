using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public class GradingService : IGradingService
{
    private readonly IYoloService _yoloService;
    private readonly IOcrService _ocrService;
    private readonly IAnswerKeyService _answerKeyService;
    private readonly ILogger<GradingService> _logger;

    public GradingService(
        IYoloService yoloService,
        IOcrService ocrService,
        IAnswerKeyService answerKeyService,
        ILogger<GradingService> logger)
    {
        _yoloService = yoloService;
        _ocrService = ocrService;
        _answerKeyService = answerKeyService;
        _logger = logger;
    }

    public async Task<GradingResult> GradeExamAsync(Stream imageStream, string fileName, string? answerKeyId = null)
    {
        try
        {
            // Get answer key
            var answerKey = answerKeyId != null 
                ? _answerKeyService.GetAnswerKey(answerKeyId)
                : _answerKeyService.GetCurrentAnswerKey();

            if (answerKey == null)
            {
                return new GradingResult
                {
                    Success = false,
                    FileName = fileName,
                    ErrorMessage = "No answer key available. Please upload an answer key first."
                };
            }

            // Copy stream to memory for multiple reads
            using var memoryStream = new MemoryStream();
            await imageStream.CopyToAsync(memoryStream);
            var imageBytes = memoryStream.ToArray();

            // Detect answers and student ID in parallel. Both services receive their own stream.
            using var yoloStream = new MemoryStream(imageBytes);
            using var studentIdStream = new MemoryStream(imageBytes);

            var yoloTask = _yoloService.DetectAnswersAsync(yoloStream);
            var studentIdTask = _ocrService.ExtractNumberFromImageAsync(studentIdStream, fileName);

            await Task.WhenAll(yoloTask, studentIdTask);

            var yoloResult = await yoloTask;

            if (!yoloResult.Success)
            {
                return new GradingResult
                {
                    Success = false,
                    FileName = fileName,
                    ErrorMessage = $"YOLO detection failed: {yoloResult.ErrorMessage}"
                };
            }

            var studentIdResult = await studentIdTask;
            var studentId = studentIdResult.Success ? studentIdResult.ExtractedNumber : null;

            // Compare answers
            var gradingResult = CompareAnswers(
                yoloResult.Answers, 
                answerKey.Answers, 
                studentId, 
                fileName);

            return gradingResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to grade exam {FileName}", fileName);
            return new GradingResult
            {
                Success = false,
                FileName = fileName,
                ErrorMessage = ex.Message
            };
        }
    }

    public async Task<BatchGradingResult> GradeExamsBatchAsync(
        IEnumerable<(Stream Stream, string FileName)> images,
        string? answerKeyId = null)
    {
        var results = new List<GradingResult>();
        
        foreach (var (stream, fileName) in images)
        {
            using var memoryStream = new MemoryStream();
            await stream.CopyToAsync(memoryStream);
            memoryStream.Position = 0;
            
            var result = await GradeExamAsync(memoryStream, fileName, answerKeyId);
            results.Add(result);
        }

        var successResults = results.Where(r => r.Success).ToList();
        
        return new BatchGradingResult
        {
            Results = results,
            TotalProcessed = results.Count,
            SuccessCount = successResults.Count,
            FailedCount = results.Count - successResults.Count,
            AverageScore = successResults.Count > 0 
                ? Math.Round(successResults.Average(r => r.ScorePercentage), 2)
                : 0,
            AnswerKeyId = answerKeyId ?? _answerKeyService.GetCurrentAnswerKey()?.Id
        };
    }

    public GradingResult CompareAnswers(
        Dictionary<int, string> detectedAnswers,
        Dictionary<int, string> correctAnswers,
        string? studentId = null,
        string? fileName = null)
    {
        var questionResults = new List<QuestionResult>();
        var correctCount = 0;

        // Get all question numbers from the answer key
        var allQuestions = correctAnswers.Keys.OrderBy(q => q).ToList();

        foreach (var questionNum in allQuestions)
        {
            var correctAnswer = correctAnswers.GetValueOrDefault(questionNum);
            var studentAnswer = detectedAnswers.GetValueOrDefault(questionNum);

            string status;
            bool isCorrect = false;

            if (string.IsNullOrEmpty(studentAnswer))
            {
                status = "BLANK";
            }
            else if (studentAnswer == correctAnswer)
            {
                status = "CORRECT";
                isCorrect = true;
                correctCount++;
            }
            else
            {
                status = "WRONG";
            }

            questionResults.Add(new QuestionResult
            {
                QuestionNumber = questionNum,
                StudentAnswer = studentAnswer,
                CorrectAnswer = correctAnswer,
                IsCorrect = isCorrect,
                Status = status
            });
        }

        var totalQuestions = allQuestions.Count;
        var scorePercentage = totalQuestions > 0 
            ? Math.Round((double)correctCount / totalQuestions * 100, 2)
            : 0;

        return new GradingResult
        {
            Success = true,
            StudentId = studentId,
            FileName = fileName,
            DetectedAnswers = detectedAnswers,
            QuestionResults = questionResults,
            CorrectCount = correctCount,
            TotalQuestions = totalQuestions,
            ScorePercentage = scorePercentage
        };
    }
}
