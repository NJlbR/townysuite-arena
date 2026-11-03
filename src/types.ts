export type McmmoSkillName = 'building' | 'vitality' | 'combat' | 'mining' | 'woodcutting';

export interface McmmoStats {
  building: number; // 0 to 100
  buildingXp: number;
  vitality: number;
  combat: number;
  mining: number;
  woodcutting: number;
}

export type BuildingCategory = 'civilian' | 'military' | 'magic' | 'industry' | 'wonder';

export interface ResourceCost {
  material: string;
  count: number;
  nameRu: string;
  icon: string;
}

export interface TownBuff {
  id: string;
  type: 'max_health' | 'health_regen' | 'damage' | 'damage_resistance' | 'mcmmo_xp_boost' | 'speed' | 'tax_reduction' | 'hero_of_the_village' | 'town_shield' | 'fortification';
  value: number;
  unit: string;
  descriptionRu: string;
}

export interface ChunkFootprint {
  widthChunks: number;  // 1 or 2
  lengthChunks: number; // 1 or 2
}

export interface BuildingBlueprint {
  id: string;
  nameRu: string;
  nameEn: string;
  category: BuildingCategory;
  description: string;
  requiredBuildingLevel: number; // mcMMO building level
  chunkFootprint: ChunkFootprint; // 1x1, 1x2, or 2x2 for Wonders
  size: {
    width: number; // X in blocks
    length: number; // Z in blocks
    height: number; // Y in blocks
  };
  resources: ResourceCost[];
  buffs: TownBuff[];
  isWorldWonder?: boolean;
  wonderCompletedByTown?: string | null; // Once built globally, locked!
  lore?: string;
  blocksPattern?: {
    material: string;
    color: string;
    count: number;
  }[];
}

export type ConstructionStatus = 'planning' | 'constructing' | 'active' | 'damaged' | 'destroyed';

export interface ChunkCoordType {
  x: number;
  z: number;
  world?: string;
}

export interface ActiveTownBuilding {
  instanceId: string;
  blueprintId: string;
  townName: string;
  placedBy: string;
  status: ConstructionStatus;
  progressPercent: number; // 0 to 100
  placedBlocks: number;
  totalBlocks: number;
  healthPercent: number; // 0 to 100, drops on siege
  assignedChunks: ChunkCoordType[];
  placedMaterials: Record<string, number>;
  assignedBuilders: string[];
  createdAt: number;
  lastRepairedAt?: number;
}

export interface TownBuildPlot {
  x: number;
  z: number;
  world: string;
  townName: string;
  occupiedByBuildingId?: string;
}

export interface TownCitizen {
  uuid: string;
  username: string;
  role: 'mayor' | 'assistant' | 'builder' | 'citizen';
  mcmmoStats: McmmoStats;
  isOnline: boolean;
}

export interface TownData {
  name: string;
  mayor: string;
  bankBalance: number;
  townBlocks: number; // Claims count
  citizens: TownCitizen[];
  buildPlots: TownBuildPlot[];
  activeBuildings: ActiveTownBuilding[];
  worldWondersOwned: string[];
}

export interface LogMessage {
  id: string;
  timestamp: string;
  prefix: 'towny' | 'mcmmo' | 'system' | 'combat' | 'build';
  message: string;
}
