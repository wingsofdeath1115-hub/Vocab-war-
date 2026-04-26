from pathlib import Path
import shutil

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import BuildRequest, BuildResponse
from app.services.pipeline import AssetPipeline

app = FastAPI(title="AI Animated Asset Pipeline")
pipeline = AssetPipeline()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/api/build", response_model=BuildResponse)
async def build_asset(
    image: UploadFile = File(...),
    character_name: str = Form("Knight_Lancer_2D"),
    style_prompt: str = Form(""),
    frame_width: int = Form(128),
    frame_height: int = Form(128),
    frames_per_action: int = Form(8),
    actions: str = Form("idle,walk,attack,hurt"),
    tags: str = Form("2D,cartoon,auto-chess,lancer"),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    temp_path = Path("output") / f"upload_{image.filename}"
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    req = BuildRequest(
        character_name=character_name,
        style_prompt=style_prompt,
        frame_width=frame_width,
        frame_height=frame_height,
        frames_per_action=frames_per_action,
        actions=[a.strip().lower() for a in actions.split(",") if a.strip()],
        tags=[t.strip() for t in tags.split(",") if t.strip()],
    )

    result = pipeline.run(temp_path, req)
    return BuildResponse(**result)


@app.get("/api/download/{job_id}")
def download_zip(job_id: str):
    candidates = list(Path("output").glob(f"{job_id}/*_asset.zip"))
    if not candidates:
        raise HTTPException(status_code=404, detail="ZIP not found")
    return FileResponse(candidates[0], media_type="application/zip", filename=candidates[0].name)
