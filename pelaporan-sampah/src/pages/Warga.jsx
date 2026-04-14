import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { CheckCircle2, UploadCloud, X, Trash2, Camera, MapPin, Clock, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE = '/api';

const KATEGORI_LIST = [
  { value: 'Sampah', label: 'Sampah', icon: '🗑️' },
  { value: 'Banjir', label: 'Banjir/Drainase', icon: '🌊' },
  { value: 'Pencemaran Air', label: 'Pencemaran Air', icon: '💧' },
  { value: 'Pencemaran Udara', label: 'Pencemaran Udara', icon: '🌫️' },
  { value: 'Fasilitas Rusak', label: 'Fasilitas Rusak', icon: '🔧' },
  { value: 'Hewan Liar', label: 'Hewan Liar', icon: '🐕' },
  { value: 'Pohon Bahaya', label: 'Pohon Bahaya', icon: '🌳' },
  { value: 'Kebakaran', label: 'Kebakaran', icon: '🔥' },
  { value: 'Lainnya', label: 'Lainnya', icon: '📌' },
];

function resolveImgSrc(val) {
  if (!val) return null;
  if (val.startsWith('data:')) return val;
  if (val.startsWith('/')) return 'https://eco-lapor.43.157.235.76.nip.io' + val;
  return null;
}

export function Warga() {
  const [formData, setFormData] = useState({ nama: '', lokasi: '', deskripsi: '', kategori: 'Sampah' });
  const [foto, setFoto] = useState(null);
  const [fotoPreview, setFotoPreview] = useState(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reportId, setReportId] = useState(null);
  const [submitError, setSubmitError] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [exifData, setExifData] = useState(null);
  const [deskripsiOtomatis, setDeskripsiOtomatis] = useState(false);
  const [myReports, setMyReports] = useState([]);
  const [loadingReports, setLoadingReports] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({ page: 1, per_page: 5, total: 0, total_pages: 1 });
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const processPhoto = async (file) => {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { alert('File terlalu besar. Maksimal 5MB.'); return; }
    if (!file.type.startsWith('image/')) { alert('Hanya file gambar yang diizinkan.'); return; }

    setFoto(file);
    setDeskripsiOtomatis(false);
    setExifData(null);

    const reader = new FileReader();
    reader.onload = async (e) => {
      setFotoPreview(e.target.result);

      // 1. Extract EXIF GPS
      try {
        const exifr = (await import('exifr')).default;
        const exif = await exifr.parse(e.target.result, {
          gps: true,
          pick: ['latitude', 'longitude', 'DateTimeOriginal', 'CreateDate', 'timestamp']
        });
        if (exif && (exif.latitude || exif.longitude)) {
          const lokasiString = `${exif.latitude.toFixed(6)}, ${exif.longitude.toFixed(6)}`;
          setExifData({ lat: exif.latitude, lon: exif.longitude, timestamp: exif.DateTimeOriginal || exif.CreateDate || null, lokasiString });
          // Try reverse geocode
          try {
            const geoRes = await fetch(`${API_BASE}/geocode/reverse?lat=${exif.latitude}&lon=${exif.longitude}`);
            const geoData = await geoRes.json();
            if (geoData.location) {
              setFormData(prev => ({ ...prev, lokasi: geoData.location }));
            } else {
              setFormData(prev => ({ ...prev, lokasi: lokasiString }));
            }
          } catch (geoErr) {
            setFormData(prev => ({ ...prev, lokasi: lokasiString }));
          }
        }
      } catch (exifErr) {
        console.warn('EXIF extraction failed:', exifErr.message);
      }

      // 2. AI auto-describe
      setIsAnalyzing(true);
      try {
        const res = await fetch(`${API_BASE}/agent/describe`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: e.target.result })
        });
        const data = await res.json();
        if (data.success && data.description) {
          setFormData(prev => ({ ...prev, deskripsi: data.description }));
          setDeskripsiOtomatis(true);
        }
      } catch (aiErr) {
        console.warn('AI description failed:', aiErr.message);
      } finally {
        setIsAnalyzing(false);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => { e.preventDefault(); setIsDragging(false); processPhoto(e.dataTransfer.files[0]); };
  const handleRemoveFoto = () => { setFoto(null); setFotoPreview(null); setExifData(null); setDeskripsiOtomatis(false); if (fileInputRef.current) fileInputRef.current.value = ''; };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.nama) { alert('Mohon isi nama pelapor.'); return; }
    if (!fotoPreview) { alert('Mohon upload foto.'); return; }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/laporan`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nama: formData.nama, lokasi: formData.lokasi, deskripsi: formData.deskripsi,
          foto: fotoPreview, user_id: null, kategori: formData.kategori,
          exif_lat: exifData?.lat || null, exif_lon: exifData?.lon || null,
          exif_timestamp: exifData?.timestamp || null
        })
      });
      const data = await res.json();
      if (data.success) {
        setReportId(data.id);
        setIsSuccess(true);
        setFormData({ nama: '', lokasi: '', deskripsi: '', kategori: 'Sampah' });
        setExifData(null);
        setDeskripsiOtomatis(false);
        handleRemoveFoto();
        setTimeout(() => navigate('/'), 2000);
      } else {
        setSubmitError(data.reason || data.error || 'Gagal mengirim laporan');
        setTimeout(() => setSubmitError(null), 10000);
      }
    } catch (err) {
      alert('Terjadi kesalahan saat mengirim laporan.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Fetch reports with pagination
  const fetchReports = useCallback((p = 1) => {
    setLoadingReports(true);
    fetch(`${API_BASE}/laporan?page=${p}`)
      .then(r => r.json())
      .then(d => {
        setMyReports(d.laporan || []);
        setPagination(d.pagination || { page: 1, per_page: 5, total: 0, total_pages: 1 });
      })
      .catch(console.error)
      .finally(() => setLoadingReports(false));
  }, []);

  useEffect(() => { fetchReports(page); }, [page, fetchReports]);
  useEffect(() => { if (reportId) fetchReports(1); }, [reportId, fetchReports]);

  const statusColor = (s) => {
    if (s === 'Menunggu') return 'bg-amber-100 text-amber-700';
    if (s === 'Diproses') return 'bg-blue-100 text-blue-700';
    return 'bg-green-100 text-green-700';
  };

  const kategoriIcon = (k) => KATEGORI_LIST.find(c => c.value === k)?.icon || '📌';

  return (
    <div className="max-w-2xl mx-auto space-y-8 pb-12 pt-8">
      <div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Form Pelaporan</h2>
        <p className="text-slate-500 mt-2 font-medium">Laporkan isu lingkungan di sekitar Anda.</p>
      </div>

      {submitError && (
        <div className="bg-red-50 text-red-800 p-4 rounded-xl flex items-start gap-3 border border-red-200">
          <X className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div><span className="font-bold block">Laporan ditolak</span><span className="text-sm opacity-80">{submitError}</span></div>
        </div>
      )}

      {isSuccess && (
        <div className="bg-green-50 text-green-800 p-4 rounded-xl flex items-center gap-3 border border-green-200">
          <CheckCircle2 className="text-green-600 flex-shrink-0" size={20} />
          <div><span className="font-bold block">Laporan berhasil dikirim!</span><span className="text-sm opacity-80">ID Laporan: #{reportId}</span></div>
        </div>
      )}

      <Card className="p-6 md:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input label="Nama Lengkap" placeholder="Masukkan nama Anda" value={formData.nama} onChange={(e) => setFormData({...formData, nama: e.target.value})} required />

          {/* Kategori Selection */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-700">Kategori Laporan</label>
            <div className="grid grid-cols-3 gap-2">
              {KATEGORI_LIST.map(k => (
                <button key={k.value} type="button" onClick={() => setFormData({...formData, kategori: k.value})}
                  className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer border ${
                    formData.kategori === k.value
                      ? 'bg-green-50 border-green-400 text-green-700 ring-1 ring-green-400'
                      : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}>
                  <span>{k.icon}</span>
                  <span className="truncate">{k.label}</span>
                </button>
              ))}
            </div>
          </div>

          <Input
            label={<span className="flex items-center gap-2">Lokasi Kejadian {exifData && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">📍 dari GPS foto</span>}</span>}
            placeholder="Contoh: Jl. Melati Gg. 2, Pasar Rebo (opsional jika upload foto dengan GPS)"
            value={formData.lokasi}
            onChange={(e) => setFormData({...formData, lokasi: e.target.value})}
          />
          <Input
            type="textarea"
            label={<span className="flex items-center gap-2">Deskripsi Detail {deskripsiOtomatis && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">✨ Otomatis dari AI</span>}</span>}
            placeholder="Jelaskan kondisi secara detail (opsional — auto dari AI jika upload foto)..."
            value={formData.deskripsi}
            onChange={(e) => { setFormData({...formData, deskripsi: e.target.value}); setDeskripsiOtomatis(false); }}
          />

          {/* Photo Upload */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-700">
              Dokumentasi <span className="text-slate-400 font-normal">(📍 GPS & ✨ deskripsi otomatis dari foto)</span>
            </label>
            {fotoPreview ? (
              <div className="relative rounded-xl overflow-hidden bg-slate-100">
                <img src={fotoPreview} alt="Preview" className="w-full h-48 object-cover" />
                <button type="button" onClick={handleRemoveFoto} className="absolute top-2 right-2 p-1.5 bg-black/60 hover:bg-black/80 text-white rounded-full transition-colors cursor-pointer"><X size={16} /></button>
                <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/60 text-white text-xs rounded-md flex items-center gap-1">
                  {foto?.name} {isAnalyzing && <span className="animate-pulse ml-1">• menganalisis...</span>}
                </div>
                {exifData && (
                  <div className="absolute top-2 left-2 px-2 py-1 bg-green-600/90 text-white text-xs rounded-md">
                    📍 {exifData.lokasiString}
                    {exifData.timestamp && <span className="ml-1">• {new Date(exifData.timestamp).toLocaleString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>}
                  </div>
                )}
              </div>
            ) : (
              <div onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }} onDragLeave={() => setIsDragging(false)} onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`w-full border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${isDragging ? 'border-blue-400 bg-blue-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}`}>
                <div className={`p-3 rounded-full mb-3 transition-colors ${isDragging ? 'bg-blue-100' : 'bg-slate-100'}`}>
                  <UploadCloud size={28} className={isDragging ? 'text-blue-500' : 'text-slate-400'} />
                </div>
                <p className="text-sm font-semibold text-slate-700 mb-1">{isDragging ? 'Lepaskan file di sini' : 'Seret foto di sini'}</p>
                <p className="text-xs text-slate-400">JPG, PNG, WEBP — Maks 5MB</p>
                <p className="text-xs text-blue-500 mt-1">📍 GPS otomatis • ✨ Deskripsi AI</p>
                <div className="flex gap-3 mt-4">
                  <button type="button" onClick={(e) => { e.stopPropagation(); const input = document.createElement('input'); input.type = 'file'; input.accept = 'image/*'; input.capture = 'environment'; input.onchange = (ev) => { if (ev.target.files[0]) processPhoto(ev.target.files[0]); }; input.click(); }}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-xl transition-colors cursor-pointer"><Camera size={16} />Ambil Foto</button>
                  <button type="button" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold rounded-xl transition-colors cursor-pointer"><UploadCloud size={16} />Galeri</button>
                </div>
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={(e) => processPhoto(e.target.files[0])} />
              </div>
            )}
          </div>

          <Button type="submit" disabled={isSubmitting || isAnalyzing} className="w-full">
            {isSubmitting ? 'Mengirim...' : isAnalyzing ? 'Menganalisis foto...' : 'Kirim Laporan'}
          </Button>
        </form>
      </Card>

      {/* Laporan Saya with Pagination */}
      <div>
        <h3 className="text-xl font-bold text-slate-900 mb-4">📋 Laporan Terbaru</h3>

        {/* Detail Modal */}
        {selectedItem && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white rounded-t-2xl border-b border-slate-100 p-6 flex items-center justify-between">
                <h3 className="text-xl font-bold text-slate-900">Laporan #{selectedItem.id}</h3>
                <button onClick={() => setSelectedItem(null)} className="p-2 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer"><X size={20} className="text-slate-500" /></button>
              </div>
              <div className="p-6 space-y-4">
                {selectedItem.foto && (() => { const src = resolveImgSrc(selectedItem.foto); return src ? <img src={src} alt="Dokumentasi" className="w-full rounded-xl object-contain max-h-64 bg-slate-100" onError={e => { e.target.style.display='none'; }} /> : null; })()}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Status</p><p className="font-bold text-slate-700">{selectedItem.status}</p></div>
                  <div className="bg-slate-50 rounded-xl p-4"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Kategori</p><p className="font-bold text-slate-700">{kategoriIcon(selectedItem.kategori)} {selectedItem.kategori || 'Sampah'}</p></div>
                  <div className="bg-slate-50 rounded-xl p-4"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Prioritas</p><p className="font-bold text-slate-700">{selectedItem.prioritas || '-'}</p></div>
                  <div className="bg-slate-50 rounded-xl p-4"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Tanggal</p><p className="font-bold text-slate-700">{selectedItem.tanggal}</p></div>
                </div>
                <div className="flex items-start gap-3"><MapPin size={18} className="text-rose-500 mt-0.5 flex-shrink-0" /><div><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Lokasi</p><p className="text-slate-700 font-medium">{selectedItem.lokasi}</p></div></div>
                <div className="flex items-start gap-3"><Clock size={18} className="text-blue-500 mt-0.5 flex-shrink-0" /><div><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Deskripsi</p><p className="text-slate-700 font-medium">{selectedItem.deskripsi}</p></div></div>
              </div>
              <div className="sticky bottom-0 bg-white rounded-b-2xl border-t border-slate-100 p-6">
                <button onClick={() => setSelectedItem(null)} className="w-full py-3 rounded-xl font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors cursor-pointer">Tutup</button>
              </div>
            </div>
          </div>
        )}

        {loadingReports ? (
          <div className="text-center py-8 text-slate-400">Memuat...</div>
        ) : myReports.length === 0 ? (
          <div className="text-center py-8 text-slate-400 bg-white rounded-xl p-6 border border-slate-100">
            <p className="font-medium">Belum ada laporan.</p>
            <p className="text-sm mt-1">Isi form di atas untuk membuat laporan pertama Anda.</p>
          </div>
        ) : (
          <>
            <div className="space-y-3">
              {myReports.map(item => (
                <div key={item.id} onClick={async () => { try { const res = await fetch(`/api/laporan/${item.id}/preview`); const data = await res.json(); setSelectedItem({ ...item, foto: data.foto }); } catch(e) { setSelectedItem(item); } }}
                  className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 flex items-start gap-4 cursor-pointer hover:shadow-md transition-shadow">
                  {item.foto_exists ? (
                    <div className="p-2 bg-green-50 rounded-lg flex-shrink-0"><Camera size={20} className="text-green-600" /></div>
                  ) : (
                    <div className="p-2 bg-slate-50 rounded-lg flex-shrink-0"><Trash2 size={20} className="text-slate-400" /></div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-slate-800">#{item.id} — {item.lokasi}</p>
                    <p className="text-sm text-slate-500 mt-0.5 line-clamp-1">{item.deskripsi}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {item.tanggal}
                      {item.kategori && <span className="ml-2">• {kategoriIcon(item.kategori)} {item.kategori}</span>}
                      {item.prioritas && <span className="ml-2">• {item.prioritas}</span>}
                    </p>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${statusColor(item.status)}`}>{item.status}</span>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}
                  className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer">
                  <ChevronLeft size={18} />
                </button>
                <span className="text-sm text-slate-600 font-medium">
                  Hal {page} dari {pagination.total_pages}
                </span>
                <button onClick={() => setPage(p => Math.min(pagination.total_pages, p + 1))} disabled={page >= pagination.total_pages}
                  className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer">
                  <ChevronRight size={18} />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
