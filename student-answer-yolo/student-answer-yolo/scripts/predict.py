
from ultralytics import YOLO

model = YOLO("runs/detect/runs/student_answer_v2/weights/best.pt")

results = model.predict(
    source="dataset/images/test",
    conf=0.15,
    save=True
)

def get_option(x_center):
    if 720 <= x_center < 780:
        return "A"
    elif 780 <= x_center < 840:
        return "B"
    elif 840 <= x_center < 900:
        return "C"
    elif 900 <= x_center < 960:
        return "D"
    return None

def get_question(y_center):
    start_y = 300
    row_height = 18

    question = int((y_center - start_y) / row_height) + 1

    if 1 <= question <= 20:
        return question
    return None

answers = {}

for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2

        question = get_question(y_center)
        option = get_option(x_center)

        if question is not None and option is not None:
            answers[question] = option

for q in sorted(answers.keys()):
    print(f"{q}: {answers[q]}")