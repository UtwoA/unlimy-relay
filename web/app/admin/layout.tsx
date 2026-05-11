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
        <h1>Relay Admin</h1>
        <div className="admin-nav">
          <a href="/admin">Dashboard</a>
          <a href="/admin/nodes">Nodes</a>
          <a href="/admin/alerts">Alerts</a>
          <a href="/admin/audit">Audit</a>
        </div>
        <form action="/api/auth/logout" method="post">
          <button type="submit">Logout</button>
        </form>
      </div>
      {children}
    </>
  );
}
