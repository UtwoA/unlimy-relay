import { apiGet } from '../../lib/api';

async function fetchAlerts() {
  const res = await apiGet('/alerts');
  if (!res.ok) return null;
  return res.json();
}

export default async function AlertsPage() {
  const alerts = await fetchAlerts();
  if (!alerts) {
    return (
      <div className="card">
        <h2>Alerts</h2>
        <p>Authentication required.</p>
        <a href="/login">Go to login</a>
      </div>
    );
  }

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
