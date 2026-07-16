"""バンディット型 提案ランキング(尖った武器).

各提案タイプの採用実績(成功/失敗)を Beta 分布でモデル化し、Thompson Sampling で
「期待採用価値」の高い提案を優先提示する。探索と活用を両立し、提示の質を自律最適化する。
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List


def _beta_sample(alpha: float, beta: float, rng: random.Random) -> float:
    """Beta(alpha,beta) をガンマ2本から生成(標準ライブラリのみ)."""
    ga = rng.gammavariate(alpha, 1.0)
    gb = rng.gammavariate(beta, 1.0)
    return ga / (ga + gb) if (ga + gb) > 0 else 0.0


@dataclass
class ArmStat:
    accepts: int = 0
    dismisses: int = 0

    @property
    def posterior_mean(self) -> float:
        return (self.accepts + 1) / (self.accepts + self.dismisses + 2)


class SuggestionBandit:
    """提案ID(=arm)ごとの採用/却下を学習し、期待価値順にランキングする."""

    def __init__(self, seed: int = 42) -> None:
        self._arms: Dict[str, ArmStat] = {}
        self._rng = random.Random(seed)

    def update(self, suggestion_id: str, accepted: bool) -> None:
        st = self._arms.setdefault(suggestion_id, ArmStat())
        if accepted:
            st.accepts += 1
        else:
            st.dismisses += 1

    def score(self, suggestion_id: str) -> float:
        """Thompson Sampling: 事後Betaからの1サンプル(探索込みの期待価値)."""
        st = self._arms.get(suggestion_id, ArmStat())
        return _beta_sample(st.accepts + 1, st.dismisses + 1, self._rng)

    def posterior_mean(self, suggestion_id: str) -> float:
        return self._arms.get(suggestion_id, ArmStat()).posterior_mean

    def rank(self, suggestion_ids: List[str]) -> List[str]:
        """Thompson サンプリング値で降順ランキング."""
        return sorted(suggestion_ids, key=lambda sid: self.score(sid), reverse=True)

    def rank_by_mean(self, suggestion_ids: List[str]) -> List[str]:
        """事後平均で降順(探索なしの確定ランキング, 説明・可視化用)."""
        return sorted(suggestion_ids, key=lambda sid: self.posterior_mean(sid), reverse=True)
