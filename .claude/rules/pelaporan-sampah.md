# Frontend Rules — React (pelaporan-sampah/)

Loads automatically when working in `pelaporan-sampah/**` paths.

## Skill Reference

Use `ui-ux-pro-max` skill for:
- Premium design patterns, image-first layouts
- Design token system (`globals.css`)
- Accessibility (WCAG 2.1, 4.5:1 contrast minimum)
- Component architecture and visual hierarchy

Use `frontend-design` skill for general React/Vite best practices.

Location: `~/.agents/skills/ui-ux-pro-max/SKILL.md`

---

## Design System

This frontend uses **TailwindCSS**. Check `pelaporan-sampah/src/app/globals.css` for design token definitions before using custom colors, spacing, or border radii.

### AI Aesthetic Mistakes to Avoid

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| `rounded-xl`, `rounded-lg` | Use tokens from `globals.css` |
| `text-slate-400`, `bg-gray-900` | Use token variables from `globals.css` |
| `shadow-lg shadow-indigo-500/20` | No colored shadows |
| `bg-gradient-to-b from-violet-900/20` | Use solid background colors |
| `animate-pulse` all over | Minimal animation |
| Purple/indigo gradient buttons | White or bordered buttons only |

### Accessibility Requirements

- **Minimum contrast ratio: 4.5:1** for normal text
- Never use `text-white/50` for disabled text — `text-white/70` minimum
- Badge/label backgrounds: ensure sufficient contrast
- Run Lighthouse accessibility audit before PR

## Component Structure

```
pelaporan-sampah/src/
├── components/
│   ├── ui/           # Primitives: Button, Card, Badge, Modal
│   ├── forms/        # Report submission forms
│   ├── maps/         # Leaflet/OpenStreetMap integration (hotspots)
│   └── layout/       # Layout components
├── pages/
│   ├── ReportList.tsx
│   ├── ReportDetail.tsx
│   └── StatsDashboard.tsx
├── hooks/
│   └── useReports.ts
└── lib/
    └── api.ts        # API client
```

## API Client Pattern

```ts
const API_BASE = import.meta.env.VITE_API_URL || "https://your-app.vercel.app"

export const api = {
  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE}/api/v1${path}`)
    if (!res.ok) throw new Error(`API error: ${res.status}`)
    return res.json()
  },
  async patch<T>(path: string, data: unknown): Promise<T> {
    const res = await fetch(`${API_BASE}/api/v1${path}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error(`API error: ${res.status}`)
    return res.json()
  },
}
```

## Report Status Flow

```
BARU → DIVERIFIKASI → DALAM_PROSES → SELESAI → DITUTUP
```

## Waste Categories

| Code | Description | Handler |
|------|-------------|---------|
| `SAMPAH_TERBANG` | Wind-blown litter | DLH |
| `SAMPAH_TIMBUNAN` | Dumped waste | DLH + RT |
| `SAMPAH_MASIF` | Large accumulation | DLH |
| `SAMPAH_SUNGAI` | River pollution | DLH |
| `LAIN_LAIN` | Other | RT/RW |

## Hotspot Map

The `GET /api/v1/reports/hotspots` endpoint returns GeoJSON. Render with Leaflet + OpenStreetMap (no API key required):

```tsx
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function HotspotMap({ geojson }: { geojson: GeoJSON.FeatureCollection }) {
  return (
    <MapContainer center={[-1.3, 120]} zoom={6} className="h-96 w-full">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <GeoJSON data={geojson} />
    </MapContainer>
  )
}
```

## React Query Patterns

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"

function ReportList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["reports"],
    queryFn: () => api.get("/reports"),
  })
  // ...
}
```

## Performance Rules

- Memoize expensive computations: `useMemo`
- Prevent unnecessary re-renders: `React.memo` for pure components
- Lazy load pages: `React.lazy` + `Suspense`
- Images: use `loading="lazy"` and proper aspect ratios

## Naming Conventions

- Components: **PascalCase** — `ReportCard.tsx`
- Utilities: **camelCase** — `formatDate.ts`
- Directories: **kebab-case** — `components/report-card/`
