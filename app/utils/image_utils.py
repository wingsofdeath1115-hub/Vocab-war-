from __future__ import annotations

from pathlib import Path
from typing import Iterable
from PIL import Image, ImageSequence
import cv2
import numpy as np


def ensure_transparent_png(image: Image.Image) -> Image.Image:
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    data = np.array(image)
    rgb = data[:, :, :3]
    near_white = (rgb > 245).all(axis=2)
    data[near_white, 3] = 0
    return Image.fromarray(data, mode="RGBA")


def extract_frames_from_video(video_path: Path, target_count: int) -> list[Image.Image]:
    frames: list[Image.Image] = []
    cap = cv2.VideoCapture(str(video_path))
    ok = True
    while ok:
        ok, frame = cap.read()
        if ok and frame is not None:
            rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            pil_image = Image.fromarray(rgba)
            frames.append(ensure_transparent_png(pil_image))
    cap.release()
    if not frames:
        return []
    if len(frames) <= target_count:
        return frames
    idx = np.linspace(0, len(frames) - 1, target_count, dtype=int)
    return [frames[i] for i in idx]


def extract_frames_from_gif(gif_path: Path, target_count: int) -> list[Image.Image]:
    image = Image.open(gif_path)
    frames = [ensure_transparent_png(frame.copy()) for frame in ImageSequence.Iterator(image)]
    if not frames:
        return []
    if len(frames) <= target_count:
        return frames
    idx = np.linspace(0, len(frames) - 1, target_count, dtype=int)
    return [frames[i] for i in idx]


def normalize_frames(frames: Iterable[Image.Image], width: int, height: int) -> list[Image.Image]:
    normalized: list[Image.Image] = []
    for frame in frames:
        frame = frame.convert("RGBA")
        bbox = frame.getbbox()
        crop = frame.crop(bbox) if bbox else frame

        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        x = (width - crop.width) // 2
        y = height - crop.height
        canvas.alpha_composite(crop, (max(0, x), max(0, y)))
        normalized.append(canvas)
    return normalized


def build_spritesheet(action_frames: dict[str, list[Image.Image]], width: int, height: int, cols: int) -> Image.Image:
    rows = len(action_frames)
    sheet = Image.new("RGBA", (cols * width, rows * height), (0, 0, 0, 0))
    for row, (_, frames) in enumerate(action_frames.items()):
        for col in range(cols):
            frame = frames[min(col, len(frames) - 1)]
            sheet.alpha_composite(frame, (col * width, row * height))
    return sheet
