import React, { useState } from 'react';
import { NationWarManagerView } from './NationWarManagerView';
import { ChunkSiegeCaptureSimulator } from './ChunkSiegeCaptureSimulator';
import { INITIAL_NATIONS } from '../data/nationWarData';
import {
  Map,
  Compass,
  Bed,
  Shield,
  Flame,
  Landmark,
  Crown,
  Sparkles,
  RefreshCw,
  Layers,
  Check,
  Eye,
  Sliders,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Sun,
  Moon,
  Sunset,
  Edit3,
  X,
  Plus,
  Trash2,
  AlertTriangle,
  Info,
  Swords,
  Bomb,
  FastForward,
  Tent,
  Flag
} from 'lucide-react';
import { TOWNY_RESPAWN_METADATA } from '../data/townyRespawnData';
import { downloadTownyRespawnJar, downloadTownyRespawnBundle } from '../utils/downloadHelpers';

interface SimBed {
  id: string;
  name: string;
  world: string;
  x: number;
  y: number;
  z: number;
  mapPercentX: number; // percentage position on BlueMap image
  mapPercentY: number;
}

export const TownyRespawnSimulator: React.FC = () => {
  // Top view toggle: 'bluemap', 'nation_war', 'chunk_capture', or 'respawn_gui'
  const [activeView, setActiveView] = useState<'bluemap' | 'nation_war' | 'chunk_capture' | 'respawn_gui'>('bluemap');
  const [showNationWars, setShowNationWars] = useState<boolean>(true);

  // BlueMap state
  const [zoom, setZoom] = useState<number>(100);
  const [panX, setPanX] = useState<number>(0);
  const [panY, setPanY] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [perspective, setPerspective] = useState<'isometric' | 'topdown'>('isometric');
  const [timeOfDay, setTimeOfDay] = useState<'day' | 'sunset' | 'night'>('day');
  const [showTowns, setShowTowns] = useState<boolean>(true);
  const [showSieges, setShowSieges] = useState<boolean>(true);
  const [showBeds, setShowBeds] = useState<boolean>(true);
  const [showSpawn, setShowSpawn] = useState<boolean>(true);
  const [inspectedEntity, setInspectedEntity] = useState<string | null>(null);

  // In-Game /respawn Simulator state
  const [ingameMode, setIngameMode] = useState<'normal_command' | 'death_screen' | 'respawn_menu'>('respawn_menu');
  const [renamingBedId, setRenamingBedId] = useState<string | null>(null);
  const [renameInput, setRenameInput] = useState<string>('');
  const [respawnFeedback, setRespawnFeedback] = useState<string | null>(null);

  // Dynamic player beds (can be renamed by player!)
  const [beds, setBeds] = useState<SimBed[]>([
    {
      id: 'bed_1',
      name: 'Лесная усадьба (Дом #1)',
      world: 'world',
      x: 184,
      y: 68,
      z: 242,
      mapPercentX: 28,
      mapPercentY: 76
    },
    {
      id: 'bed_2',
      name: 'Горная база у водопада',
      world: 'world',
      x: 82,
      y: 114,
      z: 112,
      mapPercentX: 14,
      mapPercentY: 34
    }
  ]);

  // Handle Pan / Drag for BlueMap
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - panX, y: e.clientY - panY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPanX(e.clientX - dragStart.x);
    setPanY(e.clientY - dragStart.y);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetView = () => {
    setZoom(100);
    setPanX(0);
    setPanY(0);
  };

  // Renaming bed logic
  const handleStartRename = (bed: SimBed) => {
    setRenamingBedId(bed.id);
    setRenameInput(bed.name);
  };

  const handleSaveRename = () => {
    if (!renamingBedId || !renameInput.trim()) return;
    const trimmed = renameInput.trim().slice(0, 32);
    setBeds(prev => prev.map(b => b.id === renamingBedId ? { ...b, name: trimmed } : b));
    setRenamingBedId(null);
    setRespawnFeedback(`✔ Кровать переименована в «${trimmed}»!`);
    setTimeout(() => setRespawnFeedback(null), 3000);
  };

  // 1. Simulate breaking a bed (Auto-deletion from menu)
  const handleBreakBed = (bedId: string) => {
    const target = beds.find(b => b.id === bedId);
    if (!target) return;
    setBeds(prev => prev.filter(b => b.id !== bedId));
    setRespawnFeedback(`💥 Блок кровати разрушен! Кровать «${target.name}» автоматически удалена из меню /respawn.`);
    setTimeout(() => setRespawnFeedback(null), 4000);
  };

  // Reset default beds
  const handleResetBeds = () => {
    setBeds([
      {
        id: 'bed_1',
        name: 'Лесная усадьба (Дом #1)',
        world: 'world',
        x: 184,
        y: 68,
        z: 242,
        mapPercentX: 28,
        mapPercentY: 76
      },
      {
        id: 'bed_2',
        name: 'Горная база у водопада',
        world: 'world',
        x: 82,
        y: 114,
        z: 112,
        mapPercentX: 14,
        mapPercentY: 34
      }
    ]);
    setRespawnFeedback('🔄 Список кроватей сброшен к исходному.');
    setTimeout(() => setRespawnFeedback(null), 3000);
  };

  // 2. Simulate another player attempting to claim this bed
  const handleTestOtherPlayerClaim = (bedName: string) => {
    setRespawnFeedback(`❌ [TownyRespawn] Эта кровать уже занята игроком Lord_Alden! На одной кровати может поставить спавн только один игрок.`);
    setTimeout(() => setRespawnFeedback(null), 4500);
  };

  // 3. Simulate HEAD vs FOOT click test
  const handleTestHeadVsFoot = (bed: SimBed) => {
    setRespawnFeedback(`✔ Изголовье [X: ${bed.x}] и Изножье [X: ${bed.x + 1}] нормализованы к одной кровати «${bed.name}». Дублирования нет!`);
    setTimeout(() => setRespawnFeedback(null), 4500);
  };

  const handleAddNewBed = () => {
    if (beds.length >= 3) {
      setRespawnFeedback('✖ Достигнут лимит кроватей (3/3)!');
      setTimeout(() => setRespawnFeedback(null), 3000);
      return;
    }
    const newIndex = beds.length + 1;
    const newBed: SimBed = {
      id: `bed_${Date.now()}`,
      name: `Кровать #${newIndex} (Новый форпост)`,
      world: 'world',
      x: Math.floor(100 + Math.random() * 80),
      y: 72,
      z: Math.floor(160 + Math.random() * 80),
      mapPercentX: 52 + Math.random() * 12,
      mapPercentY: 48 + Math.random() * 12
    };
    setBeds(prev => [...prev, newBed]);
    setRespawnFeedback(`✔ Добавлена новая кровать «${newBed.name}» (${beds.length + 1}/3)!`);
    setTimeout(() => setRespawnFeedback(null), 3000);
  };

  // Execute Respawn Simulation
  const handleExecuteRespawn = (locationName: string, coords: string) => {
    setRespawnFeedback(
      `⚡ Возрождение в «${locationName}» [${coords}]! Чистый респавн (Без слепоты и замедления). Сопротивление 5 сек.`
    );
    if (ingameMode === 'death_screen' || ingameMode === 'respawn_menu') {
      setTimeout(() => {
        setIngameMode('respawn_menu');
      }, 500);
    }
    setTimeout(() => {
      setRespawnFeedback(null);
    }, 4500);
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Top Main Card */}
      <div className="bg-neutral-900/90 border border-neutral-800 rounded-3xl p-6 sm:p-8 backdrop-blur-md shadow-2xl relative overflow-hidden">
        {/* Header & Mode Switcher */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-neutral-800">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="p-2.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Map className="w-6 h-6" />
              </span>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                    TownyRespawn & Веб-карта BlueMap
                  </h2>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                    v1.1.0
                  </span>
                </div>
                <div className="text-xs text-neutral-400 flex items-center gap-2 mt-1">
                  <span>Реальный вид карты без чанковых сеток</span>
                  <span aria-hidden="true">•</span>
                  <span className="text-cyan-400">Переименование кроватей</span>
                  <span aria-hidden="true">•</span>
                  <span className="text-emerald-400 font-medium">Без слепоты и замедления</span>
                </div>
              </div>
            </div>
            <p className="text-neutral-300 text-sm sm:text-base max-w-3xl">
              Карта мира вынесена на сайт в аутентичном стиле BlueMap со сплошным реалистичным рельефом без чанковых границ.
              В игре меню <code className="px-1.5 py-0.5 rounded bg-neutral-800 text-amber-300 font-mono text-xs">/respawn</code> представляет собой удобный список точек с возможностью переименования кроватей каждым игроком!
            </p>
          </div>

          {/* Download Buttons */}
          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            <button
              onClick={() => downloadTownyRespawnJar()}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-neutral-950 font-bold text-sm transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
            >
              <Map className="w-4 h-4" />
              <span>Скачать TownyRespawn.jar</span>
            </button>
            <button
              onClick={() => downloadTownyRespawnBundle()}
              className="px-4 py-2.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-semibold text-sm transition-all border border-neutral-700 flex items-center gap-2 cursor-pointer"
            >
              <span>Bundle ZIP</span>
            </button>
          </div>
        </div>

        {/* View Switcher Tabs: BlueMap vs In-Game GUI */}
        <div className="flex items-center justify-between gap-4 mt-6 flex-wrap">
          <div className="flex items-center p-1 bg-neutral-950 border border-neutral-800 rounded-2xl">
            <button
              onClick={() => setActiveView('bluemap')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                activeView === 'bluemap'
                  ? 'bg-cyan-500 text-neutral-950 shadow-md'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Map className="w-4 h-4" />
              <span>Реалистичная веб-карта BlueMap (Сайт)</span>
            </button>
            <button
              onClick={() => setActiveView('nation_war')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                activeView === 'nation_war'
                  ? 'bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 text-neutral-950 shadow-md font-black'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Crown className="w-4 h-4 text-amber-400" />
              <span>Войны Наций (Nation Wars)</span>
              <span className="px-1.5 py-0.2 rounded bg-red-600 text-white font-mono text-[10px] font-bold">24ч/2ч</span>
            </button>
            <button
              onClick={() => setActiveView('chunk_capture')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                activeView === 'chunk_capture'
                  ? 'bg-gradient-to-r from-red-500 via-rose-500 to-amber-500 text-neutral-950 shadow-md font-black'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Flag className="w-4 h-4 text-red-500" />
              <span>Почанковый Штурм & Флаг</span>
              <span className="px-1.5 py-0.2 rounded bg-amber-400 text-neutral-950 font-mono text-[10px] font-black">v1.4.0 NEW</span>
            </button>
            <button
              onClick={() => setActiveView('respawn_gui')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                activeView === 'respawn_gui'
                  ? 'bg-cyan-500 text-neutral-950 shadow-md'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Bed className="w-4 h-4" />
              <span>Симулятор /respawn & Кровати</span>
            </button>
          </div>

          {/* Active status indicator */}
          <div className="text-xs text-neutral-400 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Кроватей привязано: <strong className="text-white">{beds.length}/3</strong></span>
          </div>
        </div>

        {/* Live Feedback Toast */}
        {respawnFeedback && (
          <div className="mt-4 p-3.5 rounded-xl bg-cyan-950/80 border border-cyan-500/40 text-cyan-200 text-sm flex items-center gap-2 shadow-lg animate-fade-in">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>{respawnFeedback}</span>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 1: REALISTIC BLUEMAP (Continuous realistic terrain, NO chunk grid)   */}
        {/* ========================================================================= */}
        {activeView === 'bluemap' && (
          <div className="mt-6">
            {/* BlueMap Control Header Bar */}
            <div className="bg-neutral-950/90 border border-neutral-800 rounded-t-2xl p-3 sm:p-4 flex flex-wrap items-center justify-between gap-4">
              {/* Left: BlueMap Branding & World */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-xs font-mono font-bold text-cyan-400">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <span>BlueMap v5 · world</span>
                </div>

                {/* Perspective selector */}
                <div className="flex items-center bg-neutral-900 rounded-lg p-0.5 border border-neutral-800 text-xs">
                  <button
                    onClick={() => setPerspective('isometric')}
                    className={`px-2.5 py-1 rounded font-medium transition-colors ${
                      perspective === 'isometric' ? 'bg-cyan-500 text-neutral-950' : 'text-neutral-400 hover:text-white'
                    }`}
                  >
                    3D Изометрия
                  </button>
                  <button
                    onClick={() => setPerspective('topdown')}
                    className={`px-2.5 py-1 rounded font-medium transition-colors ${
                      perspective === 'topdown' ? 'bg-cyan-500 text-neutral-950' : 'text-neutral-400 hover:text-white'
                    }`}
                  >
                    2D Спутник
                  </button>
                </div>
              </div>

              {/* Center: Lighting / Time of day */}
              <div className="flex items-center gap-1 bg-neutral-900 p-1 rounded-xl border border-neutral-800">
                <button
                  onClick={() => setTimeOfDay('day')}
                  className={`p-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-all ${
                    timeOfDay === 'day' ? 'bg-amber-500 text-neutral-950 shadow-sm' : 'text-neutral-400 hover:text-white'
                  }`}
                  title="Дневное освещение"
                >
                  <Sun className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">День</span>
                </button>
                <button
                  onClick={() => setTimeOfDay('sunset')}
                  className={`p-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-all ${
                    timeOfDay === 'sunset' ? 'bg-orange-500 text-white shadow-sm' : 'text-neutral-400 hover:text-white'
                  }`}
                  title="Закатное освещение"
                >
                  <Sunset className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Закат</span>
                </button>
                <button
                  onClick={() => setTimeOfDay('night')}
                  className={`p-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-all ${
                    timeOfDay === 'night' ? 'bg-indigo-600 text-white shadow-sm' : 'text-neutral-400 hover:text-white'
                  }`}
                  title="Ночное освещение"
                >
                  <Moon className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Ночь</span>
                </button>
              </div>

              {/* Right: Layers Toggles & Zoom Controls */}
              <div className="flex items-center gap-2 flex-wrap">
                {/* Layer pills */}
                <button
                  onClick={() => setShowNationWars(!showNationWars)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-colors flex items-center gap-1.5 ${
                    showNationWars ? 'bg-amber-950/80 border-amber-500/70 text-amber-300 shadow-sm' : 'bg-neutral-900 border-neutral-800 text-neutral-500 line-through'
                  }`}
                >
                  <Swords className="w-3 h-3 text-amber-400" />
                  <span>Войны Наций</span>
                </button>
                <button
                  onClick={() => setShowTowns(!showTowns)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-colors flex items-center gap-1.5 ${
                    showTowns ? 'bg-emerald-950/70 border-emerald-500/60 text-emerald-300' : 'bg-neutral-900 border-neutral-800 text-neutral-500 line-through'
                  }`}
                >
                  <Landmark className="w-3 h-3" />
                  <span>Города</span>
                </button>
                <button
                  onClick={() => setShowSieges(!showSieges)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-colors flex items-center gap-1.5 ${
                    showSieges ? 'bg-red-950/70 border-red-500/60 text-red-300' : 'bg-neutral-900 border-neutral-800 text-neutral-500 line-through'
                  }`}
                >
                  <Flame className="w-3 h-3" />
                  <span>Осады</span>
                </button>
                <button
                  onClick={() => setShowBeds(!showBeds)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-colors flex items-center gap-1.5 ${
                    showBeds ? 'bg-cyan-950/70 border-cyan-500/60 text-cyan-300' : 'bg-neutral-900 border-neutral-800 text-neutral-500 line-through'
                  }`}
                >
                  <Bed className="w-3 h-3" />
                  <span>Кровати ({beds.length})</span>
                </button>

                {/* Zoom */}
                <div className="flex items-center bg-neutral-900 rounded-lg border border-neutral-800">
                  <button
                    onClick={() => setZoom(Math.max(60, zoom - 15))}
                    className="p-1.5 hover:text-white text-neutral-400"
                    title="Уменьшить"
                  >
                    <ZoomOut className="w-3.5 h-3.5" />
                  </button>
                  <span className="px-2 text-xs font-mono text-neutral-300">{zoom}%</span>
                  <button
                    onClick={() => setZoom(Math.min(180, zoom + 15))}
                    className="p-1.5 hover:text-white text-neutral-400"
                    title="Увеличить"
                  >
                    <ZoomIn className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={resetView}
                    className="p-1.5 hover:text-white text-neutral-400 border-l border-neutral-800"
                    title="Сбросить центрирование"
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>

            {/* BlueMap Canvas Viewport */}
            <div
              className="relative w-full h-[520px] sm:h-[620px] bg-neutral-950 overflow-hidden cursor-grab active:cursor-grabbing border-x border-b border-neutral-800 rounded-b-2xl select-none"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              {/* The Realistic Continuous Terrain Canvas */}
              <div
                className="w-full h-full relative transition-transform duration-75 ease-out"
                style={{
                  transform: `translate(${panX}px, ${panY}px) scale(${zoom / 100})`,
                  transformOrigin: 'center center'
                }}
              >
                {/* Realistic Photorealistic Minecraft Terrain Layer (NO chunk grid lines!) */}
                <img
                  src={`${import.meta.env.BASE_URL}bluemap_realistic_terrain.jpg`}
                  alt="Realistic BlueMap Minecraft World"
                  className={`w-full h-full object-cover transition-all duration-500 pointer-events-none ${
                    timeOfDay === 'sunset' ? 'brightness-90 sepia-[0.25] hue-rotate-[-10deg]' :
                    timeOfDay === 'night' ? 'brightness-[0.45] contrast-125 saturate-75' :
                    'brightness-100'
                  }`}
                />

                {/* Night Lighting Overlay for Torches & Glow */}
                {timeOfDay === 'night' && (
                  <div className="absolute inset-0 bg-blue-950/30 mix-blend-color-burn pointer-events-none" />
                )}

                {/* 0. Nation Wars Frontline & Nations Territory Overlay on BlueMap */}
                {showNationWars && (
                  <>
                    {/* North Alliance Nation Territory (Northern Region) */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('nation_north');
                      }}
                      className="absolute top-[14%] left-[12%] w-[46%] h-[40%] rounded-[40%] border-2 border-dashed border-amber-500/70 bg-amber-500/10 shadow-[0_0_35px_rgba(245,158,11,0.25)] cursor-pointer hover:border-amber-400 hover:bg-amber-500/15 transition-all group"
                    >
                      <div className="absolute top-[8%] left-[22%] px-3 py-1 rounded-xl bg-neutral-950/95 border border-amber-500 text-amber-300 shadow-xl flex items-center gap-2 group-hover:scale-105 transition-transform whitespace-nowrap">
                        <Crown className="w-3.5 h-3.5 text-amber-400" />
                        <div>
                          <div className="text-xs font-bold text-amber-300">Северный Альянс</div>
                          <div className="text-[10px] text-neutral-400">Глава: Yaroslav_Great · 3 города</div>
                        </div>
                      </div>
                    </div>

                    {/* Towns of Northern Alliance: Novgorod, Nordgard, Valhalla */}
                    {/* Novgorod (Capital) */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('town_novgorod');
                      }}
                      className="absolute top-[34%] left-[38%] -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
                    >
                      <div className="relative flex flex-col items-center">
                        <div className="w-8 h-8 rounded-full bg-amber-500 border-2 border-white shadow-xl flex items-center justify-center text-neutral-950 font-bold group-hover:scale-125 transition-transform">
                          🏛
                        </div>
                        <div className="mt-1 px-2.5 py-0.5 rounded-lg bg-neutral-950/95 border border-amber-400 text-amber-200 text-[10px] font-bold shadow-lg flex items-center gap-1 group-hover:scale-105 transition-transform whitespace-nowrap">
                          <span>Новгород</span>
                          <span className="text-[9px] px-1 rounded bg-amber-500/20 text-amber-300 font-mono">24ч/2ч</span>
                        </div>
                      </div>
                    </div>

                    {/* Nordgard (Fortress town) */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('town_nordgard');
                      }}
                      className="absolute top-[28%] left-[18%] -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
                    >
                      <div className="relative flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-amber-600 border-2 border-white shadow-xl flex items-center justify-center text-white font-bold group-hover:scale-125 transition-transform">
                          🛡
                        </div>
                        <div className="mt-1 px-2 py-0.5 rounded-lg bg-neutral-950/95 border border-amber-500 text-amber-200 text-[10px] font-bold shadow-lg whitespace-nowrap">
                          Нордгард
                        </div>
                      </div>
                    </div>

                    {/* Valhalla */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('town_valhalla');
                      }}
                      className="absolute top-[20%] left-[48%] -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
                    >
                      <div className="relative flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-amber-700 border-2 border-white shadow-xl flex items-center justify-center text-white font-bold group-hover:scale-125 transition-transform">
                          ⚔
                        </div>
                        <div className="mt-1 px-2 py-0.5 rounded-lg bg-neutral-950/95 border border-amber-600 text-amber-200 text-[10px] font-bold shadow-lg whitespace-nowrap">
                          Валгалла
                        </div>
                      </div>
                    </div>

                    {/* South League Nation Territory (Southern Region) */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('nation_south');
                      }}
                      className="absolute top-[46%] left-[44%] w-[52%] h-[48%] rounded-[45%] border-2 border-dashed border-emerald-500/70 bg-emerald-500/10 shadow-[0_0_35px_rgba(16,185,129,0.25)] cursor-pointer hover:border-emerald-400 hover:bg-emerald-500/15 transition-all group"
                    >
                      <div className="absolute top-[6%] left-[32%] px-3 py-1 rounded-xl bg-neutral-950/95 border border-emerald-400 text-emerald-300 shadow-xl flex items-center gap-2 group-hover:scale-105 transition-transform whitespace-nowrap">
                        <Crown className="w-3.5 h-3.5 text-emerald-400" />
                        <div>
                          <div className="text-xs font-bold text-emerald-300">Южная Лига</div>
                          <div className="text-[10px] text-neutral-400">Глава: Prince_Vsevolod · 3 города</div>
                        </div>
                      </div>
                    </div>

                    {/* Towns of Southern League: Kitezh, Solntsedar */}
                    {/* Kitezh-Grad */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('town_kitezh');
                      }}
                      className="absolute top-[48%] left-[82%] -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
                    >
                      <div className="relative flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-emerald-600 border-2 border-white shadow-xl flex items-center justify-center text-white font-bold group-hover:scale-125 transition-transform">
                          🏰
                        </div>
                        <div className="mt-1 px-2 py-0.5 rounded-lg bg-neutral-950/95 border border-emerald-400 text-emerald-200 text-[10px] font-bold shadow-lg whitespace-nowrap">
                          Китеж-Град
                        </div>
                      </div>
                    </div>

                    {/* Solntsedar */}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectedEntity('town_solntsedar');
                      }}
                      className="absolute top-[78%] left-[74%] -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
                    >
                      <div className="relative flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-emerald-700 border-2 border-white shadow-xl flex items-center justify-center text-white font-bold group-hover:scale-125 transition-transform">
                          ⚓
                        </div>
                        <div className="mt-1 px-2 py-0.5 rounded-lg bg-neutral-950/95 border border-emerald-500 text-emerald-200 text-[10px] font-bold shadow-lg whitespace-nowrap">
                          Солнцедар
                        </div>
                      </div>
                    </div>

                    {/* Frontline Dynamic Banner in BlueMap Header */}
                    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 pointer-events-auto">
                      <div
                        onClick={() => setActiveView('nation_war')}
                        className="px-4 py-2 rounded-2xl bg-neutral-950/95 border-2 border-amber-500/80 text-white shadow-2xl backdrop-blur-md flex items-center gap-3 cursor-pointer hover:border-amber-400 hover:scale-105 transition-all"
                      >
                        <Swords className="w-4 h-4 text-amber-400 animate-pulse" />
                        <div className="text-xs">
                          <span className="font-bold text-amber-300">ВОЙНА НАЦИЙ:</span>{' '}
                          <span className="text-neutral-200">Северный Альянс ⚔ Южная Лига</span>
                          <span className="ml-2 font-mono px-1.5 py-0.5 rounded bg-red-950 text-red-300 border border-red-800 text-[10px]">
                            Единый таймер наций
                          </span>
                        </div>
                        <span className="text-xs font-bold text-amber-400 underline ml-1">Центр войны ➔</span>
                      </div>
                    </div>
                  </>
                )}

                
                {/* 1. Towny Territory Glowing Overlay: City of Avalonia */}
                {showTowns && (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      setInspectedEntity('town_avalonia');
                    }}
                    className="absolute top-[22%] left-[43%] w-[48%] h-[56%] rounded-[45%] border-2 border-emerald-400/80 bg-emerald-500/10 shadow-[0_0_30px_rgba(16,185,129,0.35)] backdrop-blur-[0.5px] cursor-pointer hover:border-emerald-300 hover:bg-emerald-500/15 transition-all group"
                  >
                    {/* Glowing Town Banner Badge */}
                    <div className="absolute top-[12%] left-[32%] px-3 py-1.5 rounded-xl bg-neutral-950/90 border border-emerald-400 text-emerald-300 shadow-xl flex items-center gap-2 group-hover:scale-105 transition-transform">
                      <Landmark className="w-4 h-4 text-emerald-400 shrink-0" />
                      <div>
                        <div className="text-xs font-bold leading-tight">Город «Авалония»</div>
                        <div className="text-[10px] text-neutral-400">Мэр: Lord_Alden · 24 жителя</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. TownySieges Warzone Frontline Overlay: Siege Camp & Cannon Battery */}
                {showSieges && (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      setInspectedEntity('siege_nordgard');
                    }}
                    className="absolute top-[52%] left-[32%] w-[26%] h-[32%] rounded-full border-2 border-dashed border-red-500/90 bg-red-950/25 shadow-[0_0_25px_rgba(239,68,68,0.4)] animate-pulse cursor-pointer hover:border-red-400 transition-all group"
                  >
                    {/* Siege Badge */}
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-3 py-1 rounded-xl bg-red-950/95 border border-red-500 text-red-200 shadow-xl flex items-center gap-2 group-hover:scale-105 transition-transform whitespace-nowrap">
                      <Flame className="w-3.5 h-3.5 text-red-400 animate-bounce" />
                      <div>
                        <div className="text-xs font-bold text-red-300">ОСАДНЫЙ ЛАГЕРЬ</div>
                        <div className="text-[10px] text-red-200/80">Орудия активны · 01:42:15</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. Server Spawn Beacon Beam Overlay */}
                {showSpawn && (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      setInspectedEntity('server_spawn');
                    }}
                    className="absolute top-[38%] left-[72%] -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
                  >
                    {/* Beacon Light Beam */}
                    <div className="w-2 h-44 bg-gradient-to-t from-cyan-400 via-cyan-300/80 to-transparent blur-[1px] mx-auto animate-pulse" />
                    {/* Beacon Badge */}
                    <div className="px-2.5 py-1 rounded-lg bg-neutral-950/90 border border-cyan-400 text-cyan-300 text-[11px] font-bold shadow-lg flex items-center gap-1.5 -mt-2 group-hover:scale-110 transition-transform">
                      <Compass className="w-3 h-3 text-cyan-400" />
                      <span>Спавн Сервера</span>
                    </div>
                  </div>
                )}

                {/* 4. Player Beds Markers (with dynamic custom names from renaming!) */}
                {showBeds && beds.map((bed, idx) => (
                  <div
                    key={bed.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      setInspectedEntity(`bed_${bed.id}`);
                    }}
                    className="absolute cursor-pointer group -translate-x-1/2 -translate-y-1/2 transition-all"
                    style={{
                      left: `${bed.mapPercentX}%`,
                      top: `${bed.mapPercentY}%`
                    }}
                  >
                    <div className="relative flex flex-col items-center">
                      {/* Bed Icon Pin */}
                      <div className="w-7 h-7 rounded-full bg-red-600 border-2 border-white shadow-lg flex items-center justify-center text-white group-hover:scale-125 transition-transform">
                        <Bed className="w-3.5 h-3.5" />
                      </div>
                      {/* Bed Name Label */}
                      <div className="mt-1 px-2 py-0.5 rounded-md bg-neutral-950/90 border border-red-400/80 text-white text-[10px] font-semibold shadow-md whitespace-nowrap group-hover:scale-105 transition-transform">
                        {bed.name}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* BlueMap Floating Information Box / Tooltip */}
              <div className="absolute bottom-4 left-4 z-20 pointer-events-none max-w-sm">
                <div className="bg-neutral-950/90 border border-neutral-800 rounded-xl p-3 backdrop-blur-md shadow-xl text-xs text-neutral-300">
                  <div className="flex items-center gap-1.5 font-bold text-white mb-1">
                    <Info className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Сплошной рельеф BlueMap</span>
                  </div>
                  <p className="text-[11px] text-neutral-400">
                    Перетаскивайте карту зажатой мышью, масштабируйте колесиком. Нажмите на любой город, осаду или кровать для просмотра информации.
                  </p>
                </div>
              </div>

              {/* Inspected Entity Details Modal Overlay */}
              {inspectedEntity && (
                <div className="absolute top-4 right-4 z-30 max-w-sm w-full bg-neutral-950/95 border border-neutral-700 rounded-2xl p-4 shadow-2xl backdrop-blur-md animate-fade-in text-xs">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-neutral-800">
                    <span className="font-bold text-white text-sm">
                      {inspectedEntity === 'town_avalonia' && '🏛 Город «Авалония» (Towny)'}
                      {inspectedEntity === 'siege_nordgard' && '⚔ Осадный сектор «Нордгард»'}
                      {inspectedEntity === 'server_spawn' && '🏛 Спавн сервера (Центральный)'}
                      {inspectedEntity.startsWith('bed_') && '🛏 Персональная точка возрождения'}
                    </span>
                    <button
                      onClick={() => setInspectedEntity(null)}
                      className="text-neutral-400 hover:text-white p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {inspectedEntity === 'nation_north' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Нация: <strong className="text-amber-400">Северный Альянс</strong></div>
                      <div>Король (Глава): <strong className="text-white">Yaroslav_Great</strong></div>
                      <div>Столица: <strong className="text-neutral-200">Новгород</strong></div>
                      <div>Города: <strong className="text-white">Новгород, Нордгард, Валгалла</strong></div>
                      <div className="p-2 rounded bg-amber-950/60 border border-amber-500/40 text-amber-200 text-[11px]">
                        Все 3 города нации синхронизированы под единый 24-часовой таймер подготовки и 2-часовой штурм!
                      </div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Перейти к управлению Войной Наций
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'nation_south' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Нация: <strong className="text-emerald-400">Южная Лига</strong></div>
                      <div>Король (Глава): <strong className="text-white">Prince_Vsevolod</strong></div>
                      <div>Столица: <strong className="text-neutral-200">Авалония</strong></div>
                      <div>Города: <strong className="text-white">Авалония, Китеж-Град, Солнцедар</strong></div>
                      <div className="p-2 rounded bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-[11px]">
                        При объявлении войны все города переходят в режим подготовки и последующего 2ч штурма.
                      </div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Перейти к управлению Войной Наций
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'town_novgorod' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Город: <strong className="text-amber-400">Новгород (Столица)</strong></div>
                      <div>Нация: <strong className="text-white">Северный Альянс</strong></div>
                      <div>Мэр: <strong className="text-white">Yaroslav_Mayor</strong></div>
                      <div>Население: <strong className="text-white">28 жителей</strong></div>
                      <div className="p-2 rounded bg-neutral-900 border border-neutral-700 text-[11px]">
                        Военный статус: <strong className="text-amber-400">Единый таймер подготовки к штурму (24ч)</strong>. В фазе 2ч штурма становится уязвим к взрывам.
                      </div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Управление Войной Наций ➔
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'town_nordgard' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Город: <strong className="text-amber-400">Нордгард (Крепость)</strong></div>
                      <div>Нация: <strong className="text-white">Северный Альянс</strong></div>
                      <div>Мэр: <strong className="text-white">Ragnar_Lodbrok</strong></div>
                      <div>Население: <strong className="text-white">19 жителей</strong></div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Управление Войной Наций ➔
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'town_valhalla' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Город: <strong className="text-amber-400">Валгалла</strong></div>
                      <div>Нация: <strong className="text-white">Северный Альянс</strong></div>
                      <div>Мэр: <strong className="text-white">Einar_Stone</strong></div>
                      <div>Население: <strong className="text-white">14 жителей</strong></div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Управление Войной Наций ➔
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'town_kitezh' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Город: <strong className="text-emerald-400">Китеж-Град</strong></div>
                      <div>Нация: <strong className="text-white">Южная Лига</strong></div>
                      <div>Мэр: <strong className="text-white">Vsevolod_Prince</strong></div>
                      <div>Население: <strong className="text-white">18 жителей</strong></div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Управление Войной Наций ➔
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'town_solntsedar' && (
                    <div className="space-y-2 text-neutral-300">
                      <div>Город: <strong className="text-emerald-400">Солнцедар</strong></div>
                      <div>Нация: <strong className="text-white">Южная Лига</strong></div>
                      <div>Мэр: <strong className="text-white">Helena_Sun</strong></div>
                      <div>Население: <strong className="text-white">12 жителей</strong></div>
                      <button
                        onClick={() => setActiveView('nation_war')}
                        className="w-full py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                      >
                        Управление Войной Наций ➔
                      </button>
                    </div>
                  )}

                  {inspectedEntity === 'town_avalonia' && (
                    <div className="space-y-1.5 text-neutral-300">
                      <div>Статус: <strong className="text-emerald-400">Мирный город Towny</strong></div>
                      <div>Мэр: <strong className="text-white">Lord_Alden</strong></div>
                      <div>Нация: <strong className="text-amber-400">Великая Альянция</strong></div>
                      <div>Население: <strong className="text-white">24 жителя · 142 чанка</strong></div>
                      <div>Казна: <strong className="text-yellow-400">18,450 монет</strong></div>
                      <div className="pt-2">
                        <button
                          onClick={() => handleExecuteRespawn('Ратуша Авалонии', 'X: 160, Y: 70, Z: 210')}
                          className="w-full py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                        >
                          Возродиться в ратуше города (/t spawn)
                        </button>
                      </div>
                    </div>
                  )}

                  {inspectedEntity === 'siege_nordgard' && (
                    <div className="space-y-1.5 text-neutral-300">
                      <div>Статус: <strong className="text-red-400">Активный осадный форпост (TownySieges)</strong></div>
                      <div>Атакующие: <strong className="text-white">Нордгард (Мэр: Ragnar_Lodbrok)</strong></div>
                      <div>Цель: <strong className="text-amber-400">Город Авалония</strong></div>
                      <div>Осадная артиллерия: <strong className="text-orange-400">Мортиры разблокированы (2ч штурма)</strong></div>
                      <div className="p-2 rounded bg-red-950/60 border border-red-500/40 text-red-200 text-[11px]">
                        Внимание: Во время активного штурма территория подвержена разрушению ядрами орудий.
                      </div>
                    </div>
                  )}

                  {inspectedEntity === 'server_spawn' && (
                    <div className="space-y-1.5 text-neutral-300">
                      <div>Локация: <strong className="text-cyan-400">Центральная площадь мира</strong></div>
                      <div>Координаты: <strong className="text-white">X: 0, Y: 70, Z: 0</strong></div>
                      <div>PvP: <strong className="text-emerald-400">Отключено (Мирная зона)</strong></div>
                      <div className="pt-2">
                        <button
                          onClick={() => handleExecuteRespawn('Главный Спавн Сервера', 'X: 0, Y: 70, Z: 0')}
                          className="w-full py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                        >
                          Возродиться на спавне сервера
                        </button>
                      </div>
                    </div>
                  )}

                  {inspectedEntity.startsWith('bed_') && (
                    <div className="space-y-2 text-neutral-300">
                      {(() => {
                        const bedId = inspectedEntity.replace('bed_', '');
                        const bed = beds.find(b => b.id === bedId);
                        if (!bed) return null;
                        return (
                          <>
                            <div>Название: <strong className="text-white text-sm">{bed.name}</strong></div>
                            <div>Координаты: <strong className="font-mono text-cyan-300">X: {bed.x}, Y: {bed.y}, Z: {bed.z}</strong></div>
                            <div>Статус: <strong className="text-emerald-400">Цела и активна</strong></div>
                            <div className="flex items-center gap-2 pt-2">
                              <button
                                onClick={() => handleExecuteRespawn(bed.name, `X: ${bed.x}, Y: ${bed.y}, Z: ${bed.z}`)}
                                className="flex-1 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition-colors cursor-pointer"
                              >
                                Возродиться на кровати
                              </button>
                              <button
                                onClick={() => {
                                  setActiveView('respawn_gui');
                                  handleStartRename(bed);
                                }}
                                className="px-3 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-amber-300 font-bold text-xs border border-neutral-700 transition-colors flex items-center gap-1 cursor-pointer"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                                <span>Имя</span>
                              </button>
                            </div>
                          </>
                        );
                      })()}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* ========================================================================= */}
        {/* VIEW 2: NATION WARS CONTROL CENTER (24h Prep, 2h Assault, Unified Timers)   */}
        {/* ========================================================================= */}
        {activeView === 'nation_war' && (
          <div className="mt-6">
            <NationWarManagerView
              onOpenBlueMapWithWar={() => setActiveView('bluemap')}
              onSelectTownOnMap={(townId) => {
                setInspectedEntity(townId);
                setActiveView('bluemap');
              }}
            />
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 3: CHUNK-BY-CHUNK SIEGE CAPTURE SIMULATOR (v1.4.0)                   */}
        {/* ========================================================================= */}
        {activeView === 'chunk_capture' && (
          <div className="mt-6">
            <ChunkSiegeCaptureSimulator />
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 4: IN-GAME /RESPAWN SIMULATOR & BED RENAMING (NO MAP IN MINECRAFT!)  */}
        {/* ========================================================================= */}
        {activeView === 'respawn_gui' && (
          <div className="mt-6 space-y-6">
            {/* Top Sub-Mode Bar: Normal /respawn vs Death Screen */}
            <div className="flex items-center justify-between p-4 bg-neutral-950 border border-neutral-800 rounded-2xl flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Режим симуляции:</span>
                <button
                  onClick={() => setIngameMode('respawn_menu')}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    ingameMode === 'respawn_menu' ? 'bg-cyan-500 text-neutral-950' : 'bg-neutral-900 text-neutral-400 hover:text-white'
                  }`}
                >
                  Команда /respawn (Выбор из списка)
                </button>
                <button
                  onClick={() => setIngameMode('death_screen')}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    ingameMode === 'death_screen' ? 'bg-red-600 text-white shadow-lg shadow-red-500/20' : 'bg-neutral-900 text-neutral-400 hover:text-white'
                  }`}
                >
                  ☠ Экран смерти Minecraft
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleAddNewBed}
                  disabled={beds.length >= 3}
                  className="px-3 py-1.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 disabled:opacity-50 text-neutral-200 text-xs font-bold border border-neutral-700 flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Привязать кровать ({beds.length}/3)</span>
                </button>
              </div>
            </div>

            {/* CASE A: Simulated Vanilla Death Screen */}
            {ingameMode === 'death_screen' && (
              <div className="p-8 sm:p-12 bg-red-950/80 border-2 border-red-700 rounded-3xl text-center space-y-6 shadow-2xl backdrop-blur-md">
                <div className="space-y-2">
                  <h3 className="text-4xl sm:text-5xl font-black text-white font-mono tracking-wide drop-shadow-md">
                    Вы погибли!
                  </h3>
                  <p className="text-red-200 text-sm">
                    Ваш персонаж пал в бою. Нажмите «Возродиться», чтобы открыть список точек возрождения.
                  </p>
                  <div className="text-xs text-neutral-400 font-mono">Счёт: 1,420</div>
                </div>

                <div className="max-w-md mx-auto pt-4 space-y-3">
                  <button
                    onClick={() => {
                      setIngameMode('respawn_menu');
                      setRespawnFeedback('✔ Открыто меню выбора точек возрождения! (Без слепоты и замедления)');
                      setTimeout(() => setRespawnFeedback(null), 3500);
                    }}
                    className="w-full py-4 rounded-xl bg-neutral-800 hover:bg-neutral-700 border-2 border-neutral-600 hover:border-white text-white font-black text-lg transition-all shadow-xl cursor-pointer"
                  >
                    Возродиться
                  </button>
                  <div className="text-[11px] text-emerald-400 font-medium">
                    ⚡ Без слепоты, без замедления — мгновенный переход к выбору безопасной точки!
                  </div>
                </div>
              </div>
            )}

            {/* CASE B: Simulated In-Game Chest GUI (/respawn List) */}
            {ingameMode === 'respawn_menu' && (
              <div className="p-6 bg-neutral-950 border border-neutral-800 rounded-3xl space-y-6 shadow-2xl">
                {/* Minecraft Chest GUI Container Replica */}
                <div className="bg-[#2b2b2b] p-4 rounded-2xl border-4 border-[#3c3c3c] shadow-inner max-w-4xl mx-auto">
                  {/* Chest GUI Title */}
                  <div className="text-sm font-bold text-neutral-300 font-mono mb-4 px-2 flex items-center justify-between">
                    <span>Выбор точки возрождения /respawn</span>
                    <span className="text-xs text-neutral-400">Инвентарь: 54 слота</span>
                  </div>

                  {/* Top Banner Item (Slot 4) */}
                  <div className="p-3 mb-4 rounded-xl bg-[#202020] border border-[#444] flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 text-xl">
                        🧭
                      </div>
                      <div>
                        <div className="text-sm font-bold text-amber-300 font-mono">ВАШИ ТОЧКИ ВОЗРОЖДЕНИЯ</div>
                        <div className="text-xs text-neutral-400">
                          ЛКМ: Возродиться · ПКМ по кровати: Переименовать ✍
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-neutral-400 font-mono">
                      Кроватей: <strong className="text-emerald-400">{beds.length}/3</strong>
                    </div>
                  </div>

                  {/* List of Registered Beds */}
                  <div className="space-y-2 mb-6">
                    <div className="flex items-center justify-between px-1">
                      <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                        Привязанные кровати игрока ({beds.length}):
                      </div>
                      {beds.length === 0 && (
                        <button
                          onClick={handleResetBeds}
                          className="text-xs text-cyan-400 hover:underline flex items-center gap-1 cursor-pointer"
                        >
                          <RefreshCw className="w-3 h-3" />
                          <span>Сбросить / вернуть кровати</span>
                        </button>
                      )}
                    </div>

                    {beds.length === 0 ? (
                      <div className="p-6 rounded-2xl bg-[#1d1d1d] border-2 border-neutral-700 text-center space-y-3">
                        <div className="text-3xl">🚫</div>
                        <div className="text-sm font-bold text-neutral-300 font-mono">
                          У вас нет активных кроватей
                        </div>
                        <p className="text-xs text-neutral-400 max-w-md mx-auto">
                          Все разрушенные кровати были автоматически удалены из меню /respawn и базы данных.
                          Поспите на любой целой кровати в безопасном месте, чтобы привязать её!
                        </p>
                        <button
                          onClick={handleResetBeds}
                          className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-neutral-950 font-bold text-xs transition-colors cursor-pointer inline-flex items-center gap-1.5"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                          <span>Восстановить демонстрационные кровати</span>
                        </button>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {beds.map((bed, idx) => (
                        <div
                          key={bed.id}
                          className="p-3.5 rounded-xl bg-[#202020] border-2 border-red-500/40 hover:border-red-400 transition-all flex flex-col justify-between group shadow-md"
                        >
                          <div>
                            <div className="flex items-center justify-between gap-2 mb-1.5">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">🛏</span>
                                <span className="font-bold text-white text-xs sm:text-sm font-mono truncate max-w-[160px]">
                                  {bed.name}
                                </span>
                              </div>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-950 text-red-300 font-mono border border-red-800">
                                #{idx + 1}
                              </span>
                            </div>

                            <div className="text-[11px] text-neutral-400 font-mono space-y-0.5 mb-2">
                              <div>Мир: <span className="text-neutral-200">{bed.world}</span></div>
                              <div>Координаты: <span className="text-cyan-300">X: {bed.x}, Y: {bed.y}, Z: {bed.z}</span></div>
                              <div className="text-[10px] text-neutral-400">
                                Изголовье: <span className="text-white">X:{bed.x}</span> · Изножье: <span className="text-white">X:{bed.x + 1}</span>
                              </div>
                              <div className="text-emerald-400 text-[10px] flex items-center gap-1">
                                <Check className="w-3 h-3" />
                                <span>Кровать цела · 1 владелец</span>
                              </div>
                            </div>

                            {/* Testing interactive actions */}
                            <div className="bg-[#181818] p-2 rounded-lg border border-[#333] mb-2 space-y-1">
                              <div className="text-[10px] text-neutral-400 font-bold uppercase tracking-wider">Тесты функций:</div>
                              <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                                <button
                                  onClick={() => handleTestHeadVsFoot(bed)}
                                  className="px-2 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-cyan-300 border border-neutral-700 text-left truncate cursor-pointer"
                                  title="Проверка: клик по обоим блокам кровати считается одной кроватью"
                                >
                                  🔗 Тест Head+Foot
                                </button>
                                <button
                                  onClick={() => handleTestOtherPlayerClaim(bed.name)}
                                  className="px-2 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-amber-300 border border-neutral-700 text-left truncate cursor-pointer"
                                  title="Попытка другого игрока привязать эту же кровать"
                                >
                                  ⛔ 1 игрок на кровать
                                </button>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-1.5 pt-2 border-t border-neutral-800">
                            <button
                              onClick={() => handleExecuteRespawn(bed.name, `X: ${bed.x}, Y: ${bed.y}, Z: ${bed.z}`)}
                              className="flex-1 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1 cursor-pointer"
                              title="ЛКМ в игре: Возродиться"
                            >
                              <span>Возродиться</span>
                            </button>
                            <button
                              onClick={() => handleStartRename(bed)}
                              className="px-2 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-amber-300 font-semibold text-xs border border-neutral-700 transition-colors flex items-center gap-1 cursor-pointer"
                              title="ПКМ в игре для переименования"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                              <span className="hidden sm:inline">Имя</span>
                            </button>
                            <button
                              onClick={() => handleBreakBed(bed.id)}
                              className="px-2 py-1.5 rounded-lg bg-red-950/80 hover:bg-red-900 text-red-300 border border-red-800 transition-colors flex items-center gap-1 cursor-pointer"
                              title="Сломать кровать для проверки авто-удаления из меню"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                              <span className="text-[10px]">Сломать</span>
                            </button>
                          </div>
                        </div>
                      ))}
                      </div>
                    )}
                  </div>

                  {/* Public & Town Spawn Options */}
                  <div className="space-y-2 pt-2 border-t border-[#444]">
                    <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider px-1">
                      Дополнительные точки возрождения:
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                      {/* Town Spawn */}
                      <div
                        onClick={() => handleExecuteRespawn('Спавн Города Авалония', 'X: 160, Y: 70, Z: 210')}
                        className="p-3 rounded-xl bg-[#202020] border border-amber-500/50 hover:border-amber-400 cursor-pointer transition-all hover:bg-[#252525] group"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">🏛</span>
                          <span className="font-bold text-amber-300 text-xs font-mono">Спавн Города</span>
                        </div>
                        <div className="text-[11px] text-neutral-400 font-mono">
                          Город «Авалония» (/t spawn)
                        </div>
                        <div className="mt-2 text-[10px] text-amber-400/90 font-medium group-hover:underline">
                          ▸ Нажмите для возрождения
                        </div>
                      </div>

                      {/* Nation Spawn */}
                      <div
                        onClick={() => handleExecuteRespawn('Столица Нации', 'X: 300, Y: 72, Z: 500')}
                        className="p-3 rounded-xl bg-[#202020] border border-emerald-500/50 hover:border-emerald-400 cursor-pointer transition-all hover:bg-[#252525] group"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">👑</span>
                          <span className="font-bold text-emerald-300 text-xs font-mono">Спавн Нации</span>
                        </div>
                        <div className="text-[11px] text-neutral-400 font-mono">
                          Столица нации (/n spawn)
                        </div>
                        <div className="mt-2 text-[10px] text-emerald-400/90 font-medium group-hover:underline">
                          ▸ Нажмите для возрождения
                        </div>
                      </div>

                      {/* Vanilla Random Spawn */}
                      <div
                        onClick={() => handleExecuteRespawn('Ванильный респавн (Дикая природа)', 'X: ~450, Y: 68, Z: ~-820')}
                        className="p-3 rounded-xl bg-[#202020] border border-cyan-500/50 hover:border-cyan-400 cursor-pointer transition-all hover:bg-[#252525] group"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">🌲</span>
                          <span className="font-bold text-cyan-300 text-xs font-mono">Ванильный респавн</span>
                        </div>
                        <div className="text-[11px] text-neutral-400 font-mono">
                          Случайное место в дикой природе
                        </div>
                        <div className="mt-2 text-[10px] text-cyan-400/90 font-medium group-hover:underline">
                          ▸ Нажмите для возрождения
                        </div>
                      </div>

                      {/* Server Spawn */}
                      <div
                        onClick={() => handleExecuteRespawn('Спавн Сервера', 'X: 0, Y: 70, Z: 0')}
                        className="p-3 rounded-xl bg-[#202020] border border-yellow-500/50 hover:border-yellow-400 cursor-pointer transition-all hover:bg-[#252525] group"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">⭐</span>
                          <span className="font-bold text-yellow-300 text-xs font-mono">На спавн сервера</span>
                        </div>
                        <div className="text-[11px] text-neutral-400 font-mono">
                          Мирная охраняемая площадь
                        </div>
                        <div className="mt-2 text-[10px] text-yellow-400/90 font-medium group-hover:underline">
                          ▸ Нажмите для возрождения
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Info Footer Line in Chest */}
                  <div className="mt-4 pt-3 border-t border-[#3c3c3c] flex items-center justify-between text-[11px] text-neutral-400 font-mono">
                    <span>💡 Команда в чате: <code className="text-amber-300">/respawn rename &lt;номер&gt; &lt;имя&gt;</code></span>
                    <span className="text-emerald-400">🛡 Защита 5 сек после возрождения</span>
                  </div>
                </div>
              </div>
            )}

            {/* Bed Renaming Modal */}
            {renamingBedId && (
              <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
                <div className="bg-neutral-900 border border-neutral-700 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
                    <div className="flex items-center gap-2 text-white font-bold text-base">
                      <Edit3 className="w-5 h-5 text-amber-400" />
                      <span>Переименование кровати</span>
                    </div>
                    <button
                      onClick={() => setRenamingBedId(null)}
                      className="text-neutral-400 hover:text-white p-1"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  <p className="text-xs text-neutral-300">
                    Введите новое название для вашей точки возрождения. В игре переименование также доступно правым кликом мыши (ПКМ) или командой <code className="px-1.5 py-0.5 rounded bg-neutral-800 text-amber-300 font-mono">/respawn rename</code>.
                  </p>

                  <div>
                    <label className="block text-xs font-medium text-neutral-400 mb-1.5">
                      Новое название (до 32 символов):
                    </label>
                    <input
                      type="text"
                      value={renameInput}
                      onChange={(e) => setRenameInput(e.target.value)}
                      maxLength={32}
                      className="w-full px-4 py-2.5 rounded-xl bg-neutral-950 border border-neutral-700 text-white font-mono text-sm focus:outline-none focus:border-cyan-400"
                      placeholder="Например: Дом у озера"
                      autoFocus
                    />
                  </div>

                  <div className="flex items-center gap-3 pt-2">
                    <button
                      onClick={() => setRenamingBedId(null)}
                      className="flex-1 py-2.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-300 font-semibold text-xs transition-colors cursor-pointer"
                    >
                      Отмена
                    </button>
                    <button
                      onClick={handleSaveRename}
                      disabled={!renameInput.trim()}
                      className="flex-1 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-neutral-950 font-bold text-xs transition-colors cursor-pointer"
                    >
                      Сохранить название
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
