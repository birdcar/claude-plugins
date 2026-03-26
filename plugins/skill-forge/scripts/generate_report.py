#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

"""Generate a self-contained HTML eval viewer from benchmark data.

In server mode (default): starts an HTTP server, opens the browser, and waits
for feedback to be submitted via POST /feedback before shutting down.

In static mode (--static <path>): writes the HTML file and exits immediately.
"""

from __future__ import annotations

import argparse
import html
import http.server
import json
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate HTML eval viewer from benchmark data.")
    parser.add_argument("--iteration-dir", required=True, help="Path to the iteration directory.")
    parser.add_argument("--skill-name", required=True, help="Skill name for display.")
    parser.add_argument("--benchmark", required=True, help="Path to benchmark.json.")
    parser.add_argument("--static", default="", help="Write HTML to this path and exit (no server).")
    parser.add_argument("--port", type=int, default=8765, help="Port for the local HTTP server (default: 8765).")
    return parser.parse_args()


def read_json_safe(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return None


def read_text_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def collect_eval_data(iteration_dir: Path) -> list[dict[str, Any]]:
    eval_dirs = sorted(
        d for d in iteration_dir.iterdir() if d.is_dir() and d.name.startswith("eval-")
    )
    evals: list[dict[str, Any]] = []
    known_configs = {"with_skill", "without_skill", "old_skill", "new_skill"}

    for eval_dir in eval_dirs:
        metadata = read_json_safe(eval_dir / "eval_metadata.json") or {}
        comparison = read_json_safe(eval_dir / "comparison.json")
        analysis = read_json_safe(eval_dir / "analysis.json")

        configs: dict[str, Any] = {}
        for cfg_dir in sorted(eval_dir.iterdir()):
            if cfg_dir.is_dir() and cfg_dir.name in known_configs:
                configs[cfg_dir.name] = {
                    "grading": read_json_safe(cfg_dir / "grading.json"),
                    "timing": read_json_safe(cfg_dir / "timing.json"),
                    "metrics": read_json_safe(cfg_dir / "metrics.json"),
                    "transcript": read_text_safe(cfg_dir / "transcript.txt"),
                }

        evals.append({
            "name": eval_dir.name,
            "metadata": metadata,
            "configs": configs,
            "comparison": comparison,
            "analysis": analysis,
        })

    return evals


def build_svg_bar_chart(labels: list[str], values: list[float], title: str, color: str = "#4f8ef7") -> str:
    bar_width = 60
    gap = 20
    height = 160
    max_val = max(values) if values else 1.0
    chart_width = len(labels) * (bar_width + gap) + gap

    bars = ""
    label_els = ""
    value_els = ""
    for i, (label, val) in enumerate(zip(labels, values)):
        bar_h = int((val / max_val) * 100) if max_val else 0
        x = gap + i * (bar_width + gap)
        y = 110 - bar_h
        bars += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" fill="{color}" rx="3"/>'
        safe_label = html.escape(label[:12])
        label_els += f'<text x="{x + bar_width // 2}" y="128" text-anchor="middle" font-size="10" fill="#aaa">{safe_label}</text>'
        value_els += f'<text x="{x + bar_width // 2}" y="{y - 4}" text-anchor="middle" font-size="10" fill="#eee">{val:.2f}</text>'

    return (
        f'<div style="margin:12px 0"><div style="color:#aaa;font-size:12px;margin-bottom:4px">{html.escape(title)}</div>'
        f'<svg width="{chart_width}" height="{height}" style="background:#1a1a2e;border-radius:6px">'
        f"{bars}{label_els}{value_els}"
        f"</svg></div>"
    )


def render_assertion_table(assertions: list[dict[str, Any]], configs: list[str]) -> str:
    if not assertions:
        return "<p style='color:#888'>No assertions found.</p>"

    header_cells = "".join(f"<th>{html.escape(c)}</th>" for c in configs)
    rows = ""
    for a in assertions:
        text = html.escape(a.get("text", ""))
        disc = a.get("discriminating", True)
        disc_badge = "" if disc else " <span style='color:#f0c040;font-size:11px'>[non-discriminating]</span>"
        cells = ""
        for cfg in configs:
            rate = a.get(f"{cfg}_pass_rate")
            if rate is None:
                cells += "<td style='color:#555'>—</td>"
            else:
                pct = rate * 100
                color = "#4caf50" if rate >= 0.8 else ("#f44336" if rate <= 0.2 else "#f0c040")
                cells += f"<td style='color:{color};font-weight:bold'>{pct:.0f}%</td>"
        rows += f"<tr><td>{text}{disc_badge}</td>{cells}</tr>"

    return (
        f"<table style='border-collapse:collapse;width:100%'>"
        f"<thead><tr><th style='text-align:left'>Assertion</th>{header_cells}</tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def render_evals_section(evals: list[dict[str, Any]]) -> str:
    if not evals:
        return "<p style='color:#888'>No eval runs found.</p>"

    sections = []
    for ev in evals:
        name = html.escape(ev["name"])
        prompt = html.escape(ev["metadata"].get("prompt", ""))
        tabs = ""
        panels = ""
        for cfg, data in ev["configs"].items():
            safe_cfg = html.escape(cfg)
            transcript = html.escape(data.get("transcript", "") or "")
            panel_id = f"{ev['name']}-{cfg}"
            tabs += f'<button onclick="showTab(\'{panel_id}\')" class="tab-btn" id="btn-{panel_id}">{safe_cfg}</button>'
            panels += (
                f'<div id="{panel_id}" class="tab-panel" style="display:none">'
                f'<pre style="white-space:pre-wrap;word-break:break-word;font-size:12px;color:#ccc;background:#111;padding:12px;border-radius:6px;max-height:400px;overflow-y:auto">{transcript or "(no transcript)"}</pre>'
                f"</div>"
            )

        comparison = ev.get("comparison") or {}
        comp_html = ""
        if comparison:
            winner = html.escape(str(comparison.get("winner", "")))
            reasoning = html.escape(str(comparison.get("reasoning", "")))
            comp_html = f"<p><strong>Blind comparison winner:</strong> {winner}</p><p style='color:#aaa;font-size:13px'>{reasoning}</p>"

        sections.append(
            f"<div style='margin-bottom:32px;border:1px solid #333;border-radius:8px;padding:16px'>"
            f"<h3 style='color:#4f8ef7;margin:0 0 8px'>{name}</h3>"
            f"<p style='color:#aaa;font-size:13px'><em>{prompt}</em></p>"
            f"<div style='margin:8px 0'>{tabs}</div>"
            f"<div>{panels}</div>"
            f"{comp_html}"
            f"</div>"
        )

    return "\n".join(sections)


def render_insights(evals: list[dict[str, Any]]) -> str:
    all_suggestions: list[dict[str, Any]] = []
    for ev in evals:
        analysis = ev.get("analysis") or {}
        for s in analysis.get("improvement_suggestions", []):
            all_suggestions.append(s)

    if not all_suggestions:
        return "<p style='color:#888'>No analyzer insights available.</p>"

    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_suggestions.sort(key=lambda s: priority_order.get(s.get("priority", "low"), 2))

    items = []
    for s in all_suggestions:
        priority = s.get("priority", "low")
        color = {"high": "#f44336", "medium": "#f0c040", "low": "#4caf50"}.get(priority, "#888")
        desc = html.escape(str(s.get("description", "")))
        category = html.escape(str(s.get("category", "")))
        items.append(
            f"<li style='margin-bottom:8px'>"
            f"<span style='color:{color};font-size:11px;text-transform:uppercase;font-weight:bold'>[{priority}]</span> "
            f"<span style='color:#aaa;font-size:11px'>[{category}]</span> {desc}"
            f"</li>"
        )

    return f"<ul style='list-style:none;padding:0'>{''.join(items)}</ul>"


def render_feedback_form(assertions: list[dict[str, Any]], static: bool) -> str:
    assertion_checks = ""
    for a in assertions:
        text = html.escape(a.get("text", ""))
        assertion_checks += (
            f"<div style='margin:6px 0'>"
            f"<label><input type='checkbox' name='keep' value='{text}' checked> Keep: {text}</label>"
            f"</div>"
        )

    submit_action = "submitFeedbackStatic()" if static else "submitFeedback()"

    return f"""
<form id="feedback-form" onsubmit="event.preventDefault();{submit_action}">
  <div style="margin-bottom:16px">
    <label style="display:block;margin-bottom:6px;color:#aaa">Overall rating</label>
    <div id="star-rating" style="font-size:28px;cursor:pointer">
      {''.join(f'<span class="star" data-val="{i}" onclick="setRating({i})" style="color:#555">&#9733;</span>' for i in range(1, 6))}
    </div>
    <input type="hidden" id="rating-value" name="rating" value="0">
  </div>
  <div style="margin-bottom:16px">
    <label style="display:block;margin-bottom:6px;color:#aaa">Notes</label>
    <textarea name="notes" id="feedback-notes" rows="4" style="width:100%;background:#1a1a2e;color:#eee;border:1px solid #333;border-radius:6px;padding:8px;font-size:14px"></textarea>
  </div>
  <div style="margin-bottom:16px">
    <label style="display:block;margin-bottom:8px;color:#aaa">Assertion feedback</label>
    {assertion_checks}
  </div>
  <div style="margin-bottom:16px">
    <label style="display:block;margin-bottom:6px;color:#aaa">Next action</label>
    <select name="next_action" id="next-action" style="background:#1a1a2e;color:#eee;border:1px solid #333;border-radius:6px;padding:8px">
      <option value="iterate">Iterate (revise skill)</option>
      <option value="done">Done (accept results)</option>
      <option value="more_evals">Run more evals</option>
    </select>
  </div>
  <button type="submit" style="background:#4f8ef7;color:#fff;border:none;padding:10px 24px;border-radius:6px;font-size:15px;cursor:pointer">Submit Feedback</button>
  <span id="feedback-status" style="margin-left:12px;color:#4caf50"></span>
</form>
"""


def build_html(
    skill_name: str,
    benchmark: dict[str, Any],
    evals: list[dict[str, Any]],
    static: bool,
) -> str:
    configs = list(benchmark.get("configurations", {}).keys())
    assertions = benchmark.get("assertions", [])
    run_summary = benchmark.get("run_summary", {})
    winner = run_summary.get("winner", "")
    margin = run_summary.get("margin", 0.0)
    total_evals = run_summary.get("total_evals", 0)

    config_stats_html = ""
    for cfg, stats in benchmark.get("configurations", {}).items():
        pr = stats.get("result", {}).get("pass_rate", {})
        tok = stats.get("result", {}).get("tokens", {})
        dur = stats.get("result", {}).get("duration_ms", {})
        is_winner = cfg == winner
        border = "border:2px solid #4f8ef7" if is_winner else "border:1px solid #333"
        config_stats_html += (
            f"<div style='flex:1;{border};border-radius:8px;padding:16px;min-width:180px'>"
            f"<div style='color:#4f8ef7;font-weight:bold;margin-bottom:8px'>{html.escape(cfg)}"
            + (" <span style='color:#4caf50;font-size:12px'>[WINNER]</span>" if is_winner else "")
            + f"</div>"
            f"<div style='color:#aaa;font-size:13px'>Pass rate: <strong style='color:#eee'>{pr.get('mean', 0):.2%}</strong> ± {pr.get('stddev', 0):.2%}</div>"
            f"<div style='color:#aaa;font-size:13px'>Tokens: {tok.get('mean', 0):.0f} ± {tok.get('stddev', 0):.0f}</div>"
            f"<div style='color:#aaa;font-size:13px'>Duration: {dur.get('mean', 0) / 1000:.1f}s ± {dur.get('stddev', 0) / 1000:.1f}s</div>"
            f"</div>"
        )

    pr_labels = [html.escape(c) for c in configs]
    pr_values = [benchmark.get("configurations", {}).get(c, {}).get("result", {}).get("pass_rate", {}).get("mean", 0.0) for c in configs]
    tok_values = [benchmark.get("configurations", {}).get(c, {}).get("result", {}).get("tokens", {}).get("mean", 0.0) for c in configs]
    dur_values = [benchmark.get("configurations", {}).get(c, {}).get("result", {}).get("duration_ms", {}).get("mean", 0.0) / 1000 for c in configs]

    charts_html = (
        build_svg_bar_chart(pr_labels, pr_values, "Pass Rate (mean)", "#4f8ef7")
        + build_svg_bar_chart(pr_labels, tok_values, "Tokens (mean)", "#7c4dff")
        + build_svg_bar_chart(pr_labels, dur_values, "Duration seconds (mean)", "#00bcd4")
    )

    embedded_data = json.dumps({
        "benchmark": benchmark,
        "evals": evals,
        "skill_name": skill_name,
    }, ensure_ascii=False)

    submit_js = (
        """
async function submitFeedback() {
  const payload = buildFeedbackPayload();
  try {
    const resp = await fetch('/feedback', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    document.getElementById('feedback-status').textContent = resp.ok ? 'Feedback submitted!' : 'Error submitting.';
  } catch(e) {
    document.getElementById('feedback-status').textContent = 'Error: ' + e;
  }
}
"""
        if not static
        else """
function submitFeedbackStatic() {
  const payload = buildFeedbackPayload();
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'feedback.json'; a.click();
  document.getElementById('feedback-status').textContent = 'feedback.json downloaded.';
}
"""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eval Report: {html.escape(skill_name)}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d0d1a;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;line-height:1.6}}
h1,h2,h3{{color:#fff;margin-bottom:12px}}
h2{{font-size:18px;border-bottom:1px solid #333;padding-bottom:6px;margin:32px 0 16px}}
section{{padding:24px;max-width:1100px;margin:0 auto}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{padding:8px 12px;border:1px solid #333;text-align:left}}
th{{background:#1a1a2e;color:#aaa;font-weight:600}}
tr:hover td{{background:#1a1a2e}}
.tab-btn{{background:#1a1a2e;color:#aaa;border:1px solid #333;padding:6px 14px;border-radius:4px;cursor:pointer;margin-right:6px;font-size:13px}}
.tab-btn:hover,.tab-btn.active{{background:#4f8ef7;color:#fff}}
.star{{transition:color 0.1s}}
.star.active{{color:#f0c040}}
</style>
</head>
<body>
<div style="background:#1a1a2e;padding:16px 24px;border-bottom:1px solid #333">
  <h1 style="font-size:22px">Eval Report: {html.escape(skill_name)}</h1>
  <div style="color:#aaa;font-size:13px">Winner: <strong style="color:#4caf50">{html.escape(winner)}</strong> &nbsp;|&nbsp; Margin: {margin:.2%} &nbsp;|&nbsp; Total evals: {total_evals}</div>
</div>

<section>
  <h2>Summary</h2>
  <div style="display:flex;gap:16px;flex-wrap:wrap">{config_stats_html}</div>
</section>

<section>
  <h2>Assertion Results</h2>
  {render_assertion_table(assertions, configs)}
</section>

<section>
  <h2>Output Comparison</h2>
  {render_evals_section(evals)}
</section>

<section>
  <h2>Metrics</h2>
  {charts_html}
</section>

<section>
  <h2>Analyzer Insights</h2>
  {render_insights(evals)}
</section>

<section>
  <h2>Feedback</h2>
  {render_feedback_form(assertions, static)}
</section>

<script>
const __data__ = {embedded_data};

function showTab(id) {{
  const panels = document.querySelectorAll('.tab-panel');
  panels.forEach(p => p.style.display = 'none');
  document.getElementById(id).style.display = 'block';
}}

function setRating(val) {{
  document.getElementById('rating-value').value = val;
  document.querySelectorAll('.star').forEach(s => {{
    s.classList.toggle('active', parseInt(s.dataset.val) <= val);
  }});
}}

function buildFeedbackPayload() {{
  const form = document.getElementById('feedback-form');
  const rating = parseInt(document.getElementById('rating-value').value) || 0;
  const notes = document.getElementById('feedback-notes').value;
  const nextAction = document.getElementById('next-action').value;
  const checks = Array.from(form.querySelectorAll('input[name=keep]'));
  const assertionFeedback = checks.map(el => ({{text: el.value, keep: el.checked, note: ''}}));
  return {{
    submitted_at: new Date().toISOString(),
    overall_rating: rating,
    notes: notes,
    assertion_feedback: assertionFeedback,
    next_action: nextAction,
  }};
}}

{submit_js}
</script>
</body>
</html>"""


class FeedbackHandler(http.server.BaseHTTPRequestHandler):
    html_content: bytes = b""
    feedback_path: Path = Path("feedback.json")
    shutdown_event: threading.Event = threading.Event()

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.html_content)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        if urlparse(self.path).path == "/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body)
                self.feedback_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
                print(f"Feedback written to {self.feedback_path}", file=sys.stderr)
                self.shutdown_event.set()
            except (json.JSONDecodeError, OSError) as exc:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass


def serve_html(html_content: str, feedback_path: Path, port: int) -> None:
    FeedbackHandler.html_content = html_content.encode("utf-8")
    FeedbackHandler.feedback_path = feedback_path
    shutdown_event = threading.Event()
    FeedbackHandler.shutdown_event = shutdown_event

    server = http.server.HTTPServer(("127.0.0.1", port), FeedbackHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"Serving eval report at {url}")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    webbrowser.open(url)
    print("Waiting for feedback submission... (Ctrl-C to abort)")

    try:
        shutdown_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        print("Server stopped.")


def main() -> None:
    args = parse_args()

    iteration_dir = Path(args.iteration_dir)
    benchmark_path = Path(args.benchmark)

    if not iteration_dir.is_dir():
        print(f"Error: iteration directory not found: {iteration_dir}", file=sys.stderr)
        sys.exit(1)

    benchmark = read_json_safe(benchmark_path)
    if not benchmark:
        print(f"Error: could not read benchmark.json from {benchmark_path}", file=sys.stderr)
        sys.exit(1)

    evals = collect_eval_data(iteration_dir)
    static_mode = bool(args.static)

    report_html = build_html(args.skill_name, benchmark, evals, static=static_mode)

    if static_mode:
        out_path = Path(args.static)
        out_path.write_text(report_html, encoding="utf-8")
        print(f"Report written to {out_path}")
        return

    feedback_path = iteration_dir / "feedback.json"
    serve_html(report_html, feedback_path, args.port)


if __name__ == "__main__":
    main()
