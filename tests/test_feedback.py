import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import SuggestionEngine, FeedbackStore  # noqa: E402
from backend.mock_agent_api import DEMO_CONTEXT  # noqa: E402


def test_multiplier_default_is_one():
    fb = FeedbackStore()
    assert fb.confidence_multiplier("x") == 1.0


def test_accepts_raise_multiplier_dismisses_lower():
    fb = FeedbackStore()
    for _ in range(5):
        fb.record_accept("a")
    for _ in range(5):
        fb.record_dismiss("d")
    assert fb.confidence_multiplier("a") > 1.0
    assert fb.confidence_multiplier("d") < 1.0


def test_suppression_after_repeated_dismiss():
    fb = FeedbackStore(suppress_after=3, suppress_threshold=0.8)
    for _ in range(4):
        fb.record_dismiss("remind_payment")
    assert fb.is_suppressed("remind_payment") is True


def test_not_suppressed_before_min_samples():
    fb = FeedbackStore(suppress_after=3)
    fb.record_dismiss("x")
    assert fb.is_suppressed("x") is False


def test_engine_suppresses_dismissed_suggestion():
    fb = FeedbackStore(suppress_after=3, suppress_threshold=0.8)
    engine = SuggestionEngine(feedback=fb)
    ids_before = {s.id for s in engine.suggest(DEMO_CONTEXT)}
    assert "remind_payment" in ids_before
    for _ in range(4):
        fb.record_dismiss("remind_payment")
    ids_after = {s.id for s in engine.suggest(DEMO_CONTEXT)}
    assert "remind_payment" not in ids_after   # 学習で抑制


def test_engine_boosts_accepted_suggestion_confidence():
    fb = FeedbackStore()
    base = {s.id: s.confidence for s in SuggestionEngine().suggest(DEMO_CONTEXT)}
    for _ in range(5):
        fb.record_accept("assign_owner")
    boosted = {s.id: s.confidence for s in SuggestionEngine(feedback=fb).suggest(DEMO_CONTEXT)}
    assert boosted["assign_owner"] > base["assign_owner"]
