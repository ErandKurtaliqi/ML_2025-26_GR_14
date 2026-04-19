import cv2
import numpy as np
from ultralytics import YOLO

MODEL_PATH = "runs/detect/runs/student_answer_v2/weights/best.pt"

IMAGE_PATH = "dataset/images/test/IMG_8177.jpg"
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
    
    warped = cv2.warpPerspective(img, M, (dst_w, dst_h))
    
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
            
            cv2.rectangle(warped, (x1, y1), (x2, y2), (255, 0, 0), 1)
            
            if r > 0 and c > 0:
                label = f"{r}{options[c]}"
                cv2.putText(warped, label, (x1+5, y2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    results = model.predict(source=img_path, conf=0.2, verbose=False)
    boxes = results[0].boxes.xyxy.cpu().numpy()

    for box in boxes:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        
        p = np.array([[[cx, cy]]], dtype="float32")
        tp = cv2.perspectiveTransform(p, M)[0][0]
        tx, ty = int(tp[0]), int(tp[1])
        
        row_num = int(ty / row_h)
        col_num = int(tx / col_w)

        if 0 <= row_num <= 20 and 0 <= col_num <= 4:
            cv2.circle(warped, (tx, ty), 10, (0, 255, 255), -1)
            cv2.circle(warped, (tx, ty), 11, (0, 0, 0), 2)
            
            result_label = f"Match -> R{row_num}:{options[col_num]}"
            cv2.putText(warped, result_label, (tx + 15, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imwrite(output_path, warped)
    print(f"Detailed Row Debug saved as: {output_path}")


def get_row_specific_answers(img_path):
    img = cv2.imread(img_path)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_cnt = max(contours, key=cv2.contourArea)
    
    approx = cv2.approxPolyDP(table_cnt, 0.02 * cv2.arcLength(table_cnt, True), True)
    if len(approx) != 4: approx = cv2.boxPoints(cv2.minAreaRect(table_cnt))
        
    pts1 = order_points(approx.reshape(4, 2))
    dst_w, dst_h = 500, 1000 
    pts2 = np.float32([[0, 0], [dst_w, 0], [dst_w, dst_h], [0, dst_h]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (dst_w, dst_h))

    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    horizontal_sum = np.sum(binary, axis=1)
    
    detected_y_lines = []
    line_threshold = dst_w * 255 * 0.4 
    
    for y in range(len(horizontal_sum)):
        if horizontal_sum[y] > line_threshold:
            if not detected_y_lines or abs(y - detected_y_lines[-1]) > 10:
                detected_y_lines.append(y)

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

        row_num = -1
        for i in range(len(detected_y_lines) - 1):
            if detected_y_lines[i] < ty < detected_y_lines[i+1]:
                row_num = i 
                break
        
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

    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    horizontal_sum = np.sum(binary, axis=1)
    
    detected_y_lines = []
    line_threshold = dst_w * 255 * 0.4 
    
    for y in range(len(horizontal_sum)):
        if horizontal_sum[y] > line_threshold:
            if not detected_y_lines or abs(y - detected_y_lines[-1]) > 15:
                detected_y_lines.append(y)

    results = model.predict(source=img_path, conf=0.2, verbose=False)
    boxes = results[0].boxes.xyxy.cpu().numpy()
    cols_labels = ['idx', 'a', 'b', 'c', 'd']
    col_width = dst_w / 5

    for box in boxes:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        p = np.array([[[cx, cy]]], dtype="float32")
        tp = cv2.perspectiveTransform(p, M)[0][0]
        tx, ty = tp[0], tp[1]

        row_num = -1
        for i in range(len(detected_y_lines) - 1):
            if detected_y_lines[i] < ty < detected_y_lines[i+1]:
                row_num = i
                break
        
        if row_num != -1:
            col_num = int(tx / col_width)
            ans = cols_labels[col_num] if col_num < 5 else "ERR"
            
            cv2.circle(warped, (int(tx), int(ty)), 8, (0, 255, 255), -1)
            cv2.putText(warped, f"Box{row_num}:{ans}", (int(tx)+10, int(ty)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    for y in detected_y_lines:
        cv2.line(warped, (0, y), (dst_w, y), (0, 255, 0), 2)

    cv2.imwrite(output_path, warped)
generate_auto_grid_debug(IMAGE_PATH)
results = get_row_specific_answers(IMAGE_PATH)
for q, ans in results.items():
    print(f"Row {q}: {ans}")


