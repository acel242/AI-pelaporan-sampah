# FORMAT PROPOSAL PROGRAM BCA

---

# COVER

## EcoLapor Manado v2.0
### Pelaporan Sampah Berbasis AI Agent untuk Pemerintah Kota Manado

**Program:** Gerakan Berbakti untuk Indonesia Lebih Bersih  
**Lokasi:** Kota Manado, Sulawesi Utara  
**Tanggal:** April 2026  
**Versi:** 2.0  

---

# HALAMAN IDENTITAS

| Field | Detail |
|-------|--------|
| **Nama Program** | EcoLapor Manado v2.0 |
| **Jenis Program** | Platform Pelaporan Sampah Berbasis AI |
| **Lokasi Implementasi** | Kota Manado, Sulawesi Utara |
| **Pelaksanaan Program** | 8 Juli - 6 Agustus 2026 (30 hari) |
| **Durasi Program** | 4 Minggu (Pilot) |
| **Penanggung Jawab** | Tim Pengembangan EcoLapor |
| **Kontak** | - |
| **Target Beneficiaries** | Warga Manado + Petugas Dinas LH |
| **Anggaran** | Rp 6.500.000 (Total) |

---

# RINGKASAN

EcoLapor adalah sistem pelaporan sampah berbasis AI Agent untuk Pemerintah Kota Manado, Sulawesi Utara. Sistem ini dirancang untuk meningkatkan efisiensi pengelolaan laporan sampah dari masyarakat melalui chatbot Telegram, dashboard web interaktif, dan AI reasoning untuk prioritas otomatis serta verifikasi keramaian (crowd verification).

**Permasalahan Utama:**
- Laporan palsu/spam masih mungkin terjadi tanpa verifikasi
- Tidak ada sistem vote/verifikasi dari masyarakat sekitar
- AI suggest solutions belum ada UI untuk warga melihat
- Fitur export ke Google Maps belum terpublikasi
- Belum ada autentikasi warga untuk tracking laporan pribadi

**Solusi yang Ditawarkan:**
1. Crowd Verification System — vote dari warga untuk validasi
2. Multi-Foto Upload — sampai 3 foto per laporan
3. Gamifikasi — badge dan leaderboard untuk pelapor aktif
4. AI Agent untuk Petugas — chatbot untuk petugas kebersihan
5. Auto-Routing — assign otomatis ke district berdasarkan lokasi

**Angka Kunci:**
- Total Laporan: 23+ (pilot)
- Estimasi Biaya Bulanan: Rp 300.000 - 700.000
- Target Resolution Rate: > 80% dalam 7 hari
- Target Waktu Respons: < 24 jam

---

# BAB I ANALISIS MASALAH

## 1.1 Latar Belakang

### EcoLapor di Manado

Kota Manado, dengan populasi sekitar 450.000 jiwa, menghadapi tantangan signifikan dalam pengelolaan sampah. Sistem pelaporan konvensional menyebabkan:

1. **Waktu respons yang lambat** — Laporan butuh waktu berhari-hari
2. **Tidak ada transparansi** — Warga tidak tahu status laporan
3. **Data tidak terstruktur** — Laporan tersimpan di berbagai channel
4. **Hotspot tidak teridentifikasi** — Sulit melihat area paling bermasalah

## 1.2 Capaian Sistem Saat Ini (v1.5)

| Komponen | Status | Keterangan |
|----------|--------|------------|
| Telegram Bot | ✅ Aktif | @ecolapor_bot, laporan via chat + AI priority |
| Dashboard Warga | ✅ Aktif | React, melihat status laporan + upload foto |
| Dashboard Admin | ✅ Aktif | Flask, statistik, update status, bulk actions |
| AI Priority Reasoning | ✅ Aktif | Groq vision + Deepseek fallback |
| Heatmap + Clustering | ✅ Selesai | Peta interaktif dengan heatmap per wilayah |
| Before/After Gallery | ✅ Aktif | Foto bukti tidak overwrite foto warga |
| Crowd Verification | ✅ Selesai | Vote dari warga untuk validasi |
| Auto-Escalate | ✅ Aktif | Laporan >3 hari auto-escalate |
| Reverse Geocoding | ✅ Aktif | Koordinat → alamat readable |
| GPS from EXIF | ✅ Aktif | Ekstrak GPS dari foto |
| Database | ✅ Aktif | SQLite, 23 laporan |

