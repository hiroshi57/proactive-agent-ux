"""簡易モック バックエンド API(FastAPI). 先読み提案 / ワンクリック実行 / 進捗取得."""
from __future__ import annotations

from .progress import ProgressRunner
from .suggester import SuggestionEngine

ENGINE = SuggestionEngine()
RUNNER = ProgressRunner()

# デモ用の既定文脈(フロントが未指定時に使う)
DEMO_CONTEXT = {
    "current_view": "dashboard",
    "time_of_day": "morning",
    "recent_actions": ["viewed_invoice", "created_ticket"],
    "pending": {
        "unpaid_invoice": {"id": 1042, "days_left": 2},
        "unassigned_ticket": {"id": 87},
        "daily_report_due": True,
        "anomaly": {"metric": "CVR", "delta": "-32%"},
    },
}


def create_app():  # pragma: no cover
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(title="proactive-agent-ux mock", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    class Ctx(BaseModel):
        context: dict | None = None

    class Exec(BaseModel):
        action_type: str

    @app.post("/suggest")
    def suggest(body: Ctx):
        ctx = body.context or DEMO_CONTEXT
        return {"suggestions": [s.as_dict() for s in ENGINE.suggest(ctx)]}

    @app.post("/execute")
    def execute(body: Exec):
        # ワンクリック実行: 全ステップ完了まで進める
        return RUNNER.run_all(body.action_type).as_dict()

    @app.get("/progress/{task_id}")
    def progress(task_id: str):
        return RUNNER.get(task_id).as_dict()

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


try:  # pragma: no cover
    app = create_app()
except Exception:
    app = None
