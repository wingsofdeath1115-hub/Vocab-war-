from __future__ import annotations

from pathlib import Path
import requests
from PIL import Image, ImageEnhance
from app.utils.image_utils import ensure_transparent_png


class GeminiClient:
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model

    def segment_character(self, input_path: Path, output_path: Path) -> Path:
        """
        Demo-safe implementation:
        - If GEMINI key exists, this is where API call would go.
        - Fallback: light cleanup + transparent near-white background.
        """
        image = Image.open(input_path).convert("RGBA")
        image = ImageEnhance.Sharpness(image).enhance(1.2)
        image = ensure_transparent_png(image)
        image.save(output_path, "PNG")
        return output_path


class VideoGenerationClient:
    def __init__(self, banana_api_key: str | None, banana_model_key: str | None):
        self.banana_api_key = banana_api_key
        self.banana_model_key = banana_model_key

    def generate_action_clip(
        self,
        action: str,
        character_png: Path,
        prompt: str,
        output_path: Path,
    ) -> Path:
        """
        Placeholder API connector. For production:
        - call Banana/Replicate API and save mp4/gif output_path.
        This fallback emits a synthetic GIF-like frame source via PNG sequence semantics.
        """
        base = Image.open(character_png).convert("RGBA")
        frames: list[Image.Image] = []
        for i in range(8):
            frame = base.copy()
            shift = (i % 4) - 2
            canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            canvas.alpha_composite(frame, (shift * 2, 0))
            frames.append(canvas)

        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=80,
            loop=0,
            disposal=2,
            transparency=0,
        )
        return output_path


def download_file(url: str, path: Path) -> Path:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path
