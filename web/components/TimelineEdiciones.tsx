'use client';

import { EVOLUCION } from '@/lib/data';

interface PorEdicion {
  Edicion: number;
  propuestas: number;
  apoyos: number;
  seleccionadas: number;
  tasa_seleccion: number;
  periodo: string;
}

export default function TimelineEdiciones() {
  const data = EVOLUCION.por_edicion as PorEdicion[];
  const maxProp = Math.max(...data.map((d) => d.propuestas));
  const maxApo = Math.max(...data.map((d) => d.apoyos));

  return (
    <section style={{ marginTop: '2rem', marginBottom: '2rem' }}>
      <h2 style={{ fontSize: '1.5rem', borderBottom: '1px solid var(--color-rule)', paddingBottom: '0.4rem' }}>
        7 ediciones, 9 años: la evolución
      </h2>
      <p style={{ color: 'var(--color-muted)', maxWidth: 720 }}>
        Volumen de propuestas y apoyos por edición. La tasa de selección (% de propuestas finalmente
        ejecutadas) cae al crecer la participación: el sistema gana voz pero pierde capacidad de
        respuesta.
      </p>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${data.length},1fr)`,
          gap: '0.4rem',
          alignItems: 'end',
          marginTop: '1rem',
          background: 'white',
          padding: '1rem',
          borderRadius: 6,
          border: '1px solid var(--color-rule)',
        }}
      >
        {data.map((d) => {
          const h1 = (d.propuestas / maxProp) * 100;
          const h2 = (d.apoyos / Math.max(maxApo, 1)) * 100;
          return (
            <div key={d.Edicion} style={{ textAlign: 'center' }}>
              <div style={{ height: 150, display: 'flex', alignItems: 'end', justifyContent: 'center', gap: 4 }}>
                <div
                  title={`${d.propuestas} propuestas`}
                  style={{
                    width: 18,
                    height: `${h1}%`,
                    background: 'var(--color-accent)',
                    borderRadius: '3px 3px 0 0',
                  }}
                />
                <div
                  title={`${d.apoyos.toLocaleString('es-ES')} apoyos`}
                  style={{
                    width: 18,
                    height: `${h2}%`,
                    background: '#5e3c8c',
                    borderRadius: '3px 3px 0 0',
                  }}
                />
              </div>
              <div style={{ marginTop: 6, fontSize: '0.78rem', fontWeight: 600 }}>Ed. {d.Edicion}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>{d.periodo}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)', marginTop: 3 }}>
                {(d.tasa_seleccion * 100).toFixed(1)}% sel.
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem', color: 'var(--color-muted)', marginTop: '0.6rem' }}>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, background: 'var(--color-accent)', marginRight: 4, verticalAlign: 'middle' }} /> Propuestas</span>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, background: '#5e3c8c', marginRight: 4, verticalAlign: 'middle' }} /> Apoyos ciudadanos</span>
      </div>
    </section>
  );
}
