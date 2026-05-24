// Static data loaders. All data is pre-built JSON shipped with the bundle.
import distritos from '@/public/data/distritos.json';
import temas from '@/public/data/temas.json';
import matriz from '@/public/data/matriz.json';
import evolucion from '@/public/data/evolucion.json';
import fichas from '@/public/data/fichas_distrito.json';
import resumen from '@/public/data/resumen.json';

export type Cuadrante =
  | 'Demanda legítima'
  | 'Sobre-demandante'
  | 'Silencioso vulnerable'
  | 'Cómodo';

export const CUADRANTE_COLOR: Record<Cuadrante, string> = {
  'Demanda legítima': '#b03a2e',
  'Sobre-demandante': '#d4a017',
  'Silencioso vulnerable': '#5e3c8c',
  Cómodo: '#3a8c4d',
};

export const CUADRANTE_LABEL_PUBLICO: Record<Cuadrante, string> = {
  'Demanda legítima': 'Demanda alineada con carencia',
  'Sobre-demandante': 'Demanda por encima del indicador',
  'Silencioso vulnerable': 'Silencio sobre carencia observable',
  Cómodo: 'Sin carencia ni demanda destacadas',
};

export const CUADRANTE_DESCRIPCION: Record<Cuadrante, string> = {
  'Demanda legítima':
    'Carencia alta + demanda alta: la voz ciudadana coincide con la realidad medible.',
  'Sobre-demandante':
    'Carencia baja + demanda alta: la demanda relativa queda por encima de lo que el indicador objetivo sugiere.',
  'Silencioso vulnerable':
    'Carencia alta + demanda baja: existe la carencia pero no llega a expresarse como demanda en Decidim.',
  Cómodo:
    'Carencia baja + demanda baja: ni hay problema observable ni se reclama.',
};

export const CUADRANTE_ACCION: Record<Cuadrante, string> = {
  'Demanda legítima': 'Priorizar / estudiar viabilidad técnica',
  'Sobre-demandante': 'Comunicar datos y criterios de selección',
  'Silencioso vulnerable': 'Outreach presencial y validación vecinal',
  Cómodo: 'Mantener seguimiento ordinario',
};

export interface Tema {
  id: number;
  nombre: string;
  n_propuestas: number;
  n_apoyos: number;
  n_seleccionadas: number;
}

export interface MatrizCelda {
  demanda_z: number | null;
  carencia_z: number | null;
  discrepancia: number | null;
  cuadrante: Cuadrante;
  n_apoyos: number;
  n_propuestas: number;
  apoyos_per_1000hab: number;
  indicador_realidad: string;
  valor_realidad: number | null;
}

export type Matriz = Record<string, Record<string, MatrizCelda>>;

export interface FichaDistrito {
  id_distrito: number;
  nombre_distrito: string;
  poblacion: number;
  vulnerabilidad_global: number | null;
  vulnerabilidad_equip: number | null;
  m2_verde_per_hab: number;
  m_carril_bici_per_1000hab: number;
  n_equipamientos: number;
  n_centros_educativos: number;
  n_fallas: number;
  top_demandas: { tema: string; apoyos: number; propuestas: number }[];
  silencios_vulnerables: { tema: string; carencia_z: number; demanda_z: number }[];
  demandas_zombi: { tema: string; ediciones: number; apoyos: number }[];
}

export const TEMAS = temas as unknown as Tema[];
export const MATRIZ = matriz as unknown as Matriz;
export const EVOLUCION = evolucion as any;
export const FICHAS = fichas as unknown as Record<string, FichaDistrito>;
export const RESUMEN = resumen as {
  n_propuestas_total: number;
  n_apoyos_total: number;
  n_seleccionadas_total: number;
  n_distritos: number;
  n_temas: number;
  n_ediciones: number;
  periodo: string;
  tasa_seleccion_global: number;
  cuadrante_counts: Record<string, number>;
  presupuesto_total_solicitado_eur: number;
};
export const DISTRITOS_GEOJSON = distritos as any;
