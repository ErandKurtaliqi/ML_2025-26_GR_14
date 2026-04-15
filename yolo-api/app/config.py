import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = os.getenv(
    "YOLO_MODEL_PATH",
    str(BASE_DIR.parent / "student-answer-yolo" / "student-answer-yolo" / "runs" / "detect" / "runs" / "student_answer_detection" / "weights" / "best.pt")
)

NUM_ROWS = 20
NUM_COLS = 4
OPTIONS = ["A", "B", "C", "D"]

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
