"""Markdown レポート生成

build_daily_stats() の結果を Markdown 文字列に変換する。

利用例::

    from app.analysis.trend_detector import build_daily_stats
    from app.reporting.markdown_report import render_markdown_report

    stats = build_daily_stats()
    md = render_markdown_report(stats)
    print(md)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def render_markdown_report(stats: dict[str, Any]) -> str:
    """stats dict → Markdown 文字列"""
    hours = stats.get("hours", 24)
    total = stats.get("total", 0)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append(f"# AI Dev Trend Report ({hours}h)")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    # サマリー
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- 対象期間: 直近 {hours} 時間")
    lines.append(f"- 対象件数: {total} 件")

    # 品質内訳
    llm_count = stats.get("llm_count", 0)
    fallback_count = stats.get("fallback_count", 0)
    fallback_rate = f"{fallback_count / total * 100:.0f}%" if total > 0 else "0%"
    lines.append(f"- LLM要約: {llm_count} 件 / fallback: {fallback_count} 件 ({fallback_rate})")

    source_counts = stats.get("source_counts", {})
    if source_counts:
        src_parts = [f"{s} ({c})" for s, c in source_counts.items()]
        lines.append(f"- ソース内訳: {', '.join(src_parts)}")

    lines.append("")

    # カテゴリ集計
    category_counts = stats.get("category_counts", {})
    if category_counts:
        lines.append("## Categories")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        for cat, count in category_counts.items():
            lines.append(f"| {cat} | {count} |")
        lines.append("")

    # Top tags
    tag_top = stats.get("tag_top10", {})
    if tag_top:
        lines.append("## Top Tags")
        lines.append("")
        tag_strs = [f"`{t}` ({c})" for t, c in tag_top.items()]
        lines.append(", ".join(tag_strs))
        lines.append("")

    # Highlighted items
    highlighted = stats.get("highlighted", [])
    if highlighted:
        lines.append("## Highlighted")
        lines.append("")
        for i, h in enumerate(highlighted, 1):
            tags = ", ".join(h.get("tags", [])) or "-"
            buzz = h.get("buzz_score", 0.0)
            is_fallback = h.get("buzz_reason", "") == "(LLM未使用)"
            mark = "[fallback]" if is_fallback else "[LLM]"
            lines.append(f"### {i}. [{h.get('category', '?')}] {mark} buzz={buzz:.1f}")
            lines.append("")
            lines.append(f"> {h.get('short_summary', '')}")
            lines.append("")
            lines.append(f"- tags: {tags}")
            reason = h.get("buzz_reason", "")
            if reason:
                lines.append(f"- reason: {reason}")
            lines.append("")

    # 空データ時
    if total == 0:
        lines.append("対象期間内のデータがありません。")
        lines.append("")

    return "\n".join(lines)
