using System.Net.Http.Headers;
using System.Text.Json;
using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public class StudentIdService : IOcrService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<StudentIdService> _logger;
    private readonly string _studentIdApiUrl;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };

    public StudentIdService(HttpClient httpClient, IConfiguration configuration, ILogger<StudentIdService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        var baseUrl = configuration["YoloApi:BaseUrl"] ?? "http://localhost:8001";
        _studentIdApiUrl = $"{baseUrl.TrimEnd('/')}/student-id";
    }

    public async Task<OcrResult> ExtractNumberFromImageAsync(Stream imageStream, string fileName)
    {
        try
        {
            using var content = new MultipartFormDataContent();
            using var memoryStream = new MemoryStream();
            await imageStream.CopyToAsync(memoryStream);
            memoryStream.Position = 0;

            var fileContent = new ByteArrayContent(memoryStream.ToArray());
            fileContent.Headers.ContentType = new MediaTypeHeaderValue(GetContentType(fileName));
            content.Add(fileContent, "file", string.IsNullOrWhiteSpace(fileName) ? "image.jpg" : fileName);

            var response = await _httpClient.PostAsync(_studentIdApiUrl, content);
            var body = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("Student ID API returned {StatusCode}: {Body}", response.StatusCode, body);
                return new OcrResult
                {
                    Success = false,
                    FileName = fileName,
                    ErrorMessage = $"Student ID API error: {response.StatusCode}"
                };
            }

            var result = JsonSerializer.Deserialize<OcrResult>(body, JsonOptions);
            return result ?? new OcrResult
            {
                Success = false,
                FileName = fileName,
                ErrorMessage = "Failed to deserialize student ID response"
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to connect to Student ID API at {Url}", _studentIdApiUrl);
            return new OcrResult
            {
                Success = false,
                FileName = fileName,
                ErrorMessage = $"Failed to connect to Student ID API: {ex.Message}"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling Student ID API for {FileName}", fileName);
            return new OcrResult
            {
                Success = false,
                FileName = fileName,
                ErrorMessage = ex.Message
            };
        }
    }

    public async Task<BatchOcrResult> ExtractNumbersFromImagesAsync(
        IEnumerable<(Stream Stream, string FileName)> images)
    {
        var tasks = images.Select(async image =>
        {
            using var memoryStream = new MemoryStream();
            await image.Stream.CopyToAsync(memoryStream);
            memoryStream.Position = 0;
            return await ExtractNumberFromImageAsync(memoryStream, image.FileName);
        });

        var results = (await Task.WhenAll(tasks)).ToList();

        return new BatchOcrResult
        {
            Results = results,
            TotalProcessed = results.Count,
            SuccessCount = results.Count(r => r.Success),
            FailedCount = results.Count(r => !r.Success)
        };
    }

    private static string GetContentType(string fileName)
    {
        return Path.GetExtension(fileName).ToLowerInvariant() switch
        {
            ".png" => "image/png",
            ".bmp" => "image/bmp",
            ".tif" or ".tiff" => "image/tiff",
            _ => "image/jpeg"
        };
    }
}
