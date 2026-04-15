using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public interface IAnswerKeyService
{
    Task<AnswerKeyResponse> UploadFromCsvAsync(Stream csvStream, string? name = null);
    AnswerKey? GetAnswerKey(string id);
    AnswerKey? GetCurrentAnswerKey();
    List<AnswerKey> GetAllAnswerKeys();
    bool DeleteAnswerKey(string id);
    void SetCurrentAnswerKey(string id);
}
