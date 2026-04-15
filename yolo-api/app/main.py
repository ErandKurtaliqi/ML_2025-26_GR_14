from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .detection_service import detection_service, SCRIPT_BASE_DIR
from .models import DetectionResult, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting YOLO Answer Detection API...")
    if not detection_service.load_model():
        logger.warning("Failed to load YOLO model - API will return errors until model is available")
    yield
    logger.info("Shutting down YOLO Answer Detection API...")


app = FastAPI(
    title="YOLO Answer Detection API",
    description="API for detecting marked answers on exam sheets using YOLO",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if detection_service.is_loaded() else "degraded",
        model_loaded=detection_service.is_loaded(),
        model_path=SCRIPT_BASE_DIR
    )


@app.post("/detect", response_model=DetectionResult)
async def detect_answers(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (jpg, png, etc.)"
        )

    try:
        contents = await file.read()
        result = detection_service.detect_answers(contents)
        return result
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/batch", response_model=list[DetectionResult])
async def detect_answers_batch(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            results.append(DetectionResult(
                success=False,
                error_message=f"File {file.filename} is not an image"
            ))
            continue

        try:
            contents = await file.read()
            result = detection_service.detect_answers(contents)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            results.append(DetectionResult(
                success=False,
                error_message=str(e)
            ))

    return results


if __name__ == "__main__":
    import uvicorn
    from .config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
