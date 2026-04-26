# FORMAT PROPOSAL PROGRAM BCA

---

# COVER

## EcoLapor Wonosobo v3.0
### Platform Pelaporan Lingkungan Berbasis AI untuk Pemerintah Kabupaten Wonosobo

**Program:** Gerakan Berbakti untuk Indonesia Lebih Bersih  
**Lokasi:** Kabupaten Wonosobo, Jawa Tengah  
**Tanggal:** April 2026  
**Versi:** 3.0  
**Status:** Draft untuk Persetujuan Dinas Lingkungan Hidup Kabupaten Wonosobo  

---

# HALAMAN IDENTITAS

| Field | Detail |
|-------|--------|
| **Nama Program** | EcoLapor Wonosobo |
| **Jenis Program** | Platform Pelaporan Lingkungan Berbasis AI |
| **Lokasi Implementasi** | Kabupaten Wonosobo, Jawa Tengah |
| **Pelaksanaan Program** | 8 Juli - 6 Agustus 2026 (30 hari) |
| **Durasi Program** | 4 Minggu (Pilot) |
| **Penanggung Jawab** | Tim Pengembangan EcoLapor |
| **Versi Dokumen** | 3.0 |
| **Tanggal** | 25 April 2026 |
| **Target Beneficiaries** | Warga Wonosobo + Petugas Dinas LH |
| **Anggaran Total** | Rp 6.500.000 |

---

# RINGKASAN

EcoLapor Wonosobo adalah platform pelaporan lingkungan berbasis AI yang dirancang untuk meningkatkan efisiensi pengelolaan laporan isu lingkungan di Kabupaten Wonosobo, Jawa Tengah. Sistem ini memungkinkan warga melaporkan masalah lingkungan (sampah, jalan rusak) melalui chatbot Telegram atau formulir web, dengan procesamiento otomatis menggunakan AI untuk penentuan prioritas, kategorisasi, dan routing ke petugas terkait.

## Permasalahan Utama

| No | Permasalahan | Dampak |
|----|-------------|--------|
| 1 | Laporan lingkungan dari warga sulit di-track dan follow-up | Warga kehilangan kepercayaan terhadap pemerintah |
| 2 | Verifikasi laporan manual memakan waktu lama | Prioritas tidak tepat sasaran |
| 3 | Tidak ada sistem voting dari masyarakat | Laporan palsu/spam sulit dideteksi |
| 4 | Petugas tidak tahu lokasi laporan terdekat | Respons lambat dan tidak efisien |
| 5 | Tidak ada visualisasi data spasial | Sulit identifikasi hotspot masalah |

## Solusi yang Ditawarkan

EcoLapor Wonosobo menyediakan:
- **Chatbot Telegram (@ecolapor_bot)** — Pelaporan mudah via chat dengan AI assistance
- **Dashboard Web** — Warga melihat status, petugas mengelola laporan
- **AI Priority Engine** — Otomatisasi klasifikasi dan prioritas
- **Crowd Verification** — Validasi oleh masyarakat sekitar
- **Peta Interaktif** — Heatmap untuk identifikasi hotspot
- **Auto-Routing** — Berdasarkan lokasi ke district/kelurahan terkait

## Angka Kunci

| Metric | Nilai |
|--------|-------|
| Total Laporan | 23+ (pilot) |
| Kategori | 2 (Sampah, Jalan Rusak) |
| Wilayah Coverage | Kabupaten Wonosobo |
| Estimasi Biaya Bulanan | Rp 300.000 - 700.000 |
| Target Resolution Rate | > 80% dalam 7 hari |
| Target Waktu Respons | < 24 jam |

## Permintaan Dana

| Fase | Durasi | Estimasi Biaya |
|------|--------|----------------|
| Fase 1 (Verifikasi & Trust) | 1 minggu | Rp 1.500.000 |
| Fase 2 (AI Lanjutan) | 1 minggu | Rp 2.000.000 |
| Fase 3 (Skalabilitas) | 2 minggu | Rp 3.000.000 |
| **Total** | **4 Minggu** | **Rp 6.500.000** |

---

