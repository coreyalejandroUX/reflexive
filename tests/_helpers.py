import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for sub in ("mobile", "study", "study/redteam"):
    sys.path.insert(0, str(ROOT / sub))


def envelope(**overrides):
    text = overrides.pop("text", "Lost the tutor chat after opening the bus ticket.")
    env = {
        "envelope_version": "0.1",
        "capture_id": "m-20261027T081512Z-a1b2",
        "captured_at": "2026-10-27T08:15:12-05:00",
        "device": "iphone",
        "capture_type": "context_loss",
        "fidelity": "user-supplied",
        "text": text,
        "text_method": "dictation",
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    env.update(overrides)
    return env


def write_envelope(inbox: Path, env: dict, name=None) -> Path:
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / (name or f"{env['capture_id']}.json")
    path.write_text(json.dumps(env, sort_keys=True), encoding="utf-8")
    return path


def tree_hash(folder: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(folder.rglob("*")):
        if p.is_file():
            h.update(p.name.encode())
            h.update(p.read_bytes())
    return h.hexdigest()
