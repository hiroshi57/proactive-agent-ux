import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import SuggestionBandit  # noqa: E402


def test_posterior_mean_updates():
    b = SuggestionBandit()
    for _ in range(8):
        b.update("good", True)
    for _ in range(8):
        b.update("bad", False)
    assert b.posterior_mean("good") > 0.7
    assert b.posterior_mean("bad") < 0.3


def test_rank_by_mean_orders_by_acceptance():
    b = SuggestionBandit()
    for _ in range(10):
        b.update("high", True)
    for _ in range(5):
        b.update("mid", True)
        b.update("mid", False)
    for _ in range(10):
        b.update("low", False)
    ranked = b.rank_by_mean(["low", "mid", "high"])
    assert ranked == ["high", "mid", "low"]


def test_thompson_score_in_range():
    b = SuggestionBandit()
    b.update("x", True)
    s = b.score("x")
    assert 0.0 <= s <= 1.0


def test_unknown_arm_is_neutral_prior():
    b = SuggestionBandit()
    assert abs(b.posterior_mean("never_seen") - 0.5) < 1e-9   # Beta(1,1)=0.5


def test_thompson_favors_better_arm_on_average():
    b = SuggestionBandit(seed=1)
    for _ in range(20):
        b.update("great", True)
    for _ in range(20):
        b.update("poor", False)
    wins = 0
    for _ in range(200):
        if b.score("great") > b.score("poor"):
            wins += 1
    assert wins > 180        # 良いarmがほぼ常に勝つ
