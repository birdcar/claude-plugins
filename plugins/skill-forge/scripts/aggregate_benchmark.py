#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

"""Aggregate grading results across eval directories into benchmark.json.

Reads all eval-* subdirectories in an iteration directory, collects grading.json
and timing.json from each configuration folder, and produces a benchmark.json
with pass rates, token/duration stats, assertion discrimination analysis, and a
winner determination.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate grading results into benchmark.json.")
    parser.add_argument("--iteration-dir", required=True, help="Path to the iteration directory containing eval-* subdirs.")
    parser.add_argument("--skill-name", required=True, help="Skill name (written into benchmark.json).")
    return parser.parse_args()


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def read_json_safe(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return None


def discover_configs(eval_dir: Path) -> list[str]:
    known = {"with_skill", "without_skill", "old_skill", "new_skill"}
    found = []
    for child in sorted(eval_dir.iterdir()):
        if child.is_dir() and child.name in known:
            found.append(child.name)
    return found


def collect_data(
    iteration_dir: Path,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    """Discover eval dirs and collect grading + timing data per config per eval.

    Returns (sorted eval dir names, data dict keyed by config label).
    """
    eval_dirs = sorted(
        d for d in iteration_dir.iterdir() if d.is_dir() and d.name.startswith("eval-")
    )

    all_configs: set[str] = set()
    for eval_dir in eval_dirs:
        all_configs.update(discover_configs(eval_dir))

    # config_data[config][eval_name] = {"grading": ..., "timing": ...}
    config_data: dict[str, dict[str, Any]] = {cfg: {} for cfg in all_configs}

    for eval_dir in eval_dirs:
        for cfg in all_configs:
            cfg_dir = eval_dir / cfg
            if not cfg_dir.is_dir():
                continue
            grading = read_json_safe(cfg_dir / "grading.json")
            timing = read_json_safe(cfg_dir / "timing.json")
            config_data[cfg][eval_dir.name] = {"grading": grading, "timing": timing}

    return [d.name for d in eval_dirs], config_data


def compute_config_stats(config_runs: dict[str, Any]) -> dict[str, Any]:
    """Compute mean/stddev for pass_rate, tokens, and duration_ms across runs."""
    pass_rates: list[float] = []
    tokens: list[float] = []
    durations: list[float] = []

    for run in config_runs.values():
        grading = run.get("grading")
        timing = run.get("timing")

        if grading:
            summary = grading.get("summary", {})
            pr = summary.get("pass_rate")
            if isinstance(pr, (int, float)):
                pass_rates.append(float(pr))

        if timing:
            t = timing.get("total_tokens")
            d = timing.get("duration_ms")
            if isinstance(t, (int, float)):
                tokens.append(float(t))
            if isinstance(d, (int, float)):
                durations.append(float(d))

    return {
        "runs": len(config_runs),
        "result": {
            "pass_rate": {"mean": round(mean(pass_rates), 4), "stddev": round(stddev(pass_rates), 4)},
            "tokens": {"mean": round(mean(tokens), 1), "stddev": round(stddev(tokens), 1)},
            "duration_ms": {"mean": round(mean(durations), 1), "stddev": round(stddev(durations), 1)},
        },
    }


def collect_assertion_rates(
    config_data: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build per-assertion pass rates across all configs.

    Flags an assertion as non-discriminating if all configs have pass_rate >0.8
    or all configs have pass_rate <0.2.
    """
    all_configs = list(config_data.keys())

    # assertion_text -> config -> list[passed bools]
    assertion_results: dict[str, dict[str, list[bool]]] = {}

    for cfg, runs in config_data.items():
        for _, run in runs.items():
            grading = run.get("grading")
            if not grading:
                continue
            for exp in grading.get("expectations", []):
                text = exp.get("text", "")
                passed = exp.get("passed", False)
                if not text:
                    continue
                assertion_results.setdefault(text, {})
                assertion_results[text].setdefault(cfg, []).append(bool(passed))

    assertions: list[dict[str, Any]] = []
    for text, cfg_results in assertion_results.items():
        entry: dict[str, Any] = {"text": text}
        rates: list[float] = []
        for cfg in all_configs:
            bools = cfg_results.get(cfg, [])
            rate = mean([float(b) for b in bools]) if bools else 0.0
            entry[f"{cfg}_pass_rate"] = round(rate, 4)
            rates.append(rate)

        all_high = all(r > 0.8 for r in rates)
        all_low = all(r < 0.2 for r in rates)
        entry["discriminating"] = not (all_high or all_low)
        assertions.append(entry)

    return assertions


def determine_winner(config_stats: dict[str, dict[str, Any]]) -> tuple[str, float]:
    best_config = ""
    best_rate = -1.0
    for cfg, stats in config_stats.items():
        rate = stats["result"]["pass_rate"]["mean"]
        if rate > best_rate:
            best_rate = rate
            best_config = cfg

    if len(config_stats) >= 2:
        rates = sorted((s["result"]["pass_rate"]["mean"] for s in config_stats.values()), reverse=True)
        margin = round(rates[0] - rates[1], 4)
    else:
        margin = 0.0

    return best_config, margin


def main() -> None:
    args = parse_args()
    iteration_dir = Path(args.iteration_dir)

    if not iteration_dir.is_dir():
        print(f"Error: iteration directory not found: {iteration_dir}", file=sys.stderr)
        sys.exit(1)

    eval_names, config_data = collect_data(iteration_dir)

    if not config_data:
        print("Error: no configuration data found in eval directories.", file=sys.stderr)
        sys.exit(1)

    config_stats = {cfg: compute_config_stats(runs) for cfg, runs in config_data.items()}
    assertions = collect_assertion_rates(config_data)
    winner, margin = determine_winner(config_stats)

    iteration_num = 0
    parts = iteration_dir.name.split("-")
    if len(parts) == 2 and parts[1].isdigit():
        iteration_num = int(parts[1])

    benchmark: dict[str, Any] = {
        "skill_name": args.skill_name,
        "iteration": iteration_num,
        "configurations": config_stats,
        "assertions": assertions,
        "run_summary": {
            "total_evals": len(eval_names),
            "winner": winner,
            "margin": margin,
        },
    }

    output_path = iteration_dir / "benchmark.json"
    output_path.write_text(json.dumps(benchmark, indent=2), encoding="utf-8")

    print(f"Benchmark written to {output_path}")
    print(f"Winner: {winner} (margin: {margin:.2%})")
    print(f"Total evals: {len(eval_names)}")
    for cfg, stats in config_stats.items():
        pr = stats["result"]["pass_rate"]
        print(f"  {cfg}: pass_rate={pr['mean']:.2%} ± {pr['stddev']:.2%} over {stats['runs']} run(s)")

    discriminating = [a for a in assertions if a["discriminating"]]
    non_discriminating = [a for a in assertions if not a["discriminating"]]
    print(f"Assertions: {len(assertions)} total, {len(discriminating)} discriminating, {len(non_discriminating)} non-discriminating")


if __name__ == "__main__":
    main()
