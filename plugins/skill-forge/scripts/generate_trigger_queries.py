#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

"""Generate 20 trigger test queries for a skill using the Claude CLI.

Produces a structured JSON eval set split across positive (should trigger)
and negative (should not trigger) categories. Output is written to
{skill-dir}/docs/trigger-eval.json by default.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


QUERY_CATEGORIES = {
    "should_trigger": ["exact_match", "exact_match", "exact_match", "paraphrased", "paraphrased", "paraphrased", "edge_case", "edge_case", "embedded", "embedded"],
    "should_not_trigger": ["adjacent_domain", "adjacent_domain", "adjacent_domain", "general_programming", "general_programming", "general_programming", "keyword_overlap", "keyword_overlap", "other_skill_target", "other_skill_target"],
}

GENERATION_PROMPT = (
    "Generate trigger evaluation queries for Claude Code skill '{skill_name}'.\n\n"
    "Description: {description}\n\nBody summary: {body_summary}\n\n"
    "Generate exactly 20 queries in this distribution:\n"
    "SHOULD TRIGGER (10): 3 exact_match, 3 paraphrased, 2 edge_case, 2 embedded\n"
    "SHOULD NOT TRIGGER (10): 3 adjacent_domain, 3 general_programming, 2 keyword_overlap, 2 other_skill_target\n\n"
    "Return ONLY valid JSON (no markdown):\n"
    '{{\"queries\": [{{\"text\": \"...\", \"should_trigger\": true, \"category\": \"exact_match\"}}, ...]}}\n'
    "Exactly 20 items: 10 should_trigger first, then 10 should_not_trigger."
)


def resolve_skill_md(skill_path: str) -> Path:
    """Resolve SKILL.md path from directory or file argument."""
    p = Path(skill_path)
    if p.is_file():
        return p
    candidate = p / "SKILL.md"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"No SKILL.md found at '{skill_path}'")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Minimal YAML frontmatter parser (no PyYAML). Returns (fields_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    raw = content[3:end].strip()
    fields: dict = {}
    current_key: str | None = None
    current_val_lines: list[str] = []
    for line in raw.splitlines():
        kv = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)", line)
        if kv:
            if current_key:
                fields[current_key] = " ".join(current_val_lines).strip().lstrip(">").strip()
            current_key, current_val_lines = kv.group(1), [kv.group(2)]
        elif current_key and (line.startswith("  ") or not line.strip()):
            current_val_lines.append(line.strip())
    if current_key:
        fields[current_key] = " ".join(current_val_lines).strip().lstrip(">").strip()
    return fields, content[end + 4 :]


def summarize_body(body: str, max_chars: int = 800) -> str:
    """Return the first max_chars of the body, trimmed at a sentence boundary."""
    if len(body) <= max_chars:
        return body.strip()
    truncated = body[:max_chars]
    last_period = truncated.rfind(".")
    if last_period > max_chars // 2:
        return truncated[: last_period + 1].strip()
    return truncated.strip() + "..."


def call_claude(prompt: str, model: str) -> str:
    """Invoke `claude -p` with the given prompt and return stdout."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", model],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error (exit {result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()


def extract_json(text: str) -> dict:
    """Extract the first JSON object from text (handles markdown code fences)."""
    # Strip markdown fences
    text = re.sub(r"```[a-z]*\n?", "", text).strip()
    # Find outermost braces
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in Claude response.")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("Malformed JSON in Claude response.")


def build_output(skill_name: str, raw_queries: list[dict]) -> dict:
    """Assign sequential IDs and validate/normalise the query list."""
    if len(raw_queries) != 20:
        raise ValueError(f"Expected 20 queries from Claude, got {len(raw_queries)}.")
    queries = []
    expected_order = (
        [(True, cat) for cat in QUERY_CATEGORIES["should_trigger"]]
        + [(False, cat) for cat in QUERY_CATEGORIES["should_not_trigger"]]
    )
    for idx, (raw, (expected_trigger, expected_cat)) in enumerate(zip(raw_queries, expected_order)):
        queries.append(
            {
                "id": idx,
                "text": raw.get("text", ""),
                "should_trigger": raw.get("should_trigger", expected_trigger),
                "category": raw.get("category", expected_cat),
            }
        )
    return {
        "skill_name": skill_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queries": queries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 20 trigger test queries for a skill.")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory or SKILL.md file.")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude model ID.")
    parser.add_argument("--output", help="Output JSON path (default: {skill-dir}/docs/trigger-eval.json).")
    args = parser.parse_args()

    skill_md = resolve_skill_md(args.skill_path)
    content = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    skill_name = fm.get("name", skill_md.parent.name)
    description = fm.get("description", "(no description)")
    body_summary = summarize_body(body)

    prompt = GENERATION_PROMPT.format(
        skill_name=skill_name,
        description=description,
        body_summary=body_summary,
    )

    try:
        raw_output = call_claude(prompt, args.model)
        parsed = extract_json(raw_output)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        output_data = build_output(skill_name, parsed.get("queries", []))
    except ValueError as exc:
        print(f"Error building output: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        docs_dir = skill_md.parent / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        output_path = docs_dir / "trigger-eval.json"

    output_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
    print(f"Wrote {len(output_data['queries'])} queries to {output_path}")


if __name__ == "__main__":
    main()
