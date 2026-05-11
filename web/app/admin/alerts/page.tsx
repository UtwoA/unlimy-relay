import { requireAdminJson } from '../../../lib/admin';

export default async function AdminAlertsPage() {
  const alerts = await requireAdminJson('/alerts');

  return (
    <div className="card">
      <h2>Алерты</h2>
      <table>
        <thead>
          <tr><th>Severity</th><th>Kind</th><th>Сообщение</th><th>Время</th></tr>
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

