'use client';

import hallazgos from '@/public/data/hallazgos.json';

interface Hallazgo {
  id: string;
  titulo: string;
  cifra: string;
  texto: string;
  fuente: string;
}

export default function HallazgosSection() {
  const items = hallazgos as Hallazgo[];
  return (
    <section style={{ marginTop: '3rem', marginBottom: '2rem' }}>
      <h2 style={{ fontSize: '1.6rem', borderBottom: '1px solid var(--color-rule)', paddingBottom: '0.4rem' }}>
        13 hallazgos
      </h2>
      <p style={{ color: 'var(--color-muted)', maxWidth: 720 }}>
        Cifras concretas derivadas del pipeline analítico. Cada hallazgo es reproducible ejecutando los
        scripts ETL del repositorio.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: '1rem', marginTop: '1.2rem' }}>
        {items.map((h) => (
          <article
            key={h.id}
            style={{
              background: 'white',
              border: '1px solid var(--color-rule)',
              borderRadius: 6,
              padding: '1rem 1.1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
            }}
          >
            <header style={{ display: 'flex', alignItems: 'baseline', gap: '0.6rem' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--color-muted)', fontWeight: 600 }}>{h.id}</span>
              <h3 style={{ fontSize: '1.05rem', margin: 0, lineHeight: 1.25 }}>{h.titulo}</h3>
            </header>
            <p
              style={{
                fontSize: '1.3rem',
                fontFamily: 'var(--font-serif)',
                color: 'var(--color-accent)',
                margin: '0.3rem 0',
              }}
            >
              {h.cifra}
            </p>
            <p style={{ margin: 0, fontSize: '0.92rem', lineHeight: 1.55 }}>{h.texto}</p>
            <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--color-muted)' }}>{h.fuente}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
