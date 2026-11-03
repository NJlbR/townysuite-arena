import os

code = '''import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Layers,
  BookOpen,
  Sparkles,
  Shield,
  Hammer,
  Eye,
  Compass,
  Code2,
  Wrench,
  Download,
  Check,
  Palette,
  RotateCw,
  ZoomIn,
  ZoomOut,
  Copy,
  ExternalLink,
  ChevronRight,
  Castle,
  Building2,
  Flame,
  Crosshair,
  HelpCircle,
  Play,
  Pause,
  RotateCcw,
  Sun,
  Moon,
  Sunset,
  Info,
  Maximize2
} from 'lucide-react';
import {
  CANNON_MODEL_JSON,
  CANNON_VANILLA_MODEL_JSON,
  CANNON_CUSTOM_MODEL_JSON,
  CANNON_MODEL_JSON_STR,
  CANNON_VANILLA_JSON_STR,
  CANNON_CUSTOM_JSON_STR,
  CANNON_BBMODEL_JSON_STR,
  CANNON_METADATA
} from '../data/cannonModelData';
import {
  downloadCannonBbmodel,
  downloadCannonJson,
  downloadCannonVanillaJson,
  downloadCannonCustomJson,
  downloadCannonWoodPng,
  downloadCannonMetalPng,
  downloadCannonRp
} from '../utils/downloadHelpers';
import { BUILDING_FAMILIES, BuildingFamily, BuildingVariant, SolidVolume } from '../data/buildingVariantsData';
import { INITIAL_BLUEPRINTS } from '../data/defaultBuildings';

// Additional 3D Siege item models for preview
interface ElementBox {
  name: string;
  from: [number, number, number];
  to: [number, number, number];
  color: string;
  stroke: string;
}

interface ItemModel3D {
  id: string;
  nameRu: string;
  category: string;
  description: string;
  customModelData: number;
  texturePack: string;
  elements: ElementBox[];
}

const SIEGE_MODELS: ItemModel3D[] = [
  {
    id: 'cannon',
    nameRu: '32-фунтовая Осадная Пушка',
    category: 'Тяжелая артиллерия',
    description: 'Основное осадное орудие TownySieges. Разрушает стены баллистическими ядрами, наносит сплеш-урон и пробивает фортификации.',
    customModelData: 10001,
    texturePack: 'assets/siegecannons/textures/block/cannon_metal.png',
    elements: [
      { name: 'carriage_bed', from: [3, 1, 2], to: [13, 3, 15], color: '#382513', stroke: '#52341b' },
      { name: 'axle', from: [1, 2, 8], to: [15, 4, 10], color: '#1a1a1a', stroke: '#333333' },
      { name: 'wheel_left', from: [0, 0, 6], to: [2, 8, 12], color: '#2b1b0e', stroke: '#472d17' },
      { name: 'wheel_right', from: [14, 0, 6], to: [16, 8, 12], color: '#2b1b0e', stroke: '#472d17' },
      { name: 'left_cheek', from: [3, 3, 6], to: [5, 7, 13], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'right_cheek', from: [11, 3, 6], to: [13, 7, 13], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'trunnion_left', from: [4, 5, 8], to: [6, 7, 10], color: '#444444', stroke: '#666666' },
      { name: 'trunnion_right', from: [10, 5, 8], to: [12, 7, 10], color: '#444444', stroke: '#666666' },
      { name: 'breech', from: [5, 4, 11], to: [11, 8, 15], color: '#262626', stroke: '#3d3d3d' },
      { name: 'barrel_mid', from: [5.5, 4.5, 5], to: [10.5, 7.5, 11], color: '#333333', stroke: '#4d4d4d' },
      { name: 'barrel_muzzle', from: [6, 5, 0], to: [10, 7, 5], color: '#2b2b2b', stroke: '#404040' },
      { name: 'muzzle_ring', from: [5.5, 4.5, -0.5], to: [10.5, 7.5, 1], color: '#1f1f1f', stroke: '#383838' },
    ]
  },
  {
    id: 'mortar',
    nameRu: 'Мортира «Молот Осады»',
    category: 'Навесная мортира',
    description: 'Короткоствольное орудие высокого угла обстрела для перебрасывания зажигательных снарядов через высокие городские стены.',
    customModelData: 10002,
    texturePack: 'assets/siegecannons/textures/block/mortar_metal.png',
    elements: [
      { name: 'base_plate', from: [2, 0, 2], to: [14, 2, 14], color: '#1a1a1a', stroke: '#333333' },
      { name: 'timber_mount', from: [3, 2, 4], to: [13, 5, 12], color: '#382513', stroke: '#52341b' },
      { name: 'bracket_left', from: [2, 4, 5], to: [4, 9, 11], color: '#2d1c0f', stroke: '#4a2f1a' },
      { name: 'bracket_right', from: [12, 4, 5], to: [14, 9, 11], color: '#2d1c0f', stroke: '#4a2f1a' },
      { name: 'chamber_breech', from: [4, 5, 8], to: [12, 11, 14], color: '#222222', stroke: '#3a3a3a' },
      { name: 'barrel_chubby', from: [4.5, 8, 4], to: [11.5, 14, 10], color: '#2b2b2b', stroke: '#474747' },
      { name: 'muzzle_bell', from: [4, 13, 3], to: [12, 16, 9], color: '#1a1a1a', stroke: '#333333' },
    ]
  },
  {
    id: 'ballista',
    nameRu: 'Тяжелая Осадная Баллиста',
    category: 'Метательное орудие',
    description: 'Станковый бронебойный торсионный стреломет. Идеален для точечного снятия защитников с башен и пробивания деревянных ворот.',
    customModelData: 10003,
    texturePack: 'assets/siegecannons/textures/block/ballista_wood.png',
    elements: [
      { name: 'tripod_front_left', from: [2, 0, 3], to: [4, 6, 5], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'tripod_front_right', from: [12, 0, 3], to: [14, 6, 5], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'tripod_rear', from: [7, 0, 13], to: [9, 5, 15], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'stock_body', from: [6, 5, 1], to: [10, 8, 15], color: '#2b1b0e', stroke: '#472d17' },
      { name: 'guide_rail', from: [7, 8, 2], to: [9, 9, 14], color: '#1f1f1f', stroke: '#383838' },
      { name: 'cross_beam', from: [-2, 6, 1], to: [18, 8, 3], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'tension_string_left', from: [-1, 7, 2], to: [7, 8, 9], color: '#d97706', stroke: '#f59e0b' },
      { name: 'tension_string_right', from: [17, 7, 2], to: [9, 8, 9], color: '#d97706', stroke: '#f59e0b' },
      { name: 'bolt_steel', from: [7.5, 8.5, 0], to: [8.5, 9.5, 11], color: '#94a3b8', stroke: '#cbd5e1' },
    ]
  },
  {
    id: 'ram',
    nameRu: 'Кованый Таран с Навесом',
    category: 'Штурмовой таран',
    description: 'Подвесное бревно с кованой насадкой на цепях под крытым гонтовым навесом, защищающим штурмующих от стрел и кипящего масла.',
    customModelData: 10004,
    texturePack: 'assets/siegecannons/textures/block/ram_timber.png',
    elements: [
      { name: 'skid_left', from: [2, 0, 1], to: [4, 2, 15], color: '#2b1b0e', stroke: '#472d17' },
      { name: 'skid_right', from: [12, 0, 1], to: [14, 2, 15], color: '#2b1b0e', stroke: '#472d17' },
      { name: 'post_fl', from: [2, 2, 2], to: [4, 11, 4], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'post_fr', from: [12, 2, 2], to: [14, 11, 4], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'post_rl', from: [2, 2, 12], to: [4, 11, 14], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'post_rr', from: [12, 2, 12], to: [14, 11, 14], color: '#3d2814', stroke: '#5e3e20' },
      { name: 'roof_ridge', from: [1, 11, 0], to: [15, 13, 16], color: '#1c1917', stroke: '#292524' },
      { name: 'ram_timber', from: [6, 4, 1], to: [10, 8, 15], color: '#451a03', stroke: '#78350f' },
      { name: 'iron_ram_head', from: [5.5, 3.5, -2], to: [10.5, 8.5, 2], color: '#334155', stroke: '#64748b' },
    ]
  }
];

// Architectural Building Guides Data
interface BuildingManual {
  title: string;
  subtitle: string;
  category: string;
  difficulty: 'Новичок' | 'Мастер' | 'Эксперт';
  readTime: string;
  summary: string;
  proTips: string[];
  gradientFormula: string[];
  depthRules: string[];
  palette: { name: string; hex: string; role: string }[];
}

const ARCHITECTURE_MANUALS: BuildingManual[] = [
  {
    title: 'Правило 3D-Глубины и Рельефа Фасадов',
    subtitle: 'Как навсегда избавиться от скучных плоских коробок в Майнкрафте',
    category: 'Основы архитектуры',
    difficulty: 'Новичок',
    readTime: '4 мин',
    summary: 'Любая стена в Minecraft кажется плоской и игрушечной, если все блоки находятся в одной плоскости. Профессиональные строители создают минимум 3 слоя глубины: вынесенный силовой каркас (вперед на 1 блок), несущую стену (средний слой) и углубленные оконные ниши/бойницы (назад на 1 блок).',
    proTips: [
      'Выносите вертикальные колонны (обтесанные бревна, сланцевые пилястры) на 1 блок вперед от плоскости фасада.',
      'Используйте перевернутые ступени под оконными проемами и под карнизом крыши — это создает плавные полукруглые арки без квадратных углов.',
      'Добавляйте ограды (Walls) и железные решетки вместо обычного плоского стекла: они занимают центральные 2 пикселя блока и дают мощный рельеф.',
      'Создавайте контрфорсы: утолщение фундамента на 2 блока у основания, сужающееся к середине стены ступенями.'
    ],
    gradientFormula: [
      'Слой 0-1 (Фундамент): Глубинный сланец (Deepslate) + Базальт для эффекта массивности и веса',
      'Слой 2-3 (Нижний цоколь): Булыжник (Cobblestone) + Андезит (Andesite) с легким выветриванием',
      'Слой 4-6 (Тело стены): Каменные кирпичи (Stone Bricks) + Потрескавшиеся кирпичи',
      'Слой 7+ (Карниз): Полированный андезит + Деревянные стропила'
    ],
    depthRules: [
      'Z -1: Внутренние оконные рамы, тонкое стекло, фонари в нишах',
      'Z 0: Основная кладка стены из каменных кирпичей',
      'Z +1: Несущие балки из бревен, контрфорсы, нависающие крыши и желоба',
      'Z +2: Входные порталы, балконы, подвесные вывески и факельные бра'
    ],
    palette: [
      { name: 'Каменные кирпичи', hex: '#88929e', role: 'Основной каркас' },
      { name: 'Глубинный сланец', hex: '#333842', role: 'Массивный цоколь' },
      { name: 'Обтесанный темный дуб', hex: '#422e1b', role: 'Силовые балки' },
      { name: 'Булыжник', hex: '#717882', role: 'Текстурный шум' },
      { name: 'Светящийся фонарь', hex: '#f59e0b', role: 'Точечный акцент' }
    ]
  },
  {
    title: 'Анатомия Реалистичных Крыш (A-Frame, Mansard, Gable)',
    subtitle: 'Геометрия без эффекта «ступенчатой пирамиды» и плоских скатов',
    category: 'Кровельное искусство',
    difficulty: 'Мастер',
    readTime: '6 мин',
    summary: 'Худшая ошибка — делать крышу простым чередованием ступеней под 45 градусов. Красивые средневековые крыши имеют крутой подъем (A-Frame 2:1), голландские фронтоны (Dutch Gable) и обязательный вынос карниза наружу минимум на 1-2 блока.',
    proTips: [
      'Чередуйте блок + ступенька для создания крутых готических крыш (наклон 60 градусов вместо стандартных 45).',
      'Обязательно делайте нависание (Overhang): карниз должен выступать на 1 блок по бокам и на 1 блок спереди от стены.',
      'Поддерживайте нависающие ступени перевернутыми ступенями снизу — крыша сразу становится монолитной и тяжелой.',
      'Используйте контрастный обод (Trim): если крыша из темного призмарина или темного дуба, окантуйте скат каменными кирпичами или диоритом.'
    ],
    gradientFormula: [
      'Нижний скат: Темные сланцевые плиты (Deepslate Tiles)',
      'Середина ската: Доски из темного дуба + Еловые ступени',
      'Конек крыши: Полублоки из булыжника + Люки из темного дуба для гребня',
      'Оконные слуховые люкарны: Врезка фронтонов со стеклянными бойницами'
    ],
    depthRules: [
      'Вынос карниза вперед: +1 блок по отношению к фронтону',
      'Перевернутые ступени снизу: скрывают пустоты и дают толщину стропилам',
      'Деревянные балки-стяжки: поперечные перекладины под коньком для реализма'
    ],
    palette: [
      { name: 'Темный дуб', hex: '#3d2614', role: 'Основное покрытие' },
      { name: 'Сланцевые плиты', hex: '#262930', role: 'Тяжелый контур' },
      { name: 'Еловые ступени', hex: '#5c4028', role: 'Переходы и скаты' },
      { name: 'Еловые люки', hex: '#483320', role: 'Гребень и слуховые окна' }
    ]
  },
  {
    title: 'Фортификация: Стены, Зубцы, Машикули и Бойницы',
    subtitle: 'Как строить городские стены, которые выглядят неприступно и защищают в PvP',
    category: 'Военная архитектура',
    difficulty: 'Эксперт',
    readTime: '5 мин',
    summary: 'В плагине Towny городские стены — это первая линия обороны от пушечных ядер и штурмовых лестниц. Правильная стена имеет стрелковую галерею (walkway), зубцы-мерлоны с укрытиями от стрел и выносные машикули для сброса лавы и камней.',
    proTips: [
      'Шаг зубцов: делайте мерлоны по схеме 1 блок зубец, 1 блок бойница (или 2 блока укрытия, 1 проем с полублоком).',
      'На вершине стены используйте каменные ограды: игрок за ними полностью защищен хитбоксом от попадания стрел скелетов и вражеских снайперов.',
      'Машикули: выносные кронштейны из ступеней на высоте 8-10 блоков позволяют защитникам смотреть строго вниз к подножию стены.',
      'Двухслойная броня: внешний слой из каменных кирпичей, внутренний сердечник из обсидиана или базальта для защиты от взрывов ТНТ.'
    ],
    gradientFormula: [
      'Цоколь (0-3 блока): Растрескавшиеся каменные кирпичи + Замшелый булыжник у земли',
      'Основная стена (4-8 блоков): Каменные кирпичи + Андезит для текстурного разнообразия',
      'Боевой ход (9-11 блоков): Сланцевые полублоки с факелами на цепях',
      'Зубцы (12 блок): Каменные ступени спиной наружу для создания бойниц'
    ],
    depthRules: [
      'Ширина стены минимум 3-5 блоков: 1 блок внешняя броня, 2-3 блока проход для стражи, 1 блок внутренний парапет',
      'Башни через каждые 3-4 чанка для флангового перекрестного огня'
    ],
    palette: [
      { name: 'Каменные кирпичи', hex: '#7a828e', role: 'Несущая броня' },
      { name: 'Потрескавшиеся кирпичи', hex: '#636b77', role: 'Следы осад' },
      { name: 'Замшелый камень', hex: '#5f7560', role: 'Влажность у земли' },
      { name: 'Железные прутья', hex: '#94a3b8', role: 'Стрелковые бойницы' }
    ]
  }
];

export const ModelPreviewHub: React.FC = () => {
  const [hubTab, setHubTab] = useState<'models' | 'buildings' | 'manuals'>('buildings');

  // Item Models State
  const [selectedModelId, setSelectedModelId] = useState<string>('cannon');
  const [wireframe, setWireframe] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [rotation, setRotation] = useState<{ yaw: number; pitch: number }>({ yaw: 35, pitch: 22 });
  const [zoom, setZoom] = useState<number>(1.1);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  // Buildings State
  const [selectedFamilyId, setSelectedFamilyId] = useState<string>('town_hall');
  const [selectedVariantId, setSelectedVariantId] = useState<string>('nordic_timber');
  const [buildingAutoRotate, setBuildingAutoRotate] = useState<boolean>(true);
  const [buildingRotation, setBuildingRotation] = useState<{ yaw: number; pitch: number }>({ yaw: 42, pitch: 26 });
  const [buildingZoom, setBuildingZoom] = useState<number>(1.0);
  const [buildingWireframe, setBuildingWireframe] = useState<boolean>(false);
  const [lightingMode, setLightingMode] = useState<'day' | 'sunset' | 'night'>('day');

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const buildingCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDraggingItemRef = useRef<boolean>(false);
  const isDraggingBuildingRef = useRef<boolean>(false);
  const lastMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const activeSiegeModel = SIEGE_MODELS.find((m) => m.id === selectedModelId) || SIEGE_MODELS[0];
  const activeFamily = BUILDING_FAMILIES.find((f) => f.id === selectedFamilyId) || BUILDING_FAMILIES[0];
  const activeVariant = activeFamily.variants.find((v) => v.id === selectedVariantId) || activeFamily.variants[0];

  // Helper copy function
  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2500);
  };

  // Switch family and select its first variant
  const handleSelectFamily = (familyId: string) => {
    setSelectedFamilyId(familyId);
    const fam = BUILDING_FAMILIES.find((f) => f.id === familyId);
    if (fam && fam.variants.length > 0) {
      setSelectedVariantId(fam.variants[0].id);
    }
  };

  // -------------------------------------------------------------
  // 3D Canvas Renderer for Item Models
  // -------------------------------------------------------------
  useEffect(() => {
    if (hubTab !== 'models') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const centerX = width / 2;
      const centerY = height / 2 + 15;

      const radYaw = (rotation.yaw * Math.PI) / 180;
      const radPitch = (rotation.pitch * Math.PI) / 180;
      const cosY = Math.cos(radYaw);
      const sinY = Math.sin(radYaw);
      const cosP = Math.cos(radPitch);
      const sinP = Math.sin(radPitch);

      const project = (x: number, y: number, z: number) => {
        const cx = x - 8;
        const cy = y - 4;
        const cz = z - 8;
        const rx = cx * cosY - cz * sinY;
        const rz = cx * sinY + cz * cosY;
        const ry = cy * cosP - rz * sinP;
        const finalZ = cy * sinP + rz * cosP;
        const scale = 17 * zoom;
        const px = centerX + rx * scale;
        const py = centerY - ry * scale;
        return { px, py, depth: finalZ };
      };

      // Draw subtle ground 16x16 grid
      ctx.strokeStyle = '#262626';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let g = 0; g <= 16; g += 4) {
        const p1 = project(g, -4, 0);
        const p2 = project(g, -4, 16);
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);
        const p3 = project(0, -4, g);
        const p4 = project(16, -4, g);
        ctx.moveTo(p3.px, p3.py);
        ctx.lineTo(p4.px, p4.py);
      }
      ctx.stroke();

      // Collect faces
      interface FaceToRender {
        points: { px: number; py: number }[];
        depth: number;
        color: string;
        stroke: string;
      }

      const facesToRender: FaceToRender[] = [];

      activeSiegeModel.elements.forEach((el) => {
        const [x1, y1, z1] = el.from;
        const [x2, y2, z2] = el.to;
        const corners = [
          project(x1, y1, z1), project(x2, y1, z1), project(x2, y2, z1), project(x1, y2, z1),
          project(x1, y1, z2), project(x2, y2, z2), project(x2, y2, z2), project(x1, y2, z2),
        ];

        const faceIndices = [
          { name: 'north', idxs: [0, 1, 2, 3] },
          { name: 'south', idxs: [5, 4, 7, 6] },
          { name: 'up',    idxs: [3, 2, 6, 7] },
          { name: 'down',  idxs: [4, 5, 1, 0] },
          { name: 'west',  idxs: [4, 0, 3, 7] },
          { name: 'east',  idxs: [1, 5, 6, 2] },
        ];

        faceIndices.forEach((f) => {
          const pts = f.idxs.map((i) => corners[i]);
          const avgDepth = pts.reduce((acc, p) => acc + p.depth, 0) / 4;

          // Backface culling
          const v1x = pts[1].px - pts[0].px;
          const v1y = pts[1].py - pts[0].py;
          const v2x = pts[2].px - pts[0].px;
          const v2y = pts[2].py - pts[0].py;
          const cross = v1x * v2y - v1y * v2x;

          if (cross < 0) {
            facesToRender.push({
              points: pts,
              depth: avgDepth,
              color: el.color,
              stroke: el.stroke,
            });
          }
        });
      });

      // Painter's algorithm
      facesToRender.sort((a, b) => a.depth - b.depth);

      facesToRender.forEach((face) => {
        ctx.beginPath();
        ctx.moveTo(face.points[0].px, face.points[0].py);
        for (let i = 1; i < face.points.length; i++) {
          ctx.lineTo(face.points[i].px, face.points[i].py);
        }
        ctx.closePath();

        if (wireframe) {
          ctx.strokeStyle = face.stroke;
          ctx.lineWidth = 1.5;
          ctx.stroke();
        } else {
          ctx.fillStyle = face.color;
          ctx.fill();
          ctx.strokeStyle = face.stroke;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      });

      if (autoRotate) {
        setRotation((prev) => ({ ...prev, yaw: (prev.yaw + 0.4) % 360 }));
      }
      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animationFrameId);
  }, [rotation, zoom, wireframe, autoRotate, activeSiegeModel, hubTab]);

  // -------------------------------------------------------------
  // SOLID 3D Canvas Renderer for Complete Minecraft Buildings
  // ("Отображение цельно, как в самом Minecraft")
  // -------------------------------------------------------------
  useEffect(() => {
    if (hubTab !== 'buildings') return;
    const canvas = buildingCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const centerX = width / 2;
      const centerY = height / 2 + 55;

      // Atmosphere Sky & Backdrop
      if (lightingMode === 'night') {
        const skyGrad = ctx.createLinearGradient(0, 0, 0, height);
        skyGrad.addColorStop(0, '#090d16');
        skyGrad.addColorStop(1, '#05070a');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, width, height);

        // Subtle stars in background
        ctx.fillStyle = '#94a3b8';
        for (let s = 0; s < 25; s++) {
          const sx = (s * 37) % width;
          const sy = (s * 23) % (height * 0.45);
          ctx.fillRect(sx, sy, 1.5, 1.5);
        }
      } else if (lightingMode === 'sunset') {
        const skyGrad = ctx.createLinearGradient(0, 0, 0, height);
        skyGrad.addColorStop(0, '#451a03');
        skyGrad.addColorStop(0.6, '#1e1b4b');
        skyGrad.addColorStop(1, '#0a0a0f');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, width, height);
      } else {
        // Daylight clean dark studio
        ctx.fillStyle = '#0d0d10';
        ctx.fillRect(0, 0, width, height);
      }

      const radYaw = (buildingRotation.yaw * Math.PI) / 180;
      const radPitch = (buildingRotation.pitch * Math.PI) / 180;
      const cosY = Math.cos(radYaw);
      const sinY = Math.sin(radYaw);
      const cosP = Math.cos(radPitch);
      const sinP = Math.sin(radPitch);

      // Scale factor according to building size
      const maxDim = Math.max(
        activeVariant.dimensions.width,
        activeVariant.dimensions.length,
        activeVariant.dimensions.height
      );
      const baseScale = (220 / Math.max(16, maxDim)) * buildingZoom;

      const project = (x: number, y: number, z: number) => {
        const cx = x;
        const cy = y - activeVariant.dimensions.height * 0.4;
        const cz = z;

        // Yaw (around Y axis)
        const rx = cx * cosY - cz * sinY;
        const rz = cx * sinY + cz * cosY;

        // Pitch (around X axis)
        const ry = cy * cosP - rz * sinP;
        const finalZ = cy * sinP + rz * cosP;

        const px = centerX + rx * baseScale;
        const py = centerY - ry * baseScale;
        return { px, py, depth: finalZ };
      };

      // Draw Minecraft Grass / Stone Foundation Grid Baseplate
      const halfW = activeVariant.dimensions.width * 0.65;
      const halfL = activeVariant.dimensions.length * 0.65;
      const gridCorners = [
        project(-halfW, 0, -halfL),
        project(halfW, 0, -halfL),
        project(halfW, 0, halfL),
        project(-halfW, 0, halfL),
      ];

      // Ground plane polygon
      ctx.beginPath();
      ctx.moveTo(gridCorners[0].px, gridCorners[0].py);
      for (let i = 1; i < gridCorners.length; i++) {
        ctx.lineTo(gridCorners[i].px, gridCorners[i].py);
      }
      ctx.closePath();
      ctx.fillStyle = lightingMode === 'night' ? '#111827' : '#1c1917';
      ctx.fill();
      ctx.strokeStyle = lightingMode === 'night' ? '#1f2937' : '#292524';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Collect solid building faces (Solid Minecraft Architecture)
      interface SolidFaceToRender {
        points: { px: number; py: number }[];
        depth: number;
        color: string;
        stroke: string;
        name: string;
        isGlowing?: boolean;
      }

      const facesToRender: SolidFaceToRender[] = [];

      activeVariant.elements.forEach((vol) => {
        const [x1, y1, z1] = vol.from;
        const [x2, y2, z2] = vol.to;

        // 8 Corners of the solid cuboid volume
        const c = [
          project(x1, y1, z1), project(x2, y1, z1), project(x2, y2, z1), project(x1, y2, z1),
          project(x1, y1, z2), project(x2, y1, z2), project(x2, y2, z2), project(x1, y2, z2),
        ];

        // 6 Solid Faces with Minecraft directional lighting factors
        const faceDefs = [
          { name: 'TOP',    idxs: [3, 2, 6, 7], light: 1.05 },
          { name: 'BOTTOM', idxs: [4, 5, 1, 0], light: 0.50 },
          { name: 'SOUTH',  idxs: [5, 4, 7, 6], light: 0.95 },
          { name: 'NORTH',  idxs: [0, 1, 2, 3], light: 0.68 },
          { name: 'EAST',   idxs: [1, 5, 6, 2], light: 0.85 },
          { name: 'WEST',   idxs: [4, 0, 3, 7], light: 0.75 },
        ];

        faceDefs.forEach((f) => {
          const pts = f.idxs.map((i) => c[i]);
          const avgDepth = pts.reduce((acc, p) => acc + p.depth, 0) / 4;

          // Backface culling via 2D cross-product
          const v1x = pts[1].px - pts[0].px;
          const v1y = pts[1].py - pts[0].py;
          const v2x = pts[2].px - pts[0].px;
          const v2y = pts[2].py - pts[0].py;
          const cross = v1x * v2y - v1y * v2x;

          if (cross < 0) {
            // Apply Minecraft Shading & Atmosphere to face color
            let faceColor = vol.color;
            if (vol.isGlowing) {
              faceColor = vol.color; // Keep vibrant for lanterns / beacons
            }

            facesToRender.push({
              points: pts,
              depth: avgDepth,
              color: faceColor,
              stroke: vol.stroke,
              name: vol.name,
              isGlowing: vol.isGlowing,
            });
          }
        });
      });

      // Painter's algorithm: sort back-to-front by depth
      facesToRender.sort((a, b) => a.depth - b.depth);

      // Render solid faces
      facesToRender.forEach((face) => {
        ctx.beginPath();
        ctx.moveTo(face.points[0].px, face.points[0].py);
        for (let i = 1; i < face.points.length; i++) {
          ctx.lineTo(face.points[i].px, face.points[i].py);
        }
        ctx.closePath();

        if (buildingWireframe) {
          ctx.strokeStyle = face.stroke;
          ctx.lineWidth = 1.2;
          ctx.stroke();
        } else {
          // Solid Minecraft fill
          ctx.fillStyle = face.color;
          ctx.fill();

          // Authentic Minecraft Block outline
          ctx.strokeStyle = face.stroke;
          ctx.lineWidth = 0.8;
          ctx.stroke();

          // Lantern & Beacon Night Radiance Glow
          if (face.isGlowing && (lightingMode === 'night' || lightingMode === 'sunset')) {
            ctx.shadowColor = face.color;
            ctx.shadowBlur = 12;
            ctx.fillStyle = face.color;
            ctx.fill();
            ctx.shadowBlur = 0; // reset
          }
        }
      });

      if (buildingAutoRotate) {
        setBuildingRotation((prev) => ({ ...prev, yaw: (prev.yaw + 0.35) % 360 }));
      }

      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animationFrameId);
  }, [
    buildingRotation,
    buildingZoom,
    buildingAutoRotate,
    buildingWireframe,
    lightingMode,
    activeVariant,
    hubTab
  ]);

  // Drag controls for Item Model
  const handleItemMouseDown = (e: React.MouseEvent) => {
    isDraggingItemRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleItemMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingItemRef.current) return;
    const deltaX = e.clientX - lastMousePosRef.current.x;
    const deltaY = e.clientY - lastMousePosRef.current.y;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };

    setRotation((prev) => ({
      yaw: (prev.yaw + deltaX * 0.8) % 360,
      pitch: Math.max(-80, Math.min(80, prev.pitch + deltaY * 0.8)),
    }));
  };

  const handleItemMouseUp = () => {
    isDraggingItemRef.current = false;
  };

  // Drag controls for Solid Building Scene
  const handleBuildingMouseDown = (e: React.MouseEvent) => {
    isDraggingBuildingRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleBuildingMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingBuildingRef.current) return;
    const deltaX = e.clientX - lastMousePosRef.current.x;
    const deltaY = e.clientY - lastMousePosRef.current.y;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };

    setBuildingRotation((prev) => ({
      yaw: (prev.yaw + deltaX * 0.7) % 360,
      pitch: Math.max(-85, Math.min(85, prev.pitch + deltaY * 0.7)),
    }));
  };

  const handleBuildingMouseUp = () => {
    isDraggingBuildingRef.current = false;
  };

  const giveCommand = `/give @p carrot_on_a_stick{CustomModelData:${activeSiegeModel.customModelData},display:{Name:'{"text":"${activeSiegeModel.nameRu}","color":"gold","bold":true}'}} 1`;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-neutral-900 via-neutral-900/95 to-amber-950/40 border border-neutral-800 rounded-2xl p-6 sm:p-8 mb-8 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-medium mb-3">
              <Box className="w-3.5 h-3.5" />
              <span>Цельные 3D Постройки и Модели Minecraft</span>
              <span className="px-1.5 py-0.2 bg-amber-400 text-neutral-950 font-bold rounded text-[10px]">3D</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black text-white tracking-tight flex items-center gap-3">
              <span>Каталог 3D Моделей и Архитектуры</span>
            </h1>
            <p className="text-sm sm:text-base text-neutral-300 mt-2 max-w-2xl leading-relaxed">
              Цельное 3D-отображение построек в стилистике Minecraft (как в игре), множество архитектурных вариантов каждого здания по законам билдинга, а также 3D-орудия Blockbench и руководства топ-мастеров.
            </p>
          </div>

          {/* Hub Tab Switcher */}
          <div className="flex bg-neutral-950 border border-neutral-800 p-1.5 rounded-xl gap-1 shrink-0">
            <button
              onClick={() => setHubTab('buildings')}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                hubTab === 'buildings'
                  ? 'bg-amber-500 text-neutral-950 shadow-md shadow-amber-500/20'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Castle className="w-4 h-4" />
              <span>Цельные Постройки 3D</span>
            </button>

            <button
              onClick={() => setHubTab('models')}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                hubTab === 'models'
                  ? 'bg-amber-500 text-neutral-950 shadow-md shadow-amber-500/20'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Box className="w-4 h-4" />
              <span>3D Орудия Blockbench</span>
            </button>

            <button
              onClick={() => setHubTab('manuals')}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                hubTab === 'manuals'
                  ? 'bg-amber-500 text-neutral-950 shadow-md shadow-amber-500/20'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Мануалы билдеров</span>
            </button>
          </div>
        </div>
      </div>

      {/* ============================================================= */}
      {/* TAB 1: SOLID COMPLETE MINECRAFT BUILDINGS & VARIANTS          */}
      {/* ============================================================= */}
      {hubTab === 'buildings' && (
        <div className="space-y-6">
          {/* Building Selector Strip (All 7 Towny Buildings) */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
            {BUILDING_FAMILIES.map((family) => {
              const isSelected = selectedFamilyId === family.id;
              return (
                <button
                  key={family.id}
                  onClick={() => handleSelectFamily(family.id)}
                  className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                    isSelected
                      ? 'bg-amber-500/15 border-amber-500/60 text-white shadow-lg shadow-amber-500/10'
                      : 'bg-neutral-900/80 border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800/80'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xl">
                      {family.id === 'town_hall' && '🏛️'}
                      {family.id === 'barracks' && '🛡️'}
                      {family.id === 'watchtower' && '🗼'}
                      {family.id === 'city_wall' && '🧱'}
                      {family.id === 'hospital' && '🏥'}
                      {family.id === 'arcane_library' && '🔮'}
                      {family.id === 'sun_pyramid' && '👑'}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-neutral-950/80 text-amber-400 font-semibold">
                      {family.variants.length} стиля
                    </span>
                  </div>
                  <div className="font-bold text-xs sm:text-sm text-white truncate">
                    {family.baseNameRu.split('(')[0]}
                  </div>
                  <div className="text-[10px] text-neutral-500 uppercase tracking-wider mt-0.5">
                    {family.category}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Main 3D Solid Viewer & Variant Selector Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column: Style Variants & Rules Panel */}
            <div className="lg:col-span-5 space-y-4">
              {/* Style Variants Selector Cards */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span>Архитектурные варианты ({activeFamily.variants.length})</span>
                  </h3>
                  <span className="text-xs text-amber-400 font-mono">
                    Выбор стиля
                  </span>
                </div>

                <div className="space-y-2.5">
                  {activeFamily.variants.map((variant) => {
                    const isSelected = selectedVariantId === variant.id;
                    return (
                      <button
                        key={variant.id}
                        onClick={() => setSelectedVariantId(variant.id)}
                        className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-start gap-3 ${
                          isSelected
                            ? 'bg-amber-500/15 border-amber-500/60 text-white shadow-md'
                            : 'bg-neutral-950/60 border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800/60'
                        }`}
                      >
                        <div
                          className={`p-2 rounded-lg shrink-0 ${
                            isSelected ? 'bg-amber-500 text-neutral-950' : 'bg-neutral-800 text-neutral-300'
                          }`}
                        >
                          <Castle className="w-4 h-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="font-bold text-sm text-white flex items-center justify-between">
                            <span className="truncate">{variant.nameRu}</span>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-neutral-900 text-amber-400 border border-neutral-800 shrink-0 ml-2">
                              {variant.styleTag}
                            </span>
                          </div>
                          <p className="text-xs text-neutral-400 mt-1 line-clamp-2 leading-relaxed">
                            {variant.description}
                          </p>
                          <div className="flex items-center gap-3 text-[11px] font-mono text-neutral-500 mt-2">
                            <span>Размер: {variant.dimensions.width}×{variant.dimensions.length}×{variant.dimensions.height}</span>
                            <span>•</span>
                            <span>Блоков: ~{variant.blockCountTotal}</span>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Applied Builder Rules Breakdown for Active Variant */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Hammer className="w-4 h-4 text-cyan-400" />
                    <span>Примененные правила стройки</span>
                  </h3>
                  <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Стандарт Master-Builder
                  </span>
                </div>

                <div className="space-y-3 text-xs">
                  {/* Depth Rule */}
                  <div className="p-3 rounded-xl bg-neutral-950 border border-neutral-800/80">
                    <div className="font-bold text-amber-400 flex items-center gap-1.5 mb-1">
                      <Box className="w-3.5 h-3.5" />
                      <span>1. Правило 3D-Глубины и Выноса</span>
                    </div>
                    <p className="text-neutral-300 text-[11px] leading-relaxed">
                      {activeVariant.appliedRules.depthRule}
                    </p>
                  </div>

                  {/* Gradient Formula */}
                  <div className="p-3 rounded-xl bg-neutral-950 border border-neutral-800/80">
                    <div className="font-bold text-cyan-400 flex items-center gap-1.5 mb-1">
                      <Layers className="w-3.5 h-3.5" />
                      <span>2. Формула Текстурного Градиента</span>
                    </div>
                    <p className="text-neutral-300 text-[11px] leading-relaxed">
                      {activeVariant.appliedRules.gradientFormula}
                    </p>
                  </div>

                  {/* Roof Profile */}
                  <div className="p-3 rounded-xl bg-neutral-950 border border-neutral-800/80">
                    <div className="font-bold text-amber-300 flex items-center gap-1.5 mb-1">
                      <Compass className="w-3.5 h-3.5" />
                      <span>3. Профиль Крыши и Нависание</span>
                    </div>
                    <p className="text-neutral-300 text-[11px] leading-relaxed">
                      {activeVariant.appliedRules.roofProfile}
                    </p>
                  </div>

                  {/* Lighting & Detail */}
                  <div className="p-3 rounded-xl bg-neutral-950 border border-neutral-800/80">
                    <div className="font-bold text-emerald-400 flex items-center gap-1.5 mb-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>4. Освещение и Детализация</span>
                    </div>
                    <p className="text-neutral-300 text-[11px] leading-relaxed">
                      {activeVariant.appliedRules.lightingDetail}
                    </p>
                  </div>
                </div>

                {/* Palette Percentage Breakdown */}
                <div className="pt-3 border-t border-neutral-800">
                  <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                    <span>Палитра материалов постройки:</span>
                    <span className="text-[10px] font-mono text-neutral-500">100% блоки Майнкрафт</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {activeVariant.palette.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-2 rounded-lg bg-neutral-950 border border-neutral-800 flex items-center gap-2 text-xs"
                      >
                        <div
                          className="w-3.5 h-3.5 rounded shrink-0 shadow-sm"
                          style={{ backgroundColor: item.hex }}
                        />
                        <div className="min-w-0 flex-1">
                          <div className="text-[11px] text-neutral-200 truncate">{item.name}</div>
                          <div className="text-[10px] font-mono text-amber-400 font-semibold">
                            {item.percentage}% объема
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* In-game build command */}
                <div className="pt-2">
                  <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                    <span>Команда возведения этого стиля</span>
                    {copiedText === 'buildCmd' ? (
                      <span className="text-emerald-400 text-[10px] flex items-center gap-1 font-mono">
                        <Check className="w-3 h-3" /> Скопировано!
                      </span>
                    ) : null}
                  </div>
                  <div className="flex items-center gap-2 bg-neutral-950 border border-neutral-800 rounded-xl p-2.5">
                    <code className="text-xs font-mono text-amber-300 truncate flex-1 select-all">
                      {activeVariant.buildCommand}
                    </code>
                    <button
                      onClick={() => copyToClipboard(activeVariant.buildCommand, 'buildCmd')}
                      className="p-1.5 hover:bg-neutral-800 rounded-lg text-neutral-400 hover:text-white transition-colors shrink-0"
                      title="Скопировать"
                    >
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Solid 3D Minecraft Viewer */}
            <div className="lg:col-span-7 flex flex-col space-y-4">
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 flex-1 flex flex-col">
                {/* 3D Scene Controls Toolbar */}
                <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-neutral-800">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Цельная 3D Архитектура Minecraft
                    </span>
                    <span className="text-xs text-neutral-500 hidden sm:inline">
                      · Вращение ЛКМ в 360°
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {/* Lighting Atmosphere Toggle (Day / Sunset / Night) */}
                    <div className="flex bg-neutral-950 border border-neutral-800 rounded-lg p-0.5">
                      <button
                        onClick={() => setLightingMode('day')}
                        className={`p-1.5 rounded transition-colors ${
                          lightingMode === 'day' ? 'bg-amber-500/20 text-amber-300' : 'text-neutral-500 hover:text-white'
                        }`}
                        title="День"
                      >
                        <Sun className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setLightingMode('sunset')}
                        className={`p-1.5 rounded transition-colors ${
                          lightingMode === 'sunset' ? 'bg-orange-500/20 text-orange-300' : 'text-neutral-500 hover:text-white'
                        }`}
                        title="Закат"
                      >
                        <Sunset className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setLightingMode('night')}
                        className={`p-1.5 rounded transition-colors ${
                          lightingMode === 'night' ? 'bg-cyan-500/20 text-cyan-300' : 'text-neutral-500 hover:text-white'
                        }`}
                        title="Ночь (Светящиеся фонари)"
                      >
                        <Moon className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <button
                      onClick={() => setBuildingAutoRotate(!buildingAutoRotate)}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
                        buildingAutoRotate
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-neutral-800 text-neutral-400'
                      }`}
                    >
                      <RotateCw className="w-3.5 h-3.5" />
                      <span>{buildingAutoRotate ? 'Вращение ВКЛ' : 'Вращение ВЫКЛ'}</span>
                    </button>

                    <button
                      onClick={() => setBuildingWireframe(!buildingWireframe)}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
                        buildingWireframe
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                          : 'bg-neutral-800 text-neutral-400'
                      }`}
                    >
                      <Layers className="w-3.5 h-3.5" />
                      <span>Каркас</span>
                    </button>

                    {/* Zoom */}
                    <div className="flex items-center bg-neutral-950 border border-neutral-800 rounded-lg p-0.5">
                      <button
                        onClick={() => setBuildingZoom((z) => Math.max(0.6, z - 0.15))}
                        className="p-1.5 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white transition-colors"
                        title="Уменьшить"
                      >
                        <ZoomOut className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-[11px] font-mono px-1.5 text-neutral-400">
                        {Math.round(buildingZoom * 100)}%
                      </span>
                      <button
                        onClick={() => setBuildingZoom((z) => Math.min(2.2, z + 0.15))}
                        className="p-1.5 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white transition-colors"
                        title="Увеличить"
                      >
                        <ZoomIn className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <button
                      onClick={() => {
                        setBuildingRotation({ yaw: 42, pitch: 26 });
                        setBuildingZoom(1.0);
                      }}
                      className="p-1.5 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-neutral-400 hover:text-white transition-colors"
                      title="Сбросить ракурс"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* 3D Canvas Screen */}
                <div
                  className="relative flex-1 min-h-[480px] bg-neutral-950 rounded-xl overflow-hidden border border-neutral-800/80 cursor-grab active:cursor-grabbing flex items-center justify-center select-none"
                  onMouseDown={handleBuildingMouseDown}
                  onMouseMove={handleBuildingMouseMove}
                  onMouseUp={handleBuildingMouseUp}
                  onMouseLeave={handleBuildingMouseUp}
                >
                  <canvas
                    ref={buildingCanvasRef}
                    width={760}
                    height={520}
                    className="w-full h-full object-contain"
                  />

                  {/* Overlay Badges */}
                  <div className="absolute bottom-3 left-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] font-mono text-neutral-400 flex items-center gap-3">
                    <span>Yaw: {Math.round(buildingRotation.yaw)}°</span>
                    <span>Pitch: {Math.round(buildingRotation.pitch)}°</span>
                    <span>Зум: {buildingZoom.toFixed(1)}x</span>
                  </div>

                  <div className="absolute top-3 left-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-3 py-1.5 text-xs text-white font-bold flex items-center gap-2">
                    <Castle className="w-3.5 h-3.5 text-amber-400" />
                    <span>{activeVariant.nameRu}</span>
                  </div>

                  <div className="absolute top-3 right-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] font-mono text-amber-400 flex items-center gap-1.5">
                    <span>{activeVariant.elements.length} архитектурных объемов</span>
                  </div>
                </div>

                {/* Building Volume Elements Breakdown */}
                <div className="mt-4 pt-4 border-t border-neutral-800">
                  <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                    <span>Составные части Minecraft архитектуры:</span>
                    <span className="text-[11px] font-mono text-neutral-500">
                      Габариты: {activeVariant.dimensions.width}x{activeVariant.dimensions.length}x{activeVariant.dimensions.height} блоков
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                    {activeVariant.elements.map((el, idx) => (
                      <div
                        key={idx}
                        className="bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs flex items-center gap-2"
                      >
                        <div
                          className="w-3 h-3 rounded shadow-sm shrink-0"
                          style={{ backgroundColor: el.color }}
                        />
                        <div className="min-w-0 flex-1">
                          <div className="text-[11px] font-medium text-neutral-200 truncate">{el.name}</div>
                          <div className="text-[9px] font-mono text-neutral-500 truncate">{el.materialName}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================= */}
      {/* TAB 2: 3D SIEGE WEAPONS & BLOCKBENCH MODELS                   */}
      {/* ============================================================= */}
      {hubTab === 'models' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left: Model Selector & Info */}
          <div className="lg:col-span-4 space-y-4">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider text-neutral-400 mb-3 flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-amber-400" />
                <span>Выбор модели орудия</span>
              </h3>
              <div className="space-y-2">
                {SIEGE_MODELS.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => setSelectedModelId(model.id)}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex items-start gap-3 ${
                      selectedModelId === model.id
                        ? 'bg-amber-500/10 border-amber-500/40 text-white shadow-sm'
                        : 'bg-neutral-950/60 border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800'
                    }`}
                  >
                    <div
                      className={`p-2 rounded-lg shrink-0 ${
                        selectedModelId === model.id ? 'bg-amber-500 text-neutral-950' : 'bg-neutral-800 text-neutral-400'
                      }`}
                    >
                      <Box className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-bold text-sm text-white truncate flex items-center justify-between">
                        <span>{model.nameRu}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-neutral-800 text-amber-400">
                          CMD {model.customModelData}
                        </span>
                      </div>
                      <div className="text-xs text-neutral-400 mt-0.5">{model.category}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Model Card Details */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Info className="w-4 h-4 text-cyan-400" />
                <span>Характеристики модели</span>
              </h3>
              <p className="text-xs text-neutral-300 leading-relaxed">
                {activeSiegeModel.description}
              </p>

              <div className="space-y-2 text-xs font-mono pt-2 border-t border-neutral-800">
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-500">CustomModelData:</span>
                  <span className="text-amber-400 font-bold">{activeSiegeModel.customModelData}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-500">Полигонов/Кубов:</span>
                  <span className="text-white">{activeSiegeModel.elements.length} элементов</span>
                </div>
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-500">Базовый предмет:</span>
                  <span className="text-cyan-400">carrot_on_a_stick</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-neutral-500">Формат файла:</span>
                  <span className="text-emerald-400">Blockbench JSON / .bbmodel</span>
                </div>
              </div>

              {/* In-game command */}
              <div className="pt-2">
                <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>Команда выдачи в игре</span>
                  {copiedText === 'cmd' ? (
                    <span className="text-emerald-400 text-[10px] flex items-center gap-1">
                      <Check className="w-3 h-3" /> Скопировано!
                    </span>
                  ) : null}
                </div>
                <div className="flex items-center gap-2 bg-neutral-950 border border-neutral-800 rounded-xl p-2.5">
                  <code className="text-[11px] font-mono text-amber-300 truncate flex-1 select-all">
                    {giveCommand}
                  </code>
                  <button
                    onClick={() => copyToClipboard(giveCommand, 'cmd')}
                    className="p-1.5 hover:bg-neutral-800 rounded-lg text-neutral-400 hover:text-white transition-colors shrink-0"
                    title="Скопировать команду"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Direct Downloads */}
              <div className="pt-2 space-y-2">
                <button
                  onClick={() => downloadCannonBbmodel()}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer shadow-md shadow-amber-500/20"
                >
                  <Download className="w-4 h-4" />
                  <span>Скачать проект .bbmodel (Blockbench)</span>
                </button>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => downloadCannonJson()}
                    className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium transition-colors border border-neutral-700 cursor-pointer"
                  >
                    <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                    <span>cannon.json</span>
                  </button>
                  <button
                    onClick={() => downloadCannonRp()}
                    className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium transition-colors border border-neutral-700 cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5 text-amber-400" />
                    <span>RP Пак .zip</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right: 3D Interactive Canvas & Controls */}
          <div className="lg:col-span-8 flex flex-col space-y-4">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 flex-1 flex flex-col">
              {/* Canvas Toolbar */}
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-neutral-800">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Интерактивная 3D Сцена
                  </span>
                  <span className="text-xs text-neutral-500 hidden sm:inline">
                    · Зажмите ЛКМ для вращения
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setAutoRotate(!autoRotate)}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
                      autoRotate
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-neutral-800 text-neutral-400'
                    }`}
                  >
                    <RotateCw className="w-3.5 h-3.5" />
                    <span>{autoRotate ? 'Авто-вращение ВКЛ' : 'Вращение ВЫКЛ'}</span>
                  </button>

                  <button
                    onClick={() => setWireframe(!wireframe)}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
                      wireframe
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        : 'bg-neutral-800 text-neutral-400'
                    }`}
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Каркас (Wireframe)</span>
                  </button>

                  <div className="flex items-center bg-neutral-950 border border-neutral-800 rounded-lg p-0.5">
                    <button
                      onClick={() => setZoom((z) => Math.max(0.6, z - 0.2))}
                      className="p-1.5 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white transition-colors"
                      title="Уменьшить"
                    >
                      <ZoomOut className="w-3.5 h-3.5" />
                    </button>
                    <span className="text-[11px] font-mono px-1.5 text-neutral-400">
                      {Math.round(zoom * 100)}%
                    </span>
                    <button
                      onClick={() => setZoom((z) => Math.min(2.4, z + 0.2))}
                      className="p-1.5 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white transition-colors"
                      title="Увеличить"
                    >
                      <ZoomIn className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* 3D Canvas Element */}
              <div
                className="relative flex-1 min-h-[420px] bg-neutral-950 rounded-xl overflow-hidden border border-neutral-800/80 cursor-grab active:cursor-grabbing flex items-center justify-center select-none"
                onMouseDown={handleItemMouseDown}
                onMouseMove={handleItemMouseMove}
                onMouseUp={handleItemMouseUp}
                onMouseLeave={handleItemMouseUp}
              >
                <canvas
                  ref={canvasRef}
                  width={720}
                  height={460}
                  className="w-full h-full object-contain"
                />

                <div className="absolute bottom-3 left-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] font-mono text-neutral-400 flex items-center gap-3">
                  <span>Yaw: {Math.round(rotation.yaw)}°</span>
                  <span>Pitch: {Math.round(rotation.pitch)}°</span>
                  <span>Zoom: {zoom.toFixed(1)}x</span>
                </div>

                <div className="absolute top-3 right-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] text-amber-400 font-semibold flex items-center gap-1.5">
                  <Palette className="w-3.5 h-3.5" />
                  <span>Текстуры: Wood & Metal</span>
                </div>
              </div>

              {/* Model Element Tree Inspector */}
              <div className="mt-4 pt-4 border-t border-neutral-800">
                <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Анатомия элементов 3D модели ({activeSiegeModel.elements.length} блоков)</span>
                  <span className="text-[11px] font-mono text-neutral-500">Координаты в пространстве Blockbench [0..16]</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  {activeSiegeModel.elements.map((el, i) => (
                    <div
                      key={i}
                      className="bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs flex items-center gap-2"
                    >
                      <div className="w-3 h-3 rounded" style={{ backgroundColor: el.color }} />
                      <div className="min-w-0 flex-1">
                        <div className="text-[11px] font-medium text-neutral-300 truncate">{el.name}</div>
                        <div className="text-[9px] font-mono text-neutral-500 truncate">
                          [{el.from.join(',')}] → [{el.to.join(',')}]
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================= */}
      {/* TAB 3: ARCHITECTURE MANUALS & BUILDER GUIDES                   */}
      {/* ============================================================= */}
      {hubTab === 'manuals' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {ARCHITECTURE_MANUALS.map((manual, idx) => (
              <div
                key={idx}
                className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 flex flex-col justify-between hover:border-amber-500/40 transition-all shadow-lg"
              >
                <div>
                  <div className="flex items-center justify-between text-xs mb-3">
                    <span className="px-2 py-0.5 rounded bg-neutral-800 text-amber-400 font-mono font-medium">
                      {manual.category}
                    </span>
                    <span className="text-neutral-500 font-mono">{manual.readTime}</span>
                  </div>

                  <h3 className="text-lg font-bold text-white mb-2 leading-snug">
                    {manual.title}
                  </h3>
                  <p className="text-xs text-amber-400/80 mb-3 font-medium">
                    {manual.subtitle}
                  </p>
                  <p className="text-xs text-neutral-300 leading-relaxed mb-4">
                    {manual.summary}
                  </p>

                  {/* Pro Tips */}
                  <div className="space-y-2 mb-4 pt-3 border-t border-neutral-800">
                    <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">
                      Ключевые приемы мастеров:
                    </div>
                    {manual.proTips.map((tip, tIdx) => (
                      <div key={tIdx} className="text-xs text-neutral-300 flex items-start gap-2">
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>

                  {/* Palette Preview */}
                  <div className="pt-3 border-t border-neutral-800">
                    <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-2">
                      Рекомендуемая палитра блоков:
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {manual.palette.map((pal, pIdx) => (
                        <div
                          key={pIdx}
                          className="flex items-center gap-1.5 px-2 py-1 rounded bg-neutral-950 border border-neutral-800 text-[11px]"
                          title={pal.role}
                        >
                          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: pal.hex }} />
                          <span className="text-neutral-300">{pal.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-neutral-800 flex items-center justify-between text-xs">
                  <span className="text-neutral-500">Сложность: {manual.difficulty}</span>
                  <span className="text-amber-400 font-bold flex items-center gap-1">
                    Гайд внедрен в схемы Towny <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Golden Rules Summary Card */}
          <div className="bg-gradient-to-r from-amber-950/30 via-neutral-900 to-neutral-900 border border-amber-500/30 rounded-2xl p-6 sm:p-8">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <span>Золотые правила строительства красивых городов Towny</span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-neutral-950/80 border border-neutral-800">
                <div className="text-amber-400 font-bold mb-1">1. Не делайте плоских стен</div>
                <div className="text-neutral-300 leading-relaxed">
                  Всегда углубляйте окна на 1 блок назад или выносите опорные балки наружу. Тень создает 80% красоты постройки.
                </div>
              </div>
              <div className="p-4 rounded-xl bg-neutral-950/80 border border-neutral-800">
                <div className="text-amber-400 font-bold mb-1">2. Смешивайте текстуры</div>
                <div className="text-neutral-300 leading-relaxed">
                  Не стройте стены из одного камня. Разбавляйте 70% каменных кирпичей 20% потрескавшимися и 10% андезитом.
                </div>
              </div>
              <div className="p-4 rounded-xl bg-neutral-950/80 border border-neutral-800">
                <div className="text-amber-400 font-bold mb-1">3. Нависание крыш (Eaves)</div>
                <div className="text-neutral-300 leading-relaxed">
                  Крыша должна свисать минимум на 1 блок за пределы стенки и иметь перевернутые ступени под свесом.
                </div>
              </div>
              <div className="p-4 rounded-xl bg-neutral-950/80 border border-neutral-800">
                <div className="text-amber-400 font-bold mb-1">4. Скрытый и теплый свет</div>
                <div className="text-neutral-300 leading-relaxed">
                  Откажитесь от беспорядочных факелов на полу. Вешайте фонари на цепи или прячьте светокамень под полублоки.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open('src/components/ModelPreviewHub.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ModelPreviewHub.tsx written successfully!")
