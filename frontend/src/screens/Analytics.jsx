import React from "react";

// 学習アナリティクス: 提案採用率(低採用は自動抑制)。
export default function Analytics({ acceptance, onOpenReport }) {
  return (
    <div className="card">
      <h2>学習アナリティクス</h2>
      <p>提案ごとの採用率。繰り返し却下された提案は自動的に抑制されます。</p>
      <table>
        <thead><tr><th>提案ID</th><th>採用/提示</th><th>採用率</th></tr></thead>
        <tbody>{(acceptance || []).map((a) => (
          <tr key={a.suggestion_id}>
            <td>{a.suggestion_id}</td><td>{a.accepts}/{a.total}</td>
            <td>{Math.round(a.acceptance_rate * 100)}%</td></tr>))}
        </tbody>
      </table>
      {onOpenReport && <button className="primary" onClick={onOpenReport}>HTMLレポート</button>}
    </div>
  );
}
