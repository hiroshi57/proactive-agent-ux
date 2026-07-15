const BASE = import.meta.env?.VITE_API || "http://localhost:8000";
const h = (t) => ({ "Content-Type": "application/json", "X-Tenant-Id": t });

export async function suggest(t, context = {}) {
  return (await fetch(`${BASE}/v1/suggest`, { method: "POST", headers: h(t), body: JSON.stringify({ context }) })).json();
}
export async function sendFeedback(t, suggestionId, accepted) {
  return (await fetch(`${BASE}/v1/feedback`, { method: "POST", headers: h(t), body: JSON.stringify({ suggestion_id: suggestionId, accepted }) })).json();
}
export function reportUrl() { return `${BASE}/v1/report`; }
