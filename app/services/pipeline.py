from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import json
import zipfile

from app.config import settings
from app.schemas import BuildRequest
from app.services.ai_clients import GeminiClient, VideoGenerationClient
from app.utils.image_utils import (
    extract_frames_from_gif,
    normalize_frames,
    build_spritesheet,
)

ACTION_PROMPTS = {
    "idle": "Subtle breathing, blinking, small weight shift loop, clear profile view.",
    "walk": "Smooth side-view walk cycle, clear leg swing, consistent body profile.",
    "attack": "Swift forward thrust of weapon/fist, high impact, return to idle stance.",
    "hurt": "Brief recoil and stagger, visible reaction to damage, return to neutral.",
}


class AssetPipeline:
    def __init__(self):
        self.gemini = GeminiClient(settings.gemini_api_key, settings.gemini_model)
        self.video = VideoGenerationClient(settings.banana_api_key, settings.banana_model_key)

    def run(self, source_image: Path, req: BuildRequest) -> dict[str, str]:
        job_id = uuid4().hex[:12]
        job_dir = settings.output_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        cutout_path = job_dir / "character_cutout.png"
        self.gemini.segment_character(source_image, cutout_path)

        action_frames: dict[str, list] = {}
        for action in req.actions:
            clip_path = job_dir / f"{action}.gif"
            combined_prompt = f"{req.style_prompt}\n{ACTION_PROMPTS[action]}"
            self.video.generate_action_clip(action, cutout_path, combined_prompt, clip_path)
            frames = extract_frames_from_gif(clip_path, req.frames_per_action)
            action_frames[action] = normalize_frames(frames, req.frame_width, req.frame_height)

        spritesheet = build_spritesheet(action_frames, req.frame_width, req.frame_height, req.frames_per_action)
        spritesheet_name = f"{req.character_name.lower()}_spritesheet.png"
        spritesheet_path = job_dir / spritesheet_name
        spritesheet.save(spritesheet_path, "PNG")

        metadata = {
            "name": req.character_name,
            "version": "1.0",
            "texture": spritesheet_name,
            "frame_dimensions": {"width": req.frame_width, "height": req.frame_height},
            "animations": {},
            "tags": req.tags,
        }

        for row, action in enumerate(req.actions):
            metadata["animations"][action] = {
                "row": row,
                "start_col": 0,
                "frame_count": req.frames_per_action,
                "speed_fps": 10 if action != "attack" else 12,
                "loop": action != "attack",
            }

        metadata_path = job_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        zip_path = job_dir / f"{req.character_name.lower()}_asset.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(spritesheet_path, arcname=spritesheet_name)
            zf.write(metadata_path, arcname="metadata.json")

        return {
            "job_id": job_id,
            "zip_path": str(zip_path),
            "metadata_path": str(metadata_path),
            "spritesheet_path": str(spritesheet_path),
        }
