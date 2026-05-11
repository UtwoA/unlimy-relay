import { redirect } from 'next/navigation';

import { apiGet } from './api';

export async function requireAdminJson(path: string) {
  const res = await apiGet(path);
  if (res.status === 401 || res.status === 403) {
    redirect('/login');
  }
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}
