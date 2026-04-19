import sys
import os
import tempfile
import logging
from pathlib import Path
from typing import Optional

from .models import DetectionResult, DetectedAnswer

logger = logging.getLogger(__name__)

SCRIPT_BASE_DIR = str(Path(__file__).resolve().parent.parent.parent / "student-answer-yolo" / "student-answer-yolo")
SCRIPT_DIR = os.path.join(SCRIPT_BASE_DIR, "scripts")

_extract_answers = None


def _import_script():
    """Import the actual extract_answers.py script from the student-answer-yolo project."""
    global _extract_answers
    if _extract_answers is not None:
        return _extract_answers

    original_cwd = os.getcwd()
    try:
        os.chdir(SCRIPT_BASE_DIR)

        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)

        import extract_answers
        _extract_answers = extract_answers
        logger.info(f"Imported extract_answers from: {SCRIPT_DIR}")
        logger.info(f"Script model loaded with CWD: {SCRIPT_BASE_DIR}")
        return _extract_answers
    finally:
        os.chdir(original_cwd)


class AnswerDetectionService:
    def __init__(self):
        self._script = None

    def load_model(self) -> bool:
        try:
            self._script = _import_script()
            if self._script is None:
                logger.error("Failed to import extract_answers script")
                return False
            logger.info("extract_answers script loaded successfully (same script, same model)")
            return True
        except Exception as e:
            logger.error(f"Failed to import extract_answers: {e}")
            return False

    def is_loaded(self) -> bool:
        return self._script is not None

    def detect_answers(self, image_bytes: bytes) -> DetectionResult:
        if not self.is_loaded():
            return DetectionResult(
                success=False,
                error_message="Script not loaded"
            )

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(image_bytes)

            raw_answers = self._script.get_row_specific_answers(tmp_path)

            answers = {}
            detected_list = []
            for q_num, ans_list in raw_answers.items():
                # Exactly one detected letter → use it; two or more (or none) → neither (empty)
                if len(ans_list) == 1:
                    answer = str(ans_list[0]).strip().upper()
                else:
                    answer = ""
                answers[q_num] = answer
                detected_list.append(DetectedAnswer(
                    question=q_num,
                    answer=answer,
                    confidence=1.0
                ))

            return DetectionResult(
                success=True,
                answers=answers,
                detected_answers=detected_list,
                total_detections=len(detected_list),
                method="EXTRACT_ANSWERS_SCRIPT"
            )

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return DetectionResult(
                success=False,
                error_message=str(e)
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


detection_service = AnswerDetectionService()