## 1.3 Permasalahan per Stakeholder

### Dari Sisi Warga

| Permasalahan | Frekuensi |
|-------------|-----------|
| Tidak ada feedback setelah melapor | Sangat Tinggi |
| Tidak percaya laporan akan ditindaklanjuti | Tinggi |
| Tidak tahu caranya melaporkan | Tinggi |
| Lokasi sulit dijelaskan | Sedang |

### Dari Sisi Petugas Dinas LH

| Permasalahan | Frekuensi |
|-------------|-----------|
| Tidak ada sistem pencatatan terpusat | Tinggi |
| Prioritas manual tidak konsisten | Tinggi |
| Tidak ada metric kinerja | Tinggi |
| Ulasan laporan memakan waktu | Sedang |

---

# BAB II METODE PELAKSANAAN

## 2.1 Metode Pengumpulan Data

### Data Primer
- **Pelaporan Warga:** Via Telegram Bot atau Web Form dengan upload foto
- **GPS Location:** Via GPS from EXIF atau manual input
- **Crowd Voting:** Verifikasi dari warga sekitar lokasi

### Data Sekunder
- **Data Historik:** Laporan dari sistem sebelumnya
- **Peta Dasar:** OpenStreetMap untuk visualisasi

## 2.2 Metode Analisis

### AI Priority Scoring

| Prioritas | Kondisi | SLA |
|-----------|---------|-----|
| 🟢 Rendah | Vote < 3, foto tidak jelas | 14 hari |
| 🟡 Sedang | Default | 7 hari |
| 🔴 Tinggi | >3 hari tidak ditanggapi | 24 jam |

### Teknologi Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend Web | React 18 + Vite + Tailwind + Leaflet |
| Backend API | Flask (Python) port 5000 |
| Bot | Python Telegram Bot + python-dotenv |
| AI (Primary) | Deepseek v4-pro/v4-flash |
| AI (Vision) | Groq llama-3.2-11b-vision |
| Database | SQLite (pelaporan.db) |

## 2.3 Timeline Implementasi

| Minggu | Tanggal | Aktivitas | Output |
|--------|---------|-----------|--------|
| 1 | 8-14 Juli 2026 | Crowd verification + Multi-foto + Gamifikasi | Trust system aktif |
| 2 | 15-21 Juli 2026 | AI Agent petugas + Prediksi waktu + Auto-routing | AI features complete |
| 3 | 22-28 Juli 2026 | Analisis tren spatial + Dashboard publik + Testing | Visualisasi aktif |
| 4 | 29 Juli - 6 Agustus 2026 | User auth + Mobile app + Pilot evaluation | System ready |

---

# BAB III PROGRAM KERJA & RENCANA ANGGARAN

## 3.1 Rencana Pengembangan (v2.0)

### Fase 1 — Verifikasi & Trust (1 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| Crowd Verification | Vote "benar"/"palsu" untuk validasi laporan | Critical |
| Multi-Foto | Upload sampai 3 foto per laporan | High |
| Gamifikasi | Badge "Pelapor Aktif", leaderboard | Medium |

### Fase 2 — AI Lanjutan (1 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| AI Agent Petugas | Chatbot untuk petugas kebersihan | High |
| Prediksi Waktu | Estimasi waktu proses berdasarkan historical | Medium |
| Auto-Routing | Assign ke district berdasarkan koordinat | High |

### Fase 3 — Skalabilitas (2 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| User Authentication | Login HP terverifikasi (OTP) | High |
| Analisis Tren Spatial | Heatmap + statistik per district | Medium |
| Dashboard Publik | Peta umum tanpa login | Medium |
| Mobile App | React Native untuk warga | Low |

## 3.2 Estimasi Biaya Operasional Bulanan

