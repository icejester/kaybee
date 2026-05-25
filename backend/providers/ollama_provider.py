import json
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
        async for chunk in self.ask_stream_messages([{"role": "user", "content": question}]):
            yield chunk

    async def ask_stream_messages(self, messages: list[dict]):
        """Yield NDJSON chunks from Ollama /api/chat for multi-turn streaming."""
        payload = {"model": self.model, "messages": messages, "stream": True}
        async with httpx.AsyncClient(timeout=120) as client:
            try:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            done = data.get("done", False)
                            yield json.dumps({"response": content, "done": done}) + "\n"
                        except json.JSONDecodeError:
                            pass
            except httpx.ConnectError:
                yield '{"error": "Cannot connect to Ollama. Is it running?"}\n'
            except httpx.HTTPStatusError as e:
                yield f'{{"error": "Ollama returned {e.response.status_code}"}}\n'
