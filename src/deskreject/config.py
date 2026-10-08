import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Endpoint(BaseModel):
    model: str
    url: str

class Settings(BaseModel):
    ollama_vision_endpoints: list[Endpoint]
    text_model: str
    coder_model: str
    vision_enabled: bool = True
    vision_max_px: int = 1024
    vision_max_crops: int = 12
    vision_timeout_s: int = 90
    cache_dir: Path = Path(".cache")
    default_preset: str = "neurips-style-double-blind"

def load_settings() -> Settings:
    vision_endpoints = []
    endpoints_str = os.getenv("OLLAMA_VISION_ENDPOINTS", "")
    if endpoints_str:
        for ep in endpoints_str.split(","):
            ep = ep.strip()
            if "@" in ep:
                model, url = ep.split("@", 1)
                vision_endpoints.append(Endpoint(model=model, url=url))

    return Settings(
        ollama_vision_endpoints=vision_endpoints,
        text_model=os.getenv("TEXT_MODEL", "gemma4:12b-it-qat@http://127.0.0.1:11434"),
        coder_model=os.getenv("CODER_MODEL", "qwen2.5-coder:14b@http://127.0.0.1:11434"),
        vision_enabled=os.getenv("VISION_ENABLED", "true").lower() == "true",
        vision_max_px=int(os.getenv("VISION_MAX_PX", "1024")),
        vision_max_crops=int(os.getenv("VISION_MAX_CROPS", "12")),
        vision_timeout_s=int(os.getenv("VISION_TIMEOUT_S", "90")),
        cache_dir=Path(os.getenv("CACHE_DIR", ".cache")),
        default_preset=os.getenv("DEFAULT_PRESET", "neurips-style-double-blind"),
    )

settings = load_settings()
