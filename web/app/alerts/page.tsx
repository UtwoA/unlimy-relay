const API = process.env.MASTER_PUBLIC_API ?? 'http://localhost:8080/api/v1';

async function fetchAlerts() {
  const res = await fetch(`${API}/alerts`, { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}

export default async function AlertsPage() {
  const alerts = await fetchAlerts();
  return (
    <div className="card">
      <h2>Alerts</h2>
      <table>
        <thead>
          <tr><th>Severity</th><th>Kind</th><th>Message</th><th>Time</th></tr>
        </thead>
        <tbody>
          {alerts.map((a: any) => (
            <tr key={a.id}>
              <td>{a.severity}</td>
              <td>{a.kind}</td>
              <td>{a.message}</td>
              <td>{a.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
