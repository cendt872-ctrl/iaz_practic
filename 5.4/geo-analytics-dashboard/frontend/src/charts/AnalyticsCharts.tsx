import React from 'react';
import { ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const h = React.createElement;
const UAF_PALETTE = ['#F39200', '#6A653A', '#035C6B', '#293757', '#671318', '#707276', '#444A38', '#E52421'];

export const AnalyticsCharts = ({ timeseries, categoriesData }: { timeseries: any[]; categoriesData: any }) => {
  if (!categoriesData) return null;

  const card = (title: string, chartEl: any) =>
    h(
      'div',
      { className: 'bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow' },
      h('h3', { className: 'text-sm font-semibold text-uaf-gold uppercase mb-3' }, title),
      h('div', { className: 'h-60' }, h(ResponsiveContainer as any, { width: '100%', height: '100%' }, chartEl))
    );

  return h(
    'div',
    { className: 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4' },
    card(
      '1. Динаміка кількості подій (30 діб)',
      h(
        AreaChart as any,
        { data: timeseries },
        h(CartesianGrid as any, { strokeDasharray: '3 3', stroke: '#4D4634' }),
        h(XAxis as any, { dataKey: 'date', tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(YAxis as any, { tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(Tooltip as any, { contentStyle: { backgroundColor: '#1E1C16', borderColor: '#F39200' } }),
        h(Legend as any),
        h(Area as any, { type: 'monotone', dataKey: 'events_count', name: 'Усього подій', stroke: '#F39200', fill: '#F39200', fillOpacity: 0.35 }),
        h(Area as any, { type: 'monotone', dataKey: 'critical_events', name: 'Критичні', stroke: '#E52421', fill: '#E52421', fillOpacity: 0.45 })
      )
    ),
    card(
      '2. Розподіл об’єктів за видами та Силами',
      h(
        BarChart as any,
        { data: categoriesData.by_category, layout: 'vertical' },
        h(CartesianGrid as any, { strokeDasharray: '3 3', stroke: '#4D4634' }),
        h(XAxis as any, { type: 'number', tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(YAxis as any, { type: 'category', dataKey: 'name', width: 120, tick: { fill: '#D6D3D1', fontSize: 10 } }),
        h(Tooltip as any, { contentStyle: { backgroundColor: '#1E1C16', borderColor: '#F39200' } }),
        h(
          Bar as any,
          { dataKey: 'value', name: 'Кількість об’єктів', fill: '#6A653A' },
          ...(categoriesData.by_category || []).map((_: any, i: number) => h(Cell as any, { key: i, fill: UAF_PALETTE[i % UAF_PALETTE.length] }))
        )
      )
    ),
    card(
      '3. Розподіл об’єктів за статусами',
      h(
        PieChart as any,
        null,
        h(
          Pie as any,
          { data: categoriesData.by_status, dataKey: 'value', nameKey: 'name', cx: '50%', cy: '50%', innerRadius: 45, outerRadius: 75, label: true },
          ...(categoriesData.by_status || []).map((_: any, i: number) => h(Cell as any, { key: i, fill: UAF_PALETTE[i % UAF_PALETTE.length] }))
        ),
        h(Tooltip as any, { contentStyle: { backgroundColor: '#1E1C16', borderColor: '#F39200' } }),
        h(Legend as any)
      )
    ),
    card(
      '4. Динаміка індексу готовності та змін стану',
      h(
        LineChart as any,
        { data: timeseries },
        h(CartesianGrid as any, { strokeDasharray: '3 3', stroke: '#4D4634' }),
        h(XAxis as any, { dataKey: 'date', tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(YAxis as any, { tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(Tooltip as any, { contentStyle: { backgroundColor: '#1E1C16', borderColor: '#F39200' } }),
        h(Legend as any),
        h(Line as any, { type: 'monotone', dataKey: 'readiness_index', name: 'Готовність (%)', stroke: '#F39200', strokeWidth: 2, dot: false }),
        h(Line as any, { type: 'monotone', dataKey: 'status_changes', name: 'Зміни станів', stroke: '#035C6B', strokeWidth: 2 })
      )
    ),
    card(
      '5. Баланс доступних і задіяних ресурсів',
      h(
        BarChart as any,
        { data: categoriesData.resources_comparison },
        h(CartesianGrid as any, { strokeDasharray: '3 3', stroke: '#4D4634' }),
        h(XAxis as any, { dataKey: 'name', tick: { fill: '#D6D3D1', fontSize: 10 } }),
        h(YAxis as any, { tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(Tooltip as any, { contentStyle: { backgroundColor: '#1E1C16', borderColor: '#F39200' } }),
        h(Legend as any),
        h(Bar as any, { dataKey: 'value', name: 'Доступно', stackId: 'a', fill: '#6A653A' }),
        h(Bar as any, { dataKey: 'extra', name: 'У використанні', stackId: 'a', fill: '#F39200' })
      )
    ),
    card(
      '6. Розподіл подій за рівнями важливості',
      h(
        BarChart as any,
        { data: categoriesData.by_severity },
        h(CartesianGrid as any, { strokeDasharray: '3 3', stroke: '#4D4634' }),
        h(XAxis as any, { dataKey: 'name', tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(YAxis as any, { tick: { fill: '#D6D3D1', fontSize: 11 } }),
        h(Tooltip as any, { contentStyle: { backgroundColor: '#1E1C16', borderColor: '#F39200' } }),
        h(Bar as any, { dataKey: 'value', name: 'Кількість подій', fill: '#F39200' })
      )
    )
  );
};