# BAB I ANALISIS MASALAH

## 1.1 Latar Belakang

Kabupaten Wonosobo, dengan populasi sekitar 900.000 jiwa, menghadapi tantangan signifikan dalam pengelolaan lingkungan. Sistem pelaporan konvensional yang berbasis manual (telepon, datang langsung ke kantor) menyebabkan:

1. **Waktu respons yang lambat** — Laporan butuh waktu berhari-hari untuk sampai ke petugas yang tepat
2. **Tidak ada transparansi** — Warga tidak tahu status laporan mereka setelah disubmit
3. **Data tidak terstruktur** — Laporan tersimpan dalam bentuk kertas atau chat WhatsApp yang sulit dianalisis
4. **Hotspot tidak teridentifikasi** — Tidak ada visualisasi untuk melihat area mana yang paling bermasalah

### EcoLapor Manado (Pilot Result)
- **Hasil:** 23+ laporan aktif, response time berkurang 60%
- **Lesson Learned:** AI priority engine perlu diintegrasikan sejak awal
- **Lesson Learned:** Crowd verification efektif menurunkan laporan palsu

## 1.2 Analisis Permasalahan

### Dari Sisi Warga

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak tahu caranya melaporkan | Warga tidak tahu nomor kontak Dinas LH | Tinggi |
| Tidak ada feedback setelah melapor | Submit laporan lalu tidak ada kabar | Sangat Tinggi |
| Tidak percaya laporan akan ditindaklanjuti | Pernah laporan tapi tidak ada aksi | Tinggi |
| Lokasi sulit dijelaskan | Alamat tidak jelas, GPS tidak aktif | Sedang |
| Satu masalah dilaporkan berkali-kali | warga lain juga laporkan hal sama | Sedang |

### Dari Sisi Pemerintah/Petugas

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak ada sistem pencatatan terpusat | Laporan di chat, email, telepon terpisah | Tinggi |
| Prioritas manual tidak konsisten | Semua dianggap penting atau tidak ada yang penting | Tinggi |
| Tidak tahu lokasi pasti laporan | Harus tanya ulang ke pelapor | Sedang |
| Tidak ada metric kinerja | Tidak tahu berapa laporan yang diselesaikan | Tinggi |
| Ulasan laporan memakan waktu | Petugas harus ketik satu-satu | Sedang |

## 1.3 Sistem Similar di Indonesia

| Sistem | Lembaga | Kekuatan | Kelemahan |
|--------|---------|----------|----------|
| **Lapor.go.id** | Government | Nationwide, sudah dikenal | Tidak ada AI, tidak ada geolocation |
| **Qisc回答** | Private | Focus pada infrastruktur | Tidak ada AI analysis, UI kompleks |

## 1.4 Capaian Sistem Saat Ini (v2.x)

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

---

# BAB II METODE PELAKSANAAN

## 2.1 Metode Pengumpulan Data

### Data Primer
- **Pelaporan Warga:** Via Telegram Bot atau Web Form dengan upload foto
- **GPS Location:** Via GPS from EXIF atau manual input koordinat
- **Crowd Voting:** Verifikasi dari warga sekitar lokasi

### Data Sekunder
- **Data Historik:** Laporan dari sistem sebelumnya (chat, email)
- **Peta Dasar:** OpenStreetMap untuk visualisasi
- **Regulasi:** Perda Kabupaten Wonosobo tentang pengelolaan sampah

## 2.2 Metode Analisis

### AI Priority Engine

| Model | Fungsi | Provider |
|-------|--------|----------|
| Vision Analysis | Deteksi jenis & severity dari foto | Groq (llama-3.2-11b-vision) |
| Text Classification | Kategorisasi otomatis (Sampah / Jalan Rusak) | Deepseek v4-flash |
| Priority Scoring | Z-score-like priority (Rendah / Sedang / Tinggi) | Deepseek v4-pro |

### Prioritas Scoring

| Prioritas | Kondisi | SLA |
|-----------|---------|-----|
| 🟢 Rendah | Vote < 3, foto tidak jelas | 14 hari |
| 🟡 Sedang | Default, vote >= 3 | 7 hari |
| 🔴 Tinggi | Auto-escalate >3 hari, atau >5 vote menandakan penting | 24 jam |

