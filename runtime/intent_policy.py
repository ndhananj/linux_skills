#!/usr/bin/env python3
"""Prompt intent to tool shortlisting policy."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class SelectionResult:
    tool_names: Tuple[str, ...]
    mode: str
    intent_family: Optional[str]
    confidence: str
    excluded_tools: Tuple[str, ...]


def select_tools(
    prompt: str,
    tool_names: Sequence[str],
    max_tools: int,
    mode: str = "per_skill_fixed_slice",
) -> SelectionResult:
    if max_tools <= 0:
        return SelectionResult(tuple(tool_names), "all", None, "high", tuple())

    intent_family, confidence = _detect_intent_family(prompt)

    if mode == "per_skill_fixed_slice" and intent_family is not None and confidence == "high":
        slice_names = _fixed_slice_tool_names(intent_family)
        if slice_names:
            selected = tuple(name for name in slice_names if name in set(tool_names))[:max_tools]
            if selected:
                return SelectionResult(
                    tool_names=selected,
                    mode="per_skill_fixed_slice",
                    intent_family=intent_family,
                    confidence=confidence,
                    excluded_tools=tuple(_excluded_tools_for_family(intent_family)),
                )

    selected = tuple(_score_based_selection(prompt, tool_names, max_tools))
    return SelectionResult(
        tool_names=selected,
        mode="score_based",
        intent_family=intent_family,
        confidence=confidence,
        excluded_tools=tuple(),
    )


def _detect_intent_family(prompt: str) -> Tuple[Optional[str], str]:
    prompt_lc = prompt.lower()

    recursive_markers = (
        "recursively",
        "recursive",
        "subdirectories",
        "subdirs",
        "directory tree",
        "tree of directories",
    )
    if "directories" in prompt_lc and (" under " in prompt_lc or any(m in prompt_lc for m in recursive_markers)):
        return "directory_listing_recursive", "high"

    if "directories" in prompt_lc and (" in " in prompt_lc or "under " in prompt_lc or "inside " in prompt_lc):
        return "directory_listing", "high"

    conceptual_verbs = (
        "define",
        "recall",
        "outline",
        "describe",
        "recognize",
        "distinguish",
        "list",
        "explain",
        "install",
    )
    if any(prompt_lc.startswith(v + " ") for v in conceptual_verbs):
        return None, "low"

    operational_patterns = (
        r"\bshow\b",
        r"\bfind\b",
        r"\bcheck\b",
        r"\brun\b",
        r"\bdisplay\b",
        r"\btail\b",
        r"\bstatus\b",
        r"\btroubleshoot\b",
        r"\bmonitor\b",
        r"\btop\s+\d+\b",
        r"\bshow me\b",
    )
    if not any(re.search(p, prompt_lc) for p in operational_patterns):
        return None, "low"

    if (
        ("largest files" in prompt_lc or "biggest files" in prompt_lc)
        or ("largest" in prompt_lc and "files" in prompt_lc)
        or ("top" in prompt_lc and "files" in prompt_lc and ("large" in prompt_lc or "size" in prompt_lc))
    ):
        return "file_size_listing", "high"
    if any(kw in prompt_lc for kw in ["tail", "journal", "syslog", "auth log", "logs"]):
        return "logging_basic", "high"
    if any(kw in prompt_lc for kw in ["interfaces", "routing", "dns", "ports", "ifconfig", "netstat", "ip "]):
        return "networking_basic", "high"
    if any(kw in prompt_lc for kw in ["process", "service", "cpu", "memory"]) or re.search(r"\btop\s+\d+\b", prompt_lc):
        return "process_basic", "high"
    if any(kw in prompt_lc for kw in ["disk", "storage", "mount", "swap", "filesystem", "lsblk"]):
        return "disk_storage_basic", "high"
    if any(kw in prompt_lc for kw in ["list files", "find files", "directory", "directories", "ls ", "pwd"]):
        return "filesystem_navigation", "high"
    return None, "low"


def _fixed_slice_tool_names(family: str) -> List[str]:
    slices = {
        "file_size_listing": [
            "file_system__largest_files",
            "file_system__disk_usage",
            "file_system__list_directory",
        ],
        "directory_listing": [
            "file_system__list_directories",
            "file_system__list_directory",
            "file_system__find_files",
        ],
        "directory_listing_recursive": [
            "file_system__list_directories_recursive",
            "file_system__list_directories",
            "file_system__find_files",
        ],
        "filesystem_navigation": [
            "file_system__list_directory",
            "file_system__list_directories",
            "file_system__find_files",
            "file_system__disk_usage",
            "file_system__disk_free",
            "file_system__touch_file",
        ],
        "logging_basic": [
            "logging__tail_log",
            "logging__view_journal",
            "logging__show_syslog",
            "logging__search_log",
            "process_and_service__view_journal",
        ],
        "networking_basic": [
            "networking__show_interfaces",
            "networking__show_routing_table",
            "networking__dns_lookup",
            "networking__show_open_ports",
            "networking__show_active_connections",
            "troubleshooting__check_network_connectivity",
        ],
        "process_basic": [
            "process_and_service__show_top_processes",
            "process_and_service__list_processes",
            "process_and_service__service_status",
            "performance__show_top_processes_by_cpu",
            "performance__show_top_processes_by_memory",
            "performance__show_memory_usage",
        ],
        "disk_storage_basic": [
            "storage__list_block_devices",
            "storage__show_mounts",
            "storage__show_swap_usage",
            "file_system__disk_free",
            "file_system__disk_usage",
        ],
    }
    return slices.get(family, [])


def _excluded_tools_for_family(family: str) -> List[str]:
    exclusions = {
        "file_size_listing": [
            "text_processing__concatenate_files",
            "text_processing__diff_files",
            "text_processing__join_files",
        ]
    }
    return exclusions.get(family, [])


def _score_based_selection(prompt: str, tool_names: Sequence[str], max_tools: int) -> List[str]:
    normalized_prompt = prompt.lower().replace("ci/cd", "cicd")
    tokens = set(re.findall(r"[a-zA-Z0-9_]{3,}", normalized_prompt))
    stop = {"the", "and", "for", "with", "that", "this", "from", "into", "show", "list", "have"}
    tokens = {tok for tok in tokens if tok not in stop}
    keyword_scores = _keyword_skill_scores(tokens)

    scored: List[tuple[int, str]] = []
    for full_name in tool_names:
        skill, func = full_name.split("__", 1)
        score = 0
        if skill in tokens:
            score += 5
        score += keyword_scores.get(skill, 0) * 4
        func_parts = set(func.split("_"))
        score += len(func_parts.intersection(tokens)) * 2
        if score > 0:
            scored.append((score, full_name))

    if scored:
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [name for _, name in scored[:max_tools]]

    core_skills = ["file_system", "process_and_service", "networking", "package_management", "logging", "troubleshooting"]
    selected: List[str] = []
    for skill in core_skills:
        for name in sorted(tool_names):
            if name.startswith(f"{skill}__"):
                selected.append(name)
                if len(selected) >= max_tools:
                    break
        if len(selected) >= max_tools:
            break
    return selected


def _keyword_skill_scores(tokens: set[str]) -> Dict[str, int]:
    keyword_map: Mapping[str, set[str]] = {
        "kernel": {"boot_and_kernel"},
        "bootloader": {"boot_and_kernel"},
        "grub": {"boot_and_kernel"},
        "dracut": {"boot_and_kernel"},
        "initramfs": {"boot_and_kernel"},
        "bios": {"boot_and_kernel"},
        "uefi": {"boot_and_kernel"},
        "boot": {"boot_and_kernel", "file_system"},
        "proc": {"file_system"},
        "dev": {"file_system"},
        "var": {"file_system"},
        "filesystem": {"file_system", "storage"},
        "partition": {"storage"},
        "raid": {"storage"},
        "lvm": {"storage"},
        "iscsi": {"storage"},
        "mount": {"storage", "file_system"},
        "permission": {"user_and_group", "file_system"},
        "chmod": {"user_and_group"},
        "chown": {"user_and_group"},
        "chgrp": {"user_and_group"},
        "network": {"networking", "troubleshooting"},
        "ipv4": {"networking"},
        "ipv6": {"networking"},
        "distribution": {"troubleshooting"},
        "distributions": {"troubleshooting"},
        "cloud": {"troubleshooting"},
        "dns": {"networking", "troubleshooting"},
        "dhcp": {"networking"},
        "firewall": {"security"},
        "waf": {"security"},
        "iptables": {"security"},
        "ufw": {"security"},
        "nftables": {"security"},
        "pam": {"security"},
        "ldap": {"security"},
        "authentication": {"security"},
        "auth": {"security"},
        "crypto": {"security"},
        "cryptography": {"security"},
        "threat": {"security"},
        "cia": {"security"},
        "container": {"containerization"},
        "docker": {"containerization"},
        "process": {"process_and_service"},
        "daemon": {"process_and_service"},
        "systemd": {"process_and_service", "logging", "scheduling"},
        "journalctl": {"logging", "process_and_service"},
        "service": {"process_and_service"},
        "script": {"shell_scripting", "text_processing"},
        "awk": {"text_processing", "file_system"},
        "sed": {"text_processing", "file_system"},
        "grep": {"text_processing", "file_system"},
        "egrep": {"text_processing"},
        "find": {"file_system"},
        "tee": {"shell_scripting", "text_processing"},
        "git": {"version_control"},
        "terraform": {"iac_and_cicd"},
        "iac": {"iac_and_cicd"},
        "cicd": {"iac_and_cicd"},
        "package": {"package_management"},
        "apt": {"package_management"},
        "yum": {"package_management"},
        "pacman": {"package_management"},
        "performance": {"performance", "troubleshooting"},
        "cpu": {"performance"},
        "memory": {"performance"},
        "swap": {"storage", "performance"},
        "hardware": {"troubleshooting", "performance"},
        "lspci": {"troubleshooting"},
        "lsusb": {"troubleshooting"},
        "dmidecode": {"troubleshooting"},
        "schedule": {"scheduling"},
        "cron": {"scheduling"},
        "timer": {"scheduling"},
        "resolved": {"troubleshooting"},
        "log": {"logging"},
        "troubleshoot": {"troubleshooting"},
    }
    scores: Dict[str, int] = {}
    for token in tokens:
        for skill in keyword_map.get(token, set()):
            scores[skill] = scores.get(skill, 0) + 1
    return scores
