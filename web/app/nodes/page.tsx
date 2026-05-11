import { apiGet } from '../../lib/api';

async function fetchNodes() {
  const res = await apiGet('/nodes');
  if (!res.ok) return null;
  return res.json();
}

export default async function NodesPage() {
  const nodes = await fetchNodes();
  if (!nodes) {
    return (
      <div className="card">
        <h2>Nodes</h2>
        <p>Authentication required.</p>
        <a href="/login">Go to login</a>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Nodes</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Name</th><th>Region</th><th>Provider</th><th>Status</th><th>Online</th><th>RTT</th>
          </tr>
        </thead>
        <tbody>
          {nodes.map((n: any) => (
            <tr key={n.id}>
              <td>{n.id}</td>
              <td>{n.name}</td>
              <td>{n.region}</td>
              <td>{n.provider}</td>
              <td>{n.status}</td>
              <td className={n.is_online ? 'badge-on' : 'badge-off'}>{n.is_online ? 'online' : 'offline'}</td>
              <td>{n.rtt_ms}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
