namespace ExamNumberReader.Models;

public class OcrResult
{
    public bool Success { get; set; }
    public string? ExtractedNumber { get; set; }
    public string? RawOcrText { get; set; }
    public double Confidence { get; set; }
    public string? ErrorMessage { get; set; }
    public string? FileName { get; set; }
}

public class BatchOcrResult
{
    public List<OcrResult> Results { get; set; } = [];
    public int TotalProcessed { get; set; }
    public int SuccessCount { get; set; }
    public int FailedCount { get; set; }
}
