using System.Text.RegularExpressions;
using ExamNumberReader.Models;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;
using Tesseract;

namespace ExamNumberReader.Services;

public partial class TesseractOcrService : IOcrService, IDisposable
{
    private readonly TesseractEngine _engine;
    private readonly InferenceSession _mnistSession;
    private readonly ILogger<TesseractOcrService> _logger;
    private readonly bool _saveDebugImages;
    private readonly string _debugDir;

    private static readonly (double X, double Y, double W, double H, float Thresh, int Dilate)[] Configs =
    [
        // Standard left-center crops
        (0.02, 0.30, 0.40, 0.30, 0.30f, 1),
        (0.02, 0.30, 0.40, 0.30, 0.35f, 1),
        (0.02, 0.30, 0.40, 0.30, 0.35f, 2),
        (0.02, 0.30, 0.40, 0.30, 0.40f, 1),
        (0.02, 0.30, 0.40, 0.30, 0.40f, 2),
        (0.02, 0.30, 0.40, 0.30, 0.45f, 2),
        (0.02, 0.30, 0.40, 0.30, 0.50f, 2),
        (0.02, 0.30, 0.40, 0.30, 0.35f, 3),
        (0.02, 0.30, 0.40, 0.30, 0.40f, 3),
        // Shifted lower (for numbers positioned lower on the page)
        (0.02, 0.35, 0.40, 0.30, 0.35f, 2),
        (0.02, 0.35, 0.40, 0.30, 0.40f, 2),
        (0.02, 0.35, 0.40, 0.30, 0.50f, 2),
        (0.02, 0.38, 0.40, 0.25, 0.40f, 2),
        // No dilation (preserve thin strokes like "9" tail)
        (0.02, 0.30, 0.40, 0.30, 0.35f, 0),
        (0.02, 0.30, 0.40, 0.30, 0.40f, 0),
        (0.02, 0.30, 0.40, 0.30, 0.45f, 0),
        (0.02, 0.30, 0.40, 0.30, 0.50f, 0),
        // Wider captures
        (0.00, 0.25, 0.48, 0.40, 0.35f, 2),
        (0.00, 0.25, 0.48, 0.40, 0.40f, 2),
        (0.00, 0.25, 0.48, 0.40, 0.50f, 2),
        (0.00, 0.25, 0.48, 0.40, 0.40f, 0),
        // Tighter crops
        (0.05, 0.35, 0.30, 0.20, 0.35f, 2),
        (0.05, 0.35, 0.30, 0.20, 0.40f, 2),
        // Low threshold (preserve thin strokes like "7" horizontal bar and "8" loops)
        (0.02, 0.30, 0.40, 0.30, 0.25f, 0),
        (0.02, 0.30, 0.40, 0.30, 0.25f, 1),
        (0.00, 0.25, 0.48, 0.40, 0.30f, 0),
        (0.00, 0.25, 0.48, 0.40, 0.30f, 1),
        // Shifted higher (for numbers positioned higher on the page)
        (0.02, 0.22, 0.40, 0.30, 0.35f, 1),
        (0.02, 0.22, 0.40, 0.30, 0.40f, 2),
        (0.02, 0.25, 0.40, 0.28, 0.35f, 1),
    ];

    public TesseractOcrService(IConfiguration configuration, ILogger<TesseractOcrService> logger)
    {
        _logger = logger;
        _saveDebugImages = configuration.GetValue("Ocr:SaveDebugImages", false);

        var tessDataPath = configuration["Tesseract:TessDataPath"]
            ?? Path.Combine(AppContext.BaseDirectory, "tessdata");
        if (!Directory.Exists(tessDataPath))
            tessDataPath = Path.Combine(Directory.GetCurrentDirectory(), "tessdata");

        _engine = new TesseractEngine(tessDataPath, "eng", EngineMode.Default);
        _engine.SetVariable("tessedit_char_whitelist", "0123456789");

        var modelPath = Path.Combine(AppContext.BaseDirectory, "models", "mnist-12.onnx");
        if (!File.Exists(modelPath))
            modelPath = Path.Combine(Directory.GetCurrentDirectory(), "models", "mnist-12.onnx");

        _mnistSession = new InferenceSession(modelPath);

        _debugDir = Path.Combine(Directory.GetCurrentDirectory(), "debug_crops");
        if (_saveDebugImages)
            Directory.CreateDirectory(_debugDir);
    }

