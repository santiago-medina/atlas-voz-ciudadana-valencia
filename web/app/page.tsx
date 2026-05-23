export default function Home() {
  return (
    <main style={{ maxWidth: 760, margin: '0 auto', padding: '4rem 1.5rem' }}>
      <p style={{ fontSize: '0.9rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
        Premios de Datos Abiertos del Ayuntamiento de València 2026
      </p>
      <h1 style={{ fontSize: '3rem', lineHeight: 1.1, margin: '0.5rem 0 1.5rem' }}>
        Atlas de la Voz Ciudadana de València
      </h1>
      <p style={{ fontSize: '1.2rem', lineHeight: 1.6, color: 'var(--color-ink)', maxWidth: 640 }}>
        ¿La voz ciudadana refleja las carencias reales de cada distrito? Cruzamos las{' '}
        <strong>5.285 propuestas vecinales</strong> presentadas a Decidim VLC entre 2015 y 2023 con
        los datasets municipales del Portal de Datos Abiertos para responder esta pregunta.
      </p>
      <hr />
      <p style={{ color: 'var(--color-muted)' }}>
        Sitio en construcción · Actualizado durante mayo-junio 2026
      </p>
      <p>
        <a href="https://github.com/santiago-medina/atlas-voz-ciudadana-valencia">
          Repositorio en GitHub →
        </a>
      </p>
    </main>
  );
}
