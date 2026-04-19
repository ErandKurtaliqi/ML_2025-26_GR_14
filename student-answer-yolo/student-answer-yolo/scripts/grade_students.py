"""
Student Answer Sheet Grading System
====================================
1. Detects X marks using YOLO model
2. Maps each X to a (question, option) using table contour + line detection
3. Reads the 5-digit student ID from the left side using EasyOCR
4. Compares answers against an answer key
5. Saves results to CSV

Usage:
    python scripts/grade_students.py                         # process all images in dataset/images/train
    python scripts/grade_students.py --image path/to/img.jpg # process a single image
    python scripts/grade_students.py --debug                 # save debug visualizations
    python scripts/grade_students.py --key B,C,B,A,B,...     # provide answer key (20 answers)
"""

import os
import sys
import csv
import argparse
import re
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr

MODEL_PATH = "runs/detect/runs/student_answer_v2/weights/best.pt"
NUM_ROWS = 20
NUM_COLS = 4
OPTIONS = ["A", "B", "C", "D"]
RESULTS_CSV = "results.csv"
DEBUG_DIR = "debug_output"

ANSWER_KEY = None 



def find_table_rect(img):
    """
    Find the bounding rectangle of the answer table.
    Uses contour detection to find the large rectangular grid area.
    Returns (x, y, w, h) or None.
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold to get clean binary image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 21, 10)

    # Find external contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_rect = None
    best_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 0.01 * h * w or area > 0.5 * h * w:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = bw / bh if bh > 0 else 0
        if 0.2 < aspect < 1.5 and bh > h * 0.15 and area > best_area:
            best_area = area
            best_rect = (x, y, bw, bh)

    return best_rect


def detect_vertical_lines(img, table_rect):
    """
    Detect vertical grid lines within the table to find actual column boundaries.
    Returns sorted list of x-coordinates of vertical lines, or None if not enough found.
    """
    tx, ty, tw, th = table_rect
    
    # Crop table region with some padding
    pad = 10
    x1 = max(0, tx - pad)
    y1 = max(0, ty - pad)
    x2 = min(img.shape[1], tx + tw + pad)
    y2 = min(img.shape[0], ty + th + pad)
    
    table_crop = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(table_crop, cv2.COLOR_BGR2GRAY)
    
    # Use morphological operations to isolate vertical lines
    # Create a kernel that is tall and thin (vertical)
    vert_kernel_len = max(th // 5, 30)
    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vert_kernel_len))
    
    # Apply threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Extract vertical lines
    vert_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vert_kernel, iterations=2)
    
    # Find contours of vertical lines
    contours, _ = cv2.findContours(vert_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    line_xs = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        # Vertical lines should be tall relative to width
        if ch > th * 0.3 and cw < tw * 0.1:
            # Use center x, adjusted back to image coordinates
            center_x = x1 + x + cw // 2
            line_xs.append(center_x)
    
    line_xs.sort()
    
    # Merge lines that are very close together (within 2% of table width)
    if line_xs:
        merge_thresh = tw * 0.02
        merged = [line_xs[0]]
        for lx in line_xs[1:]:
            if lx - merged[-1] > merge_thresh:
                merged.append(lx)
            else:
                merged[-1] = (merged[-1] + lx) // 2
        line_xs = merged
    
    # We expect 6 vertical lines: left edge | Dt. | A | B | C | D | right edge
    if len(line_xs) >= 5:
        return line_xs
    
    return None


def detect_horizontal_lines(img, table_rect):
    """
    Detect horizontal grid lines within the table to find actual row boundaries.
    Returns sorted list of y-coordinates, or None if not enough found.
    """
    tx, ty, tw, th = table_rect
    
    pad = 10
    x1 = max(0, tx - pad)
    y1 = max(0, ty - pad)
    x2 = min(img.shape[1], tx + tw + pad)
    y2 = min(img.shape[0], ty + th + pad)
    
    table_crop = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(table_crop, cv2.COLOR_BGR2GRAY)
    
    # Horizontal kernel
    horiz_kernel_len = max(tw // 5, 30)
    horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horiz_kernel_len, 1))
    
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    horiz_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horiz_kernel, iterations=2)
    
    contours, _ = cv2.findContours(horiz_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    line_ys = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if cw > tw * 0.3 and ch < th * 0.05:
            center_y = y1 + y + ch // 2
            line_ys.append(center_y)
    
    line_ys.sort()
    
    # Merge close lines
    if line_ys:
        merge_thresh = th * 0.015
        merged = [line_ys[0]]
        for ly in line_ys[1:]:
            if ly - merged[-1] > merge_thresh:
                merged.append(ly)
            else:
                merged[-1] = (merged[-1] + ly) // 2
        line_ys = merged
    
    # We expect 22 horizontal lines (top border + header + 20 data rows + bottom border)
    # But at minimum we need enough to define the grid
    if len(line_ys) >= 10:
        return line_ys
    
    return None


def get_column_boundaries_from_lines(vert_lines, table_x, table_w):
    """
    Given detected vertical lines, determine the A/B/C/D column boundaries.
    The table has columns: Dt. | A | B | C | D
    
    We need 5 boundaries (4 columns = 5 edges) for the answer area.
    """
    # The vertical lines include the table left edge and the Dt./A boundary
    # We need to identify which lines separate the answer columns
    
    # If we have 6 lines: left | Dt/A | A/B | B/C | C/D | right
    if len(vert_lines) >= 6:
        # The first line is the table left edge, second is Dt./A boundary
        # Lines index 1..5 give us the 5 answer column boundaries
        return vert_lines[1:6]
    elif len(vert_lines) == 5:
        # Possibly missing the left edge OR the right edge
        # Check if the first line is close to table_x (left edge)
        if abs(vert_lines[0] - table_x) < table_w * 0.05:
            # First line is left edge, need to extrapolate right boundary
            boundaries = vert_lines[1:5]
            # Extrapolate the 5th boundary
            avg_gap = np.mean(np.diff(boundaries))
            boundaries.append(int(boundaries[-1] + avg_gap))
            return boundaries
        else:
            # First line is probably the Dt/A boundary
            return vert_lines[:5]
    
    return None


def get_column_boundaries_fallback(table_x, table_w):
    """
    Fallback: compute column boundaries from table geometry.
    The table has 5 columns: Dt. | A | B | C | D
    The Dt. column is narrow (~13-16% of width).
    """
    # Try different dt_fraction values and return the most likely one
    dt_fraction = 0.15
    dt_width = table_w * dt_fraction
    answer_area_start = table_x + dt_width
    answer_area_width = table_w - dt_width
    col_width = answer_area_width / 4.0

    col_boundaries = []
    for i in range(5):
        col_boundaries.append(answer_area_start + i * col_width)

    return col_boundaries


def get_row_boundaries(horiz_lines, table_y, table_h):
    """
    Given detected horizontal lines, determine the row center Y coordinates.
    Returns dict mapping question number (1-20) to (y_top, y_bottom) tuple.
    """
    # Remove lines that are far outside the table
    filtered = [y for y in horiz_lines if table_y - 20 <= y <= table_y + table_h + 20]
    
    if len(filtered) < 3:
        return None
    
    # The first line should be the top of the table, second is after the header
    # Then data rows follow
    rows = {}
    
    # If we have enough lines for all rows (22 = top + header bottom + 20 row bottoms)
    if len(filtered) >= 20:
        # Use the lines directly: filtered[0] = top, filtered[1] = header bottom
        # filtered[2] = row 1 bottom, etc.
        for q in range(1, min(21, len(filtered))):
            if q + 1 < len(filtered):
                rows[q] = (filtered[q], filtered[q + 1])
    
    return rows if rows else None


# ═══════════════════════════════════════════════════════════════════
# PERSPECTIVE CORRECTION
# ═══════════════════════════════════════════════════════════════════

def correct_table_perspective(img, table_rect):
    """
    Attempt to correct perspective distortion of the table area.
    Uses the table contour to find a homography transform.
    Returns the corrected image and the transform matrix, or (img, None) if correction fails.
    """
    tx, ty, tw, th = table_rect
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Find the table contour more precisely using Canny edges
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 21, 10)
    
    # Look for largest contour near the table rect
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_cnt = None
    best_overlap = 0
    for cnt in contours:
        cx, cy, cw, ch = cv2.boundingRect(cnt)
        # Check overlap with table_rect
        ox = max(0, min(tx + tw, cx + cw) - max(tx, cx))
        oy = max(0, min(ty + th, cy + ch) - max(ty, cy))
        overlap = ox * oy
        if overlap > best_overlap:
            best_overlap = overlap
            best_cnt = cnt
    
    if best_cnt is None:
        return img, None
    
    # Approximate the contour with a polygon
    epsilon = 0.02 * cv2.arcLength(best_cnt, True)
    approx = cv2.approxPolyDP(best_cnt, epsilon, True)
    
    if len(approx) == 4:
        # We have a quadrilateral — can do perspective correction
        pts = approx.reshape(4, 2).astype(np.float32)
        
        # Order points: top-left, top-right, bottom-right, bottom-left
        rect = order_points(pts)
        
        # Destination: a perfect rectangle
        dst = np.array([
            [tx, ty],
            [tx + tw, ty],
            [tx + tw, ty + th],
            [tx, ty + th]
        ], dtype=np.float32)
        
        M = cv2.getPerspectiveTransform(rect, dst)
        corrected = cv2.warpPerspective(img, M, (w, h))
        return corrected, M
    
    return img, None


def order_points(pts):
    """Order 4 points as: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left has smallest sum
    rect[2] = pts[np.argmax(s)]  # bottom-right has largest sum
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]  # top-right has smallest difference
    rect[3] = pts[np.argmax(d)]  # bottom-left has largest difference
    return rect


