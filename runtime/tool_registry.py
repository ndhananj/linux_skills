#!/usr/bin/env python3
"""
tool_registry.py — Auto-discovers every tools.py in the skill tree and
builds the OpenAI-compatible function-calling schema for each callable.

Usage (standalone):
    python3 tool_registry.py          # prints a summary
    python3 tool_registry.py --json   # dumps the full schema list as JSON
"""

import ast
import importlib.util
import inspect
import json
import os
import sys
from typing import Any, Callable, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Python annotation → JSON Schema type mapping
# ---------------------------------------------------------------------------
_PY_TO_JSON: Dict[Any, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

# Directories inside the skills root that are NOT skill modules
_SKIP_DIRS = {"runtime", "__pycache__", ".git"}


def _json_type(annotation: Any) -> str:
    """Return the JSON Schema type string for a Python annotation."""
    return _PY_TO_JSON.get(annotation, "string")


def _build_schema(skill_name: str, func: Callable) -> Dict[str, Any]:
    """Build a single OpenAI function-calling schema entry from *func*."""
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""
    # First non-empty line of the docstring becomes the description
    description = next((ln.strip() for ln in doc.splitlines() if ln.strip()), func.__name__)

    properties: Dict[str, Any] = {}
    required: List[str] = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        prop: Dict[str, Any] = {"type": _json_type(param.annotation)}
        # Pull per-parameter doc from lines like "param_name: description"
        for line in doc.splitlines():
            stripped = line.strip()
            if stripped.startswith(f"{param_name}:"):
                prop["description"] = stripped[len(param_name) + 1:].strip()
                break
        properties[param_name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    # Tool name uses double-underscore as separator so the agent can split it
    tool_name = f"{skill_name}__{func.__name__}"

    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def discover_skills(
    skills_dir: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Callable]]:
    """Walk *skills_dir*, import every ``tools.py``, and return:

    * ``tool_configs`` — list of OpenAI function-calling schema dicts
    * ``tool_functions`` — mapping of ``"skill__func"`` → callable
    """
    tool_configs: List[Dict[str, Any]] = []
    tool_functions: Dict[str, Callable] = {}

    for skill_name in sorted(os.listdir(skills_dir)):
        if skill_name in _SKIP_DIRS or skill_name.startswith("."):
            continue
        skill_path = os.path.join(skills_dir, skill_name)
        tools_py = os.path.join(skill_path, "tools.py")
        if not (os.path.isdir(skill_path) and os.path.exists(tools_py)):
            continue

        # Load the module dynamically without requiring an __init__.py
        module_name = f"linux_skills__{skill_name}__tools"
        spec = importlib.util.spec_from_file_location(module_name, tools_py)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            print(f"[tool_registry] Warning: could not load {tools_py}: {exc}", file=sys.stderr)
            continue

        for func_name, func in inspect.getmembers(module, inspect.isfunction):
            if func_name.startswith("_"):
                continue
            # Skip functions that were imported from other modules
            # (e.g. run_command imported from command_runner)
            if func.__module__ != module_name:
                continue
            schema = _build_schema(skill_name, func)
            full_name = schema["function"]["name"]
            tool_configs.append(schema)
            tool_functions[full_name] = func

    return tool_configs, tool_functions


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    skills_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    configs, functions = discover_skills(skills_directory)

    if "--json" in sys.argv:
        print(json.dumps(configs, indent=2))
    else:
        print(f"Discovered {len(configs)} tools across {len({c['function']['name'].split('__')[0] for c in configs})} skill modules.\n")
        for cfg in configs:
            fn = cfg["function"]
            req = fn["parameters"].get("required", [])
            print(f"  {fn['name']:50s}  required={req}")
