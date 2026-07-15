"""プロアクティブUX サービスAPI(FastAPI). 先読み提案 + 学習フィードバック(永続). テナント分離.
`uvicorn service.api:app --reload`
"""
from backend import SuggestionEngine, ProgressRunner
from backend.mock_agent_api import DEMO_CONTEXT
from .db import ServiceDB
from .report_html import build_html_report

DB = ServiceDB(":memory:")
RUNNER = ProgressRunner()


def create_app():  # pragma: no cover
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel

    app = FastAPI(title="Proactive Agent UX", version="1.0.0")

    def tenant(x_tenant_id: str = Header(...)) -> str:
        if not x_tenant_id:
            raise HTTPException(401, "tenant required")
        return x_tenant_id

    class Ctx(BaseModel):
        context: dict | None = None

    class Exec(BaseModel):
        action_type: str

    class Feedback(BaseModel):
        suggestion_id: str
        accepted: bool

    @app.post("/v1/suggest")
    def suggest(body: Ctx, t: str = Depends(tenant)):
        # テナント別の学習(採用/却下履歴)を反映
        engine = SuggestionEngine(feedback=DB.build_store(t))
        ctx = body.context or DEMO_CONTEXT
        return {"suggestions": [s.as_dict() for s in engine.suggest(ctx)]}

    @app.post("/v1/execute")
    def execute(body: Exec, t: str = Depends(tenant)):
        return RUNNER.run_all(body.action_type).as_dict()

    @app.post("/v1/feedback")
    def feedback(body: Feedback, t: str = Depends(tenant)):
        DB.record(t, body.suggestion_id, body.accepted)
        store = DB.build_store(t)
        return {"suggestion_id": body.suggestion_id,
                "suppressed": store.is_suppressed(body.suggestion_id)}

    @app.get("/v1/report", response_class=HTMLResponse)
    def report(t: str = Depends(tenant)):
        return build_html_report(DB.acceptance(t))

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


try:  # pragma: no cover
    app = create_app()
except Exception:
    app = None
