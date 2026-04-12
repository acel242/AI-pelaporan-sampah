# PROPOSAL PENGEMBANGAN SISTEM
# EcoLapor Manado — Pelaporan Sampah Berbasis AI

---

## 1. LATAR BELAKANG

EcoLapor adalah sistem pelaporan sampah berbasis AI untuk Pemerintah Kota Manado,，旨在 meningkatkan efisiensi pengelolaan laporan sampah dari masyarakat. Sistem ini menggabungkan chatbot Telegram dengan dashboard web dan AI reasoning untuk prioritas otomatis.

**Kondisi Saat Ini:**
- Bot Telegram sudah aktif dan menangani laporan via @ecolapor_bot
- Dashboard warga (React) dan admin (Flask) sudah berfungsi
- AI priority reasoning sudah terintegrasi via Groq
- Database SQLite sudah menyimpan data laporan

---

## 2. CAPAIAN SAAT INI

### Sistem yang Sudah Berjalan

| Komponen | Status | Keterangan |
|----------|--------|------------|
| Telegram Bot | ✅ Aktif | Bot @ecolapor_bot, menangani laporan via chat |
| Dashboard Warga | ✅ Aktif | React, melihat status laporan pribadi |
| Dashboard Admin | ✅ Aktif | Flask, melihat semua laporan + statistik |
| AI Priority Reasoning | ✅ Aktif | Groq llama-3.1-8b-instant, auto-assign prioritas |
| Auto-Escalate | ✅ Aktif | Laporan >3 hari still "Menunggu" auto-escalate ke "Tinggi" |
| Image Preview | ✅ Aktif | Thumbnail foto di dashboard |
| Database | ✅ Aktif | SQLite shared, 9 laporan tersimpan |

### Teknologi yang Digunakan

- **Frontend**: React 18 + Vite + Lucide Icons
- **Backend**: Flask (Python) port 5000
- **Bot**: Python Telegram Bot + python-dotenv
- **AI**: Groq API (llama-3.1-8b-instant) — free tier 30 req/min
- **Database**: SQLite (pelaporan.db)
- **Deployment**: VPS (VM) — ports 5000 (backend), 5173 (frontend)

---

## 3. RENCANA PENGEMBANGAN

### Fase 1 — Perbaikan & Stabilisasi (1-2 minggu)

**3.1 Notifikasi Status ke Pengguna**
- Ketika admin mengubah status laporan (Menunggu → Diproses → Selesai), 用户 terima notifikasi via Telegram
- Implementasi: webhook dari Flask → Telegram Bot API

**3.2 Upload Foto Bukti**
- Admin bisa upload foto sebelum/sesudah pembersihan
- Foto ditampilkan di detail laporan

**3.3 Export Laporan**
- Admin bisa export data laporan ke CSV/Excel
- Filter berdasarkan: tanggal, status, prioritas, lokasi

**3.4 Refresh Real-time**
- Auto-refresh dashboard setiap 30 detik
- Tidak perlu manual refresh untuk lihat update

---

### Fase 2 — Fitur AI Lanjutan (2-4 minggu)

**3.5 Klasifikasi Jenis Sampah Otomatis**
- AI menganalisis deskripsi → classify: organik, anorganik, B3, campuran
- Berguna untuk statistik dan penanganan spesifik

**3.6 Prediksi Waktu Penyelesaian**
- AI estimate waktu proses berdasarkan: prioritas + lokasi + historical data
- Tampilkan estimasi ke warga saat submit laporan

**3.7 Auto-Routing Laporan**
- Berdasarkan lokasi → assign ke district/kelurahan tertentu
- Setiap district punya admin sendiri

**3.8 Analisis Tren Spatial**
- Peta panas (heatmap) laporan per wilayah
- Admin bisa lihat zona-zona yang sering muncul laporan

---

### Fase 3 — Skalabilitas (1-2 bulan)

**3.9 User Authentication**
- Login dengan nomor HP/NIK
- Satu akun = satu user, bisa track semua laporan sendiri

**3.10 Mobile App (React Native/Flutter)**
- Aplikasi mobile untuk warga
- Notifikasi push, camera upload, GPS location

**3.11 Integrasi GIS/Sistem Pemetaan**
- Laporan plotted di map
- Admin bisa lihat distribusi spasial laporan

**3.12 Dashboard Publik**
- Mapa umum yang bisa dilihat semua orang (tanpa login)
- Menampilkan statistik total laporan, zona paling banyak sampah, dll

---

## 4. ESTIMASI BIAYA OPERASI

| Komponen | Biaya/Bulan | Keterangan |
|----------|-------------|------------|
| VPS (server) | Rp 150.000 - 500.000 | Depends on specs needed |
| Groq API | GRATIS | Free tier 30 req/min, cukup untuk ±50.000 laporan/bulan |
| Domain | Rp 100.000 - 200.000/tahun | e.g. ecolapor.manadokota.go.id |
| SSL Certificate | GRATIS | Let's Encrypt |
| **Total** | **~Rp 200.000 - 700.000/bulan** | |

