import { requireAdminJson } from '../../lib/admin';

export default async function AdminDashboardPage() {
  const summary = await requireAdminJson('/metrics/summary');

  return (
    <div className="card">
      <h2>Dashboard</h2>
      <p>Total nodes: {summary.nodes_total}</p>
      <p>Online nodes: {summary.nodes_online}</p>
      <p>Operational controls are available in the Nodes section.</p>
    </div>
  );
}
