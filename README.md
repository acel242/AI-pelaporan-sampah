# 🌿 EcoLapor Wonosobo
### Sistem Pelaporan Isu Lingkungan Berbasis AI

> Platform pelaporan lingkungan cerdas untuk Kota Wonosobo — menggabungkan **AI Vision**, **Chatbot Telegram**, dan **Dashboard Web** dalam satu ekosistem terintegrasi.

---

## 🖼️ Gambaran Umum

EcoLapor memungkinkan warga melaporkan masalah lingkungan (sampah, fasilitas rusak, hewan liar, kebakaran) melalui **form web** atau **chatbot Telegram**. Sistem AI secara otomatis menganalisis foto, mengklasifikasikan kategori, menentukan prioritas, dan meneruskan ke petugas — semua **tanpa campur tangan manusia**.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Warga      │────▶│  AI Agent    │────▶│  Petugas /      │
│  (Web/Bot)  │     │  (Auto)      │     │  Admin          │
└─────────────┘     └──────────────┘     └─────────────────┘
      │                    │                      │
      │              ┌─────┴─────┐          ┌─────┴─────┐
      │              │ • Validasi │          │ • Update  │
      │              │   foto AI  │          │   status  │
      │              │ • Klasifikasi│         │ • Upload  │
      │              │   kategori │          │   foto     │
      │              │ • Prioritas│          │   sesudah  │
      │              │   otomatis │          │ • Catatan  │
      │              └───────────┘          └───────────┘
      │                    │
      ▼                    ▼
┌─────────────────────────────────────┐
│          SQLite Database            │
│     (Shared: Bot + Backend)         │
└─────────────────────────────────────┘
```

---

## ✨ Fitur Utama

### 👤 Untuk Warga
| Fitur | Deskripsi |
|-------|-----------|
| 📝 **Form Pelaporan Web** | Isi nama, lokasi, deskripsi, kategori, upload foto |
| 📸 **AI Deskripsi Otomatis** | Foto di-upload → AI otomatis generate deskripsi |
| 📍 **GPS Otomatis** | Lokasi otomatis dari browser GPS atau EXIF foto |
| 🤖 **Chatbot Telegram** | Laporkan via chat di @ecolapor_bot |
| 📋 **Cek Status Laporan** | Lihat progres: Menunggu → Diproses → Selesai |
| 🗺️ **Peta Laporan** | Lihat sebaran laporan di peta interaktif |
| 📸 **Before/After** | Lihat foto saat laporan vs foto penanganan petugas |

### 🛡️ Untuk Admin / Petugas
| Fitur | Deskripsi |
|-------|-----------|
| 📊 **Dashboard Statistik** | Total laporan, per status, per kategori, per prioritas |
| 🔄 **Update Status** | Ubah status laporan (Menunggu → Diproses → Selesai) |
| 📷 **Upload Foto Bukti** | Upload foto "sesudah" sebagai bukti penanganan |
| 🏷️ **Koreksi Kategori/Prioritas** | Override hasil AI jika kurang tepat |
| 📝 **Tambah Catatan** | Tambah catatan pada laporan |
| 🔔 **Notifikasi Realtime** | Notifikasi saat ada laporan baru atau status berubah |

### 🤖 AI Agent (Otomatis)
| Fitur | Deskripsi |
|-------|-----------|
| 🖼️ **Validasi Foto AI** | Menolak foto bukan masalah lingkungan (selfie, makanan) |
| 🏷️ **Klasifikasi Kategori** | Otomatis: Sampah, Fasilitas Rusak, Hewan Liar, Kebakaran, Lainnya |
| 🔥 **Prioritas Otomatis** | AI tentukan Rendah/Sedang/Tinggi dari deskripsi |
| 📈 **Auto-Escalate** | Laporan >3 hari → prioritas naik ke Tinggi |
| 🧠 **Self-Learning** | Mencatat koreksi admin untuk perbaikan ke depan |

---

## 🏗️ Arsitektur Sistem

```
AI-pelaporan-sampah/
├── 🤖 bot/                        # Telegram Bot + AI Agent
│   ├── main.py                    # Entry point, message handlers
│   ├── agent.py                   # LLM agent + function calling
│   ├── tools.py                   # Tool implementations
│   └── database.py                # SQLite operations
│
├── 🌐 backend/                    # Flask API Server
│   ├── server.py                  # REST API + AI validation
│   └── static/                   # Built frontend + foto files
│       ├── assets/                # JS, CSS bundles
│       └── foto/                  # Uploaded images
│
├── 💻 pelaporan-sampah/           # React Frontend (source)
│   └── src/
│       ├── pages/
│       │   ├── Warga.jsx          # Form pelaporan + daftar laporan
│       │   ├── Admin.jsx          # Dashboard admin
│       │   └── Peta.jsx           # Peta interaktif
│       ├── components/            # UI components
│       └── App.jsx                # Router + Home dashboard
│
└── 📦 pelaporan.db                # SQLite database (shared)
```

---

## 🔄 Alur Kerja

### Alur Warga (Web)
```
1. Buka eco-lapor.43.157.235.76.nip.io
2. Klik "Buat Laporan"
3. Isi form → upload foto
   ├─ AI otomatis: deskripsi dari foto
   ├─ GPS otomatis: dari browser/EXIF foto
   └─ AI validasi: cek foto relevan
4. Pilih kategori → Kirim
5. AI klasifikasi & prioritas otomatis
6. Laporan tersimpan → cek status di dashboard
```

### Alur Warga (Telegram Bot)
```
1. Chat @ecolapor_bot
2. Kirim foto + deskripsi
3. AI Agent:
   ├─ Validasi foto (AI Vision)
   ├─ Klasifikasi kategori
   ├─ Tentukan prioritas
   └─ Simpan ke database
