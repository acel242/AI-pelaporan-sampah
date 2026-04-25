# PROPOSAL PENGEMBANGAN SISTEM
# EcoLapor Manado v2.0 — Pelaporan Sampah Berbasis AI Agent

---

## 1. LATAR BELAKANG

EcoLapor adalah sistem pelaporan sampah berbasis AI Agent untuk Pemerintah Kota Manado, Sulawesi Utara. Sistem ini dirancang untuk meningkatkan efisiensi pengelolaan laporan sampah dari masyarakat melalui chatbot Telegram, dashboard web interaktif, dan AI reasoning untuk prioritas otomatis serta verifikasi keramaian (crowd verification).

**Kondisi Saat Ini (v1.0):**
- Bot Telegram @ecolapor_bot sudah aktif menangani laporan via chat
- Dashboard warga (React) dan admin (Flask) sudah berfungsi
- AI priority reasoning sudah terintegrasi via Groq + Deepseek
- Database SQLite menyimpan 23+ laporan dengan before/after photo gallery
- Heatmap dan marker clustering sudah terimplementasi
- Fitur crowd verification dan AI suggest solutions sudah ada di commit

**Permasalahan yang Dihadapi:**
- Laporan palsu/spam masih mungkin terjadi tanpa verifikasi
- Tidak ada sistem vote/verifikasi dari masyarakat sekitar
- AI suggest solutions belum ada UI untuk warga melihat
- Fitur export ke Google Maps belum terpublikasi
- belum ada autentikasi warga untuk tracking laporan pribadi

---

## 2. CAPAIAN SAAT INI (v1.5)

### Sistem yang Sudah Berjalan

| Komponen | Status | Keterangan |
|----------|--------|------------|
| Telegram Bot | ✅ Aktif | @ecolapor_bot, laporan via chat + AI priority |
| Dashboard Warga | ✅ Aktif | React, melihat status laporan + upload foto |
| Dashboard Admin | ✅ Aktif | Flask, statistik, update status, bulk actions |
| AI Priority Reasoning | ✅ Aktif | Groq vision (llama-3.2-11b) + Deepseek fallback |
| Heatmap + Clustering | ✅ Selesai | Peta interaktif dengan heatmap per wilayah |
| Before/After Gallery | ✅ Aktif | Foto bukti petugas tidak overwrite foto warga |
| Crowd Verification | ✅ Selesai | Vote dari warga untuk validasi laporan |
| AI Suggest Solutions | ✅ Selesai | AI memberikan saran solusi (admin only) |
| Auto-Escalate | ✅ Aktif | Laporan >3 hari auto-escalate ke "Tinggi" |
| Reverse Geocoding | ✅ Aktif | Koordinat → alamat readable |
| GPS from EXIF | ✅ Aktif | Ekstrak GPS dari foto langsung |
| Export Google Maps | ✅ Selesai | Export laporan ke Google Maps format |
| Database | ✅ Aktif | SQLite, 23 laporan |

### Teknologi yang Digunakan

| Layer | Teknologi |
|-------|-----------|
| Frontend Web | React 18 + Vite + Tailwind + Leaflet |
| Backend API | Flask (Python) port 5000 |
| Bot | Python Telegram Bot + python-dotenv |
| AI (Primary) | Deepseek v4-pro/v4-flash (OpenAI-compatible) |
| AI (Vision) | Groq llama-3.2-11b-vision-preview |
| Database | SQLite (pelaporan.db) |
| Map | Leaflet + OpenStreetMap |
| Deployment | VPS VM — Cloudflare Tunnel |

---

## 3. RENCANA PENGEMBANGAN (v2.0)

### Fase 1 — Verifikasi & Trust (2-3 minggu)

**3.1 Crowd Verification System**
- Warga bisa vote "benar" / "palsu" untuk laporan yang belum terverifikasi
- Laporan dengan >3 vote "palsu" otomatis diturunkan prioritasnya
- Badge "Terverifikasi Crowd" muncul di laporan yang sudah di-vote valid

**3.2 Laporan dengan Multi-Foto**
- Warga bisa upload sampai 3 foto saat submit laporan
- AI menganalisis semua foto, bukan cuma satu

**3.3 Gamifikasi Warga**
- Badge "Pelapor Aktif" untuk warga yang sering melapor
- Leaderboard bulanan pelapor teraktif
- Poin reward untuk verifikasi laporan orang lain

---

### Fase 2 — AI Lanjutan (3-4 minggu)

**3.4 AI Agent for Petugas**
- Chatbot AI untuk petugas kebersihan
- Bisa jawab pertanyaan seperti: "Laporan mana terdekat dari saya?"
- Bisa kasih instruksi teknis: "Cara evakuasi sampah di jalan X"