    public async Task<OcrResult> ExtractNumberFromImageAsync(Stream imageStream, string fileName)
    {
        try
        {
            using var memoryStream = new MemoryStream();
            await imageStream.CopyToAsync(memoryStream);
            var imageBytes = memoryStream.ToArray();

            var (mnistResult, mnistPerDigitConf) = TryMnistWithMajorityVoting(imageBytes, fileName);
            var tesseractResult = TryTesseractOcr(imageBytes, fileName);

            _logger.LogInformation("MNIST: {N1} ({C1}%), Tesseract: {N2} ({C2}%)",
                mnistResult?.ExtractedNumber, mnistResult?.Confidence,
                tesseractResult?.ExtractedNumber, tesseractResult?.Confidence);

            var result = FuseResults(mnistResult, mnistPerDigitConf, tesseractResult, fileName);

            return result ?? new OcrResult
            {
                Success = false,
                ErrorMessage = "Could not extract a 5-digit number from the image.",
                FileName = fileName
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing image {FileName}", fileName);
            return new OcrResult
            {
                Success = false,
                ErrorMessage = $"Error processing image: {ex.Message}",
                FileName = fileName
            };
        }
    }

    public async Task<BatchOcrResult> ExtractNumbersFromImagesAsync(
        IEnumerable<(Stream Stream, string FileName)> images)
    {
        var results = new List<OcrResult>();
        foreach (var (stream, fileName) in images)
            results.Add(await ExtractNumberFromImageAsync(stream, fileName));

        return new BatchOcrResult
        {
            Results = results,
            TotalProcessed = results.Count,
            SuccessCount = results.Count(r => r.Success),
            FailedCount = results.Count(r => !r.Success)
        };
    }

    /// <summary>
    /// Fuses MNIST per-digit predictions with Tesseract whole-image result.
    /// Where they agree, confidence is high. Where they disagree and MNIST
    /// confidence is low, prefer Tesseract's digit.
    /// </summary>
    private OcrResult? FuseResults(OcrResult? mnist, float[]? mnistDigitConf,
        OcrResult? tesseract, string fileName)
    {
        if (mnist is not { Success: true })
            return tesseract;
        if (tesseract is not { Success: true } || mnistDigitConf == null
            || tesseract.ExtractedNumber?.Length != 5)
            return mnist;

        var mnistNum = mnist.ExtractedNumber!;
        var tessNum = tesseract.ExtractedNumber!;
        double tessOverallConf = tesseract.Confidence / 100.0;
        var fusedDigits = new char[5];
        double totalConf = 0;

        for (int i = 0; i < 5; i++)
        {
            char mDigit = mnistNum[i];
            char tDigit = tessNum[i];
            float mConf = mnistDigitConf[i];

            if (mDigit == tDigit)
            {
                fusedDigits[i] = mDigit;
                totalConf += Math.Max(mConf, 0.95);
            }
            else if (mConf >= 0.85)
            {
                fusedDigits[i] = mDigit;
                totalConf += mConf;
                _logger.LogInformation("Fuse pos[{Pos}]: MNIST={M}({Conf:F2}) vs Tess={T} -> kept MNIST (high conf)",
                    i, mDigit, mConf, tDigit);
            }
            else if (tessOverallConf > 0.50 && mConf < 0.80)
            {
                fusedDigits[i] = tDigit;
                totalConf += 0.7;
                _logger.LogInformation("Fuse pos[{Pos}]: MNIST={M}({Conf:F2}) vs Tess={T}(tessConf={TC:F2}) -> picked Tesseract",
                    i, mDigit, mConf, tDigit, tessOverallConf);
            }
            else
            {
                fusedDigits[i] = mDigit;
                totalConf += mConf;
                _logger.LogInformation("Fuse pos[{Pos}]: MNIST={M}({Conf:F2}) vs Tess={T}(tessConf={TC:F2}) -> kept MNIST",
                    i, mDigit, mConf, tDigit, tessOverallConf);
            }
        }

        var fusedNumber = new string(fusedDigits);
        var fusedConf = totalConf / 5.0;

        _logger.LogInformation("Fused result: {Number} (MNIST={M}, Tess={T})",
            fusedNumber, mnistNum, tessNum);

        return new OcrResult
        {
            Success = true,
            ExtractedNumber = fusedNumber,
            RawOcrText = $"MNIST:{mnistNum} Tess:{tessNum} -> {fusedNumber}",
            Confidence = Math.Round(fusedConf * 100, 2),
            FileName = fileName
        };
    }

    #region MNIST with Majority Voting

    /// <summary>
    /// Runs MNIST recognition with many preprocessing configs and uses
    /// majority voting per digit position for maximum accuracy.
    /// </summary>
    private (OcrResult? Result, float[]? PerDigitConf) TryMnistWithMajorityVoting(
        byte[] imageBytes, string fileName)
    {
        try
        {
            var allVotes = new List<int[]>();
            var allWeightedConf = new List<float[]>();
            int totalVoters = 0;

            foreach (var (cx, cy, cw, ch, thresh, dilate) in Configs)
            {
                using var region = PrepareNumberRegion(imageBytes, cx, cy, cw, ch, thresh, dilate);

                CollectVotes(region, FindDigitBoundingBoxes(region), imageBytes,
                    fileName, $"cc_t{thresh}_d{dilate}",
                    ref allVotes, ref allWeightedConf, ref totalVoters);

                CollectVotes(region, VerticalProfileSegmentation(region), imageBytes,
                    fileName, $"vp_t{thresh}_d{dilate}",
                    ref allVotes, ref allWeightedConf, ref totalVoters);
            }

            // Morphological closing configs: close gaps in strokes
            foreach (var thresh in new[] { 0.40f, 0.50f })
            {
                using var region = PrepareNumberRegion(imageBytes, 0.02, 0.30, 0.40, 0.30, thresh, 0);
                MorphClose(region, 4);

                CollectVotes(region, VerticalProfileSegmentation(region), imageBytes,
                    fileName, $"vp_close4_t{thresh}",
                    ref allVotes, ref allWeightedConf, ref totalVoters);
            }

            // Gaussian blur configs
            foreach (var thresh in new[] { 0.35f, 0.45f })
            {
                using var region = PrepareNumberRegionWithBlur(imageBytes, 0.02, 0.30, 0.40, 0.30, thresh);

                CollectVotes(region, VerticalProfileSegmentation(region), imageBytes,
                    fileName, $"vp_blur_t{thresh}",
                    ref allVotes, ref allWeightedConf, ref totalVoters);
            }

            if (totalVoters < 1)
                return (null, null);

            var finalDigits = new char[5];
            var finalConf = 0.0;

            for (int pos = 0; pos < 5; pos++)
            {
                int bestDigit = 0;
                float bestScore = -1;

                for (int d = 0; d < 10; d++)
                {
                    // Score = sum of confidences for this digit (confidence-weighted voting)
                    float score = allWeightedConf[pos][d];
                    if (score > bestScore)
                    {
                        bestDigit = d;
                        bestScore = score;
                    }
                }

                finalDigits[pos] = (char)('0' + bestDigit);
                float avgConf = allVotes[pos][bestDigit] > 0
                    ? allWeightedConf[pos][bestDigit] / allVotes[pos][bestDigit]
                    : 0;
                finalConf += avgConf;

                _logger.LogInformation("Vote pos[{Pos}]: winner={Digit} votes={Votes}/{Total} conf={Conf:F3}",
                    pos, bestDigit, allVotes[pos][bestDigit], totalVoters, avgConf);

                if (allVotes[pos][bestDigit] < totalVoters * 0.7)
                {
                    for (int dd = 0; dd < 10; dd++)
                        if (allVotes[pos][dd] > 0)
                            _logger.LogInformation("  -> digit {D}: {V} votes, wConf={C:F3}",
                                dd, allVotes[pos][dd], allWeightedConf[pos][dd]);
                }
            }

            var number = new string(finalDigits);
            var totalAvgConf = finalConf / 5.0;
            var perDigitConf = new float[5];

            for (int pos = 0; pos < 5; pos++)
            {
                int d = finalDigits[pos] - '0';
                perDigitConf[pos] = allVotes[pos][d] > 0
                    ? allWeightedConf[pos][d] / allVotes[pos][d]
                    : 0;
            }

            _logger.LogInformation("Majority vote result: {Number} (avg conf {Conf:F3})", number, totalAvgConf);

            return (new OcrResult
            {
                Success = true,
                ExtractedNumber = number,
                RawOcrText = $"{number} ({totalVoters} voters)",
                Confidence = Math.Round(totalAvgConf * 100, 2),
                FileName = fileName
            }, perDigitConf);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "MNIST majority voting failed for {FileName}", fileName);
            return (null, null);
        }
    }

