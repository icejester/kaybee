from .ollama_provider import OllamaProvider
from .anthropic_provider import AnthropicProvider

PROVIDER_REGISTRY: dict[str, type] = {
    OllamaProvider.provider_type(): OllamaProvider,
    AnthropicProvider.provider_type(): AnthropicProvider,
}


def get_provider_class(provider_type: str):
    cls = PROVIDER_REGISTRY.get(provider_type)
    if not cls:
        raise ValueError(f"Unknown provider type: {provider_type}")
    return cls


def list_provider_types() -> list[dict]:
    return [
        {
            "type": cls.provider_type(),
            "required_fields": cls.required_fields(),
        }
        for cls in PROVIDER_REGISTRY.values()
    ]
