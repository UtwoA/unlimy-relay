import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';

export async function GET() {
  const token = (await cookies()).get('relay_token')?.value;
  if (!token) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }

  const res = await fetch(`${API}/admin/overview`, {
    cache: 'no-store',
    headers: { Authorization: `Bearer ${token}` },
  });

  const text = await res.text();
  return new NextResponse(text, {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
}
