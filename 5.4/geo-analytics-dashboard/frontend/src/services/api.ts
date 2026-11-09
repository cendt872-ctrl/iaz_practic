export interface FilterState {
  category: string;
  object_type: string;
  status: string;
  severity: string;
  date_from: string;
  date_to: string;
  search: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

function buildQuery(params: Record<string, string | number | undefined>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== '') searchParams.set(key, String(val));
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : '';
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Помилка перевірки стану сервера');
  return res.json();
}
export async function fetchSummaryMetrics(filters: Partial<FilterState>) {
  const res = await fetch(`${API_BASE}/metrics/summary${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Не вдалося завантажити KPI метрики');
  return res.json();
}
export async function fetchObjects(filters: Partial<FilterState>) {
  const res = await fetch(`${API_BASE}/objects${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Не вдалося завантажити список об’єктів');
  return res.json();
}
export async function fetchObjectDetail(id: number) {
  const res = await fetch(`${API_BASE}/objects/${id}`);
  if (!res.ok) throw new Error('Не вдалося завантажити деталі об’єкта');
  return res.json();
}
export async function fetchEvents(filters: Partial<FilterState>) {
  const res = await fetch(`${API_BASE}/events${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Не вдалося завантажити журнал подій');
  return res.json();
}
export async function fetchTimeseries(filters: Partial<FilterState>) {
  const res = await fetch(`${API_BASE}/analytics/timeseries${buildQuery({ days: 30, category: filters.category, severity: filters.severity })}`);
  if (!res.ok) throw new Error('Не вдалося завантажити часові ряди');
  return res.json();
}
export async function fetchCategoryAnalytics(filters: Partial<FilterState>) {
  const res = await fetch(`${API_BASE}/analytics/categories${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Не вдалося завантажити аналітику');
  return res.json();
}
export async function fetchMapGeoJson(filters: Partial<FilterState>) {
  const res = await fetch(`${API_BASE}/map/geojson${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Не вдалося завантажити GeoJSON');
  return res.json();
}
export async function fetchOsmFeatures() {
  const res = await fetch(`${API_BASE}/osm/features`);
  if (!res.ok) throw new Error('Не вдалося завантажити OSM');
  return res.json();
}
