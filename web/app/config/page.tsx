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
        <h2>Конфиг Telegram Proxy</h2>
        <p>Получите рабочий fallback-прокси в один клик.</p>
        <button onClick={load} disabled={loading}>{loading ? 'Обновляем...' : 'Обновить прокси'}</button>
        {error ? <p className="badge-off">{error}</p> : null}
        {data ? (
          <div style={{ marginTop: 12 }}>
            <p><b>Нода:</b> {data.node}</p>
            <p><b>TG:</b> <a href={data.tg_link}>{data.tg_link}</a></p>
            <p><b>HTTPS:</b> <a href={data.https_link}>{data.https_link}</a></p>
            <img alt="QR proxy" src={`data:image/png;base64,${data.qr_base64}`} style={{ width: 220, borderRadius: 12, border: '1px solid #dbe2df' }} />
          </div>
        ) : null}
      </div>

      <div className="card">
        <h3>Как подключиться</h3>
        <div className="steps">
          <div className="step"><b>1</b><span>Нажмите на TG-ссылку или отсканируйте QR.</span></div>
          <div className="step"><b>2</b><span>Подтвердите добавление прокси в Telegram.</span></div>
          <div className="step"><b>3</b><span>Если не подключается, обновите прокси и попробуйте снова.</span></div>
        </div>
      </div>

      <div className="card">
        <h3>Мини-FAQ</h3>
        <p><b>Это безопасно?</b> Да, ссылка ведет только на прокси-узел без доступа к вашим сообщениям.</p>
        <p><b>Почему иногда не работает?</b> Ноды ротируются. Нажмите «Обновить прокси» и получите свежий endpoint.</p>
        <p><b>Нужен VPN?</b> Прокси рассчитан как fallback, когда основной VPN недоступен.</p>
      </div>
    </>
  );
}
