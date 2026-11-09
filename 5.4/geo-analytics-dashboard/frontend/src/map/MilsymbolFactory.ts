import ms from 'milsymbol';
import L from 'leaflet';

export interface MilsymbolOptions {
  sidc: string;
  size?: number;
  uniqueDesignation?: string;
  higherFormation?: string;
  status?: string;
  selected?: boolean;
}

export function renderMilsymbolSvg(options: MilsymbolOptions): string {
  const { sidc, size = 32, uniqueDesignation = '', higherFormation = '', status = 'active', selected = false } = options;
  let normalizedSidc = (sidc || 'SFGPUCI---F----').padEnd(15, '-').slice(0, 15);
  const statusChar = status === 'active' || status === 'relocating' ? 'P' : 'A';
  normalizedSidc = normalizedSidc.substring(0, 3) + statusChar + normalizedSidc.substring(4);
  const symbol = new ms.Symbol(normalizedSidc, {
    size,
    uniqueDesignation,
    higherFormation,
    infoFields: Boolean(uniqueDesignation),
    outlineWidth: selected ? 4 : 2,
    outlineColor: selected ? '#F39200' : '#1E1C16',
  });
  return symbol.asSVG();
}

export function createMilsymbolLeafletIcon(options: MilsymbolOptions): L.DivIcon {
  const { sidc, size = 30, uniqueDesignation = '', status = 'active', selected = false } = options;
  let normalizedSidc = (sidc || 'SFGPUCI---F----').padEnd(15, '-').slice(0, 15);
  const statusChar = status === 'active' || status === 'relocating' ? 'P' : 'A';
  normalizedSidc = normalizedSidc.substring(0, 3) + statusChar + normalizedSidc.substring(4);
  const symbol = new ms.Symbol(normalizedSidc, {
    size,
    uniqueDesignation,
    infoFields: Boolean(uniqueDesignation),
    outlineWidth: selected ? 4 : 2,
    outlineColor: selected ? '#F39200' : '#111224',
  });
  const anchor = symbol.getAnchor();
  const symSize = symbol.getSize();
  return L.divIcon({
    className: 'milsymbol-marker-icon',
    html: symbol.asSVG(),
    iconSize: [symSize.width, symSize.height],
    iconAnchor: [anchor.x, anchor.y],
    popupAnchor: [0, -anchor.y],
  });
}

export const MILSYMBOL_LEGEND_ITEMS = [
  { label: 'Пункт управління / Командний вузол', type: 'command_post', sidc: 'SFGPE-----F----' },
  { label: 'Механізований підрозділ', type: 'mechanized_unit', sidc: 'SFGPUCI---F----' },
  { label: 'Підрозділ протиповітряної оборони', type: 'air_defense', sidc: 'SFGPUCD---F----' },
  { label: 'Логістичний вузол забезпечення', type: 'logistics_hub', sidc: 'SFGPUSS---F----' },
  { label: 'Вузол зв’язку та телеметрії', type: 'comms_node', sidc: 'SFGPUSM---F----' },
  { label: 'Радіолокаційний пост', type: 'radar_station', sidc: 'SFGPUCF---F----' },
];
