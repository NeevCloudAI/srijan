"""
One-time utility: prints the config_schema, UI mode, and default egress
for a given agent template, so we can confirm the exact invocation
Srijan should use in DEV_AGENT_COMMAND_TEMPLATE / DEBUG_AGENT_COMMAND_TEMPLATE.

Usage:
    NEEV_API_KEY=... NEEV_ORG_ID=... NEEV_PROJECT_ID=... \
        python scripts/inspect_agent_template.py claude-code
"""
import json
import os
import sys

from neevai import NeevAI


def main() -> None:
    template_name = sys.argv[1] if len(sys.argv) > 1 else "claude-code"

    with NeevAI(
        api_key=os.environ["NEEV_API_KEY"],
        org_id=os.environ["NEEV_ORG_ID"],
        project_id=os.environ["NEEV_PROJECT_ID"],
    ) as client:
        templates = client.agent_templates.list()
        match = next((t for t in templates.items if t.name == template_name), None)
        if match is None:
            available = ", ".join(t.name for t in templates.items)
            print(f"Template {template_name!r} not found. Available: {available}", file=sys.stderr)
            sys.exit(1)

        print(f"id:              {match.id}")
        print(f"name:            {match.name}")
        print(f"description:     {match.description}")
        print(f"category:        {match.category}")
        print(f"ui:              {match.ui}")
        print(f"agent_version:   {match.agent_version}")
        print(f"default_egress:  {match.default_egress}")
        print(f"config_schema:")
        print(json.dumps(match.config_schema, indent=2))


if __name__ == "__main__":
    main()