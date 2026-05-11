const API = process.env.MASTER_PUBLIC_API ?? 'http://localhost:8080/api/v1';

async function fetchAudit() {
  const res = await fetch(`${API}/audit`, { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}

export default async function AuditPage() {
  const logs = await fetchAudit();
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
