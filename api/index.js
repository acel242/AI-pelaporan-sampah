import { readFileSync } from 'fs'
import { join, extname, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DIST = join(__dirname, '..', 'pelaporan-sampah', 'dist')
const BACKEND_URL = process.env.BACKEND_URL || 'https://this-sometimes-inkjet-exemption.trycloudflare.com'

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
}

export default async function handler(req, res) {
  const url = new URL(req.url, 'http://localhost')
  const pathname = url.pathname

  // API Proxy
  if (pathname.startsWith('/api/')) {
    try {
      let body
      if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
        const chunks = []
        for await (const c of req) chunks.push(c)
        body = Buffer.concat(chunks)
      }
      const headers = Object.fromEntries(
        Object.entries(req.headers).filter(([k]) =>
          !['host', 'connection', 'transfer-encoding'].includes(k.toLowerCase())
        )
      )
      const resp = await fetch(`${BACKEND_URL}${pathname}${url.search}`, { method: req.method, headers, body })
      const text = await resp.text()
      return res.status(resp.status).setHeader('Content-Type', 'application/json').send(text)
    } catch (e) {
      console.error('[proxy]', e.message)
      return res.status(502).json({ error: 'Backend unreachable' })
    }
  }

  // Static file
  const ext = extname(pathname)
  if (MIME[ext]) {
    try {
      return res.status(200).setHeader('Content-Type', MIME[ext]).send(readFileSync(join(DIST, pathname.slice(1))))
    } catch (_) {}
  }

  // SPA fallback
  try {
    return res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8').send(readFileSync(join(DIST, 'index.html'), 'utf-8'))
  } catch (e) {
    return res.status(500).send(`Cannot find ${DIST}: ${e.message}`)
  }
}
