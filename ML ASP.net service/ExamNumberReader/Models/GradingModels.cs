namespace ExamNumberReader.Models;

public class AnswerKey
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = "Default";
    public Dictionary<int, string> Answers { get; set; } = new();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class DetectedAnswer
{
    public int Question { get; set; }
    public string Answer { get; set; } = "";
    public double Confidence { get; set; }
}

public class YoloDetectionResult
{
    public bool Success { get; set; }
    public Dictionary<int, string> Answers { get; set; } = new();
    public List<DetectedAnswer> DetectedAnswers { get; set; } = new();
    public int TotalDetections { get; set; }
    public string Method { get; set; } = "";
    public string? ErrorMessage { get; set; }
}

public class QuestionResult
{
    public int QuestionNumber { get; set; }
    public string? StudentAnswer { get; set; }
    public string? CorrectAnswer { get; set; }
    public bool IsCorrect { get; set; }
    public string Status { get; set; } = ""; // CORRECT, WRONG, BLANK
}

public class GradingResult
{
    public bool Success { get; set; }
    public string? StudentId { get; set; }
    public string? FileName { get; set; }
    public Dictionary<int, string> DetectedAnswers { get; set; } = new();
    public List<QuestionResult> QuestionResults { get; set; } = new();
    public int CorrectCount { get; set; }
    public int TotalQuestions { get; set; }
    public double ScorePercentage { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
}

public class BatchGradingResult
{
    public List<GradingResult> Results { get; set; } = new();
    public int TotalProcessed { get; set; }
    public int SuccessCount { get; set; }
    public int FailedCount { get; set; }
    public double AverageScore { get; set; }
    public string? AnswerKeyId { get; set; }
}

public class UploadAnswerKeyRequest
{
    public string? Name { get; set; }
}

public class AnswerKeyResponse
{
    public bool Success { get; set; }
    public string? Id { get; set; }
    public string? Name { get; set; }
    public int AnswerCount { get; set; }
    public Dictionary<int, string>? Answers { get; set; }
    public string? ErrorMessage { get; set; }
}

public class ExportRequest
{
    public List<GradingResult> Results { get; set; } = new();
    public string Format { get; set; } = "csv"; // csv or excel
}
