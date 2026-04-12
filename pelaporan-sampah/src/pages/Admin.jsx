import { useState } from 'react';
import { Card } from '../components/Card';
import { MapPin, Clock, FileText, CheckCircle2, X, Eye, Check } from 'lucide-react';

function DetailModal({ item, onClose, onUpdateStatus }) {
  if (!item) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-100 p-6 flex items-start justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold text-slate-900">{item.nama}</h3>
            <p className="text-sm text-slate-500 mt-1">{item.tanggal}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors cursor-pointer">
            <X size={20} className="text-slate-500" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-bold ${
            item.status === 'Menunggu' 
              ? 'bg-amber-100 text-amber-700' 
              : 'bg-green-100 text-green-700'
          }`}>
            {item.status === 'Menunggu' ? <Clock size={14} className="mr-1.5" /> : <CheckCircle2 size={14} className="mr-1.5" />}
            {item.status}
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
        </div>

        <div className="sticky bottom-0 bg-white border-t border-slate-100 p-6 flex gap-3">
          {item.status === 'Menunggu' && (
            <button
              onClick={() => { onUpdateStatus(item.id, 'Selesai'); onClose(); }}
              className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 transition-colors cursor-pointer"
            >
              <CheckCircle2 size={18} />
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
  const [filter, setFilter] = useState('Semua');

  const menungguCount = laporan.filter(l => l.status === 'Menunggu').length;
  const selesaiCount = laporan.filter(l => l.status === 'Selesai').length;

  const filteredLaporan = filter === 'Semua' 
    ? laporan 
    : laporan.filter(l => l.status === filter);

  return (
    <div className="max-w-6xl mx-auto space-y-10 animate-in fade-in zoom-in-95 duration-500 pt-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Dashboard Admin</h2>
          <p className="text-slate-500 mt-2 font-medium">Tinjau dan tindaknullati laporan warga.</p>
        </div>
        <div className="flex gap-2">
          {['Semua', 'Menunggu', 'Selesai'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
                filter === f 
                  ? 'bg-slate-800 text-white' 
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-white">
          <div className="flex items-center gap-5">
            <div className="p-3.5 bg-blue-500 text-white rounded-2xl shadow-sm">
              <FileText size={28} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-1">Total</p>
              <h3 className="text-4xl font-black text-slate-800">{laporan.length}</h3>
            </div>
          </div>
        </Card>
        <Card className="p-6 bg-gradient-to-br from-amber-50 to-white">
          <div className="flex items-center gap-5">
            <div className="p-3.5 bg-amber-500 text-white rounded-2xl shadow-sm">
              <Clock size={28} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-1">Menunggu</p>
              <h3 className="text-4xl font-black text-slate-800">{menungguCount}</h3>
            </div>
          </div>
        </Card>
        <Card className="p-6 bg-gradient-to-br from-green-50 to-white">
          <div className="flex items-center gap-5">
            <div className="p-3.5 bg-green-500 text-white rounded-2xl shadow-sm">
              <CheckCircle2 size={28} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-1">Selesai</p>
              <h3 className="text-4xl font-black text-slate-800">{selesaiCount}</h3>
            </div>
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <h3 className="text-xl font-bold text-slate-900 border-b pb-4">
          Daftar Laporan 
          <span className="text-slate-400 font-normal ml-2">({filteredLaporan.length})</span>
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-8 gap-6">
          {filteredLaporan.length === 0 ? (
            <div className="col-span-full py-16 text-center text-slate-400 bg-slate-50/50 border-2 border-dashed border-slate-200 rounded-2xl">
              {filter === 'Semua' ? 'Belum ada laporan yang masuk.' : `Tidak ada laporan dengan status "${filter}".`}
            </div>
          ) : (
            filteredLaporan.map((item) => (
              <Card 
                key={item.id} 
                className="p-0 flex flex-col justify-between group overflow-hidden border-slate-200/60 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedItem(item)}
              >
                <div className="p-7 space-y-4 flex-grow">
                  <div className="flex justify-between items-start gap-2">
                    <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold shadow-sm ${
                      item.status === 'Menunggu' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {item.status === 'Menunggu' ? <Clock size={12} className="mr-1.5" /> : <CheckCircle2 size={12} className="mr-1.5" />}
                      {item.status}
                    </span>
                    <span className="text-sm text-slate-400 font-semibold">{item.tanggal}</span>
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-slate-900 mb-1.5">{item.nama}</h4>
                    <p className="text-slate-600/90 text-sm leading-relaxed line-clamp-2">{item.deskripsi}</p>
                  </div>
                </div>
                <div className="px-7 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center text-slate-600 text-sm font-semibold gap-2.5">
                    <MapPin size={18} className="text-rose-500 flex-shrink-0" />
                    <span className="truncate">{item.lokasi}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-400 text-sm font-semibold">
                    <Eye size={16} />
                    <span>Detail</span>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>

      {selectedItem && (
        <DetailModal 
          item={selectedItem} 
          onClose={() => setSelectedItem(null)} 
          onUpdateStatus={onUpdateStatus}
        />
      )}
    </div>
  );
}
