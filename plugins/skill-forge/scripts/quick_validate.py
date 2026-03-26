#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///

"""Fast structural validation of a skill directory.

Checks frontmatter, naming, file sizes, and anti-patterns.
Exit code: 0 if all CRITICAL checks pass, 1 otherwise.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    """Parse YAML frontmatter. Returns (dict_or_None, body)."""
    if not content.startswith("---"):
        return None, content
    end = content.find("\n---", 3)
    if end == -1:
        return None, content
    raw = content[3:end].strip()
    try:
        return yaml.safe_load(raw), content[end + 4 :]
    except yaml.YAMLError:
        return None, content


def is_kebab_case(value: str) -> bool:
    """Return True if value matches kebab-case: lowercase letters, digits, hyphens only."""
    return bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", value))


def has_xml_tags(text: str) -> bool:
    """Return True if text contains XML-style tags (e.g. <tag> or </tag>)."""
    return bool(re.search(r"<[a-zA-Z][^>]*>|</[a-zA-Z][^>]*>", text))


def resolve_skill_md(skill_path: str) -> Path:
    """Resolve the SKILL.md path from either a directory or file path argument."""
    p = Path(skill_path)
    if p.is_file():
        return p
    candidate = p / "SKILL.md"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"No SKILL.md found at '{skill_path}'")


def run_checks(skill_md: Path) -> list[dict[str, Any]]:
    """Run all validation checks. Each result: name, severity, passed, message."""
    results: list[dict[str, Any]] = []
    content = skill_md.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(content)
    dir_name = skill_md.parent.name

    def check(name: str, severity: str, passed: bool, message: str) -> None:
        results.append({"name": name, "severity": severity, "passed": passed, "message": message})

    check("frontmatter_exists", "CRITICAL", fm is not None,
          "Frontmatter block found." if fm is not None else "No YAML frontmatter block detected.")
    if fm is None:
        for name in ("has_name", "has_description", "kebab_name_field", "description_length", "no_xml_in_frontmatter"):
            check(name, "CRITICAL", False, "Skipped — no frontmatter.")
    else:
        has_name = "name" in fm and bool(fm["name"])
        check("has_name", "CRITICAL", has_name, "name field present." if has_name else "Missing required 'name' field.")
        has_desc = "description" in fm and bool(fm["description"])
        check("has_description", "CRITICAL", has_desc, "description field present." if has_desc else "Missing required 'description' field.")

        if has_name:
            name_val = str(fm["name"])
            kebab_ok = is_kebab_case(name_val)
            check("kebab_name_field", "HIGH", kebab_ok, f"name '{name_val}' is kebab-case." if kebab_ok else f"name '{name_val}' is not kebab-case.")
        else:
            check("kebab_name_field", "HIGH", False, "Skipped — no name field.")

        if has_desc:
            desc_len = len(str(fm["description"]))
            desc_ok = desc_len <= 1024
            check("description_length", "HIGH", desc_ok, f"Description is {desc_len} chars (<=1024)." if desc_ok else f"Description is {desc_len} chars (exceeds 1024 limit).")
        else:
            check("description_length", "HIGH", False, "Skipped — no description field.")

        fm_block_end = content.find("\n---", 3)
        fm_raw = content[:fm_block_end] if fm_block_end != -1 else ""
        xml_found = has_xml_tags(fm_raw)
        check("no_xml_in_frontmatter", "HIGH", not xml_found, "No XML tags in frontmatter." if not xml_found else "XML tags detected in frontmatter (not allowed).")

    dir_ok = is_kebab_case(dir_name)
    check("kebab_directory_name", "HIGH", dir_ok, f"Directory '{dir_name}' is kebab-case." if dir_ok else f"Directory '{dir_name}' is not kebab-case.")

    line_count = len(content.splitlines())
    lines_ok = line_count <= 500
    check("skill_md_line_count", "MEDIUM", lines_ok, f"SKILL.md is {line_count} lines (<=500)." if lines_ok else f"SKILL.md is {line_count} lines (exceeds 500 limit).")

    agents_dir = skill_md.parent.parent / "agents"
    if agents_dir.is_dir():
        for agent_file in sorted(agents_dir.glob("*.md")):
            agent_lines = len(agent_file.read_text(encoding="utf-8").splitlines())
            agent_ok = agent_lines <= 200
            check(f"agent_line_count:{agent_file.name}", "MEDIUM", agent_ok, f"agents/{agent_file.name} is {agent_lines} lines (<=200)." if agent_ok else f"agents/{agent_file.name} is {agent_lines} lines (exceeds 200 limit).")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Fast structural validation of a skill directory.")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory or SKILL.md file.")
    args = parser.parse_args()

    try:
        skill_md = resolve_skill_md(args.skill_path)
    except FileNotFoundError as exc:
        print(json.dumps({"passed": False, "checks": [{"name": "file_exists", "severity": "CRITICAL", "passed": False, "message": str(exc)}]}))
        sys.exit(1)

    checks = run_checks(skill_md)
    critical_failures = [c for c in checks if c["severity"] == "CRITICAL" and not c["passed"]]
    passed = len(critical_failures) == 0

    print(json.dumps({"passed": passed, "checks": checks}, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
