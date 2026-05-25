import json
import anthropic
from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, config: dict):
        self.client = anthropic.Anthropic(api_key=config["api_key"])
        self.model = config["model"]

    @classmethod
    def provider_type(cls) -> str:
        return "anthropic"

    @classmethod
    def required_fields(cls) -> list[str]:
        return ["api_key", "model"]

    async def ask(self, question: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": question}],
        )
        return message.content[0].text

    async def ask_stream(self, question: str):
        """Yield NDJSON chunks in the same format as Ollama for frontend compatibility."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": question}],
            )
            text = message.content[0].text
            yield json.dumps({"response": text, "done": False}) + "\n"
            yield json.dumps({"response": "", "done": True}) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