    private static readonly float[] MnistScales = [20f];
    private static readonly int[] DigitPaddings = [4];

    private void CollectVotes(Image<Rgba32> region, List<Rectangle> boxes,
        byte[] imageBytes, string fileName, string tag,
        ref List<int[]> allVotes, ref List<float[]> allWeightedConf, ref int totalVoters)
    {
        if (boxes.Count > 5)
            boxes = MergeCloseBoxes(boxes, region.Width);
        if (boxes.Count is < 4 or > 6)
            return;
        if (boxes.Count > 5)
            boxes = boxes.Take(5).ToList();
        if (boxes.Count != 5)
            return;

        boxes.Sort((a, b) => a.X.CompareTo(b.X));

        while (allVotes.Count < 5)
        {
            allVotes.Add(new int[10]);
            allWeightedConf.Add(new float[10]);
        }

        var safeName = Path.GetFileNameWithoutExtension(fileName);

        float[] rotations = [0, -7, 7, -12, 12];

        for (int i = 0; i < 5; i++)
        {
            var box = boxes[i];
            int pad = 4;
            int bx = Math.Max(0, box.X - pad);
            int by = Math.Max(0, box.Y - pad);
            int bw = Math.Min(box.Width + pad * 2, region.Width - bx);
            int bh = Math.Min(box.Height + pad * 2, region.Height - by);

            using var digitImage = region.Clone();
            digitImage.Mutate(ctx => ctx.Crop(new Rectangle(bx, by, bw, bh)));

            foreach (var angle in rotations)
            {
                using var rotated = digitImage.Clone();
                if (angle != 0)
                    rotated.Mutate(ctx => ctx.Rotate(angle).EntropyCrop());

                using var mnistReady = PrepareMnistInput(rotated, 20f);

                if (_saveDebugImages && angle == 0)
                {
                    using var ms = new MemoryStream();
                    mnistReady.SaveAsPng(ms);
                    File.WriteAllBytes(Path.Combine(_debugDir, $"{safeName}_{tag}_{i}.png"), ms.ToArray());
                }

                var softmax = GetMnistSoftmax(mnistReady);
                int digit = Array.IndexOf(softmax, softmax.Max());
                float conf = softmax.Max();

                if (conf < 0.95f && (digit == 3 || digit == 5 || digit == 9))
                {
                    float sum359 = softmax[3] + softmax[5] + softmax[9];
                    if (sum359 > 0.2f)
                    {
                        int structural = StructuralDisambiguate359(digitImage);
                        float structBonus = 0.3f;
                        allVotes[i][structural]++;
                        allWeightedConf[i][structural] += softmax[structural] + structBonus;
                    }
                }

                if (conf < 0.97f && (digit == 3 || digit == 7))
                {
                    int structural73 = StructuralDisambiguate73(digitImage);
                    float structBonus = 0.35f;
                    allVotes[i][structural73]++;
                    allWeightedConf[i][structural73] += softmax[structural73] + structBonus;
                }

                if (conf < 0.97f && (digit == 3 || digit == 8))
                {
                    int structural83 = StructuralDisambiguate83(digitImage);
                    float structBonus = 0.35f;
                    allVotes[i][structural83]++;
                    allWeightedConf[i][structural83] += softmax[structural83] + structBonus;
                }

                allVotes[i][digit]++;
                allWeightedConf[i][digit] += conf;
            }
        }

        totalVoters++;
    }

