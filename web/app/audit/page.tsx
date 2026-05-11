import { apiGet } from '../../lib/api';

async function fetchAudit() {
  const res = await apiGet('/audit');
  if (!res.ok) return null;
  return res.json();
}

export default async function AuditPage() {
  const logs = await fetchAudit();
  if (!logs) {
    return (
      <div className="card">
        <h2>Access and Audit</h2>
        <p>Admin authentication required.</p>
        <a href="/login">Go to login</a>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Access and Audit</h2>
      <table>
        <thead>
          <tr><th>Actor</th><th>Action</th><th>Object</th><th>Time</th></tr>
        </thead>
        <tbody>
          {logs.map((l: any) => (
            <tr key={l.id}>
              <td>{l.actor}</td>
              <td>{l.action}</td>
              <td>{l.object_type}:{l.object_id}</td>
              <td>{l.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
