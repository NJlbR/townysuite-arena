import { TownData } from '../types';

export const INITIAL_TOWN: TownData = {
  name: 'Новгород',
  mayor: 'Yaroslav_Mayor',
  bankBalance: 48500, // Towny dollars / gold
  townBlocks: 16, // 16 chunks claimed
  citizens: [
    {
      uuid: 'u-mayor-1',
      username: 'Yaroslav_Mayor',
      role: 'mayor',
      mcmmoStats: {
        building: 45,
        buildingXp: 4200,
        vitality: 70,
        combat: 85,
        mining: 60,
        woodcutting: 55,
      },
      isOnline: true,
    },
    {
      uuid: 'u-builder-1',
      username: 'Alex_Architect',
      role: 'builder',
      mcmmoStats: {
        building: 68,
        buildingXp: 8900,
        vitality: 55,
        combat: 40,
        mining: 80,
        woodcutting: 75,
      },
      isOnline: true,
    },
    {
      uuid: 'u-novice-1',
      username: 'Dan_Novice',
      role: 'citizen',
      mcmmoStats: {
        building: 14, // Needs lv 20 for Hospital! Blocked from building
        buildingXp: 1200,
        vitality: 30,
        combat: 25,
        mining: 40,
        woodcutting: 35,
      },
      isOnline: true,
    },
    {
      uuid: 'u-master-1',
      username: 'Elena_MasterMason',
      role: 'builder',
      mcmmoStats: {
        building: 88, // Can build Wonder of the World!
        buildingXp: 18500,
        vitality: 65,
        combat: 50,
        mining: 95,
        woodcutting: 90,
      },
      isOnline: true,
    },
    {
      uuid: 'u-warrior-1',
      username: 'Igor_Vanguard',
      role: 'citizen',
      mcmmoStats: {
        building: 0, // Fresh account with 0 mcMMO - completely blocked!
        buildingXp: 0,
        vitality: 90,
        combat: 92,
        mining: 50,
        woodcutting: 40,
      },
      isOnline: false,
    },
  ],
  buildPlots: [
    { x: 10, z: 12, world: 'world', townName: 'Новгород', occupiedByBuildingId: 'bld-init-hospital' },
    { x: 11, z: 12, world: 'world', townName: 'Новгород' },
    { x: 12, z: 12, world: 'world', townName: 'Новгород' },
    { x: 11, z: 13, world: 'world', townName: 'Новгород' },
    { x: 12, z: 13, world: 'world', townName: 'Новгород' },
  ],
  activeBuildings: [
    {
      instanceId: 'bld-init-hospital',
      blueprintId: 'hospital',
      townName: 'Новгород',
      placedBy: 'Yaroslav_Mayor',
      status: 'active',
      progressPercent: 100,
      placedBlocks: 256,
      totalBlocks: 256,
      healthPercent: 100,
      assignedChunks: [{ x: 10, z: 12, world: 'world' }],
      placedMaterials: {
        STONE_BRICKS: 128,
        WHITE_CONCRETE: 64,
        RED_WOOL: 32,
        GLASS: 32,
      },
      assignedBuilders: ['Alex_Architect', 'Elena_MasterMason'],
      createdAt: Date.now() - 3600000 * 24,
      lastRepairedAt: Date.now(),
    },
  ],
  worldWondersOwned: [],
};

export const RIVAL_TOWNS = [
  {
    name: 'Китеж-Град',
    mayor: 'Prince_Vsevolod',
    residentsCount: 14,
    power: 840,
  },
  {
    name: 'Валгалла',
    mayor: 'Ragnar_Lothbrok',
    residentsCount: 9,
    power: 610,
  },
];
