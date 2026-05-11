import { cookies } from 'next/headers';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';

export async function apiGet(path: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get('relay_token')?.value;
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${API}${path}`, { cache: 'no-store', headers });
  return res;
}
