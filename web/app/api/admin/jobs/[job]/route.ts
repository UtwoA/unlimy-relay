import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';
const allowed = new Set(['health', 'rotation']);

export async function POST(_: NextRequest, context: any) {
  const token = (await cookies()).get('relay_token')?.value;
  if (!token) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }

  const job = context?.params?.job;
  if (!allowed.has(job)) {
    return NextResponse.json({ detail: 'Unsupported job' }, { status: 400 });
  }

  const target = job === 'health' ? '/jobs/health/run' : '/jobs/rotation/run';
  const res = await fetch(`${API}${target}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });

  const text = await res.text();
  return new NextResponse(text, {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
}
