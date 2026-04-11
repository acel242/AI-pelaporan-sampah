import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Warga } from './pages/Warga';
import { Admin } from './pages/Admin';
import { LogOut, Leaf } from 'lucide-react';
import { Button } from './components/Button';

const dummyData = [
  {
    id: 1,
    nama: "Hendrik P",
    lokasi: "Jl. Gatot Subroto no 21",
    deskripsi: "Tumpukan sampah plastik menutupi trotoar, tolong segera dibersihkan.",
    status: "Menunggu",
    tanggal: "11/4/2026"
  },
  {
    id: 2,
    nama: "Nisa Aulia",
    lokasi: "Alun-alun Kota sisi timur",
    deskripsi: "Sampah sisa acara belum diangkut sejak semalam.",
    status: "Selesai",
    tanggal: "10/4/2026"
  }
];

function Navbar({ role, onLogout }) {
  if (!role) return null;
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

function App() {
  const [laporan, setLaporan] = useState(dummyData);
  const [userRole, setUserRole] = useState(null);
  const navigate = useNavigate();

  const handleLogin = (role) => {
    setUserRole(role);
    if (role === 'warga') navigate('/warga');
    if (role === 'admin') navigate('/admin');
  };

  const handleLogout = () => {
    setUserRole(null);
    navigate('/');
  };

  const handleAddLaporan = (newLaporan) => {
    setLaporan([newLaporan, ...laporan]);
  };

  // Protective routing logic
  useEffect(() => {
    const currentPath = window.location.pathname;
    if (!userRole && currentPath !== '/') {
        navigate('/');
    }
  }, [userRole, navigate]);

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-blue-100">
      <Navbar role={userRole} onLogout={handleLogout} />
      <main className="px-4">
        <Routes>
          <Route path="/" element={<Login onLogin={handleLogin} />} />
          <Route 
            path="/warga" 
            element={userRole === 'warga' ? <Warga addLaporan={handleAddLaporan} /> : <Navigate to="/" />} 
          />
          <Route 
            path="/admin" 
            element={userRole === 'admin' ? <Admin laporan={laporan} /> : <Navigate to="/" />} 
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
