import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { Warga } from './pages/Warga';
import { Admin } from './pages/Admin';
import { LogOut, Leaf, MapPin, FileText, CheckCircle2, Clock, AlertTriangle, Trash2, Plus } from 'lucide-react';
import { Button } from './components/Button';

const API_BASE = '/api';

function Navbar({ role, onLogout }) {
  const navigate = useNavigate();

  if (!role) return (
    <nav className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-10 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2 text-green-600">
            <Leaf size={28} />
            <span className="font-bold text-xl text-slate-800 tracking-tight">EcoLapor</span>
          </div>
          <Button variant="secondary" onClick={() => navigate('/admin')} className="py-2 px-4 gap-2 flex items-center shadow-none border border-slate-200 text-sm">
            Admin
          </Button>
        </div>
      </div>
    </nav>
  );
  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-10 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2 text-green-600">
            <Leaf size={28} />
            <span className="font-bold text-xl text-slate-800 tracking-tight">EcoLapor</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-500 hidden sm:block">
              Masuk sebagai <span className="font-bold text-slate-700 capitalize">{role}</span>
            </span>
            <Button variant="secondary" onClick={onLogout} className="py-2 px-3 gap-2 flex items-center shadow-none border border-slate-200">
              <LogOut size={16} />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function Dashboard({ onBuatLaporan }) {
  const [stats, setStats] = useState({ total: 0, by_status: {}, by_priority: {} });
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/stats`).then(r => r.json()),
      fetch(`${API_BASE}/laporan`).then(r => r.json())
    ]).then(([statsData, laporanData]) => {
      setStats({
        total: statsData.total || 0,
        by_status: statsData.by_status || {},
        by_priority: statsData.by_priority || {}
      });
      const all = laporanData.laporan || [];
      setRecent(all.slice(0, 3));
    }).finally(() => setLoading(false));
  }, []);

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

  return (
    <div className="max-w-5xl mx-auto space-y-10 pt-8 pb-12">
      {/* Hero */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm font-bold">
          <Leaf size={16} />
          EcoLapor Manado
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
          Laporkan Sampah<br className="hidden sm:block" /> di Sekitar Anda
        </h1>
        <p className="text-slate-500 text-lg max-w-xl mx-auto">
          Bantu kami menjaga kebersihan Manado dengan melaporkan titik sampah yang butuh perhatian.
        </p>
        <Button onClick={onBuatLaporan} className="mt-2 py-4 px-8 text-base gap-2 shadow-lg">
          <Plus size={18} />
          Buat Laporan Baru
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon, from, to }) => (
          <div key={label} className={`p-5 bg-gradient-to-br ${from} ${to} text-white rounded-2xl shadow-sm`}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-white/10 rounded-xl">{icon}</div>
            </div>
            <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">{label}</p>
            <p className="text-3xl font-black mt-1">{loading ? '-' : value}</p>
          </div>
        ))}
      </div>

      {/* Recent Reports */}
      {recent.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-slate-900">Laporan Terbaru</h2>
          <div className="space-y-3">
            {recent.map(item => (
              <div key={item.id} className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 flex items-start gap-4">
                <div className="p-2 bg-slate-50 rounded-lg">
                  <Trash2 size={20} className="text-slate-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-slate-800 truncate">{item.nama}</p>
                  <p className="text-sm text-slate-500 flex items-center gap-1 mt-0.5">
                    <MapPin size={12} /> {item.lokasi}
                  </p>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${statusColor(item.status)}`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const [userRole, setUserRole] = useState(null);
  const navigate = useNavigate();

  const handleLogin = (role) => {
    setUserRole(role);
    if (role === 'admin') navigate('/admin');
  };

  const handleLogout = () => {
    setUserRole(null);
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-blue-100">
      <Navbar role={userRole} onLogout={handleLogout} />
      <main className="px-4">
        <Routes>
          <Route 
            path="/" 
            element={
              <Dashboard onBuatLaporan={() => navigate('/warga')} />
            } 
          />
          <Route path="/warga" element={<Warga />} />
          <Route 
            path="/admin" 
            element={userRole === 'admin' ? <Admin /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/login" 
            element={<AdminLogin onLogin={handleLogin} />} 
          />
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
    if (password === 'ecolapor2026') {
      onLogin('admin');
    } else {
      setError(true);
      setTimeout(() => setError(false), 2000);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100 w-full max-w-sm text-center">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-green-100 text-green-600 rounded-2xl shadow-inner">
            <Leaf size={44} strokeWidth={2.5} />
          </div>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight mb-2">EcoLapor</h1>
        <p className="text-slate-500 mb-6 text-sm font-medium">Login Admin</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Masukkan password admin"
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 text-center ${error ? 'border-red-400 focus:ring-red-400' : 'border-slate-200 focus:ring-blue-500'}`}
          />
          {error && <p className="text-red-500 text-sm font-medium">Password salah!</p>}
          <Button type="submit" className="w-full py-3.5">
            Masuk
          </Button>
        </form>
        
        <button
          onClick={() => navigate('/')}
          className="mt-4 text-sm text-slate-400 hover:text-slate-600 transition-colors"
        >
          ← Kembali ke beranda
        </button>
      </div>
    </div>
  );
}

export default App;