    #endregion

    #region Segmentation Methods

    /// <summary>
    /// Segments digits using vertical projection profile analysis.
    /// Counts dark pixels per column and finds gaps to separate digits.
    /// </summary>
    private static List<Rectangle> VerticalProfileSegmentation(Image<Rgba32> image)
    {
        int width = image.Width, height = image.Height;

        var profile = new int[width];
        for (int x = 0; x < width; x++)
            for (int y = 0; y < height; y++)
                if (image[x, y].R < 128) profile[x]++;

        var segments = new List<(int Start, int End)>();
        bool inDigit = false;
        int segStart = 0;
        int minGap = Math.Max(1, width / 80);

        for (int x = 0; x < width; x++)
        {
            if (profile[x] > 0 && !inDigit)
            { segStart = x; inDigit = true; }
            else if (profile[x] == 0 && inDigit)
            {
                int gapLen = 0;
                for (int gx = x; gx < width && profile[gx] == 0; gx++) gapLen++;
                if (gapLen >= minGap) { segments.Add((segStart, x - 1)); inDigit = false; }
            }
        }
        if (inDigit) segments.Add((segStart, width - 1));

        if (segments.Count < 5)
        {
            var newSegments = new List<(int Start, int End)>();
            int avgWidth = segments.Count > 0 ? segments.Sum(s => s.End - s.Start + 1) / segments.Count : 1;

            foreach (var seg in segments)
            {
                int segWidth = seg.End - seg.Start + 1;
                if (segWidth > avgWidth * 1.7 && newSegments.Count + (segments.Count - newSegments.Count) < 5)
                {
                    int mid = (seg.Start + seg.End) / 2;
                    int bestSplit = mid, minP = int.MaxValue;
                    int range = segWidth / 4;
                    for (int sx = mid - range; sx <= mid + range; sx++)
                        if (sx >= 0 && sx < width && profile[sx] < minP)
                        { minP = profile[sx]; bestSplit = sx; }
                    newSegments.Add((seg.Start, bestSplit));
                    newSegments.Add((bestSplit + 1, seg.End));
                }
                else newSegments.Add(seg);
            }
            segments = newSegments;
        }

        var boxes = new List<Rectangle>();
        foreach (var (start, end) in segments)
        {
            int segW = end - start + 1;
            if (segW < 3) continue;
            int minY = height, maxY = 0;
            for (int x = start; x <= end; x++)
                for (int y = 0; y < height; y++)
                    if (image[x, y].R < 128)
                    { if (y < minY) minY = y; if (y > maxY) maxY = y; }
            if (maxY > minY)
                boxes.Add(new Rectangle(start, minY, segW, maxY - minY + 1));
        }
        return boxes;
    }

