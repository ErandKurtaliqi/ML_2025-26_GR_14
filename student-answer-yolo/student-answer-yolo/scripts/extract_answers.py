# # from ultralytics import YOLO
# # IMAGE_PATH = "dataset/images/test/IMG_8177.jpg" 
# # MODEL_PATH = "runs/detect/runs/student_answer_detection/weights/best.pt"

# # NUM_ROWS = 20
# # NUM_COLS = 4
# # OPTIONS = ["A", "B", "C", "D"]

# # model = YOLO(MODEL_PATH)

# # results = model.predict(
# #     source=IMAGE_PATH,
# #     conf=0.15,
# #     save=False
# # )

# # detections = []

# # for r in results:
# #     for box in r.boxes:
# #         x1, y1, x2, y2 = box.xyxy[0].tolist()
# #         conf = float(box.conf[0])

# #         x_center = (x1 + x2) / 2
# #         y_center = (y1 + y2) / 2

# #         detections.append({
# #             "x1": x1, "y1": y1, "x2": x2, "y2": y2,
# #             "xc": x_center, "yc": y_center, "conf": conf
# #         })

# # if not detections:
# #     print("Nuk u gjet asnjë marked_box.")
# #     raise SystemExit

# # # Zona dinamike nga detections
# # min_x = min(d["xc"] for d in detections)
# # max_x = max(d["xc"] for d in detections)
# # min_y = min(d["yc"] for d in detections)
# # max_y = max(d["yc"] for d in detections)

# # # padding
# # pad_x = 35
# # pad_y = 20

# # TABLE_X1 = min_x - pad_x
# # TABLE_X2 = max_x + pad_x
# # TABLE_Y1 = min_y - pad_y
# # TABLE_Y2 = max_y + pad_y

# # row_h = (TABLE_Y2 - TABLE_Y1) / NUM_ROWS
# # col_w = (TABLE_X2 - TABLE_X1) / NUM_COLS

# # answers = {}
# # question_candidates = {}

# # for d in detections:
# #     x_center = d["xc"]
# #     y_center = d["yc"]
# #     conf = d["conf"]

# #     row_idx = int((y_center - TABLE_Y1) / row_h)
# #     col_idx = int((x_center - TABLE_X1) / col_w)

# #     if 0 <= row_idx < NUM_ROWS and 0 <= col_idx < NUM_COLS:
# #         question = row_idx + 1
# #         option = OPTIONS[col_idx]

# #         if question not in question_candidates:
# #             question_candidates[question] = {}

# #         # Keep only the strongest detection per option for each question.
# #         if option not in question_candidates[question] or conf > question_candidates[question][option]["conf"]:
# #             question_candidates[question][option] = {
# #                 "option": option,
# #                 "conf": conf,
# #                 "xc": x_center,
# #                 "yc": y_center
# #             }

# # invalid_questions = {}

# # for question, option_map in question_candidates.items():
# #     if len(option_map) == 1:
# #         answers[question] = next(iter(option_map.values()))
# #     elif len(option_map) > 1:
# #         invalid_questions[question] = sorted(option_map.keys())

# # print("\nPergjigjet e detektuara:\n")
# # for q in range(1, 21):
# #     if q in invalid_questions:
# #         marked = ", ".join(invalid_questions[q])
# #         print(f"{q}: gabim (dy ose me shume opcione: {marked})")
# #     elif q in answers:
# #         print(f"{q}: {answers[q]['option']} (conf={answers[q]['conf']:.2f})")
# #     else:
# #         print(f"{q}: nuk u gjet")

# # print("\nZona dinamike:")
# # print(f"TABLE_X1={TABLE_X1:.1f}, TABLE_X2={TABLE_X2:.1f}")
# # print(f"TABLE_Y1={TABLE_Y1:.1f}, TABLE_Y2={TABLE_Y2:.1f}")



# # 20260309_210021.jpg
# import cv2
# import numpy as np
# from ultralytics import YOLO

# # --- Setup ---
# MODEL_PATH = "runs/detect/runs/student_answer_detection/weights/best.pt"
# IMAGE_PATH = "dataset/images/test/IMG_8177.jpg"
# model = YOLO(MODEL_PATH)

# def order_points(pts):
#     """Sorts coordinates to: top-left, top-right, bottom-right, bottom-left"""
#     rect = np.zeros((4, 2), dtype="float32")
#     s = pts.sum(axis=1)
#     rect[0] = pts[np.argmin(s)]
#     rect[2] = pts[np.argmax(s)]
#     diff = np.diff(pts, axis=1)
#     rect[1] = pts[np.argmin(diff)]
#     rect[3] = pts[np.argmax(diff)]
#     return rect

