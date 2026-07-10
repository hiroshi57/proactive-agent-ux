"""進捗の可視化. ワンクリック実行したアクションをステップに分解し状態遷移させる."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List

# アクション種別ごとの実行ステップ(mock)
_STEPS: Dict[str, List[str]] = {
    "send_reminder": ["宛先を解決", "文面を生成", "メール送信", "送信ログ記録"],
    "assign_owner": ["候補者をスコアリング", "最適担当を選定", "アサイン適用"],
    "generate_report": ["データ収集", "集計", "レポート整形", "保存"],
    "drilldown": ["対象メトリクスを特定", "関連データ取得", "ビュー生成"],
}


@dataclass
class Step:
    name: str
    status: str = "pending"      # pending / running / done

    def as_dict(self):
        return {"name": self.name, "status": self.status}


@dataclass
class ProgressTask:
    id: str
    action_type: str
    steps: List[Step]

    @property
    def progress(self) -> float:
        done = sum(1 for s in self.steps if s.status == "done")
        return done / len(self.steps) if self.steps else 1.0

    @property
    def completed(self) -> bool:
        return all(s.status == "done" for s in self.steps)

    def as_dict(self):
        return {"id": self.id, "action_type": self.action_type,
                "progress": round(self.progress, 2), "completed": self.completed,
                "steps": [s.as_dict() for s in self.steps]}


class ProgressRunner:
    def __init__(self) -> None:
        self._seq = itertools.count(1)
        self._tasks: Dict[str, ProgressTask] = {}

    def start(self, action_type: str) -> ProgressTask:
        steps = [Step(n) for n in _STEPS.get(action_type, ["実行"])]
        task = ProgressTask(id=f"task-{next(self._seq)}", action_type=action_type, steps=steps)
        self._tasks[task.id] = task
        return task

    def advance(self, task_id: str) -> ProgressTask:
        """次の pending ステップを done にする(1ステップ進める)."""
        task = self._tasks[task_id]
        for s in task.steps:
            if s.status != "done":
                s.status = "done"
                break
        return task

    def run_all(self, action_type: str) -> ProgressTask:
        """ワンクリック実行: 全ステップを完了まで進める."""
        task = self.start(action_type)
        while not task.completed:
            self.advance(task.id)
        return task

    def get(self, task_id: str) -> ProgressTask:
        return self._tasks[task_id]