    #endregion

    #region MNIST Inference

    private static Image<Rgba32> PrepareMnistInput(Image<Rgba32> digitImage, float targetSize = 20f)
    {
        int side = Math.Max(digitImage.Width, digitImage.Height);
        float scale = targetSize / side;
        int newW = Math.Max((int)(digitImage.Width * scale), 1);
        int newH = Math.Max((int)(digitImage.Height * scale), 1);

        digitImage.Mutate(ctx => ctx.Resize(newW, newH));

        var canvas = new Image<Rgba32>(28, 28, Color.White);
        int offsetX = (28 - digitImage.Width) / 2;
        int offsetY = (28 - digitImage.Height) / 2;
        canvas.Mutate(ctx => ctx.DrawImage(digitImage, new Point(offsetX, offsetY), 1f));
        return canvas;
    }

    private (int Digit, float Confidence) RunMnistInference(Image<Rgba32> image28x28)
    {
        var softmax = GetMnistSoftmax(image28x28);
        int bestDigit = Array.IndexOf(softmax, softmax.Max());
        return (bestDigit, softmax.Max());
    }

    private float[] GetMnistSoftmax(Image<Rgba32> image28x28)
    {
        var inputTensor = new DenseTensor<float>([1, 1, 28, 28]);

        for (int y = 0; y < 28; y++)
            for (int x = 0; x < 28; x++)
                inputTensor[0, 0, y, x] = 1.0f - (image28x28[x, y].R / 255.0f);

        var inputName = _mnistSession.InputMetadata.Keys.First();
        using var results = _mnistSession.Run([NamedOnnxValue.CreateFromTensor(inputName, inputTensor)]);

        var output = results.First().AsEnumerable<float>().ToArray();
        var maxVal = output.Max();
        var expSum = output.Sum(v => MathF.Exp(v - maxVal));
        return output.Select(v => MathF.Exp(v - maxVal) / expSum).ToArray();
    }

    private int StructuralDisambiguate359(Image<Rgba32> digitCrop)
    {
        int w = digitCrop.Width, h = digitCrop.Height;
        int midY = h / 2;

        int upperInk = 0, lowerInk = 0;
        int lowerLeftInk = 0, lowerRightInk = 0;
        int upperLeftInk = 0, upperRightInk = 0;
        int midX = w / 2;

        for (int py = 0; py < h; py++)
            for (int px = 0; px < w; px++)
            {
                if (digitCrop[px, py].R >= 128) continue;
                if (py < midY)
                {
                    upperInk++;
                    if (px < midX) upperLeftInk++;
                    else upperRightInk++;
                }
                else
                {
                    lowerInk++;
                    if (px < midX) lowerLeftInk++;
                    else lowerRightInk++;
                }
            }

        if (upperInk + lowerInk == 0) return 5;

        float upperRatio = (float)upperInk / (upperInk + lowerInk);
        float lowerRightRatio = lowerInk > 0 ? (float)lowerRightInk / lowerInk : 0.5f;

        _logger.LogDebug("Structural: upperRatio={U:F2}, lowerRightRatio={R:F2}, upperLR={UL}/{UR}, lowerLR={LL}/{LR}",
            upperRatio, lowerRightRatio, upperLeftInk, upperRightInk, lowerLeftInk, lowerRightInk);

        // "9": heavy upper ink (loop), lower ink concentrated on right (tail descends right)
        // "3": more balanced upper/lower, ink on right for both halves
        // "5": horizontal bar at top, curve at bottom center-right

        if (upperRatio > 0.45f && lowerRightRatio > 0.55f)
            return 9;
        if (upperRatio > 0.5f && lowerRightRatio < 0.45f)
            return 5;
        return 3;
    }

