import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';

const allowed = new Set(['check', 'rotate', 'disable', 'enable', 'restart']);

export async function POST(_: NextRequest, context: any) {
  const token = (await cookies()).get('relay_token')?.value;
  if (!token) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }

  const params = context?.params ?? {};
  const id = params.id;
  const action = params.action;

  if (!id || !allowed.has(action)) {
    return NextResponse.json({ detail: 'Unsupported action' }, { status: 400 });
  }

  const url = `${API}/nodes/${id}/${action}`;
  const body = action === 'rotate' ? JSON.stringify({ trigger_type: 'manual' }) : undefined;

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body,
  });

  const text = await res.text();
  return new NextResponse(text, { status: res.status, headers: { 'Content-Type': 'application/json' } });
}
