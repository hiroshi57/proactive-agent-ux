import React, { useState } from "react";
import ProgressView from "./ProgressView";

// 先読み提案カード. 差別化: 提案理由(reason)の可視化 + ワンクリック実行。
export default function ProactiveSuggestion({ suggestion, onExecute }) {
  const { title, reason, confidence, action, steps = [] } = suggestion;
  const [activeCount, setActiveCount] = useState(0);
  const [busy, setBusy] = useState(false);

  const runOneClick = async () => {
    setBusy(true);
    // 実バックエンド: await onExecute(action.type); ここでは進捗を段階表示
    for (let i = 1; i <= steps.length; i++) {
      // eslint-disable-next-line no-await-in-loop
      await new Promise((r) => setTimeout(r, 400));
      setActiveCount(i);
    }
    setBusy(false);
    if (onExecute) onExecute(action.type);
  };

  const finished = activeCount >= steps.length && steps.length > 0;

  return (
    <div className="card">
      <div className="head">
        <strong>{title}</strong>
        <span className="conf">確信度 {(confidence * 100).toFixed(0)}%</span>
      </div>
      {/* ★ 提案理由の可視化 */}
      <div className="reason">なぜ提案? {reason}</div>
      {/* ★ ワンクリック実行 */}
      <button onClick={runOneClick} disabled={busy || finished}>
        {finished ? "完了 ✓" : busy ? "実行中..." : `${action.label}（ワンクリック）`}
      </button>
      {activeCount > 0 && <ProgressView steps={steps} activeCount={activeCount} />}
    </div>
  );
}
