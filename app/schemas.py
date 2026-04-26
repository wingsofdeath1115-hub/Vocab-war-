from pydantic import BaseModel, Field
from typing import Literal

ActionName = Literal["idle", "walk", "attack", "hurt"]


class BuildRequest(BaseModel):
    character_name: str = Field(default="Knight_Lancer_2D")
    style_prompt: str = Field(default="")
    frame_width: int = 128
    frame_height: int = 128
    frames_per_action: int = 8
    actions: list[ActionName] = Field(default_factory=lambda: ["idle", "walk", "attack", "hurt"])
    tags: list[str] = Field(default_factory=lambda: ["2D", "cartoon", "auto-chess", "lancer"])


class BuildResponse(BaseModel):
    job_id: str
    zip_path: str
    metadata_path: str
    spritesheet_path: str