| Komponen | Biaya | Keterangan |
|----------|-------|------------|
| VPS Server | Rp 200.000 - 500.000 | 2 vCPU, 4GB RAM |
| Deepseek API | Rp 50.000 - 150.000 | ~$2-5/bulan |
| Groq API | GRATIS | Free tier unlimited |
| Domain | Rp 100.000/tahun | ~Rp 8.000/bulan |
| SSL | GRATIS | Let's Encrypt |
| **Total** | **~Rp 300.000 - 700.000/bulan** | |

## 3.3 Biaya Pengembangan

| Fase | Durasi | Biaya |
|------|--------|-------|
| Fase 1 (Verifikasi) | 1 minggu | Rp 1.500.000 |
| Fase 2 (AI) | 1 minggu | Rp 2.000.000 |
| Fase 3 (Skala) | 2 minggu | Rp 3.000.000 |
| **Total** | **4 Minggu** | **Rp 6.500.000** |

---

# BAB IV KEBERLANJUTAN

## 4.1 Rencana Handover

1. **Transfer Knowledge** — Training untuk tim teknis Dinas LH
2. **Dokumentasi** — Dokumentasi lengkap dalam bahasa Indonesia
3. **Source Code** — Commit ke repository dengan license
4. **Operasi** — Tim IT Dinas LH übernimmt

## 4.2 Metrix Keberhasilan

| Metric | Target | Cara Ukur |
|--------|--------|-----------|
| Waktu respons rata-rata | < 24 jam | submit → Diproses |
| Resolution rate | > 80% | Selesai dalam 7 hari |
| Accuracy AI priority | > 90% | Manual assessment |
| Crowd participation | > 20% | Warga ikut vote |
| Cost per laporan | < Rp 500 | ops cost / laporan |

## 4.3 Rencana Keberlanjutan Finansial

| Sumber Dana | Potensi |
|-------------|---------|
| Dinas LH Kota Manado | Budget operasional daerah |
| APBDes/APBD | Dana daerah untuk lingkungan |
| CSR Perusahaan | Partnership dengan korporasi |

---

# BAB V PENUTUP

EcoLapor v1.5 sudah memiliki fondasi yang solid dengan chatbot Telegram, dashboard web interaktif, heatmap, crowd verification, dan AI priority reasoning. Pengembangan ke v2.0 fokus pada:

1. **Verifikasi keramaian** — trust system tanpa perlu admin manual
2. **AI Agent untuk petugas** — otomatisasi tugas repetitif
3. **Gamifikasi** — tingkatkan engagement warga
4. **Mobile app** — aksesibilitas lebih baik

Dengan estimasi biaya Rp 300.000-700.000/bulan, sistem ini sangat feasible untuk Pemerintah Kota Manado.

**Langkah selanjutnya**: Persetujuan dari Dinas LH untuk pilot project 4 minggu, kemudian evaluasi dan pengembangan Fase 2.

---

# LAMPIRAN

## A. Link Sistem Berjalan
- Dashboard: https://eco-lapor.duckdns.org/peta
- Bot Telegram: @ecolapor_bot

## B. Referensi
- Deepseek API: https://platform.deepseek.com
- Groq API: https://console.groq.com
- Leaflet.js: https://leafletjs.com
- React: https://react.dev

## C. API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | /api/laporan | Submit laporan baru (auto AI priority) |
| GET | /api/laporan | Get all dengan filter + pagination |
| GET | /api/laporan/:id | Get single laporan + gallery |
| PATCH | /api/laporan/:id/status | Update status |
| POST | /api/laporan/:id/vote | Crowd vote (benar/palsu) |
| GET | /api/stats | Statistik dashboard admin |

## D. Database Schema

```sql
CREATE TABLE laporan (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    lokasi TEXT,
    latitude TEXT,
    longitude TEXT,
    deskripsi TEXT,
    foto TEXT,
    foto_gallery TEXT,
    kategori TEXT,
    status TEXT DEFAULT 'Menunggu',
    prioritas TEXT DEFAULT 'Sedang',
    vote_count INTEGER DEFAULT 0,
    tanggal TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    vote_type TEXT,
    created_at TEXT
);
```

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem EcoLapor Manado v2.0*
*Versi: 2.0 | Tanggal: April 2026*
*Disusun untuk: Program Gerakan Berbakti*
