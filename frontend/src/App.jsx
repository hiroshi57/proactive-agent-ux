import React, { useEffect, useState } from "react";
import ProactiveSuggestion from "./components/ProactiveSuggestion";
import Analytics from "./screens/Analytics.jsx";
import { suggest, sendFeedback, reportUrl } from "./api.js";

const TENANT = "demo-tenant";
const DEMO = [
  { id: "remind_payment", title: "支払いリマインドを送信", confidence: 0.9,
    reason: "請求書#1042 が未払いで支払期限まで残り2日です",
    action: { type: "send_reminder", label: "リマインド送信" },
    steps: ["宛先を解決", "文面を生成", "メール送信", "送信ログ記録"] },
  { id: "assign_owner", title: "担当者をアサイン", confidence: 0.8,
    reason: "新規チケット#87 に担当者が未設定です",
    action: { type: "assign_owner", label: "自動アサイン" },
    steps: ["候補者をスコアリング", "最適担当を選定", "アサイン適用"] },
];
const DEMO_ACC = [
  { suggestion_id: "remind_payment", accepts: 1, total: 5, acceptance_rate: 0.2 },
  { suggestion_id: "assign_owner", accepts: 4, total: 5, acceptance_rate: 0.8 },
];

export default function App() {
  const [tab, setTab] = useState("suggest");
  const [items, setItems] = useState(DEMO);

  useEffect(() => {
    suggest(TENANT).then((d) => d.suggestions?.length && setItems(d.suggestions)).catch(() => {});
  }, []);

  const onFeedback = (id, accepted) => sendFeedback(TENANT, id, accepted).catch(() => {});

  return (
    <div className="wrap">
      <h1>先読み提案エージェント</h1>
      <nav>
        <button onClick={() => setTab("suggest")} disabled={tab === "suggest"}>先読み提案</button>
        <button onClick={() => setTab("analytics")} disabled={tab === "analytics"}>学習アナリティクス</button>
      </nav>
      {tab === "suggest"
        ? items.map((s) => (
            <ProactiveSuggestion key={s.id} suggestion={s} onExecute={() => onFeedback(s.id, true)} />))
        : <Analytics acceptance={DEMO_ACC} onOpenReport={() => window.open(reportUrl(), "_blank")} />}
    </div>
  );
}