**3.5 Prediksi Waktu Penyelesaian**
- AI estimasi waktu proses berdasarkan: prioritas + lokasi + historical
- Tampilkan estimasi ke warga saat submit: "Ditangani dalam 2-3 hari"

**3.6 Auto-Routing Berdasarkan Lokasi**
- Laporan auto-assign ke district/kelurahan berdasarkan koordinat
- Setiap district punya admin + petugas sendiri
- Notifikasi otomatis ke petugas yang zugehörig

**3.7 Analisis Tren Spatial**
- Heatmap bulanan untuk lihat zonaHotspot sampah
- Statistik per district: mana paling banyak laporan, paling cepat selesai
- Prediksi area rawan berdasarkan historical data

---

### Fase 3 — Skalabilitas & Sustainability (2-3 bulan)

**3.8 User Authentication**
- Login dengan nomor HP terverifikasi (OTP)
- Satu akun = satu user, track semua laporan sendiri
- Notification preference: Telegram / SMS / WhatsApp

**3.9 Mobile App (React Native)**
- Aplikasi mobile untuk warga
- Camera upload + GPS auto-detect
- Push notification untuk update status laporan

**3.10 Integrasi Pihak Ketiga**
- API untuk Dinas LH kota akses data real-time
- Webhook ke sistem pemerintah daerah lain
- Integration dengan 112 / call center

**3.11 Dashboard Publik**
- Mapa umum yang bisa dilihat semua orang (tanpa login)
- Statistik total, zona paling banyak sampah, resolution rate
- Embeddable widget untuk website pemerintah

---

## 4. ESTIMASI BIAYA OPERASI

| Komponen | Biaya/Bulan | Keterangan |
|----------|-------------|------------|
| VPS (server) | Rp 200.000 - 500.000 | Depends on specs needed |
| Deepseek API | Rp 50.000 - 150.000 | ~$2-5/bulan untuk 100K requests |
| Groq API | GRATIS | Free tier 30 req/min, cukup untuk ±50K laporan/bulan |
| Cloudflare Tunnel | GRATIS | Remote access tanpa perlu public IP |
| Domain | Rp 100.000 - 200.000/tahun | e.g. ecolapor.manadokota.go.id |
| SSL Certificate | GRATIS | Let's Encrypt |
| **Total** | **~Rp 300.000 - 700.000/bulan** | |

---

## 5. TIM PENGEMBANG

| Peran | Tugas |
|-------|-------|
| Project Manager | Koordinasi, monitoring, reporting |
| Backend Developer | Flask API, database, integrations |
| Frontend Developer | React dashboard, mobile app |
| AI/ML Engineer | AI features, analytics, crowd verification logic |
| UI/UX Designer | Wireframe, mockup, user flow |
| System Admin | Server, deployment, monitoring, security |

**Estimasi tim minimal**: 2-3 orang (1 fullstack + 1 AI engineer + 1 designer)

---

## 6. METRIX KEBERHASILAN

| Metric | Target | Cara Ukur |
|--------|--------|-----------|
| Waktu respons rata-rata | < 24 jam | Dari submit → status "Diproses" |
| Resolution rate | > 80% | Laporan selesai dalam 7 hari |
| Accuracy AI priority | > 90% | Bandingkan dengan manual assessment |
| Crowd participation | > 20% | Warga yang ikut vote / verifikasi |
| User satisfaction | > 4/5 bintang | Survey bulanan |
| Laporan palsu/spam | < 5% | Persentase laporan yang divote "palsu" |
| Uptime system | > 99% | Monitoring uptime |
| Cost per laporan | < Rp 500 | Biaya operasi / jumlah laporan |

---

## 7. DOKUMENTASI TEKNIS

### Arsitektur Sistem v2.0

```
                        ┌──────────────────┐
                        │      Warga       │
                        │   (Telegram +    │
                        │    Website)      │
                        └────────┬─────────┘
                                 │ message / http
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │  Telegram Bot    │  │   Flask API      │  │  React Frontend  │
  │  (Python/pytele) │  │   (port 5000)   │  │  (port 5004)     │
  └────────┬─────────┘  └────────┬─────────┘  └──────────────────┘
           │                      │
           │ write/read           │ read/write
           ▼                      ▼
  ┌──────────────────────────────────────────────┐
  │              SQLite Database                  │
  │           (pelaporan.db)                     │
  └──────────────────────────────────────────────┘
           │                      │
           │ AI reasoning         │ AI vision
           ▼                      ▼
  ┌──────────────────┐  ┌──────────────────┐
  │   Deepseek API    │  │    Groq API       │
  │  (v4-pro/flasha) │  │ (llama-3.2-11b)  │
  └──────────────────┘  └──────────────────┘
```

