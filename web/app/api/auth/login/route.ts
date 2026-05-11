import { NextRequest, NextResponse } from 'next/server';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${API}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!upstream.ok) {
    const detail = await upstream.text();
    return NextResponse.json({ ok: false, detail }, { status: upstream.status });
  }

  const payload = await upstream.json();
  const response = NextResponse.json({ ok: true, role: payload.role });
  response.cookies.set('relay_token', payload.access_token, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 8,
  });
  return response;
}
