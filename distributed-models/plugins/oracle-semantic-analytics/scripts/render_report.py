#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from analytics_config import runtime_settings


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:80] or "oracle-semantic-report"


def coerce_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def normalize_payload(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Report payload must be a JSON object.")
    columns = payload.get("columns") or []
    rows = payload.get("rows") or []
    if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
        raise ValueError("Payload field 'columns' must be a list of strings.")
    if not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
        raise ValueError("Payload field 'rows' must be a list of row arrays.")
    return payload


def infer_chart(columns: list[str], rows: list[list[Any]], requested: str | None) -> dict[str, Any]:
    if requested and requested != "auto":
        chart_type = requested
    elif len(rows) < 2 or len(columns) < 2:
        chart_type = "none"
    else:
        chart_type = "bar"
        first = columns[0].lower()
        if any(token in first for token in ["term", "year", "date", "month", "period"]):
            chart_type = "line"

    numeric_index = None
    for idx in range(1, len(columns)):
        numeric_values = [coerce_number(row[idx]) for row in rows if idx < len(row)]
        if numeric_values and all(value is not None for value in numeric_values):
            numeric_index = idx
            break

    if chart_type != "none" and numeric_index is None:
        chart_type = "none"

    return {
        "type": chart_type,
        "label_index": 0,
        "value_index": numeric_index,
    }


def render_table(columns: list[str], rows: list[list[Any]]) -> str:
    header = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
    body_rows = []
    for row in rows:
        cells = []
        for idx, _col in enumerate(columns):
            value = row[idx] if idx < len(row) else ""
            cells.append(f"<td>{html.escape('' if value is None else str(value))}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def render_chart_script(columns: list[str], rows: list[list[Any]], chart: dict[str, Any]) -> str:
    chart_type = chart["type"]
    if chart_type == "none":
        return ""
    label_index = chart["label_index"]
    value_index = chart["value_index"]
    points = []
    for row in rows:
        if label_index >= len(row) or value_index is None or value_index >= len(row):
            continue
        value = coerce_number(row[value_index])
        if value is None:
            continue
        points.append({"label": str(row[label_index]), "value": value})
    if not points:
        return ""

    chart_data = json.dumps(points)
    value_label = columns[value_index]
    return f"""
<section>
  <h2>Visualization</h2>
  <canvas id="chart" width="960" height="420" role="img" aria-label="{html.escape(chart_type)} chart of {html.escape(value_label)}"></canvas>
</section>
<script>
const chartType = {json.dumps(chart_type)};
const data = {chart_data};
const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");
const width = canvas.width;
const height = canvas.height;
const margin = {{ left: 70, right: 24, top: 28, bottom: 78 }};
const plotW = width - margin.left - margin.right;
const plotH = height - margin.top - margin.bottom;
const maxValue = Math.max(...data.map(d => d.value), 1);

ctx.clearRect(0, 0, width, height);
ctx.font = "13px system-ui, -apple-system, Segoe UI, sans-serif";
ctx.strokeStyle = "#d0d7de";
ctx.fillStyle = "#57606a";
ctx.beginPath();
ctx.moveTo(margin.left, margin.top);
ctx.lineTo(margin.left, height - margin.bottom);
ctx.lineTo(width - margin.right, height - margin.bottom);
ctx.stroke();

for (let i = 0; i <= 4; i++) {{
  const y = margin.top + plotH - (plotH * i / 4);
  const value = Math.round(maxValue * i / 4);
  ctx.fillText(String(value), 12, y + 4);
  ctx.strokeStyle = "#eef1f4";
  ctx.beginPath();
  ctx.moveTo(margin.left, y);
  ctx.lineTo(width - margin.right, y);
  ctx.stroke();
}}

if (chartType === "line") {{
  ctx.strokeStyle = "#0969da";
  ctx.lineWidth = 3;
  ctx.beginPath();
  data.forEach((d, i) => {{
    const x = margin.left + (data.length === 1 ? plotW / 2 : plotW * i / (data.length - 1));
    const y = margin.top + plotH - (d.value / maxValue) * plotH;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }});
  ctx.stroke();
  data.forEach((d, i) => {{
    const x = margin.left + (data.length === 1 ? plotW / 2 : plotW * i / (data.length - 1));
    const y = margin.top + plotH - (d.value / maxValue) * plotH;
    ctx.fillStyle = "#0969da";
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  }});
}} else {{
  const gap = 8;
  const barW = Math.max(10, (plotW - gap * (data.length - 1)) / data.length);
  data.forEach((d, i) => {{
    const x = margin.left + i * (barW + gap);
    const barH = (d.value / maxValue) * plotH;
    const y = margin.top + plotH - barH;
    ctx.fillStyle = "#0969da";
    ctx.fillRect(x, y, barW, barH);
  }});
}}

ctx.fillStyle = "#24292f";
data.forEach((d, i) => {{
  const x = chartType === "line"
    ? margin.left + (data.length === 1 ? plotW / 2 : plotW * i / (data.length - 1))
    : margin.left + i * (plotW / data.length) + plotW / data.length / 2;
  ctx.save();
  ctx.translate(x, height - margin.bottom + 18);
  ctx.rotate(-Math.PI / 4);
  ctx.fillText(d.label, 0, 0);
  ctx.restore();
}});
</script>
"""


def render_html(payload: dict[str, Any]) -> str:
    question = str(payload.get("question") or "Oracle semantic analytics report")
    sql = str(payload.get("sql") or "")
    summary = str(payload.get("summary") or "")
    columns = payload["columns"]
    rows = payload["rows"]
    chart = infer_chart(columns, rows, payload.get("chart_type"))
    chart_script = render_chart_script(columns, rows, chart)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(question)}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 32px; color: #24292f; }}
    main {{ max-width: 1120px; margin: 0 auto; }}
    h1 {{ font-size: 24px; margin: 0 0 8px; }}
    h2 {{ font-size: 18px; margin-top: 28px; }}
    .meta {{ color: #57606a; font-size: 13px; margin-bottom: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; }}
    th {{ background: #f6f8fa; }}
    pre {{ background: #f6f8fa; border: 1px solid #d0d7de; padding: 12px; overflow: auto; }}
    canvas {{ max-width: 100%; border: 1px solid #d0d7de; }}
  </style>
</head>
<body>
<main>
  <h1>{html.escape(question)}</h1>
  <div class="meta">Generated {html.escape(generated_at)} · Chart decision: {html.escape(chart["type"])}</div>
  {f"<section><h2>Summary</h2><p>{html.escape(summary)}</p></section>" if summary else ""}
  {chart_script}
  <section>
    <h2>Result Table</h2>
    {render_table(columns, rows)}
  </section>
  {f"<section><h2>Validated SQL</h2><pre>{html.escape(sql)}</pre></section>" if sql else ""}
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", help="Path to report JSON payload, or '-' to read JSON from stdin.")
    args = parser.parse_args()

    raw = Path(args.payload).read_text(encoding="utf-8-sig") if args.payload != "-" else __import__("sys").stdin.read().lstrip("\ufeff")
    payload = normalize_payload(raw)
    reports_dir = Path(runtime_settings()["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(str(payload.get('question') or 'report'))}.html"
    path = reports_dir / filename
    path.write_text(render_html(payload), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
