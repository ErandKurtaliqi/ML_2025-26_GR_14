import uvicorn
import os
from app.config import API_HOST, API_PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=os.environ.get("YOLO_API_RELOAD", "").lower() in ("1", "true", "yes")
    )