## 2.3 Timeline Implementasi

| Minggu | Tanggal | Aktivitas | Output |
|--------|---------|-----------|--------|
| 1 | 8-14 Juli 2026 | Setup environment, AI priority engine optimization, crowd verification tuning | Sistem stabil, AI accuracy >90% |
| 2 | 15-21 Juli 2026 | Dashboard refinement, heatmap improvement, notification system | UI/UX improvements, real-time notif |
| 3 | 22-28 Juli 2026 | Petugas training, integrasi Dinas LH, user testing | Petugas bisa operate, feedback incorporated |
| 4 | 29 Juli - 6 Agustus 2026 | Pilot evaluation, documentation, handover | System ready for scale |

## 2.4 Teknologi yang Digunakan

| Layer | Teknologi | Version |
|-------|-----------|---------|
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

## 2.5 Alur Pelaporan

```
[WARGA] → /laporkan → [BOT: lokasi?] → [BOT: foto?] → [AI analyze] → [Assign priority] → [Store DB] → [Notify petugas] → [Selesai]
```

---

# BAB III PROGRAM KERJA & RENCANA ANGGARAN

## 3.1 Rencana Pengembangan v3.0

### Fase 1 — Verifikasi & Trust (1 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| Crowd Verification | Vote benar/palsu untuk validasi laporan | Critical |
| AI Priority Engine | Scoring otomatis berdasarkan foto & text | Critical |
| Auto-Escalate | Laporan >3 hari naik prioritas | High |
| Reverse Geocoding | Koordinat → alamat readable | High |

### Fase 2 — AI Lanjutan (1 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| AI Suggest Solutions | AI memberikan saran penanganan | Medium |
| Image Before/After | Dokumentasi sebelum dan sesudah | Medium |
| Advanced Heatmap | Clustering dan filter lebih advanced | Medium |
| Export Google Maps | Export ke JSON format | Low |

### Fase 3 — Skalabilitas (2 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| Multi-Kategori | Tambah kategori: Drainase, Penerangan, dll | High |
| Mobile Optimization | Responsive untuk mobile | High |
| Notification Push | Real-time notification ke petugas | High |
| Laporan Otomatis | Generate laporan bulanan untuk Dinas | Medium |

## 3.2 Estimasi Biaya Operasional Bulanan

| Komponen | Biaya | Keterangan |
|----------|-------|------------|
| VPS Server | Rp 200.000 - 400.000 | 2 vCPU, 4GB RAM |
| Deepseek API | Rp 50.000 - 100.000 | ~500-1000 requests |
| Groq API | GRATIS | Free tier unlimited |
| Domain | GRATIS | duckdns.org |
| Cloudflare Tunnel | GRATIS | Remote access |
| SSL | GRATIS | Let's Encrypt |
| **Total** | **Rp 300.000 - 700.000/bulan** | |

## 3.3 Biaya Pengembangan

| Fase | Durasi | Biaya |
|------|--------|-------|
| Fase 1 (Verifikasi & Trust) | 1 minggu | Rp 1.500.000 |
| Fase 2 (AI Lanjutan) | 1 minggu | Rp 2.000.000 |
| Fase 3 (Skalabilitas) | 2 minggu | Rp 3.000.000 |
| **Total** | **4 Minggu** | **Rp 6.500.000** |

## 3.4 Komponen EcoLapor

| Komponen | Deskripsi |
|----------|-----------|
| Chatbot Telegram | @ecolapor_bot - pelaporan via chat |
| Dashboard Warga | Cek status, peta sebaran, form |
| Dashboard Admin | Manajemen laporan, statistik |
| AI Priority Engine | Klasifikasi dan prioritas otomatis |
| Heatmap | Visualisasi hotspot masalah |

---

# BAB IV KEBERLANJUTAN

## 4.1 Rencana Handover

