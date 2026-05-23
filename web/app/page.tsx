'use client';

import dynamic from 'next/dynamic';
import { useState } from 'react';
import {
  TEMAS,
  MATRIZ,
  RESUMEN,
  FICHAS,
  CUADRANTE_COLOR,
  CUADRANTE_DESCRIPCION,
  Cuadrante,
} from '@/lib/data';

const AtlasMap = dynamic(() => import('@/components/AtlasMap'), { ssr: false });

export default function Home() {
  const [selectedTema, setSelectedTema] = useState<string | null>(null);
  const [selectedDistrito, setSelectedDistrito] = useState<number | null>(null);

  const ficha = selectedDistrito ? FICHAS[String(selectedDistrito)] : null;
  const fmt = (n: number) => n.toLocaleString('es-ES');

  return (
    <main style={{ maxWidth: 1180, margin: '0 auto', padding: '2.5rem 1.5rem' }}>
      <header style={{ borderBottom: '1px solid var(--color-rule)', paddingBottom: '1.5rem', marginBottom: '2rem' }}>
        <p
          style={{
            fontSize: '0.78rem',
            color: 'var(--color-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.12em',
            margin: 0,
          }}
        >
          Premios de Datos Abiertos del Ayuntamiento de València · Edición 2026
        </p>
        <h1 style={{ fontSize: '2.6rem', lineHeight: 1.05, margin: '0.5rem 0 0.8rem' }}>
          Atlas de la Voz Ciudadana de València
        </h1>
        <p style={{ fontSize: '1.1rem', lineHeight: 1.55, color: 'var(--color-ink)', maxWidth: 760 }}>
          Cruzamos las <strong>{fmt(RESUMEN.n_propuestas_total)} propuestas</strong> presentadas en{' '}
          <strong>{RESUMEN.n_ediciones} ediciones</strong> de Decidim VLC ({RESUMEN.periodo}) con{' '}
          <strong>once datasets municipales</strong> del Portal de Datos Abiertos para responder a una
          pregunta: <em>¿la voz ciudadana refleja las carencias reales de cada distrito?</em>
        </p>
      </header>

      <section style={{ marginBottom: '2rem' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))',
            gap: '1rem',
          }}
        >
          {[
            ['Propuestas', fmt(RESUMEN.n_propuestas_total)],
            ['Apoyos ciudadanos', fmt(RESUMEN.n_apoyos_total)],
            ['Seleccionadas', fmt(RESUMEN.n_seleccionadas_total)],
            ['Tasa de selección', `${(RESUMEN.tasa_seleccion_global * 100).toFixed(1)}%`],
            [
              'Inversión solicitada',
              `${(RESUMEN.presupuesto_total_solicitado_eur / 1_000_000).toFixed(0)} M €`,
            ],
            ['Distritos analizados', RESUMEN.n_distritos.toString()],
            ['Temas detectados', RESUMEN.n_temas.toString()],
          ].map(([k, v]) => (
            <div
              key={k}
              style={{
                background: 'white',
                border: '1px solid var(--color-rule)',
                padding: '0.9rem 1rem',
                borderRadius: 6,
              }}
            >
              <div
                style={{
                  fontSize: '0.72rem',
                  color: 'var(--color-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                }}
              >
                {k}
              </div>
              <div style={{ fontSize: '1.4rem', fontFamily: 'var(--font-serif)', marginTop: '0.2rem' }}>{v}</div>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '0.6rem' }}>Mapa de discrepancia</h2>
        <p style={{ color: 'var(--color-muted)', fontSize: '0.95rem', marginTop: 0 }}>
          Selecciona un tema para ver el cuadrante de cada distrito. Cada cuadrante cruza el nivel de
          demanda ciudadana (apoyos por habitante) con la carencia real medida en los datasets municipales.
        </p>
        <div style={{ marginBottom: '0.8rem' }}>
          <select
            value={selectedTema ?? ''}
            onChange={(e) => setSelectedTema(e.target.value || null)}
            style={{
              padding: '0.5rem 0.7rem',
              fontSize: '0.95rem',
              border: '1px solid var(--color-rule)',
              borderRadius: 4,
              background: 'white',
              minWidth: 360,
            }}
          >
            <option value="">— Elige un tema —</option>
            {TEMAS.map((t) => (
              <option key={t.id} value={t.nombre}>
                {t.nombre} ({fmt(t.n_apoyos)} apoyos)
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', alignItems: 'start' }}>
          <AtlasMap selectedTema={selectedTema} matriz={MATRIZ} onSelectDistrito={setSelectedDistrito} />
          <aside style={{ minHeight: 200 }}>
            <h3 style={{ fontSize: '1rem', marginTop: 0, marginBottom: '0.6rem' }}>Leyenda</h3>
            {(Object.keys(CUADRANTE_COLOR) as Cuadrante[]).map((c) => (
              <div key={c} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <span
                  style={{
                    width: 14,
                    height: 14,
                    background: CUADRANTE_COLOR[c],
                    borderRadius: 3,
                    marginTop: 4,
                    flexShrink: 0,
                  }}
                />
                <div>
                  <strong style={{ fontSize: '0.9rem' }}>{c}</strong>
                  <p style={{ margin: '0.15rem 0 0', fontSize: '0.8rem', color: 'var(--color-muted)', lineHeight: 1.4 }}>
                    {CUADRANTE_DESCRIPCION[c]}
                  </p>
                </div>
              </div>
            ))}
          </aside>
        </div>
      </section>

      {ficha && (
        <section style={{ marginBottom: '2rem', background: 'white', padding: '1.5rem', borderRadius: 8, border: '1px solid var(--color-rule)' }}>
          <h2 style={{ margin: '0 0 0.2rem', fontSize: '1.7rem' }}>{ficha.nombre_distrito}</h2>
          <p style={{ margin: '0 0 1.2rem', color: 'var(--color-muted)', fontSize: '0.95rem' }}>
            {fmt(ficha.poblacion)} habitantes · {ficha.n_equipamientos} equipamientos municipales ·{' '}
            {ficha.m2_verde_per_hab.toFixed(1)} m²/hab de verde ·{' '}
            {ficha.m_carril_bici_per_1000hab.toFixed(0)} m de carril bici/1.000 hab
            {ficha.vulnerabilidad_global !== null && (
              <>
                {' · Índice de vulnerabilidad: '}
                <strong>{ficha.vulnerabilidad_global.toFixed(2)}</strong>
              </>
            )}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.2rem' }}>
            <div>
              <h4 style={{ margin: '0 0 0.5rem' }}>Lo más pedido</h4>
              <ol style={{ margin: 0, paddingLeft: '1.2rem', lineHeight: 1.5 }}>
                {ficha.top_demandas.map((t, i) => (
                  <li key={i}>
                    {t.tema} <span style={{ color: 'var(--color-muted)', fontSize: '0.85rem' }}>({fmt(t.apoyos)} apoyos)</span>
                  </li>
                ))}
              </ol>
            </div>
            <div>
              <h4 style={{ margin: '0 0 0.5rem' }}>Silencios vulnerables</h4>
              {ficha.silencios_vulnerables.length === 0 ? (
                <p style={{ color: 'var(--color-muted)', fontStyle: 'italic' }}>Sin silencios detectados.</p>
              ) : (
                <ol style={{ margin: 0, paddingLeft: '1.2rem', lineHeight: 1.5 }}>
                  {ficha.silencios_vulnerables.map((s, i) => (
                    <li key={i}>{s.tema}</li>
                  ))}
                </ol>
              )}
            </div>
            <div>
              <h4 style={{ margin: '0 0 0.5rem' }}>Demandas zombi</h4>
              {ficha.demandas_zombi.length === 0 ? (
                <p style={{ color: 'var(--color-muted)', fontStyle: 'italic' }}>Ninguna detectada.</p>
              ) : (
                <ol style={{ margin: 0, paddingLeft: '1.2rem', lineHeight: 1.5 }}>
                  {ficha.demandas_zombi.slice(0, 5).map((z, i) => (
                    <li key={i}>
                      {z.tema}{' '}
                      <span style={{ color: 'var(--color-muted)', fontSize: '0.85rem' }}>
                        ({z.ediciones} ediciones · 0 seleccionadas)
                      </span>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        </section>
      )}

      <footer style={{ borderTop: '1px solid var(--color-rule)', paddingTop: '1rem', color: 'var(--color-muted)', fontSize: '0.85rem' }}>
        Datos: Portal de Datos Abiertos del Ayuntamiento de València (opendata.vlci.valencia.es) ·{' '}
        Padrón municipal 2022. Código y metodología:{' '}
        <a href="https://github.com/santiago-medina/atlas-voz-ciudadana-valencia">GitHub</a>.
      </footer>
    </main>
  );
}
