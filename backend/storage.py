import json
import os
import uuid
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
ENTRIES_FILE = DATA_DIR / "entries.json"
KEYS_FILE = DATA_DIR / "keys.json"

# Fields that must never be returned to the frontend
_SENSITIVE_FIELD_NAMES = {"api_key", "secret", "token"}


def _load_entries() -> list[dict]:
    if not ENTRIES_FILE.exists():
        return []
    return json.loads(ENTRIES_FILE.read_text())


def _save_entries(entries: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ENTRIES_FILE.write_text(json.dumps(entries, indent=2))


def _load_keys() -> dict:
    if not KEYS_FILE.exists():
        return {}
    return json.loads(KEYS_FILE.read_text())


def _save_keys(keys: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2))


def _safe_config(config: dict) -> dict:
    return {k: v for k, v in config.items() if k not in _SENSITIVE_FIELD_NAMES}


def list_entries() -> list[dict]:
    keys = _load_keys()
    result = []
    for entry in _load_entries():
        result.append({
            **entry,
            "config": _safe_config(entry.get("config", {})),
            "has_key": bool(keys.get(entry["id"])),
        })
    return result


def get_raw_entry(entry_id: str) -> dict | None:
    """Return entry with key fields merged in — for internal use only."""
    entries = _load_entries()
    keys = _load_keys()
    for entry in entries:
        if entry["id"] == entry_id:
            merged_config = {**entry.get("config", {}), **keys.get(entry_id, {})}
            return {**entry, "config": merged_config}
    return None


def add_entry(label: str, provider_type: str, config: dict, key_fields: dict | None = None) -> dict:
    entries = _load_entries()
    keys = _load_keys()

    entry_id = uuid.uuid4().hex[:8]
    safe_cfg = _safe_config(config)
    entry = {"id": entry_id, "label": label, "provider_type": provider_type, "config": safe_cfg}
    entries.append(entry)
    _save_entries(entries)

    if key_fields:
        keys[entry_id] = key_fields
        _save_keys(keys)

    return {**entry, "has_key": bool(key_fields)}


def remove_entry(entry_id: str) -> bool:
    entries = _load_entries()
    new_entries = [e for e in entries if e["id"] != entry_id]
    if len(new_entries) == len(entries):
        return False
    _save_entries(new_entries)

    keys = _load_keys()
    keys.pop(entry_id, None)
    _save_keys(keys)
    return True


def seed_default_entry(ollama_base_url: str, model: str) -> None:
    """Called on startup when entries.json does not exist yet."""
    if ENTRIES_FILE.exists():
        return
    add_entry(
        label="local",
        provider_type="ollama",
        config={"model": model, "base_url": ollama_base_url},
    )
