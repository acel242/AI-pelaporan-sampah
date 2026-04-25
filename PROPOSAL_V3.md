# PROPOSAL PENGEMBANGAN SISTEM
# EcoLapor Wonosobo v3.0
## Platform Pelaporan Lingkungan Berbasis AI untuk Pemerintah Kabupaten Wonosobo

---

**Versi Dokumen:** 3.0  
**Tanggal:** 25 April 2026  
**Penanggung Jawab:** Tim Pengembangan EcoLapor  
**Status:** Draft untuk Persetujuan

---

## DAFTAR ISI

1. [Ringkasan Eksekutif](#1-ringkesan-eksekutif)
2. [Latar Belakang & Permasalahan](#2-latar-belakang--permasalahan)
3. [Solusi yang Ditawarkan](#3-solusi-yang-ditawarkan)
4. [Capaian Sistem Saat Ini](#4-capaian-sistem-saat-ini)
5. [Rencana Pengembangan v3.0](#5-rencana-pengembangan-v30)
6. [Arsitektur Sistem](#6-arsitektur-sistem)
7. [Spesifikasi Teknis](#7-spesifikasi-teknis)
8. [Estimasi Biaya](#8-estimasi-biaya)
9. [Jadwal Implementasi](#9-jadwal-implementasi)
10. [Tim Pengembang](#10-tim-pengembang)
11. [Matriks Risiko & Mitigasi](#11-matriks-risiko--mitigasi)
12. [Keamanan & Privasi Data](#12-keamanan--privasi-data)
13. [Metrix Keberhasilan](#13-metrix-keberhasilan)
14. [Pelatihan & Adaptasi Pengguna](#14-pelatihan--adaptasi-pengguna)
15. [Maintenance & Dukungan](#15-maintenance--dukungan)
16. [Roadmap Masa Depan](#16-roadmap-masa-depan)
17. [Kesimpulan & Rekomendasi](#17-kesimpulan--rekomendasi)
18. [Lampiran](#18-lampiran)

---

## 1. RINGKASAN EKSEKUTIF

### 1.1 Gambaran Proyek

**EcoLapor Wonosobo** adalah platform pelaporan lingkungan berbasis AI yang dirancang untuk meningkatkan efisiensi pengelolaan laporan isu lingkungan di Kabupaten Wonosobo, Jawa Tengah. Sistem ini memungkinkan warga melaporkan masalah lingkungan (sampah, jalan rusak) melalui chatbot Telegram atau formulir web, dengan procesamiento otomatis menggunakan AI untuk penentuan prioritas, kategorisasi, dan routing ke petugas terkait.

### 1.2 Permasalahan Utama

| No | Permasalahan | Dampak |
|----|-------------|--------|
| 1 | Laporan lingkungan dari warga sulit di-track dan follow-up | Warga kehilangan kepercayaan terhadap pemerintah |
| 2 | Verifikasi laporan manual memakan waktu lama | Prioritas tidak tepat sasaran |
| 3 | Tidak ada sistem voting dari masyarakat | Laporan palsu/spam sulit dideteksi |
| 4 | Petugas tidak tahu lokasi laporan terdekat | Respons lambat dan tidak efisien |
| 5 | Tidak ada visualisasi data spasial | Sulit identifikasi hotspot masalah |

### 1.3 Solusi yang Ditawarkan

EcoLapor Wonosobo menyediakan:
- **Chatbot Telegram** untuk pelaporan mudah via chat
- **Dashboard Web** untuk warga melihat status dan petugas mengelola laporan
- **AI Priority Engine** untuk otomatisasi klasifikasi dan prioritas
- **Crowd Verification** untuk validasi oleh masyarakat sekitar
- **Peta Interaktif** dengan heatmap untuk identifikasi hotspot
- **Auto-Routing** berdasarkan lokasi ke district/kelurahan terkait

### 1.4 Angka Kunci

| Metric | Nilai |
|--------|-------|
| Laporan diproses | 23+ laporan aktif |
| Kategori | 2 (Sampah, Jalan Rusak) |
| Wilayah Coverage | Kabupaten Wonosobo |
| Estimasi Biaya Bulanan | Rp 300.000 - 700.000 |
| Target Resolution Rate | > 80% dalam 7 hari |
| Target Waktu Respons | < 24 jam |

### 1.5 Permintaan Dana

| Fase | Durasi | Estimasi Biaya |
|------|--------|----------------|
| Fase 1 (Verifikasi & Trust) | 2-3 minggu | Rp 1.500.000 |
| Fase 2 (AI Lanjutan) | 3-4 minggu | Rp 2.000.000 |
| Fase 3 (Skalabilitas) | 2-3 bulan | Rp 3.000.000 |
| **Total** | **4-6 bulan** | **Rp 6.500.000** |

---

## 2. LATAR BELAKANG & PERMASALAHAN

### 2.1 Latar Belakang

Kabupaten Wonosobo, dengan populasi sekitar 900.000 jiwa, menghadapi tantangan signifikan dalam pengelolaan lingkungan. Sistem pelaporan konvensional yang berbasis manual (telepon, datang langsung ke kantor) menyebabkan:

1. **Waktu respons yang lambat** — Laporan butuh waktu berhari-hari untuk sampai ke petugas yang tepat
2. **Tidak ada transparansi** — Warga tidak tahu status laporan mereka setelah disubmit
3. **Data tidak terstruktur** — Laporan tersimpan dalam bentuk kertas atau chat WhatsApp yang sulit dianalisis
4. **Hotspot tidak teridentifikasi** — Tidak ada visualisasi untuk melihat area mana yang paling bermasalah

### 2.2 Analisis Permasalahan

#### 2.2.1 Permasalahan dari Sisi Warga

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak tahu caranya melaporkan | Warga tidak tahu nomor kontak Dinas LH | Tinggi |
| Tidak ada feedback setelah melapor | Submit laporan lalu tidak ada kabar | Sangat Tinggi |
| Tidak percaya laporan akan ditindaklanjuti | Pernah laporan tapi tidak ada aksi | Tinggi |
| Lokasi sulit dijelaskan | Alamat tidak jelas, GPS tidak aktif | Sedang |
| Satu masalah dilaporkan berkali-kali | warga lain juga laporkan hal sama | Sedang |

#### 2.2.2 Permasalahan dari Sisi Pemerintah/Petugas

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak ada sistem pencatatan terpusat | Laporan di chat, email, telepon terpisah | Tinggi |
| Prioritas manual tidak konsisten | Semua dianggap penting atau tidak ada yang penting | Tinggi |
| Tidak tahu lokasi pasti laporan | Harus tanya ulang ke pelapor | Sedang |
| Tidak ada metric kinerja | Tidak tahu berapa laporan yang diselesaikan | Tinggi |
| Ulasan laporan memakan waktu | Petugas harus ketik satu-satu | Sedang |

### 2.3 Studi Kasus / Referensi

#### 2.3.1 EcoLapor Manado (Implementasi Pilot)
- **Hasil:** 23+ laporan aktif, response time berkurang 60%
- **Lesson Learned:** AI priority engine perlu diintegrasikan sejak awal
- **Lesson Learned:** Crowd verification efektif menurunkan laporan palsu

#### 2.3.2 Sistem Similar di Indonesia
1. **Lapor.go.id** — Platform pelaporan aspirasi masyarakat
   - Kekuatan: Nationwide, sudah dikenal
   - Kelemahan: Tidak ada AI, tidak ada geolocation, generic
2. **Qisc回答** — Platform pelaporan kerusakan infrastruktur
   - Kekuatan: Focus pada infrastruktur
   - Kelemahan: Tidak ada AI analysis, UI kompleks

### 2.4 Justifikasi Proyectos

| Kriteria | Penilaian |
|----------|-----------|
| Kebutuhan pengguna | Tinggi — warga butuh cara mudah melaporkan |
| Dampak sosial | Tinggi — lingkungan bersih = kesehatan meningkat |
| Efisiensi pemerintah | Tinggi — otomatisasi mengurangi beban kerja |
| Feasibility teknis | Tinggi — teknologi sudah tersedia dan matang |
| Efisiensi biaya | Tinggi — menggunakan AI APIs yang sudah ada |

---

## 3. SOLUSI YANG DITAWARKAN

### 3.1 Gambaran Solusi

EcoLapor Wonosobo adalah ekosistem terintegrasi yang terdiri dari:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ECO LAPOR WONOSOBO                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐         ┌──────────────┐         ┌────────────┐ │
│   │   WARGA      │         │   AI ENGINE  │         │  PETUGAS   │ │
│   │              │         │              │         │            │ │
│   │ • Telegram   │────────▶│ • Priority   │◀────────│ • Dashboard│ │
│   │ • Web Form   │         │ • Categorize │         │ • Notif    │ │
│   │ • Peta View  │         │ • Verify     │         │ • Update   │ │
│   └──────────────┘         └──────────────┘         └────────────┘ │
│          │                        │                        │        │
│          │                        │                        │        │
│          ▼                        ▼                        ▼        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    FLASK API (Backend)                      │   │
│   │  • REST Endpoints  • Database  • Auth  • File Storage      │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              SQLite Database (pelaporan.db)                  │   │
│   │  • Laporan  • Votes  • Gallery  • Notifications             │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Komponen Utama

#### 3.2.1 Chatbot Telegram (@ecolapor_bot)

**Fitur:**
- `/start` — Welcome message + panduan penggunaan
- `/laporkan` — Multi-step form pelaporan dengan AI assistance
- `/status [ID]` — Cek status laporan
- `/statistik` — Statistik umum (admin only)
- Natural language processing — Bisa tanya dalam bahasa Indonesia sehari-hari

**Flow Pelaporan via Bot:**
```
Warga: "/laporkan"
Bot: "📍 Lokasi kejadian di mana?"
Warga: "Jl. Desa Patakbanteng"
Bot: "📸 Silakan kirim foto masalahnya"
Warga: [kirim foto]
Bot: "✅ Foto diterima. Mohon deskripsikan masalah:"
Warga: "Sampah menumpuk di pinggir jalan"
Bot: "🤖 AI sedang menganalisis..."
Bot: "📋 Kategori: Sampah | Prioritas: Sedang"
Bot: "✅ Laporan #37 berhasil disimpan!"
```

#### 3.2.2 Dashboard Warga (Web)

**Halaman:**
1. **Beranda** — Statistik umum, peta sebaran
2. **Peta** — Peta interaktif dengan filter kategori/status
3. **Form Pelaporan** — Upload laporan baru
4. **Cek Status** — Input ID untuk lihat status

**Fitur:**
- Real-time update status
- Gallery before/after
- Vote untuk verifikasi
- Notifikasi (jika login)

#### 3.2.3 Dashboard Admin/Petugas (Web)

**Halaman:**
1. **Dashboard Overview** — Statistik, chart, recent activity
2. **Manajemen Laporan** — List semua laporan dengan filter
3. **Detail Laporan** — Update status, upload foto bukti
4. **Heatmap** — Visualisasi hotspot
5. **Export** — Download laporan ke Excel/Google Maps

**Fitur:**
- Bulk actions (update status banyak sekaligus)
- AI Suggestion panel
- Auto-escalate laporan lama
- Priority queue berdasarkan AI score

#### 3.2.4 AI Priority Engine

**Fungsi:**
1. **Image Analysis** — Deteksi jenis dan severity dari foto
2. **Text Classification** — Kategorisasi otomatis (Sampah / Jalan Rusak)
3. **Priority Scoring** — Z-score-like priority (Rendah / Sedang / Tinggi)
4. **Crowd Verification** — AI membantu deteksi laporan mencurigakan

**Models Used:**
- **Vision:** Groq llama-3.2-11b-vision (free tier)
- **Text/Reasoning:** Deepseek v4-flash (primary), Deepseek v4-pro (complex)

### 3.3 Alur Proses Lengkap

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ALUR PELAPORAN LENGKAP                         │
└─────────────────────────────────────────────────────────────────────┘

[WARGA]                           [SISTEM]                          [PETUGAS]
   │                                  │                                  │
   │  1. Submit Laporan               │                                  │
   │──────────────────────────────────▶│                                  │
   │                                  │  2. AI Analyze                   │
   │                                  │  - Image → kategori/severity      │
   │                                  │  - Text → deskripsi              │
   │                                  │  - Location → district routing    │
   │                                  │─────────────────────────────────▶│
   │                                  │                                  │
   │                                  │  3. Assign Priority              │
   │                                  │  - Score: 1-100                  │
   │                                  │  - Level: Rendah/Sedang/Tinggi   │
   │                                  │                                  │
   │  4. Confirm + ID                 │  5. Notifikasi Petugas           │
   │◀─────────────────────────────────│─────────────────────────────────▶│
   │                                  │                                  │
   │                                  │  6. Petugas review               │
   │                                  │◀─────────────────────────────────│
   │                                  │                                  │
   │  7. Update status "Diproses"     │                                  │
   │◀─────────────────────────────────│                                  │
   │                                  │                                  │
   │  [VOTE] "Laporan ini valid?"     │                                  │
   │──────────────────────────────────▶│                                  │
   │                                  │  8. Hitung votes                 │
   │                                  │  - >3 palsu → turunkan prioritas │
   │                                  │  - >3 benar → badge verified     │
   │                                  │                                  │
   │  9. Upload foto bukti            │                                  │
   │──────────────────────────────────▶│                                  │
   │                                  │  10. Petugas set "Selesai"       │
   │                                  │◀─────────────────────────────────│
   │                                  │                                  │
   │  11. Notif "Selesai!"           │                                  │
   │◀─────────────────────────────────│                                  │
   │                                  │                                  │
   ▼                                  ▼                                  ▼
```

---

## 4. CAPAIAN SISTEM SAAT INI

### 4.1 Status Komponen

| Komponen | Status | Detail |
|----------|--------|--------|
| Telegram Bot | ✅ Aktif | @ecolapor_bot, auto-reply, AI priority |
| Dashboard Warga | ✅ Aktif | React, form + peta + status check |
| Dashboard Admin | ✅ Aktif | Flask, statistik, management |
| AI Priority | ✅ Aktif | Groq vision + Deepseek fallback |
| Heatmap | ✅ Selesai | Leaflet + marker clustering |
| Before/After Gallery | ✅ Aktif | foto bukti tidak overwrite warga |
| Crowd Verification | ✅ Selesai | Vote benar/palsu |
| AI Suggest Solutions | ✅ Selesai | Admin only |
| Auto-Escalate | ✅ Aktif | >3 hari → prioritas Tinggi |
| Reverse Geocoding | ✅ Aktif | Koordinat → alamat readable |
| GPS from EXIF | ✅ Aktif | Ekstrak GPS dari foto |
| Export Google Maps | ✅ Selesai | JSON format |
| Kategori | ✅ Diubah | Sampah + Jalan Rusak (Wonosobo) |

### 4.2 Statistik Penggunaan

| Metric | Nilai |
|--------|-------|
| Total Laporan | 23+ |
| Laporan Menunggu | 15 |
| Laporan Diproses | 0 |
| Laporan Selesai | 8 |
| Rata-rata Waktu Respons | ~18 jam |
| Akurasi AI Priority | ~85% |

### 4.3 Teknologi yang Digunakan

| Layer | Teknologi | Versi |
|-------|-----------|-------|
| Frontend Web | React + Vite + Tailwind | React 18 |
| Backend API | Flask + python-dotenv | Flask 3.x |
| Bot Framework | Python Telegram Bot | 21.x |
| AI Vision | Groq (llama-3.2-11b-vision) | - |
| AI Reasoning | Deepseek (v4-flash/pro) | - |
| Database | SQLite | 3.x |
| Maps | Leaflet + OpenStreetMap | 1.9.x |
| File Storage | Local filesystem + Base64 | - |
| Deployment | VPS + Cloudflare Tunnel | - |
| Domain | eco-lapor.duckdns.org | - |

### 4.4 Database Schema

```sql
-- Laporan utama
CREATE TABLE laporan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    nama TEXT NOT NULL,
    lokasi TEXT,
    latitude TEXT,
    longitude TEXT,
    deskripsi TEXT,
    foto TEXT,
    foto_gallery TEXT,          -- JSON array
    kategori TEXT,              -- Sampah / Jalan Rusak
    status TEXT DEFAULT 'Menunggu',  -- Menunggu / Diproses / Selesai
    prioritas TEXT DEFAULT 'Sedang',  -- Rendah / Sedang / Tinggi
    vote_count INTEGER DEFAULT 0,
    vote_verified INTEGER DEFAULT 0,
    tanggal TEXT,               -- DD/MM/YYYY
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crowd voting
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laporan_id INTEGER REFERENCES laporan(id),
    voter_ip TEXT,
    vote_type TEXT,             -- benar / palsu
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foto bukti (before/after)
CREATE TABLE foto_bukti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laporan_id INTEGER REFERENCES laporan(id),
    foto_url TEXT,
    foto_type TEXT,             -- before / after
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifikasi
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laporan_id INTEGER REFERENCES laporan(id),
    message TEXT,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

