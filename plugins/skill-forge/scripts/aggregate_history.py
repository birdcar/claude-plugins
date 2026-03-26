#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

"""Summarize a skill's history.json evaluation log.

Reports score trends, common changes, description churn, and trigger accuracy.
Default output is human-readable; --json for machine-readable.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_history(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"history.json not found at '{path}'")
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "entries" in data:
        return data["entries"]
    raise ValueError("Unexpected history.json format — expected a list or {entries: [...]}")


def date_range(entries: list[dict]) -> tuple[str, str]:
    dates = [e.get("timestamp", e.get("date", "")) for e in entries if e.get("timestamp") or e.get("date")]
    if not dates:
        return ("unknown", "unknown")
    return (min(dates)[:10], max(dates)[:10])


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def score_trend(values: list[float], window: int = 3) -> str:
    """Compare average of first `window` values vs last `window` values.

    Returns 'improving', 'declining', or 'stable'.
    """
    if len(values) < window * 2:
        return "stable"
    first_avg = _avg(values[:window])
    last_avg = _avg(values[-window:])
    delta = last_avg - first_avg
    if delta > 0.05:
        return "improving"
    if delta < -0.05:
        return "declining"
    return "stable"


def extract_dimension_scores(entries: list[dict]) -> dict[str, list[float]]:
    """Collect per-dimension score series across all entries."""
    dims: dict[str, list[float]] = {}
    for entry in entries:
        scores = entry.get("scores", {})
        if isinstance(scores, dict):
            for dim, val in scores.items():
                if isinstance(val, (int, float)):
                    dims.setdefault(dim, []).append(float(val))
    return dims


def count_changes(entries: list[dict], field: str) -> dict[str, int]:
    """Count how often each change description appears in applied/skipped lists."""
    counts: dict[str, int] = {}
    for entry in entries:
        for item in entry.get(field, []):
            label = item if isinstance(item, str) else item.get("description", str(item))
            counts[label] = counts.get(label, 0) + 1
    return counts


def top_n(counts: dict[str, int], n: int = 5) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda x: -x[1])[:n]


def description_change_count(entries: list[dict]) -> int:
    """Count entries where the description field changed vs previous entry."""
    changes = 0
    prev_desc: str | None = None
    for entry in entries:
        desc = entry.get("description", entry.get("skill_description"))
        if desc is not None and desc != prev_desc and prev_desc is not None:
            changes += 1
        if desc is not None:
            prev_desc = desc
    return changes


def trigger_accuracy_series(entries: list[dict]) -> list[float]:
    """Extract trigger accuracy values across entries (if present)."""
    series: list[float] = []
    for entry in entries:
        acc = entry.get("trigger_accuracy", entry.get("eval", {}).get("accuracy") if isinstance(entry.get("eval"), dict) else None)
        if isinstance(acc, (int, float)):
            series.append(float(acc))
    return series


def build_summary(entries: list[dict]) -> dict[str, Any]:
    earliest, latest = date_range(entries)
    dim_scores = extract_dimension_scores(entries)
    applied_counts = count_changes(entries, "applied_changes")
    skipped_counts = count_changes(entries, "skipped_changes")
    trigger_series = trigger_accuracy_series(entries)

    dim_trends: dict[str, dict] = {}
    for dim, vals in dim_scores.items():
        dim_trends[dim] = {
            "trend": score_trend(vals),
            "first_avg": round(_avg(vals[:3]), 3),
            "last_avg": round(_avg(vals[-3:]), 3),
            "count": len(vals),
        }

    return {
        "total_entries": len(entries),
        "date_range": {"earliest": earliest, "latest": latest},
        "description_changes": description_change_count(entries),
        "dimension_trends": dim_trends,
        "top_applied_changes": [{"change": k, "count": v} for k, v in top_n(applied_counts)],
        "top_skipped_changes": [{"change": k, "count": v} for k, v in top_n(skipped_counts)],
        "trigger_accuracy": {
            "available": len(trigger_series) > 0,
            "trend": score_trend(trigger_series) if trigger_series else "n/a",
            "latest": round(trigger_series[-1], 3) if trigger_series else None,
            "series_length": len(trigger_series),
        },
    }


def format_human(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"History Summary")
    lines.append(f"  Entries:    {summary['total_entries']}")
    lines.append(f"  Date range: {summary['date_range']['earliest']} → {summary['date_range']['latest']}")
    lines.append(f"  Description changes: {summary['description_changes']}")
    lines.append("")

    if summary["dimension_trends"]:
        lines.append("Score Trends (per dimension):")
        for dim, info in summary["dimension_trends"].items():
            arrow = {"improving": "↑", "declining": "↓", "stable": "→"}.get(info["trend"], "?")
            lines.append(f"  {dim:<30} {arrow} {info['trend']:<10} (avg {info['first_avg']} → {info['last_avg']}, n={info['count']})")
        lines.append("")

    ta = summary["trigger_accuracy"]
    if ta["available"]:
        arrow = {"improving": "↑", "declining": "↓", "stable": "→"}.get(ta["trend"], "?")
        lines.append(f"Trigger Accuracy: {arrow} {ta['trend']}  (latest: {ta['latest']:.0%}, {ta['series_length']} data points)")
        lines.append("")

    if summary["top_applied_changes"]:
        lines.append("Most Applied Changes:")
        for item in summary["top_applied_changes"]:
            lines.append(f"  {item['count']:>3}x  {item['change']}")
        lines.append("")

    if summary["top_skipped_changes"]:
        lines.append("Most Skipped Changes:")
        for item in summary["top_skipped_changes"]:
            lines.append(f"  {item['count']:>3}x  {item['change']}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a skill's history.json evaluation log.")
    parser.add_argument("--history-path", required=True, help="Path to history.json file.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output machine-readable JSON.")
    args = parser.parse_args()

    try:
        entries = load_history(args.history_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("History file is empty — no entries to summarize.", file=sys.stderr)
        sys.exit(0)

    summary = build_summary(entries)

    if args.json_output:
        print(json.dumps(summary, indent=2))
    else:
        print(format_human(summary))


if __name__ == "__main__":
    main()
