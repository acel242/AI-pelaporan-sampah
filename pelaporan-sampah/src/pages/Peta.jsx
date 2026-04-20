import { useState, useEffect, useRef, useCallback } from 'react';
import { MapPin, X, RefreshCw, Layers, Flame, CircleDot } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

const API_BASE = '/api';
const BASE_URL = window.location.origin;

const KATEGORI_COLORS = {
  'Sampah': '#6b7280',
  'Fasilitas Rusak': '#f59e0b',
  'Hewan Liar': '#8b5cf6',
  'Kebakaran': '#ef4444',
  'Lainnya': '#a855f7',
};

const KATEGORI_ICONS = {
  'Sampah': '🗑️', 'Fasilitas Rusak': '🔧', 'Hewan Liar': '🐕', 'Kebakaran': '🔥', 'Lainnya': '📌',
};

function parseCoords(report) {
  if (report.latitude && report.longitude) {
    const lat = parseFloat(report.latitude);
    const lng = parseFloat(report.longitude);
    if (!isNaN(lat) && !isNaN(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180) {
      return { lat, lng };
    }
  }
  if (report.lokasi) {
    const parts = report.lokasi.split(',').map(s => parseFloat(s.trim()));
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1]) && Math.abs(parts[0]) <= 90 && Math.abs(parts[1]) <= 180) {
      return { lat: parts[0], lng: parts[1] };
    }
  }
  return null;
}

const REFRESH_INTERVAL = 15000;

