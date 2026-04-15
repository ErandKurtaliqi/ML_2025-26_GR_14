using System.Net.Http.Headers;
using System.Text.Json;
using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public class YoloService : IYoloService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<YoloService> _logger;
    private readonly string _yoloApiUrl;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };

    public YoloService(HttpClient httpClient, IConfiguration configuration, ILogger<YoloService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _yoloApiUrl = configuration["YoloApi:BaseUrl"] ?? "http://localhost:8001";
    }

    public async Task<YoloDetectionResult> DetectAnswersAsync(Stream imageStream)
    {
        try
        {
            using var content = new MultipartFormDataContent();
            using var memoryStream = new MemoryStream();
            await imageStream.CopyToAsync(memoryStream);
            memoryStream.Position = 0;

            var fileContent = new ByteArrayContent(memoryStream.ToArray());
            fileContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg");
            content.Add(fileContent, "file", "image.jpg");

            var response = await _httpClient.PostAsync($"{_yoloApiUrl}/detect", content);

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync();
                _logger.LogError("YOLO API returned {StatusCode}: {Body}", response.StatusCode, errorBody);
                return new YoloDetectionResult
                {
                    Success = false,
                    ErrorMessage = $"YOLO API error: {response.StatusCode}"
                };
            }

            var json = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<YoloDetectionResult>(json, JsonOptions);

            return result ?? new YoloDetectionResult
            {
                Success = false,
                ErrorMessage = "Failed to deserialize YOLO response"
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to connect to YOLO API at {Url}", _yoloApiUrl);
            return new YoloDetectionResult
            {
                Success = false,
                ErrorMessage = $"Failed to connect to YOLO API: {ex.Message}"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling YOLO API");
            return new YoloDetectionResult
            {
                Success = false,
                ErrorMessage = ex.Message
            };
        }
    }

    public async Task<List<YoloDetectionResult>> DetectAnswersBatchAsync(
        IEnumerable<(Stream Stream, string FileName)> images)
    {
        var results = new List<YoloDetectionResult>();
        foreach (var (stream, fileName) in images)
        {
            var result = await DetectAnswersAsync(stream);
            results.Add(result);
        }
        return results;
    }
}
