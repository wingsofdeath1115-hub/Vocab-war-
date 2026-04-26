from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    app_name: str = "AI-to-Animated-Game-Asset Pipeline"
    output_dir: Path = Path("output")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    banana_api_key: str | None = os.getenv("BANANA_API_KEY")
    banana_model_key: str | None = os.getenv("BANANA_MODEL_KEY")
    replicate_api_token: str | None = os.getenv("REPLICATE_API_TOKEN")


settings = Settings()
settings.output_dir.mkdir(parents=True, exist_ok=True)