export function Peta() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedGallery, setSelectedGallery] = useState([]);
  const [filterKategori, setFilterKategori] = useState('Semua');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [newCount, setNewCount] = useState(0);
  const [viewMode, setViewMode] = useState('markers'); // 'markers' | 'heatmap' | 'cluster'
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const clusterRef = useRef(null);
  const heatLayerRef = useRef(null);
  const LRef = useRef(null);
  const prevIdsRef = useRef(new Set());

  const fetchAll = useCallback(async () => {
    let all = [];
    let p = 1;
    while (true) {
      const res = await fetch(`${API_BASE}/laporan?page=${p}`);
      const data = await res.json();
      all = all.concat(data.laporan || []);
      if (p >= (data.pagination?.total_pages || 1)) break;
      p++;
    }

    const currentIds = new Set(all.map(r => r.id));
    const newOnes = all.filter(r => !prevIdsRef.current.has(r.id));
    if (prevIdsRef.current.size > 0 && newOnes.length > 0) {
      setNewCount(newOnes.length);
      setTimeout(() => setNewCount(0), 5000);
    }
    prevIdsRef.current = currentIds;

    setReports(all);
    setLastUpdated(new Date());
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchAll]);

  useEffect(() => {
    if (loading || !mapRef.current || mapInstanceRef.current) return;

    Promise.all([
      import('leaflet'),
      import('leaflet.markercluster'),
      import('leaflet.heat')
    ]).then(([L, markerCluster, leafletHeat]) => {
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      const map = L.map(mapRef.current).setView([1.4748, 124.8421], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
      }).addTo(map);
      
      mapInstanceRef.current = map;
      LRef.current = L;
    });
  }, [loading]);

  // Update markers/clusters/heatmap when data or viewMode changes
  useEffect(() => {
    if (!mapInstanceRef.current || !LRef.current) return;
    const L = LRef.current;
    const map = mapInstanceRef.current;

    // Clear existing layers
    if (clusterRef.current) {
      map.removeLayer(clusterRef.current);
      clusterRef.current = null;
    }
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    const filtered = filterKategori === 'Semua' ? reports : reports.filter(r => r.kategori === filterKategori);
    const withCoords = filtered.filter(r => parseCoords(r));

    if (viewMode === 'heatmap') {
      // Heatmap mode
      const heatData = withCoords.map(r => {
        const coords = parseCoords(r);
        const intensity = r.prioritas === 'Tinggi' ? 1.0 : r.prioritas === 'Sedang' ? 0.7 : 0.4;
        return [coords.lat, coords.lng, intensity];
      });
      
      if (heatData.length > 0 && L.heatLayer) {
        heatLayerRef.current = L.heatLayer(heatData, {
          radius: 25,
          blur: 15,
          maxZoom: 17,
          max: 1.0,
          gradient: {0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
        }).addTo(map);
      }
    } else if (viewMode === 'cluster') {
      // Marker cluster mode
      const clusterGroup = L.markerClusterGroup({
        chunkedLoading: true,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: true,
        zoomToBoundsOnClick: true,
        maxClusterRadius: 80,
        iconCreateFunction: function(cluster) {
          const count = cluster.getChildCount();
          return L.divIcon({
            html: `<div style="background:rgba(59,130,246,0.9);color:white;width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:14px;border:3px solid white;box-shadow:0 4px 12px rgba(0,0,0,0.3);">${count}</div>`,
            className: 'marker-cluster',
            iconSize: L.point(40, 40)
          });
        }
      });

      withCoords.forEach(r => {
        const coords = parseCoords(r);
        const color = KATEGORI_COLORS[r.kategori] || '#6b7280';
        const isUrgent = r.status === 'Menunggu' || r.prioritas === 'Tinggi';
        const pulseHtml = isUrgent
          ? `<div style="position:absolute;width:40px;height:40px;border-radius:50%;background:${color};opacity:0.3;animation:pulse 2s infinite;top:-6px;left:-6px;"></div>`
          : '';

        const icon = L.divIcon({
          className: 'custom-marker',
          html: `
            <style>@keyframes pulse{0%{transform:scale(1);opacity:0.3}100%{transform:scale(2);opacity:0}}</style>
            <div style="position:relative;display:flex;align-items:center;justify-content:center;">
              ${pulseHtml}
              <div style="background:${color};width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);font-size:15px;cursor:pointer;position:relative;z-index:1">${KATEGORI_ICONS[r.kategori] || '📌'}</div>
            </div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15],
        });

        const marker = L.marker([coords.lat, coords.lng], { icon });
        
        const popupContent = `
          <div style="min-width:200px;font-family:system-ui">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
              <span style="font-size:20px">${KATEGORI_ICONS[r.kategori] || '📌'}</span>
              <strong style="font-size:14px">#${r.id} ${r.nama || ''}</strong>
            </div>
            <div style="display:flex;gap:4px;margin-bottom:6px">
              <span style="padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:700;background:${r.status === 'Menunggu' ? '#fef3c7;color:#b45309' : r.status === 'Diproses' ? '#dbeafe;color:#1d4ed8' : '#dcfce7;color:#15803d'}">${r.status}</span>
              <span style="padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:700;background:${r.prioritas === 'Tinggi' ? '#fecaca;color:#dc2626' : r.prioritas === 'Sedang' ? '#fef3c7;color:#b45309' : '#dcfce7;color:#15803d'}">${r.prioritas}</span>
            </div>
            <p style="font-size:12px;color:#64748b;margin:0 0 4px">${r.lokasi}</p>
            <p style="font-size:12px;color:#475569;margin:0">${(r.deskripsi || '').substring(0, 80)}${(r.deskripsi || '').length > 80 ? '...' : ''}</p>
            <p style="font-size:10px;color:#94a3b8;margin-top:4px">${r.tanggal || ''}</p>
          </div>`;
        marker.bindPopup(popupContent);
        clusterGroup.addLayer(marker);
      });

      map.addLayer(clusterGroup);
      clusterRef.current = clusterGroup;
    } else {
      // Normal marker mode (default)
      withCoords.forEach(r => {
        const coords = parseCoords(r);
        const color = KATEGORI_COLORS[r.kategori] || '#6b7280';
        const isUrgent = r.status === 'Menunggu' || r.prioritas === 'Tinggi';
        const pulseHtml = isUrgent
          ? `<div style="position:absolute;width:40px;height:40px;border-radius:50%;background:${color};opacity:0.3;animation:pulse 2s infinite;top:-6px;left:-6px;"></div>`
          : '';

        const icon = L.divIcon({
          className: 'custom-marker',
          html: `
            <style>@keyframes pulse{0%{transform:scale(1);opacity:0.3}100%{transform:scale(2);opacity:0}}</style>
            <div style="position:relative;display:flex;align-items:center;justify-content:center;">
              ${pulseHtml}
              <div style="background:${color};width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);font-size:15px;cursor:pointer;position:relative;z-index:1">${KATEGORI_ICONS[r.kategori] || '📌'}</div>
            </div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15],
        });

        const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(map);

        const popupContent = `
          <div style="min-width:200px;font-family:system-ui">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
              <span style="font-size:20px">${KATEGORI_ICONS[r.kategori] || '📌'}</span>
              <strong style="font-size:14px">#${r.id} ${r.nama || ''}</strong>
            </div>
            <div style="display:flex;gap:4px;margin-bottom:6px">
              <span style="padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:700;background:${r.status === 'Menunggu' ? '#fef3c7;color:#b45309' : r.status === 'Diproses' ? '#dbeafe;color:#1d4ed8' : '#dcfce7;color:#15803d'}">${r.status}</span>
              <span style="padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:700;background:${r.prioritas === 'Tinggi' ? '#fecaca;color:#dc2626' : r.prioritas === 'Sedang' ? '#fef3c7;color:#b45309' : '#dcfce7;color:#15803d'}">${r.prioritas}</span>
            </div>
            <p style="font-size:12px;color:#64748b;margin:0 0 4px">${r.lokasi}</p>
            <p style="font-size:12px;color:#475569;margin:0">${(r.deskripsi || '').substring(0, 80)}${(r.deskripsi || '').length > 80 ? '...' : ''}</p>
            <p style="font-size:10px;color:#94a3b8;margin-top:4px">${r.tanggal || ''}</p>
          </div>`;
        marker.bindPopup(popupContent);
        marker.on('click', () => setSelectedItem(r));
        markersRef.current.push(marker);
      });
    }
  }, [reports, filterKategori, viewMode]);

  const openDetail = async (item) => {
    setSelectedItem(item);
    setSelectedGallery([]);
    try {
      const res = await fetch(`${API_BASE}/laporan/${item.id}`);
      const data = await res.json();
      setSelectedItem(data);
      setSelectedGallery(data.gallery || []);
    } catch {}
  };

  const statusBadge = (s) => {
    if (s === 'Menunggu') return 'bg-amber-100 text-amber-700';
    if (s === 'Diproses') return 'bg-blue-100 text-blue-700';
    return 'bg-green-100 text-green-700';
  };

  function resolveImgSrc(val) {
    if (!val) return null;
    if (val.startsWith('data:')) return val;
    if (val.startsWith('/')) return BASE_URL + val;
    return null;
  }

  const reportsWithCoords = reports.filter(r => parseCoords(r));
  const reportsWithoutCoords = reports.filter(r => !parseCoords(r));

  return (
    <div className="max-w-7xl mx-auto space-y-6 pt-8 pb-12">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">🗺️ Peta Laporan</h2>
          <p className="text-slate-500 mt-2 font-medium">
            {reportsWithCoords.length} laporan dengan GPS • {reportsWithoutCoords.length} tanpa koordinat
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {/* View Mode Toggle */}
          <div className="flex bg-white rounded-xl border border-slate-200 p-1 shadow-sm">
            <button
              onClick={() => setViewMode('markers')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5 ${
                viewMode === 'markers' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <MapPin size={14} /> Marker
            </button>
            <button
              onClick={() => setViewMode('cluster')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5 ${
                viewMode === 'cluster' ? 'bg-indigo-100 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <CircleDot size={14} /> Cluster
            </button>
            <button
              onClick={() => setViewMode('heatmap')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5 ${
                viewMode === 'heatmap' ? 'bg-red-100 text-red-700' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Flame size={14} /> Heatmap
            </button>
          </div>

          {newCount > 0 && (
            <span className="px-3 py-1.5 rounded-full text-xs font-bold bg-green-100 text-green-700 animate-pulse">
              🔔 {newCount} laporan baru!
            </span>
          )}
          <button onClick={fetchAll} className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium bg-white border border-slate-200 hover:bg-slate-50 cursor-pointer transition-colors">
            <RefreshCw size={14} className={lastUpdated ? '' : 'animate-spin'} />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-slate-400">
        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
        Real-time • Auto refresh setiap 15 detik
        {lastUpdated && <span className="ml-1">• Terakhir: {lastUpdated.toLocaleTimeString('id-ID')}</span>}
      </div>

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

      <div className="flex flex-wrap gap-4 bg-white rounded-xl p-4 border border-slate-100">
        <span className="text-xs font-semibold text-slate-400 uppercase">Keterangan:</span>
        {Object.entries(KATEGORI_COLORS).map(([k, c]) => (
          <div key={k} className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ background: c }}></span>
            <span className="text-xs text-slate-600">{k}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-amber-500 animate-pulse"></span>
          <span className="text-xs text-slate-600">Menunggu / Prioritas Tinggi</span>
        </div>
      </div>

      {reportsWithoutCoords.length > 0 && filterKategori === 'Semua' && (
        <div className="space-y-3">
          <h3 className="text-lg font-bold text-slate-900">📋 Tanpa Koordinat ({reportsWithoutCoords.length})</h3>
          <p className="text-sm text-slate-400">Laporan ini belum memiliki lokasi GPS. Upload foto dengan GPS aktif agar muncul di peta.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {reportsWithoutCoords.slice(0, 10).map(item => (
              <div key={item.id} onClick={() => openDetail(item)}
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

      {selectedItem && (() => {
        const beforePhotos = selectedGallery.filter(g => g.photo_type === 'before');
        const afterPhotos = selectedGallery.filter(g => g.photo_type === 'after');
        const beforeGallerySrc = beforePhotos.length > 0
          ? (beforePhotos[0].foto_url?.startsWith('/') ? BASE_URL + beforePhotos[0].foto_url : beforePhotos[0].foto_url)
          : null;
        const beforeBase64Src = resolveImgSrc(selectedItem.foto);
        const hasBefore = beforeGallerySrc || beforeBase64Src;

        return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={() => setSelectedItem(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="sticky top-0 bg-white rounded-t-2xl border-b border-slate-100 p-5 flex items-center justify-between z-10">
              <div>
                <h3 className="text-lg font-bold text-slate-900">#{selectedItem.id} {selectedItem.nama}</h3>
                <div className="flex gap-2 mt-1">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${statusBadge(selectedItem.status)}`}>{selectedItem.status}</span>
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600">{KATEGORI_ICONS[selectedItem.kategori] || '📌'} {selectedItem.kategori}</span>
                </div>
              </div>
              <button onClick={() => setSelectedItem(null)} className="p-2 hover:bg-slate-100 rounded-full cursor-pointer"><X size={20} className="text-slate-500" /></button>
            </div>
            <div className="p-5 space-y-4">
              {hasBefore && (
                <div className="space-y-2">
                  <p className="text-sm font-bold text-slate-700">📸 Sebelum & Sesudah</p>
                  <div className={`grid ${afterPhotos.length > 0 ? 'grid-cols-2' : 'grid-cols-1'} gap-2`}>
                    <div className="relative">
                      <div className="absolute top-1.5 left-1.5 z-10 px-1.5 py-0.5 rounded text-[10px] font-bold text-white bg-amber-500">📷 SEBELUM</div>
                      {beforeGallerySrc ? (
                        <img src={beforeGallerySrc} alt="Sebelum" className="w-full rounded-lg object-cover h-36 bg-slate-100"
                          onError={e => { if (beforeBase64Src) e.target.src = beforeBase64Src; else e.target.style.display='none'; }} />
                      ) : beforeBase64Src ? (
                        <img src={beforeBase64Src} alt="Sebelum" className="w-full rounded-lg object-cover h-36 bg-slate-100"
                          onError={e => { e.target.style.display='none'; }} />
                      ) : null}
                    </div>
                    {afterPhotos.length > 0 ? (
                      <div className="relative">
                        <div className="absolute top-1.5 left-1.5 z-10 px-1.5 py-0.5 rounded text-[10px] font-bold text-white bg-green-500">✅ SESUDAH</div>
                        <img src={afterPhotos[0].foto_url?.startsWith('/') ? BASE_URL + afterPhotos[0].foto_url : afterPhotos[0].foto_url}
                          alt="Sesudah" className="w-full rounded-lg object-cover h-36 bg-slate-100" onError={e => { e.target.style.display='none'; }} />
                      </div>
                    ) : (
                      <div className="relative">
                        <div className="absolute top-1.5 left-1.5 z-10 px-1.5 py-0.5 rounded text-[10px] font-bold text-white bg-slate-400">⏳ SESUDAH</div>
                        <div className="w-full rounded-lg h-36 bg-slate-50 flex flex-col items-center justify-center border-2 border-dashed border-slate-200">
                          <p className="text-xs text-slate-400">Menunggu penanganan</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              <div className="flex items-start gap-2 text-sm text-slate-600"><MapPin size={16} className="text-rose-500 mt-0.5 flex-shrink-0" />{selectedItem.lokasi}</div>
              <p className="text-sm text-slate-600">{selectedItem.deskripsi}</p>
              <div className="flex items-center justify-between">
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${selectedItem.prioritas === 'Tinggi' ? 'bg-red-100 text-red-700' : selectedItem.prioritas === 'Sedang' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>Prioritas {selectedItem.prioritas}</span>
                <span className="text-xs text-slate-400">{selectedItem.tanggal}</span>
              </div>
              {selectedItem.catatan && (
                <div className="bg-slate-50 rounded-lg p-3"><p className="text-xs font-semibold text-slate-400 uppercase mb-0.5">Catatan</p><p className="text-sm text-slate-700">{selectedItem.catatan}</p></div>
              )}
            </div>
            <div className="border-t border-slate-100 p-4">
              <button onClick={() => setSelectedItem(null)} className="w-full py-2.5 rounded-xl font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer">Tutup</button>
            </div>
          </div>
        </div>
        );
      })()}
    </div>
  );
}