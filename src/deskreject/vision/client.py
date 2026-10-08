import base64
import json
from io import BytesIO

import httpx
from PIL import Image

from deskreject.config import Endpoint, settings
from deskreject.netguard import make_client


class OllamaVisionClient:
    """Client for Ollama vision API, with image downscaling and netguard."""

    def __init__(self, endpoint: Endpoint, client: httpx.Client | None = None) -> None:
        self.endpoint = endpoint
        self.client = client or make_client(settings)

    def chat(self, image_png: bytes, prompt: str, schema: dict, timeout: int = 90) -> dict:
        """Send an image to Ollama and return the parsed JSON response."""
        # Downscale image if needed
        img = Image.open(BytesIO(image_png))
        max_px = settings.vision_max_px
        if img.width > max_px or img.height > max_px:
            ratio = max_px / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

        payload = {
            "model": self.endpoint.model,
            "stream": False,
            "format": schema,
            "options": {
                "temperature": 0,
                "seed": 7,
                "num_ctx": 4096,
            },
            "keep_alive": "30m",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [b64_img],
                }
            ],
        }

        response = self.client.post(f"{self.endpoint.url}/api/chat", json=payload, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        content = data.get("message", {}).get("content", "{}")
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from vision model: {content}")
