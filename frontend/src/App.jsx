import React, { useEffect, useState } from "react";
import ProactiveSuggestion from "./components/ProactiveSuggestion";

const API = import.meta.env?.VITE_API || "http://localhost:8000";

// フロントとバックエンド(mock_agent_api)を接続する App.
// バックエンド未起動時は内蔵デモ提案にフォールバック。
const DEMO = [
  { id: "remind_payment", title: "支払いリマインドを送信", confidence: 0.9,
    reason: "請求書#1042 が未払いで支払期限まで残り2日です",
    action: { type: "send_reminder", label: "リマインド送信" },
    steps: ["宛先を解決", "文面を生成", "メール送信", "送信ログ記録"] },
];

export default function App() {
  const [items, setItems] = useState(DEMO);

  useEffect(() => {
    fetch(`${API}/suggest`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" })
      .then((r) => r.json())
      .then((d) => d.suggestions?.length && setItems(d.suggestions))
      .catch(() => {});
  }, []);

  return (
    <div className="wrap">
      <h1>先読み提案エージェント</h1>
      {items.map((s) => (
        <ProactiveSuggestion key={s.id} suggestion={s} />
      ))}
    </div>
  );
}
