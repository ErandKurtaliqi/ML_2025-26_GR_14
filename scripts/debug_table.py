import cv2
from ultralytics import YOLO

IMAGE_PATH = "dataset/images/test/20260309_210021.jpg"
MODEL_PATH = "runs/detect/runs/student_answer_detection/weights/best.pt"

TABLE_X1 = 2180    
TABLE_X2 = 1600    
TABLE_Y1 = 2200     
TABLE_Y2 = 1055    

NUM_ROWS = 20
NUM_COLS = 4

model = YOLO(MODEL_PATH)

results = model.predict(
    source=IMAGE_PATH,
    conf=0.25,
    save=False
)

img = cv2.imread(IMAGE_PATH)
if img is None:
    raise ValueError("Nuk u lexua imazhi.")

cv2.rectangle(img, (TABLE_X1, TABLE_Y1), (TABLE_X2, TABLE_Y2), (0, 255, 0), 2)

row_h = (TABLE_Y2 - TABLE_Y1) / NUM_ROWS
col_w = (TABLE_X2 - TABLE_X1) / NUM_COLS

for i in range(NUM_ROWS + 1):
    y = int(TABLE_Y1 + i * row_h)
    cv2.line(img, (TABLE_X1, y), (TABLE_X2, y), (0, 255, 255), 1)

for j in range(NUM_COLS + 1):
    x = int(TABLE_X1 + j * col_w)
    cv2.line(img, (x, TABLE_Y1), (x, TABLE_Y2), (255, 255, 0), 1)

for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = float(box.conf[0])

        x_center = int((x1 + x2) / 2)
        y_center = int((y1 + y2) / 2)

        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        cv2.circle(img, (x_center, y_center), 4, (0, 0, 255), -1)

        cv2.putText(
            img,
            f"{conf:.2f}",
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 255),
            1,
            cv2.LINE_AA
        )

output_path = "test_images/debug_table.jpg"
cv2.imwrite(output_path, img)

print(f"Debug image saved to: {output_path}")