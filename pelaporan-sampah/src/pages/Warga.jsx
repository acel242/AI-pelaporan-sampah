import { useState, useRef } from 'react';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { CheckCircle2, UploadCloud, X } from 'lucide-react';

const API_BASE = '/api';

export function Warga() {
  const [formData, setFormData] = useState({ nama: '', lokasi: '', deskripsi: '' });
  const [foto, setFoto] = useState(null);
  const [fotoPreview, setFotoPreview] = useState(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reportId, setReportId] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      alert('File terlalu besar. Maksimal 5MB.');
      return;
    }
    if (!file.type.startsWith('image/')) {
      alert('Hanya file gambar yang diizinkan.');
      return;
    }
    setFoto(file);
    const reader = new FileReader();
    reader.onload = (e) => setFotoPreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleRemoveFoto = () => {
    setFoto(null);
    setFotoPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.nama || !formData.lokasi || !formData.deskripsi) return;
    
    setIsSubmitting(true);
    
    try {
      const res = await fetch(`${API_BASE}/laporan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nama: formData.nama,
          lokasi: formData.lokasi,
          deskripsi: formData.deskripsi,
          foto: fotoPreview || null,
          user_id: 0  // Anonymous for web users
        })
      });
      
      const data = await res.json();
      
      if (data.success) {
        setReportId(data.id);
        setIsSuccess(true);
        setFormData({ nama: '', lokasi: '', deskripsi: '' });
        handleRemoveFoto();
        setTimeout(() => setIsSuccess(false), 10000);
      } else {
        alert('Gagal mengirim laporan: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Submit error:', err);
      alert('Terjadi kesalahan saat mengirim laporan.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 pb-12 animate-in fade-in zoom-in-95 duration-500 pt-8">
      <div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Form Pelaporan</h2>
        <p className="text-slate-500 mt-2 font-medium">
          Laporkan tumpukan sampah liar di lingkungan Anda. Kami akan segera menindaklanjuti.
        </p>
      </div>

      {isSuccess && (
        <div className="bg-green-50 text-green-800 p-4 rounded-xl flex items-center gap-3 border border-green-200 animate-in slide-in-from-top-2">
          <CheckCircle2 className="text-green-600 flex-shrink-0" size={20} />
          <div>
            <span className="font-bold block">Laporan berhasil dikirim!</span>
            <span className="text-sm opacity-80">ID Laporan: #{reportId}</span>
          </div>
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
          
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-700">
              Dokumentasi <span className="text-slate-400 font-normal">(Opsional)</span>
            </label>
            
            {fotoPreview ? (
              <div className="relative rounded-xl overflow-hidden bg-slate-100">
                <img 
                  src={fotoPreview} 
                  alt="Preview" 
                  className="w-full h-48 object-cover"
                />
                <button
                  type="button"
                  onClick={handleRemoveFoto}
                  className="absolute top-2 right-2 p-1.5 bg-black/60 hover:bg-black/80 text-white rounded-full transition-colors cursor-pointer"
                >
                  <X size={16} />
                </button>
                <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/60 text-white text-xs rounded-md">
                  {foto?.name}
                </div>
              </div>
            ) : (
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`w-full border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
                  isDragging 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                }`}
              >
                <div className={`p-3 rounded-full mb-3 transition-colors ${
                  isDragging ? 'bg-blue-100' : 'bg-slate-100'
                }`}>
                  <UploadCloud size={28} className={isDragging ? 'text-blue-500' : 'text-slate-400'} />
                </div>
                <p className="text-sm font-semibold text-slate-700 mb-1">
                  {isDragging ? 'Lepaskan file di sini' : 'Seret foto ke sini atau klik untuk pilih'}
                </p>
                <p className="text-xs text-slate-400">JPG, PNG, WEBP — Maksimal 5MB</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                />
              </div>
            )}
          </div>

          <div className="pt-2">
            <Button 
              type="submit" 
              className="w-full py-3.5 text-base shadow-lg shadow-blue-500/20"
              disabled={!formData.nama || !formData.lokasi || !formData.deskripsi || isSubmitting}
            >
              {isSubmitting ? 'Mengirim...' : 'Kirim Laporan'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
