#!/usr/bin/env python3
"""Direct local LLM sanity and latency check (no tools)."""

from __future__ import annotations

import os
import time

import openai
import yaml


def main() -> int:
    runtime_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cfg_path = os.path.join(runtime_dir, "config.yaml")

    with open(cfg_path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    local = cfg.get("llm", {}).get("local", {})
    base_url = local.get("base_url", "http://localhost:8080/v1")
    model = local.get("model", "local-model")

    client = openai.OpenAI(base_url=base_url, api_key=local.get("api_key", "local-key"))

    prompt = "Reply with exactly: OK"
    print(f"[sanity] Prompt: {prompt}")
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are concise."},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = time.perf_counter() - start
    content = (resp.choices[0].message.content or "").strip()
    print(f"[sanity] Response latency: {elapsed:.2f}s")
    print(f"[sanity] Response text: {content}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
