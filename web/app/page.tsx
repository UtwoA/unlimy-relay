import { apiGet } from '../lib/api';

async function fetchSummary() {
  const res = await apiGet('/metrics/summary');
  if (!res.ok) return null;
  return res.json();
}

export default async function Dashboard() {
  const summary = await fetchSummary();
  if (!summary) {
    return (
      <div className="card">
        <h2>Dashboard</h2>
        <p>Please sign in to view relay metrics.</p>
        <a href="/login">Go to login</a>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Dashboard</h2>
      <p>Total nodes: {summary.nodes_total}</p>
      <p>Online nodes: {summary.nodes_online}</p>
      <p>Realtime view is available via page refresh in this version.</p>
    </div>
  );
}
