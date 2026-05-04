import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Card } from '../components/Card';
import { MapPin, Clock, FileText, CheckCircle2, X, Eye, Search, AlertTriangle, RefreshCw, BarChart3, ChevronDown, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const API_BASE = '/api';

const KATEGORI_LIST = [
  { value: 'Semua', label: 'Semua', icon: '📋' },
  { value: 'Sampah', label: 'Sampah', icon: '🗑️' },
  { value: 'Fasilitas Rusak', label: 'Fasilitas Rusak', icon: '🔧' },
  { value: 'Hewan Liar', label: 'Hewan Liar', icon: '🐕' },
  { value: 'Kebakaran', label: 'Kebakaran', icon: '🔥' },
  { value: 'Lainnya', label: 'Lainnya', icon: '📌' },
];

function resolveImgSrc(val) {
  if (!val) return null;
  if (val.startsWith('data:')) return val;
  if (val.startsWith('/')) return window.location.origin + val;
  return null;
}

function DetailModal({ item, onClose, onRefresh }) {
  if (!item) return null;
  const [catatan, setCatatan] = useState(item.catatan || '');
  const [prioritas, setPrioritas] = useState(item.prioritas);
  const [saving, setSaving] = useState(false);
  const [gallery, setGallery] = useState([]);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const miniMapRef = useRef(null);
  const miniMapInstanceRef = useRef(null);

  // Parse coords from lokasi
  const parseCoords = (lokasi) => {
    if (!lokasi) return null;
    const parts = lokasi.split(',').map(s => parseFloat(s.trim()));
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1]) && Math.abs(parts[0]) <= 90 && Math.abs(parts[1]) <= 180) {
      return { lat: parts[0], lng: parts[1] };
    }
    return null;
  };
  const coords = parseCoords(item.lokasi);

  // Fetch gallery
  useEffect(() => {
    fetch(`${API_BASE}/laporan/${item.id}/gallery`).then(r => r.json()).then(d => setGallery(d.photos || [])).catch(() => {});
  }, [item.id]);

  // Mini map
  useEffect(() => {
    if (!coords || !miniMapRef.current || miniMapInstanceRef.current) return;
    import('leaflet').then(L => {
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });
      const map = L.map(miniMapRef.current).setView([coords.lat, coords.lng], 16);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map);
      L.marker([coords.lat, coords.lng]).addTo(map).bindPopup(`<b>${item.nama}</b><br>${item.lokasi}`).openPopup();
      miniMapInstanceRef.current = map;
      // Invalidate size after modal renders
      setTimeout(() => map.invalidateSize(), 200);
    });
    return () => { if (miniMapInstanceRef.current) { miniMapInstanceRef.current.remove(); miniMapInstanceRef.current = null; } };
  }, [coords]);

  const handleUploadAfter = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadingPhoto(true);
    const reader = new FileReader();
    reader.onload = async (ev) => {
      try {
        const res = await fetch(`${API_BASE}/laporan/${item.id}/gallery`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ foto: ev.target.result, photo_type: 'after', caption: 'Foto penanganan' })
        });
        if (res.ok) {
          const d = await res.json();
          setGallery(prev => [...prev, { id: d.id, foto_url: d.foto_url, photo_type: 'after', caption: 'Foto penanganan', uploaded_at: new Date().toISOString() }]);
          onRefresh();
        }
      } finally { setUploadingPhoto(false); }
    };
    reader.readAsDataURL(file);
  };

  const handleStatusUpdate = async (newStatus) => {
    setSaving(true);
    try { const res = await fetch(`${API_BASE}/laporan/${item.id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: newStatus }) }); if (res.ok) { onRefresh(); onClose(); } } finally { setSaving(false); }
  };
  const handlePriorityUpdate = async (newPriority) => {
    setSaving(true);
    try { const res = await fetch(`${API_BASE}/laporan/${item.id}/prioritas`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prioritas: newPriority }) }); if (res.ok) { setPrioritas(newPriority); onRefresh(); } } finally { setSaving(false); }
  };
  const handleCatatanSave = async () => {
    setSaving(true);
    try { const res = await fetch(`${API_BASE}/laporan/${item.id}/catatan`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ catatan }) }); if (res.ok) onRefresh(); } finally { setSaving(false); }
  };
  const handleDelete = async () => {
    if (!window.confirm(`Hapus laporan #${item.id}?`)) return;
    setSaving(true);
    try { const res = await fetch(`${API_BASE}/laporan/${item.id}`, { method: 'DELETE' }); if (res.ok) { onRefresh(); onClose(); } } finally { setSaving(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-100 p-6 flex items-start justify-between gap-4 z-10">
          <div>
            <h3 className="text-xl font-bold text-slate-900">{item.nama}</h3>
            <p className="text-sm text-slate-500 mt-1">ID: #{item.id} • {KATEGORI_LIST.find(k => k.value === item.kategori)?.icon || '📌'} {item.kategori || 'Sampah'}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors cursor-pointer"><X size={20} className="text-slate-500" /></button>
        </div>
        <div className="p-6 space-y-5">
          <div className="flex flex-wrap gap-2">
            <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${item.status === 'Menunggu' ? 'bg-amber-100 text-amber-700' : item.status === 'Diproses' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>{item.status}</span>
            <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${prioritas === 'Tinggi' ? 'bg-red-100 text-red-700' : prioritas === 'Sedang' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>Prioritas {prioritas}</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded-xl p-4"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Tanggal</p><p className="text-slate-700 font-bold">{item.tanggal}</p></div>
            <div className="bg-slate-50 rounded-xl p-4"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Kategori</p><p className="text-slate-700 font-bold">{KATEGORI_LIST.find(k => k.value === item.kategori)?.icon || '📌'} {item.kategori || 'Sampah'}</p></div>
          </div>
          <div className="flex items-start gap-3"><MapPin size={18} className="text-rose-500 mt-0.5 flex-shrink-0" /><div><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Lokasi</p><p className="text-slate-700 font-medium">{item.lokasi}</p></div></div>

          {/* Mini Map */}
          {coords && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-2">📍 Lokasi di Peta</p>
              <div ref={miniMapRef} className="w-full h-48 rounded-xl overflow-hidden border border-slate-200" style={{zIndex: 0}} />
            </div>
          )}
          {!coords && (
            <div className="bg-slate-50 rounded-xl p-4 text-center">
              <p className="text-sm text-slate-400">Lokasi tidak memiliki koordinat GPS</p>
              <p className="text-xs text-slate-300 mt-1">Upload foto dengan GPS aktif agar lokasi muncul di peta</p>
            </div>
          )}
          <div><p className="text-xs font-semibold text-slate-400 uppercase mb-2">Deskripsi</p><p className="text-slate-600 leading-relaxed">{item.deskripsi}</p></div>
          {item.foto && (() => { const src = resolveImgSrc(item.foto); return src ? <div><p className="text-xs font-semibold text-slate-400 uppercase mb-2">Foto Sebelum (Laporan)</p><img src={src} alt="Dokumentasi" className="w-full h-48 object-cover rounded-xl bg-slate-100" onError={e => { e.target.style.display='none'; }} /></div> : null; })()}

          {/* Gallery: Before/After */}
          {(gallery.length > 0 || item.status !== 'Menunggu') && (
            <div className="space-y-3">
              <p className="text-xs font-semibold text-slate-400 uppercase">Galeri Before/After</p>
              {gallery.length > 0 && (
                <div className="grid grid-cols-2 gap-3">
                  {gallery.map(g => (
                    <div key={g.id} className="relative rounded-xl overflow-hidden bg-slate-100">
                      <img src={g.foto_url?.startsWith('/') ? window.location.origin + g.foto_url : g.foto_url} alt={g.photo_type} className="w-full h-32 object-cover" onError={e => { e.target.style.display='none'; }} />
                      <span className={`absolute bottom-1 left-1 px-2 py-0.5 rounded text-xs font-bold text-white ${g.photo_type === 'before' ? 'bg-amber-500' : 'bg-green-500'}`}>{g.photo_type === 'before' ? '📷 Sebelum' : '✅ Sesudah'}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Upload After Photo */}
              {item.status !== 'Menunggu' && (
                <div>
                  <label className="flex items-center justify-center gap-2 px-4 py-3 bg-green-50 border border-green-200 border-dashed rounded-xl text-sm font-medium text-green-700 hover:bg-green-100 cursor-pointer transition-colors">
                    <span>{uploadingPhoto ? 'Uploading...' : '+ Upload Foto Penanganan (After)'}</span>
                    <input type="file" accept="image/*" className="hidden" onChange={handleUploadAfter} disabled={uploadingPhoto} />
                  </label>
                </div>
              )}
            </div>
          )}

          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase">Ubah Prioritas</p>
            <div className="flex gap-2">
              {['Tinggi', 'Sedang', 'Rendah'].map(p => (
                <button key={p} onClick={() => handlePriorityUpdate(p)} disabled={saving || prioritas === p}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold transition-colors cursor-pointer ${prioritas === p ? p === 'Tinggi' ? 'bg-red-500 text-white' : p === 'Sedang' ? 'bg-amber-500 text-white' : 'bg-green-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>{p}</button>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase">Catatan</p>
            <div className="flex gap-2">
              <input type="text" value={catatan} onChange={(e) => setCatatan(e.target.value)} placeholder="Tambahkan catatan..." className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <button onClick={handleCatatanSave} disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 cursor-pointer disabled:opacity-50">Simpan</button>
            </div>
          </div>
        </div>
        <div className="sticky bottom-0 bg-white border-t border-slate-100 p-6 flex flex-wrap gap-3">
          {item.status === 'Menunggu' && (<>
            <button onClick={() => handleStatusUpdate('Diproses')} disabled={saving} className="flex-1 min-w-[140px] flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 cursor-pointer disabled:opacity-50"><RefreshCw size={16} />Proses</button>
            <button onClick={() => handleStatusUpdate('Selesai')} disabled={saving} className="flex-1 min-w-[140px] flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 cursor-pointer disabled:opacity-50"><CheckCircle2 size={16} />Selesai</button>
          </>)}
          {item.status === 'Diproses' && <button onClick={() => handleStatusUpdate('Selesai')} disabled={saving} className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 cursor-pointer disabled:opacity-50"><CheckCircle2 size={16} />Selesai</button>}
          <button onClick={handleDelete} disabled={saving} className="flex items-center gap-2 px-5 py-3 rounded-xl font-semibold bg-red-600 text-white hover:bg-red-700 cursor-pointer disabled:opacity-50"><Trash2 size={16} />Hapus</button>
          <button onClick={onClose} className="px-6 py-3 rounded-xl font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer">Tutup</button>
        </div>
      </div>
    </div>
  );
}

export function Admin() {
  const [laporan, setLaporan] = useState([]);
  const [stats, setStats] = useState({ total: 0, by_status: {}, by_priority: {}, by_category: {} });
  const [selectedItem, setSelectedItem] = useState(null);
  const [filterStatus, setFilterStatus] = useState('Semua');
  const [filterKategori, setFilterKategori] = useState('Semua');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({ page: 1, per_page: 5, total: 0, total_pages: 1 });

  const fetchData = useCallback(async (p = 1) => {
    try {
      const params = new URLSearchParams();
      if (filterStatus !== 'Semua') params.set('status', filterStatus);
      if (filterKategori !== 'Semua') params.set('kategori', filterKategori);
      if (searchQuery) params.set('search', searchQuery);
      params.set('page', p);
      const [laporanRes, statsRes] = await Promise.all([fetch(`${API_BASE}/laporan?${params}`), fetch(`${API_BASE}/stats`)]);
      const laporanData = await laporanRes.json();
      const statsData = await statsRes.json();
      setLaporan(laporanData.laporan || []);
      setPagination(laporanData.pagination || { page: 1, per_page: 5, total: 0, total_pages: 1 });
      setStats({ total: statsData.total || 0, by_status: statsData.by_status || {}, by_priority: statsData.by_priority || {}, by_category: statsData.by_category || {} });
    } catch (err) { console.error('Failed to fetch data:', err); } finally { setLoading(false); }
  }, [filterStatus, filterKategori, searchQuery]);

  useEffect(() => { fetchData(page); }, [page]);
  useEffect(() => { setPage(1); fetchData(1); }, [filterStatus, filterKategori, searchQuery]);

  const statsDisplay = useMemo(() => ({
    total: stats.total,
    menunggu: stats.by_status?.Menunggu || 0,
    diproses: stats.by_status?.Diproses || 0,
    selesai: stats.by_status?.Selesai || 0,
  }), [stats]);

  const kategoriIcon = (k) => KATEGORI_LIST.find(c => c.value === k)?.icon || '📌';

  return (
    <div className="max-w-6xl mx-auto space-y-10 pt-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Dashboard Admin</h2>
          <p className="text-slate-500 mt-2 font-medium">Kelola dan tanggapi laporan lingkungan warga</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500"><BarChart3 size={16} /><span>{statsDisplay.total} total laporan</span></div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total', value: statsDisplay.total, from: 'from-slate-800', to: 'to-slate-900', icon: <FileText size={22} /> },
          { label: 'Menunggu', value: statsDisplay.menunggu, from: 'from-amber-500', to: 'to-amber-600', icon: <Clock size={22} /> },
          { label: 'Diproses', value: statsDisplay.diproses, from: 'from-blue-500', to: 'to-blue-600', icon: <RefreshCw size={22} /> },
          { label: 'Selesai', value: statsDisplay.selesai, from: 'from-green-500', to: 'to-green-600', icon: <CheckCircle2 size={22} /> },
        ].map(({ label, value, from, to, icon }) => (
          <Card key={label} className={`p-5 bg-gradient-to-br ${from} ${to} text-white`}>
            <div className="flex items-center gap-4"><div className="p-2.5 bg-white/10 rounded-xl">{icon}</div><div><p className="text-xs font-semibold text-white/60 uppercase tracking-wider">{label}</p><h3 className="text-3xl font-black">{loading ? '-' : value}</h3></div></div>
          </Card>
        ))}
      </div>

      {/* Category stats */}
      {stats.by_category && Object.keys(stats.by_category).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {KATEGORI_LIST.filter(k => k.value !== 'Semua').map(k => {
            const count = stats.by_category[k.value] || 0;
            if (count === 0) return null;
            return <span key={k.value} className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 rounded-full text-sm font-medium text-slate-700">{k.icon} {k.label}: <strong>{count}</strong></span>;
          })}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input type="text" placeholder="Cari nama, lokasi, atau deskripsi..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white" />
        </div>
        <div className="flex gap-2">
          <select value={filterKategori} onChange={(e) => setFilterKategori(e.target.value)} className="px-3 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white cursor-pointer text-sm">
            {KATEGORI_LIST.map(k => <option key={k.value} value={k.value}>{k.icon} {k.label}</option>)}
          </select>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="px-3 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white cursor-pointer text-sm">
            <option value="Semua">Semua Status</option>
            <option value="Menunggu">Menunggu</option>
            <option value="Diproses">Diproses</option>
            <option value="Selesai">Selesai</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Daftar Laporan <span className="text-slate-400 font-normal ml-2">({pagination.total} total)</span></h3>

        {loading ? (
          <div className="py-16 text-center text-slate-400"><RefreshCw size={32} className="animate-spin mx-auto mb-2" /><p>Memuat...</p></div>
        ) : laporan.length === 0 ? (
          <div className="py-16 text-center text-slate-400 bg-slate-50/50 border-2 border-dashed border-slate-200 rounded-2xl"><Search size={32} className="opacity-50 mx-auto mb-2" /><p>Tidak ada laporan.</p></div>
        ) : (
          <div className="space-y-3">
            {laporan.map((item) => (
              <Card key={item.id} className="p-4 flex items-start gap-4 border-slate-200/60 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer"
                onClick={async () => { try { const res = await fetch(`/api/laporan/${item.id}/preview`); const data = await res.json(); setSelectedItem({ ...item, foto: data.foto }); } catch(e) { setSelectedItem(item); } }}>
                <div className="flex-1 min-w-0 space-y-1.5">
                  <div className="flex flex-wrap gap-1.5 items-center">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${item.status === 'Menunggu' ? 'bg-amber-100 text-amber-700' : item.status === 'Diproses' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>{item.status}</span>
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${item.prioritas === 'Tinggi' ? 'bg-red-100 text-red-700' : item.prioritas === 'Sedang' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>{item.prioritas}</span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600">{kategoriIcon(item.kategori)} {item.kategori || 'Sampah'}</span>
                    <span className="text-xs text-slate-400">{item.tanggal}</span>
                  </div>
                  <h4 className="text-base font-bold text-slate-900">{item.nama}</h4>
                  <p className="text-sm text-slate-600 line-clamp-1">{item.deskripsi}</p>
                  <div className="flex items-center gap-1.5 text-slate-500 text-sm"><MapPin size={14} className="text-rose-400 flex-shrink-0" /><span className="truncate">{item.lokasi}</span></div>
                </div>
                <ChevronDown size={14} className="text-slate-400 flex-shrink-0 mt-2" />
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {pagination.total_pages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-4">
            <button onClick={() => { const p = Math.max(1, page - 1); setPage(p); }} disabled={page <= 1}
              className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-30 cursor-pointer"><ChevronLeft size={18} /></button>
            <span className="text-sm text-slate-600 font-medium">Hal {page} dari {pagination.total_pages}</span>
            <button onClick={() => { const p = Math.min(pagination.total_pages, page + 1); setPage(p); }} disabled={page >= pagination.total_pages}
              className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-30 cursor-pointer"><ChevronRight size={18} /></button>
          </div>
        )}
      </div>

      {selectedItem && <DetailModal item={selectedItem} onClose={() => setSelectedItem(null)} onRefresh={() => fetchData(page)} />}
    </div>
  );
}
