import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Atlas de la Voz Ciudadana de València',
  description:
    'Análisis cruzado entre las propuestas vecinales de Decidim VLC (2015-2023) y los datasets municipales del Ayuntamiento de València.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
