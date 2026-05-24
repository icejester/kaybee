import httpx
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self, config: dict):
        self.base_url = config.get("base_url", "http://ollama:11434")
        self.model = config["model"]

    @classmethod
    def provider_type(cls) -> str:
        return "ollama"

    @classmethod
    def required_fields(cls) -> list[str]:
        return ["model", "base_url"]

    async def ask(self, question: str) -> str:
        payload = {"model": self.model, "prompt": question, "stream": False}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json()["response"]

    async def ask_stream(self, question: str):
        """Yield raw NDJSON chunks from Ollama for streaming passthrough."""
        payload = {"model": self.model, "prompt": question, "stream": True}
        async with httpx.AsyncClient(timeout=120) as client:
            try:
                async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_text():
                        yield chunk
            except httpx.ConnectError:
                yield '{"error": "Cannot connect to Ollama. Is it running?"}'
            except httpx.HTTPStatusError as e:
                yield f'{{"error": "Ollama returned {e.response.status_code}"}}'
