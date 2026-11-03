import os

content = '''import React, { useState, useEffect, useRef } from 'react';
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
  Info
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
import { INITIAL_BLUEPRINTS } from '../data/defaultBuildings';
import { BuildingBlueprint } from '../types';

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
  const [hubTab, setHubTab] = useState<'models' | 'buildings' | 'manuals'>('models');

  // Item Models State
  const [selectedModelId, setSelectedModelId] = useState<string>('cannon');
  const [modelType, setModelType] = useState<'vanilla' | 'custom'>('custom');
  const [wireframe, setWireframe] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [rotation, setRotation] = useState<{ yaw: number; pitch: number }>({ yaw: 35, pitch: 22 });
  const [zoom, setZoom] = useState<number>(1.1);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  // Buildings State
  const [selectedBuildingId, setSelectedBuildingId] = useState<string>('town_hall');
  const [currentLayer, setCurrentLayer] = useState<number>(4);
  const [isAnimatingBuild, setIsAnimatingBuild] = useState<boolean>(false);
  const [buildingRotation, setBuildingRotation] = useState<number>(45);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const buildingCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDraggingRef = useRef<boolean>(false);
  const lastMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const activeSiegeModel = SIEGE_MODELS.find((m) => m.id === selectedModelId) || SIEGE_MODELS[0];
  const activeBlueprint = INITIAL_BLUEPRINTS.find((b) => b.id === selectedBuildingId) || INITIAL_BLUEPRINTS[0];

  // Helper copy function
  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2500);
  };

  // 3D Canvas Renderer for Item Models
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
          project(x1, y1, z2), project(x2, y1, z2), project(x2, y2, z2), project(x1, y2, z2),
        ];

        const faceIndices = [
          { name: 'north', idxs: [0, 1, 2, 3], light: 0.85 },
          { name: 'south', idxs: [5, 4, 7, 6], light: 0.95 },
          { name: 'up',    idxs: [3, 2, 6, 7], light: 1.15 },
          { name: 'down',  idxs: [4, 5, 1, 0], light: 0.65 },
          { name: 'west',  idxs: [4, 0, 3, 7], light: 0.80 },
          { name: 'east',  idxs: [1, 5, 6, 2], light: 1.00 },
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

  // Building Isometric Visualizer
  useEffect(() => {
    if (hubTab !== 'buildings') return;
    const canvas = buildingCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2 + 60;

    const rad = (buildingRotation * Math.PI) / 180;
    const cosA = Math.cos(rad);
    const sinA = Math.sin(rad);

    const bWidth = Math.min(activeBlueprint.size.width, 16);
    const bLength = Math.min(activeBlueprint.size.length, 16);
    const maxHeight = Math.min(activeBlueprint.size.height, 12);
    const visibleLayers = Math.min(currentLayer, maxHeight);

    const projectVoxel = (bx: number, by: number, bz: number) => {
      const cx = bx - bWidth / 2;
      const cz = bz - bLength / 2;
      const rx = cx * cosA - cz * sinA;
      const rz = cx * sinA + cz * cosA;
      const scale = 14;
      const isoX = rx * scale * 1.4;
      const isoY = (rz * 0.7 - by * 1.1) * scale;
      return { px: centerX + isoX, py: centerY + isoY, depth: rz };
    };

    // Draw footprint base plane
    ctx.strokeStyle = '#333333';
    ctx.fillStyle = '#171717';
    ctx.beginPath();
    const c1 = projectVoxel(0, 0, 0);
    const c2 = projectVoxel(bWidth, 0, 0);
    const c3 = projectVoxel(bWidth, 0, bLength);
    const c4 = projectVoxel(0, 0, bLength);
    ctx.moveTo(c1.px, c1.py);
    ctx.lineTo(c2.px, c2.py);
    ctx.lineTo(c3.px, c3.py);
    ctx.lineTo(c4.px, c4.py);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Render layers
    for (let y = 0; y <= visibleLayers; y++) {
      const isTopCurrentLayer = y === visibleLayers;
      const layerRatio = y / maxHeight;

      // Color scheme based on height & materials
      let baseColor = '#64748b'; // stone bricks default
      let topColor = '#94a3b8';
      let sideColor = '#475569';

      if (y === 0) {
        baseColor = '#334155'; // foundation
        topColor = '#475569';
        sideColor = '#1e293b';
      } else if (y > maxHeight * 0.6) {
        baseColor = '#78350f'; // wood roof
        topColor = '#92400e';
        sideColor = '#451a03';
      }

      // Draw perimeter wall blocks for layer
      for (let x = 0; x < bWidth; x += 2) {
        for (let z = 0; z < bLength; z += 2) {
          const isPerimeter = x === 0 || x >= bWidth - 2 || z === 0 || z >= bLength - 2;
          const isCorner = (x === 0 || x >= bWidth - 2) && (z === 0 || z >= bLength - 2);

          if (isPerimeter || y === 0 || (isTopCurrentLayer && y === maxHeight)) {
            const p = projectVoxel(x, y, z);
            const size = 12;

            // Draw pseudo 3D isometric block
            ctx.fillStyle = isCorner ? '#d97706' : topColor;
            ctx.beginPath();
            ctx.moveTo(p.px, p.py - size);
            ctx.lineTo(p.px + size, p.py - size / 2);
            ctx.lineTo(p.px, p.py);
            ctx.lineTo(p.px - size, p.py - size / 2);
            ctx.closePath();
            ctx.fill();

            // Right side
            ctx.fillStyle = sideColor;
            ctx.beginPath();
            ctx.moveTo(p.px, p.py);
            ctx.lineTo(p.px + size, p.py - size / 2);
            ctx.lineTo(p.px + size, p.py + size / 2);
            ctx.lineTo(p.px, p.py + size);
            ctx.closePath();
            ctx.fill();

            // Left side
            ctx.fillStyle = baseColor;
            ctx.beginPath();
            ctx.moveTo(p.px, p.py);
            ctx.lineTo(p.px - size, p.py - size / 2);
            ctx.lineTo(p.px - size, p.py + size / 2);
            ctx.lineTo(p.px, p.py + size);
            ctx.closePath();
            ctx.fill();

            ctx.strokeStyle = 'rgba(0,0,0,0.4)';
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
    }
  }, [hubTab, selectedBuildingId, currentLayer, buildingRotation, activeBlueprint]);

  // Handle Build Animation
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isAnimatingBuild) {
      interval = setInterval(() => {
        setCurrentLayer((prev) => {
          const max = Math.min(activeBlueprint.size.height, 12);
          if (prev >= max) {
            setIsAnimatingBuild(false);
            return max;
          }
          return prev + 1;
        });
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isAnimatingBuild, activeBlueprint]);

  // Drag controls for 3D model
  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - lastMousePosRef.current.x;
    const deltaY = e.clientY - lastMousePosRef.current.y;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };

    setRotation((prev) => ({
      yaw: (prev.yaw + deltaX * 0.8) % 360,
      pitch: Math.max(-80, Math.min(80, prev.pitch + deltaY * 0.8)),
    }));
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const giveCommand = `/give @p carrot_on_a_stick{CustomModelData:${activeSiegeModel.customModelData},display:{Name:'{"text":"${activeSiegeModel.nameRu}","color":"gold","bold":true}'}} 1`;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-neutral-900 via-neutral-900/90 to-amber-950/40 border border-neutral-800 rounded-2xl p-6 sm:p-8 mb-8 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-medium mb-3">
              <Box className="w-3.5 h-3.5" />
              <span>Blockbench 3D & Towny Architecture Suite</span>
              <span className="px-1.5 py-0.2 bg-amber-400 text-neutral-950 font-bold rounded text-[10px]">3D</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black text-white tracking-tight flex items-center gap-3">
              <span>Предпросмотр моделей и Архитектура</span>
            </h1>
            <p className="text-sm sm:text-base text-neutral-300 mt-2 max-w-2xl leading-relaxed">
              Интерактивный 3D-просмотрщик предметов Blockbench (осадные орудия, пушки, осадная техника) и послойный каталог архитектурных чертежей Towny с гайдами по строительству от топ-билдеров.
            </p>
          </div>

          {/* Hub Tab Switcher */}
          <div className="flex bg-neutral-950 border border-neutral-800 p-1.5 rounded-xl gap-1 shrink-0">
            <button
              onClick={() => setHubTab('models')}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                hubTab === 'models'
                  ? 'bg-amber-500 text-neutral-950 shadow-md shadow-amber-500/20'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Box className="w-4 h-4" />
              <span>3D Орудия</span>
            </button>

            <button
              onClick={() => setHubTab('buildings')}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                hubTab === 'buildings'
                  ? 'bg-amber-500 text-neutral-950 shadow-md shadow-amber-500/20'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Castle className="w-4 h-4" />
              <span>Постройки Towny</span>
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

      {/* TAB 1: 3D ITEM & SIEGE MODELS */}
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
                    <div className={`p-2 rounded-lg shrink-0 ${selectedModelId === model.id ? 'bg-amber-500 text-neutral-950' : 'bg-neutral-800 text-neutral-400'}`}>
                      <Box className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-bold text-sm text-white truncate flex items-center justify-between">
                        <span>{model.nameRu}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-neutral-800 text-amber-400">CMD {model.customModelData}</span>
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
                      autoRotate ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-neutral-800 text-neutral-400'
                    }`}
                  >
                    <RotateCw className="w-3.5 h-3.5" />
                    <span>{autoRotate ? 'Авто-вращение ВКЛ' : 'Вращение ВЫКЛ'}</span>
                  </button>

                  <button
                    onClick={() => setWireframe(!wireframe)}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
                      wireframe ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'bg-neutral-800 text-neutral-400'
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
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
              >
                <canvas
                  ref={canvasRef}
                  width={720}
                  height={460}
                  className="w-full h-full object-contain"
                />

                {/* Canvas Overlay Labels */}
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

      {/* TAB 2: TOWNY BUILDINGS & SCHEMATICS */}
      {hubTab === 'buildings' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left: Building Selection & Stats */}
          <div className="lg:col-span-4 space-y-4">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider text-neutral-400 mb-3 flex items-center gap-2">
                <Castle className="w-4 h-4 text-amber-400" />
                <span>Здания в плагине Towny</span>
              </h3>
              <div className="space-y-2">
                {INITIAL_BLUEPRINTS.map((b) => (
                  <button
                    key={b.id}
                    onClick={() => {
                      setSelectedBuildingId(b.id);
                      setCurrentLayer(Math.min(b.size.height, 6));
                    }}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex items-start gap-3 ${
                      selectedBuildingId === b.id
                        ? 'bg-amber-500/10 border-amber-500/40 text-white shadow-sm'
                        : 'bg-neutral-950/60 border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800'
                    }`}
                  >
                    <div className="w-8 h-8 rounded-lg bg-neutral-800 flex items-center justify-center text-base shrink-0">
                      {b.category === 'military' ? '🛡️' : b.category === 'wonder' ? '👑' : '🏛️'}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-bold text-sm text-white truncate flex items-center justify-between">
                        <span>{b.nameRu}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-neutral-800 text-amber-400">
                          {b.size.width}x{b.size.length}x{b.size.height}
                        </span>
                      </div>
                      <div className="text-xs text-neutral-400 mt-0.5 truncate">{b.lore || b.description}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Building Info Card */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-cyan-400" />
                  <span>Параметры постройки</span>
                </h3>
                {activeBlueprint.isWorldWonder && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    Чудо Света
                  </span>
                )}
              </div>

              <p className="text-xs text-neutral-300 leading-relaxed">
                {activeBlueprint.description}
              </p>

              {/* Buffs */}
              <div className="space-y-2 pt-2 border-t border-neutral-800">
                <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">
                  Предоставляемые баффы городу:
                </div>
                {activeBlueprint.buffs.map((buff) => (
                  <div key={buff.id} className="p-2.5 rounded-xl bg-neutral-950 border border-neutral-800/80 text-xs">
                    <div className="font-semibold text-amber-300 flex items-center justify-between">
                      <span>{buff.unit}</span>
                      <span className="text-neutral-500 font-mono text-[10px]">+{buff.value}</span>
                    </div>
                    <div className="text-neutral-400 text-[11px] mt-0.5">{buff.descriptionRu}</div>
                  </div>
                ))}
              </div>

              {/* Resource Checklist */}
              <div className="space-y-2 pt-2 border-t border-neutral-800">
                <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider flex items-center justify-between">
                  <span>Необходимые ресурсы</span>
                  <span className="text-neutral-500 text-[10px] font-mono">
                    Всего: {activeBlueprint.resources.reduce((acc, r) => acc + r.count, 0)} блоков
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-1.5">
                  {activeBlueprint.resources.map((res, i) => (
                    <div key={i} className="flex items-center gap-2 p-1.5 rounded-lg bg-neutral-950 border border-neutral-800 text-xs">
                      <span>{res.icon}</span>
                      <div className="min-w-0 flex-1">
                        <div className="text-[11px] text-neutral-300 truncate">{res.nameRu}</div>
                        <div className="text-[10px] font-mono text-amber-400 font-bold">{res.count} шт.</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* In-game build command */}
              <div className="pt-2">
                <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>Команда строительства</span>
                  {copiedText === 'buildCmd' ? (
                    <span className="text-emerald-400 text-[10px] flex items-center gap-1">
                      <Check className="w-3 h-3" /> Скопировано!
                    </span>
                  ) : null}
                </div>
                <div className="flex items-center gap-2 bg-neutral-950 border border-neutral-800 rounded-xl p-2.5">
                  <code className="text-xs font-mono text-amber-300 truncate flex-1 select-all">
                    /townybuild build {activeBlueprint.id}
                  </code>
                  <button
                    onClick={() => copyToClipboard(`/townybuild build ${activeBlueprint.id}`, 'buildCmd')}
                    className="p-1.5 hover:bg-neutral-800 rounded-lg text-neutral-400 hover:text-white transition-colors shrink-0"
                    title="Скопировать"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Isometric Voxel Layer Visualizer */}
          <div className="lg:col-span-8 flex flex-col space-y-4">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 flex-1 flex flex-col">
              {/* Layer Controls */}
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-neutral-800">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Послойный чертеж (Слой {currentLayer} из {activeBlueprint.size.height})
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setIsAnimatingBuild(!isAnimatingBuild)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                      isAnimatingBuild
                        ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {isAnimatingBuild ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                    <span>{isAnimatingBuild ? 'Пауза анимации' : 'Анимация стройки'}</span>
                  </button>

                  <button
                    onClick={() => setBuildingRotation((r) => (r + 45) % 360)}
                    className="p-1.5 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-neutral-300 text-xs flex items-center gap-1 transition-colors"
                    title="Повернуть на 45°"
                  >
                    <RotateCw className="w-3.5 h-3.5" />
                    <span className="text-[11px] font-mono">{buildingRotation}°</span>
                  </button>

                  <button
                    onClick={() => setCurrentLayer(0)}
                    className="p-1.5 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-neutral-400 hover:text-white transition-colors"
                    title="Сбросить на фундамент"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Interactive Layer Slider */}
              <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 mb-4 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-400">
                    Слой 0 (Фундамент / Цоколь)
                  </span>
                  <span className="font-bold text-amber-400 font-mono">
                    Высота Y: +{currentLayer} блоков
                  </span>
                  <span className="text-neutral-400">
                    Слой {activeBlueprint.size.height} (Крыша)
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={activeBlueprint.size.height}
                  value={currentLayer}
                  onChange={(e) => setCurrentLayer(parseInt(e.target.value, 10))}
                  className="w-full accent-amber-500 h-2 bg-neutral-800 rounded-lg cursor-pointer"
                />
              </div>

              {/* Isometric Canvas */}
              <div className="relative flex-1 min-h-[400px] bg-neutral-950 rounded-xl overflow-hidden border border-neutral-800/80 flex items-center justify-center">
                <canvas
                  ref={buildingCanvasRef}
                  width={720}
                  height={440}
                  className="w-full h-full object-contain"
                />

                <div className="absolute bottom-3 left-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] font-mono text-neutral-400 flex items-center gap-3">
                  <span>Габариты: {activeBlueprint.size.width}×{activeBlueprint.size.length}</span>
                  <span>Чанки: {activeBlueprint.chunkFootprint.widthChunks}×{activeBlueprint.chunkFootprint.lengthChunks}</span>
                  <span>Уровень города: Lvl {activeBlueprint.requiredBuildingLevel}</span>
                </div>

                <div className="absolute top-3 right-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] text-cyan-400 font-medium">
                  Изометрическая проекция 3D
                </div>
              </div>

              {/* Building Master Builder Breakdown */}
              <div className="mt-4 pt-4 border-t border-neutral-800">
                <h4 className="text-xs font-bold text-neutral-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Архитектурные приемы этой постройки:</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="bg-neutral-950 border border-neutral-800 p-3 rounded-xl">
                    <div className="font-bold text-amber-300 mb-1">1. Выносной каркас</div>
                    <div className="text-neutral-400 text-[11px] leading-relaxed">
                      Угловые столбы выдвинуты наружу на 1 блок, придавая зданию ощущение прочности и защищенности.
                    </div>
                  </div>
                  <div className="bg-neutral-950 border border-neutral-800 p-3 rounded-xl">
                    <div className="font-bold text-amber-300 mb-1">2. Градиент материалов</div>
                    <div className="text-neutral-400 text-[11px] leading-relaxed">
                      Тяжелый глубинный сланец в основании переходит в каменные кирпичи и деревянные стропила.
                    </div>
                  </div>
                  <div className="bg-neutral-950 border border-neutral-800 p-3 rounded-xl">
                    <div className="font-bold text-amber-300 mb-1">3. Нависающая кровля</div>
                    <div className="text-neutral-400 text-[11px] leading-relaxed">
                      Скат крыши выступает за пределы стен на 1 блок с перевернутыми ступенями для объема.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: ARCHITECTURE MANUALS & BUILDER GUIDES */}
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
    f.write(content)

print("ModelPreviewHub.tsx successfully written!")
