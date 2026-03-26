#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

"""Single eval run orchestrator.

Executes a prompt via `claude -p`, captures the JSON output, extracts metrics,
and writes results to the output directory. Designed to be called as a subagent
task — timing.json is NOT written here; the caller captures that from task
completion metadata.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single eval via claude -p.")
    parser.add_argument("--prompt", required=True, help="Prompt text to execute.")
    parser.add_argument("--eval-id", required=True, type=int, help="Numeric eval identifier.")
    parser.add_argument("--eval-name", required=True, help="Descriptive name for this eval.")
    parser.add_argument("--output-dir", required=True, help="Base directory for this eval (e.g. iteration-0/eval-0).")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude model ID to use.")
    parser.add_argument("--config-label", required=True, help="Configuration label: with_skill, without_skill, old_skill, or new_skill.")
    return parser.parse_args()


def write_metadata_if_missing(eval_dir: Path, eval_id: int, eval_name: str, prompt: str) -> None:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        return
    metadata = {
        "eval_id": eval_id,
        "eval_name": eval_name,
        "prompt": prompt,
        "assertions": [],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def run_claude(prompt: str, model: str) -> tuple[int, str]:
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", model],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout


def extract_metrics(claude_output: str) -> tuple[str, dict[str, int]]:
    """Parse claude JSON output; return (transcript_text, metrics_dict).

    The claude --output-format json response is a list of message objects.
    We concatenate assistant content for the transcript and count tool use events.
    Falls back gracefully if parsing fails.
    """
    transcript_chars = len(claude_output)
    tool_calls = 0
    files_created = 0
    errors = 0
    output_chars = 0
    transcript_lines: list[str] = []

    try:
        data = json.loads(claude_output)
        messages = data if isinstance(data, list) else data.get("messages", [])

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if isinstance(content, str):
                if role == "assistant":
                    output_chars += len(content)
                transcript_lines.append(f"[{role}] {content}")
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get("type", "")
                        if block_type == "text":
                            text = block.get("text", "")
                            if role == "assistant":
                                output_chars += len(text)
                            transcript_lines.append(f"[{role}] {text}")
                        elif block_type == "tool_use":
                            tool_calls += 1
                            tool_name = block.get("name", "")
                            if tool_name in ("Write", "Edit"):
                                files_created += 1
                            transcript_lines.append(f"[tool_use:{tool_name}] {json.dumps(block.get('input', {}))}")
                        elif block_type == "tool_result":
                            result_content = block.get("content", "")
                            if isinstance(result_content, str) and "error" in result_content.lower():
                                errors += 1
                            transcript_lines.append(f"[tool_result] {result_content}")

        if not transcript_lines:
            transcript_lines = [claude_output]

    except (json.JSONDecodeError, TypeError):
        transcript_lines = [claude_output]
        output_chars = transcript_chars

    transcript = "\n".join(transcript_lines)
    metrics = {
        "tool_calls": tool_calls,
        "files_created": files_created,
        "errors": errors,
        "output_chars": output_chars,
        "transcript_chars": transcript_chars,
    }
    return transcript, metrics


def main() -> None:
    args = parse_args()

    eval_dir = Path(args.output_dir)
    config_dir = eval_dir / args.config_label
    outputs_dir = config_dir / "outputs"

    eval_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    write_metadata_if_missing(eval_dir, args.eval_id, args.eval_name, args.prompt)

    returncode, claude_output = run_claude(args.prompt, args.model)

    if returncode != 0:
        error_msg = claude_output.strip() or f"claude exited with code {returncode}"
        (config_dir / "metrics.json").write_text(
            json.dumps({"tool_calls": 0, "files_created": 0, "errors": 1, "output_chars": 0, "transcript_chars": 0}, indent=2),
            encoding="utf-8",
        )
        print(json.dumps({"status": "error", "message": error_msg}))
        return

    transcript, metrics = extract_metrics(claude_output)

    (config_dir / "transcript.txt").write_text(transcript, encoding="utf-8")
    (config_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "config": args.config_label,
        "eval_id": args.eval_id,
        "output_dir": str(config_dir),
    }))


if __name__ == "__main__":
    main()
