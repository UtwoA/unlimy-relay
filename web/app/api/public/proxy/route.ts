import { NextRequest, NextResponse } from 'next/server';

const API = process.env.MASTER_PUBLIC_API ?? 'http://master-api:8080/api/v1';

type CacheItem = { at: number; payload: unknown };
const cache = new Map<string, CacheItem>();
const attempts = new Map<string, number[]>();

const CACHE_MS = 60_000;
const WINDOW_MS = 60_000;
const MAX_REQ = 25;

function clientIp(req: NextRequest): string {
  const fwd = req.headers.get('x-forwarded-for');
  if (fwd) return fwd.split(',')[0].trim();
  return 'unknown';
}

export async function GET(req: NextRequest) {
  const ip = clientIp(req);
  const now = Date.now();

  const arr = attempts.get(ip) ?? [];
  const valid = arr.filter((x) => now - x <= WINDOW_MS);
  if (valid.length >= MAX_REQ) {
    return NextResponse.json({ detail: 'Too many requests' }, { status: 429 });
  }
  valid.push(now);
  attempts.set(ip, valid);

  const cached = cache.get(ip);
  if (cached && now - cached.at <= CACHE_MS) {
    return NextResponse.json(cached.payload);
  }

  const upstream = await fetch(`${API}/proxy/random/qr`, { cache: 'no-store' });
  if (!upstream.ok) {
    const detail = await upstream.text();
    return NextResponse.json({ detail: detail || 'Unavailable' }, { status: upstream.status });
  }

  const payload = await upstream.json();
  cache.set(ip, { at: now, payload });
  return NextResponse.json(payload);
}
