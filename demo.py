"""デモ(APIキー不要). `python demo.py`"""
from backend import SuggestionEngine, ProgressRunner, FeedbackStore
from backend.mock_agent_api import DEMO_CONTEXT


def main():
    feedback = FeedbackStore()
    engine = SuggestionEngine(feedback=feedback)
    runner = ProgressRunner()

    print("=== ① 先読み提案(理由つき) ===")
    suggestions = engine.suggest(DEMO_CONTEXT)
    for s in suggestions:
        print(f"\n[{s.confidence:.0%}] {s.title}")
        print(f"    なぜ提案?: {s.reason}")
        print(f"    ワンクリック: [{s.action.label}] -> {s.action.type}")

    print("\n=== ②③ ワンクリック実行 + 進捗の可視化 ===")
    top = suggestions[0]
    task = runner.start(top.action.type)
    print(f"実行: {top.title}")
    while not task.completed:
        runner.advance(task.id)
        bar = "".join("#" if st.status == "done" else "-" for st in task.steps)
        current = next((st.name for st in task.steps if st.status != "done"), "完了")
        print(f"  [{bar}] {task.progress:.0%}  次: {current}")
    print(f"  -> 完了 ({top.action.type})")

    print("\n=== フィードバック学習(却下を繰り返すと抑制) ===")
    print(f"  remind_payment を4回却下する...")
    for _ in range(4):
        feedback.record_dismiss("remind_payment")
    ids = {s.id for s in engine.suggest(DEMO_CONTEXT)}
    print(f"  再提案から remind_payment は{'消えた(抑制)' if 'remind_payment' not in ids else '残っている'}")
    print(f"  現在の提案: {sorted(ids)}")


if __name__ == "__main__":
    main()
