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
  CUADRANTE_LABEL_PUBLICO,
  CUADRANTE_ACCION,
  Cuadrante,
} from '@/lib/data';

const AtlasMap = dynamic(() => import('@/components/AtlasMap'), { ssr: false });
import HallazgosSection from '@/components/HallazgosSection';
import TimelineEdiciones from '@/components/TimelineEdiciones';

export default function Home() {
  // Tema precargado: "Pacificación del tráfico", uno de los hallazgos
  // más rotundos (Campanar / Pla del Real con velocidad alta y demanda baja).
  const DEFAULT_TEMA = TEMAS.find((t) => t.nombre === 'Pacificación del tráfico' && MATRIZ[t.nombre])?.nombre
    ?? TEMAS.find((t) => MATRIZ[t.nombre])?.nombre
    ?? null;
  const [selectedTema, setSelectedTema] = useState<string | null>(DEFAULT_TEMA);
  const [selectedDistrito, setSelectedDistrito] = useState<number | null>(null);
  const pctSilencio = ((RESUMEN.cuadrante_counts?.['Silencioso vulnerable'] ?? 0)
    / Object.values(RESUMEN.cuadrante_counts ?? {}).reduce((a, b) => a + b, 0) * 100);

  const ficha = selectedDistrito ? FICHAS[String(selectedDistrito)] : null;
  // toLocaleString('es-ES') no agrupa números de 4 dígitos (5285) por defecto.
  // Forzamos separador de miles siempre para consistencia editorial: 5.285.
  const fmt = (n: number) =>
    new Intl.NumberFormat('es-ES', { useGrouping: 'always' as any }).format(n);

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
          Cruzamos las <strong>{fmt(RESUMEN.n_propuestas_total)} propuestas</strong> con título legible
          presentadas en <strong>{RESUMEN.n_ediciones} ediciones</strong> de Decidim VLC ({RESUMEN.periodo})
          con <strong>{(RESUMEN as any).n_datasets_realidad ?? 22} datasets de realidad urbana</strong> del Portal de Datos Abiertos para
          responder a una pregunta: <em>¿la voz ciudadana refleja las carencias observables en los
          datos municipales de cada distrito?</em>
        </p>
        <p
          style={{
            fontSize: '1.05rem',
            lineHeight: 1.5,
            color: 'var(--color-accent)',
            fontStyle: 'italic',
            maxWidth: 760,
            margin: '1rem 0 0',
            fontFamily: 'var(--font-serif)',
          }}
        >
          El mayor riesgo de Decidim no es que unos barrios pidan demasiado, sino que otros, con
          necesidades documentadas, no lleguen a pedir nada.
        </p>
        <p style={{ fontSize: '0.85rem', color: 'var(--color-muted)', marginTop: '0.6rem', maxWidth: 760 }}>
          La octava edición de DecidimVLC (2025-2026) está en curso. Los hallazgos de este atlas
          llegan a tiempo para informar su mecanismo de reequilibrio territorial.
        </p>
      </header>

      <section
        style={{
          margin: '1.5rem 0 2rem',
          background: '#fff',
          border: '2px solid var(--color-accent)',
          borderRadius: 8,
          padding: '1.4rem 1.6rem',
        }}
      >
        <div
          style={{
            fontSize: '0.78rem',
            textTransform: 'uppercase',
            letterSpacing: '0.12em',
            color: 'var(--color-accent)',
            fontWeight: 700,
            marginBottom: '0.4rem',
          }}
        >
          Hallazgo central
        </div>
        <p
          style={{
            fontSize: '1.5rem',
            lineHeight: 1.3,
            margin: '0 0 0.6rem',
            fontFamily: 'var(--font-serif)',
            color: 'var(--color-ink)',
          }}
        >
          Casi <strong style={{ color: 'var(--color-accent)' }}>1 de cada 2</strong> necesidades
          urbanas observables{' '}
          <strong style={{ color: 'var(--color-accent)' }}>no llega a expresarse como demanda</strong>{' '}
          ciudadana.
        </p>
        <p style={{ fontSize: '0.9rem', color: 'var(--color-muted)', margin: '0 0 0.8rem', lineHeight: 1.5 }}>
          De {Object.values(RESUMEN.cuadrante_counts ?? {}).reduce((a, b) => a + b, 0)} pares
          (distrito × tema) analizables con indicador municipal específico,{' '}
          {pctSilencio.toFixed(0)}% caen en el cuadrante "silencio sobre carencia observable":
          el distrito tiene una carencia por encima de la media de la ciudad pero su demanda
          relativa en Decidim queda por debajo. Es el cuadrante más frecuente.
        </p>
        <p
          style={{
            fontSize: '0.85rem',
            color: 'var(--color-ink)',
            margin: 0,
            padding: '0.6rem 0.8rem',
            background: '#faf7f0',
            borderRadius: 4,
            borderLeft: '3px solid var(--color-accent)',
          }}
        >
          <strong>Qué permite hacer este atlas:</strong> identificar dónde Decidim necesita salir
          a buscar voz ciudadana, dónde el Ayuntamiento debe explicar mejor sus decisiones, y
          dónde la demanda vecinal coincide con carencias objetivas. El mecanismo de
          reequilibrio territorial de la 8ª edición (en curso) puede beneficiarse directamente
          de estos resultados.
        </p>
      </section>

      <section
        style={{
          margin: '1.5rem 0 2rem',
          background: '#f8f6f1',
          border: '1px solid var(--color-rule)',
          borderRadius: 8,
          padding: '1.2rem 1.4rem',
        }}
      >
        <h3 style={{ margin: '0 0 0.8rem', fontSize: '1.1rem' }}>Cómo funciona el atlas, en 90 segundos</h3>
        <ol
          style={{
            margin: 0,
            paddingLeft: '1.2rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '0.8rem 1.4rem',
            lineHeight: 1.45,
            fontSize: '0.92rem',
          }}
        >
          <li>
            <strong>{fmt(RESUMEN.n_propuestas_total ?? 0)} propuestas</strong> de Decidim → clasificación
            temática automática con embeddings multilingües
          </li>
          <li>
            <strong>Apoyos normalizados</strong> por población del padrón 2022 → demanda relativa
            por distrito
          </li>
          <li>
            <strong>{(RESUMEN as any).n_datasets_realidad ?? 22} datasets municipales</strong> → indicadores
            territoriales específicos por tema (carril bici, m² verde, velocidad de calles…)
          </li>
          <li>
            <strong>Comparación contra la media de la ciudad</strong> → cuatro cuadrantes que
            sintetizan la coincidencia entre demanda y carencia
          </li>
        </ol>
      </section>

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

        <div
          style={{
            background: '#faf7f0',
            border: '1px solid var(--color-rule)',
            borderRadius: 6,
            padding: '0.9rem 1.1rem',
            margin: '0.6rem 0 1rem',
            fontSize: '0.88rem',
            lineHeight: 1.55,
          }}
        >
          <strong style={{ display: 'block', marginBottom: '0.3rem' }}>
            Cómo leer este mapa
          </strong>
          <p style={{ margin: '0 0 0.4rem' }}>
            <strong>En resumen:</strong> comparamos si un distrito pide más o menos que la media de
            la ciudad, y si sus datos urbanos están mejor o peor que la media. El cruce de las dos
            comparaciones genera cuatro cuadrantes.
          </p>
          <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
            <li>
              <strong>Demanda</strong> = apoyos ciudadanos por 1.000 habitantes en ese tema (z-score
              respecto a la media de los 19 distritos).
            </li>
            <li>
              <strong>Carencia</strong> = indicador municipal específico del tema (m² verde/hab,
              metros de carril bici/hab, velocidad media de calles, paradas EMT/hab, etc.).
            </li>
          </ul>
        </div>

        <div
          className="grid-2col"
          style={{
            background: '#fff',
            border: '1px dashed var(--color-muted)',
            borderRadius: 6,
            padding: '0.9rem 1.1rem',
            margin: '0 0 1rem',
            fontSize: '0.85rem',
            lineHeight: 1.5,
          }}
        >
          <div>
            <strong style={{ color: 'var(--color-accent)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              ✓ Qué significa este mapa
            </strong>
            <ul style={{ margin: '0.4rem 0 0', paddingLeft: '1rem' }}>
              <li>Detecta posibles desajustes entre necesidad observable e intensidad de demanda expresada.</li>
              <li>Compara distritos contra la media de la ciudad usando indicadores municipales públicos.</li>
              <li>Identifica patrones territoriales útiles para diseño de política participativa.</li>
            </ul>
          </div>
          <div>
            <strong style={{ color: 'var(--color-muted)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              ✗ Qué no significa
            </strong>
            <ul style={{ margin: '0.4rem 0 0', paddingLeft: '1rem' }}>
              <li>No prueba causalidad ni mide las preferencias reales del vecindario.</li>
              <li>No agota la necesidad urbana: solo lo que hay datasets disponibles para medir.</li>
              <li>"Demanda baja" no equivale a "ausencia de necesidad" (Decidim no es muestra representativa).</li>
            </ul>
          </div>
        </div>

        <p style={{ color: 'var(--color-muted)', fontSize: '0.92rem' }}>
          Elige un tema y descubre qué distritos piden mucho, cuáles tienen carencias observables sin
          demanda explícita, y dónde la voz ciudadana coincide con la realidad medible.
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
            <option value="">Elige un tema…</option>
            {TEMAS.filter((t) => MATRIZ[t.nombre]).map((t) => (
              <option key={t.id} value={t.nombre}>
                {t.nombre} ({fmt(t.n_apoyos)} apoyos)
              </option>
            ))}
          </select>
          <div style={{ marginTop: '0.4rem', fontSize: '0.78rem', color: 'var(--color-muted)' }}>
            Mostrando los <strong>{TEMAS.filter((t) => MATRIZ[t.nombre]).length} de {TEMAS.length} temas</strong>
            {' '}con un indicador municipal específico que permite calcular cuadrante. Los{' '}
            {TEMAS.length - TEMAS.filter((t) => MATRIZ[t.nombre]).length} temas sin indicador directo
            (aceras, iluminación, seguridad ciudadana, etc.) se muestran en las fichas de distrito
            pero quedan fuera del índice de discrepancia.
          </div>
          {selectedTema && MATRIZ[selectedTema] && (
            <div
              style={{
                marginTop: '0.5rem',
                fontSize: '0.82rem',
                color: 'var(--color-muted)',
                fontStyle: 'italic',
              }}
            >
              Indicador de carencia: <code style={{ background: '#f4f1ea', padding: '1px 6px', borderRadius: 3, fontSize: '0.85em' }}>
                {Object.values(MATRIZ[selectedTema])[0]?.indicador_realidad ?? 'n/a'}
              </code>
              {Object.values(MATRIZ[selectedTema])[0]?.indicador_realidad === 'ind_equip'
                ? ' (subíndice de vulnerabilidad equipamental, dataset municipal 2021)'
                : ''}
            </div>
          )}
        </div>

        <div className="grid-mapa">
          <AtlasMap selectedTema={selectedTema} matriz={MATRIZ} onSelectDistrito={setSelectedDistrito} />
          <aside style={{ minHeight: 200 }}>
            <h3 style={{ fontSize: '1rem', marginTop: 0, marginBottom: '0.6rem' }}>Leyenda</h3>
            {(Object.keys(CUADRANTE_COLOR) as Cuadrante[]).map((c) => (
              <div key={c} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.7rem' }}>
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
                  <strong style={{ fontSize: '0.9rem' }}>{CUADRANTE_LABEL_PUBLICO[c]}</strong>
                  <p style={{ margin: '0.15rem 0 0.1rem', fontSize: '0.78rem', color: 'var(--color-muted)', lineHeight: 1.4 }}>
                    {CUADRANTE_DESCRIPCION[c]}
                  </p>
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--color-ink)', fontStyle: 'italic' }}>
                    → {CUADRANTE_ACCION[c]}
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
          <div className="grid-3col">
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

      <TimelineEdiciones />

      <section style={{ marginTop: '3rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.6rem', borderBottom: '1px solid var(--color-rule)', paddingBottom: '0.4rem' }}>
          Tres ideas para llevarse
        </h2>
        <p style={{ color: 'var(--color-muted)', maxWidth: 720, marginTop: '0.4rem' }}>
          Si solo hay tiempo para tres conclusiones del Atlas, estas son las que recomendamos
          retener:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div style={{ background: 'white', border: '1px solid var(--color-rule)', borderTop: '4px solid #5e3c8c', padding: '1rem 1.1rem', borderRadius: 4 }}>
            <div style={{ fontSize: '0.72rem', color: '#5e3c8c', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
              1 · El patrón dominante
            </div>
            <p style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.5 }}>
              El cuadrante más frecuente no es "demanda excesiva": es{' '}
              <strong>silencio sobre carencia observable</strong>. {pctSilencio.toFixed(0)}% de los
              pares analizables. La participación tiene sesgos territoriales detectables.
            </p>
          </div>
          <div style={{ background: 'white', border: '1px solid var(--color-rule)', borderTop: '4px solid var(--color-accent)', padding: '1rem 1.1rem', borderRadius: 4 }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
              2 · Las demandas que esperan
            </div>
            <p style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.5 }}>
              <strong>28 pares (distrito × tema) repiten propuestas en 4 o más ediciones
              consecutivas</strong> sin ninguna selección. Acumulan más de 8.000 apoyos
              ciudadanos. El sistema necesita responder explícitamente sobre cada caso.
            </p>
          </div>
          <div style={{ background: 'white', border: '1px solid var(--color-rule)', borderTop: '4px solid #d4a017', padding: '1rem 1.1rem', borderRadius: 4 }}>
            <div style={{ fontSize: '0.72rem', color: '#a17d10', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
              3 · El embudo presupuestario
            </div>
            <p style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.5 }}>
              Por cada euro finalmente ejecutado, la ciudadanía pidió{' '}
              <strong>cuatro</strong>: {fmt(Math.round((RESUMEN as any).presupuesto_total_solicitado_eur / 1_000_000))} M €
              solicitados frente a {fmt(Math.round((RESUMEN as any).presupuesto_seleccionado_eur / 1_000_000))} M €
              seleccionados. La distancia entre expectativa ciudadana y capacidad presupuestaria
              debería comunicarse explícitamente.
            </p>
          </div>
        </div>
      </section>

      <HallazgosSection />

      <section style={{ marginTop: '3rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.6rem', borderBottom: '1px solid var(--color-rule)', paddingBottom: '0.4rem' }}>
          Tres recomendaciones prioritarias para la 8ª edición
        </h2>
        <p style={{ color: 'var(--color-muted)', maxWidth: 720 }}>
          La 8ª edición de DecidimVLC (2025-2026, en curso) puede incorporar tres medidas
          directamente derivadas del análisis. Dos recomendaciones adicionales se detallan a
          continuación como complementarias.
        </p>
        <ol style={{ lineHeight: 1.6, fontSize: '0.95rem', maxWidth: 760, marginTop: '1rem' }}>
          <li>
            <strong>Ir a buscar la voz vecinal en los distritos más silenciosos</strong>. Organizar
            sesiones presenciales en Campanar, Algirós, Rascanya, l'Olivereta y Benicalap, en
            colaboración con asociaciones vecinales y mercados municipales. Es la acción con más
            impacto sobre el cuadrante más frecuente, el de "silencio sobre carencia observable".
          </li>
          <li>
            <strong>Publicar cada año el estado de las propuestas que se repiten</strong>. Para
            cada combinación de distrito y tema que ha presentado propuestas en 4 o más ediciones
            sin ser seleccionada nunca, indicar qué decisión técnica se ha tomado: aceptada y
            pendiente de ejecución, rechazada por motivos concretos, aplazada o aún en estudio.
            Una respuesta explícita evita que los vecinos sientan que sus propuestas se han
            quedado sin contestar.
          </li>
          <li>
            <strong>Revisar la categoría "Toda la ciudad"</strong>. El 22,6 % de las propuestas se
            etiquetan así y, al no asignarse a ningún distrito, quedan fuera del mecanismo de
            reequilibrio territorial. Pedir que cada propuesta indique en qué barrio o distrito
            tendría más efecto mejora la representatividad por distrito.
          </li>
        </ol>
        <details style={{ marginTop: '1.4rem', fontSize: '0.92rem' }}>
          <summary style={{ cursor: 'pointer', color: 'var(--color-muted)', fontWeight: 600 }}>
            Ver dos recomendaciones complementarias
          </summary>
          <ol start={4} style={{ lineHeight: 1.6, paddingLeft: '1.2rem', marginTop: '0.6rem' }}>
            <li>
              <strong>Dar más peso a los apoyos de los distritos más vulnerables</strong> según el
              índice oficial de vulnerabilidad por barrios, para que la participación de barrios
              menos organizados pese más en el resultado final.
            </li>
            <li>
              <strong>Contrastar los silencios detectados con las asociaciones vecinales</strong>
              antes de actuar sobre ellos. La ausencia de demanda puede deberse a desconocimiento,
              desconfianza, brecha digital o saturación previa, y cada caso pide una respuesta
              distinta.
            </li>
          </ol>
        </details>
      </section>

      <section style={{ marginTop: '2rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.4rem', borderBottom: '1px solid var(--color-rule)', paddingBottom: '0.4rem' }}>
          Límites del Atlas
        </h2>
        <ul style={{ lineHeight: 1.6, fontSize: '0.9rem', maxWidth: 760, color: 'var(--color-ink)' }}>
          <li>
            <strong>No mide la necesidad urbana en su totalidad.</strong> Mide la discrepancia entre
            la demanda en Decidim y un conjunto concreto de indicadores municipales abiertos. Carencias
            en salud, atención a mayores, seguridad subjetiva o bienestar quedan parcialmente fuera.
          </li>
          <li>
            <strong>Decidim no es una muestra representativa de la población.</strong> Quien participa
            está en general más organizado y conectado. "Demanda baja" no equivale necesariamente a
            "ausencia de necesidad".
          </li>
          <li>
            <strong>Para el tema "Centros de salud"</strong> no existe en el portal un dataset
            que mida directamente la cobertura sanitaria por distrito, así que se utiliza el
            subíndice de vulnerabilidad equipamental del Ayuntamiento (2021). Es una aproximación
            razonable, pero no es lo mismo que medir la carencia sanitaria directamente.
          </li>
          <li>
            <strong>La unidad de análisis es el distrito</strong> (19 unidades). Distritos
            heterogéneos pueden tener bolsas de silencio internas que el agregado distrital esconde.
          </li>
        </ul>
      </section>

      <section
        style={{
          marginTop: '3rem',
          marginBottom: '2rem',
          padding: '2rem 1.5rem',
          background: '#1a1a1a',
          color: '#faf7f0',
          borderRadius: 8,
          textAlign: 'center',
        }}
      >
        <p
          style={{
            fontSize: '1.4rem',
            lineHeight: 1.4,
            margin: 0,
            fontFamily: 'var(--font-serif)',
            maxWidth: 720,
            marginLeft: 'auto',
            marginRight: 'auto',
            fontStyle: 'italic',
          }}
        >
          El reto no es escuchar más propuestas, sino escuchar mejor dónde la necesidad no consigue
          hacerse oír.
        </p>
      </section>

      <footer style={{ borderTop: '1px solid var(--color-rule)', paddingTop: '1rem', color: 'var(--color-muted)', fontSize: '0.85rem' }}>
        Datos: Portal de Datos Abiertos del Ayuntamiento de València (opendata.vlci.valencia.es) ·{' '}
        Padrón municipal 2022. Código y metodología:{' '}
        <a href="https://github.com/santiago-medina/atlas-voz-ciudadana-valencia">GitHub</a>.
      </footer>
    </main>
  );
}
