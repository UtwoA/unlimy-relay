import { requireAdminJson } from '../../../lib/admin';

export default async function AdminAuditPage() {
  const logs = await requireAdminJson('/audit');

  return (
    <div className="card">
      <h2>Журнал действий</h2>
      <table>
        <thead>
          <tr><th>Кто</th><th>Действие</th><th>Объект</th><th>Время</th></tr>
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

