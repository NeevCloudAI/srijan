from src.agents.adapters.base import AgentAdapter
from src.config import settings


class ClaudeCodeAdapter(AgentAdapter):
    name = "claude-code"
    default_command_template = "claude-code --print {task}"

    def env(self) -> dict[str, str]:
        return {"ANTHROPIC_API_KEY": settings.neev_api_key}
