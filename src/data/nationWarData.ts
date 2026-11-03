// Nation Wars Data & Models for TownySieges & TownyExplosionUnblocker

export interface NationTown {
  id: string;
  name: string;
  nationId: string;
  mayor: string;
  residentsCount: number;
  bankGold: number;
  coordinates: { x: number; y: number; z: number };
  mapPercentX: number;
  mapPercentY: number;
  isCapital?: boolean;
  healthPercent: number; // 0-100%
  recentExplosionHits: number;
  lastDamageTimestamp?: number;
}

export interface Nation {
  id: string;
  name: string;
  leader: string; // King / Глава нации
  capitalName: string;
  bankGold: number;
  colorName: string;
  badgeBg: string;
  borderColor: string;
  glowColor: string;
  textColor: string;
  towns: NationTown[];
}

export type NationWarPhase = 'PEACE' | 'PREPARATION' | 'ACTIVE_ASSAULT' | 'COMPLETED';

export interface SiegeCampWarLink {
  id: string;
  attackerTownName: string;
  defenderTownName: string;
  attackerNationId: string;
  defenderNationId: string;
  placedAt: number;
  claimedChunks: number;
  locationName: string;
  mapPercentX: number;
  mapPercentY: number;
}

export interface NationWarSession {
  id: string;
  attackerNationId: string;
  defenderNationId: string;
  declaredByLeader: string;
  phase: NationWarPhase;
  preparationTotalSeconds: number; // 24 hours (86400)
  assaultTotalSeconds: number;     // 2 hours (7200)
  remainingSeconds: number;
  isTickerPaused: boolean;
  activeCamps: SiegeCampWarLink[];
  explosionCasualties: number;
  blocksDestroyedTotal: number;
}

export const INITIAL_NATIONS: Nation[] = [
  {
    id: 'north_alliance',
    name: 'Северный Альянс',
    leader: 'Yaroslav_Great',
    capitalName: 'Новгород',
    bankGold: 142500,
    colorName: 'amber',
    badgeBg: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    borderColor: 'border-amber-500',
    glowColor: 'rgba(245, 158, 11, 0.35)',
    textColor: 'text-amber-400',
    towns: [
      {
        id: 'town_novgorod',
        name: 'Новгород',
        nationId: 'north_alliance',
        mayor: 'Yaroslav_Mayor',
        residentsCount: 28,
        bankGold: 48500,
        coordinates: { x: 160, y: 70, z: 240 },
        mapPercentX: 38,
        mapPercentY: 34,
        isCapital: true,
        healthPercent: 100,
        recentExplosionHits: 0
      },
      {
        id: 'town_nordgard',
        name: 'Нордгард',
        nationId: 'north_alliance',
        mayor: 'Ragnar_Lodbrok',
        residentsCount: 19,
        bankGold: 29000,
        coordinates: { x: 80, y: 110, z: 120 },
        mapPercentX: 18,
        mapPercentY: 28,
        healthPercent: 100,
        recentExplosionHits: 0
      },
      {
        id: 'town_valhalla',
        name: 'Валгалла',
        nationId: 'north_alliance',
        mayor: 'Einar_Stone',
        residentsCount: 14,
        bankGold: 18400,
        coordinates: { x: 260, y: 85, z: 90 },
        mapPercentX: 48,
        mapPercentY: 20,
        healthPercent: 100,
        recentExplosionHits: 0
      }
    ]
  },
  {
    id: 'south_league',
    name: 'Южная Лига',
    leader: 'Prince_Vsevolod',
    capitalName: 'Авалония',
    bankGold: 118200,
    colorName: 'emerald',
    badgeBg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    borderColor: 'border-emerald-500',
    glowColor: 'rgba(16, 185, 129, 0.35)',
    textColor: 'text-emerald-400',
    towns: [
      {
        id: 'town_avalonia',
        name: 'Авалония',
        nationId: 'south_league',
        mayor: 'Lord_Alden',
        residentsCount: 24,
        bankGold: 38200,
        coordinates: { x: 320, y: 68, z: 360 },
        mapPercentX: 62,
        mapPercentY: 60,
        isCapital: true,
        healthPercent: 100,
        recentExplosionHits: 0
      },
      {
        id: 'town_kitezh',
        name: 'Китеж-Град',
        nationId: 'south_league',
        mayor: 'Vsevolod_Prince',
        residentsCount: 18,
        bankGold: 22800,
        coordinates: { x: 440, y: 65, z: 280 },
        mapPercentX: 82,
        mapPercentY: 48,
        healthPercent: 100,
        recentExplosionHits: 0
      },
      {
        id: 'town_solntsedar',
        name: 'Солнцедар',
        nationId: 'south_league',
        mayor: 'Helena_Sun',
        residentsCount: 12,
        bankGold: 16100,
        coordinates: { x: 370, y: 64, z: 490 },
        mapPercentX: 74,
        mapPercentY: 78,
        healthPercent: 100,
        recentExplosionHits: 0
      }
    ]
  }
];

export function formatTimeHoursMinutesSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${pad(h)}:${pad(m)}:${pad(s)}`;
}