    /// <summary>
    /// Disambiguates "7" vs "3":
    /// - "7" has a strong horizontal stroke in the top ~20% and very little ink in the lower-left
    /// - "3" has curves on the right side with ink spread more evenly vertically
    /// </summary>
    private int StructuralDisambiguate73(Image<Rgba32> digitCrop)
    {
        int w = digitCrop.Width, h = digitCrop.Height;
        int topBand = Math.Max(1, h / 5);

        int topInk = 0, totalInk = 0;
        int lowerLeftInk = 0, lowerRightInk = 0;
        int midX = w / 2, midY = h / 2;

        for (int py = 0; py < h; py++)
            for (int px = 0; px < w; px++)
            {
                if (digitCrop[px, py].R >= 128) continue;
                totalInk++;
                if (py < topBand) topInk++;
                if (py >= midY)
                {
                    if (px < midX) lowerLeftInk++;
                    else lowerRightInk++;
                }
            }

        if (totalInk == 0) return 3;

        float topDensity = (float)topInk / (topBand * w);
        float lowerLeftRatio = (lowerLeftInk + lowerRightInk) > 0
            ? (float)lowerLeftInk / (lowerLeftInk + lowerRightInk) : 0.5f;

        int topRowInkSpan = 0;
        for (int px = 0; px < w; px++)
        {
            for (int py = 0; py < topBand; py++)
            {
                if (digitCrop[px, py].R < 128) { topRowInkSpan++; break; }
            }
        }
        float topSpanRatio = (float)topRowInkSpan / w;

        _logger.LogDebug("Struct73: topDensity={TD:F3}, topSpan={TS:F2}, lowerLeftRatio={LL:F2}",
            topDensity, topSpanRatio, lowerLeftRatio);

        // "7" has a wide horizontal bar at top (high span) and descends right (low lower-left ink)
        if (topSpanRatio > 0.5f && lowerLeftRatio < 0.35f)
            return 7;
        // "7" has high top density from the horizontal bar
        if (topDensity > 0.15f && topSpanRatio > 0.4f && lowerLeftRatio < 0.4f)
            return 7;

        return 3;
    }

    /// <summary>
    /// Disambiguates "8" vs "3":
    /// - "8" has two closed loops, so ink appears on BOTH left and right sides
    /// - "3" has curves opening to the left, so very little ink on the left side
    /// </summary>
    private int StructuralDisambiguate83(Image<Rgba32> digitCrop)
    {
        int w = digitCrop.Width, h = digitCrop.Height;
        int leftStrip = Math.Max(1, w / 4);

        int leftInk = 0, rightInk = 0, totalInk = 0;

        for (int py = 0; py < h; py++)
            for (int px = 0; px < w; px++)
            {
                if (digitCrop[px, py].R >= 128) continue;
                totalInk++;
                if (px < leftStrip) leftInk++;
                else if (px >= w - leftStrip) rightInk++;
            }

        if (totalInk == 0) return 3;

        float leftRatio = (float)leftInk / totalInk;
        float rightRatio = (float)rightInk / totalInk;

        int midY = h / 2;
        int midBand = Math.Max(1, h / 6);
        int midLeftInk = 0;
        for (int py = midY - midBand; py <= midY + midBand && py < h; py++)
        {
            if (py < 0) continue;
            for (int px = 0; px < leftStrip; px++)
                if (digitCrop[px, py].R < 128) midLeftInk++;
        }

        _logger.LogDebug("Struct83: leftRatio={L:F3}, rightRatio={R:F3}, midLeftInk={ML}",
            leftRatio, rightRatio, midLeftInk);

        // "8" has significant left-side ink (closed loops touch the left edge)
        if (leftRatio > 0.12f)
            return 8;
        // "8" has ink at the mid-left where the two loops meet
        if (midLeftInk > 3)
            return 8;

        return 3;
    }

    #endregion

    #region Tesseract Fallback

    private OcrResult? TryTesseractOcr(byte[] imageBytes, string fileName)
    {
        OcrResult? best = null;
        double bestConf = -1;

        var data = PreprocessFullImage(imageBytes, 0.02, 0.30, 0.40, 0.30, 0.4f);
        foreach (var mode in new[] { PageSegMode.SingleLine, PageSegMode.SingleWord })
        {
            try
            {
                using var pix = Pix.LoadFromMemory(data);
                using var page = _engine.Process(pix, mode);
                var text = page.GetText().Trim();
                var conf = page.GetMeanConfidence();
                var num = ExtractFiveDigitNumber(text);
                if (num != null && conf > bestConf)
                {
                    bestConf = conf;
                    best = new OcrResult
                    {
                        Success = true, ExtractedNumber = num, RawOcrText = text,
                        Confidence = Math.Round(conf * 100, 2), FileName = fileName
                    };
                }
            }
            catch { /* try next */ }
        }
        return best;
    }

