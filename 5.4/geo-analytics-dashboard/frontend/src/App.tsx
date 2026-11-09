import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { UafTridentLogo } from './components/UafTridentLogo';
import { TacticalMap } from './map/TacticalMap';
import { renderMilsymbolSvg } from './map/MilsymbolFactory';
import { AnalyticsCharts } from './charts/AnalyticsCharts';
import { FilterState, fetchHealth, fetchSummaryMetrics, fetchObjects, fetchObjectDetail, fetchEvents, fetchTimeseries, fetchCategoryAnalytics, fetchMapGeoJson, fetchOsmFeatures } from './services/api';

const h = React.createElement;

const INITIAL_FILTERS: FilterState = { category: '', object_type: '', status: '', severity: '', date_from: '', date_to: '', search: '' };
const CATEGORIES = ['Сухопутні війська', 'Повітряні Сили', 'Військово-Морські Сили', 'Десантно-штурмові війська', 'Сили спеціальних операцій', 'Сили територіальної оборони', 'Морська піхота', 'Військова служба правопорядку'];

export const App: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);
  const [currentTime, setCurrentTime] = useState<string>(new Date().toLocaleString('uk-UA'));
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [objects, setObjects] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [timeseries, setTimeseries] = useState<any[]>([]);
  const [categoriesData, setCategoriesData] = useState<any>(null);
  const [areasGeoJson, setAreasGeoJson] = useState<any[]>([]);
  const [osmFeatures, setOsmFeatures] = useState<any[]>([]);
  const [selectedObject, setSelectedObject] = useState<any | null>(null);
  const [objectDetail, setObjectDetail] = useState<any | null>(null);
  const [sortField, setSortField] = useState<'id' | 'name' | 'category' | 'status'>('id');
  const [sortAsc, setSortAsc] = useState<boolean>(true);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date().toLocaleString('uk-UA')), 1000);
    return () => clearInterval(timer);
  }, []);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [hRes, mRes, oRes, evRes, tsRes, catRes, gjRes, osmRes] = await Promise.all([
        fetchHealth(),
        fetchSummaryMetrics(filters),
        fetchObjects(filters),
        fetchEvents(filters),
        fetchTimeseries(filters),
        fetchCategoryAnalytics(filters),
        fetchMapGeoJson(filters),
        fetchOsmFeatures(),
      ]);
      setHealth(hRes);
      setMetrics(mRes);
      setObjects(oRes);
      setEvents(evRes);
      setTimeseries(tsRes);
      setCategoriesData(catRes);
      setAreasGeoJson((gjRes.features || []).filter((f: any) => f.properties.layer === 'areas'));
      setOsmFeatures(osmRes.features || []);
    } catch (err: any) {
      setError(err.message || 'Помилка з’єднання з FastAPI');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleSelectObject = async (obj: any) => {
    setSelectedObject(obj);
    try {
      setObjectDetail(await fetchObjectDetail(obj.id));
    } catch {
      setObjectDetail(obj);
    }
  };

  const sortedObjects = useMemo(() => {
    const copy = [...objects];
    copy.sort((a, b) => (a[sortField] < b[sortField] ? (sortAsc ? -1 : 1) : a[sortField] > b[sortField] ? (sortAsc ? 1 : -1) : 0));
    return copy;
  }, [objects, sortField, sortAsc]);

  const toggleSort = (field: 'id' | 'name' | 'category' | 'status') => {
    if (sortField === field) setSortAsc(!sortAsc);
    else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const kpiCard = (label: string, val: any, borderCls: string) =>
    h(
      'div',
      { className: `bg-uaf-panel border-l-4 ${borderCls} p-4 rounded shadow` },
      h('div', { className: 'text-xs text-stone-400 uppercase' }, label),
      h('div', { className: 'text-3xl font-bold text-white mt-1' }, val ?? '—')
    );

  return h(
    'div',
    { className: 'min-h-screen flex flex-col bg-uaf-darkbg text-stone-100' },
    // Шапка
    h(
      'header',
      { className: 'bg-uaf-mundyr border-b-2 border-uaf-gold px-6 py-3 flex flex-wrap items-center justify-between gap-4 shadow-md' },
      h(
        'div',
        { className: 'flex items-center gap-3.5' },
        h(UafTridentLogo, { className: 'w-11 h-11' }),
        h(
          'div',
          null,
          h(
            'div',
            { className: 'flex items-center gap-2' },
            h('span', { className: 'text-xs uppercase tracking-widest px-2 py-0.5 bg-uaf-gold text-black font-bold rounded-sm' }, 'Збройні Сили України'),
            h('span', { className: 'text-xs text-stone-300 border border-stone-500 px-2 py-0.5 rounded-sm' }, 'СИНТЕТИЧНИЙ КОНТУР (ДЕМО)')
          ),
          h('h1', { className: 'text-lg md:text-xl font-bold text-white mt-0.5' }, 'Інформаційно-аналітична система геопросторового моніторингу')
        )
      ),
      h(
        'div',
        { className: 'flex flex-wrap items-center gap-4 text-xs' },
        h('div', { className: 'bg-uaf-darkbg/70 px-3 py-1.5 rounded border border-stone-600' }, `PostGIS: ${health?.database_connected ? 'ПІДКЛЮЧЕНО' : 'ОЧІКУВАННЯ'}`),
        h('div', { className: 'bg-uaf-darkbg/70 px-3 py-1.5 rounded border border-stone-600 font-mono' }, currentTime),
        h(
          'button',
          {
            onClick: loadDashboardData,
            className: 'bg-uaf-gold hover:bg-amber-500 text-black font-bold px-3.5 py-1.5 rounded transition',
          },
          loading ? 'Оновлення...' : 'Оновити дані'
        )
      )
    ),
    // Основний контент
    h(
      'main',
      { className: 'flex-1 p-6 space-y-6 max-w-[1920px] w-full mx-auto' },
      error && h('div', { className: 'bg-uaf-maroon border border-uaf-vspred text-white px-4 py-3 rounded text-sm' }, error),
      // KPI
      h(
        'section',
        { className: 'grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4' },
        kpiCard("Усього об'єктів", metrics?.total_objects, 'border-uaf-gold'),
        kpiCard("Активних об'єктів", metrics?.active_objects, 'border-uaf-step'),
        kpiCard('Зареєстровано подій', metrics?.total_events, 'border-uaf-wave'),
        kpiCard('Відкритих подій', metrics?.open_events, 'border-uaf-vspred'),
        kpiCard('Обсяг ресурсів', metrics?.total_resources_units, 'border-uaf-steel'),
        kpiCard('Доступність ресурсів', metrics ? `${metrics.resource_availability_pct}%` : '—', 'border-uaf-gold')
      ),
      // Фільтри
      h(
        'section',
        { className: 'bg-uaf-panel border border-uaf-mundyr p-4 rounded shadow space-y-3' },
        h(
          'div',
          { className: 'flex items-center justify-between' },
          h('span', { className: 'text-sm font-semibold text-uaf-gold uppercase' }, 'Фільтрація геопросторових та аналітичних даних'),
          h('button', { onClick: () => setFilters(INITIAL_FILTERS), className: 'text-xs text-stone-300 hover:text-uaf-gold underline' }, 'Скинути фільтри')
        ),
        h(
          'div',
          { className: 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs' },
          h(
            'select',
            {
              value: filters.category,
              onChange: (e: any) => setFilters({ ...filters, category: e.target.value }),
              className: 'bg-uaf-darkbg border border-uaf-mundyr rounded px-2.5 py-2 text-stone-100',
            },
            h('option', { value: '' }, 'Усі види та Сили ЗСУ'),
            ...CATEGORIES.map((c) => h('option', { key: c, value: c }, c))
          ),
          h(
            'select',
            {
              value: filters.status,
              onChange: (e: any) => setFilters({ ...filters, status: e.target.value }),
              className: 'bg-uaf-darkbg border border-uaf-mundyr rounded px-2.5 py-2 text-stone-100',
            },
            h('option', { value: '' }, 'Усі статуси'),
            h('option', { value: 'active' }, 'Активний (active)'),
            h('option', { value: 'standby' }, 'Резерв (standby)'),
            h('option', { value: 'maintenance' }, 'Обслуговування (maintenance)'),
            h('option', { value: 'relocating' }, 'Переміщення (relocating)')
          ),
          h(
            'select',
            {
              value: filters.severity,
              onChange: (e: any) => setFilters({ ...filters, severity: e.target.value }),
              className: 'bg-uaf-darkbg border border-uaf-mundyr rounded px-2.5 py-2 text-stone-100',
            },
            h('option', { value: '' }, 'Усі рівні важливості подій'),
            h('option', { value: 'critical' }, 'Критичний'),
            h('option', { value: 'high' }, 'Високий'),
            h('option', { value: 'medium' }, 'Середній'),
            h('option', { value: 'low' }, 'Низький')
          ),
          h('input', {
            type: 'text',
            placeholder: 'Пошук за кодом або назвою...',
            value: filters.search,
            onChange: (e: any) => setFilters({ ...filters, search: e.target.value }),
            className: 'w-full bg-uaf-darkbg border border-uaf-mundyr rounded px-3 py-2 text-stone-100',
          })
        )
      ),
      // Карта + Деталі
      h(
        'section',
        { className: 'grid grid-cols-1 lg:grid-cols-4 gap-6' },
        h(
          'div',
          { className: 'lg:col-span-3' },
          h(TacticalMap, {
            objects,
            events,
            areasGeoJson,
            osmFeatures,
            selectedObject,
            onSelectObject: handleSelectObject,
          })
        ),
        h(
          'div',
          { className: 'bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow flex flex-col justify-between' },
          objectDetail
            ? h(
                'div',
                { className: 'space-y-3 text-xs' },
                h(
                  'div',
                  { className: 'flex items-start justify-between border-b border-uaf-mundyr pb-2' },
                  h(
                    'div',
                    null,
                    h('span', { className: 'font-mono bg-uaf-mundyr text-uaf-gold px-2 py-0.5 rounded' }, objectDetail.code),
                    h('h2', { className: 'text-sm font-bold text-white mt-1' }, objectDetail.name)
                  ),
                  h('div', {
                    className: 'w-11 h-11 flex items-center justify-center bg-uaf-darkbg rounded border border-uaf-mundyr',
                    dangerouslySetInnerHTML: { __html: renderMilsymbolSvg({ sidc: objectDetail.sidc, size: 32, status: objectDetail.status }) },
                  })
                ),
                h('div', null, `Категорія: ${objectDetail.category}`),
                h('div', null, `Статус: ${objectDetail.status}`),
                h('div', null, `SIDC: ${objectDetail.sidc}`),
                h('div', null, `Орієнтир OSM: ${objectDetail.osm_feature_name || '—'}`),
                h('div', null, `Зона: ${objectDetail.area_name || '—'}`)
              )
            : h('div', { className: 'my-auto text-center py-12 text-xs text-stone-400' }, 'Оберіть умовний знак milsymbol на карті або в таблиці для перегляду паспорта об’єкта.'),
          h(
            'div',
            { className: 'pt-2 border-t border-uaf-mundyr text-[11px] text-stone-400 flex justify-between' },
            h('span', null, 'is_synthetic = true'),
            h('span', { className: 'text-uaf-gold font-semibold' }, 'zsu.gov.ua')
          )
        )
      ),
      // Графіки
      h(
        'section',
        { className: 'space-y-3' },
        h('h2', { className: 'text-base font-bold text-white uppercase' }, 'Аналітичні показники (дані PostgreSQL/PostGIS)'),
        h(AnalyticsCharts, { timeseries, categoriesData })
      ),
      // Таблиця
      h(
        'section',
        { className: 'bg-uaf-panel border border-uaf-mundyr rounded shadow overflow-hidden' },
        h(
          'div',
          { className: 'overflow-x-auto max-h-96' },
          h(
            'table',
            { className: 'w-full text-left border-collapse text-xs' },
            h(
              'thead',
              { className: 'bg-uaf-mundyr text-stone-200 sticky top-0' },
              h(
                'tr',
                null,
                h('th', { className: 'p-3' }, 'milsymbol'),
                h('th', { className: 'p-3 cursor-pointer', onClick: () => toggleSort('id') }, 'Код'),
                h('th', { className: 'p-3 cursor-pointer', onClick: () => toggleSort('name') }, 'Назва'),
                h('th', { className: 'p-3 cursor-pointer', onClick: () => toggleSort('category') }, 'Вид / Сили'),
                h('th', { className: 'p-3 cursor-pointer', onClick: () => toggleSort('status') }, 'Статус'),
                h('th', { className: 'p-3' }, 'Координати'),
                h('th', { className: 'p-3 text-right' }, 'Карта')
              )
            ),
            h(
              'tbody',
              { className: 'divide-y divide-uaf-mundyr/60' },
              ...sortedObjects.map((obj) =>
                h(
                  'tr',
                  { key: obj.id, className: 'hover:bg-uaf-mundyr/40' },
                  h(
                    'td',
                    { className: 'p-2.5' },
                    h('div', {
                      className: 'w-8 h-8 flex items-center justify-center',
                      dangerouslySetInnerHTML: { __html: renderMilsymbolSvg({ sidc: obj.sidc, size: 22, status: obj.status }) },
                    })
                  ),
                  h('td', { className: 'p-2.5 font-mono text-uaf-gold' }, obj.code),
                  h('td', { className: 'p-2.5' }, obj.name),
                  h('td', { className: 'p-2.5' }, obj.category),
                  h('td', { className: 'p-2.5 uppercase font-semibold' }, obj.status),
                  h('td', { className: 'p-2.5 font-mono' }, `${obj.latitude.toFixed(4)}, ${obj.longitude.toFixed(4)}`),
                  h(
                    'td',
                    { className: 'p-2.5 text-right' },
                    h(
                      'button',
                      {
                        onClick: () => handleSelectObject(obj),
                        className: 'bg-uaf-gold text-black font-semibold px-2.5 py-1 rounded-sm',
                      },
                      'На карті'
                    )
                  )
                )
              )
            )
          )
        )
      )
    )
  );
};

export default App;
