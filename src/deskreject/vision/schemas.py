ANONYMITY_SCHEMA = {
  "type": "object",
  "properties": {
    "found": {"type": "boolean"},
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kind": {"type": "string", "enum": ["logo", "crest", "text", "watermark", "badge", "other"]},
          "description": {"type": "string"},
          "text": {"type": ["string", "null"]},
          "confidence": {"type": "number"}
        },
        "required": ["kind", "description", "confidence"]
      }
    }
  },
  "required": ["found", "items"]
}

PANEL_SCHEMA = {
  "type": "object",
  "properties": {
    "labels": {"type": "array", "items": {"type": "string"}},
    "panel_count": {"type": "integer"},
    "confidence": {"type": "number"}
  },
  "required": ["labels", "panel_count", "confidence"]
}
