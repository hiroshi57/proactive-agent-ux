"""永続化層(SQLite, 標準ライブラリ). フィードバック(採用/却下)保存. テナント分離.

保存済み履歴から FeedbackStore を再構築し、テナント別に学習した確信度調整・抑制を適用する。
"""
from __future__ import annotations

import sqlite3
from typing import Dict, List

from backend import FeedbackStore

SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    suggestion_id TEXT NOT NULL,
    accepted INTEGER NOT NULL
);
"""


class ServiceDB:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def record(self, tenant_id: str, suggestion_id: str, accepted: bool) -> None:
        self.conn.execute(
            "INSERT INTO feedback(tenant_id, suggestion_id, accepted) VALUES (?,?,?)",
            (tenant_id, suggestion_id, 1 if accepted else 0))
        self.conn.commit()

    def build_store(self, tenant_id: str) -> FeedbackStore:
        store = FeedbackStore()
        rows = self.conn.execute(
            "SELECT suggestion_id, accepted FROM feedback WHERE tenant_id=?", (tenant_id,)).fetchall()
        for r in rows:
            if r["accepted"]:
                store.record_accept(r["suggestion_id"])
            else:
                store.record_dismiss(r["suggestion_id"])
        return store

    def acceptance(self, tenant_id: str) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT suggestion_id, SUM(accepted) AS acc, COUNT(*) AS total "
            "FROM feedback WHERE tenant_id=? GROUP BY suggestion_id", (tenant_id,)).fetchall()
        return [{"suggestion_id": r["suggestion_id"], "accepts": r["acc"], "total": r["total"],
                 "acceptance_rate": round(r["acc"] / r["total"], 3) if r["total"] else 0.0}
                for r in rows]

    def close(self) -> None:
        self.conn.close()