    #endregion

    #region Image Processing

    private static Image<Rgba32> PrepareNumberRegion(byte[] imageBytes,
        double cropX, double cropY, double cropW, double cropH, float threshold, int dilateRadius)
    {
        var image = Image.Load<Rgba32>(imageBytes);

        int x = (int)(image.Width * cropX);
        int y = (int)(image.Height * cropY);
        int w = (int)(image.Width * cropW);
        int h = (int)(image.Height * cropH);
        w = Math.Min(w, image.Width - x);
        h = Math.Min(h, image.Height - y);

        image.Mutate(ctx =>
        {
            ctx.Crop(new Rectangle(x, y, w, h));
            ctx.Grayscale();
            ctx.Contrast(1.5f);
            ctx.BinaryThreshold(threshold);
        });

        if (dilateRadius > 0) Dilate(image, dilateRadius);
        AutoTrim(image, 5);
        return image;
    }

    private static Image<Rgba32> PrepareNumberRegionWithBlur(byte[] imageBytes,
        double cropX, double cropY, double cropW, double cropH, float threshold)
    {
        var image = Image.Load<Rgba32>(imageBytes);

        int x = (int)(image.Width * cropX);
        int y = (int)(image.Height * cropY);
        int w = (int)(image.Width * cropW);
        int h = (int)(image.Height * cropH);
        w = Math.Min(w, image.Width - x);
        h = Math.Min(h, image.Height - y);

        image.Mutate(ctx =>
        {
            ctx.Crop(new Rectangle(x, y, w, h));
            ctx.Grayscale();
            ctx.Contrast(1.5f);
            ctx.GaussianBlur(2f);
            ctx.BinaryThreshold(threshold);
        });

        Dilate(image, 1);
        AutoTrim(image, 5);
        return image;
    }

    private static void Dilate(Image<Rgba32> image, int radius)
    {
        var copy = image.Clone();
        var black = new Rgba32(0, 0, 0, 255);
        int r2 = radius * radius;

        for (int py = 0; py < copy.Height; py++)
            for (int px = 0; px < copy.Width; px++)
            {
                if (copy[px, py].R >= 128) continue;
                for (int dy = -radius; dy <= radius; dy++)
                    for (int dx = -radius; dx <= radius; dx++)
                    {
                        if (dx * dx + dy * dy > r2) continue;
                        int nx = px + dx, ny = py + dy;
                        if (nx >= 0 && nx < image.Width && ny >= 0 && ny < image.Height)
                            image[nx, ny] = black;
                    }
            }
    }

    private static void Erode(Image<Rgba32> image, int radius)
    {
        var copy = image.Clone();
        var white = new Rgba32(255, 255, 255, 255);
        int r2 = radius * radius;

        for (int py = 0; py < copy.Height; py++)
            for (int px = 0; px < copy.Width; px++)
            {
                if (copy[px, py].R >= 128) continue;
                bool hasWhiteNeighbor = false;
                for (int dy = -radius; dy <= radius && !hasWhiteNeighbor; dy++)
                    for (int dx = -radius; dx <= radius && !hasWhiteNeighbor; dx++)
                    {
                        if (dx * dx + dy * dy > r2) continue;
                        int nx = px + dx, ny = py + dy;
                        if (nx < 0 || nx >= copy.Width || ny < 0 || ny >= copy.Height ||
                            copy[nx, ny].R >= 128)
                            hasWhiteNeighbor = true;
                    }
                if (hasWhiteNeighbor)
                    image[px, py] = white;
            }
    }

    /// <summary>Morphological close: dilate then erode, closing gaps in strokes.</summary>
    private static void MorphClose(Image<Rgba32> image, int radius)
    {
        Dilate(image, radius);
        Erode(image, radius);
    }

    private static byte[] PreprocessFullImage(byte[] imageBytes,
        double cropX, double cropY, double cropW, double cropH, float threshold)
    {
        using var image = PrepareNumberRegion(imageBytes, cropX, cropY, cropW, cropH, threshold, 1);
        image.Mutate(ctx =>
        {
            int targetH = 80;
            float s = (float)targetH / image.Height;
            ctx.Resize(Math.Max((int)(image.Width * s), 200), targetH);
            ctx.Pad(image.Width + 40, image.Height + 40, Color.White);
        });
        using var outputStream = new MemoryStream();
        image.SaveAsPng(outputStream);
        return outputStream.ToArray();
    }

