"""FastAPI application — entry point for the Retail Medallion Pipeline."""
from __future__ import annotations

import asyncio
from pathlib import Path

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agents.orchestrator import Orchestrator

BASE_DIR = Path(__file__).parent
DATA_RAW = BASE_DIR / "data" / "raw"
REPORTS_DIR = BASE_DIR / "reports"
MAX_CSV_BYTES = 50 * 1024 * 1024  # 50 MB

app = FastAPI(title="Retail Medallion Pipeline")

# Static mounts
app.mount("/data", StaticFiles(directory=str(BASE_DIR / "data")), name="data")

DATA_RAW.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
for sub in ("bronze", "silver", "gold"):
    (BASE_DIR / "data" / sub).mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = BASE_DIR / "frontend" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    dest = DATA_RAW / file.filename
    size = 0
    async with aiofiles.open(dest, "wb") as f:
        while chunk := await file.read(65536):
            size += len(chunk)
            if size > MAX_CSV_BYTES:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File exceeds 50 MB limit.")
            await f.write(chunk)

    return {"file_id": file.filename, "file_path": str(dest), "size_bytes": size}


@app.get("/run/{file_id}")
async def run_pipeline(file_id: str):
    file_path = DATA_RAW / file_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    async def event_stream():
        orchestrator = Orchestrator(file_path, base_dir=BASE_DIR)
        async for event in orchestrator.run():
            yield event
            await asyncio.sleep(0)  # yield control to event loop

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/reports/{filename}")
async def serve_report(filename: str):
    report_path = REPORTS_DIR / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(str(report_path), media_type="text/html")