Setelah masa pilot berakhir:
1. **Transfer Knowledge** — Training intensif untuk tim teknis Dinas LH
2. **Dokumentasi** — Dokumentasi lengkap sistem dalam bahasa Indonesia
3. **Source Code** — Commit ke repository dengan dokumentasi lengkap
4. **Operasi** — Tim IT Dinas LH übernimmt operasional

## 4.2 Rencana Monitoring & Evaluasi

| Aktivitas | Frekuensi | Penanggung Jawab |
|-----------|-----------|------------------|
| Review laporan masuk | Harian | Staf Dinas LH |
| Evaluasi sistem | Mingguan | Tim teknis |
| Audit keamanan | 6-bulanan | Tim IT |
| Backup database | Harian | System Admin |
| Pilot evaluation | Week 4 | Semua stakeholder |

## 4.3 Metrix Keberhasilan

| Metric | Baseline | Target | Cara Ukur |
|--------|----------|--------|-----------|
| Resolution rate | 40% | > 80% dalam 7 hari | % laporan closed on time |
| Response time | ~48 jam | < 24 jam | Avg time from submit → proses |
| User engagement | 20 laporan/bulan | > 100 laporan/bulan | Submit rate |
| AI accuracy | 85% | > 90% | Manual validation sample |
| System uptime | N/A | > 99% | Monitoring |
| Cost per report | N/A | < Rp 10.000 | Total ops cost / laporan |

## 4.4 Rencana Keberlanjutan Finansial

| Sumber Dana | Potensi |
|-------------|---------|
| Dinas Lingkungan Hidup | Budget operasional daerah |
| APBDes | Dana desa untuk lingkungan |
| CSR Perusahaan | Partnership dengan korporasi |
| Grants Nasional | KLHK, Bappenas environmental grants |

## 4.5 Pelatihan & Adaptasi Pengguna

| Peserta | Durasi | Materi |
|---------|--------|--------|
| Staf Dinas LH | 1 hari | Dashboard admin, update status |
| Operator Teknis | 2 hari | Sistem penuh, troubleshooting |
| Warga (Champion) | 1 sesi | Cara pakai Telegram bot |

### User Adoption Strategy
1. **Pilot group** — 10 warga volunteer di 1 kecamatan
2. **Social proof** — Share success story laporan yang cepat ditanggapi
3. **Incentive** — Laporan yang verified bisa dapat apresiasi
4. **Word of mouth** — Kader lingkungan promosikan ke warga

## 4.6 Maintenance & Dukungan

| Channel | Untuk | Jam Operasional |
|---------|-------|-----------------|
| Telegram Group | Staf Dinas LH | 08:00-17:00 WIB |
| WhatsApp Admin | Escalation | 24/7 untuk urgent |
| Email | Issues formal | Senin-Jumat |

### SLA

| Issue | Response Time | Resolution Time |
|-------|---------------|-----------------|
| Critical (system down) | 1 jam | 4 jam |
| High (feature broken) | 4 jam | 24 jam |
| Medium (UI bug) | 1 hari | 3 hari |
| Low (improvement) | 1 minggu | Sprint next |

## 4.7 Keamanan & Privasi Data

### Data Classification

| Data | Sensitivity | Protection |
|------|-------------|------------|
| Nama pelapor | Medium | Only visible to petugas |
| Lokasi laporan | Medium | Shown publicly on map (generalized) |
| Foto bukti | Medium | Public on dashboard |
| No. HP | High | Only visible to petugas, encrypted |

### Access Control

```
Warga
  └── Submit laporan
  └── Cek status laporan sendiri
  └── Vote verifikasi

Staf Dinas LH
  └── View semua laporan
  └── Update status
  └── Upload foto bukti
  └── Export laporan

Admin
  └── Full access
  └── Manage users
  └── System settings
```

---

# BAB V PENUTUP

## 5.1 Kesimpulan

EcoLapor Wonosobo v3.0 adalah solusi komprehensif untuk masalah pelaporan lingkungan dengan fitur:

