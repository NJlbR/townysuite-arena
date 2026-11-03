import json

content = '''// Comprehensive Architectural Building Variants for Minecraft Towny Suite
// Implemented following professional Minecraft master-builder design principles:
// 1. 3D Depth Rule (Outset frames, recessed window embrasures)
// 2. Texture & Color Gradients (Heavy foundation -> textured body -> timber/slate crown)
// 3. Realistic Roof Profiles (Steep pitch, 1-block eaves overhangs, ridge caps)
// 4. Defensive & Functional Details (Machicolations, crenelations, lanterns, banners)

export interface SolidVolume {
  name: string;
  from: [number, number, number]; // [x, y, z] in local Minecraft block units
  to: [number, number, number];
  color: string;
  stroke: string;
  materialName: string;
}

export interface BuildingVariant {
  id: string;
  nameRu: string;
  nameEn: string;
  styleTag: string;
  description: string;
  lore: string;
  dimensions: { width: number; length: number; height: number };
  chunkFootprint: { widthChunks: number; lengthChunks: number };
  requiredLevel: number;
  blockCountTotal: number;
  appliedRules: {
    depthRule: string;
    gradientFormula: string;
    roofProfile: string;
    lightingDetail: string;
  };
  palette: {
    name: string;
    hex: string;
    percentage: number;
    icon: string;
  }[];
  elements: SolidVolume[];
  buildCommand: string;
}

export interface BuildingFamily {
  id: string;
  baseNameRu: string;
  category: 'civilian' | 'military' | 'wonder' | 'defense' | 'magic';
  variants: BuildingVariant[];
}

export const BUILDING_FAMILIES: BuildingFamily[] = [
  {
    id: 'town_hall',
    baseNameRu: 'Мэрия Города (Ратуша)',
    category: 'civilian',
    variants: [
      {
        id: 'nordic_timber',
        nameRu: 'Нордический Ратушный Двор',
        nameEn: 'Nordic Timber & Deepslate Hall',
        styleTag: 'Фахверк и Сланец',
        description: 'Массивный сланцевый фундамент, выступающие опорные балки из темного дуба, двухъярусный зал с часовой колокольней и крутыми крышами.',
        lore: 'Традиционная ратуша северных вольных городов. Двойная крыша легко выдерживает снегопады, а звон колокола слышен за 500 блоков.',
        dimensions: { width: 16, length: 16, height: 16 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 10,
        blockCountTotal: 1680,
        appliedRules: {
          depthRule: 'Каркас из обтесанных дубовых колонн вынесен на 1 блок наружу; окна заглублены на 1 блок в ниши.',
          gradientFormula: 'Сланцевые кирпичи в цоколе (0-3) → Каменные кирпичи (4-7) → Темный дуб и ель (8-16).',
          roofProfile: 'A-Frame 2:1 крутизной 60° с выносом свеса на 1.5 блока за пределы стен и перевернутыми ступенями.',
          lightingDetail: 'Подвесные кованые фонари на железных цепях под фронтонами и скрытый свет под полублоками.'
        },
        palette: [
          { name: 'Каменные кирпичи', hex: '#787d85', percentage: 38, icon: '🧱' },
          { name: 'Темный дуб', hex: '#422e1b', percentage: 28, icon: '🪵' },
          { name: 'Глубинный сланец', hex: '#2b303a', percentage: 18, icon: '⬛' },
          { name: 'Стекло и решетки', hex: '#38bdf8', percentage: 10, icon: '🪟' },
          { name: 'Золотые акценты', hex: '#f59e0b', percentage: 6, icon: '👑' }
        ],
        buildCommand: '/townybuild build town_hall --style=nordic',
        elements: [
          // Foundation Podium
          { name: 'Подий фундамента', from: [-7.5, 0, -7.5], to: [7.5, 1.5, 7.5], color: '#2b303a', stroke: '#3f4756', materialName: 'Глубинный сланец' },
          // Main Building Core Walls
          { name: 'Стены первого яруса', from: [-6, 1.5, -6], to: [6, 6, 6], color: '#666d77', stroke: '#858d99', materialName: 'Каменные кирпичи' },
          // Outset Timber Framing Pillars (Rule of Depth: +1 block outward)
          { name: 'Угловая балка СЗ', from: [-6.8, 1.5, -6.8], to: [-5.6, 9, -5.6], color: '#3d2814', stroke: '#5a3d20', materialName: 'Темный дуб' },
          { name: 'Угловая балка СВ', from: [5.6, 1.5, -6.8], to: [6.8, 9, -5.6], color: '#3d2814', stroke: '#5a3d20', materialName: 'Темный дуб' },
          { name: 'Угловая балка ЮЗ', from: [-6.8, 1.5, 5.6], to: [-5.6, 9, 6.8], color: '#3d2814', stroke: '#5a3d20', materialName: 'Темный дуб' },
          { name: 'Угловая балка ЮВ', from: [5.6, 1.5, 5.6], to: [6.8, 9, 6.8], color: '#3d2814', stroke: '#5a3d20', materialName: 'Темный дуб' },
          // Recessed Upper Hall Floor
          { name: 'Второй этаж (Совет)', from: [-5.5, 6, -5.5], to: [5.5, 9.5, 5.5], color: '#4a331c', stroke: '#634527', materialName: 'Доски из темного дуба' },
          // Entrance Portico / Stairs
          { name: 'Парадное крыльцо', from: [-2.5, 0.5, 6.5], to: [2.5, 2.5, 8.5], color: '#3a404c', stroke: '#515a6b', materialName: 'Сланцевые ступени' },
          { name: 'Навес крыльца', from: [-2.8, 4.5, 6.2], to: [2.8, 5.5, 8.8], color: '#2b1b0e', stroke: '#472d17', materialName: 'Деревянный навес' },
          // Main Gabled Roof (With 1-block Overhang)
          { name: 'Основной скат крыши', from: [-7.2, 9.5, -6.5], to: [7.2, 13.5, 6.5], color: '#1c1917', stroke: '#332e2b', materialName: 'Крутая кровля' },
          { name: 'Конек крыши', from: [-7.5, 13.5, -1], to: [7.5, 14.2, 1], color: '#573d23', stroke: '#755432', materialName: 'Дубовый конек' },
          // Clock Tower Bell Spire
          { name: 'Часовая башня', from: [-2.5, 9, -2.5], to: [2.5, 15, 2.5], color: '#5a626d', stroke: '#757e8c', materialName: 'Каменная башня' },
          { name: 'Колокольня с решетками', from: [-2, 15, -2], to: [2, 17, 2], color: '#d97706', stroke: '#f59e0b', materialName: 'Золотой колокол' },
          { name: 'Шпиль колокольни', from: [-1.2, 17, -1.2], to: [1.2, 20, 1.2], color: '#0f766e', stroke: '#14b8a6', materialName: 'Медный шпиль' }
        ]
      },
      {
        id: 'gothic_citadel',
        nameRu: 'Имперский Капитолий',
        nameEn: 'Imperial Gothic Capitol',
        styleTag: 'Готика и Андезит',
        description: 'Стрельчатые арки, высокие полированные контрфорсы, витражи и позолоченный шпиль для столичных городов высшего ранга.',
        lore: 'Символ мощи и незыблемой власти мэра. Высокие витражные стрельчатые окна наполняют зал золотистым светом.',
        dimensions: { width: 16, length: 16, height: 21 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 25,
        blockCountTotal: 1940,
        appliedRules: {
          depthRule: 'Контрфорсы сужаются ступенями с 3 блоков у основания до 1 блока у карниза, создавая максимальный объем.',
          gradientFormula: 'Базальт и черный сланец → Полированный андезит → Светлые каменные кирпичи → Золоченые навершия.',
          roofProfile: 'Высокий мансардный шпиль с крутизной 3:1 и стрельчатыми люкарнами.',
          lightingDetail: 'Витражная подсветка изнутри и золотые светильники на контрфорсах.'
        },
        palette: [
          { name: 'Полированный андезит', hex: '#8a939e', percentage: 42, icon: '🏛️' },
          { name: 'Сланцевая плитка', hex: '#262a33', percentage: 24, icon: '⬛' },
          { name: 'Золотые блоки', hex: '#f59e0b', percentage: 14, icon: '👑' },
          { name: 'Витражное стекло', hex: '#6366f1', percentage: 12, icon: '🪟' },
          { name: 'Морские фонари', hex: '#6ee7b7', percentage: 8, icon: '🏮' }
        ],
        buildCommand: '/townybuild build town_hall --style=gothic',
        elements: [
          { name: 'Ступенчатый стилобат', from: [-8, 0, -8], to: [8, 2, 8], color: '#1e222b', stroke: '#303644', materialName: 'Сланцевый стилобат' },
          { name: 'Главный неф капитолия', from: [-5.5, 2, -5.5], to: [5.5, 11, 5.5], color: '#7a838f', stroke: '#949ea9', materialName: 'Полированный андезит' },
          // Flying Buttresses (Контрфорсы)
          { name: 'Контрфорс СЗ', from: [-7.5, 1, -7.5], to: [-5.5, 10, -5.5], color: '#525a66', stroke: '#6c7684', materialName: 'Андезитовый контрфорс' },
          { name: 'Контрфорс СВ', from: [5.5, 1, -7.5], to: [7.5, 10, -5.5], color: '#525a66', stroke: '#6c7684', materialName: 'Андезитовый контрфорс' },
          { name: 'Контрфорс ЮЗ', from: [-7.5, 1, 5.5], to: [-5.5, 10, 7.5], color: '#525a66', stroke: '#6c7684', materialName: 'Андезитовый контрфорс' },
          { name: 'Контрфорс ЮВ', from: [5.5, 1, 5.5], to: [7.5, 10, 7.5], color: '#525a66', stroke: '#6c7684', materialName: 'Андезитовый контрфорс' },
          // Gothic Arched Portal
          { name: 'Стрельчатый портал', from: [-3, 2, 5.5], to: [3, 8, 7.5], color: '#383e4a', stroke: '#4d5564', materialName: 'Стрельчатая арка' },
          // High Mansard Roof
          { name: 'Мансардный купол', from: [-6, 11, -6], to: [6, 15, 6], color: '#1a1f29', stroke: '#2e3545', materialName: 'Сланцевая кровля' },
          { name: 'Верхняя галерея', from: [-3.5, 15, -3.5], to: [3.5, 17, 3.5], color: '#8a939e', stroke: '#a3acb7', materialName: 'Зубчатая балюстрада' },
          { name: 'Готический шпиль', from: [-1.5, 17, -1.5], to: [1.5, 22, 1.5], color: '#d97706', stroke: '#f59e0b', materialName: 'Позолоченный шпиль' }
        ]
      },
      {
        id: 'renaissance_palace',
        nameRu: 'Средиземноморский Палаццо',
        nameEn: 'Mediterranean Renaissance Palazzo',
        styleTag: 'Песчаник и Колоннада',
        description: 'Открытая лоджия с полукруглыми аркадами, теплый песчаник, терракота и плоская смотровая терраса с перголой.',
        lore: 'Изысканный палаццо южных торговых республик. Внутренний атриум сохраняет прохладу в жаркие дни.',
        dimensions: { width: 16, length: 16, height: 14 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 20,
        blockCountTotal: 1590,
        appliedRules: {
          depthRule: 'Арочная аркада первого яруса создает глубокую теневую лоджию с отступом в 2 блока.',
          gradientFormula: 'Красный песчаник → Гладкий песчаник → Терракота → Кварцевый карниз.',
          roofProfile: 'Низкоскатная черепичная кровля со ступенчатой терракотовой окантовкой и балюстрадой.',
          lightingDetail: 'Теплые факелы в чашах и фонари на терракотовых колоннах.'
        },
        palette: [
          { name: 'Гладкий песчаник', hex: '#d8cb9a', percentage: 45, icon: '🏜️' },
          { name: 'Терракота', hex: '#98523d', percentage: 25, icon: '🧱' },
          { name: 'Кварцевые пилястры', hex: '#eae5d8', percentage: 15, icon: '🏛️' },
          { name: 'Древесина акации', hex: '#b8582d', percentage: 15, icon: '🪵' }
        ],
        buildCommand: '/townybuild build town_hall --style=renaissance',
        elements: [
          { name: 'Стилобат из песчаника', from: [-7.5, 0, -7.5], to: [7.5, 1.2, 7.5], color: '#b5a575', stroke: '#c9ba8a', materialName: 'Песчаник' },
          { name: 'Аркада лоджии', from: [-6.5, 1.2, -6.5], to: [6.5, 6, 6.5], color: '#cfbf88', stroke: '#dfcf9b', materialName: 'Гладкий песчаник' },
          { name: 'Колонны портика', from: [-6.8, 1.2, 5.5], to: [-5.2, 6, 6.8], color: '#eae5d8', stroke: '#f5f0e3', materialName: 'Кварцевые пилястры' },
          { name: 'Колонны портика Пр', from: [5.2, 1.2, 5.5], to: [6.8, 6, 6.8], color: '#eae5d8', stroke: '#f5f0e3', materialName: 'Кварцевые пилястры' },
          { name: 'Второй ярус с окнами', from: [-6, 6, -6], to: [6, 10, 6], color: '#98523d', stroke: '#b06149', materialName: 'Оранжевая терракота' },
          { name: 'Выносной карниз', from: [-7, 10, -7], to: [7, 11, 7], color: '#eae5d8', stroke: '#f5f0e3', materialName: 'Резной кварцевый карниз' },
          { name: 'Черепичный скат', from: [-6.5, 11, -6.5], to: [6.5, 13, 6.5], color: '#b8582d', stroke: '#ce6737', materialName: 'Акациевая кровля' },
          { name: 'Бельведер-пергола', from: [-2.5, 13, -2.5], to: [2.5, 15.5, 2.5], color: '#dfcf9b', stroke: '#eee0af', materialName: 'Смотровая пергола' }
        ]
      }
    ]
  },
  {
    id: 'barracks',
    baseNameRu: 'Военные Казармы',
    category: 'military',
    variants: [
      {
        id: 'nordic_longhouse',
        nameRu: 'Укрепленный Дружинный Двор',
        nameEn: 'Nordic Warrior Longhouse',
        styleTag: 'Сруб и Оружейная',
        description: 'Вытянутый двухсекционный сруб 14x28 блоков на мощном каменном валу с крытой оружейной и спальными полатями.',
        lore: 'В казармах закаляются ветераны городской гвардии. Запах смолы, железа и тренировочные крики не смолкают день и ночь.',
        dimensions: { width: 14, length: 28, height: 11 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 2 },
        requiredLevel: 15,
        blockCountTotal: 1720,
        appliedRules: {
          depthRule: 'Деревянные стропильные фермы вынесены наружу на 1 блок вдоль всего 28-блочного фасада, разбивая монотонность.',
          gradientFormula: 'Булыжник + Андезит в цоколе → Еловые бревна в перекрытиях → Сланцевый шифер на крыше.',
          roofProfile: 'Вытянутая крыша-лодка с перевернутым готическим скатом и драконьими резными коньками.',
          lightingDetail: 'Кованые факельные чаши и фонари на защищенных подвесах.'
        },
        palette: [
          { name: 'Еловые бревна', hex: '#483320', percentage: 38, icon: '🪵' },
          { name: 'Каменные кирпичи', hex: '#717882', percentage: 28, icon: '🧱' },
          { name: 'Булыжник', hex: '#555b63', percentage: 18, icon: '🪨' },
          { name: 'Железные решетки', hex: '#94a3b8', percentage: 10, icon: '⛓️' },
          { name: 'Красная шерсть', hex: '#ef4444', percentage: 6, icon: '🟥' }
        ],
        buildCommand: '/townybuild build barracks --style=nordic',
        elements: [
          { name: 'Каменный цокольный вал', from: [-6.5, 0, -13.5], to: [6.5, 2, 13.5], color: '#4a5059', stroke: '#616975', materialName: 'Каменная кладка' },
          { name: 'Основной сруб казармы', from: [-5.5, 2, -12.5], to: [5.5, 6.5, 12.5], color: '#3d2b1b', stroke: '#573e27', materialName: 'Еловые бревна' },
          // Rhythmic Outset Truss Pillars (Every 4 blocks)
          { name: 'Балки фасада Лев', from: [-6.2, 1.5, -12.5], to: [-5.2, 7.5, 12.5], color: '#2b1b0e', stroke: '#452b17', materialName: 'Несущий каркас' },
          { name: 'Балки фасада Прав', from: [5.2, 1.5, -12.5], to: [6.2, 7.5, 12.5], color: '#2b1b0e', stroke: '#452b17', materialName: 'Несущий каркас' },
          // Training Yard Covered Porch
          { name: 'Крытый арсенал', from: [-3.5, 1.5, 12.5], to: [3.5, 5, 15], color: '#2b1e13', stroke: '#422e1d', materialName: 'Оружейный навес' },
          // Viking Longboat Roof
          { name: 'Крыша лонгхауса', from: [-6.5, 6.5, -13.8], to: [6.5, 10.5, 13.8], color: '#1c1917', stroke: '#302b28', materialName: 'Тяжелый гонт' },
          { name: 'Конек с резными бревнами', from: [-0.8, 10.5, -14.2], to: [0.8, 11.5, 14.2], color: '#573e27', stroke: '#735234', materialName: 'Конек крыши' }
        ]
      },
      {
        id: 'heavy_garrison_bastion',
        nameRu: 'Бастион Городской Стражи',
        nameEn: 'Imperial Guard Garrison Bastion',
        styleTag: 'Тяжелый Бастион',
        description: 'Двухэтажная каменная крепость из глубинного сланца с амбразурами, бронированными железными воротами и смотровой вышкой.',
        lore: 'Спроектирован выдерживать прямое попадание пушечных ядер. Внутри оборудован подземный пороховой склад.',
        dimensions: { width: 14, length: 28, height: 14 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 2 },
        requiredLevel: 35,
        blockCountTotal: 2150,
        appliedRules: {
          depthRule: 'Двойная скошенная стена фундамента с машикулями на высоте 8 блоков защищает основание от подкопов.',
          gradientFormula: 'Базальт → Плиты глубинного сланца → Каменные кирпичи → Железный бруствер.',
          roofProfile: 'Плоская боевая кровля-плац с зубцами мерлонами и угловыми барбаканами.',
          lightingDetail: 'Защищенные факелы в бойницах и прожекторы на вышке.'
        },
        palette: [
          { name: 'Глубинный сланец', hex: '#262930', percentage: 48, icon: '⬛' },
          { name: 'Каменные кирпичи', hex: '#6b7280', percentage: 26, icon: '🧱' },
          { name: 'Железные блоки', hex: '#94a3b8', percentage: 14, icon: '🛡️' },
          { name: 'Базальт', hex: '#374151', percentage: 12, icon: '🪨' }
        ],
        buildCommand: '/townybuild build barracks --style=bastion',
        elements: [
          { name: 'Бронированный цоколь', from: [-7, 0, -14], to: [7, 3, 14], color: '#1f2228', stroke: '#323742', materialName: 'Полированный базальт' },
          { name: 'Стены бастиона', from: [-6, 3, -13], to: [6, 9, 13], color: '#383d47', stroke: '#4d5462', materialName: 'Сланцевые кирпичи' },
          // Corner Turrets (4 corner towers)
          { name: 'Угловая башня СЗ', from: [-7.2, 2, -14.2], to: [-4.8, 11, -11.8], color: '#272a31', stroke: '#3d424e', materialName: 'Угловой барбакан' },
          { name: 'Угловая башня СВ', from: [4.8, 2, -14.2], to: [7.2, 11, -11.8], color: '#272a31', stroke: '#3d424e', materialName: 'Угловой барбакан' },
          { name: 'Угловая башня ЮЗ', from: [-7.2, 2, 11.8], to: [-4.8, 11, 14.2], color: '#272a31', stroke: '#3d424e', materialName: 'Угловой барбакан' },
          { name: 'Угловая башня ЮВ', from: [4.8, 2, 11.8], to: [7.2, 11, 14.2], color: '#272a31', stroke: '#3d424e', materialName: 'Угловой барбакан' },
          // Battlements & Walkway
          { name: 'Зубчатый парапет (Мерлоны)', from: [-6.5, 9, -13.5], to: [6.5, 11, 13.5], color: '#4b525e', stroke: '#616978', materialName: 'Зубцы-мерлоны' },
          // Watch Post Spire
          { name: 'Наблюдательная вышка', from: [-2.5, 9, -2.5], to: [2.5, 14, 2.5], color: '#2b2f38', stroke: '#434957', materialName: 'Центральная вышка' }
        ]
      }
    ]
  },
  {
    id: 'watchtower',
    baseNameRu: 'Дозорная Башня',
    category: 'military',
    variants: [
      {
        id: 'timber_sentry',
        nameRu: 'Северная Вежа с Навесом',
        nameEn: 'Northern Timber Sentry Tower',
        styleTag: 'Камень и Дерево',
        description: 'Коническая каменная основа 7x7 блоков с расширяющейся на деревянных консолях верхней боевой площадкой.',
        lore: 'С верхней площадки открывается круговой обзор на все чанки города. Часовой замечает армию врага задолго до осады.',
        dimensions: { width: 7, length: 7, height: 18 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 5,
        blockCountTotal: 780,
        appliedRules: {
          depthRule: 'Верхняя боевая площадка вынесена на 1.5 блока консолями (кронштейнами) из ступеней и бревен.',
          gradientFormula: 'Булыжник у земли → Каменные кирпичи по стволу → Темный дуб на боевом ярусе.',
          roofProfile: 'Четырехскатный крутой пирамидальный навес со смотровыми бойницами.',
          lightingDetail: 'Подвесные сигнальные фонари во все четыре стороны света.'
        },
        palette: [
          { name: 'Каменные кирпичи', hex: '#717882', percentage: 44, icon: '🧱' },
          { name: 'Темный дуб', hex: '#3d2814', percentage: 32, icon: '🪵' },
          { name: 'Булыжник', hex: '#52575e', percentage: 16, icon: '🪨' },
          { name: 'Фонари и решетки', hex: '#f59e0b', percentage: 8, icon: '🏮' }
        ],
        buildCommand: '/townybuild build watchtower --style=timber',
        elements: [
          { name: 'Расширенное подножие', from: [-3.5, 0, -3.5], to: [3.5, 2.5, 3.5], color: '#42464d', stroke: '#585d66', materialName: 'Булыжный цоколь' },
          { name: 'Ствол башни (Шахта)', from: [-2.5, 2.5, -2.5], to: [2.5, 12, 2.5], color: '#68707a', stroke: '#818b96', materialName: 'Каменные кирпичи' },
          // Corbel Brackets (Вынос консолей: +1.5 блока наружу)
          { name: 'Консоли расширения', from: [-3.2, 11, -3.2], to: [3.2, 12.5, 3.2], color: '#3d2814', stroke: '#5a3d20', materialName: 'Деревянные консоли' },
          // Overhanging Sentry Box
          { name: 'Выносная смотровая', from: [-3.8, 12.5, -3.8], to: [3.8, 15.5, 3.8], color: '#4a331c', stroke: '#634527', materialName: 'Боевая площадка' },
          // Steep Pyramid Roof
          { name: 'Шатер крыши', from: [-4.2, 15.5, -4.2], to: [4.2, 19, 4.2], color: '#1c1917', stroke: '#332e2b', materialName: 'Гонтовый шатер' },
          { name: 'Шпиль с флюгером', from: [-0.4, 19, -0.4], to: [0.4, 21, 0.4], color: '#d97706', stroke: '#f59e0b', materialName: 'Медный флюгер' }
        ]
      },
      {
        id: 'gothic_spire',
        nameRu: 'Готический Шпилевой Донжон',
        nameEn: 'Gothic Citadel Spire',
        styleTag: 'Готический Донжон',
        description: 'Восьмигранная каменная башня со стрельчатыми бойницами, выносными машикулями и шпилем из темного призмарина.',
        lore: 'Высочайшая точка крепости, выдерживающая любые ураганы. Служит также ориентиром для торговых караванов.',
        dimensions: { width: 7, length: 7, height: 23 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 20,
        blockCountTotal: 960,
        appliedRules: {
          depthRule: 'Стрельчатые контрфорсы с 4 сторон создают крестообразную форму ствола башни.',
          gradientFormula: 'Глубинный сланец → Андезит → Каменные кирпичи → Медный шпиль.',
          roofProfile: 'Стрельчатый восьмигранный готический шпиль крутизной 4:1.',
          lightingDetail: 'Светящиеся кристаллы маяка на вершине шпиля.'
        },
        palette: [
          { name: 'Сланцевые кирпичи', hex: '#333842', percentage: 40, icon: '⬛' },
          { name: 'Полированный андезит', hex: '#8a939e', percentage: 35, icon: '🏛️' },
          { name: 'Окисленная медь', hex: '#0d9488', percentage: 15, icon: '🟢' },
          { name: 'Маяк и золото', hex: '#38bdf8', percentage: 10, icon: '💎' }
        ],
        buildCommand: '/townybuild build watchtower --style=gothic',
        elements: [
          { name: 'Цоколь с контрфорсами', from: [-3.8, 0, -3.8], to: [3.8, 3, 3.8], color: '#272b33', stroke: '#3d434f', materialName: 'Сланцевый фундамент' },
          { name: 'Восьмигранный ствол', from: [-2.6, 3, -2.6], to: [2.6, 15, 2.6], color: '#565e6b', stroke: '#6e7787', materialName: 'Андезитовая кладка' },
          { name: 'Машикули и карниз', from: [-3.5, 14.5, -3.5], to: [3.5, 16.5, 3.5], color: '#333842', stroke: '#4b5260', materialName: 'Выносные машикули' },
          { name: 'Зубчатый ярус с бойницами', from: [-3.2, 16.5, -3.2], to: [3.2, 18.5, 3.2], color: '#687282', stroke: '#828c9e', materialName: 'Стрелковая площадка' },
          { name: 'Окисленный медный шпиль', from: [-1.8, 18.5, -1.8], to: [1.8, 24, 1.8], color: '#0f766e', stroke: '#14b8a6', materialName: 'Медный шпиль' }
        ]
      }
    ]
  },
  {
    id: 'city_wall',
    baseNameRu: 'Городская Стена',
    category: 'defense',
    variants: [
      {
        id: 'rampart_classic',
        nameRu: 'Крепостная Стена с Галереей',
        nameEn: 'Medieval Fortress Curtain Wall',
        styleTag: 'Классическая Кутина',
        description: 'Укрепленная секция 16x8 блоков: массивные контрфорсы, мерлоны с укрытиями от стрел и крытая деревянная галерея.',
        lore: 'Непреодолимая преграда для пехоты. Ширина стены позволяет передвигаться двум конным стражникам бок о бок.',
        dimensions: { width: 16, length: 8, height: 12 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 10,
        blockCountTotal: 1540,
        appliedRules: {
          depthRule: 'Контрфорсы выступают на 1 блок вперед через каждые 4 блока; стрелковые бойницы утоплены внутрь.',
          gradientFormula: 'Замшелый булыжник у земли → Каменные кирпичи в теле → Сланцевые полублоки на парапете.',
          roofProfile: 'Односкатный деревянный навес над стрелковой галереей для защиты от навесных стрел.',
          lightingDetail: 'Фонари на кронштейнах вдоль всего внутреннего прохода.'
        },
        palette: [
          { name: 'Каменные кирпичи', hex: '#717882', percentage: 46, icon: '🧱' },
          { name: 'Булыжник', hex: '#52575e', percentage: 22, icon: '🪨' },
          { name: 'Темный дуб', hex: '#422e1b', percentage: 18, icon: '🪵' },
          { name: 'Железные решетки', hex: '#94a3b8', percentage: 14, icon: '⛓️' }
        ],
        buildCommand: '/townybuild build city_wall --style=classic',
        elements: [
          { name: 'Массивный цокольный вал', from: [-8, 0, -3.5], to: [8, 2, 3.5], color: '#3d424a', stroke: '#525963', materialName: 'Булыжное основание' },
          { name: 'Тело стены (Броня)', from: [-8, 2, -2.5], to: [8, 8, 2.5], color: '#68707a', stroke: '#818b96', materialName: 'Каменные кирпичи' },
          // Buttresses (Контрфорсы)
          { name: 'Контрфорс Левый', from: [-6, 1, 2.5], to: [-4, 7.5, 3.8], color: '#4f555e', stroke: '#68707a', materialName: 'Выносной контрфорс' },
          { name: 'Контрфорс Центр', from: [-1, 1, 2.5], to: [1, 7.5, 3.8], color: '#4f555e', stroke: '#68707a', materialName: 'Выносной контрфорс' },
          { name: 'Контрфорс Правый', from: [4, 1, 2.5], to: [6, 7.5, 3.8], color: '#4f555e', stroke: '#68707a', materialName: 'Выносной контрфорс' },
          // Walkway Deck & Crenelations
          { name: 'Боевой ход (Настил)', from: [-8, 8, -2.8], to: [8, 8.8, 2.8], color: '#2b303a', stroke: '#3f4756', materialName: 'Сланцевый настил' },
          { name: 'Зубцы-мерлоны (Парапет)', from: [-8, 8.8, 2], to: [8, 10.5, 2.8], color: '#68707a', stroke: '#818b96', materialName: 'Зубцы мерлоны' },
          // Covered Timber Canopy
          { name: 'Крыша галереи', from: [-8, 10.5, -3.2], to: [8, 12, 0.5], color: '#2b1b0e', stroke: '#472d17', materialName: 'Деревянный навес' }
        ]
      },
      {
        id: 'gothic_machicolated',
        nameRu: 'Сланцевая Куртина с Машикулями',
        nameEn: 'Deepslate Machicolated Curtain',
        styleTag: 'Тяжелый Сланец',
        description: 'Высокая стена из глубинного сланца с выносными камнемётными галереями (машикулями) и двойным стрелковым ярусом.',
        lore: 'Создана специально для отражения пушечных атак. Скошенный цоколь рикошетит падающие снаряды.',
        dimensions: { width: 16, length: 8, height: 14 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 25,
        blockCountTotal: 1880,
        appliedRules: {
          depthRule: 'Машикули выступают на 1 блок по всей длине стены со щелями для сброса лавы.',
          gradientFormula: 'Базальт → Сланцевые кирпичи → Полированный сланец → Железные щиты.',
          roofProfile: 'Двусторонний зубчатый парапет с укрытиями от флангового огня.',
          lightingDetail: 'Встроенные светильники в амбразурах машикулей.'
        },
        palette: [
          { name: 'Сланцевые кирпичи', hex: '#262930', percentage: 55, icon: '⬛' },
          { name: 'Полированный сланец', hex: '#373b45', percentage: 25, icon: '🧱' },
          { name: 'Базальт', hex: '#1c1e24', percentage: 12, icon: '🪨' },
          { name: 'Железные решетки', hex: '#94a3b8', percentage: 8, icon: '⛓️' }
        ],
        buildCommand: '/townybuild build city_wall --style=machicolated',
        elements: [
          { name: 'Скошенный цоколь', from: [-8, 0, -4], to: [8, 3, 4], color: '#1c1e24', stroke: '#2c2f38', materialName: 'Базальтовый скос' },
          { name: 'Монолитная стена', from: [-8, 3, -3], to: [8, 10, 3], color: '#2d313a', stroke: '#404552', materialName: 'Сланцевые кирпичи' },
          { name: 'Выносные машикули', from: [-8, 9.5, 2.5], to: [8, 11.5, 4.2], color: '#1c1e24', stroke: '#30343f', materialName: 'Машикули' },
          { name: 'Боевой парапет', from: [-8, 11.5, 3.2], to: [8, 13.5, 4.2], color: '#3d424e', stroke: '#525968', materialName: 'Мерлоны со щелями' },
          { name: 'Внутренний ход', from: [-8, 10, -3], to: [8, 10.8, 3], color: '#262930', stroke: '#3a3e48', materialName: 'Бронебойный настил' }
        ]
      }
    ]
  },
  {
    id: 'hospital',
    baseNameRu: 'Городская Больница',
    category: 'civilian',
    variants: [
      {
        id: 'monastery_infirmary',
        nameRu: 'Орденский Госпиталь',
        nameEn: 'Order Monastery Infirmary',
        styleTag: 'Фахверк и Белый Бетон',
        description: 'Светлый фасад с белым бетоном, темным дубовым каркасом, аптекарской оранжереей и крестообразным порталом.',
        lore: 'Здесь день и ночь варят лечебные зелья и ухаживают за ранеными солдатами после битв за территории.',
        dimensions: { width: 12, length: 12, height: 10 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 20,
        blockCountTotal: 1120,
        appliedRules: {
          depthRule: 'Контрастный дубовый фахверк вынесен на 1 блок относительно белоснежных стен.',
          gradientFormula: 'Каменный цоколь → Белый бетон с красным крестом → Темный дуб на стропилах.',
          roofProfile: 'Крутая двускатная кровля с врезанными слуховыми окнами для вентиляции палат.',
          lightingDetail: 'Теплые фонари над каждым койко-местом и светящиеся колбы с зельями.'
        },
        palette: [
          { name: 'Белый бетон', hex: '#f8fafc', percentage: 38, icon: '⬜' },
          { name: 'Темный дуб', hex: '#422e1b', percentage: 26, icon: '🪵' },
          { name: 'Каменные кирпичи', hex: '#717882', percentage: 18, icon: '🧱' },
          { name: 'Красная шерсть (Крест)', hex: '#ef4444', percentage: 10, icon: '🟥' },
          { name: 'Стекло', hex: '#38bdf8', percentage: 8, icon: '🪟' }
        ],
        buildCommand: '/townybuild build hospital --style=monastery',
        elements: [
          { name: 'Каменный цоколь', from: [-6, 0, -6], to: [6, 1.5, 6], color: '#52575e', stroke: '#696f78', materialName: 'Каменные кирпичи' },
          { name: 'Белоснежные стены', from: [-5, 1.5, -5], to: [5, 6, 5], color: '#f1f5f9', stroke: '#cbd5e1', materialName: 'Белый бетон' },
          // Timber Framing Posts
          { name: 'Фахверк СЗ', from: [-5.6, 1.5, -5.6], to: [-4.6, 6.5, -4.6], color: '#3d2814', stroke: '#5a3d20', materialName: 'Дубовый каркас' },
          { name: 'Фахверк СВ', from: [4.6, 1.5, -5.6], to: [5.6, 6.5, -4.6], color: '#3d2814', stroke: '#5a3d20', materialName: 'Дубовый каркас' },
          { name: 'Фахверк ЮЗ', from: [-5.6, 1.5, 4.6], to: [-4.6, 6.5, 5.6], color: '#3d2814', stroke: '#5a3d20', materialName: 'Дубовый каркас' },
          { name: 'Фахверк ЮВ', from: [4.6, 1.5, 4.6], to: [5.6, 6.5, 5.6], color: '#3d2814', stroke: '#5a3d20', materialName: 'Дубовый каркас' },
          // Red Cross Sign
          { name: 'Красный крест фасада', from: [-1.2, 3, 5.2], to: [1.2, 5.2, 5.4], color: '#dc2626', stroke: '#ef4444', materialName: 'Красный крест' },
          // High Roof with Dormers
          { name: 'Крыша госпиталя', from: [-5.8, 6, -5.5], to: [5.8, 9.5, 5.5], color: '#1c1917', stroke: '#332e2b', materialName: 'Темная кровля' },
          { name: 'Вентиляционная башенка', from: [-1.2, 9.5, -1.2], to: [1.2, 11.5, 1.2], color: '#422e1b', stroke: '#5c4126', materialName: 'Аптекарская вышка' }
        ]
      }
    ]
  },
  {
    id: 'arcane_library',
    baseNameRu: 'Тайная Библиотека Чар',
    category: 'magic',
    variants: [
      {
        id: 'wizard_sanctum',
        nameRu: 'Шпиль Архимага',
        nameEn: 'Archmage Wizard Sanctum',
        styleTag: 'Обсидиан и Лазурит',
        description: 'Витая мистическая башня с парящими арками, кристаллическими лазуритовыми рунами и зачаровальней высшего круга.',
        lore: 'В книгах этой библиотеки хранятся древнейшие заклинания починки и шелкового касания, запрещенные в обычных мирах.',
        dimensions: { width: 10, length: 10, height: 16 },
        chunkFootprint: { widthChunks: 1, lengthChunks: 1 },
        requiredLevel: 30,
        blockCountTotal: 1240,
        appliedRules: {
          depthRule: 'Парящие обсидиановые контрфорсы отделены от стен башни на 1 блок воздуха и соединяются только в арках.',
          gradientFormula: 'Обсидиан → Темный призмарин → Лазурит → Аметистовые кристаллы.',
          roofProfile: 'Спиральный кристаллический шпиль с парящим маяком над книжным залом.',
          lightingDetail: 'Пульсирующие лазуритовые лампы и мистические частицы чар.'
        },
        palette: [
          { name: 'Книжные полки', hex: '#854d0e', percentage: 35, icon: '📚' },
          { name: 'Обсидиан', hex: '#1e112a', percentage: 25, icon: '⬛' },
          { name: 'Лазурит', hex: '#1d4ed8', percentage: 20, icon: '🔷' },
          { name: 'Темный дуб', hex: '#3d2814', percentage: 12, icon: '🪵' },
          { name: 'Аметист/Чуд', hex: '#c084fc', percentage: 8, icon: '✨' }
        ],
        buildCommand: '/townybuild build arcane_library --style=sanctum',
        elements: [
          { name: 'Обсидиановый алтарь', from: [-5, 0, -5], to: [5, 1.5, 5], color: '#160d21', stroke: '#2e1c45', materialName: 'Обсидиан' },
          { name: 'Книжная ротонда', from: [-4, 1.5, -4], to: [4, 9, 4], color: '#3d2814', stroke: '#5a3d20', materialName: 'Книжные полки и дуб' },
          // Floating Arcane Buttresses
          { name: 'Арка СЗ', from: [-5.5, 1.5, -5.5], to: [-3.8, 10, -3.8], color: '#1e1b4b', stroke: '#312e81', materialName: 'Мистическая арка' },
          { name: 'Арка СВ', from: [3.8, 1.5, -5.5], to: [5.5, 10, -3.8], color: '#1e1b4b', stroke: '#312e81', materialName: 'Мистическая арка' },
          { name: 'Арка ЮЗ', from: [-5.5, 1.5, 3.8], to: [-3.8, 10, 5.5], color: '#1e1b4b', stroke: '#312e81', materialName: 'Мистическая арка' },
          { name: 'Арка ЮВ', from: [3.8, 1.5, 3.8], to: [5.5, 10, 5.5], color: '#1e1b4b', stroke: '#312e81', materialName: 'Мистическая арка' },
          // Upper Celestial Observatory
          { name: 'Зачаровальный купол', from: [-3.2, 9, -3.2], to: [3.2, 13, 3.2], color: '#1d4ed8', stroke: '#3b82f6', materialName: 'Лазуритовый свод' },
          { name: 'Кристаллический шпиль', from: [-1, 13, -1], to: [1, 17, 1], color: '#a855f7', stroke: '#c084fc', materialName: 'Аметистовый шпиль' }
        ]
      }
    ]
  },
  {
    id: 'sun_pyramid',
    baseNameRu: 'Великая Пирамида Солнца (Чудо Света)',
    category: 'wonder',
    variants: [
      {
        id: 'golden_ziggurat',
        nameRu: 'Золотой Зиккурат Солнца',
        nameEn: 'Golden Sun Ziggurat',
        styleTag: 'Ступенчатый Монолит',
        description: 'Грандиозный 20x20 ступенчатый зиккурат из резного песчаника с золочеными ступенями и сияющим лучом маяка.',
        lore: 'Чудо Света, воздвигнутое в зените могущества империи. Дарует пассивную Спешку II и Сопротивление всем жителям нации.',
        dimensions: { width: 20, length: 20, height: 16 },
        chunkFootprint: { widthChunks: 2, lengthChunks: 2 },
        requiredLevel: 50,
        blockCountTotal: 3480,
        appliedRules: {
          depthRule: 'Каждый ярус сужается на 1.5 блока внутрь, образуя широкие паломнические террасы с колоннами.',
          gradientFormula: 'Красный песчаник в основании → Гладкий песчаник → Резной песчаник → Золотые блоки.',
          roofProfile: 'Усеченная пирамида с алтарной платформой и вечным огнем в чашах.',
          lightingDetail: 'Сияющий луч маяка 256 блоков в небо и золотые факелы.'
        },
        palette: [
          { name: 'Гладкий песчаник', hex: '#d8cb9a', percentage: 55, icon: '🏜️' },
          { name: 'Резной песчаник', hex: '#cbbd88', percentage: 22, icon: '🏛️' },
          { name: 'Золотые блоки', hex: '#f59e0b', percentage: 14, icon: '👑' },
          { name: 'Маяк и Незерит', hex: '#38bdf8', percentage: 9, icon: '💎' }
        ],
        buildCommand: '/townybuild build sun_pyramid --style=ziggurat',
        elements: [
          { name: 'Ярус 1 (Основание)', from: [-9.5, 0, -9.5], to: [9.5, 2.5, 9.5], color: '#b5a470', stroke: '#c9b782', materialName: 'Красный песчаник' },
          { name: 'Ярус 2 (Терраса)', from: [-8, 2.5, -8], to: [8, 5, 8], color: '#c4b37d', stroke: '#d9c68f', materialName: 'Гладкий песчаник' },
          { name: 'Ярус 3 (Терраса)', from: [-6.5, 5, -6.5], to: [6.5, 7.5, 6.5], color: '#cbbd88', stroke: '#dfcf9b', materialName: 'Песчаник' },
          { name: 'Ярус 4 (Терраса)', from: [-5, 7.5, -5], to: [5, 10, 5], color: '#d8cb9a', stroke: '#ebdcb0', materialName: 'Резной песчаник' },
          { name: 'Ярус 5 (Святилище)', from: [-3.5, 10, -3.5], to: [3.5, 12.5, 3.5], color: '#e5d9a9', stroke: '#f5e9bd', materialName: 'Песчаниковый алтарь' },
          // Top Golden Altar & Beacon Platform
          { name: 'Золотой алтарь солнца', from: [-2.2, 12.5, -2.2], to: [2.2, 14, 2.2], color: '#d97706', stroke: '#f59e0b', materialName: 'Золотые блоки' },
          { name: 'Маяк Чуда Света', from: [-1, 14, -1], to: [1, 15.5, 1], color: '#38bdf8', stroke: '#7dd3fc', materialName: 'Сияющий маяк' }
        ]
      }
    ]
  }
];
'''

with open('src/data/buildingVariantsData.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print("buildingVariantsData.ts successfully created!")
