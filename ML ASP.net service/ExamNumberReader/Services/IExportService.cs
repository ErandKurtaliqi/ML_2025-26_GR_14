using ExamNumberReader.Models;

namespace ExamNumberReader.Services;

public interface IExportService
{
    byte[] ExportToCsv(IEnumerable<GradingResult> results);
    byte[] ExportToExcel(IEnumerable<GradingResult> results);
}
