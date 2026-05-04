#!/bin/bash
BACKEND_LOG="/home/ubuntu/.ecolapor-tunnel-backend.log"
PROXY_LOG="/home/ubuntu/.ecolapor-proxy.log"

get_backend_url() {
    local url=$(cat /home/ubuntu/.ecolapor-tunnel-backend.log.url 2>/dev/null)
    if [ -z "$url" ]; then
        url=$(grep -o 'https://[^ ]*trycloudflare.com' $BACKEND_LOG 2>/dev/null | head -1)
    fi
    echo "$url"
}

node -e "
const http = require('http');
const fs = require('fs');
const path = require('path');
const URL = require('url').URL;

const DIST = '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah/pelaporan-sampah/dist';
const BACKEND_FILE = '/home/ubuntu/.ecolapor-tunnel-backend.log.url';
const MIME = {'.html':'text/html','.css':'text/css','.js':'application/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'};

function getBackend() {
  try {
    const url = fs.readFileSync(BACKEND_FILE, 'utf8').trim();
    if (url && url.startsWith('https://')) return url;
  } catch(_) {}
  return 'https://hottest-assured-tip-investigations.trycloudflare.com';
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  
  if (url.pathname.startsWith('/api/')) {
    const backend = getBackend();
    try {
      const bdy = await new Promise(r => { let d=[]; req.on('data',c=>d.push(c)); req.on('end',()=>r(Buffer.concat(d))); });
      const headers = {};
      for (const [k,v] of Object.entries(req.headers)) { if (!['host','connection','transfer-encoding','content-length'].includes(k.toLowerCase())) headers[k] = v; }
      const resp = await fetch(backend + url.pathname + url.search, { method: req.method, headers, body: bdy.length ? bdy : undefined, signal: AbortSignal.timeout(10000) });
      const text = await resp.text();
      res.writeHead(resp.status, {'Content-Type': resp.headers.get('content-type') || 'application/json', 'Access-Control-Allow-Origin': '*'});
      res.end(text);
    } catch (e) { res.writeHead(502); res.end(JSON.stringify({error:'Backend unreachable: ' + e.message})); }
    return;
  }

  // Proxy /static/foto/* to local backend (port 5000) - photos stored on backend server
  if (url.pathname.startsWith('/static/foto/')) {
    try {
      const resp = await fetch('http://localhost:5000' + url.pathname + url.search, { 
        method: req.method, 
        headers: { 'Accept': req.headers['accept'] || '*/*' }, 
        signal: AbortSignal.timeout(10000) 
      });
      const buf = Buffer.from(await resp.arrayBuffer());
      res.writeHead(resp.status, {'Content-Type': resp.headers.get('content-type') || 'image/jpeg', 'Cache-Control': 'public, max-age=300'});
      res.end(buf);
    } catch (e) { res.writeHead(502, {'Content-Type': 'application/json'}); res.end(JSON.stringify({error:'Failed to load image: ' + e.message})); }
    return;
  }

  const filePath = url.pathname === '/' ? '/index.html' : url.pathname;
  const fullPath = path.join(DIST, filePath);
  const ext = path.extname(fullPath);
  if (MIME[ext]) { try { res.writeHead(200, {'Content-Type': MIME[ext]}); res.end(fs.readFileSync(fullPath)); return; } catch(_) {} }
  try { res.writeHead(200, {'Content-Type':'text/html'}); res.end(fs.readFileSync(path.join(DIST, 'index.html'))); } catch(_) { res.writeHead(404); res.end('Not found'); }
});

server.listen(5004, '0.0.0.0', () => console.log('EcoLapor proxy on :5004'));
"
