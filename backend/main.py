import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
MODEL = os.getenv("MODEL", "qwen2.5-coder:7b")

app = FastAPI(title="Kaybee")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL}


@app.post("/ask")
async def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    payload = {
        "model": MODEL,
        "prompt": req.question.strip(),
        "stream": True,
    }

    async def stream_response():
        async with httpx.AsyncClient(timeout=120) as client:
            try:
                async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/generate", json=payload) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_text():
                        yield chunk
            except httpx.ConnectError:
                yield '{"error": "Cannot connect to Ollama. Is it running?"}'
            except httpx.HTTPStatusError as e:
                yield f'{{"error": "Ollama returned {e.response.status_code}"}}'

    return StreamingResponse(stream_response(), media_type="application/x-ndjson")
