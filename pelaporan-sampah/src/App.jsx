import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { Warga } from './pages/Warga';
import { Admin } from './pages/Admin';
import { Peta } from './pages/Peta';
import { LogOut, Leaf, MapPin, FileText, CheckCircle2, Clock, AlertTriangle, Trash2, Plus, ChevronLeft, ChevronRight, Map, Bell, X } from 'lucide-react';
import { Button } from './components/Button';

const API_BASE = '/api';

const KATEGORI_LIST = [
  { value: 'Sampah', label: 'Sampah', icon: '🗑️' },
  { value: 'Fasilitas Rusak', label: 'Fasilitas Rusak', icon: '🔧' },
  { value: 'Hewan Liar', label: 'Hewan Liar', icon: '🐕' },
  { value: 'Kebakaran', label: 'Kebakaran', icon: '🔥' },
  { value: 'Lainnya', label: 'Lainnya', icon: '📌' },
];

function Navbar({ role, onLogout }) {
  const navigate = useNavigate();
  const [notifs, setNotifs] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    const poll = () => {
      fetch(`${API_BASE}/notifications`).then(r => r.json()).then(d => setNotifs(d.notifications || [])).catch(() => {});
    };
    poll();
    const interval = setInterval(poll, 30000);
    return () => clearInterval(interval);
  }, []);

  const markAllRead = async () => {
    await fetch(`${API_BASE}/notifications/read-all`, { method: 'POST' });
    setNotifs([]);
    setShowNotifs(false);
  };

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-10 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2 text-green-600 cursor-pointer" onClick={() => navigate('/')}>
            <Leaf size={28} /><span className="font-bold text-xl text-slate-800 tracking-tight">EcoLapor</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => navigate('/peta')} className="py-2 px-4 gap-2 flex items-center shadow-none border border-slate-200 text-sm"><Map size={16} />Peta</Button>
            {role !== 'admin' && (
              <Button variant="secondary" onClick={() => navigate('/admin')} className="py-2 px-4 gap-2 flex items-center shadow-none border border-slate-200 text-sm">Admin</Button>
            )}
            {/* Notification Bell */}
            <div className="relative">
              <button onClick={() => setShowNotifs(!showNotifs)} className="relative p-2 hover:bg-slate-100 rounded-xl cursor-pointer">
                <Bell size={20} className="text-slate-600" />
                {notifs.length > 0 && <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">{notifs.length}</span>}
              </button>
              {showNotifs && (
                <div className="absolute right-0 top-12 w-80 bg-white rounded-xl shadow-xl border border-slate-200 max-h-80 overflow-y-auto z-50">
                  <div className="p-3 border-b border-slate-100 flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-700">Notifikasi</span>
                    {notifs.length > 0 && <button onClick={markAllRead} className="text-xs text-blue-600 hover:text-blue-800 cursor-pointer">Tandai semua dibaca</button>}
                  </div>
                  {notifs.length === 0 ? (
                    <div className="p-4 text-center text-slate-400 text-sm">Tidak ada notifikasi baru</div>
                  ) : (
                    notifs.map(n => (
                      <div key={n.id} className="p-3 border-b border-slate-50 hover:bg-slate-50 text-sm">
                        <p className="text-slate-700">{n.message}</p>
                        <p className="text-xs text-slate-400 mt-1">{n.created_at ? new Date(n.created_at).toLocaleString('id-ID') : ''}</p>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
            {role === 'admin' && (
              <>
                <span className="text-sm font-medium text-slate-500 hidden sm:block">Admin</span>
                <Button variant="secondary" onClick={onLogout} className="py-2 px-3 gap-2 flex items-center shadow-none border border-slate-200"><LogOut size={16} /><span className="hidden sm:inline">Logout</span></Button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

function resolveImgSrc(val) {
  if (!val) return null;
  if (val.startsWith('data:')) return val;
  if (val.startsWith('/')) return 'https://eco-lapor.43.157.235.76.nip.io' + val;
  return null;
}

function Dashboard({ onBuatLaporan, userRole }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total: 0, by_status: {}, by_priority: {}, by_category: {} });
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({ page: 1, per_page: 5, total: 0, total_pages: 1 });
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedGallery, setSelectedGallery] = useState([]);
  const [aiSuggestion, setAiSuggestion] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [voteInput, setVoteInput] = useState(null); // null = hidden, number = laporan_id
  const [voteName, setVoteName] = useState('');
  const [voteSubmitting, setVoteSubmitting] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const fetchData = (p = 1) => {
    Promise.all([
      fetch(`${API_BASE}/stats`).then(r => r.json()),
      fetch(`${API_BASE}/laporan?page=${p}`).then(r => r.json())
    ]).then(([statsData, laporanData]) => {
      setStats({ total: statsData.total || 0, by_status: statsData.by_status || {}, by_priority: statsData.by_priority || {}, by_category: statsData.by_category || {} });
      setRecent(laporanData.laporan || []);
      setPagination(laporanData.pagination || { page: 1, per_page: 5, total: 0, total_pages: 1 });
    }).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(page); }, [page]);

  const statCards = [
    { label: 'Total Laporan', value: stats.total, icon: <FileText size={22} />, from: 'from-slate-800', to: 'to-slate-900' },
    { label: 'Menunggu', value: stats.by_status?.Menunggu || 0, icon: <Clock size={22} />, from: 'from-amber-500', to: 'to-amber-600' },
    { label: 'Diproses', value: stats.by_status?.Diproses || 0, icon: <AlertTriangle size={22} />, from: 'from-blue-500', to: 'to-blue-600' },
    { label: 'Selesai', value: stats.by_status?.Selesai || 0, icon: <CheckCircle2 size={22} />, from: 'from-green-500', to: 'to-green-600' },
  ];

  const statusColor = (s) => {
    if (s === 'Menunggu') return 'bg-amber-100 text-amber-700';
    if (s === 'Diproses') return 'bg-blue-100 text-blue-700';
    return 'bg-green-100 text-green-700';
  };

  const kategoriIcon = (k) => KATEGORI_LIST.find(c => c.value === k)?.icon || '📌';

  const openDetail = async (item) => {
    setSelectedItem(item);
    setSelectedGallery([]);
    setAiSuggestion(null);
    setAiLoading(true);
    try {
      const res = await fetch(`${API_BASE}/laporan/${item.id}`);
      const data = await res.json();
      setSelectedItem(data);
      setSelectedGallery(data.gallery || []);
    } catch {
      try {
        const galleryRes = await fetch(`${API_BASE}/laporan/${item.id}/gallery`);
        const galleryData = await galleryRes.json();
        setSelectedGallery(galleryData.photos || []);
      } catch {}
    }
    // Fetch AI suggestion — only for admin/petugas
    if (userRole === 'admin') {
      try {
        const sugRes = await fetch(`${API_BASE}/laporan/${item.id}/suggest`);
        const sugData = await sugRes.json();
        setAiSuggestion(sugData.saran || null);
      } catch {
        setAiSuggestion(null);
      } finally {
        setAiLoading(false);
      }
    } else {
      setAiLoading(false);
    }
  };

  const handleVote = async (laporanId) => {
    if (!voteName.trim()) return;
    setVoteSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/laporan/${laporanId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nama: voteName.trim() })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message || 'Vote berhasil!');
        setVoteInput(null);
        setVoteName('');
        fetchData(page);
        // Refresh detail if open
        if (selectedItem && selectedItem.id === laporanId) {
          const res2 = await fetch(`${API_BASE}/laporan/${laporanId}`);
          const d = await res2.json();
          setSelectedItem(d);
        }
      } else {
        showToast(data.error || 'Gagal vote');
      }
    } catch {
      showToast('Gagal mengirim vote');
    } finally {
      setVoteSubmitting(false);
    }
  };

  const handleExportMaps = async () => {
    try {
      const res = await fetch(`${API_BASE}/export/maps`);
      const data = await res.json();
      if (data.url) {
        window.open(data.url, '_blank');
        showToast(`Membuka ${data.count} lokasi di Google Maps`);
      } else {
        showToast(data.message || 'Tidak ada lokasi GPS untuk diekspor');
      }
    } catch {
      showToast('Gagal membuka Google Maps');
    }
  };

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(''), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-10 pt-8 pb-12">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm font-bold"><Leaf size={16} />EcoLapor Manado</div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">Laporkan Isu Lingkungan<br className="hidden sm:block" /> di Sekitar Anda</h1>
        <p className="text-slate-500 text-lg max-w-xl mx-auto">Bantu kami menjaga Manado — sampah, banjir, pencemaran, dan isu lingkungan lainnya.</p>
        <div className="flex items-center justify-center gap-3 flex-wrap">
          <Button onClick={onBuatLaporan} className="py-4 px-8 text-base gap-2 shadow-lg"><Plus size={18} />Buat Laporan</Button>
          <Button variant="secondary" onClick={() => navigate('/peta')} className="py-4 px-8 text-base gap-2 border-slate-300"><Map size={18} />Lihat Peta</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon, from, to }) => (
          <div key={label} className={`p-5 bg-gradient-to-br ${from} ${to} text-white rounded-2xl shadow-sm`}>
            <div className="flex items-center gap-3 mb-2"><div className="p-2 bg-white/10 rounded-xl">{icon}</div></div>
            <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">{label}</p>
            <p className="text-3xl font-black mt-1">{loading ? '-' : value}</p>
          </div>
        ))}
      </div>

      {stats.by_category && Object.keys(stats.by_category).length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xl font-bold text-slate-900">📊 Laporan per Kategori</h2>
          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
            {KATEGORI_LIST.map(k => {
              const count = stats.by_category[k.value] || 0;
              return (
                <div key={k.value} className={`p-3 rounded-xl text-center ${count > 0 ? 'bg-green-50 border border-green-200' : 'bg-slate-50 border border-slate-100'}`}>
                  <span className="text-2xl">{k.icon}</span>
                  <p className="text-xs font-medium text-slate-600 mt-1">{k.label}</p>
                  <p className="text-lg font-black text-slate-800">{count}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {recent.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900">Laporan Terbaru</h2>
            <button onClick={handleExportMaps} className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-xl text-sm font-semibold hover:bg-blue-100 transition-colors cursor-pointer border border-blue-200">🗺️ Export ke Maps</button>
          </div>
          <div className="space-y-3">
            {recent.map(item => (
              <div key={item.id} className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 flex items-start gap-4">
                <button onClick={() => openDetail(item)} className="p-3 bg-green-50 rounded-xl flex-shrink-0 hover:bg-green-100 hover:scale-110 transition-all cursor-pointer" title="Lihat detail">
                  <span className="text-2xl">{kategoriIcon(item.kategori)}</span>
                </button>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-slate-800 truncate">{item.nama}</p>
                  <p className="text-sm text-slate-500 flex items-center gap-1 mt-0.5"><MapPin size={12} />{item.lokasi}</p>
                  <p className="text-xs text-slate-400 mt-0.5 truncate">{item.deskripsi}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{item.tanggal} {item.kategori && <span className="ml-2">{kategoriIcon(item.kategori)} {item.kategori}</span>}</p>
                </div>
                <div className="flex flex-col items-end gap-2 flex-shrink-0">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${statusColor(item.status)}`}>{item.status}</span>
                  {item.vote_count > 0 && <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700">👍 {item.vote_count}</span>}
                  <button onClick={() => openDetail(item)} className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors cursor-pointer flex items-center gap-1">📋 Detail</button>
                </div>
              </div>
            ))}
          </div>
          {pagination.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-30 cursor-pointer"><ChevronLeft size={18} /></button>
              <span className="text-sm text-slate-600 font-medium">Hal {page} dari {pagination.total_pages}</span>
              <button onClick={() => setPage(p => Math.min(pagination.total_pages, p + 1))} disabled={page >= pagination.total_pages} className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-30 cursor-pointer"><ChevronRight size={18} /></button>
            </div>
          )}
        </div>
      )}

      {/* Detail Modal with Before/After Gallery */}
      {selectedItem && (() => {
        const beforePhotos = selectedGallery.filter(g => g.photo_type === 'before');
        const afterPhotos = selectedGallery.filter(g => g.photo_type === 'after');
        const beforeGallerySrc = beforePhotos.length > 0
          ? (beforePhotos[0].foto_url?.startsWith('/') ? 'https://eco-lapor.43.157.235.76.nip.io' + beforePhotos[0].foto_url : beforePhotos[0].foto_url)
          : null;
        const beforeBase64Src = resolveImgSrc(selectedItem.foto);
        const hasBefore = beforeGallerySrc || beforeBase64Src;

        return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={() => setSelectedItem(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="sticky top-0 bg-white rounded-t-2xl border-b border-slate-100 p-6 flex items-center justify-between z-10">
              <div>
                <h3 className="text-xl font-bold text-slate-900">Laporan #{selectedItem.id}</h3>
                <span className={`inline-block mt-1 px-2.5 py-1 rounded-full text-xs font-bold ${statusColor(selectedItem.status)}`}>{selectedItem.status}</span>
              </div>
              <button onClick={() => setSelectedItem(null)} className="p-2 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer"><X size={20} className="text-slate-500" /></button>
            </div>
            <div className="p-6 space-y-5">
              {hasBefore && (
                <div className="space-y-3">
                  <p className="text-sm font-bold text-slate-700">📸 Perbandingan Sebelum & Sesudah</p>
                  <div className={`grid ${afterPhotos.length > 0 ? 'grid-cols-2' : 'grid-cols-1'} gap-3`}>
                    <div className="relative">
                      <div className="absolute top-2 left-2 z-10 px-2 py-1 rounded-lg text-xs font-bold text-white bg-amber-500 shadow">📷 SEBELUM</div>
                      {beforeGallerySrc ? (
                        <img src={beforeGallerySrc} alt="Sebelum" className="w-full rounded-xl object-cover h-48 bg-slate-100"
                          onError={e => { if (beforeBase64Src) { e.target.src = beforeBase64Src; } else { e.target.style.display='none'; e.target.parentElement.querySelector('.fallback-msg').style.display='flex'; } }} />
                      ) : beforeBase64Src ? (
                        <img src={beforeBase64Src} alt="Sebelum" className="w-full rounded-xl object-cover h-48 bg-slate-100"
                          onError={e => { e.target.style.display='none'; e.target.parentElement.querySelector('.fallback-msg').style.display='flex'; }} />
                      ) : null}
                      {!hasBefore && (
                        <div className="w-full rounded-xl h-48 bg-amber-50 flex items-center justify-center fallback-msg">
                          <p className="text-sm text-amber-400 font-medium">Tidak ada foto</p>
                        </div>
                      )}
                    </div>
                    {afterPhotos.length > 0 ? (
                      <div className="relative">
                        <div className="absolute top-2 left-2 z-10 px-2 py-1 rounded-lg text-xs font-bold text-white bg-green-500 shadow">✅ SESUDAH</div>
                        <img
                          src={afterPhotos[0].foto_url?.startsWith('/') ? 'https://eco-lapor.43.157.235.76.nip.io' + afterPhotos[0].foto_url : afterPhotos[0].foto_url}
                          alt="Sesudah" className="w-full rounded-xl object-cover h-48 bg-slate-100" onError={e => { e.target.style.display='none'; }} />
                      </div>
                    ) : (
                      <div className="relative">
                        <div className="absolute top-2 left-2 z-10 px-2 py-1 rounded-lg text-xs font-bold text-white bg-slate-400 shadow">⏳ SESUDAH</div>
                        <div className="w-full rounded-xl h-48 bg-slate-50 flex flex-col items-center justify-center border-2 border-dashed border-slate-200">
                          <p className="text-sm text-slate-400 font-medium">Belum ada foto</p>
                          <p className="text-xs text-slate-300 mt-1">Menunggu penanganan petugas</p>
                        </div>
                      </div>
                    )}
                  </div>
                  {afterPhotos.length > 1 && (
                    <div>
                      <p className="text-xs text-slate-400 mb-2">Foto penanganan lainnya:</p>
                      <div className="grid grid-cols-3 gap-2">
                        {afterPhotos.slice(1).map(g => (
                          <div key={g.id} className="relative rounded-lg overflow-hidden bg-slate-100">
                            <img src={g.foto_url?.startsWith('/') ? 'https://eco-lapor.43.157.235.76.nip.io' + g.foto_url : g.foto_url} alt="Sesudah" className="w-full h-24 object-cover" onError={e => { e.target.style.display='none'; }} />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {!hasBefore && afterPhotos.length === 0 && (
                <div className="bg-slate-50 rounded-xl p-4 text-center"><p className="text-sm text-slate-400">Tidak ada foto tersedia</p></div>
              )}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-50 rounded-xl p-3"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Pelapor</p><p className="font-bold text-slate-700">{selectedItem.nama}</p></div>
                <div className="bg-slate-50 rounded-xl p-3"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Kategori</p><p className="font-bold text-slate-700">{kategoriIcon(selectedItem.kategori)} {selectedItem.kategori || 'Sampah'}</p></div>
                <div className="bg-slate-50 rounded-xl p-3"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Prioritas</p><p className="font-bold text-slate-700">{selectedItem.prioritas || '-'}</p></div>
                <div className="bg-slate-50 rounded-xl p-3"><p className="text-xs font-semibold text-slate-400 uppercase mb-1">Tanggal</p><p className="font-bold text-slate-700">{selectedItem.tanggal}</p></div>
              </div>
              <div className="flex items-start gap-3"><MapPin size={18} className="text-rose-500 mt-0.5 flex-shrink-0" /><div><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Lokasi</p><p className="text-slate-700 font-medium">{selectedItem.lokasi}</p></div></div>
              <div className="flex items-start gap-3"><Clock size={18} className="text-blue-500 mt-0.5 flex-shrink-0" /><div><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Deskripsi</p><p className="text-slate-700 font-medium">{selectedItem.deskripsi}</p></div></div>
              {selectedItem.catatan && (
                <div className="flex items-start gap-3"><span className="mt-0.5">📝</span><div><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Catatan</p><p className="text-slate-700 font-medium">{selectedItem.catatan}</p></div></div>
              )}
              {userRole === 'admin' && (
              <div className="rounded-xl p-4 bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100">
                <p className="text-sm font-bold text-indigo-800 mb-2">💡 Saran Penanganan AI</p>
                {aiLoading ? (
                  <div className="flex items-center gap-2 text-indigo-400 text-sm"><div className="w-4 h-4 border-2 border-indigo-300 border-t-indigo-600 rounded-full animate-spin"></div>Menganalisis...</div>
                ) : aiSuggestion ? (
                  <p className="text-sm text-indigo-700 leading-relaxed whitespace-pre-line">{aiSuggestion}</p>
                ) : (
                  <p className="text-sm text-indigo-400 italic">Saran tidak tersedia</p>
                )}
              </div>
              )}
              {/* Vote Section */}
              <div className="rounded-xl p-4 bg-slate-50 border border-slate-200">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-bold text-slate-700">🗳️ Dukung Laporan Ini</p>
                  <span className="px-3 py-1 rounded-full text-sm font-bold bg-indigo-100 text-indigo-700">👍 {selectedItem.vote_count || 0} vote{(selectedItem.vote_count || 0) !== 1 ? 's' : ''}</span>
                </div>
                {voteInput === selectedItem.id ? (
                  <div className="space-y-2">
                    <input type="text" value={voteName} onChange={e => setVoteName(e.target.value)} placeholder="Nama Anda" className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    <div className="flex gap-2">
                      <button onClick={() => handleVote(selectedItem.id)} disabled={voteSubmitting || !voteName.trim()} className="flex-1 py-2 rounded-lg text-sm font-bold bg-indigo-600 text-white hover:bg-indigo-700 cursor-pointer disabled:opacity-50">{voteSubmitting ? 'Mengirim...' : 'Kirim Vote'}</button>
                      <button onClick={() => { setVoteInput(null); setVoteName(''); }} className="px-4 py-2 rounded-lg text-sm bg-slate-200 text-slate-600 hover:bg-slate-300 cursor-pointer">Batal</button>
                    </div>
                  </div>
                ) : (
                  <button onClick={() => setVoteInput(selectedItem.id)} className="w-full py-2.5 rounded-lg text-sm font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors cursor-pointer">Dukung Laporan Ini</button>
                )}
              </div>
            </div>
            <div className="sticky bottom-0 bg-white rounded-b-2xl border-t border-slate-100 p-6">
              <button onClick={() => setSelectedItem(null)} className="w-full py-3 rounded-xl font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors cursor-pointer">Tutup</button>
            </div>
          </div>
        </div>
        );
      })()}
      {/* Toast notification */}
      {toastMsg && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] px-6 py-3 bg-slate-800 text-white rounded-xl shadow-xl text-sm font-medium">
          {toastMsg}
        </div>
      )}
    </div>
  );
}

function App() {
  const [userRole, setUserRole] = useState(null);
  const navigate = useNavigate();

  const handleLogin = (role) => { setUserRole(role); if (role === 'admin') navigate('/admin'); };
  const handleLogout = () => { setUserRole(null); navigate('/'); };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-blue-100">
      <Navbar role={userRole} onLogout={handleLogout} />
      <main className="px-4">
        <Routes>
          <Route path="/" element={<Dashboard userRole={userRole} onBuatLaporan={() => navigate('/warga')} />} />
          <Route path="/warga" element={<Warga />} />
          <Route path="/peta" element={<Peta />} />
          <Route path="/admin" element={userRole === 'admin' ? <Admin /> : <Navigate to="/login" />} />
          <Route path="/login" element={<AdminLogin onLogin={handleLogin} />} />
        </Routes>
      </main>
    </div>
  );
}

function AdminLogin({ onLogin }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password === 'ecolapor2026') { onLogin('admin'); } else { setError(true); setTimeout(() => setError(false), 2000); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100 w-full max-w-sm text-center">
        <div className="flex justify-center mb-6"><div className="p-4 bg-green-100 text-green-600 rounded-2xl shadow-inner"><Leaf size={44} strokeWidth={2.5} /></div></div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight mb-2">EcoLapor</h1>
        <p className="text-slate-500 mb-6 text-sm font-medium">Login Admin</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Masukkan password admin"
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 text-center ${error ? 'border-red-400 focus:ring-red-400' : 'border-slate-200 focus:ring-blue-500'}`} />
          {error && <p className="text-red-500 text-sm font-medium">Password salah!</p>}
          <Button type="submit" className="w-full py-3.5">Masuk</Button>
        </form>
        <button onClick={() => navigate('/')} className="mt-4 text-sm text-slate-400 hover:text-slate-600 transition-colors cursor-pointer">← Kembali ke beranda</button>
      </div>
    </div>
  );
}

export default App;
