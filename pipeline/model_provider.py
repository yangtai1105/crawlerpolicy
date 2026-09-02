"""Provider-neutral structured model calls backed by Gemini."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StructuredModel(Protocol):
    async def generate(
        self,
        *,
        response_model: type[T],
        system_instruction: str,
        prompt: str,
    ) -> T:
        """Return model output validated against ``response_model``."""
        raise NotImplementedError


class ProviderFailure(RuntimeError):
    """A normalized model-provider failure safe for orchestration decisions."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind

    @property
    def blocks_run(self) -> bool:
        return self.kind in {"authentication", "quota", "billing"}


@dataclass
class ProviderCircuit:
    """Stop further model calls after a run-blocking provider failure."""

    failure: ProviderFailure | None = None

    @property
    def is_open(self) -> bool:
        return self.failure is not None

    def open(self, failure: ProviderFailure) -> None:
        if failure.blocks_run and self.failure is None:
            self.failure = failure


def classify_provider_failure(error: Exception) -> ProviderFailure:
    """Classify provider errors without coupling domain code to SDK exceptions."""
    message = str(error)
    normalized = message.casefold()
    if any(term in normalized for term in ("credit", "billing", "payment")):
        kind = "billing"
    elif any(
        term in normalized
        for term in ("api key", "unauthorized", "unauthenticated", "401", "403")
    ):
        kind = "authentication"
    elif any(
        term in normalized
        for term in ("quota", "rate limit", "resource exhausted", "429")
    ):
        kind = "quota"
    else:
        kind = "transient"
    return ProviderFailure(kind, message)


class GeminiStructuredModel:
    """Generate Pydantic-validated JSON with the Gemini API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        client: genai.Client | None = None,
    ) -> None:
        self.model = model
        self.client = client or genai.Client(api_key=api_key)

    async def generate(
        self,
        *,
        response_model: type[T],
        system_instruction: str,
        prompt: str,
    ) -> T:
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_model,
                    temperature=0.2,
                ),
            )
            if not response.text:
                raise RuntimeError("Gemini returned an empty structured response")
            return response_model.model_validate_json(response.text)
        except ProviderFailure:
            raise
        except Exception as error:
            raise classify_provider_failure(error) from error
