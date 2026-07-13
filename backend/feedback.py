"""フィードバック学習(全機能). 採用/却下履歴で提案の確信度を適応調整する.

繰り返し却下される提案は下げ、採用される提案は上げる。十分な回数却下されたら
提案自体を抑制する(=ユーザーに学習して寄り添うプロアクティブ性)。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class FeedbackStat:
    accepts: int = 0
    dismisses: int = 0

    @property
    def total(self) -> int:
        return self.accepts + self.dismisses

    @property
    def acceptance_rate(self) -> float:
        # ベイズ平滑化(Beta(1,1)事前): (a+1)/(a+d+2)
        return (self.accepts + 1) / (self.total + 2)


class FeedbackStore:
    def __init__(self, suppress_after: int = 3, suppress_threshold: float = 0.8) -> None:
        self._stats: Dict[str, FeedbackStat] = {}
        self.suppress_after = suppress_after         # 抑制判定に必要な最小回数
        self.suppress_threshold = suppress_threshold  # 却下率がこれ以上で抑制

    def _stat(self, sid: str) -> FeedbackStat:
        return self._stats.setdefault(sid, FeedbackStat())

    def record_accept(self, sid: str) -> None:
        self._stat(sid).accepts += 1

    def record_dismiss(self, sid: str) -> None:
        self._stat(sid).dismisses += 1

    def confidence_multiplier(self, sid: str) -> float:
        """採用率に基づく0.5〜1.5の乗数(未学習は1.0)."""
        st = self._stats.get(sid)
        if st is None or st.total == 0:
            return 1.0
        return 0.5 + st.acceptance_rate   # acceptance_rate∈(0,1) -> 乗数∈(0.5,1.5)

    def is_suppressed(self, sid: str) -> bool:
        st = self._stats.get(sid)
        if st is None or st.total < self.suppress_after:
            return False
        dismiss_rate = st.dismisses / st.total
        return dismiss_rate >= self.suppress_threshold

    def stats(self, sid: str) -> FeedbackStat:
        return self._stat(sid)
