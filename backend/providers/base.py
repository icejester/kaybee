from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    async def ask(self, question: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def required_fields(cls) -> list[str]:
        pass

    @classmethod
    @abstractmethod
    def provider_type(cls) -> str:
        pass
