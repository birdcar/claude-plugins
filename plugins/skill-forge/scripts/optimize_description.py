#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

"""Automated description optimization loop for Claude Code skills.

Iterates: score train set → propose improved description → re-score test set.
Writes optimization-result.json to {skill-dir}/docs/.

Trigger detection heuristic: run `claude -p "query" --output-format json` and
check if the skill name appears in the JSON output. False positives are possible
if the skill name is mentioned incidentally in the response.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


IMPROVE_PROMPT = (
    "Optimize the description field of Claude Code skill '{skill_name}'.\n\n"
    "Current description:\n{current_description}\n\n"
    "False negatives (should trigger, did not):\n{false_negatives}\n\n"
    "False positives (should not trigger, did):\n{false_positives}\n\n"
    "Train accuracy: {train_score:.0%}\n\n"
    "Write an improved description that: keeps third-person trigger phrase style; "
    "sharpens positive triggers to fix false negatives; adds 'Do NOT use for...' "
    "clauses for false positives; stays under 1024 chars.\n"
    "Return ONLY the new description text — no JSON, no explanation."
)


def resolve_skill_md(skill_path: str) -> Path:
    p = Path(skill_path)
    if p.is_file():
        return p
    candidate = p / "SKILL.md"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"No SKILL.md found at '{skill_path}'")


def get_description(content: str) -> str:
    """Extract the description value from frontmatter."""
    match = re.search(r"^description:\s*(.*?)(?=\n[a-zA-Z]|\Z)", content[3:], re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    return " ".join(line.strip() for line in match.group(1).splitlines()).strip().lstrip(">").strip()


def set_description(content: str, new_desc: str) -> str:
    """Replace the description value in frontmatter, preserving all other fields."""
    # Format as YAML block scalar if multi-line-ish
    escaped = new_desc.replace("\n", " ")
    replacement = f"description: >-\n  {escaped}"

    def _replacer(m: re.Match) -> str:  # type: ignore[type-arg]
        return replacement

    updated = re.sub(
        r"^description:\s*.*?(?=\n[a-zA-Z_]|\nname:|\Z)",
        _replacer,
        content,
        flags=re.DOTALL | re.MULTILINE,
    )
    return updated


def split_eval_set(queries: list[dict], train_ratio: float = 0.6) -> tuple[list[dict], list[dict]]:
    """Deterministic 60/40 split based on query ID (even IDs → train)."""
    train = [q for q in queries if q["id"] % 10 < int(10 * train_ratio)]
    test = [q for q in queries if q["id"] % 10 >= int(10 * train_ratio)]
    return train, test


def run_query(query_text: str, skill_name: str, model: str, verbose: bool) -> bool:
    """Return True if the skill name appears triggered in the claude CLI JSON output.

    Heuristic: check if skill name (normalised) appears anywhere in the response.
    False positives are possible when the skill name appears in unrelated text.
    """
    cmd = ["claude", "-p", query_text, "--model", model, "--output-format", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"  [timeout] {query_text[:60]}", file=sys.stderr)
        return False
    if result.returncode != 0:
        if verbose:
            print(f"  [error] exit {result.returncode}: {result.stderr[:100]}", file=sys.stderr)
        return False
    out = result.stdout.lower()
    triggered = skill_name.lower().replace("-", "") in out.replace("-", "").replace(" ", "")
    if verbose:
        print(f"  {'[TRIGGER]' if triggered else '[skip]'} {query_text[:70]}", file=sys.stderr)
    return triggered


def score_queries(queries: list[dict], skill_name: str, model: str, runs: int, verbose: bool) -> tuple[float, list[dict]]:
    """Score queries, running each `runs` times with majority-vote. Returns (accuracy, results)."""
    results, correct = [], 0
    for q in queries:
        votes = sum(run_query(q["text"], skill_name, model, verbose) for _ in range(runs))
        triggered = votes > runs // 2
        hit = triggered == q["should_trigger"]
        correct += hit
        results.append({**q, "triggered": triggered, "correct": hit})
    return correct / len(queries) if queries else 0.0, results


def propose_description(skill_name: str, current_desc: str, scored: list[dict], train_score: float, model: str) -> str:
    """Ask Claude to rewrite the description to fix failures in `scored`."""
    fn = "\n".join(f"  - {r['text']}" for r in scored if r["should_trigger"] and not r["triggered"]) or "  (none)"
    fp = "\n".join(f"  - {r['text']}" for r in scored if not r["should_trigger"] and r["triggered"]) or "  (none)"
    prompt = IMPROVE_PROMPT.format(skill_name=skill_name, current_description=current_desc,
                                   false_negatives=fn, false_positives=fp, train_score=train_score)
    result = subprocess.run(["claude", "-p", prompt, "--model", model], capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> None:
    p = argparse.ArgumentParser(description="Automated skill description optimization loop.")
    p.add_argument("--skill-path", required=True)
    p.add_argument("--eval-set", required=True)
    p.add_argument("--model", default="claude-sonnet-4-6")
    p.add_argument("--max-iterations", type=int, default=5)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    skill_md = resolve_skill_md(args.skill_path)
    eval_data = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    queries: list[dict] = eval_data["queries"]
    skill_name: str = eval_data.get("skill_name", skill_md.parent.name)
    train_queries, test_queries = split_eval_set(queries)

    if args.verbose:
        print(f"Skill: {skill_name}  train={len(train_queries)}  test={len(test_queries)}", file=sys.stderr)

    started_at = datetime.now(timezone.utc).isoformat()
    iterations: list[dict] = []
    current_desc = get_description(skill_md.read_text(encoding="utf-8"))

    for i in range(args.max_iterations):
        if args.verbose:
            print(f"\n=== Iteration {i} ===", file=sys.stderr)
        train_score, train_results = score_queries(train_queries, skill_name, args.model, runs=3, verbose=args.verbose)
        test_score, _ = score_queries(test_queries, skill_name, args.model, runs=1, verbose=args.verbose)
        iterations.append({"iteration": i, "description": current_desc,
                            "train_score": round(train_score, 4), "test_score": round(test_score, 4)})
        if args.verbose:
            print(f"  train={train_score:.0%}  test={test_score:.0%}", file=sys.stderr)
        if i < args.max_iterations - 1:
            try:
                current_desc = propose_description(skill_name, current_desc, train_results, train_score, args.model)
            except RuntimeError as exc:
                print(f"Warning: {exc}", file=sys.stderr)
                break

    best = max(iterations, key=lambda x: x["test_score"])
    output = {"skill_name": skill_name, "started_at": started_at,
               "completed_at": datetime.now(timezone.utc).isoformat(), "iterations": iterations,
               "best_iteration": best["iteration"], "best_description": best["description"],
               "best_test_score": best["test_score"]}
    docs_dir = skill_md.parent / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_path = docs_dir / "optimization-result.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"best_iteration": best["iteration"], "best_test_score": best["test_score"], "output": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
