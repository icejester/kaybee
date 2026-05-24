import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from providers.registry import list_provider_types, get_provider_class
from providers.ollama_provider import OllamaProvider
from providers.anthropic_provider import AnthropicProvider
import storage

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
MODEL = os.getenv("MODEL", "qwen2.5-coder:7b")

app = FastAPI(title="Kaybee")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    storage.seed_default_entry(OLLAMA_BASE_URL, MODEL)


VERBOSITY_PREFIXES = {
    "concise": (
        "Respond with only what was asked for — the command, code, or answer. "
        "No explanation, no preamble, no commentary. Be terse and exact."
        "\n\n"
    ),
    "verbose": (
        "Provide the answer (command, code, or solution) followed by a clear explanation "
        "of how it works and why."
        "\n\n"
    ),
}


# --- Request / Response models ---

class AskRequest(BaseModel):
    question: str
    entry_id: str
    mode: str = "concise"


class AddEntryRequest(BaseModel):
    label: str
    provider_type: str
    config: dict = {}
    key_fields: dict = {}


# --- Endpoints ---

@app.get("/health")
async def health():
    entries = storage.list_entries()
    active = entries[0] if entries else None
    label = active["label"] if active else "no model configured"
    return {"status": "ok", "model": label}


@app.get("/providers")
async def providers():
    return list_provider_types()


@app.get("/entries")
async def entries():
    return storage.list_entries()


@app.post("/entries")
async def add_entry(req: AddEntryRequest):
    # Validate provider type exists
    get_provider_class(req.provider_type)  # raises ValueError if unknown

    # Separate sensitive key fields from safe config fields
    provider_cls = get_provider_class(req.provider_type)
    sensitive = {f for f in provider_cls.required_fields() if f in {"api_key", "secret", "token"}}

    safe_config = {k: v for k, v in req.config.items() if k not in sensitive}
    key_fields = {k: v for k, v in req.config.items() if k in sensitive}
    # Also accept explicit key_fields from the request body
    key_fields.update(req.key_fields)

    try:
        entry = storage.add_entry(
            label=req.label,
            provider_type=req.provider_type,
            config=safe_config,
            key_fields=key_fields or None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return entry


@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str):
    removed = storage.remove_entry(entry_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"ok": True}


@app.post("/ask")
async def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    raw = storage.get_raw_entry(req.entry_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    prefix = VERBOSITY_PREFIXES.get(req.mode, VERBOSITY_PREFIXES["concise"])
    prompt = prefix + req.question.strip()

    try:
        provider_cls = get_provider_class(raw["provider_type"])
        provider = provider_cls(raw["config"])
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def stream():
        async for chunk in provider.ask_stream(prompt):
            yield chunk

    return StreamingResponse(stream(), media_type="application/x-ndjson")
