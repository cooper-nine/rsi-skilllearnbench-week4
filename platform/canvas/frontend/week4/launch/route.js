export async function POST(request) {
  const token = process.env.RSI_WEEK4_TOKEN;
  if (process.env.NODE_ENV !== 'development' || !token) {
    return new Response(null, { status: 404 });
  }
  const host = request.headers.get('host') ?? '';
  if (!/^(localhost|127\.0\.0\.1)(:\d+)?$/.test(host)
      || request.headers.get('origin') !== 'http://' + host) {
    return new Response(null, { status: 403 });
  }
  const structure = await request.text();
  if (structure.length > 150000) return new Response(null, { status: 413 });
  const backend = process.env.RSI_FLOW_BACKEND_URL ?? 'http://127.0.0.1:39910';
  const result = await fetch(backend + '/api/engine/flow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flowId: 'RSI_WEEK4_CANVAS', params: { structure, token } }),
  });
  return new Response(await result.text(), {
    status: result.status, headers: { 'Content-Type': 'application/json' },
  });
}
