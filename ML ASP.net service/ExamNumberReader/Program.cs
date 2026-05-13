using ExamNumberReader.Services;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Exam Grading System API",
        Version = "v1",
        Description = "Automatic exam grading system using YOLO for answer detection and Keras handwriting recognition for student ID extraction."
    });
});

// CORS configuration
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Register services
builder.Services.AddSingleton<IAnswerKeyService, AnswerKeyService>();
builder.Services.AddSingleton<IExportService, ExportService>();

// HttpClient for YOLO API
builder.Services.AddHttpClient<IYoloService, YoloService>(client =>
{
    client.Timeout = TimeSpan.FromMinutes(2);
});

// HttpClient for injected student ID model API
builder.Services.AddHttpClient<IOcrService, StudentIdService>(client =>
{
    client.Timeout = TimeSpan.FromMinutes(2);
});

builder.Services.AddScoped<IGradingService, GradingService>();

builder.Services.Configure<Microsoft.AspNetCore.Http.Features.FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 50 * 1024 * 1024;
});

var app = builder.Build();

app.UseCors();

app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Exam Grading System API v1");
    c.RoutePrefix = string.Empty;
});

app.MapControllers();

app.Run();
