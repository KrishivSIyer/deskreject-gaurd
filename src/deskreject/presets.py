from pathlib import Path

import yaml

from deskreject.models import Preset


def load_preset(preset_id: str) -> Preset:
    preset_path = Path(__file__).resolve().parent.parent.parent / "presets" / f"{preset_id}.yaml"
    with open(preset_path, "r") as f:
        data = yaml.safe_load(f)
    return Preset(**data)