# ═══════════════════════════════════════════════════════════════════
# ANSWER EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def extract_answers_from_image(img_path, model, debug=False, debug_dir=None):
    """
    Process a single image and return the detected answers.
    
    Strategy:
    1. Detect X marks with YOLO
    2. Find the table rectangle via contour detection
    3. Attempt perspective correction
    4. Detect actual grid lines (horizontal + vertical) for precise mapping
    5. Fall back to uniform grid division if line detection fails
    6. Map each detection to its grid cell
    """
    img = cv2.imread(img_path)
    if img is None:
        print(f"  [ERROR] Could not read image: {img_path}")
        return None

    h, w = img.shape[:2]
    basename = os.path.splitext(os.path.basename(img_path))[0]

    # ── YOLO Detection ──
    results = model.predict(source=img_path, conf=0.15, iou=0.45, agnostic_nms=True, verbose=False)

    det_centers = []
    det_confs = []
    det_boxes = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            xc = (x1 + x2) / 2
            yc = (y1 + y2) / 2
            det_centers.append([xc, yc])
            det_confs.append(conf)
            det_boxes.append([x1, y1, x2, y2])

    n_det = len(det_centers)
    if n_det < 3:
        print(f"  [WARN] Only {n_det} detections in {basename}, skipping.")
        return None

    pts = np.array(det_centers, dtype="float32")
    confs = np.array(det_confs)

    # ── Find table rectangle ──
    table_rect = find_table_rect(img)
    method = "TABLE_RECT"

    if table_rect is not None:
        tx, ty, tw, th = table_rect
        
        # Try perspective correction
        corrected_img, M = correct_table_perspective(img, table_rect)
        if M is not None:
            method = "TABLE_RECT+PERSP"
            # Re-find table rect in corrected image
            new_rect = find_table_rect(corrected_img)
            if new_rect is not None:
                tx, ty, tw, th = new_rect
                table_rect = new_rect
            
            # Transform detection points using the perspective matrix
            det_pts = np.array(det_centers, dtype=np.float32).reshape(-1, 1, 2)
            transformed = cv2.perspectiveTransform(det_pts, M)
            det_centers_mapped = transformed.reshape(-1, 2).tolist()
        else:
            det_centers_mapped = det_centers
        
        # ── Try to detect actual grid lines ──
        work_img = corrected_img if M is not None else img
        vert_lines = detect_vertical_lines(work_img, table_rect)
        horiz_lines = detect_horizontal_lines(work_img, table_rect)
        
        # Determine column boundaries
        if vert_lines is not None:
            col_bounds = get_column_boundaries_from_lines(vert_lines, tx, tw)
            if col_bounds is not None:
                method += "+VLINES"
            else:
                col_bounds = get_column_boundaries_fallback(tx, tw)
        else:
            col_bounds = get_column_boundaries_fallback(tx, tw)
        
        # Determine row mapping
        use_line_rows = False
        row_map = None
        if horiz_lines is not None:
            row_map = get_row_boundaries(horiz_lines, ty, th)
            if row_map and len(row_map) >= 15:
                use_line_rows = True
                method += "+HLINES"
        
        if not use_line_rows:
            # Uniform row grid: 1 header row + 20 data rows = 21 rows
            total_rows_incl_header = 21
            row_height = th / total_rows_incl_header
            data_start_y = ty + row_height

        # ── Map detections to grid cells ──
        question_candidates = {}
        debug_assignments = []

        for i, (xc_orig, yc_orig) in enumerate(det_centers):
            xc, yc = det_centers_mapped[i]
            
            # Row assignment
            if use_line_rows:
                row_idx = -1
                best_dist = float('inf')
                for q, (yt, yb) in row_map.items():
                    center_y = (yt + yb) / 2
                    dist = abs(yc - center_y)
                    if yt - 5 <= yc <= yb + 5 and dist < best_dist:
                        row_idx = q
                        best_dist = dist
                
                # If not in any row, find nearest
                if row_idx == -1:
                    for q, (yt, yb) in row_map.items():
                        center_y = (yt + yb) / 2
                        dist = abs(yc - center_y)
                        if dist < best_dist:
                            row_idx = q
                            best_dist = dist
            else:
                row_float = (yc - data_start_y) / row_height
                row_idx = round(row_float) + 1

            if row_idx < 1 or row_idx > 20:
                debug_assignments.append((xc_orig, yc_orig, -1, -1, confs[i], "OUT"))
                continue

            # Column assignment: find which column the detection falls in
            col_idx = -1
            for c in range(len(col_bounds) - 1):
                left = col_bounds[c]
                right = col_bounds[c + 1] if c + 1 < len(col_bounds) else col_bounds[c] + tw * 0.21
                if left <= xc <= right:
                    col_idx = c
                    break

            if col_idx == -1:
                # Find nearest column center
                col_centers = []
                for c in range(min(4, len(col_bounds) - 1)):
                    cc = (col_bounds[c] + col_bounds[c + 1]) / 2
                    col_centers.append(cc)
                
                if not col_centers:
                    col_centers = [(col_bounds[c] + col_bounds[min(c+1, len(col_bounds)-1)]) / 2 for c in range(min(4, len(col_bounds)))]
                
                if col_centers:
                    col_idx = int(np.argmin([abs(xc - cc) for cc in col_centers]))

            col_idx = max(0, min(3, col_idx))
            q_num = row_idx
            opt = OPTIONS[col_idx]
            conf = confs[i]

            debug_assignments.append((xc_orig, yc_orig, q_num, col_idx, conf, opt))

            if q_num not in question_candidates:
                question_candidates[q_num] = {}
            if opt not in question_candidates[q_num] or conf > question_candidates[q_num][opt]:
                question_candidates[q_num][opt] = conf

    else:
        # ── Fallback: K-means columns + uniform Y grid from detections ──
        method = "KMEANS_FALLBACK"
        det_centers_mapped = det_centers
        
        pts_x = pts[:, 0].reshape(-1, 1).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
        _, labels_x, centers_x = cv2.kmeans(pts_x, NUM_COLS, None, criteria, 20,
                                            cv2.KMEANS_PP_CENTERS)
        col_order = np.argsort(centers_x.flatten())
        x_label_to_col = {int(label): i for i, label in enumerate(col_order)}

        min_y = pts[:, 1].min()
        max_y = pts[:, 1].max()
        total_span = max_y - min_y
        row_h = total_span / (NUM_ROWS - 1)
        grid_top = min_y - row_h / 2

        question_candidates = {}
        debug_assignments = []
        for i, (xc, yc) in enumerate(det_centers):
            col_idx = x_label_to_col[int(labels_x[i][0])]
            row_idx = round((yc - grid_top) / row_h)
            row_idx = max(0, min(NUM_ROWS - 1, row_idx))
            col_idx = max(0, min(3, col_idx))

            q_num = row_idx + 1
            opt = OPTIONS[col_idx]
            conf = confs[i]

            debug_assignments.append((xc, yc, q_num, col_idx, conf, opt))

            if q_num not in question_candidates:
                question_candidates[q_num] = {}
            if opt not in question_candidates[q_num] or conf > question_candidates[q_num][opt]:
                question_candidates[q_num][opt] = conf

    # ── Resolve conflicts: if two detections map to same row, pick highest confidence ──
    answers = {}
    for q, opt_map in question_candidates.items():
        best_opt = max(opt_map, key=opt_map.get)
        answers[q] = best_opt

    # ── Debug visualization ──
    if debug and debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        debug_img = img.copy()

        cv2.putText(debug_img, f"Method: {method} | Det: {n_det}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        if table_rect is not None:
            tx, ty, tw, th = table_rect
            
            # Draw table rectangle  
            cv2.rectangle(debug_img, (tx, ty), (tx + tw, ty + th), (0, 255, 0), 3)

            # Draw column boundaries
            if 'col_bounds' in dir():
                for ci in range(len(col_bounds)):
                    cx = int(col_bounds[ci])
                    color = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (200,200,200)][ci % 5]
                    cv2.line(debug_img, (cx, ty), (cx, ty + th), color, 2)
                    if ci < 4:
                        cv2.putText(debug_img, OPTIONS[ci], (cx + 5, ty - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Draw row lines
            if use_line_rows and row_map:
                for q, (yt, yb) in row_map.items():
                    cv2.line(debug_img, (tx, int(yt)), (tx + tw, int(yt)), (0, 255, 255), 1)
                    cv2.putText(debug_img, str(q), (tx - 50, int((yt + yb) / 2) + 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            else:
                row_height = th / 21.0
                for r_i in range(22):
                    ry = int(ty + r_i * row_height)
                    cv2.line(debug_img, (tx, ry), (tx + tw, ry), (0, 255, 255), 1)
                    if 1 <= r_i <= 20:
                        cv2.putText(debug_img, str(r_i), (tx - 50, ry + 15),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for assignment in debug_assignments:
            xc, yc, q_num, col_idx, conf, opt = assignment
            color = colors[max(0, col_idx) % 4]
            cv2.circle(debug_img, (int(xc), int(yc)), 10, color, -1)
            if q_num > 0:
                label = f"Q{q_num}{opt} ({conf:.2f})"
            else:
                label = f"OUT ({conf:.2f})"
            cv2.putText(debug_img, label, (int(xc) + 15, int(yc) + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Save debug detections log
        log_path = os.path.join(debug_dir, f"{basename}_assignments.txt")
        with open(log_path, 'w') as f:
            f.write(f"Table: x={tx}, y={ty}, w={tw}, h={th}\n")
            f.write(f"Method: {method}\n")
            if 'col_bounds' in dir():
                f.write(f"Col boundaries: {[f'{c:.0f}' for c in col_bounds]}\n")
            f.write(f"\n")
            for assignment in debug_assignments:
                xc, yc, q_num, col_idx, conf, opt = assignment
                f.write(f"({int(xc)}, {int(yc)}) conf={conf:.2f} -> Q{q_num} {opt} (col={col_idx})\n")
            f.write(f"\nFinal answers:\n")
            for q in range(1, 21):
                f.write(f"  Q{q:2d}: {answers.get(q, '-')}\n")

        debug_path = os.path.join(debug_dir, f"{basename}_debug.jpg")
        cv2.imwrite(debug_path, debug_img)

    print(f"  Method: {method} | Detections: {n_det}")
    return answers


# ═══════════════════════════════════════════════════════════════════
# STUDENT ID EXTRACTION via EasyOCR
# ═══════════════════════════════════════════════════════════════════

def extract_student_id(img_path, reader, debug=False, debug_dir=None):
    """Extract the 5-digit student ID from the left side of the answer sheet."""
    img = cv2.imread(img_path)
    if img is None:
        return "UNKNOWN"

    h, w = img.shape[:2]
    basename = os.path.splitext(os.path.basename(img_path))[0]

    # ── Crop multiple regions to find the ID ──
    # The ID is typically in the left-center area of the sheet
    crops = []
    
    # Primary crop: left side, vertical middle
    y_start = int(0.28 * h)
    y_end = int(0.60 * h)
    x_start = int(0.02 * w)
    x_end = int(0.45 * w)
    crops.append(img[y_start:y_end, x_start:x_end])
    
    # Wider crop if first fails
    y_start2 = int(0.25 * h)
    y_end2 = int(0.65 * h)
    x_start2 = int(0.01 * w)
    x_end2 = int(0.50 * w)
    crops.append(img[y_start2:y_end2, x_start2:x_end2])

    all_candidates = []
    
    for crop_idx, crop in enumerate(crops):
        crop_up = cv2.resize(crop, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        strategies = []

        # S1: CLAHE + threshold
        gray1 = cv2.cvtColor(crop_up, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray1 = clahe.apply(gray1)
        _, s1 = cv2.threshold(gray1, 140, 255, cv2.THRESH_BINARY_INV)
        s1 = cv2.bitwise_not(s1)
        strategies.append(s1)

        # S2: Adaptive threshold
        gray2 = cv2.cvtColor(crop_up, cv2.COLOR_BGR2GRAY)
        s2 = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 31, 15)
        strategies.append(s2)

        # S3: Blue channel isolation (for blue pen)
        b, g, r = cv2.split(crop_up)
        blue_diff = np.clip(r.astype(int) - b.astype(int), 0, 255).astype(np.uint8)
        _, s3 = cv2.threshold(blue_diff, 20, 255, cv2.THRESH_BINARY)
        s3 = cv2.bitwise_not(s3)
        strategies.append(s3)

        # S4: Otsu
        gray4 = cv2.cvtColor(crop_up, cv2.COLOR_BGR2GRAY)
        gray4 = cv2.GaussianBlur(gray4, (3, 3), 0)
        _, s4 = cv2.threshold(gray4, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        strategies.append(s4)

        # S5: Sharpened + contrast enhanced
        gray5 = cv2.cvtColor(crop_up, cv2.COLOR_BGR2GRAY)
        sharp_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        gray5 = cv2.filter2D(gray5, -1, sharp_kernel)
        gray5 = cv2.convertScaleAbs(gray5, alpha=1.5, beta=10)
        _, s5 = cv2.threshold(gray5, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        strategies.append(s5)

        for si, prep_img in enumerate(strategies):
            try:
                ocr_results = reader.readtext(prep_img, allowlist='0123456789',
                                              paragraph=False, min_size=10)
                digit_entries = []
                for r_item in ocr_results:
                    text = r_item[1]
                    conf = r_item[2]
                    digits_only = re.sub(r'[^0-9]', '', text)
                    if digits_only:
                        bbox = r_item[0]
                        cx = sum(p[0] for p in bbox) / 4
                        digit_entries.append((cx, digits_only, conf))

                if digit_entries:
                    digit_entries.sort(key=lambda e: e[0])
                    all_digits = "".join(entry[1] for entry in digit_entries)
                    avg_conf = np.mean([e[2] for e in digit_entries])
                    if len(all_digits) >= 4:
                        all_candidates.append((all_digits[:5], avg_conf, f"crop{crop_idx}_s{si}"))
            except Exception:
                pass

        if debug and debug_dir and crop_idx == 0:
            os.makedirs(debug_dir, exist_ok=True)
            cv2.imwrite(os.path.join(debug_dir, f"{basename}_id_crop.jpg"), crop)
            for si, s in enumerate(strategies):
                cv2.imwrite(os.path.join(debug_dir, f"{basename}_id_s{si+1}.jpg"), s)

    if not all_candidates:
        return "UNKNOWN"

    # Prefer 5-digit candidates
    five_digit = [c for c in all_candidates if len(c[0]) == 5]
    if five_digit:
        # Use voting: count most common 5-digit result
        from collections import Counter
        counts = Counter(c[0] for c in five_digit)
        most_common = counts.most_common(1)[0]
        if most_common[1] >= 2:
            return most_common[0]
        # Otherwise pick highest confidence
        best = max(five_digit, key=lambda c: c[1])
    else:
        best = max(all_candidates, key=lambda c: c[1])

    student_id = best[0]
    if len(student_id) < 5:
        student_id = student_id.ljust(5, '?')

    return student_id


# ═══════════════════════════════════════════════════════════════════
# GRADING
# ═══════════════════════════════════════════════════════════════════

def grade_answers(detected_answers, answer_key):
    if answer_key is None:
        return None, None, None

    correct = 0
    details = {}
    for q in range(1, NUM_ROWS + 1):
        correct_ans = answer_key.get(q, None)
        student_ans = detected_answers.get(q, None)
        if correct_ans is None:
            details[q] = {"student": student_ans or "-", "correct": "-", "status": "N/A"}
            continue
        if student_ans == correct_ans:
            correct += 1
            details[q] = {"student": student_ans, "correct": correct_ans, "status": "CORRECT"}
        elif student_ans is None:
            details[q] = {"student": "-", "correct": correct_ans, "status": "BLANK"}
        else:
            details[q] = {"student": student_ans, "correct": correct_ans, "status": "WRONG"}

    total = len([q for q in answer_key if answer_key[q] is not None])
    return correct, total, details


# ═══════════════════════════════════════════════════════════════════
# PROCESS & SAVE
# ═══════════════════════════════════════════════════════════════════

def process_images(image_paths, debug=False):
    print("=" * 60)
    print("  STUDENT ANSWER SHEET GRADING SYSTEM")
    print("=" * 60)

    print("\n[1/2] Loading YOLO model...")
    model = YOLO(MODEL_PATH)

    print("[2/2] Loading OCR engine...")
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    debug_dir = DEBUG_DIR if debug else None
    all_results = []

    print(f"\nProcessing {len(image_paths)} image(s)...\n")
    print("-" * 60)

    for idx, img_path in enumerate(image_paths, 1):
        basename = os.path.basename(img_path)
        print(f"\n[{idx}/{len(image_paths)}] {basename}")

        student_id = extract_student_id(img_path, reader, debug=debug, debug_dir=debug_dir)
        print(f"  Student ID: {student_id}")

        answers = extract_answers_from_image(img_path, model, debug=debug, debug_dir=debug_dir)
        if answers is None:
            print(f"  [SKIP] Could not extract answers.")
            all_results.append({
                "student_id": student_id, "image": basename,
                "answers": {}, "correct": None, "total": None
            })
            continue

        print(f"  Detected answers:")
        for q in range(1, NUM_ROWS + 1):
            ans = answers.get(q, "-")
            print(f"    Q{q:2d}: {ans}")

        correct_count = None
        total = None
        if ANSWER_KEY:
            correct_count, total, details = grade_answers(answers, ANSWER_KEY)
            print(f"\n  Score: {correct_count}/{total} = {correct_count/total*100:.1f}%")
            for q in range(1, NUM_ROWS + 1):
                d = details[q]
                print(f"    Q{q:2d}: {d['student']:>1s} vs {d['correct']:>1s}  [{d['status']}]")

        all_results.append({
            "student_id": student_id, "image": basename,
            "answers": answers, "correct": correct_count, "total": total
        })

    return all_results


def save_results(all_results, output_path):
    header = ["student_id", "image"]
    for q in range(1, NUM_ROWS + 1):
        header.append(f"Q{q}")
    header.extend(["correct_count", "total_questions", "score_percent"])

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for result in all_results:
            row = [result["student_id"], result["image"]]
            for q in range(1, NUM_ROWS + 1):
                row.append(result["answers"].get(q, ""))
            row.append(result.get("correct", ""))
            row.append(result.get("total", ""))
            if result.get("correct") is not None and result.get("total"):
                pct = round(result["correct"] / result["total"] * 100, 1)
                row.append(f"{pct}%")
            else:
                row.append("")
            writer.writerow(row)

    print(f"\n{'=' * 60}")
    print(f"  Results saved to: {output_path}")
    print(f"  Total students processed: {len(all_results)}")
    if any(r.get("correct") is not None for r in all_results):
        avg = np.mean([r["correct"] for r in all_results if r.get("correct") is not None])
        print(f"  Average score: {avg:.1f}")
    print(f"{'=' * 60}")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Grade student answer sheets")
    parser.add_argument("--image", type=str, help="Path to a single image")
    parser.add_argument("--folder", type=str, default="dataset/images/train",
                        help="Folder to process (default: dataset/images/train)")
    parser.add_argument("--debug", action="store_true", help="Save debug visualizations")
    parser.add_argument("--output", type=str, default=RESULTS_CSV,
                        help=f"Output CSV path (default: {RESULTS_CSV})")
    parser.add_argument("--key", type=str, default=None,
                        help="Answer key: 'B,C,B,A,B,...' (20 answers)")
    args = parser.parse_args()

    global ANSWER_KEY
    if args.key:
        keys = [k.strip().upper() for k in args.key.split(",")]
        if len(keys) != NUM_ROWS:
            print(f"ERROR: Answer key must have exactly {NUM_ROWS} answers, got {len(keys)}")
            sys.exit(1)
        ANSWER_KEY = {i + 1: k for i, k in enumerate(keys)}
        print(f"Answer key loaded: {ANSWER_KEY}")

    if args.image:
        if not os.path.exists(args.image):
            print(f"ERROR: Image not found: {args.image}")
            sys.exit(1)
        image_paths = [args.image]
    else:
        folder = args.folder
        if not os.path.isdir(folder):
            print(f"ERROR: Folder not found: {folder}")
            sys.exit(1)
        image_paths = sorted([
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])

    if not image_paths:
        print("No images found.")
        sys.exit(1)

    results = process_images(image_paths, debug=args.debug)
    save_results(results, args.output)


if __name__ == "__main__":
    main()
