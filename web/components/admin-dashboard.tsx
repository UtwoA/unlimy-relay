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

function TrendSpark({
  title,
  values,
  suffix = '',
  className = '',
}: {
  title: string;
  values: number[];
  suffix?: string;
  className?: string;
}) {
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);
  const last = values.length ? values[values.length - 1] : 0;

  return (
    <div className={`trend-card ${className}`.trim()}>
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

  const actionTitle: Record<string, string> = {
    check: 'проверка',
    rotate: 'ротация',
    restart: 'рестарт',
    disable: 'отключение',
    enable: 'включение',
  };
  const jobTitle: Record<string, string> = {
    health: 'health-check',
    rotation: 'rotation',
  };

  async function load() {
    const res = await fetch('/api/admin/overview', { cache: 'no-store' });
    if (!res.ok) {
      const t = await res.text();
      setBanner({ type: 'err', msg: `Ошибка загрузки обзора: ${t}` });
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
        setBanner({ type: 'err', msg: `Не удалось запустить задачу ${jobTitle[job]}: ${t}` });
        return;
      }
      setBanner({ type: 'ok', msg: `Задача ${jobTitle[job]} отправлена` });
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
        setBanner({ type: 'err', msg: `Действие "${actionTitle[action]}" для ноды ${id} не выполнено: ${t}` });
        return;
      }
      setBanner({ type: 'ok', msg: `Действие "${actionTitle[action]}" выполнено для ноды ${id}` });
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
    return <div className="card"><p>Загружаем обзор админ-панели...</p></div>;
  }

  if (!data) {
    return <div className="card"><p>Не удалось загрузить данные дашборда.</p></div>;
  }

  return (
    <>
      <div className="card">
        <div className="config-card-title">
          <h2>Операционный дашборд</h2>
          <div style={{ display: 'flex', gap: 8 }}>
            <button disabled={busy === 'job:health'} onClick={() => runJob('health')}>Запустить health-check</button>
            <button disabled={busy === 'job:rotation'} onClick={() => runJob('rotation')}>Запустить rotation job</button>
            <button onClick={() => void load()}>Обновить</button>
          </div>
        </div>
        <p className="muted">Автообновление каждые 15 секунд</p>
        {banner ? <p className={banner.type === 'ok' ? 'badge-on' : 'badge-off'}>{banner.msg}</p> : null}
      </div>

      <div className="kpi-grid">
        <div className="card kpi"><span>Всего нод</span><b>{data.kpi.nodes_total}</b></div>
        <div className="card kpi"><span>Онлайн</span><b>{data.kpi.nodes_online}</b></div>
        <div className="card kpi"><span>Офлайн</span><b>{data.kpi.nodes_offline}</b></div>
        <div className="card kpi"><span>На выводе</span><b>{data.kpi.nodes_draining}</b></div>
        <div className="card kpi"><span>Средний RTT</span><b>{data.kpi.avg_rtt_ms.toFixed(1)} мс</b></div>
        <div className="card kpi"><span>Успех Handshake</span><b>{(data.kpi.avg_handshake_rate * 100).toFixed(1)}%</b></div>
        <div className="card kpi"><span>Алерты (24ч)</span><b>{data.kpi.active_alerts_count}</b></div>
      </div>

      <div className="trend-grid">
        <TrendSpark className="online" title="Доля онлайн" values={trends.online} suffix="%" />
        <TrendSpark className="rtt" title="Средний RTT" values={trends.rtt} suffix="мс" />
        <TrendSpark className="hs" title="Успех рукопожатия" values={trends.hs} suffix="%" />
      </div>

      <div className="card">
        <h3>Проблемные ноды</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Имя</th><th>Статус</th><th>Регион</th><th>Провайдер</th><th>RTT</th><th>Handshake</th><th>Оценка</th><th>Действия</th>
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
                  <button onClick={() => runNodeAction(n.id, 'check')} disabled={busy === `node:${n.id}:check`}>проверка</button>{' '}
                  <button onClick={() => runNodeAction(n.id, 'rotate')} disabled={busy === `node:${n.id}:rotate`}>ротация</button>{' '}
                  <button onClick={() => runNodeAction(n.id, 'restart')} disabled={busy === `node:${n.id}:restart`}>рестарт</button>{' '}
                  <button onClick={() => runNodeAction(n.id, n.is_enabled ? 'disable' : 'enable')} disabled={busy === `node:${n.id}:${n.is_enabled ? 'disable' : 'enable'}`}>
                    {n.is_enabled ? 'выкл' : 'вкл'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="split-grid">
        <div className="card">
          <h3>Последние алерты</h3>
          <table>
            <thead><tr><th>Серьезность</th><th>Тип</th><th>Сообщение</th><th>Время</th></tr></thead>
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
          <h3>Последние действия</h3>
          <table>
            <thead><tr><th>Кто</th><th>Действие</th><th>Объект</th><th>Время</th></tr></thead>
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

