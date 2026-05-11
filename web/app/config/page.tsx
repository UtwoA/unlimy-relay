'use client';

import { useEffect, useMemo, useState } from 'react';

type ProxyPayload = {
  node: string;
  tg_link: string;
  https_link: string;
  qr_base64: string;
};

type PublicStatus = {
  availability_pct: number;
  active_nodes: number;
  avg_latency_ms: number;
  region: string;
  provider: string;
  protocol: string;
  handshake: string;
  reachability: string;
  rotation_seconds: number;
};

function fmtCountdown(seconds: number): string {
  const mm = Math.floor(seconds / 60).toString().padStart(2, '0');
  const ss = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${mm}:${ss}`;
}

export default function ConfigPage() {
  const [data, setData] = useState<ProxyPayload | null>(null);
  const [status, setStatus] = useState<PublicStatus | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [countdown, setCountdown] = useState(1800);

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [proxyRes, statusRes] = await Promise.all([
        fetch('/api/public/proxy', { cache: 'no-store' }),
        fetch('/api/public/status', { cache: 'no-store' }),
      ]);

      if (!proxyRes.ok) {
        const body = await proxyRes.json().catch(() => ({}));
        setError(body.detail || 'Прокси временно недоступен, попробуйте позже.');
        setData(null);
      } else {
        const payload = await proxyRes.json();
        setData(payload);
      }

      if (statusRes.ok) {
        const st = await statusRes.json();
        setStatus(st);
        setCountdown(st.rotation_seconds || 1800);
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const canConnect = useMemo(() => Boolean(data?.tg_link), [data]);

  return (
    <>
      <div className="card">
        <h1>Unlimy Relay</h1>
        <p className="muted">Быстрое подключение к Telegram через резервный прокси</p>
      </div>

      <div className="card stats-grid">
        <div><b>Доступность:</b> {status ? `${status.availability_pct}%` : '-'}</div>
        <div><b>Активных нод:</b> {status?.active_nodes ?? '-'}</div>
        <div><b>Средняя задержка:</b> {status ? `${status.avg_latency_ms}мс` : '-'}</div>
        <div><b>Регион:</b> {status?.region ?? '-'}</div>
        <div><b>Провайдер:</b> {status?.provider ?? '-'}</div>
        <div><b>Протокол:</b> {status?.protocol ?? 'EE/FakeTLS'}</div>
      </div>

      <div className="config-hero">
        <div className="card">
          <div className="config-card-title">
            <h2>Конфиг Proxy</h2>
            <button onClick={load} disabled={loading}>{loading ? 'Обновляем...' : 'Обновить'}</button>
          </div>

          {error ? <p className="badge-off">{error}</p> : null}

          <p><b>Следующее автообновление через:</b> {fmtCountdown(countdown)}</p>

          {data ? (
            <div className="config-meta">
              <p><b>Нода:</b> {data.node}</p>
              <p><b>Handshake:</b> <span className={status?.handshake === 'ok' ? 'badge-on' : 'badge-off'}>{status?.handshake === 'ok' ? 'OK' : 'нестабильно'}</span></p>
              <p><b>Доступность Telegram:</b> <span className={status?.reachability === 'healthy' ? 'badge-on' : 'badge-off'}>{status?.reachability === 'healthy' ? 'доступно' : 'нестабильно'}</span></p>
              <p><b>TG-ссылка:</b> <a href={data.tg_link}>{data.tg_link}</a></p>
              <p><b>HTTPS-ссылка:</b> <a href={data.https_link}>{data.https_link}</a></p>
              <p>
                <a className="cta-link" href={data.tg_link}>Подключить в Telegram</a>
              </p>
            </div>
          ) : (
            <p className="muted">Ожидаем доступный endpoint...</p>
          )}
        </div>

        <div className="card qr-wrap">
          {data ? (
            <img alt="QR proxy" src={`data:image/png;base64,${data.qr_base64}`} />
          ) : (
            <p style={{ color: 'var(--muted)' }}>QR появится после загрузки</p>
          )}
        </div>
      </div>

      <div className="card">
        <h3>3 шага подключения</h3>
        <div className="steps">
          <div className="step"><b>1</b><span>Нажмите «Подключить в Telegram» или сканируйте QR-код.</span></div>
          <div className="step"><b>2</b><span>Подтвердите добавление прокси в клиенте Telegram.</span></div>
          <div className="step"><b>3</b><span>Если подключение не прошло, нажмите «Обновить» и повторите.</span></div>
        </div>
      </div>

      <div className="card">
        <h3>Что это?</h3>
            <p style={{ color: 'var(--muted)' }}>
          Это fallback-канал доступа к Telegram. Он помогает подключиться в случаях, когда обычный маршрут нестабилен.
        </p>
      </div>

      <div className="card">
        <h3>Совместимость клиентов</h3>
        <p className="muted">Поддерживаются:</p>
        <ul>
          <li>Telegram Android</li>
          <li>Telegram iOS</li>
          <li>Telegram Desktop</li>
          <li>Telegram macOS</li>
        </ul>
      </div>

      <div className="card faq">
        <h3>Мини-FAQ</h3>
        <p><b>Это безопасно?</b> Ссылка содержит только параметры подключения прокси.</p>
        <p><b>Почему иногда не работает?</b> Ноды ротируются и часть может временно быть недоступной.</p>
        <p><b>Нужен VPN?</b> Нет, это fallback-канал для Telegram, когда обычный маршрут недоступен.</p>
      </div>
    </>
  );
}

