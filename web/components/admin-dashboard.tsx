'use client';

import { useEffect, useMemo, useState } from 'react';

type Kpi = {
  nodes_total: number;
  nodes_online: number;
  nodes_offline: number;
  nodes_draining: number;
  avg_rtt_ms: number;
  avg_handshake_rate: number;
  active_alerts_count: number;
};

type ProblemNode = {
  id: number;
  name: string;
  status: string;
  region: string;
  provider: string;
  is_online: boolean;
  is_enabled: boolean;
  rtt_ms: number;
  handshake_success_rate: number;
  score: number;
  age_hours: number;
};

type AlertItem = {
  id: number;
  severity: string;
  kind: string;
  message: string;
  created_at: string;
};

type AuditItem = {
  id: number;
  actor: string;
  action: string;
  object_type: string;
  object_id: string;
  created_at: string;
};

type TrendPoint = {
  hour: string;
  online_ratio: number;
  avg_rtt_ms: number;
  handshake_ok_ratio: number;
};

type OverviewPayload = {
  kpi: Kpi;
  problem_nodes: ProblemNode[];
  recent_alerts: AlertItem[];
  recent_audit: AuditItem[];
  trends_24h: TrendPoint[];
};

function points(values: number[], min: number, max: number): string {
  if (values.length === 0) return '';
  const width = 260;
  const height = 64;
  const range = max - min || 1;
  return values
    .map((v, i) => {
      const x = (i / Math.max(values.length - 1, 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');
}

function TrendSpark({ title, values, suffix = '' }: { title: string; values: number[]; suffix?: string }) {
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);
  const last = values.length ? values[values.length - 1] : 0;

  return (
    <div className="trend-card">
      <div className="trend-head">
        <span>{title}</span>
        <b>{last.toFixed(2)}{suffix}</b>
      </div>
      <svg viewBox="0 0 260 64" className="sparkline" role="img" aria-label={title}>
        <polyline points={points(values, min, max)} fill="none" stroke="currentColor" strokeWidth="2" />
      </svg>
    </div>
  );
}

export default function AdminDashboard() {
  const [data, setData] = useState<OverviewPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState('');
  const [banner, setBanner] = useState<{ type: 'ok' | 'err'; msg: string } | null>(null);

  async function load() {
    const res = await fetch('/api/admin/overview', { cache: 'no-store' });
    if (!res.ok) {
      const t = await res.text();
      setBanner({ type: 'err', msg: `overview failed: ${t}` });
      return;
    }
    const payload = await res.json();
    setData(payload);
  }

  useEffect(() => {
    let mounted = true;
    async function boot() {
      try {
        await load();
      } finally {
        if (mounted) setLoading(false);
      }
    }
    void boot();
    const timer = setInterval(() => {
      void load();
    }, 15_000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  async function runJob(job: 'health' | 'rotation') {
    setBusy(`job:${job}`);
    setBanner(null);
    try {
      const res = await fetch(`/api/admin/jobs/${job}`, { method: 'POST' });
      if (!res.ok) {
        const t = await res.text();
        setBanner({ type: 'err', msg: `${job} job failed: ${t}` });
        return;
      }
      setBanner({ type: 'ok', msg: `${job} job queued` });
      await load();
    } finally {
      setBusy('');
    }
  }

  async function runNodeAction(id: number, action: 'check' | 'rotate' | 'disable' | 'enable' | 'restart') {
    setBusy(`node:${id}:${action}`);
    setBanner(null);
    try {
      const res = await fetch(`/api/admin/nodes/${id}/${action}`, { method: 'POST' });
      if (!res.ok) {
        const t = await res.text();
        setBanner({ type: 'err', msg: `${action} failed for node ${id}: ${t}` });
        return;
      }
      setBanner({ type: 'ok', msg: `${action} done for node ${id}` });
      await load();
    } finally {
      setBusy('');
    }
  }

  const trends = useMemo(() => {
    if (!data) return { online: [], rtt: [], hs: [] };
    return {
      online: data.trends_24h.map((x) => x.online_ratio * 100),
      rtt: data.trends_24h.map((x) => x.avg_rtt_ms),
      hs: data.trends_24h.map((x) => x.handshake_ok_ratio * 100),
    };
  }, [data]);

  if (loading) {
    return <div className="card"><p>Loading admin overview...</p></div>;
  }

  if (!data) {
    return <div className="card"><p>Failed to load overview.</p></div>;
  }

  return (
    <>
      <div className="card">
        <div className="config-card-title">
          <h2>Operations Overview</h2>
          <div style={{ display: 'flex', gap: 8 }}>
            <button disabled={busy === 'job:health'} onClick={() => runJob('health')}>Run Health Checks</button>
            <button disabled={busy === 'job:rotation'} onClick={() => runJob('rotation')}>Run Rotation Job</button>
            <button onClick={() => void load()}>Refresh</button>
          </div>
        </div>
        {banner ? <p className={banner.type === 'ok' ? 'badge-on' : 'badge-off'}>{banner.msg}</p> : null}
      </div>

      <div className="kpi-grid">
        <div className="card kpi"><span>Total Nodes</span><b>{data.kpi.nodes_total}</b></div>
        <div className="card kpi"><span>Online</span><b>{data.kpi.nodes_online}</b></div>
        <div className="card kpi"><span>Offline</span><b>{data.kpi.nodes_offline}</b></div>
        <div className="card kpi"><span>Draining</span><b>{data.kpi.nodes_draining}</b></div>
        <div className="card kpi"><span>Avg RTT</span><b>{data.kpi.avg_rtt_ms.toFixed(1)} ms</b></div>
        <div className="card kpi"><span>Handshake</span><b>{(data.kpi.avg_handshake_rate * 100).toFixed(1)}%</b></div>
        <div className="card kpi"><span>Alerts (24h)</span><b>{data.kpi.active_alerts_count}</b></div>
      </div>

      <div className="trend-grid">
        <TrendSpark title="Online Ratio" values={trends.online} suffix="%" />
        <TrendSpark title="Avg RTT" values={trends.rtt} suffix="ms" />
        <TrendSpark title="Handshake OK" values={trends.hs} suffix="%" />
      </div>

      <div className="card">
        <h3>Problem Nodes</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Name</th><th>Status</th><th>Region</th><th>Provider</th><th>RTT</th><th>Handshake</th><th>Score</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.problem_nodes.map((n) => (
              <tr key={n.id}>
                <td>{n.id}</td>
                <td>{n.name}</td>
                <td>{n.status}</td>
                <td>{n.region}</td>
                <td>{n.provider}</td>
                <td>{n.rtt_ms.toFixed(1)}</td>
                <td>{(n.handshake_success_rate * 100).toFixed(1)}%</td>
                <td>{n.score.toFixed(1)}</td>
                <td>
                  <button onClick={() => runNodeAction(n.id, 'check')} disabled={busy === `node:${n.id}:check`}>check</button>{' '}
                  <button onClick={() => runNodeAction(n.id, 'rotate')} disabled={busy === `node:${n.id}:rotate`}>rotate</button>{' '}
                  <button onClick={() => runNodeAction(n.id, 'restart')} disabled={busy === `node:${n.id}:restart`}>restart</button>{' '}
                  <button onClick={() => runNodeAction(n.id, n.is_enabled ? 'disable' : 'enable')} disabled={busy === `node:${n.id}:${n.is_enabled ? 'disable' : 'enable'}`}>
                    {n.is_enabled ? 'disable' : 'enable'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="split-grid">
        <div className="card">
          <h3>Recent Alerts</h3>
          <table>
            <thead><tr><th>Severity</th><th>Kind</th><th>Message</th><th>Time</th></tr></thead>
            <tbody>
              {data.recent_alerts.map((a) => (
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

        <div className="card">
          <h3>Recent Audit</h3>
          <table>
            <thead><tr><th>Actor</th><th>Action</th><th>Object</th><th>Time</th></tr></thead>
            <tbody>
              {data.recent_audit.map((a) => (
                <tr key={a.id}>
                  <td>{a.actor}</td>
                  <td>{a.action}</td>
                  <td>{a.object_type}:{a.object_id}</td>
                  <td>{a.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
