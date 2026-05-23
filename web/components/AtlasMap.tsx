'use client';

import { useEffect, useRef } from 'react';
import { CUADRANTE_COLOR, Cuadrante, Matriz, DISTRITOS_GEOJSON } from '@/lib/data';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Props {
  selectedTema: string | null;
  matriz: Matriz;
  onSelectDistrito?: (id: number) => void;
}

export default function AtlasMap({ selectedTema, matriz, onSelectDistrito }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.GeoJSON | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = L.map(containerRef.current, {
      center: [39.47, -0.376],
      zoom: 12,
      zoomControl: true,
      scrollWheelZoom: false,
    });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution:
        '© <a href="https://carto.com/">CARTO</a> · © <a href="https://openstreetmap.org">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);
    mapRef.current = map;
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    if (layerRef.current) {
      layerRef.current.remove();
      layerRef.current = null;
    }

    const layer = L.geoJSON(DISTRITOS_GEOJSON, {
      style: (feat) => {
        const id = (feat?.properties as any)?.id_distrito;
        const cell = selectedTema && matriz[selectedTema]?.[String(id)];
        const color = cell ? CUADRANTE_COLOR[cell.cuadrante as Cuadrante] : '#cccccc';
        return {
          color: '#444',
          weight: 0.7,
          fillColor: color,
          fillOpacity: selectedTema ? 0.7 : 0.25,
        };
      },
      onEachFeature: (feat, lyr) => {
        const props = feat.properties as { id_distrito: number; nombre_distrito: string; poblacion: number };
        const cell = selectedTema && matriz[selectedTema]?.[String(props.id_distrito)];
        const tooltip = `
          <div style="font-family:sans-serif;font-size:0.85rem">
            <strong>${props.nombre_distrito}</strong><br/>
            ${props.poblacion.toLocaleString('es-ES')} habitantes<br/>
            ${
              cell
                ? `<span style="color:${CUADRANTE_COLOR[cell.cuadrante as Cuadrante]}">●</span> ${cell.cuadrante}<br/>
                   ${cell.n_apoyos} apoyos · ${cell.n_propuestas} propuestas`
                : ''
            }
          </div>
        `;
        lyr.bindTooltip(tooltip, { sticky: true });
        lyr.on('click', () => onSelectDistrito?.(props.id_distrito));
      },
    }).addTo(map);
    layerRef.current = layer;
    try {
      map.fitBounds(layer.getBounds(), { padding: [20, 20] });
    } catch (e) {
      /* ignore */
    }
  }, [selectedTema, matriz, onSelectDistrito]);

  return <div ref={containerRef} style={{ height: '70vh', width: '100%', borderRadius: 8 }} />;
}
