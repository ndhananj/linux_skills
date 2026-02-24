#!/usr/bin/env python3
"""Tool call dispatch helper."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Mapping, Optional


def dispatch_tool_call(
    tool_call: Any,
    tool_functions: Mapping[str, Callable[..., Any]],
    max_output_chars: int,
    tracer: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> str:
    name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        args = {}

    if tracer is not None:
        tracer("tool_call", {"name": name, "args": args})

    func = tool_functions.get(name)
    if func is None:
        output = f"ERROR: unknown tool '{name}'"
    else:
        try:
            result = func(**args)
            output = str(result) if result is not None else "Done."
        except Exception as exc:  # noqa: BLE001
            output = f"ERROR executing {name}: {exc}"

    if len(output) > max_output_chars:
        output = output[:max_output_chars] + f"\n... [truncated to {max_output_chars} chars]"

    if tracer is not None:
        tracer(
            "tool_result",
            {
                "name": name,
                "output_preview": output[:200],
                "output_chars": len(output),
                "is_error": output.startswith("ERROR"),
            },
        )
    return output
