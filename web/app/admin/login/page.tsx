'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminLoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('relay_admin');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, totp_code: totpCode }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(body.detail || 'Login failed');
        return;
      }
      router.push('/admin');
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card admin-login">
      <h2>Admin Login</h2>
      <form onSubmit={submit}>
        <p>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
        </p>
        <p>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        </p>
        <p>
          <input value={totpCode} onChange={(e) => setTotpCode(e.target.value)} placeholder="TOTP 6-digit" maxLength={6} />
        </p>
        <button type="submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button>
      </form>
      {error ? <p className="badge-off">{error}</p> : null}
    </div>
  );
}