✅ **AI Priority Engine** — Klasifikasi dan prioritas otomatis
✅ **Crowd Verification** — Validasi oleh warga sekitar
✅ **Real-time Dashboard** — Transparansi status untuk warga
✅ **Heatmap Visualization** — Identifikasi hotspot masalah
✅ **Cost-Effective** — Hanya Rp 300-700K/bulan
✅ **Scalable** — Bisa di-extend ke kategori dan wilayah lain

## 5.2 Rekomendasi

1. **Approve pilot project** — Mulai 4 minggu di 1 kecamatan pilot
2. **Alokasikan budget** — Rp 6.500.000 untuk development
3. **Tunjuk counterpart** — Satu staff Dinas sebagai联络人
4. **Pilot evaluation** — Review setelah 4 minggu

## 5.3 Langkah Selanjutnya

| Aksi | Penanggung Jawab | Deadline |
|------|------------------|----------|
| Review proposal | Dinas LH | 1 minggu |
| Approve budget | Kepala Dinas | 2 minggu |
| Kickoff meeting | Semua stakeholder | 3 minggu |
| Dev start | Tim teknis | 4 minggu |

---

# LAMPIRAN

## A. Link Sistem Berjalan

- Backend API: http://localhost:5002
- Dashboard: eco-lapor.duckdns.org
- Telegram Bot: @ecolapor_bot

## B. Referensi Teknis

| Resource| Resource | Link |
|----------|------|
| Groq API | https://console.groq.com |
| Deepseek API | https://platform.deepseek.com |
| React Documentation | https://react.dev |
| Flask Documentation | https://flask.palletsprojects.com |
| Leaflet Documentation | https://leafletjs.com |
| Python Telegram Bot | https://python-telegram-bot.org |

## C. Database Schema

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
    foto_gallery TEXT,
    kategori TEXT,
    status TEXT DEFAULT 'Menunggu',
    prioritas TEXT DEFAULT 'Sedang',
    vote_count INTEGER DEFAULT 0,
    vote_verified INTEGER DEFAULT 0,
    tanggal TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crowd voting
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laporan_id INTEGER REFERENCES laporan(id),
    voter_ip TEXT,
    vote_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foto bukti
CREATE TABLE foto_bukti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laporan_id INTEGER REFERENCES laporan(id),
    foto_url TEXT,
    foto_type TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## D. Arsitektur Sistem

```
                         ┌───────────────────────────────────────┐
                         │           EXTERNAL SERVICES            │
                         │  • Telegram Bot API                   │
                         │  • Deepseek API (AI Chat)             │
                         │  • Groq API (Vision AI)              │
                         │  • OpenStreetMap                     │
                         └───────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Flask)                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  REST API   │  │  AI Engine │  │  File Store │  │  Database   │     │
│  │  /api/*     │  │  Priority  │  │  /static    │  │  (SQLite)   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                           │
                    ▼                                           ▼
┌─────────────────────────────┐       ┌─────────────────────────────────────┐
│     TELEGRAM BOT            │       │         FRONTEND (React)             │
│  • Message Handler          │       │  • Dashboard Warga                    │
│  • Photo Handler           │       │  • Dashboard Admin/Petugas          │
│  • Conversation Flow        │       │  • Interactive Map (Leaflet)         │
│  • Inline Buttons           │       │  • Heatmap Visualization             │
└─────────────────────────────┘       └─────────────────────────────────────┘
```

## E. Glossary

| Term | Definition |
|------|------------|
| EcoLapor | Sistem pelaporan lingkungan berbasis AI |
| Crowd Verification | Validasi oleh masyarakat sekitar |
| Heatmap | Visualisasi densitas laporan per wilayah |
| Auto-Escalate | Naik prioritas otomatis jika lama tidak ditanggapi |
| Priority Scoring | Penentuan prioritas otomatis oleh AI |

## F. Kontak

| Peran | Nama | Kontak |
|-------|------|--------|
| Project Lead | (TBD) | - |
| Technical Lead | (TBD) | - |
| Dinas LH Wonosobo | (TBD) | - |

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem EcoLapor Wonosobo v3.0*
*Versi: 3.0 | Tanggal: 25 April 2026*
*Disusun untuk: Dinas Lingkungan Hidup Kabupaten Wonosobo*
