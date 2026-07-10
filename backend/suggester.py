"""先読み提案エンジン. ユーザーの文脈から次の意図を予測し提案する.

差別化: すべての提案に「なぜ提案したか(reason)」と「ワンクリック実行アクション」を必ず付ける。
理由のない提案は生成しない(ブラックボックス提案の排除)。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Action:
    type: str                # 例: send_reminder / assign_owner / generate_report
    label: str               # ボタン文言(ワンクリック)
    args: Dict = field(default_factory=dict)


@dataclass
class Suggestion:
    id: str
    title: str
    reason: str              # ★なぜ提案したか(必須・空不可)
    action: Action           # ★ワンクリック実行
    confidence: float        # 0-1

    def as_dict(self):
        return {
            "id": self.id, "title": self.title, "reason": self.reason,
            "confidence": round(self.confidence, 2),
            "action": {"type": self.action.type, "label": self.action.label, "args": self.action.args},
        }


class SuggestionEngine:
    """文脈(recent_actions, view, pending 等) -> ルールで先読み提案."""

    def suggest(self, context: Dict) -> List[Suggestion]:
        recent = context.get("recent_actions", [])
        pending = context.get("pending", {})
        view = context.get("current_view", "")
        tod = context.get("time_of_day", "")   # morning/afternoon/evening
        out: List[Suggestion] = []

        # 1. 未払い請求書を閲覧 -> リマインド送信を先読み
        if "viewed_invoice" in recent and pending.get("unpaid_invoice"):
            inv = pending["unpaid_invoice"]
            out.append(Suggestion(
                id="remind_payment",
                title="支払いリマインドを送信",
                reason=f"請求書#{inv.get('id')} が未払いで支払期限まで残り{inv.get('days_left')}日です",
                action=Action("send_reminder", "リマインド送信", {"invoice_id": inv.get("id")}),
                confidence=0.9 if inv.get("days_left", 99) <= 3 else 0.7,
            ))

        # 2. チケット作成直後 -> 担当者アサインを先読み
        if "created_ticket" in recent and pending.get("unassigned_ticket"):
            tk = pending["unassigned_ticket"]
            out.append(Suggestion(
                id="assign_owner",
                title="担当者をアサイン",
                reason=f"新規チケット#{tk.get('id')} に担当者が未設定です",
                action=Action("assign_owner", "自動アサイン", {"ticket_id": tk.get("id")}),
                confidence=0.8,
            ))

        # 3. 朝 + 未生成の日次レポート -> レポート生成を先読み
        if tod == "morning" and pending.get("daily_report_due"):
            out.append(Suggestion(
                id="gen_daily_report",
                title="日次レポートを生成",
                reason="毎朝この時間帯に日次レポートを作成しており、本日分が未生成です",
                action=Action("generate_report", "レポート生成", {"kind": "daily"}),
                confidence=0.75,
            ))

        # 4. ダッシュボード閲覧 + 異常値 -> ドリルダウンを先読み
        if view == "dashboard" and pending.get("anomaly"):
            an = pending["anomaly"]
            out.append(Suggestion(
                id="drill_anomaly",
                title=f"{an.get('metric')}の異常を調査",
                reason=f"{an.get('metric')} が平常比{an.get('delta')}変化しています",
                action=Action("drilldown", "詳細を開く", {"metric": an.get("metric")}),
                confidence=0.85,
            ))

        # 不変条件: reason は必ず非空
        for s in out:
            assert s.reason, "提案には理由が必須"
        out.sort(key=lambda s: s.confidence, reverse=True)
        return out
