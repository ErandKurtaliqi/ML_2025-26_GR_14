import logging
import os
import sys
import tempfile
from pathlib import Path

from .models import StudentIdResult

logger = logging.getLogger(__name__)

SCRIPT_BASE_DIR = str(Path(__file__).resolve().parent.parent.parent / "student-answer-yolo" / "student-answer-yolo")
SCRIPT_DIR = os.path.join(SCRIPT_BASE_DIR, "scripts")

_get_id_student = None


def _import_script():
    """Import the injected getIdStudent.py script from the student-answer-yolo project."""
    global _get_id_student
    if _get_id_student is not None:
        return _get_id_student

    original_cwd = os.getcwd()
    try:
        os.chdir(SCRIPT_BASE_DIR)

        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)

        import getIdStudent

        _get_id_student = getIdStudent
        logger.info("Imported getIdStudent from: %s", SCRIPT_DIR)
        return _get_id_student
    finally:
        os.chdir(original_cwd)


class StudentIdDetectionService:
    def __init__(self):
        self._script = None
        self._model = None

    def load_model(self) -> bool:
        try:
            self._script = _import_script()
            model_path = getattr(self._script, "DEFAULT_KERAS_MODEL", "")
            if not model_path or not os.path.isfile(model_path):
                logger.error("Handwriting model not found: %s", model_path)
                return False

            try:
                import tensorflow as tf
                self._model = tf.keras.models.load_model(model_path)
                logger.info("Student ID TensorFlow model loaded: %s", model_path)
            except Exception as tf_error:
                from .lightweight_keras import LightweightKerasDigitModel

                if not LightweightKerasDigitModel.can_load(model_path):
                    raise tf_error
                self._model = LightweightKerasDigitModel(model_path)
                logger.info(
                    "Student ID lightweight Keras model loaded: %s (TensorFlow unavailable: %s)",
                    model_path,
                    tf_error,
                )
            return True
        except Exception as e:
            logger.error("Failed to load student ID model: %s", e)
            return False

    def is_loaded(self) -> bool:
        return self._script is not None and self._model is not None

    def detect_student_id(self, image_bytes: bytes, file_name: str | None = None) -> StudentIdResult:
        if not self.is_loaded():
            return StudentIdResult(
                success=False,
                file_name=file_name,
                error_message="Student ID script/model not loaded",
            )

        tmp_path = None
        try:
            suffix = Path(file_name or "image.jpg").suffix or ".jpg"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(image_bytes)

            student_id = self._script.detect_handwritten_id_keras(tmp_path, self._model)
            student_id = (student_id or "").strip()
            success = len(student_id) == 5 and student_id.isdigit()

            return StudentIdResult(
                success=success,
                extracted_number=student_id if success else None,
                raw_ocr_text=student_id or None,
                confidence=100.0 if success else 0.0,
                file_name=file_name,
                method="GET_ID_STUDENT_KERAS_SCRIPT",
                error_message=None if success else "Could not extract a 5-digit student ID",
            )
        except Exception as e:
            logger.error("Student ID detection failed: %s", e)
            return StudentIdResult(
                success=False,
                file_name=file_name,
                error_message=str(e),
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


student_id_service = StudentIdDetectionService()
