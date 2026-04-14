import { useState, useEffect, useRef } from 'react';
import { MapPin, X, Clock, AlertTriangle, CheckCircle2 } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const API_BASE = '/api';

const KATEGORI_COLORS = {
  'Sampah': '#6b7280',
  'Banjir': '#3b82f6',
  'Pencemaran Air': '#06b6d4',
  'Pencemaran Udara': '#9ca3af',
  'Fasilitas Rusak': '#f59e0b',
  'Hewan Liar': '#8b5cf6',
  'Pohon Bahaya': '#22c55e',
  'Kebakaran': '#ef4444',
  'Lainnya': '#a855f7',
};

const KATEGORI_ICONS = {
  'Sampah': '🗑️', 'Banjir': '🌊', 'Pencemaran Air': '💧', 'Pencemaran Udara': '🌫️',
  'Fasilitas Rusak': '🔧', 'Hewan Liar': '🐕', 'Pohon Bahaya': '🌳', 'Kebakaran': '🔥', 'Lainnya': '📌',
};

function parseCoords(lokasi) {
  if (!lokasi) return null;
  const parts = lokasi.split(',').map(s => parseFloat(s.trim()));
  if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1]) && Math.abs(parts[0]) <= 90 && Math.abs(parts[1]) <= 180) {
    return { lat: parts[0], lng: parts[1] };
  }
  return null;
}

export function Peta() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [filterKategori, setFilterKategori] = useState('Semua');
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    // Fetch all reports (need location data)
    const fetchAll = async () => {
      let all = [];
      let p = 1;
      while (true) {
        const res = await fetch(`${API_BASE}/laporan?page=${p}`);
        const data = await res.json();
        all = all.concat(data.laporan || []);
        if (p >= (data.pagination?.total_pages || 1)) break;
        p++;
      }
      setReports(all);
      setLoading(false);
    };
    fetchAll();
  }, []);

  useEffect(() => {
    if (loading || !mapRef.current || mapInstanceRef.current) return;

    // Dynamic import leaflet
    import('leaflet').then(L => {
      // Fix default icon
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      const map = L.map(mapRef.current).setView([1.4748, 124.8421], 13); // Manado center
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
      }).addTo(map);
      mapInstanceRef.current = map;
    });
  }, [loading]);

  // Update markers when reports or filter change
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    import('leaflet').then(L => {
      // Clear existing markers
      markersRef.current.forEach(m => m.remove());
      markersRef.current = [];

      const filtered = filterKategori === 'Semua' ? reports : reports.filter(r => r.kategori === filterKategori);
      const withCoords = filtered.filter(r => parseCoords(r.lokasi));

      withCoords.forEach(r => {
        const coords = parseCoords(r.lokasi);
        const color = KATEGORI_COLORS[r.kategori] || '#6b7280';

        const icon = L.divIcon({
          className: 'custom-marker',
          html: `<div style="background:${color};width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);font-size:14px;cursor:pointer">${KATEGORI_ICONS[r.kategori] || '📌'}</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14],
        });

        const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(mapInstanceRef.current);
        marker.on('click', () => setSelectedItem(r));
        markersRef.current.push(marker);
      });

      // Fit bounds if markers exist
      if (withCoords.length > 0) {
        const bounds = withCoords.map(r => {
          const c = parseCoords(r.lokasi);
          return [c.lat, c.lng];
        });
        mapInstanceRef.current.fitBounds(bounds, { padding: [30, 30] });
      }
    });
  }, [reports, filterKategori]);

  const statusBadge = (s) => {
    if (s === 'Menunggu') return 'bg-amber-100 text-amber-700';
    if (s === 'Diproses') return 'bg-blue-100 text-blue-700';
    return 'bg-green-100 text-green-700';
  };

  const reportsWithCoords = reports.filter(r => parseCoords(r.lokasi));
  const reportsWithoutCoords = reports.filter(r => !parseCoords(r.lokasi));

  return (
    <div className="max-w-7xl mx-auto space-y-6 pt-8 pb-12">
      <div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">🗺️ Peta Laporan</h2>
        <p className="text-slate-500 mt-2 font-medium">
          {reportsWithCoords.length} laporan dengan lokasi GPS • {reportsWithoutCoords.length} tanpa koordinat
        </p>
      </div>

      {/* Filter */}
      <div className="flex flex-wrap gap-2">
        {['Semua', ...Object.keys(KATEGORI_COLORS)].map(k => (
          <button key={k} onClick={() => setFilterKategori(k)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer border ${
              filterKategori === k
                ? 'text-white border-transparent'
                : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
            }`}
            style={filterKategori === k ? { backgroundColor: KATEGORI_COLORS[k] || '#6b7280' } : {}}>
            {KATEGORI_ICONS[k] || '📋'} {k}
          </button>
        ))}
      </div>

      {/* Map */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden" style={{ height: '500px' }}>
        {loading ? (
          <div className="flex items-center justify-center h-full text-slate-400">
            <div className="text-center">
              <div className="animate-spin w-8 h-8 border-2 border-slate-300 border-t-green-600 rounded-full mx-auto mb-3"></div>
              <p>Memuat peta...</p>
            </div>
          </div>
        ) : (
          <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
        )}
      </div>

      {/* List without coords */}
      {reportsWithoutCoords.length > 0 && filterKategori === 'Semua' && (
        <div className="space-y-3">
          <h3 className="text-lg font-bold text-slate-900">📋 Tanpa Koordinat ({reportsWithoutCoords.length})</h3>
          <p className="text-sm text-slate-400">Laporan ini belum memiliki lokasi GPS. Upload foto dengan GPS aktif agar muncul di peta.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {reportsWithoutCoords.slice(0, 10).map(item => (
              <div key={item.id} onClick={() => setSelectedItem(item)}
                className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 cursor-pointer hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-sm">{KATEGORI_ICONS[item.kategori] || '📌'}</span>
                    <span className="font-bold text-slate-800 ml-1">#{item.id} {item.nama}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${statusBadge(item.status)}`}>{item.status}</span>
                </div>
                <p className="text-sm text-slate-500 mt-1 flex items-center gap-1"><MapPin size={12} />{item.lokasi}</p>
                <p className="text-xs text-slate-400 mt-1 line-clamp-1">{item.deskripsi}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detail Popup */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            <div className="p-6 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-slate-900">#{selectedItem.id} {selectedItem.nama}</h3>
                <button onClick={() => setSelectedItem(null)} className="p-2 hover:bg-slate-100 rounded-full cursor-pointer"><X size={20} className="text-slate-500" /></button>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusBadge(selectedItem.status)}`}>{selectedItem.status}</span>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600">{KATEGORI_ICONS[selectedItem.kategori] || '📌'} {selectedItem.kategori || 'Sampah'}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${selectedItem.prioritas === 'Tinggi' ? 'bg-red-100 text-red-700' : selectedItem.prioritas === 'Sedang' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>Prioritas {selectedItem.prioritas}</span>
              </div>
              <div className="flex items-start gap-2 text-sm text-slate-600"><MapPin size={16} className="text-rose-500 mt-0.5 flex-shrink-0" />{selectedItem.lokasi}</div>
              <p className="text-sm text-slate-600">{selectedItem.deskripsi}</p>
              <p className="text-xs text-slate-400">{selectedItem.tanggal}</p>
            </div>
            <div className="border-t border-slate-100 p-4">
              <button onClick={() => setSelectedItem(null)} className="w-full py-2.5 rounded-xl font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer">Tutup</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
