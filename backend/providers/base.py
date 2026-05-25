from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseProvider(ABC):

    @abstractmethod
    async def ask(self, question: str) -> str:
        pass

    @abstractmethod
    async def ask_stream_messages(self, messages: list[dict]) -> AsyncIterator[str]:
        pass

    @classmethod
    @abstractmethod
    def required_fields(cls) -> list[str]:
        pass

    @classmethod
    @abstractmethod
    def provider_type(cls) -> str:
        pass
