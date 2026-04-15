using System.Globalization;
using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public class AnswerKeyService : IAnswerKeyService
{
    private readonly Dictionary<string, AnswerKey> _answerKeys = new();
    private string? _currentAnswerKeyId;
    private readonly ILogger<AnswerKeyService> _logger;

    public AnswerKeyService(ILogger<AnswerKeyService> logger)
    {
        _logger = logger;
    }

    public async Task<AnswerKeyResponse> UploadFromCsvAsync(Stream csvStream, string? name = null)
    {
        try
        {
            using var reader = new StreamReader(csvStream);
            var content = await reader.ReadToEndAsync();
            var lines = content.Split('\n', StringSplitOptions.RemoveEmptyEntries);

            var answers = new Dictionary<int, string>();

            foreach (var line in lines)
            {
                var trimmedLine = line.Trim();
                if (string.IsNullOrEmpty(trimmedLine)) continue;

                // Skip header if present
                if (trimmedLine.StartsWith("question", StringComparison.OrdinalIgnoreCase) ||
                    trimmedLine.StartsWith("nr", StringComparison.OrdinalIgnoreCase) ||
                    trimmedLine.StartsWith("#", StringComparison.OrdinalIgnoreCase))
                    continue;

                var parts = trimmedLine.Split([',', ';', '\t'], StringSplitOptions.RemoveEmptyEntries);

                if (parts.Length >= 2)
                {
                    // Format: question_number, answer (e.g., "1,A" or "1;B")
                    if (int.TryParse(parts[0].Trim(), out var questionNum))
                    {
                        var answer = parts[1].Trim().ToUpperInvariant();
                        if (IsValidAnswer(answer))
                        {
                            answers[questionNum] = answer;
                        }
                    }
                }
                else if (parts.Length == 1)
                {
                    // Format: just answers in order (e.g., "A" on line 1 means Q1=A)
                    var answer = parts[0].Trim().ToUpperInvariant();
                    if (IsValidAnswer(answer))
                    {
                        answers[answers.Count + 1] = answer;
                    }
                }
            }

            if (answers.Count == 0)
            {
                return new AnswerKeyResponse
                {
                    Success = false,
                    ErrorMessage = "No valid answers found in CSV file. Expected format: 'question_number,answer' or single answer per line."
                };
            }

            var answerKey = new AnswerKey
            {
                Name = name ?? $"Answer Key {DateTime.Now:yyyy-MM-dd HH:mm}",
                Answers = answers
            };

            _answerKeys[answerKey.Id] = answerKey;
            _currentAnswerKeyId = answerKey.Id;

            _logger.LogInformation("Loaded answer key '{Name}' with {Count} answers", answerKey.Name, answers.Count);

            return new AnswerKeyResponse
            {
                Success = true,
                Id = answerKey.Id,
                Name = answerKey.Name,
                AnswerCount = answers.Count,
                Answers = answers
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to parse answer key CSV");
            return new AnswerKeyResponse
            {
                Success = false,
                ErrorMessage = $"Failed to parse CSV: {ex.Message}"
            };
        }
    }

    public AnswerKey? GetAnswerKey(string id)
    {
        return _answerKeys.TryGetValue(id, out var key) ? key : null;
    }

    public AnswerKey? GetCurrentAnswerKey()
    {
        if (_currentAnswerKeyId == null) return null;
        return _answerKeys.TryGetValue(_currentAnswerKeyId, out var key) ? key : null;
    }

    public List<AnswerKey> GetAllAnswerKeys()
    {
        return _answerKeys.Values.OrderByDescending(k => k.CreatedAt).ToList();
    }

    public bool DeleteAnswerKey(string id)
    {
        if (_answerKeys.Remove(id))
        {
            if (_currentAnswerKeyId == id)
                _currentAnswerKeyId = _answerKeys.Keys.FirstOrDefault();
            return true;
        }
        return false;
    }

    public void SetCurrentAnswerKey(string id)
    {
        if (_answerKeys.ContainsKey(id))
            _currentAnswerKeyId = id;
    }

    private static bool IsValidAnswer(string answer)
    {
        return answer.Length == 1 && "ABCD".Contains(answer);
    }
}