    private static void AutoTrim(Image<Rgba32> image, int margin)
    {
        int minX = image.Width, minY = image.Height, maxX = 0, maxY = 0;
        for (int py = 0; py < image.Height; py++)
            for (int px = 0; px < image.Width; px++)
                if (image[px, py].R < 200)
                { if (px < minX) minX = px; if (py < minY) minY = py; if (px > maxX) maxX = px; if (py > maxY) maxY = py; }
        if (maxX <= minX || maxY <= minY) return;
        int trimX = Math.Max(0, minX - margin);
        int trimY = Math.Max(0, minY - margin);
        int trimW = Math.Min(image.Width - trimX, maxX - minX + margin * 2);
        int trimH = Math.Min(image.Height - trimY, maxY - minY + margin * 2);
        if (trimW > 10 && trimH > 10)
            image.Mutate(ctx => ctx.Crop(new Rectangle(trimX, trimY, trimW, trimH)));
    }

    private static List<Rectangle> FindDigitBoundingBoxes(Image<Rgba32> image)
    {
        int width = image.Width, height = image.Height;
        var visited = new bool[width, height];
        var boxes = new List<Rectangle>();
        int minArea = Math.Max(8, (int)(width * height * 0.001));

        for (int py = 0; py < height; py++)
            for (int px = 0; px < width; px++)
            {
                if (visited[px, py] || image[px, py].R > 128) { visited[px, py] = true; continue; }
                int bMinX = px, bMaxX = px, bMinY = py, bMaxY = py, area = 0;
                var queue = new Queue<(int, int)>();
                queue.Enqueue((px, py));
                visited[px, py] = true;

                while (queue.Count > 0)
                {
                    var (cx, cy) = queue.Dequeue();
                    area++;
                    if (cx < bMinX) bMinX = cx; if (cx > bMaxX) bMaxX = cx;
                    if (cy < bMinY) bMinY = cy; if (cy > bMaxY) bMaxY = cy;
                    for (int dy = -1; dy <= 1; dy++)
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            int nx = cx + dx, ny = cy + dy;
                            if (nx < 0 || nx >= width || ny < 0 || ny >= height || visited[nx, ny]) continue;
                            visited[nx, ny] = true;
                            if (image[nx, ny].R <= 128) queue.Enqueue((nx, ny));
                        }
                }
                if (area >= minArea)
                    boxes.Add(new Rectangle(bMinX, bMinY, bMaxX - bMinX + 1, bMaxY - bMinY + 1));
            }
        return boxes;
    }

    private static List<Rectangle> MergeCloseBoxes(List<Rectangle> boxes, int imageWidth)
    {
        boxes.Sort((a, b) => a.X.CompareTo(b.X));
        double mergeThreshold = imageWidth * 0.03;
        var merged = new List<Rectangle>();
        var used = new bool[boxes.Count];

        for (int i = 0; i < boxes.Count; i++)
        {
            if (used[i]) continue;
            var current = boxes[i];
            for (int j = i + 1; j < boxes.Count; j++)
            {
                if (used[j]) continue;
                if (boxes[j].X < current.X + current.Width + mergeThreshold)
                {
                    int nx = Math.Min(current.X, boxes[j].X);
                    int ny = Math.Min(current.Y, boxes[j].Y);
                    int nr = Math.Max(current.X + current.Width, boxes[j].X + boxes[j].Width);
                    int nb = Math.Max(current.Y + current.Height, boxes[j].Y + boxes[j].Height);
                    current = new Rectangle(nx, ny, nr - nx, nb - ny);
                    used[j] = true;
                }
            }
            merged.Add(current);
        }
        merged.Sort((a, b) => a.X.CompareTo(b.X));
        return merged;
    }

    #endregion

    private static string? ExtractFiveDigitNumber(string ocrText)
    {
        var cleaned = NonDigitRegex().Replace(ocrText, "");
        if (cleaned.Length == 5) return cleaned;
        var match = FiveDigitMatchRegex().Match(cleaned);
        if (match.Success) return match.Value;
        if (cleaned.Length > 5) return cleaned[..5];
        return null;
    }

    [GeneratedRegex(@"[^0-9]")]
    private static partial Regex NonDigitRegex();

    [GeneratedRegex(@"\d{5}")]
    private static partial Regex FiveDigitMatchRegex();

    public void Dispose()
    {
        _engine?.Dispose();
        _mnistSession?.Dispose();
        GC.SuppressFinalize(this);
    }
}
