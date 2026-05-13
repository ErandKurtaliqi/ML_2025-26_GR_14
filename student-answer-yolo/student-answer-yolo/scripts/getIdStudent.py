"""
Read the 5-digit student ID from the left white space of an answer sheet.

High-accuracy pipeline:
  1. Multi-strategy ROI extraction (adaptive + fixed crops)
  2. Multi-strategy color masking (HSV blue, LAB, grayscale, Otsu)
  3. Projection-based + contour-based hybrid digit segmentation
  4. CNN ensemble prediction with confidence voting
  5. Multi-crop voting for final result

Setup:
    py -3.10 train_handwriting_emnist.py
    py -3.10 test1.py

Usage:
    py -3.10 test1.py                           # default image
    py -3.10 test1.py --image path/to/img.jpg   # specific image
    py -3.10 test1.py --batch                    # process ALL train images
    py -3.10 test1.py --debug                    # save debug visualizations
    py -3.10 test1.py --engine ocr               # use EasyOCR instead

`--engine auto` (default): uses handwriting_emnist.keras if present, else EasyOCR.
"""

import argparse
import os
import sys
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import cv2
import numpy as np

from handwriting_paths import HANDWRITING_MODEL_PATH

DEFAULT_IMAGE = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "dataset", "images", "train", "IMG_8163.jpg")
)
_env_model = os.environ.get("HANDWRITING_MODEL", "").strip()
DEFAULT_KERAS_MODEL = (
    os.path.normpath(os.path.expandvars(_env_model))
    if _env_model
    else HANDWRITING_MODEL_PATH
)

EXPECTED_DIGITS = 5


# ═══════════════════════════════════════════════════════════════════════════
# MASK CLEANUP — remove noise, keep only the digit cluster
# ═══════════════════════════════════════════════════════════════════════════

