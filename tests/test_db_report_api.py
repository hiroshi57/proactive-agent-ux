import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from service.db import ServiceDB  # noqa: E402
from service.report_html import build_html_report  # noqa: E402


def test_feedback_persist_and_store_rebuild():
    db = ServiceDB(":memory:")
    for _ in range(4):
        db.record("t-a", "remind_payment", False)
    store = db.build_store("t-a")
    assert store.is_suppressed("remind_payment") is True   # 学習が復元される


def test_tenant_isolation():
    db = ServiceDB(":memory:")
    for _ in range(4):
        db.record("t-a", "remind_payment", False)
    # tenant-b には履歴なし -> 抑制されない
    assert db.build_store("t-b").is_suppressed("remind_payment") is False
    assert db.acceptance("t-b") == []


def test_acceptance_aggregation():
    db = ServiceDB(":memory:")
    db.record("t-a", "assign_owner", True)
    db.record("t-a", "assign_owner", True)
    db.record("t-a", "assign_owner", False)
    acc = {a["suggestion_id"]: a for a in db.acceptance("t-a")}
    assert acc["assign_owner"]["accepts"] == 2
    assert acc["assign_owner"]["total"] == 3
    assert acc["assign_owner"]["acceptance_rate"] == round(2 / 3, 3)


def test_html_report():
    html = build_html_report([{"suggestion_id": "assign_owner", "accepts": 2,
                               "total": 3, "acceptance_rate": 0.667}])
    assert "学習レポート" in html and "assign_owner" in html


def test_api_e2e_and_tenant_learning():
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from service.api import create_app
    c = TestClient(create_app())
    ha, hb = {"X-Tenant-Id": "t-a"}, {"X-Tenant-Id": "t-b"}
    # 初期は remind_payment が提案される
    ids0 = {s["id"] for s in c.post("/v1/suggest", json={}, headers=ha).json()["suggestions"]}
    assert "remind_payment" in ids0
    # 4回却下 -> 学習で抑制
    for _ in range(4):
        c.post("/v1/feedback", json={"suggestion_id": "remind_payment", "accepted": False}, headers=ha)
    ids1 = {s["id"] for s in c.post("/v1/suggest", json={}, headers=ha).json()["suggestions"]}
    assert "remind_payment" not in ids1
    # tenant-b は影響を受けない(分離)
    ids_b = {s["id"] for s in c.post("/v1/suggest", json={}, headers=hb).json()["suggestions"]}
    assert "remind_payment" in ids_b
    assert c.get("/v1/report", headers=ha).status_code == 200
