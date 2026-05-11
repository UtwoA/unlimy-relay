const API = process.env.MASTER_PUBLIC_API ?? 'http://localhost:8080/api/v1';

async function fetchSummary() {
  const res = await fetch(`${API}/metrics/summary`, { cache: 'no-store' });
  if (!res.ok) return { nodes_total: 0, nodes_online: 0 };
  return res.json();
}

export default async function Dashboard() {
  const summary = await fetchSummary();
  return (
    <div className="card">
      <h2>Dashboard</h2>
      <p>Total nodes: {summary.nodes_total}</p>
      <p>Online nodes: {summary.nodes_online}</p>
      <p>Realtime view is available via polling every page refresh for MVP.</p>
    </div>
  );
}
