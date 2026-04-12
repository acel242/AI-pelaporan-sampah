import { useState, useMemo } from 'react';
import { Card } from '../components/Card';
import { MapPin, Clock, FileText, CheckCircle2, X, Eye, Search, Filter, AlertTriangle, Check, ChevronDown, BarChart3, Activity, RefreshCw } from 'lucide-react';

function DetailModal({ item, onClose, onUpdateStatus }) {
  if (!item) return null;

  const priorityColors = {
    Tinggi: 'bg-red-100 text-red-700',
    Sedang: 'bg-amber-100 text-amber-700',
    Rendah: 'bg-green-100 text-green-700',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-100 p-6 flex items-start justify-between gap-4 z-10">
          <div>
            <h3 className="text-xl font-bold text-slate-900">{item.nama}</h3>
            <p className="text-sm text-slate-500 mt-1">ID: #{item.id}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors cursor-pointer">
            <X size={20} className="text-slate-500" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          <div className="flex flex-wrap gap-2">
            <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${
              item.status === 'Menunggu' ? 'bg-amber-100 text-amber-700' : 
              item.status === 'Diproses' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
            }`}>
              {item.status === 'Menunggu' ? <Clock size={12} className="mr-1.5" /> : 
               item.status === 'Diproses' ? <RefreshCw size={12} className="mr-1.5" /> : <CheckCircle2 size={12} className="mr-1.5" />}
              {item.status}
            </span>
            <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${priorityColors[item.prioritas]}`}>
              <AlertTriangle size={12} className="mr-1.5" />
              Prioritas {item.prioritas}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Tanggal Laporan</p>
              <p className="text-slate-700 font-bold">{item.tanggal}</p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Terakhir Diperbarui</p>
              <p className="text-slate-700 font-bold">{item.updatedAt || item.tanggal}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <MapPin size={18} className="text-rose-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-0.5">Lokasi</p>
              <p className="text-slate-700 font-medium">{item.lokasi}</p>
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Deskripsi</p>
            <p className="text-slate-600 leading-relaxed">{item.deskripsi}</p>
          </div>

          {item.foto && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Dokumentasi</p>
              <img 
                src={item.foto} 
                alt="Dokumentasi laporan" 
                className="w-full h-48 object-cover rounded-xl bg-slate-100"
              />
            </div>
          )}

          {item.catatan && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <p className="text-xs font-semibold text-amber-600 uppercase tracking-wider mb-1">Catatan Agent</p>
              <p className="text-amber-800 text-sm">{item.catatan}</p>
            </div>
          )}

          {item.activity && item.activity.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Riwayat Aktivitas</p>
              <div className="space-y-2">
                {item.activity.map((act, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-slate-300 mt-1.5 flex-shrink-0" />
                    <div>
                      <p className="text-slate-600">{act.text}</p>
                      <p className="text-xs text-slate-400">{act.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="sticky bottom-0 bg-white border-t border-slate-100 p-6 flex flex-wrap gap-3">
          {item.status === 'Menunggu' && (
            <>
              <button
                onClick={() => { onUpdateStatus(item.id, 'Diproses'); onClose(); }}
                className="flex-1 min-w-[140px] flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors cursor-pointer"
              >
                <RefreshCw size={16} />
                Proses Sekarang
              </button>
              <button
                onClick={() => { onUpdateStatus(item.id, 'Selesai'); onClose(); }}
                className="flex-1 min-w-[140px] flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 transition-colors cursor-pointer"
              >
                <CheckCircle2 size={16} />
                Tandai Selesai
              </button>
            </>
          )}
          {item.status === 'Diproses' && (
            <button
              onClick={() => { onUpdateStatus(item.id, 'Selesai'); onClose(); }}
              className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 transition-colors cursor-pointer"
            >
              <CheckCircle2 size={16} />
              Tandai Selesai
            </button>
          )}
          <button
            onClick={onClose}
            className="px-6 py-3 rounded-xl font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors cursor-pointer"
          >
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}

export function Admin({ laporan, onUpdateStatus }) {
  const [selectedItem, setSelectedItem] = useState(null);
  const [filterStatus, setFilterStatus] = useState('Semua');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('terbaru');

  const stats = useMemo(() => {
    const total = laporan.length;
    const menunggu = laporan.filter(l => l.status === 'Menunggu').length;
    const diproses = laporan.filter(l => l.status === 'Diproses').length;
    const selesai = laporan.filter(l => l.status === 'Selesai').length;
    return { total, menunggu, diproses, selesai };
  }, [laporan]);

  const filteredLaporan = useMemo(() => {
    let result = [...laporan];
    
    if (filterStatus !== 'Semua') {
      result = result.filter(l => l.status === filterStatus);
    }
    
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(l => 
        l.nama.toLowerCase().includes(q) ||
        l.lokasi.toLowerCase().includes(q) ||
        l.deskripsi.toLowerCase().includes(q)
      );
    }
    
    if (sortBy === 'terbaru') {
      result.sort((a, b) => b.id - a.id);
    } else if (sortBy === 'terlama') {
      result.sort((a, b) => a.id - b.id);
    }
    
    return result;
  }, [laporan, filterStatus, searchQuery, sortBy]);

  const handleUpdateStatus = (id, newStatus) => {
    const item = laporan.find(l => l.id === id);
    const now = new Date().toLocaleString('id-ID', { 
      day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
    
    const newActivity = [
      ...(item.activity || []),
      { text: `Status diubah ke "${newStatus}"`, time: now }
    ];
    
    onUpdateStatus(id, newStatus, newActivity);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-10 animate-in fade-in zoom-in-95 duration-500 pt-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Dashboard Admin</h2>
          <p className="text-slate-500 mt-2 font-medium">Kelola dan tanggapi laporan warga</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <BarChart3 size={16} />
          <span>{stats.total} total laporan</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-5 bg-gradient-to-br from-slate-800 to-slate-900 text-white">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-white/10 rounded-xl">
              <FileText size={22} />
            </div>
            <div>
              <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">Total</p>
              <h3 className="text-3xl font-black">{stats.total}</h3>
            </div>
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-amber-500 to-amber-600 text-white">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-white/10 rounded-xl">
              <Clock size={22} />
            </div>
            <div>
              <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">Menunggu</p>
              <h3 className="text-3xl font-black">{stats.menunggu}</h3>
            </div>
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-white/10 rounded-xl">
              <RefreshCw size={22} />
            </div>
            <div>
              <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">Diproses</p>
              <h3 className="text-3xl font-black">{stats.diproses}</h3>
            </div>
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-white/10 rounded-xl">
              <CheckCircle2 size={22} />
            </div>
            <div>
              <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">Selesai</p>
              <h3 className="text-3xl font-black">{stats.selesai}</h3>
            </div>
          </div>
        </Card>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Cari nama, lokasi, atau deskripsi..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white cursor-pointer"
          >
            <option value="Semua">Semua Status</option>
            <option value="Menunggu">Menunggu</option>
            <option value="Diproses">Diproses</option>
            <option value="Selesai">Selesai</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white cursor-pointer"
          >
            <option value="terbaru">Terbaru</option>
            <option value="terlama">Terlama</option>
          </select>
        </div>
      </div>

      {/* Laporan List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">
            Daftar Laporan 
            <span className="text-slate-400 font-normal ml-2">({filteredLaporan.length})</span>
          </h3>
        </div>

        {filteredLaporan.length === 0 ? (
          <div className="py-16 text-center text-slate-400 bg-slate-50/50 border-2 border-dashed border-slate-200 rounded-2xl">
            <div className="flex flex-col items-center gap-2">
              <Search size={32} className="opacity-50" />
              <p>Tidak ada laporan yang cocok dengan filter.</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredLaporan.map((item) => (
              <Card 
                key={item.id} 
                className="p-0 flex flex-col group overflow-hidden border-slate-200/60 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer"
                onClick={() => setSelectedItem(item)}
              >
                <div className="p-6 space-y-4 flex-grow">
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex flex-wrap gap-1.5">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        item.status === 'Menunggu' ? 'bg-amber-100 text-amber-700' : 
                        item.status === 'Diproses' ? 'bg-blue-100 text-blue-700' : 'bg-green                      }`}>
                        {item.status === 'Menunggu' ? <Clock size={12} className="mr-1" /> : 
                         item.status === 'Diproses' ? <RefreshCw size={12} className="mr-1" /> : <CheckCircle2 size={12} className="mr-1" />}
                        {item.status}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        item.prioritas === 'Tinggi' ? 'bg-red-100 text-red-700' : 
                        item.prioritas === 'Sedang' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                      }`}>
                        <AlertTriangle size={10} className="mr-1" />
                        {item.prioritas}
                      </span>
                    </div>
                    <span className="text-xs text-slate-400 font-semibold">{item.tanggal}</span>
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900 mb-1">{item.nama}</h4>
                    <p className="text-sm text-slate-600 line-clamp-2">{item.deskripsi}</p>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-500 text-sm">
                    <MapPin size={14} className="text-rose-400 flex-shrink-0" />
                    <span className="truncate">{item.lokasi}</span>
                  </div>
                </div>
                <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-slate-400 text-sm">
                    <Eye size={14} />
                    <span>Lihat Detail</span>
                  </div>
                  <ChevronDown size={14} className="text-slate-400 group-hover:translate-y-0.5 transition-transform" />
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {selectedItem && (
        <DetailModal 
          item={selectedItem} 
          onClose={() => setSelectedItem(null)} 
          onUpdateStatus={handleUpdateStatus}
        />
      )}
    </div>
  );
}
