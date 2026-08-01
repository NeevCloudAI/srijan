import base64
import json

from src.agents.adapters.base import AgentAdapter, AgentConfigError
from src.config import settings


class OpenCodeAdapter(AgentAdapter):
    name = "opencode"
    default_command_template = "opencode run {task}"

    def env(self) -> dict[str, str]:
        self._require_config()
        return {"OPENAI_API_KEY": settings.inference_api_key}

    def setup(self) -> str:
        """Writes /workspace/opencode.json wiring opencode to the platform's
        OpenAI-compatible inference endpoint. Base64 keeps the JSON (and its
        braces) out of the command template, which str.format() would mangle."""
        self._require_config()
        config = {
            "$schema": "https://opencode.ai/config.json",
            "provider": {
                "neevcloud": {
                    "npm": "@ai-sdk/openai-compatible",
                    "name": "NeevCloud Inference",
                    "options": {
                        "baseURL": settings.inference_base_url,
                        "apiKey": "{env:OPENAI_API_KEY}",
                    },
                    "models": {settings.inference_model: {"name": settings.inference_model}},
                }
            },
            "model": f"neevcloud/{settings.inference_model}",
        }
        encoded = base64.b64encode(json.dumps(config).encode()).decode()
        return f"echo {encoded} | base64 -d > /workspace/opencode.json"

    @staticmethod
    def _require_config() -> None:
        missing = [
            var
            for var, value in (
                ("INFERENCE_API_KEY", settings.inference_api_key),
                ("INFERENCE_BASE_URL", settings.inference_base_url),
                ("INFERENCE_MODEL", settings.inference_model),
            )
            if not value
        ]
        if missing:
            raise AgentConfigError(
                f"opencode agent requires {', '.join(missing)} to be set"
            )
