import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    pass


class OpenAIResponsesProvider:
    """Small standard-library adapter for the OpenAI Responses API."""

    def __init__(self, model=None, api_key=None, timeout=90):
        self.model = model or os.environ.get("OPENAI_MODEL")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.timeout = timeout
        if not self.model:
            raise ProviderError("Set OPENAI_MODEL before selecting the OpenAI provider.")
        if not self.api_key:
            raise ProviderError("Set OPENAI_API_KEY before selecting the OpenAI provider.")

    def generate(self, prompt):
        body = json.dumps({"model": self.model, "input": prompt, "store": False}).encode("utf-8")
        request = Request(
            "https://api.openai.com/v1/responses",
            data=body,
            headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ProviderError("OpenAI API returned HTTP " + str(exc.code) + ".") from None
        except (URLError, TimeoutError) as exc:
            raise ProviderError("OpenAI API request failed: " + type(exc).__name__) from None
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ProviderError("OpenAI API returned an unreadable response: " + type(exc).__name__) from None
        chunks = []
        for item in payload.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    chunks.append(content.get("text", ""))
        if not chunks:
            raise ProviderError("OpenAI API response did not include output text.")
        return {"text": "\n".join(chunks), "response_id": payload.get("id"),
                "model": payload.get("model", self.model), "usage": payload.get("usage")}


class ScriptedProvider:
    """Deterministic provider used only by tests and offline protocol checks."""

    def __init__(self, payload):
        self.payload = payload
        self.prompts = []
        self.model = "scripted-test-fixture"

    def generate(self, prompt):
        self.prompts.append(prompt)
        return {"text": json.dumps(self.payload), "response_id": None, "model": "scripted-test-fixture"}
