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
        async for chunk in self.ask_stream_messages([{"role": "user", "content": question}]):
            yield chunk

    async def ask_stream_messages(self, messages: list[dict]):
        """Yield NDJSON chunks in the same format as Ollama for frontend compatibility."""
        # Anthropic requires messages to alternate user/assistant and start with user.
        # System messages must be passed separately; filter them out here.
        api_messages = [m for m in messages if m["role"] != "system"]
        system_msgs = [m["content"] for m in messages if m["role"] == "system"]
        system = system_msgs[0] if system_msgs else anthropic.NOT_GIVEN

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=api_messages,
            )
            text = message.content[0].text
            yield json.dumps({"response": text, "done": False}) + "\n"
            yield json.dumps({"response": "", "done": True}) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