def _clean_mask_cc(mask, min_area=25):
    """Remove small connected components (noise) and keep the digit cluster."""
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n_labels <= 1:
        return mask

    # Collect components above min_area
    comps = []
    for i in range(1, n_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            comps.append((i, area, centroids[i]))

    if not comps:
        return mask

    if len(comps) == 1:
        out = np.zeros_like(mask)
        out[labels == comps[0][0]] = 255
        return out

    # Strategy: find the largest component, then keep all components
    # whose y-center is within a reasonable vertical band of it
    # (digits on a line share similar y coordinates)
    comps.sort(key=lambda c: c[1], reverse=True)  # sort by area descending
    anchor_y = comps[0][2][1]
    h = mask.shape[0]
    y_tolerance = h * 0.15  # 15% of ROI height

    # Keep components in the same horizontal band as the largest component
    band = [c for c in comps if abs(c[2][1] - anchor_y) < y_tolerance]

    if len(band) < 2:
        # Fallback: just remove noise, keep all significant components
        band = comps

    out = np.zeros_like(mask)
    for c in band:
        out[labels == c[0]] = 255
    return out


# ═══════════════════════════════════════════════════════════════════════════
# DIGIT SEGMENTATION
# ═══════════════════════════════════════════════════════════════════════════

def _split_wide_box(box, n_pieces):
    """Split a wide bounding box horizontally into n equal pieces."""
    x, y, w, h = box
    piece_w = w / n_pieces
    return [(int(x + i * piece_w), y, int(piece_w + 0.999), h) for i in range(n_pieces)]


def _merge_nearby_boxes(boxes, gap_ratio=0.35):
    """Merge bounding boxes that overlap or are very close horizontally.
    
    This fixes digits like '0' whose open strokes produce two separate
    contours (left arc + right arc) that should be a single digit.
    """
    if len(boxes) < 2:
        return boxes

    boxes = sorted(boxes, key=lambda b: b[0])  # sort by x
    median_h = float(np.median([b[3] for b in boxes]))
    max_gap = median_h * gap_ratio  # max horizontal gap to merge

    merged = [list(boxes[0])]
    for bx, by, bw, bh in boxes[1:]:
        px, py, pw, ph = merged[-1]
        p_right = px + pw
        # Check if this box overlaps or is close to the previous one
        gap = bx - p_right
        if gap < max_gap:
            # Merge: extend the previous box to cover both
            new_x = min(px, bx)
            new_y = min(py, by)
            new_right = max(p_right, bx + bw)
            new_bottom = max(py + ph, by + bh)
            merged[-1] = [new_x, new_y, new_right - new_x, new_bottom - new_y]
        else:
            merged.append([bx, by, bw, bh])

    return [tuple(b) for b in merged]


def _segment_digits_contour(mask, expected=EXPECTED_DIGITS):
    """Contour-based digit segmentation with smart merging and splitting."""
    # Apply morphological closing to reconnect broken strokes
    # (e.g. open-top zeros that appear as two separate arcs)
    # Use small 3x3 kernel to avoid merging strokes of adjacent digits
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []

    boxes = []
    for c in contours:
        if cv2.contourArea(c) < 40:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if h < 8 or w < 2:
            continue
        boxes.append((x, y, w, h))

    if not boxes:
        return []

    # Filter outliers by height (remove very small noise)
    heights = [b[3] for b in boxes]
    if len(heights) > 1:
        median_h = float(np.median(heights))
        boxes = [b for b in boxes if b[3] > median_h * 0.3]

    if not boxes:
        return []

    # Merge nearby/overlapping boxes (fixes split "0", "6", "8" etc.)
    boxes = _merge_nearby_boxes(boxes)

    median_h = float(np.median([b[3] for b in boxes]))
    typical_w = max(8.0, 0.55 * median_h)

    while len(boxes) < expected:
        idx = max(range(len(boxes)), key=lambda i: boxes[i][2])
        widest = boxes[idx]
        n_pieces = max(2, int(round(widest[2] / typical_w)))
        n_pieces = min(n_pieces, expected - len(boxes) + 1)
        if n_pieces < 2:
            break
        pieces = _split_wide_box(widest, n_pieces)
        boxes = boxes[:idx] + pieces + boxes[idx + 1:]
        if widest[2] / typical_w < 1.4:
            break

    boxes.sort(key=lambda b: b[0])
    return boxes[:expected]


def _segment_digits_projection(mask, expected=EXPECTED_DIGITS):
    """Projection-based segmentation: use vertical projection to find digit columns."""
    h, w = mask.shape
    # Vertical projection (sum of white pixels in each column)
    proj = np.sum(mask > 0, axis=0).astype(float)
    
    if proj.max() < 3:
        return []
    
    # Smooth the projection
    kernel_size = max(3, w // 40)
    if kernel_size % 2 == 0:
        kernel_size += 1
    proj_smooth = np.convolve(proj, np.ones(kernel_size) / kernel_size, mode='same')
    
    # Threshold to find digit regions
    threshold = proj_smooth.max() * 0.1
    in_digit = proj_smooth > threshold
    
    # Find transitions
    segments = []
    start = None
    for i in range(len(in_digit)):
        if in_digit[i] and start is None:
            start = i
        elif not in_digit[i] and start is not None:
            segments.append((start, i))
            start = None
    if start is not None:
        segments.append((start, len(in_digit)))
    
    if not segments:
        return []
    
    # Convert segments to bounding boxes using vertical extent
    boxes = []
    for sx, ex in segments:
        seg_w = ex - sx
        if seg_w < 3:
            continue
        col_mask = mask[:, sx:ex]
        rows = np.where(np.any(col_mask > 0, axis=1))[0]
        if len(rows) < 3:
            continue
        y_start = rows[0]
        y_end = rows[-1] + 1
        boxes.append((sx, y_start, seg_w, y_end - y_start))
    
    if not boxes:
        return []
    
    # Split wide segments
    median_h = float(np.median([b[3] for b in boxes]))
    typical_w = max(8.0, 0.55 * median_h)
    
    while len(boxes) < expected:
        idx = max(range(len(boxes)), key=lambda i: boxes[i][2])
        widest = boxes[idx]
        n_pieces = max(2, int(round(widest[2] / typical_w)))
        n_pieces = min(n_pieces, expected - len(boxes) + 1)
        if n_pieces < 2:
            break
        pieces = _split_wide_box(widest, n_pieces)
        boxes = boxes[:idx] + pieces + boxes[idx + 1:]
        if widest[2] / typical_w < 1.4:
            break
    
    boxes.sort(key=lambda b: b[0])
    return boxes[:expected]


def _segment_digits_hybrid(mask, expected=EXPECTED_DIGITS):
    """Try both contour and projection methods, return best result."""
    contour_boxes = _segment_digits_contour(mask, expected)
    proj_boxes = _segment_digits_projection(mask, expected)
    
    # Prefer the one that gives exactly `expected` boxes
    if len(contour_boxes) == expected and len(proj_boxes) != expected:
        return contour_boxes
    if len(proj_boxes) == expected and len(contour_boxes) != expected:
        return proj_boxes
    if len(contour_boxes) == expected and len(proj_boxes) == expected:
        # Use contour boxes since they tend to be more precise
        return contour_boxes
    
    # Both failed to get exact count, use whichever is closer
    if abs(len(contour_boxes) - expected) <= abs(len(proj_boxes) - expected):
        return contour_boxes
    return proj_boxes


# ═══════════════════════════════════════════════════════════════════════════
# DIGIT CROPPING & CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def _crop_to_mnist(mask, box):
    """Center a digit crop in a square canvas and resize to 28×28 (MNIST-like)."""
    x, y, w, h = box
    mh, mw = mask.shape[:2]
    # Clamp to mask bounds
    x = max(0, x)
    y = max(0, y)
    w = min(w, mw - x)
    h = min(h, mh - y)
    if w <= 0 or h <= 0:
        return np.zeros((28, 28), dtype=np.uint8)
    
    digit = mask[y:y+h, x:x+w]
    side = int(max(w, h) * 1.4)
    side = max(side, 8)
    canvas = np.zeros((side, side), dtype=np.uint8)
    dx = (side - w) // 2
    dy = (side - h) // 2
    canvas[dy:dy+h, dx:dx+w] = digit
    return cv2.resize(canvas, (28, 28), interpolation=cv2.INTER_AREA)


def _classify_digits(model, mask, boxes):
    """Classify each digit and return (id_string, avg_confidence)."""
    if not boxes:
        return "", 0.0

    batch = np.stack([_crop_to_mnist(mask, box) for box in boxes], axis=0)
    net_input = batch.reshape(len(boxes), 28, 28, 1).astype("float32") / 255.0
    predictions = model.predict(net_input, verbose=0)
    digits = np.argmax(predictions, axis=1)
    confidences = np.max(predictions, axis=1)

    detected_id = "".join(str(int(digit)) for digit in digits)
    avg_conf = float(np.mean(confidences)) if len(confidences) else 0.0
    return detected_id, avg_conf


# ═══════════════════════════════════════════════════════════════════════════
# MASK STRATEGIES  —  multiple ways to isolate handwritten ink
# ═══════════════════════════════════════════════════════════════════════════

def _mask_hsv_blue(roi_bgr):
    """HSV blue-ink masking with wide range."""
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    # Wide range for blue pen (covers navy, blue, light blue)
    lower = np.array([85, 15, 15])
    upper = np.array([145, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return mask


def _mask_hsv_blue_tight(roi_bgr):
    """Tighter HSV blue range for cleaner results."""
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([90, 30, 30])
    upper = np.array([135, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    return mask


def _mask_lab_blue(roi_bgr):
    """LAB color space: blue ink has negative b* values (blue-yellow axis)."""
    lab = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    # Blue ink → b channel < 128 (neutral) → lower b means more blue
    # Also should be darker (lower L) than white paper
    blue_mask = ((b < 115) & (l < 200)).astype(np.uint8) * 255
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return blue_mask


def _mask_gray_adaptive(roi_bgr):
    """Adaptive thresholding on grayscale — works for any ink color."""
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    # Blur first to suppress paper texture noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply CLAHE for contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 31, 18)
    # Heavier morphology to remove salt-and-pepper noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return mask


def _mask_otsu(roi_bgr):
    """Otsu thresholding on grayscale."""
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return mask


def _mask_blue_channel_diff(roi_bgr):
    """Isolate blue/dark ink by channel analysis."""
    b, g, r = cv2.split(roi_bgr)
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    # Dark ink on white paper: grayscale < threshold
    dark_enough = gray < 160
    # Blue pen: B channel is dominant OR ink is just dark
    bi = b.astype(int)
    gi = g.astype(int)
    ri = r.astype(int)
    blue_dominant = (bi - ri > 15) & (bi - gi > 5)
    # Combine: dark ink that is either blue-dominant or very dark
    very_dark = gray < 120
    mask = ((blue_dominant & dark_enough) | very_dark).astype(np.uint8) * 255
    # Clean up
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return mask


ALL_MASK_STRATEGIES = [
    ("hsv_blue", _mask_hsv_blue),
    ("hsv_tight", _mask_hsv_blue_tight),
    ("lab_blue", _mask_lab_blue),
    ("gray_adaptive", _mask_gray_adaptive),
    ("otsu", _mask_otsu),
    ("blue_diff", _mask_blue_channel_diff),
]


# ═══════════════════════════════════════════════════════════════════════════
# ROI EXTRACTION  —  multiple crop regions
# ═══════════════════════════════════════════════════════════════════════════

def _get_roi_crops(img):
    """Return multiple ROI crops covering where the student ID might be."""
    h, w = img.shape[:2]
    crops = []
    
    # Crop 1: Primary — left side, middle vertical
    y1, y2 = int(h * 0.28), int(h * 0.60)
    x1, x2 = int(w * 0.02), int(w * 0.42)
    crops.append(("primary", img[y1:y2, x1:x2]))
    
    # Crop 2: Wider vertical range
    y1, y2 = int(h * 0.25), int(h * 0.65)
    x1, x2 = int(w * 0.01), int(w * 0.45)
    crops.append(("wide", img[y1:y2, x1:x2]))
    
    # Crop 3: Tighter focus — common position
    y1, y2 = int(h * 0.35), int(h * 0.55)
    x1, x2 = int(w * 0.03), int(w * 0.35)
    crops.append(("tight", img[y1:y2, x1:x2]))
    
    # Crop 4: Lower third of left side (sometimes ID is lower)
    y1, y2 = int(h * 0.30), int(h * 0.58)
    x1, x2 = int(w * 0.02), int(w * 0.40)
    crops.append(("lower", img[y1:y2, x1:x2]))
    
    return crops


# ═══════════════════════════════════════════════════════════════════════════
# MAIN DETECTION — MULTI-STRATEGY VOTING
# ═══════════════════════════════════════════════════════════════════════════

def detect_handwritten_id_keras(img_path, model, debug=False, debug_dir=None):
    """
    Robust handwritten ID detection with multi-strategy voting.
    
    For EACH ROI crop × EACH mask strategy:
      - Segment digits
      - Classify with CNN
      - Collect (id_string, confidence) candidates
    
    Final answer chosen by majority vote among 5-digit candidates,
    weighted by CNN confidence.
    """
    img = cv2.imread(img_path)
    if img is None:
        return None

    base = os.path.splitext(os.path.basename(img_path))[0] if debug and debug_dir else None
    if debug and debug_dir:
        os.makedirs(debug_dir, exist_ok=True)

    roi_crops = _get_roi_crops(img)
    all_candidates = []  # list of (id_string, confidence, crop_name, strategy_name)

    for crop_name, roi_img in roi_crops:
        for strat_name, mask_fn in ALL_MASK_STRATEGIES:
            try:
                mask = mask_fn(roi_img)
            except Exception:
                continue
            
            # Clean mask with connected component filtering
            mask = _clean_mask_cc(mask, min_area=25)

            # Check if mask has enough content
            white_ratio = np.sum(mask > 0) / max(1, mask.size)
            if white_ratio < 0.0005 or white_ratio > 0.4:
                continue
            
            # Segment digits
            boxes = _segment_digits_hybrid(mask, expected=EXPECTED_DIGITS)
            if len(boxes) < 3:
                continue
            
            # Classify
            id_str, avg_conf = _classify_digits(model, mask, boxes)
            
            if len(id_str) >= 4:
                all_candidates.append((id_str[:5], avg_conf, crop_name, strat_name))
            
            # Save debug for primary crop
            if debug and debug_dir and crop_name == "primary":
                cv2.imwrite(os.path.join(debug_dir, f"{base}_{strat_name}_mask.jpg"), mask)
                debug_img = roi_img.copy()
                for i, box in enumerate(boxes):
                    bx, by, bw, bh = box
                    cv2.rectangle(debug_img, (bx, by), (bx+bw, by+bh), (0, 255, 0), 2)
                cv2.imwrite(os.path.join(debug_dir, f"{base}_{strat_name}_boxes.jpg"), debug_img)

    if not all_candidates:
        return ""

    # ── Voting: prefer 5-digit candidates ──
    five_digit = [(cid, conf, cn, sn) for cid, conf, cn, sn in all_candidates if len(cid) == 5]
    
    if five_digit:
        # Weighted voting: each candidate votes for its ID string, weighted by confidence
        from collections import defaultdict
        vote_scores = defaultdict(float)
        vote_counts = defaultdict(int)
        
        for cid, conf, cn, sn in five_digit:
            vote_scores[cid] += conf
            vote_counts[cid] += 1
        
        # Combine count and confidence for ranking
        best_id = max(vote_scores.keys(),
                      key=lambda k: (vote_counts[k], vote_scores[k]))
        
        if debug:
            print(f"  Voting results for {base or img_path}:")
            sorted_votes = sorted(vote_scores.items(),
                                   key=lambda kv: (vote_counts[kv[0]], kv[1]),
                                   reverse=True)
            for vid, vscore in sorted_votes[:5]:
                print(f"    {vid}: count={vote_counts[vid]}, total_conf={vscore:.2f}")
        
        return best_id
    
    # Fallback: pick highest confidence regardless of digit count
    best = max(all_candidates, key=lambda c: c[1])
    return best[0]


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Read handwritten 5-digit ID (left side).")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Path to answer sheet image")
    parser.add_argument(
        "--engine",
        choices=("auto", "keras", "ocr"),
        default="auto",
        help="auto: use handwriting_emnist.keras if present, else EasyOCR; keras/ocr = force",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_KERAS_MODEL,
        metavar="PATH",
        help=f"Trained .keras file (default: {HANDWRITING_MODEL_PATH} or HANDWRITING_MODEL env)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save ROI / mask (keras) or OCR debug crops (ocr mode)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process ALL images in dataset/images/train",
    )
    args = parser.parse_args()

    debug_dir = os.path.join(SCRIPT_DIR, "test_output") if args.debug else None

    engine = args.engine
    if engine == "auto":
        engine = "keras" if os.path.isfile(args.model) else "ocr"
        if engine == "ocr":
            print(
                f"No model file at:\n  {os.path.abspath(args.model)}\n"
                "— using EasyOCR.\n"
                "Train into that path, copy your .keras there, or set HANDWRITING_MODEL / --model:\n"
                "  py -3.10 train_handwriting_emnist.py\n"
            )

    if engine == "keras":
        if not os.path.isfile(args.model):
            print(
                "No handwriting model at:\n"
                f"  {args.model}\n"
                "Train it (Windows):\n"
                "  py -3.10 train_handwriting_emnist.py\n"
                "Or run with OCR:  py -3.10 test1.py --engine ocr"
            )
            sys.exit(1)
        print(f"Using trained handwriting model: {args.model}")
        import tensorflow as tf
        model = tf.keras.models.load_model(args.model)
    else:
        model = None

    # ── Determine images to process ──
    if args.batch:
        train_dir = os.path.normpath(
            os.path.join(SCRIPT_DIR, "..", "dataset", "images", "train")
        )
        image_paths = sorted(glob.glob(os.path.join(train_dir, "*.jpg")))
        if not image_paths:
            print(f"No images found in {train_dir}")
            sys.exit(1)
        print(f"\nBatch mode: processing {len(image_paths)} images\n")
    else:
        image_path = os.path.normpath(args.image)
        if not os.path.isfile(image_path):
            print(f"Error: image not found: {image_path}")
            sys.exit(1)
        image_paths = [image_path]

    # ── Process each image ──
    results = []
    for img_path in image_paths:
        basename = os.path.basename(img_path)

        if engine == "keras":
            student_id = detect_handwritten_id_keras(
                img_path, model, debug=args.debug, debug_dir=debug_dir
            )
            if not student_id:
                student_id = "UNKNOWN"
        else:
            import easyocr
            from grade_students import extract_student_id

            print("Loading EasyOCR...")
            reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            student_id = extract_student_id(
                img_path, reader, debug=args.debug, debug_dir=debug_dir
            )

        results.append((basename, student_id))
        print(f"  {basename}  ->  {student_id}")

    # ── Summary ──
    print("\n" + "=" * 50)
    print("  DETECTION RESULTS")
    print("=" * 50)
    for basename, sid in results:
        print(f"  {basename:30s}  ->  {sid}")
    print("=" * 50)
    print(f"  Total: {len(results)} images processed")
    unknown = sum(1 for _, s in results if s == "UNKNOWN")
    if unknown:
        print(f"  Unknown: {unknown}")
    print("=" * 50)


if __name__ == "__main__":
    main()
