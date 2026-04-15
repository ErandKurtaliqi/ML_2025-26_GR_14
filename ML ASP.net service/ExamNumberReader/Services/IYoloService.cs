using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public interface IYoloService
{
    Task<YoloDetectionResult> DetectAnswersAsync(Stream imageStream);
    Task<List<YoloDetectionResult>> DetectAnswersBatchAsync(IEnumerable<(Stream Stream, string FileName)> images);
}
