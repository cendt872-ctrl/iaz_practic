import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, Polyline, CircleMarker, useMap } from 'react-leaflet';
import { createMilsymbolLeafletIcon, renderMilsymbolSvg, MILSYMBOL_LEGEND_ITEMS } from './MilsymbolFactory';

const h = React.createElement;

const FlyToSelected = ({ selectedObject }: { selectedObject: any }) => {
  const map = useMap();
  useEffect(() => {
    if (selectedObject && selectedObject.latitude && selectedObject.longitude) {
      map.flyTo([selectedObject.latitude, selectedObject.longitude], 10, { duration: 1.0 });
    }
  }, [selectedObject, map]);
  return null;
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#E52421',
  high: '#F39200',
  medium: '#035C6B',
  low: '#6A653A',
};

export const TacticalMap = ({ objects, events, areasGeoJson, osmFeatures, selectedObject, onSelectObject }: any) => {
  const [showObjects, setShowObjects] = useState(true);
  const [showEvents, setShowEvents] = useState(true);
  const [showAreas, setShowAreas] = useState(true);
  const [showOsm, setShowOsm] = useState(true);
  const [symbolSize, setSymbolSize] = useState(30);

  return h(
    'div',
    { className: 'relative w-full h-[560px] rounded border border-uaf-mundyr overflow-hidden shadow-lg bg-uaf-eskadra' },
    // Панель шарів
    h(
      'div',
      { className: 'absolute top-3 right-3 z-[1000] bg-uaf-panel/95 border border-uaf-mundyr p-3 rounded shadow-md text-xs space-y-2 max-w-xs' },
      h('div', { className: 'font-semibold text-uaf-gold uppercase border-b border-uaf-mundyr pb-1' }, 'Шари карти PostGIS / OSM'),
      h(
        'label',
        { className: 'flex items-center gap-2 cursor-pointer' },
        h('input', { type: 'checkbox', checked: showObjects, onChange: (e: any) => setShowObjects(e.target.checked) }),
        h('span', null, `Об'єкти milsymbol (${objects.length})`)
      ),
      h(
        'label',
        { className: 'flex items-center gap-2 cursor-pointer' },
        h('input', { type: 'checkbox', checked: showEvents, onChange: (e: any) => setShowEvents(e.target.checked) }),
        h('span', null, `Синтетичні події (${events.length})`)
      ),
      h(
        'label',
        { className: 'flex items-center gap-2 cursor-pointer' },
        h('input', { type: 'checkbox', checked: showAreas, onChange: (e: any) => setShowAreas(e.target.checked) }),
        h('span', null, `Зони моніторингу (${areasGeoJson.length})`)
      ),
      h(
        'label',
        { className: 'flex items-center gap-2 cursor-pointer' },
        h('input', { type: 'checkbox', checked: showOsm, onChange: (e: any) => setShowOsm(e.target.checked) }),
        h('span', null, `Орієнтири OSM (${osmFeatures.length})`)
      ),
      h(
        'div',
        { className: 'pt-1' },
        h('div', { className: 'text-[11px] text-stone-300 mb-1' }, `Масштаб milsymbol: ${symbolSize}px`),
        h('input', {
          type: 'range',
          min: 22,
          max: 44,
          value: symbolSize,
          onChange: (e: any) => setSymbolSize(Number(e.target.value)),
          className: 'w-full',
        })
      )
    ),
    // Легенда milsymbol
    h(
      'div',
      { className: 'absolute bottom-7 left-3 z-[1000] bg-uaf-panel/95 border border-uaf-mundyr p-3 rounded shadow-md text-xs max-w-xs max-h-60 overflow-y-auto' },
      h('div', { className: 'font-semibold text-uaf-gold uppercase border-b border-uaf-mundyr pb-1 mb-2' }, 'Легенда milsymbol (APP-6)'),
      h(
        'div',
        { className: 'space-y-1.5' },
        ...MILSYMBOL_LEGEND_ITEMS.map((item) =>
          h(
            'div',
            { key: item.type, className: 'flex items-center gap-2' },
            h('div', {
              className: 'w-8 h-8 flex items-center justify-center shrink-0',
              dangerouslySetInnerHTML: { __html: renderMilsymbolSvg({ sidc: item.sidc, size: 22 }) },
            }),
            h(
              'div',
              null,
              h('div', { className: 'font-medium text-stone-100 leading-tight' }, item.label),
              h('div', { className: 'text-[10px] text-stone-400 font-mono' }, item.sidc)
            )
          )
        )
      )
    ),
    // MapContainer (center 48.537, 31.168, zoom 7)
    h(
      MapContainer as any,
      { center: [48.537, 31.168], zoom: 7, className: 'w-full h-full z-10', scrollWheelZoom: true },
      h(TileLayer as any, {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap contributors</a>',
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      }),
      h(FlyToSelected, { selectedObject }),
      showAreas &&
        areasGeoJson.map((areaFeat: any) => {
          const coords = areaFeat.geometry.coordinates[0].map((c: number[]) => [c[1], c[0]]);
          return h(
            Polygon as any,
            {
              key: areaFeat.id,
              positions: coords,
              pathOptions: { color: '#F39200', weight: 1.5, fillColor: '#4D4634', fillOpacity: 0.18 },
            },
            h(Popup as any, null, h('div', { className: 'text-xs font-bold text-uaf-gold' }, areaFeat.properties.name))
          );
        }),
      showOsm &&
        osmFeatures.map((feat: any) => {
          const geom = feat.geometry;
          const props = feat.properties;
          if (geom.type === 'Point') {
            return h(
              CircleMarker as any,
              {
                key: feat.id,
                center: [geom.coordinates[1], geom.coordinates[0]],
                radius: 5,
                pathOptions: { color: '#293757', fillColor: '#38BDF8', fillOpacity: 0.85 },
              },
              h(Popup as any, null, h('div', { className: 'text-xs font-bold text-sky-400' }, `OSM: ${props.name}`))
            );
          }
          if (geom.type === 'LineString') {
            const positions = geom.coordinates.map((c: number[]) => [c[1], c[0]]);
            return h(Polyline as any, {
              key: feat.id,
              positions,
              pathOptions: { color: '#035C6B', weight: 3, opacity: 0.75 },
            });
          }
          return null;
        }),
      showEvents &&
        events.slice(0, 80).map((ev: any) =>
          h(
            CircleMarker as any,
            {
              key: `ev-${ev.id}`,
              center: [ev.latitude, ev.longitude],
              radius: 6,
              pathOptions: {
                color: '#111224',
                weight: 1.5,
                fillColor: SEVERITY_COLORS[ev.severity] || '#F39200',
                fillOpacity: 0.9,
              },
            },
            h(
              Popup as any,
              null,
              h(
                'div',
                { className: 'text-xs space-y-1' },
                h('div', { className: 'font-bold text-uaf-gold' }, ev.title),
                h('div', null, ev.description)
              )
            )
          )
        ),
      showObjects &&
        objects.map((obj: any) => {
          const isSelected = selectedObject && selectedObject.id === obj.id;
          const icon = createMilsymbolLeafletIcon({
            sidc: obj.sidc,
            size: isSelected ? symbolSize + 8 : symbolSize,
            uniqueDesignation: obj.code.replace('UAF-SYN-', ''),
            status: obj.status,
            selected: isSelected,
          });
          return h(
            Marker as any,
            {
              key: `obj-${obj.id}`,
              position: [obj.latitude, obj.longitude],
              icon,
              eventHandlers: { click: () => onSelectObject(obj) },
            },
            h(
              Popup as any,
              null,
              h(
                'div',
                { className: 'text-xs space-y-1' },
                h('div', { className: 'font-bold text-uaf-gold' }, obj.name),
                h('div', null, `Код: ${obj.code}`),
                h('div', null, `SIDC: ${obj.sidc}`),
                h('div', null, `Вид: ${obj.category}`),
                h('div', null, `Статус: ${obj.status}`)
              )
            )
          );
        })
    )
  );
};
