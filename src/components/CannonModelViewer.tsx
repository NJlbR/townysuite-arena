import React, { useState, useEffect, useRef } from 'react';
import { Box, Download, Copy, Check, Eye, RotateCw, ZoomIn, ZoomOut, Layers, Sparkles, Terminal, Code2, ShieldAlert, Cpu, Image, HelpCircle, Palette } from 'lucide-react';
import { CANNON_MODEL_JSON, CANNON_VANILLA_MODEL_JSON, CANNON_CUSTOM_MODEL_JSON, CANNON_MODEL_JSON_STR, CANNON_VANILLA_JSON_STR, CANNON_CUSTOM_JSON_STR, CANNON_BBMODEL_JSON_STR, CANNON_METADATA } from '../data/cannonModelData';
import { downloadCannonBbmodel, downloadCannonJson, downloadCannonVanillaJson, downloadCannonCustomJson, downloadCannonWoodPng, downloadCannonMetalPng, downloadCannonRp } from '../utils/downloadHelpers';

export const CannonModelViewer: React.FC = () => {
  const [modelType, setModelType] = useState<'vanilla' | 'custom'>('custom');
  const [wireframe, setWireframe] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [rotation, setRotation] = useState({ yaw: 35, pitch: 22 });
  const [zoom, setZoom] = useState(1.1);
  const [copiedJson, setCopiedJson] = useState(false);
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDraggingRef = useRef(false);
  const lastMousePosRef = useRef({ x: 0, y: 0 });

  const currentModel = modelType === 'vanilla' ? CANNON_VANILLA_MODEL_JSON : CANNON_CUSTOM_MODEL_JSON;
  const currentJsonStr = modelType === 'vanilla' ? CANNON_VANILLA_JSON_STR : CANNON_CUSTOM_JSON_STR;

  // 3D Canvas Renderer
  useEffect(() => {
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
      const centerY = height / 2 + 10;

      // Draw subtle grid base plate (16x16 block outline)
      ctx.strokeStyle = '#262626';
      ctx.lineWidth = 1;
      
      const radYaw = (rotation.yaw * Math.PI) / 180;
      const radPitch = (rotation.pitch * Math.PI) / 180;
      const cosY = Math.cos(radYaw);
      const sinY = Math.sin(radYaw);
      const cosP = Math.cos(radPitch);
      const sinP = Math.sin(radPitch);

      const project = (x: number, y: number, z: number) => {
        // Shift origin to center of block [8, 0, 8] (since Y is -8..+8)
        const cx = x - 8;
        const cy = y;
        const cz = z - 8;

        // Yaw rotation (Y axis)
        const rx = cx * cosY - cz * sinY;
        const rz = cx * sinY + cz * cosY;

        // Pitch rotation (X axis)
        const ry = cy * cosP - rz * sinP;
        const finalZ = cy * sinP + rz * cosP;

        // Isometric / Weak perspective projection
        const scale = 16 * zoom;
        const px = centerX + rx * scale;
        const py = centerY - ry * scale;

        return { px, py, depth: finalZ };
      };

      // Draw ground grid plane (at Y = -8 ground level)
      ctx.beginPath();
      for (let g = 0; g <= 16; g += 4) {
        const p1 = project(g, -8, 0);
        const p2 = project(g, -8, 16);
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);

        const p3 = project(0, -8, g);
        const p4 = project(16, -8, g);
        ctx.moveTo(p3.px, p3.py);
        ctx.lineTo(p4.px, p4.py);
      }
      ctx.stroke();

      // Helper to check if a face of an element is exposed (not touching another element)
      const isFaceExposed = (
        elIndex: number,
        dir: 'TOP' | 'BOTTOM' | 'SOUTH' | 'NORTH' | 'EAST' | 'WEST'
      ): boolean => {
        const elA = currentModel.elements[elIndex];
        const [x1A, y1A, z1A] = elA.from;
        const [x2A, y2A, z2A] = elA.to;
        const eps = 0.05;

        for (let j = 0; j < currentModel.elements.length; j++) {
          if (j === elIndex) continue;
          const elB = currentModel.elements[j];
          const [x1B, y1B, z1B] = elB.from;
          const [x2B, y2B, z2B] = elB.to;

          if (dir === 'TOP') {
            if (Math.abs(y1B - y2A) < eps && x1B <= x1A + eps && x2B >= x2A - eps && z1B <= z1A + eps && z2B >= z2A - eps) return false;
          } else if (dir === 'BOTTOM') {
            if (Math.abs(y2B - y1A) < eps && x1B <= x1A + eps && x2B >= x2A - eps && z1B <= z1A + eps && z2B >= z2A - eps) return false;
          } else if (dir === 'EAST') {
            if (Math.abs(x1B - x2A) < eps && y1B <= y1A + eps && y2B >= y2A - eps && z1B <= z1A + eps && z2B >= z2A - eps) return false;
          } else if (dir === 'WEST') {
            if (Math.abs(x2B - x1A) < eps && y1B <= y1A + eps && y2B >= y2A - eps && z1B <= z1A + eps && z2B >= z2A - eps) return false;
          } else if (dir === 'SOUTH') {
            if (Math.abs(z1B - z2A) < eps && x1B <= x1A + eps && x2B >= x2A - eps && y1B <= y1A + eps && y2B >= y2A - eps) return false;
          } else if (dir === 'NORTH') {
            if (Math.abs(z2B - z1A) < eps && x1B <= x1A + eps && x2B >= x2A - eps && y1B <= y1A + eps && y2B >= y2A - eps) return false;
          }
        }
        return true;
      };

      // Collect and sort faces by depth (Painter's algorithm)
      interface FaceToRender {
        points: { px: number; py: number }[];
        depth: number;
        color: string;
        stroke: string;
        name: string;
        isExposed: boolean;
      }

      const facesToRender: FaceToRender[] = [];

      currentModel.elements.forEach((el, elIdx) => {
        let [x1, y1, z1] = el.from;
        let [x2, y2, z2] = el.to;

        // 2 clean textures:
        // Wood (carriage, cheeks, wedge) -> warm Dark Oak Planks
        // Metal (all other parts: barrel, spade, axle, wheels) -> forged iron / anvil
        const isWood = el.name.includes('carriage') || el.name.includes('wedge');
        const baseColor = isWood ? '#5c3920' : '#3c3f46';
        const strokeColor = isWood ? '#301c0e' : '#1d1f23';

        // 8 cube corners
        const corners = [
          [x1, y1, z1],
          [x2, y1, z1],
          [x2, y2, z1],
          [x1, y2, z1],
          [x1, y1, z2],
          [x2, y1, z2],
          [x2, y2, z2],
          [x1, y2, z2],
        ];

        const pCorners = corners.map((c) => project(c[0], c[1], c[2]));

        // 6 Cube Faces (South, North, East, West, Up, Down)
        const faces: { idxs: number[]; shade: number; dir: 'SOUTH' | 'NORTH' | 'EAST' | 'WEST' | 'TOP' | 'BOTTOM' }[] = [
          { idxs: [4, 5, 6, 7], shade: 0.9, dir: 'SOUTH' }, // South
          { idxs: [1, 0, 3, 2], shade: 0.7, dir: 'NORTH' }, // North
          { idxs: [5, 1, 2, 6], shade: 0.8, dir: 'EAST' }, // East
          { idxs: [0, 4, 7, 3], shade: 0.75, dir: 'WEST' }, // West
          { idxs: [3, 2, 6, 7], shade: 1.15, dir: 'TOP' }, // Up (Highlight)
          { idxs: [0, 1, 5, 4], shade: 0.5, dir: 'BOTTOM' }, // Down (Shadow)
        ];

        faces.forEach((f) => {
          const pts = f.idxs.map((idx) => pCorners[idx]);
          const avgDepth = pts.reduce((sum, p) => sum + p.depth, 0) / 4;

          let faceColor = baseColor;
          if (wireframe) {
            faceColor = 'rgba(234, 179, 8, 0.08)';
          }

          const exposed = isFaceExposed(elIdx, f.dir);

          facesToRender.push({
            points: pts,
            depth: avgDepth,
            color: faceColor,
            stroke: wireframe ? '#eab308' : strokeColor,
            name: el.name,
            isExposed: exposed,
          });
        });
      });

      // Sort back-to-front
      facesToRender.sort((a, b) => a.depth - b.depth);

      // Draw all faces
      facesToRender.forEach((face) => {
        ctx.beginPath();
        ctx.moveTo(face.points[0].px, face.points[0].py);
        for (let i = 1; i < face.points.length; i++) {
          ctx.lineTo(face.points[i].px, face.points[i].py);
        }
        ctx.closePath();

        ctx.fillStyle = face.color;
        ctx.fill();

        // Draw contours ONLY for open external faces (hidden internal faces do NOT draw stroke)
        if (face.isExposed) {
          ctx.strokeStyle = face.stroke;
          ctx.lineWidth = wireframe ? 1.5 : 0.9;
          ctx.stroke();
        }
      });

      if (autoRotate) {
        setRotation((prev) => ({
          yaw: (prev.yaw + 0.5) % 360,
          pitch: prev.pitch,
        }));
      }
    };

    render();
  }, [rotation, zoom, wireframe, autoRotate, currentModel]);

  // Mouse drag handlers for 3D rotation
  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
    setAutoRotate(false);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - lastMousePosRef.current.x;
    const deltaY = e.clientY - lastMousePosRef.current.y;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };

    setRotation((prev) => ({
      yaw: (prev.yaw + deltaX * 0.8) % 360,
      pitch: Math.max(-60, Math.min(60, prev.pitch - deltaY * 0.8)),
    }));
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(currentJsonStr);
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  const handleCopyCommand = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCommand(id);
    setTimeout(() => setCopiedCommand(null), 2000);
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Top Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            3D Blockbench / Minecraft 1.20 - 1.21+ (2-Texture Architecture)
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <span>{CANNON_METADATA.name}</span>
            <span className="text-xs px-2.5 py-1 rounded bg-neutral-800 text-neutral-300 font-mono border border-neutral-700">
              16×16×16 Box
            </span>
          </h2>
          <p className="text-neutral-400 text-sm mt-1">
            Массивная осадная мортира, занимающая <strong className="text-amber-300">весь блок в высоту (16×16×16, Y=0..16)</strong> без провисания сущностей наездника (крипера/игрока). Построена на 2 текстурах: <strong className="text-amber-300 font-mono">#wood</strong> и <strong className="text-neutral-300 font-mono">#metal</strong>.
          </p>
        </div>

        {/* Action Downloads */}
        <div className="flex flex-wrap items-center gap-2">
          {/* 1. BBMODEL for Blockbench (with embedded textures) */}
          <button
            onClick={() => downloadCannonBbmodel()}
            className="inline-flex items-center gap-2 px-3.5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-neutral-950 font-bold rounded-xl text-xs shadow-md shadow-amber-500/20 transition-all cursor-pointer"
            title="Открыть в Blockbench СО ВСЕМИ ЦВЕТАМИ (.bbmodel с 2 вшитыми текстурами)"
          >
            <Download className="w-4 h-4" />
            <span>Скачать .bbmodel (С цветами)</span>
          </button>

          {/* 2. Minecraft Model JSON */}
          <button
            onClick={() => (modelType === 'vanilla' ? downloadCannonVanillaJson() : downloadCannonCustomJson())}
            className="inline-flex items-center gap-2 px-3.5 py-2.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-white font-medium rounded-xl text-xs transition-colors cursor-pointer"
            title="Скачать файл модели cannon_tnt.json"
          >
            <Code2 className="w-4 h-4 text-amber-400" />
            <span>Скачать .json ({modelType === 'vanilla' ? 'Ваниль' : 'Кастом'})</span>
          </button>

          {/* 3. Wood Texture PNG */}
          <button
            onClick={() => downloadCannonWoodPng()}
            className="inline-flex items-center gap-2 px-3 py-2.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-amber-300 font-medium rounded-xl text-xs transition-colors cursor-pointer"
            title="Скачать текстуру дерева cannon_wood.png (16x16)"
          >
            <Image className="w-4 h-4 text-amber-400" />
            <span>Дерево .png</span>
          </button>

          {/* 4. Metal Texture PNG */}
          <button
            onClick={() => downloadCannonMetalPng()}
            className="inline-flex items-center gap-2 px-3 py-2.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-300 font-medium rounded-xl text-xs transition-colors cursor-pointer"
            title="Скачать текстуру металла cannon_metal.png (16x16)"
          >
            <Image className="w-4 h-4 text-neutral-400" />
            <span>Металл .png</span>
          </button>

          {/* 5. Complete Resource Pack */}
          <button
            onClick={() => downloadCannonRp()}
            className="inline-flex items-center gap-2 px-3.5 py-2.5 bg-purple-600/80 hover:bg-purple-600 text-white font-semibold rounded-xl text-xs transition-colors cursor-pointer"
            title="Скачать готовый ресурспак .ZIP (Меню + Пушка)"
          >
            <Box className="w-4 h-4 text-purple-300" />
            <span>Ресурспак (.ZIP)</span>
          </button>
        </div>
      </div>

      {/* 2-Texture Architecture Notice Card */}
      <div className="bg-amber-950/30 border border-amber-500/40 rounded-2xl p-4 sm:p-5 mb-6 text-xs text-neutral-300 space-y-2.5">
        <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
          <Palette className="w-4 h-4 shrink-0" />
          <span>Архитектура модели упрощена до 2 надёжных текстур:</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          <div className="p-3 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-2">
            <span className="font-semibold text-amber-300 block">🪵 Текстура 1: #wood (Лафет и станина)</span>
            <p className="text-neutral-400">
              Отвечает за деревянную раму пушки, боковые щековины и регулировочный клин. Использует стандартную ванильную текстуру <code className="text-amber-300 bg-neutral-900 px-1 py-0.5 rounded">minecraft:block/dark_oak_planks</code> (или <code className="text-neutral-300">cannon_wood.png</code>).
            </p>
          </div>

          <div className="p-3 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-2">
            <span className="font-semibold text-neutral-200 block">⚙️ Текстура 2: #metal (Ствол, колёса и фурнитура)</span>
            <p className="text-neutral-400">
              Отвечает за чугунный ствол, кольца усиления, цапфы, колёса и сошник. Использует текстуру кованого железа наковальни <code className="text-amber-300 bg-neutral-900 px-1 py-0.5 rounded">minecraft:block/anvil</code> (или <code className="text-neutral-300">cannon_metal.png</code>).
            </p>
          </div>
        </div>
        <div className="pt-2 text-[11px] text-emerald-400 font-medium">
          ✅ <strong>Почему это гарантированно работает:</strong> Ванильные текстуры блоков всегда присутствуют в клиенте Minecraft, поэтому модель никогда не пропадет из-за сбоя атласа или отсутствия PNG. А в файле <strong>.bbmodel</strong> обе текстуры вшиты внутрь для Blockbench!
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        {/* 3D Interactive Canvas Viewer (8 cols) */}
        <div className="lg:col-span-8 bg-neutral-900/90 border border-neutral-800 rounded-2xl p-4 flex flex-col relative overflow-hidden shadow-xl">
          {/* Controls Overlay */}
          <div className="flex flex-wrap items-center justify-between gap-2 z-10 mb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-neutral-400 bg-neutral-950/80 px-2.5 py-1 rounded border border-neutral-800">
                Кубов: {currentModel.elements.length} | 2 Текстуры (#wood, #metal)
              </span>

              {/* Model Variant Switcher */}
              <div className="inline-flex rounded-lg bg-neutral-950 p-0.5 border border-neutral-800">
                <button
                  onClick={() => setModelType('vanilla')}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-colors cursor-pointer ${
                    modelType === 'vanilla' ? 'bg-amber-500 text-neutral-950 font-bold' : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  Ваниль (Dark Oak + Anvil)
                </button>
                <button
                  onClick={() => setModelType('custom')}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-colors cursor-pointer ${
                    modelType === 'custom' ? 'bg-amber-500 text-neutral-950 font-bold' : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  Кастомные PNG (16×16)
                </button>
              </div>
            </div>

            <div className="flex items-center gap-1.5 bg-neutral-950/90 p-1 rounded-xl border border-neutral-800">
              <button
                onClick={() => setAutoRotate(!autoRotate)}
                className={`p-1.5 rounded-lg text-xs transition-colors cursor-pointer ${
                  autoRotate ? 'bg-amber-500 text-neutral-950 font-bold' : 'text-neutral-400 hover:text-white'
                }`}
                title="Авто-вращение"
              >
                <RotateCw className="w-4 h-4" />
              </button>

              <button
                onClick={() => setWireframe(!wireframe)}
                className={`p-1.5 rounded-lg text-xs transition-colors cursor-pointer ${
                  wireframe ? 'bg-amber-500 text-neutral-950 font-bold' : 'text-neutral-400 hover:text-white'
                }`}
                title="Сетка полигонов (Wireframe)"
              >
                <Layers className="w-4 h-4" />
              </button>

              <button
                onClick={() => setZoom((z) => Math.min(2.0, z + 0.15))}
                className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors cursor-pointer"
                title="Приблизить"
              >
                <ZoomIn className="w-4 h-4" />
              </button>

              <button
                onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
                className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors cursor-pointer"
                title="Отдалить"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Interactive Canvas */}
          <div className="flex-1 flex items-center justify-center relative min-h-[420px] bg-gradient-to-b from-neutral-950/80 via-neutral-950 to-neutral-950/90 rounded-xl cursor-grab active:cursor-grabbing border border-neutral-800/80 select-none">
            <canvas
              ref={canvasRef}
              width={700}
              height={440}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              className="max-w-full h-auto"
            />
            <div className="absolute bottom-3 left-4 text-[11px] text-neutral-500 pointer-events-none font-mono">
              Вращение: Зажмите ЛКМ и двигайте мышь
            </div>
          </div>

          {/* Color legend footer */}
          <div className="flex flex-wrap items-center justify-between gap-3 mt-3 pt-3 border-t border-neutral-800/80 text-xs">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm bg-[#5c3920] border border-[#301c0e]"></span>
                <span className="text-neutral-300 font-medium">#wood (Лафет / Тёмный Дуб)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm bg-[#3c3f46] border border-[#1d1f23]"></span>
                <span className="text-neutral-300 font-medium">#metal (Ствол и Колёса / Наковальня)</span>
              </div>
            </div>

            <div className="text-[11px] text-neutral-400 font-mono">
              CustomModelData: <span className="text-amber-400 font-bold">7001</span> | 0..16 UV
            </div>
          </div>
        </div>

        {/* Side Details & Elements Inspector (4 cols) */}
        <div className="lg:col-span-4 bg-neutral-900/90 border border-neutral-800 rounded-2xl p-5 flex flex-col h-[520px]">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Box className="w-4 h-4 text-amber-400" />
              Элементы модели ({currentModel.elements.length})
            </span>
            <span className="text-xs text-neutral-500 font-mono">16×16×16</span>
          </h3>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1 text-xs">
            {currentModel.elements.map((el, i) => {
              const isWood = el.name.includes('carriage') || el.name.includes('wedge');
              return (
                <div key={i} className="p-2.5 rounded-lg bg-neutral-950 border border-neutral-800/80 hover:border-neutral-700 transition-colors">
                  <div className="font-mono font-bold flex items-center justify-between">
                    <span className={isWood ? 'text-amber-400' : 'text-slate-300'}>{el.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${isWood ? 'bg-amber-950 text-amber-300' : 'bg-neutral-800 text-neutral-300'}`}>
                      {isWood ? '#wood' : '#metal'}
                    </span>
                  </div>
                  <div className="text-[11px] text-neutral-400 mt-1 font-mono grid grid-cols-2 gap-1">
                    <div>From: [{el.from.join(', ')}]</div>
                    <div>To: [{el.to.join(', ')}]</div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-4 pt-3 border-t border-neutral-800 space-y-2">
            <button
              onClick={handleCopyJson}
              className="w-full py-2.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-colors cursor-pointer"
            >
              {copiedJson ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copiedJson ? 'JSON скопирован!' : `Копировать JSON (${modelType})`}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Integration & Usage Commands */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-amber-400" />
          <span>Настройка в SiegeCannon и проверка в игре Minecraft</span>
        </h3>

        <div className="space-y-4">
          <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800">
            <div className="text-xs font-bold text-amber-300 mb-2">1. Конфиг плагина SiegeCannons (config.yml):</div>
            <pre className="font-mono text-xs text-neutral-300 overflow-x-auto whitespace-pre">
cannon:
  model:
    use-custom: true
            </pre>
            <div className="text-[11px] text-neutral-400 mt-2">
              При <code className="text-amber-300">use-custom: true</code> плагин ищет модель по пути <code className="text-amber-300">assets/siegecannon/models/item/cannon_tnt.json</code> в ресурспаке.
            </div>
          </div>

          <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-amber-300">2. Выдача предмета с моделью пушки игроку:</span>
              <button
                onClick={() => handleCopyCommand('/give @p carrot_on_a_stick{CustomModelData:7001,display:{Name:\'{"text":"Осадная Пушка","color":"gold","bold":true}\'}} 1', 'give')}
                className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 cursor-pointer"
              >
                {copiedCommand === 'give' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedCommand === 'give' ? 'Скопировано' : 'Копия'}</span>
              </button>
            </div>
            <pre className="font-mono text-xs text-neutral-300 overflow-x-auto whitespace-pre">
              /give @p carrot_on_a_stick&#123;CustomModelData:7001,display:&#123;Name:'&#123;"text":"Осадная Пушка","color":"gold","bold":true&#125;'&#125;&#125; 1
            </pre>
          </div>

          <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-amber-300">3. Размещение пушки как Item Display (1.20+ без модов):</span>
              <button
                onClick={() => handleCopyCommand('/summon item_display ~ ~ ~ {item:{id:"minecraft:carrot_on_a_stick",Count:1b,tag:{CustomModelData:7001}},transformation:[1.0f,0.0f,0.0f,0.0f,0.0f,1.0f,0.0f,0.0f,0.0f,0.0f,1.0f,0.0f,0.0f,0.0f,0.0f,1.0f]}', 'display')}
                className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 cursor-pointer"
              >
                {copiedCommand === 'display' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedCommand === 'display' ? 'Скопировано' : 'Копия'}</span>
              </button>
            </div>
            <pre className="font-mono text-xs text-neutral-300 overflow-x-auto whitespace-pre">
              /summon item_display ~ ~ ~ &#123;item:&#123;id:"minecraft:carrot_on_a_stick",Count:1b,tag:&#123;CustomModelData:7001&#125;&#125;,transformation:[1.0f,0.0f,0.0f,0.0f,0.0f,1.0f,0.0f,0.0f,0.0f,0.0f,1.0f,0.0f,0.0f,0.0f,0.0f,1.0f]&#125;
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
