import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import SuggestionEngine, ProgressRunner  # noqa: E402
from backend.mock_agent_api import DEMO_CONTEXT  # noqa: E402


def test_suggestions_generated_from_context():
    s = SuggestionEngine().suggest(DEMO_CONTEXT)
    ids = {x.id for x in s}
    assert "remind_payment" in ids
    assert "assign_owner" in ids


def test_every_suggestion_has_reason_and_oneclick_action():
    # 差別化の不変条件: 理由は必ず非空、アクションは必ず存在
    s = SuggestionEngine().suggest(DEMO_CONTEXT)
    assert s
    for x in s:
        assert x.reason and x.reason.strip()
        assert x.action and x.action.type and x.action.label


def test_suggestions_sorted_by_confidence():
    s = SuggestionEngine().suggest(DEMO_CONTEXT)
    confs = [x.confidence for x in s]
    assert confs == sorted(confs, reverse=True)


def test_empty_context_yields_no_suggestions():
    assert SuggestionEngine().suggest({}) == []


def test_urgency_raises_confidence():
    ctx = {"recent_actions": ["viewed_invoice"],
           "pending": {"unpaid_invoice": {"id": 1, "days_left": 1}}}
    s = SuggestionEngine().suggest(ctx)
    assert s[0].confidence >= 0.9   # 期限間近は確信度が上がる


def test_progress_runner_completes_all_steps():
    runner = ProgressRunner()
    task = runner.run_all("send_reminder")
    assert task.completed is True
    assert task.progress == 1.0
    assert all(st.status == "done" for st in task.steps)


def test_progress_advances_step_by_step():
    runner = ProgressRunner()
    task = runner.start("generate_report")
    assert task.progress == 0.0
    runner.advance(task.id)
    assert 0 < task.progress < 1.0
    assert not task.completed
