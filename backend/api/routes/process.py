import asyncio
import os

from fastapi import APIRouter, HTTPException

from api.models.schemas import ProcessRequest
from api.core.file_manager import scan_folder
from api.core.separator import separate_file
from api.core.profiler import measure

router = APIRouter()


@router.post("/process")
async def process(request: ProcessRequest):
    if not os.path.isdir(request.input_folder):
        raise HTTPException(status_code=500, detail=f"input_folder not found: {request.input_folder}")

    audio_files = scan_folder(request.input_folder)
    processed: list[dict] = []
    errors: list[dict] = []

    for file_path in audio_files:
        try:
            # Demucs est lourd sur le CPU et la RAM donc déporté sur un thread système, évite de bloquer l'API
            _, stats = await asyncio.to_thread(measure, separate_file, file_path, request.output_folder)
            processed.append({"file": file_path, "stats": stats})
        except Exception as e:
            errors.append({"file": file_path, "error": str(e)})

    return {
        "processed": processed,
        "errors": errors,
    }
