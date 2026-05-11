import { NextResponse } from 'next/server';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';

export async function GET() {
  const upstream = await fetch(`${API}/proxy/public-status`, { cache: 'no-store' });
  if (!upstream.ok) {
    const detail = await upstream.text();
    return NextResponse.json({ detail: detail || 'Unavailable' }, { status: upstream.status });
  }
  const payload = await upstream.json();
  return NextResponse.json(payload);
}