# def generate_deskew_results(img_path, output_path="debug_result.jpg"):
#     img = cv2.imread(img_path)
#     original_view = img.copy()
#     h, w = img.shape[:2]
    
#     # --- 1. Detect Table and Warp ---
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)
#     thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     if not contours:
#         return {"error": "No table found"}
    
#     table_cnt = max(contours, key=cv2.contourArea)
#     peri = cv2.arcLength(table_cnt, True)
#     approx = cv2.approxPolyDP(table_cnt, 0.02 * peri, True)
    
#     if len(approx) != 4:
#         rect = cv2.minAreaRect(table_cnt)
#         approx = cv2.boxPoints(rect)
    
#     # ORDER POINTS AND WARP
#     pts1 = order_points(approx.reshape(4, 2))
#     dst_w, dst_h = 500, 1000
#     pts2 = np.float32([[0, 0], [dst_w, 0], [dst_w, dst_h], [0, dst_h]])
#     M = cv2.getPerspectiveTransform(pts1, pts2)

#     # CREATE THE WARPED (FLATTENED) IMAGE FOR THE GRID VIEW
#     warped_img = cv2.warpPerspective(img, M, (dst_w, dst_h))
#     debug_warped = warped_img.copy()

#     # --- 2. Setup Debug Drawings ---
#     # ORIGINAL VIEW DRAWING
#     cv2.polylines(original_view, [approx.reshape(-1, 1, 2).astype(np.int32)], True, (0, 0, 255), 3) # Red border
#     # Add a magenta anchor at top-left
#     cv2.circle(original_view, tuple(pts1[0].astype(int)), 15, (255, 0, 255), -1)

#     # CORRECTED VIEW GRID DRAWING
#     for i in range(22): # Horizontal Rows
#         y = int(i * (dst_h / 21))
#         cv2.line(debug_warped, (0, y), (dst_w, y), (0, 255, 0), 1)
#     for j in range(6): # Vertical Cols
#         x = int(j * (dst_w / 5))
#         cv2.line(debug_warped, (x, 0), (x, dst_h), (255, 0, 0), 1)

#     # --- 3. Detect X's and Map ---
#     results = model.predict(source=img_path, conf=0.2, verbose=False)
#     boxes = results[0].boxes.xyxy.cpu().numpy()
#     confs = results[0].boxes.conf.cpu().numpy()

#     final_answers = {}
#     cols_labels = ['a', 'b', 'c', 'd']

#     for i, box in enumerate(boxes):
#         cx = (box[0] + box[2]) / 2
#         cy = (box[1] + box[3]) / 2
        
#         # --- DRAW ON ORIGINAL VIEW ---
#         # Mark all detections with a cyan circle and original coordinates
#         cv2.circle(original_view, (int(cx), int(cy)), 10, (255, 255, 0), -1)
#         label = f"({int(cx)},{int(cy)})"
#         cv2.putText(original_view, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

#         # --- TRANSFORM AND DRAW ON CORRECTED VIEW ---
#         point = np.array([[[cx, cy]]], dtype="float32")
#         transformed_point = cv2.perspectiveTransform(point, M)[0][0]
#         tx, ty = int(transformed_point[0]), int(transformed_point[1])
#         cv2.circle(debug_warped, (tx, ty), 10, (255, 255, 0), -1) # Also cyan in warped view

#         # --- MAP THE ANSWER ---
#         rel_x = tx / dst_w
#         rel_y = ty / dst_h
        
#         row = int(rel_y * 21)
#         col = int(rel_x * 5)
        
#         if 1 <= row <= 20 and 1 <= col <= 4:
#             answer = cols_labels[col-1]
#             if row not in final_answers:
#                 final_answers[row] = [answer]
#             else:
#                 final_answers[row].append(answer) # Stores both ['b', 'c']

#     # --- 4. Combine and Save Debug Output ---
#     h_w, w_w = debug_warped.shape[:2]
#     original_view = cv2.resize(original_view, (int(original_view.shape[1] * h_w / original_view.shape[0]), h_w))
#     result = np.hstack((original_view, debug_warped))
#     cv2.imwrite(output_path, result)
#     print(f"DEBUG Image saved to {output_path}")

#     return dict(sorted(final_answers.items()))