---

## 5. TIM PENGEMBANG

| Peran | Tugas |
|-------|-------|
| Project Manager | Koordinasi, monitoring |
| Backend Developer | Flask API, database, integrations |
| Frontend Developer | React dashboard, mobile app |
| AI/ML Engineer | AI features, analytics |
| UI/UX Designer | Wireframe, mockup, user flow |
| System Admin | Server, deployment, monitoring |

**Estimasi tim minimal**: 2-3 orang (1 fullstack + 1 designer)

---

## 6. METRIX KEBERHASILAN

| Metric | Target |
|--------|--------|
| Waktu respons rata-rata | < 24 jam dari laporan ke status "Diproses" |
| Resolution rate | > 80% laporan selesai dalam 7 hari |
| User satisfaction | > 4/5 bintang |
| Laporan palsu/spam | < 5% |
| Uptime system | > 99% |

---

## 7. DOKUMENTASI TEKNIS SINGKAT

### Arsitektur Sistem

```
                    ┌──────────────┐
                    │   Warga      │
                    │  (Telegram)  │
                    └──────┬───────┘
                           │ message
                           ▼
                 ┌─────────────────────┐
                 │    Telegram Bot     │
                 │   (Python/pytele)   │
                 └──────────┬──────────┘
                            │ write to DB
                            ▼
                 ┌─────────────────────┐
                 │     SQLite DB       │
                 │   (pelaporan.db)    │
                 └──────────┬──────────┘
                            │ read
              ┌────────────┴────────────┐
              ▼                          ▼
    ┌──────────────────┐      ┌──────────────────┐
    │   Flask Backend   │      │  Dashboard Web   │
    │   (port 5000)     │◄────►│   (React :5173)  │
    └──────────────────┘      └──────────────────┘
              │
              │ AI reasoning
              ▼
    ┌──────────────────┐
    │    Groq API       │
    │ (llama-3.1-8b)   │
    └──────────────────┘
```

### API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | /api/health | Health check |
| POST | /api/laporan | Submit laporan baru (auto AI priority) |
| GET | /api/laporan | Get all/laporan dengan filter |
| GET | /api/laporan/:id | Get single laporan |
| PATCH | /api/laporan/:id/status | Update status |
| PATCH | /api/laporan/:id/prioritas | Update prioritas |
| PATCH | /api/laporan/:id/catatan | Add catatan |
| POST | /api/foto | Add foto bukti |
| GET | /api/stats | Statistik dashboard admin |

### Database Schema

```sql
CREATE TABLE laporan (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    nama TEXT,
    lokasi TEXT,
    deskripsi TEXT,
    foto TEXT,           -- base64 atau URL
    status TEXT,         -- Menunggu/Diproses/Diselesaikan
    prioritas TEXT,      -- Rendah/Sedang/Tinggi
    catatan TEXT,
    tanggal TEXT,        -- DD/MM/YYYY
    created_at TEXT,    -- ISO timestamp
    updated_at TEXT
);

CREATE TABLE foto_bukti (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    foto_url TEXT,
    uploaded_at TEXT
);
```

---

## 8. JADWAL KERJA

| Minggu | Aktivitas |
|--------|-----------|
| 1-2 | Notifikasi + Upload Foto Bukti + Refresh Real-time |
| 3-4 | Export CSV + Klasifikasi Sampah AI |
| 5-6 | Prediksi Waktu + Auto-Routing |
| 7-8 | Heatmap + Dashboard Publik |
| 9-12 | User Auth + Mobile App (jika funding tersedia) |

---

## 9. RISIKO DAN MITIGASI

| Risiko | Mitigasi |
|--------|----------|
| API Groq limit tercapai | Cache priority, batch process, upgrade ke paid tier |
| Spam laporan palsu | Moderasi AI + verifikasi nomor HP |
| Server downtime | Monitoring + auto-restart + backup |
| Data hilang | Backup rutin SQLite + off-site storage |
| Kaburnya developer | Dokumentasi lengkap + open source jika memungkinkan |

---

## 10. KESIMPULAN

EcoLapor sudah memiliki fondasi yang solid dengan chatbot Telegram, dashboard web, dan AI priority reasoning. Pengembangan selanjutnya没必要昂贵 — Groq API gratis sudah cukup untuk skala kota. Dengan estimasi biaya Rp 200.000-700.000/bulan, sistem ini sangat feasible untuk Pemerintah Kota Manado.

**Langkah selanjutnya**: Persetujuan dari Dinas LH untuk pilot project 1 bulan, kemudian evaluasi dan pengembangan Fase 2.

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem EcoLapor Manado.*
*Versi: 1.0 | Tanggal: 13 April 2026*
