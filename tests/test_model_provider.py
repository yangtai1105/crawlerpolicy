from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from pipeline.model_provider import (
    GeminiStructuredModel,
    ProviderFailure,
    classify_provider_failure,
)


class Verdict(BaseModel):
    is_relevant: bool
    reason: str


async def test_gemini_provider_returns_validated_structured_output():
    client = MagicMock()
    client.aio.models.generate_content = AsyncMock(
        return_value=MagicMock(
            text='{"is_relevant": true, "reason": "Crawler policy changed"}'
        )
    )
    provider = GeminiStructuredModel(
        api_key="gemini-key",
        model="gemini-3.7-flash",
        client=client,
    )

    result = await provider.generate(
        response_model=Verdict,
        system_instruction="Classify the supplied evidence.",
        prompt="A crawler policy changed.",
    )

    assert result == Verdict(is_relevant=True, reason="Crawler policy changed")
    request = client.aio.models.generate_content.await_args.kwargs
    assert request["model"] == "gemini-3.7-flash"
    assert request["contents"] == "A crawler policy changed."
    assert request["config"].response_mime_type == "application/json"


async def test_gemini_provider_classifies_billing_failure():
    client = MagicMock()
    client.aio.models.generate_content = AsyncMock(
        side_effect=RuntimeError("Your credit balance is too low")
    )
    provider = GeminiStructuredModel(
        api_key="gemini-key",
        model="gemini-3.7-flash",
        client=client,
    )

    with pytest.raises(ProviderFailure) as captured:
        await provider.generate(
            response_model=Verdict,
            system_instruction="Classify.",
            prompt="Evidence.",
        )

    assert captured.value.kind == "billing"
    assert "credit balance" in str(captured.value)


@pytest.mark.parametrize(
    ("message", "expected_kind"),
    [
        ("API key not valid", "authentication"),
        ("429 resource exhausted quota", "quota"),
        ("503 service unavailable", "transient"),
    ],
)
def test_provider_failure_classification(message, expected_kind):
    assert classify_provider_failure(RuntimeError(message)).kind == expected_kind
