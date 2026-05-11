'use client';

import { useRouter } from 'next/navigation';
import { useMemo, useState } from 'react';

type NodeRow = {
  id: number;
  name: string;
  region: string;
  provider: string;
  status: string;
  is_online: boolean;
  is_enabled: boolean;
  rtt_ms: number;
};

const actions = ['check', 'rotate', 'restart'] as const;

export default function NodesTable({ initialNodes }: { initialNodes: NodeRow[] }) {
  const [nodes, setNodes] = useState(initialNodes);
  const [busy, setBusy] = useState<string>('');
  const [banner, setBanner] = useState<{ type: 'ok' | 'err'; msg: string } | null>(null);
  const router = useRouter();

  const sorted = useMemo(() => [...nodes].sort((a, b) => a.id - b.id), [nodes]);

  async function runAction(id: number, action: string) {
    const key = `${id}:${action}`;
    setBusy(key);
    setBanner(null);
    try {
      const res = await fetch(`/api/admin/nodes/${id}/${action}`, { method: 'POST' });
      if (!res.ok) {
        const t = await res.text();
        setBanner({ type: 'err', msg: `${action} failed: ${t}` });
        if (res.status === 401 || res.status === 403) router.push('/admin/login');
        return;
      }
      setBanner({ type: 'ok', msg: `${action} done for node ${id}` });
      await refreshNodes();
      router.refresh();
    } finally {
      setBusy('');
    }
  }

  async function toggleEnabled(row: NodeRow) {
    const action = row.is_enabled ? 'disable' : 'enable';
    await runAction(row.id, action);
  }

  async function refreshNodes() {
    const res = await fetch('/api/admin/nodes', { cache: 'no-store' });
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) router.push('/admin/login');
      return;
    }
    const payload = await res.json();
    setNodes(payload);
  }

  return (
    <div className="card">
      <h2>Nodes</h2>
      {banner ? <p className={banner.type === 'ok' ? 'badge-on' : 'badge-off'}>{banner.msg}</p> : null}
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Name</th><th>Region</th><th>Provider</th><th>Status</th><th>Online</th><th>RTT</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((n) => (
            <tr key={n.id}>
              <td>{n.id}</td>
              <td>{n.name}</td>
              <td>{n.region}</td>
              <td>{n.provider}</td>
              <td>{n.status}</td>
              <td className={n.is_online ? 'badge-on' : 'badge-off'}>{n.is_online ? 'online' : 'offline'}</td>
              <td>{n.rtt_ms}</td>
              <td>
                {actions.map((action) => {
                  const key = `${n.id}:${action}`;
                  return (
                    <button key={action} disabled={busy === key} onClick={() => runAction(n.id, action)} style={{ marginRight: 6 }}>
                      {busy === key ? '...' : action}
                    </button>
                  );
                })}
                <button disabled={busy === `${n.id}:toggle`} onClick={() => toggleEnabled(n)}>
                  {n.is_enabled ? 'disable' : 'enable'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
