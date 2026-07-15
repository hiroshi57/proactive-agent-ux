"""提案採用率 HTMLレポート(標準ライブラリのみ)."""
from __future__ import annotations

import html
from typing import List, Dict


def build_html_report(acceptance: List[Dict]) -> str:
    rows = ""
    for a in acceptance:
        rate = a["acceptance_rate"]
        bar_w = int(rate * 120)
        rows += (f'<tr><td>{html.escape(a["suggestion_id"])}</td>'
                 f'<td>{a["accepts"]}/{a["total"]}</td>'
                 f'<td><div style="background:#e4e7ee;width:120px;height:12px;border-radius:4px;display:inline-block">'
                 f'<div style="background:#4361ee;height:12px;border-radius:4px;width:{bar_w}px"></div></div> '
                 f'{rate:.0%}</td></tr>')
    return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<title>先読み提案 学習レポート</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;color:#1a1a2e}}
h1{{color:#4361ee}} table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #dde;padding:6px 10px}} th{{background:#eaeefb}}</style></head><body>
<h1>先読み提案 学習レポート</h1>
<p>提案ごとの採用率（低採用は自動抑制の対象）</p>
<table><tr><th>提案ID</th><th>採用/提示</th><th>採用率</th></tr>{rows}</table>
</body></html>"""
