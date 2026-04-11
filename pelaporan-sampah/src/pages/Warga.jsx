import { useState } from 'react';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { CheckCircle2, UploadCloud } from 'lucide-react';

export function Warga({ addLaporan }) {
  const [formData, setFormData] = useState({ nama: '', lokasi: '', deskripsi: '' });
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.nama || !formData.lokasi || !formData.deskripsi) return;
    
    addLaporan({
      id: Date.now(),
      ...formData,
      status: "Menunggu",
      tanggal: new Date().toLocaleDateString('id-ID')
    });
    
    setIsSuccess(true);
    setFormData({ nama: '', lokasi: '', deskripsi: '' });
    
    setTimeout(() => {
      setIsSuccess(false);
    }, 4000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 pb-12 animate-in fade-in zoom-in-95 duration-500 pt-8">
      <div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Form Pelaporan</h2>
        <p className="text-slate-500 mt-2 font-medium">Bantu kami menjaga kebersihan lingkungan dengan melaporkan tumpukan sampah liar.</p>
      </div>

      {isSuccess && (
        <div className="bg-green-50 text-green-800 p-4 rounded-xl flex items-center gap-3 border border-green-200 animate-in slide-in-from-top-2">
          <CheckCircle2 className="text-green-600 flex-shrink-0" />
          <span className="font-semibold text-sm">Laporan berhasil dikirim! Terima kasih atas laporan Anda.</span>
        </div>
      )}

      <Card className="p-6 md:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input 
            label="Nama Lengkap" 
            placeholder="Masukkan nama Anda"
            value={formData.nama}
            onChange={(e) => setFormData({...formData, nama: e.target.value})}
            required
          />
          <Input 
            label="Lokasi Kejadian" 
            placeholder="Contoh: Jl. Melati Gg. 2, Pasar Rebo"
            value={formData.lokasi}
            onChange={(e) => setFormData({...formData, lokasi: e.target.value})}
            required
          />
          <Input 
            type="textarea"
            label="Deskripsi Detail" 
            placeholder="Jelaskan kondisi secara detail (e.g., sudah menumpuk 3 hari dan bau menyengat)..."
            value={formData.deskripsi}
            onChange={(e) => setFormData({...formData, deskripsi: e.target.value})}
            required
          />
          
          <div className="space-y-2 flex flex-col items-start w-full">
            <label className="block text-sm font-semibold text-slate-700">Dokumentasi (Opsional)</label>
            <div className="w-full border-2 border-dashed border-slate-300 rounded-xl p-8 hover:bg-slate-50 transition-colors flex flex-col items-center justify-center cursor-pointer text-slate-500 hover:border-blue-400 group">
              <div className="p-3 bg-white rounded-full shadow-sm group-hover:scale-110 transition-transform mb-3 border border-slate-100">
                <UploadCloud size={28} className="text-blue-500" />
              </div>
              <p className="text-sm font-semibold text-slate-700 mb-1">Upload foto di sini</p>
              <p className="text-xs text-slate-400">UI Preview Only (Max 5MB)</p>
              <input type="file" className="hidden" />
            </div>
          </div>

          <div className="pt-2">
            <Button type="submit" className="w-full py-3.5 text-base shadow-lg shadow-blue-500/20">
              Kirim Laporan
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