4. Bot konfirmasi + beri ID laporan
5. Cek status: ketik "status" atau "laporan saya"
```

### Alur Admin / Petugas
```
1. Login ke dashboard admin
2. Lihat daftar laporan + statistik
3. Klik laporan → detail + foto before
4. Update status: Menunggu → Diproses → Selesai
5. Upload foto "sesudah" sebagai bukti
6. Tambah catatan jika perlu
```

---

## 🎯 Kategori Laporan

| Kategori | Icon | Contoh |
|----------|------|--------|
| 🗑️ Sampah | Tumpukan sampah, limbah, plastik, organik, B3 |
| 🔧 Fasilitas Rusak | Taman rusak, lampu mati, trotoar, jalan |
| 🐕 Hewan Liar | Hewan terlantar, sakit, berbahaya |
| 🔥 Kebakaran | Kebakaran hutan, lahan, semak |
| 📌 Lainnya | Isu lingkungan umum |

---

## 🛠️ Tech Stack

| Layer | Teknologi | Keterangan |
|-------|-----------|------------|
| **Frontend** | React 18 + Vite | SPA dengan React Router |
| **UI** | TailwindCSS + Lucide Icons | Responsive, modern design |
| **Peta** | Leaflet + OpenStreetMap | Interaktif, custom markers |
| **Backend** | Flask + Flask-CORS | REST API, port 5000 |
| **Database** | SQLite | Shared antara bot & backend |
| **Bot** | python-telegram-bot | Chatbot + AI agent |
| **AI Vision** | GPT-5.1 (SumoPod) | Validasi foto, deskripsi otomatis |
| **AI Klasifikasi** | Llama 3.1 8B (Groq) | Kategori, prioritas, sub-kategori |
| **Web Server** | Nginx | Reverse proxy + SSL (Let's Encrypt) |
| **Deployment** | VPS Ubuntu | 43.157.235.76 |

---

## 🌐 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/laporan` | Buat laporan baru |
| `GET` | `/api/laporan` | List laporan (pagination) |
| `GET` | `/api/laporan/:id` | Detail laporan + gallery |
| `GET` | `/api/laporan/:id/preview` | Preview foto (lightweight) |
| `GET` | `/api/laporan/:id/gallery` | Before/after photo gallery |
| `POST` | `/api/laporan/:id/foto` | Upload foto penanganan (after) |
| `PATCH` | `/api/laporan/:id/status` | Update status |
| `PATCH` | `/api/laporan/:id/prioritas` | Update prioritas |
| `PATCH` | `/api/laporan/:id/catatan` | Tambah catatan |
| `GET` | `/api/stats` | Statistik dashboard |
| `GET` | `/api/notifications` | Notifikasi belum dibaca |
| `POST` | `/api/agent/describe` | AI auto-describe foto |
| `POST` | `/api/agent/priority` | AI analisis prioritas |

---

## 🚀 Quick Start

### Backend + Frontend
```bash
cd AI-pelaporan-sampah
pip install -r requirements.txt
cd backend
python3 server.py    # Flask API di port 5000
```

Frontend (dev mode):
```bash
cd pelaporan-sampah
npm install
npm run dev          # Vite dev server di port 5173
```

### Telegram Bot
```bash
cd bot
cp .env.example .env
# Isi TELEGRAM_BOT_TOKEN dan GROQ_API_KEY
python3 main.py
```

---

## 📸 Screenshot Highlights

| Halaman | Fitur |
|---------|-------|
| **Home** | Statistik real-time, laporan terbaru + tombol detail |
| **Form Warga** | Upload foto → AI deskripsi + GPS otomatis |
| **Detail Laporan** | Perbandingan foto Sebelum & Sesudah side-by-side |
| **Peta** | Marker interaktif per kategori, filter warna |
| **Admin** | Full CRUD, statistik, notifikasi |
| **Telegram Bot** | AI conversation, auto-classification |

---

## 📊 Database Schema

```sql
-- Laporan utama
CREATE TABLE laporan (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    nama TEXT,
    lokasi TEXT,
    deskripsi TEXT,
    foto TEXT,                    -- URL file (sebelumnya base64)
    status TEXT DEFAULT 'Menunggu',
    prioritas TEXT DEFAULT 'Sedang',
    jenis_sampah TEXT,
    kategori TEXT DEFAULT 'Sampah',
    sub_kategori TEXT,
    latitude TEXT,
    longitude TEXT,
    catatan TEXT,
    tanggal TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Gallery before/after
CREATE TABLE report_photos (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    photo_type TEXT,              -- 'before' atau 'after'
    foto_url TEXT,
    caption TEXT,
    uploaded_at TEXT
);

-- Notifikasi
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    user_id INTEGER,
    message TEXT,
    type TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT
);

-- Self-learning koreksi
CREATE TABLE agent_corrections (
    id INTEGER PRIMARY KEY,
    laporan_id INTEGER,
    field TEXT,
    old_value TEXT,
    new_value TEXT,
    catatan TEXT,
    created_at TEXT
);
```

---

## 🔮 Roadmap

- [ ] **Notifikasi WhatsApp** — kirim update status ke warga
- [ ] **Laporan PDF** — generate laporan berkala untuk dinas
- [ ] **Multi-kota** — dukung beberapa kota/kabupaten
- [ ] **Mobile App** — React Native untuk warga
- [ ] **AI Improvement** — fine-tune dari data koreksi admin
- [ ] **Dashboard Analytics** — grafik tren bulanan/tahunan

---

## 👥 Tim

**EcoLapor Wonosobo** — Sistem Pelaporan Isu Lingkungan Berbasis AI

🟢 Live at: **https://eco-lapor.43.157.235.76.nip.io**

🤖 Telegram Bot: **@ecolapor_bot**