# # --- Execution ---
# print("Running complete answer extraction with debug output...")
# extracted_answers = generate_deskew_results(IMAGE_PATH)
# print(f"Final Extracted Answers: {extracted_answers}")

# ma e mira qekjo posht
import cv2
import numpy as np
from ultralytics import YOLO

# --- Setup ---
MODEL_PATH = "runs/detect/runs/student_answer_v2/weights/best.pt"

IMAGE_PATH = "dataset/images/train/IMG_8175.jpg"
model = YOLO(MODEL_PATH)

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def generate_row_debug(img_path, output_path="row_debug_result.jpg"):
    img = cv2.imread(img_path)
    
    # 1. Perspective Warp (Deskew)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_cnt = max(contours, key=cv2.contourArea)
    
    approx = cv2.approxPolyDP(table_cnt, 0.02 * cv2.arcLength(table_cnt, True), True)
    if len(approx) != 4: approx = cv2.boxPoints(cv2.minAreaRect(table_cnt))
        
    pts1 = order_points(approx.reshape(4, 2))
    dst_w, dst_h = 600, 1200 # Larger size for better text visibility
    pts2 = np.float32([[0, 0], [dst_w, 0], [dst_w, dst_h], [0, dst_h]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    
    # Create the flattened table
    warped = cv2.warpPerspective(img, M, (dst_w, dst_h))
    
    # 2. Draw the "Row-Specific" Grid
    row_h = dst_h / 21
    col_w = dst_w / 5
    options = ['idx', 'a', 'b', 'c', 'd']

    for r in range(21):
        if r == 0:
         y1 = 0
         y2 = 70
        else:
         y1 = 70 + int((r - 1) * row_h)
         y2 = 70 + int(r * row_h)
        for c in range(5):
            x1 = int(c * col_w)
            x2 = int((c+1) * col_w)
            
            # Draw cell borders
            cv2.rectangle(warped, (x1, y1), (x2, y2), (255, 0, 0), 1)
            
            # Label each cell with its ID (e.g., "12:c")
            if r > 0 and c > 0:
                label = f"{r}{options[c]}"
                cv2.putText(warped, label, (x1+5, y2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # 3. Detect and Map Marks
    results = model.predict(source=img_path, conf=0.2, verbose=False)
    boxes = results[0].boxes.xyxy.cpu().numpy()

    for box in boxes:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        
        # Transform detection center to warped space
        p = np.array([[[cx, cy]]], dtype="float32")
        tp = cv2.perspectiveTransform(p, M)[0][0]
        tx, ty = int(tp[0]), int(tp[1])
        
        # Determine Row/Col
        row_num = int(ty / row_h)
        col_num = int(tx / col_w)

        # Draw a bold yellow circle and label the detection result
        if 0 <= row_num <= 20 and 0 <= col_num <= 4:
            cv2.circle(warped, (tx, ty), 10, (0, 255, 255), -1)
            cv2.circle(warped, (tx, ty), 11, (0, 0, 0), 2)
            
            result_label = f"Match -> R{row_num}:{options[col_num]}"
            cv2.putText(warped, result_label, (tx + 15, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Save the result
    cv2.imwrite(output_path, warped)
    print(f"Detailed Row Debug saved as: {output_path}")

# Run

def get_row_specific_answers(img_path):
    img = cv2.imread(img_path)
    
    # 1. Perspective Warp to get a perfectly flat table
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_cnt = max(contours, key=cv2.contourArea)
    
    approx = cv2.approxPolyDP(table_cnt, 0.02 * cv2.arcLength(table_cnt, True), True)
    if len(approx) != 4: approx = cv2.boxPoints(cv2.minAreaRect(table_cnt))
        
    pts1 = order_points(approx.reshape(4, 2))
    dst_w, dst_h = 500, 1000  # Flattened size
    pts2 = np.float32([[0, 0], [dst_w, 0], [dst_w, dst_h], [0, dst_h]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (dst_w, dst_h))

    # --- 2. AUTOMATIC ROW DETECTION ---
    # Convert warped table to binary to find the horizontal black lines
    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Sum pixels horizontally to find "spikes" of ink (the lines)
    horizontal_sum = np.sum(binary, axis=1)
    
    detected_y_lines = []
    line_threshold = dst_w * 255 * 0.4  # Adjust 0.4 (40%) based on line thickness
    
    for y in range(len(horizontal_sum)):
        if horizontal_sum[y] > line_threshold:
            # Group nearby pixels into a single line
            if not detected_y_lines or abs(y - detected_y_lines[-1]) > 10:
                detected_y_lines.append(y)

    # --- 3. YOLO Detection and Snapping ---
    results = model.predict(source=img_path, conf=0.2, verbose=False)
    boxes = results[0].boxes.xyxy.cpu().numpy()

    print("Detected Y Lines (Row Boundaries):", boxes)

    final_answers = {}
    cols_labels = ['a', 'b', 'c', 'd']
    col_width = dst_w / 5

    for box in boxes:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        p = np.array([[[cx, cy]]], dtype="float32")
        tp = cv2.perspectiveTransform(p, M)[0][0]
        tx, ty = tp[0], tp[1]

        # AUTO-SNAP: Find which detected box the point 'ty' falls into
        row_num = -1
        # detected_y_lines[0] is the top of the header
        # detected_y_lines[1] is the line below the header (start of Row 1)
        for i in range(len(detected_y_lines) - 1):
            if detected_y_lines[i] < ty < detected_y_lines[i+1]:
                row_num = i 
                break
        
        # In this logic: Row 0 = Header, Row 1 = Question 1...
        if 1 <= row_num <= 20:
            col_num = int(tx / col_width)
            if 1 <= col_num <= 4:
                answer = cols_labels[col_num - 1]
                if row_num not in final_answers:
                    final_answers[row_num] = []
                if answer not in final_answers[row_num]:
                    final_answers[row_num].append(answer)

    return dict(sorted(final_answers.items()))
def generate_auto_grid_debug(img_path, output_path="auto_grid_debug.jpg"):
    img = cv2.imread(img_path)
    
    # --- 1. Perspective Warp (Same as before) ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_cnt = max(contours, key=cv2.contourArea)
    pts1 = order_points(cv2.approxPolyDP(table_cnt, 0.02 * cv2.arcLength(table_cnt, True), True).reshape(4, 2))
    dst_w, dst_h = 600, 1200 
    pts2 = np.float32([[0, 0], [dst_w, 0], [dst_w, dst_h], [0, dst_h]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (dst_w, dst_h))

    # --- 2. AUTOMATIC LINE DETECTION (Horizontal Projection) ---
    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    # Use Otsu's to find the black lines clearly
    _, binary = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Sum pixels horizontally (Projection)
    horizontal_sum = np.sum(binary, axis=1)
    
    # Find Y-coordinates where the sum is high (peaks = lines)
    detected_y_lines = []
    # threshold is 50% of the maximum width potential
    line_threshold = dst_w * 255 * 0.4 
    
    for y in range(len(horizontal_sum)):
        if horizontal_sum[y] > line_threshold:
            # Prevent detecting the same line multiple times (keep only one Y per line)
            if not detected_y_lines or abs(y - detected_y_lines[-1]) > 15:
                detected_y_lines.append(y)

    # --- 3. Process YOLO and Snapping ---
    results = model.predict(source=img_path, conf=0.2, verbose=False)
    boxes = results[0].boxes.xyxy.cpu().numpy()
    cols_labels = ['idx', 'a', 'b', 'c', 'd']
    col_width = dst_w / 5

    for box in boxes:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        p = np.array([[[cx, cy]]], dtype="float32")
        tp = cv2.perspectiveTransform(p, M)[0][0]
        tx, ty = tp[0], tp[1]

        # SNAP TO DETECTED LINES
        # Find which two detected lines the point falls between
        row_num = -1
        for i in range(len(detected_y_lines) - 1):
            if detected_y_lines[i] < ty < detected_y_lines[i+1]:
                row_num = i # This is the "Box" index
                break
        
        if row_num != -1:
            col_num = int(tx / col_width)
            ans = cols_labels[col_num] if col_num < 5 else "ERR"
            
            # Draw visual confirmation
            cv2.circle(warped, (int(tx), int(ty)), 8, (0, 255, 255), -1)
            cv2.putText(warped, f"Box{row_num}:{ans}", (int(tx)+10, int(ty)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Draw the detected lines in GREEN to show it's automatic
    for y in detected_y_lines:
        cv2.line(warped, (0, y), (dst_w, y), (0, 255, 0), 2)

    cv2.imwrite(output_path, warped)
# --- Execution ---
generate_auto_grid_debug(IMAGE_PATH)
results = get_row_specific_answers(IMAGE_PATH)
for q, ans in results.items():
    print(f"Row {q}: {ans}")


