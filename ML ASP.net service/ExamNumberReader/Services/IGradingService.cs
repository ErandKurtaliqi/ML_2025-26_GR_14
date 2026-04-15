using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public interface IGradingService
{
    Task<GradingResult> GradeExamAsync(Stream imageStream, string fileName, string? answerKeyId = null);
    Task<BatchGradingResult> GradeExamsBatchAsync(
        IEnumerable<(Stream Stream, string FileName)> images, 
        string? answerKeyId = null);
    GradingResult CompareAnswers(
        Dictionary<int, string> detectedAnswers, 
        Dictionary<int, string> correctAnswers,
        string? studentId = null,
        string? fileName = null);
}
