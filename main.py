
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid

app = FastAPI(
    title="WAYNE AI VIDEO TRANSLATOR",
    description="AI Video Translation to Khmer",
    version="1.0.0"
)

# Allow website connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary upload folder
UPLOAD_DIR = Path("/tmp/wayne_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def home():
    return {
        "name": "WAYNE AI",
        "message": "WAYNE AI Backend is running!",
        "target_language": "Khmer",
        "status": "online"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "WAYNE AI"
    }

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    if Path(file.filename).suffix.lower() != ".mp4":
        raise HTTPException(
            status_code=400,
            detail="Please upload an MP4 file"
        )

    job_id = str(uuid.uuid4())
    safe_name = f"{job_id}.mp4"
    file_path = UPLOAD_DIR / safe_name

    max_size = 500 * 1024 * 1024
    total_size = 0

    try:
        with file_path.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail="Video exceeds 500 MB limit"
                    )

                buffer.write(chunk)

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "size_bytes": total_size,
        "status": "uploaded",
        "message": "Video uploaded successfully. AI processing is not connected yet."
    }
  
