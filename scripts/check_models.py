import base64
import sys
import time
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from deskreject.config import settings


def create_test_image():
    img = Image.new("RGB", (256, 256), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((128, 128), "ANON", fill="black", anchor="mm")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def check_endpoint(ep, is_host=False):
    client = httpx.Client(timeout=30.0)
    result = {
        "endpoint": ep.url,
        "reachable": False,
        "model_present": False,
        "text_ok": False,
        "vision_ok": False,
        "first_call_s": 0.0,
        "second_call_s": 0.0,
    }

    try:
        r = client.get(f"{ep.url}/api/tags")
        if r.status_code == 200:
            result["reachable"] = True
            tags = r.json().get("models", [])
            model_names = [m.get("name") for m in tags]

            # Simple match
            if any(ep.model in m for m in model_names):
                result["model_present"] = True
            else:
                base_model = ep.model.split(":")[0]
                if any(m.startswith(base_model) for m in model_names):
                    result["model_present"] = True
    except Exception:  # noqa: BLE001
        return result

    try:
        t0 = time.time()
        payload = {
            "model": ep.model,
            "messages": [{"role": "user", "content": "Reply with 'OK'."}],
            "stream": False
        }
        r = client.post(f"{ep.url}/api/chat", json=payload)
        t1 = time.time()
        result["first_call_s"] = round(t1 - t0, 2)
        if r.status_code == 200:
            result["text_ok"] = True
    except Exception:  # noqa: BLE001, S110
        pass

    img_b64 = create_test_image()
    try:
        t0 = time.time()
        payload = {
            "model": ep.model,
            "messages": [
                {
                    "role": "user",
                    "content": "What is the text in the image?",
                    "images": [img_b64],
                }
            ],
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
        r = client.post(f"{ep.url}/api/chat", json=payload)
        t1 = time.time()
        result["second_call_s"] = round(t1 - t0, 2)
        if r.status_code == 200:
            result["vision_ok"] = True
    except Exception:  # noqa: BLE001, S110
        pass

    return result

def main():
    print(
        f"{'Endpoint':<30} | {'Reachable':<10} | {'Model':<10} | "
        f"{'Text OK':<10} | {'Vision OK':<10} | {'T1 (s)':<8} | {'T2 (s)':<8}"
    )
    print("-" * 115)

    host_ok = False

    for i, ep in enumerate(settings.ollama_vision_endpoints):
        is_host = (i == 0)
        res = check_endpoint(ep, is_host)

        print(
            f"{res['endpoint']:<30} | {res['reachable']!s:<10} | "
            f"{res['model_present']!s:<10} | {res['text_ok']!s:<10} | "
            f"{res['vision_ok']!s:<10} | {res['first_call_s']:<8} | "
            f"{res['second_call_s']:<8}"
        )

        if is_host and res["reachable"]:
            host_ok = True

    if not host_ok:
        print("ERROR: Host endpoint failed to connect.")
        sys.exit(1)

if __name__ == "__main__":
    main()
