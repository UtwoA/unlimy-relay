'use client';

import { useEffect, useState } from 'react';

type ProxyPayload = {
  node: string;
  tg_link: string;
  https_link: string;
  qr_base64: string;
};

export default function ConfigPage() {
  const [data, setData] = useState<ProxyPayload | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/public/proxy', { cache: 'no-store' });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(body.detail || 'Прокси временно недоступен, попробуйте позже.');
        setData(null);
        return;
      }
      const payload = await res.json();
      setData(payload);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <>
      <div className="card">
        <h1>Unlimy Relay</h1>
        <p style={{ color: 'var(--muted)' }}>Открытая страница подключения Telegram Proxy. Админ-доступ расположен на скрытом маршруте.</p>
      </div>

      <div className="config-hero">
        <div className="card">
          <div className="config-card-title">
            <h2>Конфиг Proxy</h2>
            <button onClick={load} disabled={loading}>{loading ? 'Обновляем...' : 'Обновить'}</button>
          </div>

          {error ? <p className="badge-off">{error}</p> : null}

          {data ? (
            <div className="config-meta">
              <p><b>Нода:</b> {data.node}</p>
              <p><b>TG-ссылка:</b> <a href={data.tg_link}>{data.tg_link}</a></p>
              <p><b>HTTPS-ссылка:</b> <a href={data.https_link}>{data.https_link}</a></p>
            </div>
          ) : (
            <p style={{ color: 'var(--muted)' }}>Ожидаем доступный endpoint...</p>
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
          <div className="step"><b>1</b><span>Нажмите на TG-ссылку или сканируйте QR-код в Telegram.</span></div>
          <div className="step"><b>2</b><span>Подтвердите добавление прокси в клиенте.</span></div>
          <div className="step"><b>3</b><span>Если не подключается, нажмите «Обновить» и попробуйте снова.</span></div>
        </div>
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
