from src.agents.adapters.base import AgentAdapter, AgentConfigError
from src.agents.adapters.claude_code import ClaudeCodeAdapter
from src.agents.adapters.opencode import OpenCodeAdapter

_ADAPTERS: dict[str, AgentAdapter] = {
    adapter.name: adapter for adapter in (ClaudeCodeAdapter(), OpenCodeAdapter())
}


def get_adapter(template: str) -> AgentAdapter:
    try:
        return _ADAPTERS[template]
    except KeyError:
        raise AgentConfigError(
            f"no adapter for agent template {template!r}; known: {sorted(_ADAPTERS)}"
        ) from None
