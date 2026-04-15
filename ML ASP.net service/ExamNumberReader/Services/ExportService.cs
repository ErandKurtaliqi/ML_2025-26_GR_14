using System.Text;
using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public class ExportService : IExportService
{
    private const int TotalQuestions = 20;

    public byte[] ExportToCsv(IEnumerable<GradingResult> results)
    {
        var sb = new StringBuilder();

        // Header
        var headers = new List<string> { "Student ID", "File Name" };
        for (int i = 1; i <= TotalQuestions; i++)
        {
            headers.Add($"Q{i}");
        }
        headers.AddRange(["Correct Count", "Total Questions", "Score (%)", "Processed At"]);
        sb.AppendLine(string.Join(",", headers));

        // Data rows
        foreach (var result in results)
        {
            var row = new List<string>
            {
                EscapeCsvField(result.StudentId ?? ""),
                EscapeCsvField(result.FileName ?? "")
            };

            for (int i = 1; i <= TotalQuestions; i++)
            {
                var qResult = result.QuestionResults.FirstOrDefault(q => q.QuestionNumber == i);
                if (qResult != null)
                {
                    var cellValue = qResult.StudentAnswer ?? "-";
                    if (!qResult.IsCorrect && !string.IsNullOrEmpty(qResult.StudentAnswer))
                    {
                        cellValue += $" ({qResult.CorrectAnswer})";
                    }
                    row.Add(EscapeCsvField(cellValue));
                }
                else
                {
                    row.Add("-");
                }
            }

            row.Add(result.CorrectCount.ToString());
            row.Add(result.TotalQuestions.ToString());
            row.Add($"{result.ScorePercentage}%");
            row.Add(result.ProcessedAt.ToString("yyyy-MM-dd HH:mm:ss"));

            sb.AppendLine(string.Join(",", row));
        }

        return Encoding.UTF8.GetPreamble().Concat(Encoding.UTF8.GetBytes(sb.ToString())).ToArray();
    }

    public byte[] ExportToExcel(IEnumerable<GradingResult> results)
    {
        // For Excel export, we create a simple CSV with .xlsx-compatible format
        // A full Excel implementation would require a library like EPPlus or ClosedXML
        // For now, we create a tab-separated file that Excel can open

        var sb = new StringBuilder();

        // Header
        var headers = new List<string> { "Student ID", "File Name" };
        for (int i = 1; i <= TotalQuestions; i++)
        {
            headers.Add($"Q{i}");
        }
        headers.AddRange(["Correct", "Total", "Score %", "Status", "Processed At"]);
        sb.AppendLine(string.Join("\t", headers));

        // Data rows
        foreach (var result in results)
        {
            var row = new List<string>
            {
                result.StudentId ?? "",
                result.FileName ?? ""
            };

            for (int i = 1; i <= TotalQuestions; i++)
            {
                var qResult = result.QuestionResults.FirstOrDefault(q => q.QuestionNumber == i);
                row.Add(qResult?.StudentAnswer ?? "-");
            }

            row.Add(result.CorrectCount.ToString());
            row.Add(result.TotalQuestions.ToString());
            row.Add(result.ScorePercentage.ToString());
            row.Add(result.Success ? "OK" : "FAILED");
            row.Add(result.ProcessedAt.ToString("yyyy-MM-dd HH:mm:ss"));

            sb.AppendLine(string.Join("\t", row));
        }

        // Summary section
        var successResults = results.Where(r => r.Success).ToList();
        if (successResults.Any())
        {
            sb.AppendLine();
            sb.AppendLine("=== SUMMARY ===");
            sb.AppendLine($"Total Exams:\t{results.Count()}");
            sb.AppendLine($"Successful:\t{successResults.Count}");
            sb.AppendLine($"Average Score:\t{Math.Round(successResults.Average(r => r.ScorePercentage), 2)}%");
            sb.AppendLine($"Highest Score:\t{successResults.Max(r => r.ScorePercentage)}%");
            sb.AppendLine($"Lowest Score:\t{successResults.Min(r => r.ScorePercentage)}%");
        }

        return Encoding.UTF8.GetPreamble().Concat(Encoding.UTF8.GetBytes(sb.ToString())).ToArray();
    }

    private static string EscapeCsvField(string field)
    {
        if (field.Contains(',') || field.Contains('"') || field.Contains('\n'))
        {
            return $"\"{field.Replace("\"", "\"\"")}\"";
        }
        return field;
    }
}
