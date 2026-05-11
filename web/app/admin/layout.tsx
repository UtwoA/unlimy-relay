import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import React from 'react';

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const token = (await cookies()).get('relay_token')?.value;
  if (!token) {
    redirect('/admin/login');
  }

  return (
    <>
      <div className="card admin-head">
        <h1>Админ-панель Relay</h1>
        <div className="admin-nav">
          <a href="/admin">Дашборд</a>
          <a href="/admin/nodes">Ноды</a>
          <a href="/admin/alerts">Алерты</a>
          <a href="/admin/audit">Аудит</a>
        </div>
        <form action="/api/auth/logout" method="post">
          <button type="submit">Выйти</button>
        </form>
      </div>
      {children}
    </>
  );
}

