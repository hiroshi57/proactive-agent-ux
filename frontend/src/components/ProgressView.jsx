import React from "react";

// 進捗の可視化: 実行ステップの状態をバー + チェックで表示。
export default function ProgressView({ steps, activeCount }) {
  const pct = Math.round((activeCount / steps.length) * 100);
  return (
    <div>
      <div className="bar">
        <div style={{ width: `${pct}%` }} />
      </div>
      {steps.map((s, i) => (
        <div className="step" key={i}>
          <span className={"dot" + (i < activeCount ? " done" : "")} />
          {s}
        </div>
      ))}
    </div>
  );
}
