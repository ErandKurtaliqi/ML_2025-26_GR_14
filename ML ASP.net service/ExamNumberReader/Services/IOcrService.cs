using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public interface IOcrService
{
    Task<OcrResult> ExtractNumberFromImageAsync(Stream imageStream, string fileName);
    Task<BatchOcrResult> ExtractNumbersFromImagesAsync(IEnumerable<(Stream Stream, string FileName)> images);
}
