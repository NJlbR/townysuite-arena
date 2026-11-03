import React, { useState, useEffect, useRef } from 'react';
import {
  Layers,
  Sparkles,
  Eye,
  Box,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Info,
  Shield,
  Wind
} from 'lucide-react';

type CellState = 'hologram' | 'foreign' | 'air';

export const LayerEdgeDivisionVisualizer: React.FC = () => {
  // 8x8 block grid for the layer slice
  const [grid, setGrid] = useState<CellState[][]>(() => {
    const initial: CellState[][] = Array(8).fill(null).map(() => Array(8).fill('air'));
    // Outer blueprint perimeter ring (required walls)
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        if (r === 0 || r === 7 || c === 0 || c === 7) {
          initial[r][c] = 'hologram';
        }
      }
    }
    // Foreign obstacle blocks on the edge contacting air and adjacent to holograms
    initial[0][3] = 'foreign';
    initial[0][4] = 'foreign';
    initial[3][0] = 'foreign';
    return initial;
  });

  const [airContactOnly, setAirContactOnly] = useState<boolean>(true);
  const [showObstacleGlow, setShowObstacleGlow] = useState<boolean>(true);
  const [showHologramGlow, setShowHologramGlow] = useState<boolean>(true);
  const [showInternalSeams, setShowInternalSeams] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'iso3d' | 'flat2d'>('iso3d');
  const [activeBrush, setActiveBrush] = useState<'foreign' | 'hologram' | 'air'>('foreign');

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Helper to toggle a cell when clicked
  const handleCellClick = (r: number, c: number) => {
    setGrid((prev) => {
      const copy = prev.map((row) => [...row]);
      const current = copy[r][c];
      if (current === activeBrush) {
        copy[r][c] = 'air';
      } else {
        copy[r][c] = activeBrush;
      }
      return copy;
    });
  };

  // Preset: Place cluster of foreign blocks in the wall
  const handlePresetForeignCluster = () => {
    setGrid((prev) => {
      const copy = prev.map((row) => [...row]);
      copy[0][2] = 'foreign';
      copy[0][3] = 'foreign';
      copy[0][4] = 'foreign';
      copy[2][7] = 'foreign';
      copy[3][7] = 'foreign';
      copy[7][3] = 'foreign';
      copy[7][4] = 'foreign';
      return copy;
    });
  };

  // Preset: Clear all foreign blocks back to pure blueprint holograms
  const handlePresetPureHolograms = () => {
    setGrid((prev) => {
      const copy = prev.map((row) => [...row]);
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          if (copy[r][c] === 'foreign') {
            copy[r][c] = 'hologram';
          }
        }
      }
      return copy;
    });
  };

  // Preset: Solid internal block (demonstrates depth vs air contact)
  const handlePresetInteriorMass = () => {
    setGrid(() => {
      const fresh: CellState[][] = Array(8).fill(null).map(() => Array(8).fill('air'));
      for (let r = 1; r <= 6; r++) {
        for (let c = 1; c <= 6; c++) {
          fresh[r][c] = 'hologram';
        }
      }
      // Foreign block core in the deep interior
      fresh[3][3] = 'foreign';
      fresh[3][4] = 'foreign';
      fresh[4][3] = 'foreign';
      fresh[4][4] = 'foreign';
      return fresh;
    });
  };

  // -----------------------------------------------------------------
  // Canvas Renderer for Air-Contact Edge Highlighting (0 Particles!)
  // -----------------------------------------------------------------
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const W = canvas.width;
    const H = canvas.height;
    const centerX = W / 2;
    const centerY = H / 2 - 10;

    // Dark grid background
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, W, H);

    if (viewMode === 'iso3d') {
      // 3D Isometric Projection Settings
      const tileWidth = 38;
      const tileHeight = 22;
      const blockHeightY = 24;

      const project = (r: number, c: number, hY = 0) => {
        const x = (c - r) * (tileWidth / 2);
        const y = (c + r) * (tileHeight / 2) - hY * blockHeightY;
        return {
          px: centerX + x,
          py: centerY - 60 + y,
        };
      };

      // Draw ground base grid plate
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      for (let r = 0; r <= 8; r++) {
        const p1 = project(r, 0, 0);
        const p2 = project(r, 8, 0);
        ctx.beginPath();
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);
        ctx.stroke();
      }
      for (let c = 0; c <= 8; c++) {
        const p1 = project(0, c, 0);
        const p2 = project(8, c, 0);
        ctx.beginPath();
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);
        ctx.stroke();
      }

      // 1. Draw solid block cubes back-to-front
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          const type = grid[r][c];
          if (type === 'air') continue;

          const topCorners = [
            project(r, c, 1),
            project(r, c + 1, 1),
            project(r + 1, c + 1, 1),
            project(r + 1, c, 1),
          ];

          const botCorners = [
            project(r, c, 0),
            project(r, c + 1, 0),
            project(r + 1, c + 1, 0),
            project(r + 1, c, 0),
          ];

          // Face colors based on block type
          let topColor = type === 'hologram' ? 'rgba(0, 180, 255, 0.40)' : 'rgba(225, 29, 72, 0.60)';
          let leftColor = type === 'hologram' ? 'rgba(0, 140, 210, 0.30)' : 'rgba(190, 18, 60, 0.50)';
          let rightColor = type === 'hologram' ? 'rgba(0, 200, 255, 0.50)' : 'rgba(244, 63, 94, 0.70)';

          // Left face (Front-left, South-West)
          ctx.beginPath();
          ctx.moveTo(topCorners[3].px, topCorners[3].py);
          ctx.lineTo(topCorners[2].px, topCorners[2].py);
          ctx.lineTo(botCorners[2].px, botCorners[2].py);
          ctx.lineTo(botCorners[3].px, botCorners[3].py);
          ctx.closePath();
          ctx.fillStyle = leftColor;
          ctx.fill();

          // Right face (Front-right, South-East)
          ctx.beginPath();
          ctx.moveTo(topCorners[1].px, topCorners[1].py);
          ctx.lineTo(topCorners[2].px, topCorners[2].py);
          ctx.lineTo(botCorners[2].px, botCorners[2].py);
          ctx.lineTo(botCorners[1].px, botCorners[1].py);
          ctx.closePath();
          ctx.fillStyle = rightColor;
          ctx.fill();

          // Top face (contacts air from above!)
          ctx.beginPath();
          ctx.moveTo(topCorners[0].px, topCorners[0].py);
          for (let i = 1; i < 4; i++) {
            ctx.lineTo(topCorners[i].px, topCorners[i].py);
          }
          ctx.closePath();
          ctx.fillStyle = topColor;
          ctx.fill();

          // Subtle base block wireframe
          ctx.strokeStyle = type === 'hologram' ? 'rgba(0, 220, 255, 0.25)' : 'rgba(255, 100, 120, 0.3)';
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      // -------------------------------------------------------------
      // 2. HIGHLIGHT EDGES STRICTLY ON CONTACT WITH AIR (PLAYER VISIBLE)
      // -------------------------------------------------------------
      ctx.save();

      interface EdgeHighlight {
        p1: { px: number; py: number };
        p2: { px: number; py: number };
        color: string;
        isAirContact: boolean;
        isObstacle: boolean;
        isFrontFacing: boolean;
      }

      const edgesToDraw: EdgeHighlight[] = [];

      // Check horizontal edges (along C axis between row r and r)
      for (let r = 0; r <= 8; r++) {
        for (let c = 0; c < 8; c++) {
          const above: CellState = r > 0 ? grid[r - 1][c] : 'air';
          const below: CellState = r < 8 ? grid[r][c] : 'air';

          const hasAir = above === 'air' || below === 'air';
          const bothSolid = above !== 'air' && below !== 'air';

          // Skip if both are air
          if (above === 'air' && below === 'air') continue;

          const isFront = r >= 3 || c >= 3;

          // Case A: Exposed edge on contact with air
          if (hasAir) {
            const solidCell = above !== 'air' ? above : below;
            const isObs = solidCell === 'foreign';
            const color = isObs ? '#ff1e40' : '#00f0ff';

            if ((isObs && showObstacleGlow) || (!isObs && showHologramGlow)) {
              // Top edge on contact with air (hY = 1)
              edgesToDraw.push({
                p1: project(r, c, 1),
                p2: project(r, c + 1, 1),
                color,
                isAirContact: true,
                isObstacle: isObs,
                isFrontFacing: isFront,
              });

              // Bottom edge on contact with air (ground level hY = 0)
              edgesToDraw.push({
                p1: project(r, c, 0),
                p2: project(r, c + 1, 0),
                color,
                isAirContact: true,
                isObstacle: isObs,
                isFrontFacing: isFront,
              });
            }
          } else if (bothSolid) {
            // Case B: Seam in the depth of the layer (between two solid blocks)
            const isTransition = above !== below;
            // In 3D, the top surface seam (hY = 1) contacts air from above!
            if (isTransition && ((above === 'foreign' || below === 'foreign') && showObstacleGlow)) {
              edgesToDraw.push({
                p1: project(r, c, 1),
                p2: project(r, c + 1, 1),
                color: '#ff1e40', // Highlight boundary where obstacle meets blueprint at air surface
                isAirContact: true,
                isObstacle: true,
                isFrontFacing: isFront,
              });
            }

            // Internal seam in depth (hY = 0 or interior vertical face without air contact)
            if (!airContactOnly && showInternalSeams) {
              edgesToDraw.push({
                p1: project(r, c, 0),
                p2: project(r, c + 1, 0),
                color: isTransition ? 'rgba(255, 60, 90, 0.4)' : 'rgba(0, 200, 255, 0.25)',
                isAirContact: false,
                isObstacle: isTransition,
                isFrontFacing: isFront,
              });
            }
          }
        }
      }

      // Check vertical edges (along R axis between col c and c)
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c <= 8; c++) {
          const left: CellState = c > 0 ? grid[r][c - 1] : 'air';
          const right: CellState = c < 8 ? grid[r][c] : 'air';

          const hasAir = left === 'air' || right === 'air';
          const bothSolid = left !== 'air' && right !== 'air';

          if (left === 'air' && right === 'air') continue;

          const isFront = r >= 3 || c >= 3;

          // Case A: Exposed edge on contact with air
          if (hasAir) {
            const solidCell = left !== 'air' ? left : right;
            const isObs = solidCell === 'foreign';
            const color = isObs ? '#ff1e40' : '#00f0ff';

            if ((isObs && showObstacleGlow) || (!isObs && showHologramGlow)) {
              // Top edge at hY = 1
              edgesToDraw.push({
                p1: project(r, c, 1),
                p2: project(r + 1, c, 1),
                color,
                isAirContact: true,
                isObstacle: isObs,
                isFrontFacing: isFront,
              });

              // Bottom edge at hY = 0
              edgesToDraw.push({
                p1: project(r, c, 0),
                p2: project(r + 1, c, 0),
                color,
                isAirContact: true,
                isObstacle: isObs,
                isFrontFacing: isFront,
              });
            }
          } else if (bothSolid) {
            // Case B: Seam in depth of layer
            const isTransition = left !== right;
            if (isTransition && ((left === 'foreign' || right === 'foreign') && showObstacleGlow)) {
              edgesToDraw.push({
                p1: project(r, c, 1),
                p2: project(r + 1, c, 1),
                color: '#ff1e40',
                isAirContact: true,
                isObstacle: true,
                isFrontFacing: isFront,
              });
            }

            if (!airContactOnly && showInternalSeams) {
              edgesToDraw.push({
                p1: project(r, c, 0),
                p2: project(r + 1, c, 0),
                color: isTransition ? 'rgba(255, 60, 90, 0.4)' : 'rgba(0, 200, 255, 0.25)',
                isAirContact: false,
                isObstacle: isTransition,
                isFrontFacing: isFront,
              });
            }
          }
        }
      }

      // Check vertical corner pillars (from hY = 0 to hY = 1) on contact with air
      for (let r = 0; r <= 8; r++) {
        for (let c = 0; c <= 8; c++) {
          // 4 quadrants meeting at vertex (r, c)
          const qNW = (r > 0 && c > 0) ? grid[r - 1][c - 1] : 'air';
          const qNE = (r > 0 && c < 8) ? grid[r - 1][c] : 'air';
          const qSW = (r < 8 && c > 0) ? grid[r][c - 1] : 'air';
          const qSE = (r < 8 && c < 8) ? grid[r][c] : 'air';

          const hasAir = qNW === 'air' || qNE === 'air' || qSW === 'air' || qSE === 'air';
          const hasSolid = qNW !== 'air' || qNE !== 'air' || qSW !== 'air' || qSE !== 'air';

          if (!hasSolid) continue;

          // Only draw pillar edge if it contacts AIR (visible on outside corner or cavity)
          if (hasAir) {
            const hasObs = qNW === 'foreign' || qNE === 'foreign' || qSW === 'foreign' || qSE === 'foreign';
            const color = hasObs ? '#ff1e40' : '#00f0ff';
            const isFront = r >= 3 || c >= 3;

            if ((hasObs && showObstacleGlow) || (!hasObs && showHologramGlow)) {
              edgesToDraw.push({
                p1: project(r, c, 0),
                p2: project(r, c, 1),
                color,
                isAirContact: true,
                isObstacle: hasObs,
                isFrontFacing: isFront,
              });
            }
          }
        }
      }

      // Render glowing vector strokes
      edgesToDraw.forEach((edge) => {
        if (!edge.isAirContact && airContactOnly) return; // Strict air-contact rule!

        ctx.strokeStyle = edge.color;
        ctx.lineWidth = edge.isObstacle ? 3.2 : 2.5;

        if (edge.isAirContact) {
          ctx.shadowColor = edge.color;
          ctx.shadowBlur = edge.isObstacle ? 14 : 10;
        } else {
          ctx.shadowBlur = 0;
          ctx.setLineDash([4, 4]);
        }

        ctx.beginPath();
        ctx.moveTo(edge.p1.px, edge.p1.py);
        ctx.lineTo(edge.p2.px, edge.p2.py);
        ctx.stroke();
        ctx.setLineDash([]);
      });

      ctx.restore();
    } else {
      // -------------------------------------------------------------
      // 2D Orthographic Flat Grid View
      // -------------------------------------------------------------
      const padding = 50;
      const cellSize = Math.min((W - padding * 2) / 8, (H - padding * 2) / 8);
      const startX = (W - cellSize * 8) / 2;
      const startY = (H - cellSize * 8) / 2;

      // Draw cells
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          const type = grid[r][c];
          const x = startX + c * cellSize;
          const y = startY + r * cellSize;

          ctx.strokeStyle = '#1e293b';
          ctx.lineWidth = 1;
          ctx.strokeRect(x, y, cellSize, cellSize);

          if (type === 'hologram') {
            ctx.fillStyle = 'rgba(0, 180, 255, 0.25)';
            ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
            ctx.fillStyle = '#38bdf8';
            ctx.font = '10px monospace';
            ctx.fillText('ГОЛОГР', x + 4, y + cellSize / 2 + 3);
          } else if (type === 'foreign') {
            ctx.fillStyle = 'rgba(225, 29, 72, 0.35)';
            ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
            ctx.fillStyle = '#f43f5e';
            ctx.font = '10px monospace';
            ctx.fillText('ПРЕПЯТ', x + 4, y + cellSize / 2 + 3);
          }
        }
      }

      ctx.save();

      // 2D Horizontal edges on contact with air
      for (let r = 0; r <= 8; r++) {
        for (let c = 0; c < 8; c++) {
          const above: CellState = r > 0 ? grid[r - 1][c] : 'air';
          const below: CellState = r < 8 ? grid[r][c] : 'air';

          const hasAir = above === 'air' || below === 'air';
          const bothSolid = above !== 'air' && below !== 'air';

          if (above === 'air' && below === 'air') continue;

          const x1 = startX + c * cellSize;
          const x2 = startX + (c + 1) * cellSize;
          const y = startY + r * cellSize;

          if (hasAir) {
            const solidCell = above !== 'air' ? above : below;
            const isObs = solidCell === 'foreign';
            const color = isObs ? '#ff1e40' : '#00f0ff';

            if ((isObs && showObstacleGlow) || (!isObs && showHologramGlow)) {
              ctx.strokeStyle = color;
              ctx.shadowColor = color;
              ctx.shadowBlur = isObs ? 12 : 9;
              ctx.lineWidth = isObs ? 3.5 : 2.8;

              ctx.beginPath();
              ctx.moveTo(x1, y);
              ctx.lineTo(x2, y);
              ctx.stroke();
            }
          } else if (bothSolid) {
            // Internal seam in depth
            if (!airContactOnly && showInternalSeams) {
              const isTransition = above !== below;
              ctx.strokeStyle = isTransition ? 'rgba(255, 60, 90, 0.5)' : 'rgba(0, 200, 255, 0.25)';
              ctx.shadowBlur = 0;
              ctx.lineWidth = 1.5;
              ctx.setLineDash([3, 3]);

              ctx.beginPath();
              ctx.moveTo(x1, y);
              ctx.lineTo(x2, y);
              ctx.stroke();
              ctx.setLineDash([]);
            }
          }
        }
      }

      // 2D Vertical edges on contact with air
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c <= 8; c++) {
          const left: CellState = c > 0 ? grid[r][c - 1] : 'air';
          const right: CellState = c < 8 ? grid[r][c] : 'air';

          const hasAir = left === 'air' || right === 'air';
          const bothSolid = left !== 'air' && right !== 'air';

          if (left === 'air' && right === 'air') continue;

          const x = startX + c * cellSize;
          const y1 = startY + r * cellSize;
          const y2 = startY + (r + 1) * cellSize;

          if (hasAir) {
            const solidCell = left !== 'air' ? left : right;
            const isObs = solidCell === 'foreign';
            const color = isObs ? '#ff1e40' : '#00f0ff';

            if ((isObs && showObstacleGlow) || (!isObs && showHologramGlow)) {
              ctx.strokeStyle = color;
              ctx.shadowColor = color;
              ctx.shadowBlur = isObs ? 12 : 9;
              ctx.lineWidth = isObs ? 3.5 : 2.8;

              ctx.beginPath();
              ctx.moveTo(x, y1);
              ctx.lineTo(x, y2);
              ctx.stroke();
            }
          } else if (bothSolid) {
            // Internal seam in depth
            if (!airContactOnly && showInternalSeams) {
              const isTransition = left !== right;
              ctx.strokeStyle = isTransition ? 'rgba(255, 60, 90, 0.5)' : 'rgba(0, 200, 255, 0.25)';
              ctx.shadowBlur = 0;
              ctx.lineWidth = 1.5;
              ctx.setLineDash([3, 3]);

              ctx.beginPath();
              ctx.moveTo(x, y1);
              ctx.lineTo(x, y2);
              ctx.stroke();
              ctx.setLineDash([]);
            }
          }
        }
      }

      ctx.restore();
    }
  }, [grid, airContactOnly, showObstacleGlow, showHologramGlow, showInternalSeams, viewMode]);

  // Statistics
  const hologramCount = grid.flat().filter((c) => c === 'hologram').length;
  const foreignCount = grid.flat().filter((c) => c === 'foreign').length;

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-neutral-800">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-medium mb-1">
            <Wind className="w-3.5 h-3.5 text-cyan-400" />
            <span>Подсветка рёбер: строго на контакте с воздухом</span>
            <span className="px-1.5 py-0.2 bg-emerald-500 text-neutral-950 font-bold rounded text-[10px]">
              AIR-CONTACT
            </span>
          </div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span>Визуализатор подсветки рёбер слоя (как видит игрок)</span>
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5 leading-relaxed">
            Рёбра подсвечиваются <b>исключительно на контакте с воздухом</b> — там, где они действительно открыты взгляду игрока. В толще слоя между глухими блоками рёбра скрыты, устраняя визуальный мусор и путаницу внутри кладки.
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="flex bg-neutral-950 border border-neutral-800 rounded-xl p-1 gap-1 shrink-0">
          <button
            onClick={() => setViewMode('iso3d')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
              viewMode === 'iso3d'
                ? 'bg-cyan-500 text-neutral-950 font-bold shadow-md'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Box className="w-3.5 h-3.5" />
            <span>3D Изометрия</span>
          </button>
          <button
            onClick={() => setViewMode('flat2d')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
              viewMode === 'flat2d'
                ? 'bg-cyan-500 text-neutral-950 font-bold shadow-md'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>2D План Слой</span>
          </button>
        </div>
      </div>

      {/* Control Buttons & Toggles Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-neutral-950/80 p-3 rounded-xl border border-neutral-800">
        <div className="flex flex-wrap items-center gap-2">
          {/* Quick Simulation Presets */}
          <button
            onClick={handlePresetForeignCluster}
            className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
            title="Препятствия на внешнем контуре стены"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Препятствия в стене</span>
          </button>

          <button
            onClick={handlePresetInteriorMass}
            className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
            title="Демонстрация: блок в толще массива не светит ребрами в глубине"
          >
            <Box className="w-3.5 h-3.5" />
            <span>Тест: блок в глубине</span>
          </button>

          <button
            onClick={handlePresetPureHolograms}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
            title="Очистить и оставить только чистый чертеж"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Чистый чертёж</span>
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Strict Air-Contact Filter (The Core Fix) */}
          <button
            onClick={() => setAirContactOnly(!airContactOnly)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
              airContactOnly
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'bg-neutral-800 text-neutral-400 border border-neutral-700'
            }`}
            title="Светятся строго рёбра на границе с воздухом"
          >
            <Wind className="w-3.5 h-3.5" />
            <span>Только контакт с воздухом: {airContactOnly ? 'ВКЛ' : 'ВЫКЛ'}</span>
          </button>

          {/* Obstacle Glow Toggle */}
          <button
            onClick={() => setShowObstacleGlow(!showObstacleGlow)}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
              showObstacleGlow
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                : 'bg-neutral-800 text-neutral-500'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span>Препятствия (Red): {showObstacleGlow ? 'ВКЛ' : 'ВЫКЛ'}</span>
          </button>

          {/* Hologram Glow Toggle */}
          <button
            onClick={() => setShowHologramGlow(!showHologramGlow)}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
              showHologramGlow
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'bg-neutral-800 text-neutral-500'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>Чертёж (Cyan): {showHologramGlow ? 'ВКЛ' : 'ВЫКЛ'}</span>
          </button>
        </div>
      </div>

      {/* Main Canvas Visualizer Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
        {/* Canvas Screen (Left 8 Cols) */}
        <div className="lg:col-span-8 bg-neutral-950 rounded-xl overflow-hidden border border-neutral-800 relative min-h-[380px] flex items-center justify-center p-2 shadow-inner">
          <canvas
            ref={canvasRef}
            width={680}
            height={380}
            className="w-full h-full object-contain"
          />

          {/* On-screen Badges */}
          <div className="absolute top-3 left-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-3 py-1.5 text-xs font-bold text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>Слой 1: Рёбра на контакте с воздухом</span>
          </div>

          <div className="absolute bottom-3 right-3 bg-neutral-900/90 backdrop-blur border border-neutral-800 rounded-lg px-2.5 py-1.5 text-[11px] font-mono text-cyan-400 flex items-center gap-2">
            <Shield className="w-3.5 h-3.5" />
            <span>Векторный контур · 0 particles · hasAir == true</span>
          </div>
        </div>

        {/* Right 4 Cols: Interactive Grid Click Palette & Explanation */}
        <div className="lg:col-span-4 space-y-3">
          <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-3.5 space-y-3">
            <div className="text-xs font-bold text-neutral-300 uppercase tracking-wider flex items-center justify-between">
              <span>Кисть редактирования сетки слоя:</span>
            </div>

            <div className="grid grid-cols-3 gap-1.5 text-xs font-semibold">
              <button
                onClick={() => setActiveBrush('foreign')}
                className={`p-2 rounded-lg border text-center transition-all cursor-pointer ${
                  activeBrush === 'foreign'
                    ? 'bg-rose-500/20 border-rose-500 text-rose-300 font-bold shadow-sm'
                    : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
                }`}
              >
                🧱 Препятствие
              </button>
              <button
                onClick={() => setActiveBrush('hologram')}
                className={`p-2 rounded-lg border text-center transition-all cursor-pointer ${
                  activeBrush === 'hologram'
                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300 font-bold shadow-sm'
                    : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
                }`}
              >
                🧊 Голограмма
              </button>
              <button
                onClick={() => setActiveBrush('air')}
                className={`p-2 rounded-lg border text-center transition-all cursor-pointer ${
                  activeBrush === 'air'
                    ? 'bg-neutral-800 border-neutral-600 text-white font-bold shadow-sm'
                    : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white'
                }`}
              >
                ⬛ Воздух
              </button>
            </div>

            {/* Clickable 8x8 Mini Grid */}
            <div className="pt-2 border-t border-neutral-800">
              <div className="text-[11px] text-neutral-400 mb-1.5 flex items-center justify-between font-mono">
                <span>Кликните по ячейке 8×8 для установки:</span>
                <span className="text-cyan-400 font-bold">{activeBrush.toUpperCase()}</span>
              </div>

              <div className="grid grid-cols-8 gap-1 p-2 bg-neutral-900 rounded-lg border border-neutral-800">
                {grid.map((row, rIdx) =>
                  row.map((cell, cIdx) => (
                    <button
                      key={`${rIdx}-${cIdx}`}
                      onClick={() => handleCellClick(rIdx, cIdx)}
                      className={`w-6 h-6 rounded text-[9px] font-mono font-bold transition-transform hover:scale-110 flex items-center justify-center cursor-pointer ${
                        cell === 'hologram'
                          ? 'bg-cyan-500/30 text-cyan-300 border border-cyan-500/60'
                          : cell === 'foreign'
                          ? 'bg-rose-500/40 text-rose-200 border border-rose-500/70'
                          : 'bg-neutral-950 text-neutral-700 border border-neutral-900'
                      }`}
                      title={`[R:${rIdx}, C:${cIdx}] ${cell.toUpperCase()}`}
                    >
                      {cell === 'hologram' ? 'H' : cell === 'foreign' ? 'F' : '·'}
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Legend Breakdown */}
            <div className="pt-2 border-t border-neutral-800 space-y-1.5 text-[11px]">
              <div className="flex items-center justify-between text-neutral-300">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/50" />
                  <span>Рёбра чертежа (на контакте с воздухом):</span>
                </span>
                <span className="font-mono font-bold text-cyan-400">{hologramCount} бл.</span>
              </div>
              <div className="flex items-center justify-between text-neutral-300">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500/50" />
                  <span>Рёбра препятствий (на контакте с воздухом):</span>
                </span>
                <span className="font-mono font-bold text-rose-400">{foreignCount} бл.</span>
              </div>
            </div>
          </div>

          {/* Explanation Box */}
          <div className="bg-neutral-950/80 border border-neutral-800 rounded-xl p-3 text-[11px] text-neutral-300 space-y-1.5 leading-relaxed">
            <div className="font-bold text-cyan-400 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-cyan-400" />
              <span>Правило контакта с воздухом (hasAir):</span>
            </div>
            <p className="text-neutral-400">
              Рёбра подсвечиваются <b>только там, где они видны игроку</b> — то есть на непосредственном контакте с воздухом. Если блок окружён другими блоками внутри кладки («в глубине слоя»), его внутренние рёбра скрыты и не создают визуальных помех.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
