from pydantic import BaseModel
from typing import Optional


class DetectedAnswer(BaseModel):
    question: int
    answer: str
    confidence: float


class DetectionResult(BaseModel):
    success: bool
    answers: dict[int, str] = {}
    detected_answers: list[DetectedAnswer] = []
    total_detections: int = 0
    method: str = ""
    error_message: Optional[str] = None


class StudentIdResult(BaseModel):
    success: bool
    extracted_number: Optional[str] = None
    raw_ocr_text: Optional[str] = None
    confidence: float = 0.0
    file_name: Optional[str] = None
    method: str = ""
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
