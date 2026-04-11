# Dokumentasi Proyek: Prototipe Aplikasi Pelaporan Sampah

## Deskripsi
Aplikasi web prototipe yang berfungsi sebagai sistem informasi bagi warga untuk melaporkan insiden/tumpukan sampah liar di lingkungannya. Proyek ini dibuat untuk tujuan uji coba konsep dan demonstrasi UI/UX, sehingga dirancang sepenuhnya berjalan pada sisi _frontend_ (Client-side) tanpa memerlukan backend server atau database.

## Teknologi Utama
- **React.js**: Library fungsional untuk antarmuka pengguna berbasis komponen modular.
- **Vite**: _Build tool_ yang ringan dan dioptimasi super cepat untuk proyek React modern.
- **Tailwind CSS v4**: _Utility-first CSS framework_ untuk memastikan permodelan elemen tata letak responsif, bersih (clean), dan estetik.
- **React Router v6**: Menangani navigasi mulus (_routing_) antar halaman tanpa me-_reload_ halaman secara keseluruhan (_Single Page Application_).
- **Lucide React**: Library ikon berbasis komponen responsif.

## Struktur Berkas Pendukung (File Tree)
```text
pelaporan-sampah/
├── src/
│   ├── components/
│   │   ├── Button.jsx   - Komponen tombol generik re-usable
│   │   ├── Card.jsx     - Wrapper konten berbentuk kartu yang dimodifikasi khusus
│   │   └── Input.jsx    - Komponen peritah spesifik yang mampu menangani input teks dan area blok (textarea)
│   ├── pages/
│   │   ├── Admin.jsx    - Endpoint layout bagi Admin dalam melihat daftar statistik dan rincian riwayat laporan terbaru
│   │   ├── Login.jsx    - Portal login dummy 
│   │   └── Warga.jsx    - Halaman reaktif pendukung input/form entry warga. 
│   ├── App.jsx          - Merupakan modul router utama sekaligus tempat di mana pengelolaan _state_ dummy global `laporan` & status identitas sesi berjalan.
│   ├── index.css        - Target injeksi syntax Tailwind CSS v4.
│   └── main.jsx         - Titik entri React dasar, menampung `BrowserRouter`.
├── package.json         - Deklarasi versi dependensi package npm.
├── index.html           - Kerangka dom HTML inti.
└── vite.config.js       - Konfigurasi bundler Vite termasuk plugin khusus fitur @tailwindcss/vite.
```

## Fitur dan Fungsionalitas
### 1. Fungsionalitas Authentication (Dummy)
Identitas pengguna disimulasikan menggunakan pengaturan _React State_ bernama `userRole` di elemen penampung utama (`App.jsx`). Apabila pengguna sedang dalam keadaan ter-logout, *protective routing constraint* dapat memaksakan arah balik (`navigate('/')`).

### 2. Mode Warga (Warga User Flow)
- **Portal Entry Terstruktur**: Mengumpulkan infomasi wajib seperti Nama Pelapor, Titik Lokasi Kejadian, dan Deskripsi Detail insiden.
- **Panel Mock-up Gambar (Visual Upload)**: Representatif file upload bergaya _drag-and-drop_ area yang disediakan secara eksklusif mewakili UI asli.
- **Feedback Berjangka**: Adanya notifikasi sukses reaktif (alert informatif hijau) yang otomatis menonaktifkan visibilitas diri sesudah beberapa detik.

### 3. Mode Admin (Admin Dashboard View)
- **Statistik Dinamis (Overview Stats)**: Menyediakan statistik rekapan atas properti array laporan aktif secara otomatis tanpa referesh.
- **Grid Laporan Transparan**: Entitas rekam jejak input dari komponen warga langsung tercetak reaktif dalam format daftar *Cards* di bawah area indikator di samping lencana (*badges*) berisi parameter label `Menunggu` atau `Selesai`.

## Cara Menjalankan Aplikasi
Buka _Command Prompt_ (Terminal) Anda pada direktori _root_ (`pelaporan-sampah`). Lakukan instruksi berikut secara berurutan:
1. Pemasangan dependansi utama:
   ```bash
   npm install
   ```
2. Jalankan _development server_:
   ```bash
   npm run dev
   ```
3. Akses tautan alamat `http://localhost:5173/` pada *web browser* (mis. Chrome/Firefox) di perangkat Anda.