### API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | /api/health | Health check |
| POST | /api/laporan | Submit laporan baru (auto AI priority) |
| GET | /api/laporan | Get all/laporan dengan filter + pagination |
| GET | /api/laporan/:id | Get single laporan + gallery |
| PATCH | /api/laporan/:id/status | Update status |
| PATCH | /api/laporan/:id/prioritas | Update prioritas |
| PATCH | /api/laporan/:id/jenis | Update jenis sampah |
| PATCH | /api/laporan/:id/catatan | Add catatan |
| POST | /api/laporan/:id/vote | Crowd vote (benar/palsu) |
| GET | /api/laporan/:id/votes | Get vote count |
| GET | /api/laporan/:id/suggest | AI suggest solution |
| POST | /api/foto | Upload foto bukti |
| POST | /api/laporan/:id/foto | Add foto ke gallery |
| GET | /api/export/maps | Export ke Google Maps format |
| GET | /api/stats | Statistik dashboard admin |
| GET | /api/notifications | Get notifications |

### Database Schema

```sql
CREATE TABLE laporan (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    nama TEXT,
    lokasi TEXT,
    latitude TEXT,
    longitude TEXT,
    deskripsi TEXT,
    foto TEXT,
    foto_gallery TEXT,       -- JSON array of additional photos
    kategori TEXT,           -- Sampah / Fasilitas Rusak / dll
    sub_kategori TEXT,
    jenis_sampah TEXT,
    status TEXT,             -- Menunggu / Diproses / Selesai
    prioritas TEXT,          -- Rendah / Sedang / Tinggi
    catatan TEXT,
    vote_count INTEGER DEFAULT 0,
    tanggal TEXT,            -- DD/MM/YYYY
    created_at TEXT,         -- ISO timestamp
    updated_at TEXT
);

CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    voter_id INTEGER,
    vote_type TEXT,          -- benar / palsu
    created_at TEXT,
    FOREIGN KEY (laporan_id) REFERENCES laporan(id)
);

CREATE TABLE foto_bukti (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    foto_url TEXT,
    foto_type TEXT,          -- before / after
    uploaded_at TEXT,
    FOREIGN KEY (laporan_id) REFERENCES laporan(id)
);
```

---

## 8. JADWAL KERJA

| Bulan | Aktivitas |
|-------|-----------|
| Bulan 1 | Crowd verification + Multi-foto + Gamifikasi |
| Bulan 2 | AI Agent petugas + Prediksi waktu + Auto-routing |
| Bulan 3 | Analisis tren spatial + Dashboard publik |
| Bulan 4 | User auth + Mobile app (React Native) |
| Bulan 5 | Integrasi pihak ketiga + API documentation |
| Bulan 6 | Testing, optimization, pilot evaluation |

---

## 9. RISIKO DAN MITIGASI

| Risiko | Probabilitas | Mitigasi |
|--------|-------------|----------|
| API Deepseek biaya tinggi | Medium | Set budget alert, use Groq as primary, Deepseek only for complex tasks |
| Laporan palsu/spam | High | Crowd verification + AI anomaly detection + OTP verification |
| Server downtime | Low | Cloudflare Tunnel + auto-restart + monitoring |
| Data hilang | Low | Backup rutin SQLite + off-site storage + git commit history |
| Kaburnya developer | Medium | Full documentation + open source if possible |
| AI misclassify priority | Medium | Human review queue for edge cases + feedback loop |
| Map tidak load di daerah terpencil | Medium | Offline-first approach + GPS fallback |

---

## 10. KESIMPULAN

EcoLapor v1.5 sudah memiliki fondasi yang solid dengan chatbot Telegram, dashboard web interaktif, heatmap, crowd verification, dan AI priority reasoning. Pengembangan ke v2.0 fokus pada:

1. **Verifikasi keramaian** — trust system tanpa perlu admin manual
2. **AI Agent untuk petugas** — otomatisasi tugas repetitif
3. **Gamifikasi** — tingkatkan engagement warga
4. **Mobile app** — aksesibilitas lebih baik

Dengan estimasi biaya Rp 300.000-700.000/bulan dan Groq API yang gratis untuk use case normal, sistem ini sangat feasible untuk Pemerintah Kota Manado.

**Langkah selanjutnya**: Persetujuan dari Dinas LH untuk pilot project 1 bulan, kemudian evaluasi dan pengembangan Fase 2.

---

## 11. LAMPIRAN

### A. Link Sistem Berjalan
- Dashboard: https://eco-lapor.duckdns.org/peta
- Bot Telegram: @ecolapor_bot

### B. Repository
- GitHub: (akan di-push setelah SSH key ditambahkan)

### C. Referensi
- Deepseek API: https://platform.deepseek.com
- Groq API: https://console.groq.com
- Leaflet.js: https://leafletjs.com
- React: https://react.dev

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem EcoLapor Manado v2.0*
*Versi: 2.0 | Tanggal: 25 April 2026*
