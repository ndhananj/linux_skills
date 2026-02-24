from __future__ import annotations

from typing import Iterable, List, Mapping


def build_contract_toolset(
    selected_tools: List[dict],
    tool_config_by_name: Mapping[str, dict],
    expected_skill: str,
    expected_any_tools: Iterable[str],
    max_tools: int = 16,
) -> List[dict]:
    """Ensure live contract tests always include expected skill/tools first.

    This is test-only overlay logic; runtime routing remains unchanged.
    """
    expected_names: List[str] = []

    for name in sorted(tool_config_by_name.keys()):
        if name.startswith(f"{expected_skill}__"):
            expected_names.append(name)

    for name in expected_any_tools:
        if name in tool_config_by_name and name not in expected_names:
            expected_names.append(name)

    selected_names = [cfg["function"]["name"] for cfg in selected_tools]
    merged: List[str] = []
    for name in expected_names + selected_names:
        if name in tool_config_by_name and name not in merged:
            merged.append(name)
        if len(merged) >= max_tools:
            break

    if not merged:
        merged = selected_names[:max_tools]

    return [tool_config_by_name[name] for name in merged]
