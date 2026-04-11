import { Card } from '../components/Card';
import { MapPin, Clock, FileText, CheckCircle2 } from 'lucide-react';

export function Admin({ laporan }) {
  const menungguCount = laporan.filter(l => l.status === 'Menunggu').length;
  const selesaiCount = laporan.filter(l => l.status === 'Selesai').length;

  return (
    <div className="max-w-6xl mx-auto space-y-10 animate-in fade-in zoom-in-95 duration-500 pt-8 pb-12">
      <div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Dashboard Admin</h2>
        <p className="text-slate-500 mt-2 font-medium">Tinjau dan tindaklanjuti laporan warga hari ini.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-white hover:shadow-md transition-all border-blue-100/50">
          <div className="flex items-center gap-5">
            <div className="p-3.5 bg-blue-500 text-white rounded-2xl shadow-sm">
              <FileText size={28} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-1">Total Laporan</p>
              <h3 className="text-4xl font-black text-slate-800">{laporan.length}</h3>
            </div>
          </div>
        </Card>
        <Card className="p-6 bg-gradient-to-br from-amber-50 to-white hover:shadow-md transition-all border-amber-100/50">
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
        <Card className="p-6 bg-gradient-to-br from-green-50 to-white hover:shadow-md transition-all border-green-100/50">
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
        <h3 className="text-xl font-bold text-slate-900 border-b pb-4">Daftar Laporan Terbaru</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-8 gap-6">
          {laporan.length === 0 ? (
            <div className="col-span-full py-16 text-center text-slate-400 bg-slate-50/50 border-2 border-dashed border-slate-200 rounded-2xl">
              Belum ada laporan yang masuk hari ini.
            </div>
          ) : (
            laporan.map((item) => (
              <Card key={item.id} className="p-0 flex flex-col justify-between group overflow-hidden border-slate-200/60 shadow-sm">
                <div className="p-7 space-y-5 flex-grow">
                  <div className="flex justify-between items-start gap-2">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold shadow-sm ${
                      item.status === 'Menunggu' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {item.status === 'Menunggu' ? <Clock size={12} className="mr-1.5" /> : <CheckCircle2 size={12} className="mr-1.5" />}
                      {item.status}
                    </span>
                    <span className="text-sm text-slate-400 font-semibold">{item.tanggal}</span>
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-slate-900 mb-1.5">{item.nama}</h4>
                    <p className="text-slate-600/90 text-sm leading-relaxed">{item.deskripsi}</p>
                  </div>
                </div>
                <div className="px-7 py-4 bg-slate-50 border-t border-slate-100 flex items-center text-slate-600 text-sm font-semibold gap-2.5">
                  <MapPin size={18} className="text-rose-500" />
                  <span className="truncate">{item.lokasi}</span>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
