import React, { useState, useEffect } from 'react';
import {
  Flag,
  Swords,
  Shield,
  ShieldAlert,
  Flame,
  Tent,
  Sparkles,
  Zap,
  Play,
  Pause,
  RotateCcw,
  Plus,
  Minus,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Copy,
  Check,
  Crown,
  FastForward,
  Layers,
  Landmark,
  Compass,
  Volume2,
  Trash2,
  StopCircle,
  RefreshCw,
  Info
} from 'lucide-react';
import { soundFx } from '../utils/audioEffects';

export interface TacticalChunk {
  id: string;
  gridX: number;
  gridZ: number;
  name: string;
  initialType: 'camp' | 'wilderness' | 'town';
  initialStatus: 'town_chunk' | 'outpost' | 'wilderness';
  currentOwner: 'attacker_camp' | 'wilderness' | 'defender_town' | 'defender_outpost' | 'attacker_town' | 'attacker_outpost';
  hasBanner: boolean;
  progress: number; // -0.05 to 1.0 (0 at start, 1.0 = captured by attackers, <= 0 = counter-captured by defenders)
  attackersCount: number;
  defendersCount: number;
  bannerPlacedAt?: number;
  isOutpost?: boolean;
}

export const ChunkSiegeCaptureSimulator: React.FC = () => {
  const BASE_CAPTURE_SECONDS = 300; // 5 минут базовое время
  const [isSimRunning, setIsSimRunning] = useState<boolean>(true);
  const [speedMultiplier, setSpeedMultiplier] = useState<number>(1);
  const [selectedChunkId, setSelectedChunkId] = useState<string>('chunk_2_2');
  const [activeTab, setActiveTab] = useState<'map' | 'recipe' | 'rules'>('map');
  const [copiedRecipe, setCopiedRecipe] = useState<boolean>(false);
  const [isAssaultActive, setIsAssaultActive] = useState<boolean>(true);
  const [isCampDisbanded, setIsCampDisbanded] = useState<boolean>(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  // System Logs
  const [systemLogs, setSystemLogs] = useState<Array<{ id: string; time: string; text: string; type: 'warn' | 'danger' | 'success' | 'info' }>>([
    {
      id: 'log_0',
      time: '12:00:00',
      text: '⚔ Осадный лагерь развернут. Фаза активного штурма (2ч)! Орудия и взрывы РАЗБЛОКИРОВАНЫ.',
      type: 'warn'
    },
    {
      id: 'log_1',
      time: '12:01:15',
      text: '🚩 Штурмовой Флаг установлен на чанк [2, 2]! Запущен световой луч маяка в небо до Y=320.',
      type: 'info'
    }
  ]);

  // Initial 6x5 tactical battlefield grid
  // Col 0: Attacker Camp (Base of siege) - originally Town Chunks & Outpost of Sparta
  // Col 1-2: Borderlands / Wilderness
  // Col 3-5: Defending Town "Авалония"
  const [chunks, setChunks] = useState<TacticalChunk[]>(() => {
    const list: TacticalChunk[] = [];
    for (let z = 0; z < 5; z++) {
      for (let x = 0; x < 6; x++) {
        let initialType: 'camp' | 'wilderness' | 'town' = 'wilderness';
        let initialStatus: 'town_chunk' | 'outpost' | 'wilderness' = 'wilderness';
        let currentOwner: 'attacker_camp' | 'wilderness' | 'defender_town' | 'defender_outpost' = 'wilderness';
        let hasBanner = false;
        let progress = 0;
        let attackersCount = 0;
        let defendersCount = 0;

        if (x === 0) {
          initialType = 'camp';
          currentOwner = 'attacker_camp';
          if (z === 0 || z === 1) {
            initialStatus = 'town_chunk'; // Чанк города атаковавшего
          } else if (z === 2) {
            initialStatus = 'outpost';    // Аванпост атаковавшего
          } else {
            initialStatus = 'wilderness'; // Дикие земли
          }
        } else if (x === 1 && (z === 2 || z === 3)) {
          initialType = 'camp';
          currentOwner = 'attacker_camp';
          initialStatus = 'wilderness';
        } else if (x >= 3) {
          initialType = 'town';
          initialStatus = 'town_chunk';
          currentOwner = 'defender_town';
        } else {
          initialType = 'wilderness';
          initialStatus = 'wilderness';
          currentOwner = 'wilderness';
        }

        // Pre-activate one capture for immediate live demo
        if (x === 2 && z === 2) {
          hasBanner = true;
          progress = 0.45;
          attackersCount = 3;
          defendersCount = 1;
        }

        list.push({
          id: `chunk_${x}_${z}`,
          gridX: x,
          gridZ: z,
          name: x <= 1 ? 'Лагерь Нордгарда' : x >= 3 ? 'Город Авалония' : 'Пограничье',
          initialType,
          initialStatus,
          currentOwner,
          hasBanner,
          progress,
          attackersCount,
          defendersCount,
          isOutpost: false
        });
      }
    }
    return list;
  });

  const addLog = (text: string, type: 'warn' | 'danger' | 'success' | 'info') => {
    const timeStr = new Date().toLocaleTimeString('ru-RU');
    setSystemLogs((prev) => [{ id: `log_${Date.now()}_${Math.random()}`, time: timeStr, text, type }, ...prev.slice(0, 15)]);
  };

  const showToast = (msg: string) => {
    setActionFeedback(msg);
    setTimeout(() => setActionFeedback(null), 4500);
  };

  // Helper: Check if a chunk is adjacent (cardinal: N, S, E, W) to any attacker_camp chunk
  const isAdjacentToCamp = (chunk: TacticalChunk, chunkList = chunks): boolean => {
    const { gridX, gridZ } = chunk;
    const neighbors = [
      { x: gridX + 1, z: gridZ },
      { x: gridX - 1, z: gridZ },
      { x: gridX, z: gridZ + 1 },
      { x: gridX, z: gridZ - 1 }
    ];
    return neighbors.some((n) => {
      const neighborChunk = chunkList.find((c) => c.gridX === n.x && c.gridZ === n.z);
      return neighborChunk && neighborChunk.currentOwner === 'attacker_camp';
    });
  };

  // Helper: Check if a chunk is adjacent to the main defending town
  const isAdjacentToDefenderTown = (chunk: TacticalChunk, chunkList = chunks): boolean => {
    const { gridX, gridZ } = chunk;
    const neighbors = [
      { x: gridX + 1, z: gridZ },
      { x: gridX - 1, z: gridZ },
      { x: gridX, z: gridZ + 1 },
      { x: gridX, z: gridZ - 1 }
    ];
    return neighbors.some((n) => {
      const neighborChunk = chunkList.find((c) => c.gridX === n.x && c.gridZ === n.z);
      return neighborChunk && neighborChunk.currentOwner === 'defender_town';
    });
  };

  // Dynamic Advantage Ratio Calculation
  const getAdvantageRatio = (attackers: number, defenders: number) => {
    if (attackers > defenders) {
      if (defenders <= 0) {
        return 1.0 + (attackers - 1) * 0.35;
      }
      return Math.min(5.0, attackers / defenders);
    } else if (defenders > attackers) {
      if (attackers <= 0) {
        return 1.0 + (defenders - 1) * 0.35;
      }
      return Math.min(5.0, defenders / attackers);
    }
    return 1.0;
  };

  // Main Simulation Loop (1 second tick)
  useEffect(() => {
    if (!isSimRunning) return;

    const interval = setInterval(() => {
      setChunks((prevChunks) => {
        let changed = false;
        const next = prevChunks.map((chunk) => {
          if (!chunk.hasBanner) return chunk;

          const { attackersCount, defendersCount, progress } = chunk;
          const ratio = getAdvantageRatio(attackersCount, defendersCount);

          // Step per second
          const baseStepPerSec = 1.0 / BASE_CAPTURE_SECONDS;
          const actualStep = baseStepPerSec * ratio * speedMultiplier;

          let newProgress = progress;

          if (attackersCount > defendersCount) {
            // Attackers pushing forward
            newProgress = Math.min(1.0, progress + actualStep);
          } else if (defendersCount > attackersCount) {
            // Defenders repelling & pushing back!
            newProgress = progress - actualStep;
          }

          if (newProgress !== progress) {
            changed = true;
          }

          // Case A: Attackers reached 100% -> Chunk becomes part of Attacker Siege Camp!
          if (newProgress >= 1.0) {
            addLog(
              `⚡ ПОБЕДА ШТУРМА: Чанк [${chunk.gridX}, ${chunk.gridZ}] полностью захвачен! Теперь это часть осадного лагеря (можно ставить флаги дальше).`,
              'success'
            );
            soundFx.playTriumph();
            return {
              ...chunk,
              hasBanner: false,
              progress: 1.0,
              currentOwner: 'attacker_camp' as const,
              name: 'Захваченный Лагерь',
              attackersCount: 0,
              defendersCount: 0
            };
          }

          // Case B: Defenders rolled progress back below 0% -> Counter-Captured by Defending Town!
          if (newProgress <= 0.0 && defendersCount > attackersCount) {
            const adjacentToTown = isAdjacentToDefenderTown(chunk, prevChunks);
            const becomesOutpost = !adjacentToTown;

            if (becomesOutpost) {
              addLog(
                `🏰 ТРИУМФ ОБОРОНЫ: Чанк [${chunk.gridX}, ${chunk.gridZ}] отбит защитниками! Так как он не граничит с городом, он стал официальным АВАНПОСТОМ (Outpost) Towny!`,
                'warn'
              );
            } else {
              addLog(
                `🛡️ ТРИУМФ ОБОРОНЫ: Чанк [${chunk.gridX}, ${chunk.gridZ}] отбит и присоединен к территории города Авалония!`,
                'success'
              );
            }
            soundFx.playTriumph();

            return {
              ...chunk,
              hasBanner: false,
              progress: 0.0,
              currentOwner: (becomesOutpost ? 'defender_outpost' : 'defender_town') as 'defender_outpost' | 'defender_town',
              name: becomesOutpost ? 'Аванпост Авалонии' : 'Город Авалония',
              isOutpost: becomesOutpost,
              attackersCount: 0,
              defendersCount: 0
            };
          }

          return { ...chunk, progress: newProgress };
        });

        return changed ? next : prevChunks;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isSimRunning, speedMultiplier]);

  // Action: Place Banner on Adjacent Chunk
  const handlePlaceBanner = (chunk: TacticalChunk) => {
    if (chunk.hasBanner) return;
    if (chunk.currentOwner === 'attacker_camp') {
      addLog(`✖ Нельзя ставить штурмовой флаг на уже захваченный чанк лагеря!`, 'danger');
      return;
    }

    if (!isAdjacentToCamp(chunk)) {
      addLog(`✖ Штурмовой флаг можно ставить ТОЛЬКО на чанки, строго граничащие с осадным лагерем!`, 'danger');
      return;
    }

    // Play Beacon + Raid Horn Sound
    soundFx.playBeaconActivate();
    soundFx.playRaidHorn();

    setChunks((prev) =>
      prev.map((c) =>
        c.id === chunk.id
          ? {
              ...c,
              hasBanner: true,
              progress: 0.05,
              attackersCount: 2,
              defendersCount: 0,
              bannerPlacedAt: Date.now()
            }
          : c
      )
    );

    setSelectedChunkId(chunk.id);
    addLog(
      `🚩 ШТУРМОВОЙ ФЛАГ УСТАНОВЛЕН на чанк [${chunk.gridX}, ${chunk.gridZ}]! Раздался рог рейда, активирован луч маяка до Y=320, запущен BossBar.`,
      'warn'
    );
  };

  // Action: Modify Troops on Selected Chunk
  const handleAdjustTroops = (type: 'attackers' | 'defenders', delta: number) => {
    setChunks((prev) =>
      prev.map((c) => {
        if (c.id !== selectedChunkId) return c;
        if (type === 'attackers') {
          const next = Math.max(0, Math.min(20, c.attackersCount + delta));
          return { ...c, attackersCount: next };
        } else {
          const next = Math.max(0, Math.min(20, c.defendersCount + delta));
          return { ...c, defendersCount: next };
        }
      })
    );
  };

  // =========================================================================
  // REQUIREMENT 1 & 4: Мэр атакующего города уничтожает лагерь (/siege disband)
  // С автоматическим возвращением всех чанков в исходный статус!
  // =========================================================================
  const handleMayorDisbandCamp = () => {
    // Sound FX: Explosion + Anvil Destroy chime
    soundFx.playExplosion();
    setTimeout(() => soundFx.playAnvilChime(), 350);

    let restoredTownChunks = 0;
    let restoredOutposts = 0;
    let restoredWilderness = 0;

    setChunks((prev) =>
      prev.map((c) => {
        if (c.currentOwner === 'attacker_camp') {
          // Restore to previous status
          if (c.initialStatus === 'town_chunk') {
            restoredTownChunks++;
            return {
              ...c,
              hasBanner: false,
              progress: 0,
              attackersCount: 0,
              defendersCount: 0,
              currentOwner: 'attacker_town' as const,
              name: 'Нордгард (Городской чанк)'
            };
          } else if (c.initialStatus === 'outpost') {
            restoredOutposts++;
            return {
              ...c,
              hasBanner: false,
              progress: 0,
              attackersCount: 0,
              defendersCount: 0,
              currentOwner: 'attacker_outpost' as const,
              name: 'Нордгард (Аванпост)',
              isOutpost: true
            };
          } else {
            restoredWilderness++;
            return {
              ...c,
              hasBanner: false,
              progress: 0,
              attackersCount: 0,
              defendersCount: 0,
              currentOwner: 'wilderness' as const,
              name: 'Дикие земли'
            };
          }
        }
        // Remove any active banners on frontier
        if (c.hasBanner) {
          return { ...c, hasBanner: false, progress: 0, attackersCount: 0, defendersCount: 0 };
        }
        return c;
      })
    );

    setIsCampDisbanded(true);
    addLog(
      `💥 МЭР РАСФОРМИРОВАЛ ЛАГЕРЬ (/siege disband)! Чанки лагеря возвращены: ${restoredTownChunks} в город Нордгард, ${restoredOutposts} в официальный аванпост, ${restoredWilderness} в дикие земли. Взрывы орудий ОТКЛЮЧЕНЫ.`,
      'danger'
    );
    showToast(`✔ Мэр расформировал осадный лагерь (/siege disband)! Все чанки возвращены в исходный статус.`);
  };

  // =========================================================================
  // REQUIREMENT 3: Единая команда админа - пропустить подготовку (/siege admin skip-prep)
  // =========================================================================
  const handleAdminSkipPrep = () => {
    soundFx.playAssaultAlert();
    setIsAssaultActive(true);
    addLog(
      `⚡ АДМИНИСТРАТОР: /siege admin skip-prep! 24-часовая подготовка пропущена! Начался АКТИВНЫЙ 2-ЧАСОВОЙ ШТУРМ. Осадные орудия и взрывы РАЗБЛОКИРОВАНЫ, TownyArchitecture удвоила стойкость стен полиса.`,
      'warn'
    );
    showToast(`⚡ /siege admin skip-prep: Подготовка пропущена! 2-часовой штурм начался!`);
  };

  // Единая команда админа - завершить осаду (/siege admin end)
  const handleAdminEndSiege = () => {
    soundFx.playTriumph();
    handleMayorDisbandCamp();
    addLog(
      `⏹ АДМИНИСТРАТОР: /siege admin end! Осада досрочно завершена администратором. Все чанки возвращены в исходный статус.`,
      'info'
    );
    showToast(`⏹ /siege admin end: Осада завершена, чанки лагеря возвращены.`);
  };

  // Action: Reset Simulation to Initial Demo State
  const handleResetSimulation = () => {
    setIsCampDisbanded(false);
    setIsAssaultActive(true);
    setChunks((prev) =>
      prev.map((c) => {
        let currentOwner: 'attacker_camp' | 'wilderness' | 'defender_town' | 'defender_outpost' = 'wilderness';
        let hasBanner = false;
        let progress = 0;
        let attackersCount = 0;
        let defendersCount = 0;

        if (c.gridX === 0) {
          currentOwner = 'attacker_camp';
        } else if (c.gridX === 1 && (c.gridZ === 2 || c.gridZ === 3)) {
          currentOwner = 'attacker_camp';
        } else if (c.gridX >= 3) {
          currentOwner = 'defender_town';
        }

        if (c.gridX === 2 && c.gridZ === 2) {
          hasBanner = true;
          progress = 0.45;
          attackersCount = 3;
          defendersCount = 1;
        }

        return {
          ...c,
          currentOwner,
          hasBanner,
          progress,
          attackersCount,
          defendersCount,
          isOutpost: false,
          name: c.gridX <= 1 ? 'Лагерь Нордгарда' : c.gridX >= 3 ? 'Город Авалония' : 'Пограничье'
        };
      })
    );
    setSelectedChunkId('chunk_2_2');
    addLog('↺ Симуляция сброшена в исходное боевое состояние штурма.', 'info');
  };

  const selectedChunk = chunks.find((c) => c.id === selectedChunkId) || chunks[0];
  const ratio = getAdvantageRatio(selectedChunk.attackersCount, selectedChunk.defendersCount);

  // Time remaining estimate
  const remainingSeconds = Math.max(
    0,
    Math.round(((1.0 - selectedChunk.progress) * BASE_CAPTURE_SECONDS) / (ratio * speedMultiplier))
  );
  const remainingMinutes = Math.floor(remainingSeconds / 60);
  const remainingSecs = remainingSeconds % 60;

  // Rollback time estimate (if defenders outnumber)
  const rollbackSeconds = Math.max(
    0,
    Math.round((selectedChunk.progress * BASE_CAPTURE_SECONDS) / (ratio * speedMultiplier))
  );

  return (
    <div className="w-full space-y-6">
      {/* Toast Feedback */}
      {actionFeedback && (
        <div className="p-3.5 rounded-xl bg-cyan-950/90 border border-cyan-500/50 text-cyan-200 text-sm flex items-center gap-2.5 shadow-xl animate-fade-in">
          <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{actionFeedback}</span>
        </div>
      )}

      {/* Main Header & Sub-Navigation */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-red-500/20 text-red-300 border border-red-500/40 flex items-center gap-1.5">
              <Flag className="w-3.5 h-3.5 text-red-400" />
              <span>Штурм & Почанковый Захват</span>
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
              TownySieges v1.5.0
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              Автовозврат чанков
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2.5">
            <span>Почанковый Захват & Возврат Чанков Осадного Лагеря</span>
          </h2>
          <p className="text-sm text-neutral-300 mt-2 max-w-3xl leading-relaxed">
            Атакующие ставят <strong>Штурмовой Флаг</strong> с лучом маяка на смежные чанки.
            При завершении осады или команде мэра <code className="px-1.5 py-0.5 rounded bg-neutral-800 text-amber-300 font-mono text-xs">/siege disband</code> все чанки лагеря <strong>автоматически возвращаются в исходный статус</strong> (город, аванпост или дикие земли)!
          </p>
        </div>

        {/* View mode buttons */}
        <div className="flex items-center gap-2 shrink-0 flex-wrap">
          <button
            onClick={() => setActiveTab('map')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'map'
                ? 'bg-red-500 text-neutral-950 shadow-lg shadow-red-500/20'
                : 'bg-neutral-800 text-neutral-300 hover:text-white'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Карта Штурма</span>
          </button>
          <button
            onClick={() => setActiveTab('recipe')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'recipe'
                ? 'bg-amber-500 text-neutral-950 shadow-lg shadow-amber-500/20'
                : 'bg-neutral-800 text-neutral-300 hover:text-white'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Крафт Флага (3x3)</span>
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'rules'
                ? 'bg-cyan-500 text-neutral-950 shadow-lg shadow-cyan-500/20'
                : 'bg-neutral-800 text-neutral-300 hover:text-white'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            <span>Правила & Команды</span>
          </button>
        </div>
      </div>

      {activeTab === 'map' && (
        <>
          {/* Action Command Bar: Mayor & Admin Controls */}
          <div className="bg-neutral-950 p-4 rounded-2xl border border-neutral-800 shadow-xl flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400 font-mono flex items-center gap-1.5">
                <Crown className="w-3.5 h-3.5 text-amber-400" />
                <span>Команды Мэра & Админа:</span>
              </span>

              {/* Mayor Disband Button */}
              <button
                onClick={handleMayorDisbandCamp}
                disabled={isCampDisbanded}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-md ${
                  isCampDisbanded
                    ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed opacity-50'
                    : 'bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 text-white shadow-red-950/50'
                }`}
                title="Мэр атакующего города стоя на чанке уничтожает лагерь с возвратом всех чанков в исходное состояние"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>/siege disband (Мэр: Уничтожить лагерь)</span>
              </button>

              {/* Admin Skip-Prep Button */}
              <button
                onClick={handleAdminSkipPrep}
                className="px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-neutral-950 transition-all flex items-center gap-1.5 cursor-pointer shadow-md shadow-amber-500/20"
                title="Пропустить 24-часовую подготовку и мгновенно активировать 2-часовой штурм"
              >
                <FastForward className="w-3.5 h-3.5" />
                <span>/siege admin skip-prep</span>
              </button>

              {/* Admin End Siege Button */}
              <button
                onClick={handleAdminEndSiege}
                className="px-3 py-1.5 rounded-xl text-xs font-bold bg-neutral-800 hover:bg-neutral-700 text-neutral-200 transition-all flex items-center gap-1.5 cursor-pointer border border-neutral-700"
                title="Завершить осаду и восстановить чанки"
              >
                <StopCircle className="w-3.5 h-3.5 text-red-400" />
                <span>/siege admin end</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold border ${
                isCampDisbanded
                  ? 'bg-neutral-900 text-neutral-400 border-neutral-800'
                  : 'bg-red-950/60 text-red-300 border-red-500/40 animate-pulse'
              }`}>
                {isCampDisbanded ? 'ЛАГЕРЬ РАСФОРМИРОВАН' : 'АКТИВНЫЙ ШТУРМ (2 ЧАСА)'}
              </span>
            </div>
          </div>

          {/* Minecraft Paper In-Game BossBar Replica */}
          <div className="bg-neutral-950 p-4 rounded-2xl border border-neutral-800 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-2">
              <span className="flex items-center gap-2 font-bold text-neutral-200">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
                <span>Paper In-Game BossBar (Видят все бойцы на захватываемом чанке):</span>
              </span>
              <span className="text-[11px] text-neutral-400">Цвет: RED | Стиль: PROGRESS_NOTCHED_10</span>
            </div>

            {selectedChunk.hasBanner ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm sm:text-base font-bold text-white flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <Flag className="w-4 h-4 text-red-400 animate-bounce" />
                    <span>
                      ШТУРМ ЧАНКА [{selectedChunk.gridX}, {selectedChunk.gridZ}]
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-neutral-800 text-neutral-300 font-mono">
                      {selectedChunk.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs sm:text-sm font-mono">
                    <span className="text-red-400 font-bold">⚔️ {selectedChunk.attackersCount} Атак.</span>
                    <span className="text-neutral-500">vs</span>
                    <span className="text-blue-400 font-bold">🛡️ {selectedChunk.defendersCount} Защит.</span>
                    <span className="text-amber-400 font-black">
                      ({Math.round(selectedChunk.progress * 100)}%)
                    </span>
                  </div>
                </div>

                {/* Simulated Minecraft BossBar Track */}
                <div className="w-full h-4 bg-neutral-900 rounded-md overflow-hidden border border-neutral-700/80 relative">
                  <div
                    className="h-full bg-gradient-to-r from-red-600 via-amber-500 to-red-500 transition-all duration-300 relative"
                    style={{ width: `${Math.max(0, Math.min(100, selectedChunk.progress * 100))}%` }}
                  >
                    <div className="absolute inset-0 bg-white/10 animate-pulse pointer-events-none" />
                  </div>
                  {/* Segment notches (Paper 10-notches style) */}
                  <div className="absolute inset-0 flex justify-between pointer-events-none px-1">
                    {[...Array(9)].map((_, i) => (
                      <div key={i} className="w-[1px] h-full bg-neutral-950/80" />
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400">
                  <span>
                    Коэффициент перевеса: <strong className="text-white">{ratio.toFixed(2)}x</strong> (
                    {selectedChunk.attackersCount > selectedChunk.defendersCount
                      ? 'Ускорение штурма'
                      : selectedChunk.defendersCount > selectedChunk.attackersCount
                      ? 'Откат прогресса защитниками'
                      : 'Базовая скорость'}
                    )
                  </span>
                  <span>
                    {selectedChunk.attackersCount > selectedChunk.defendersCount ? (
                      <span className="text-emerald-400">
                        До победы: ~{remainingMinutes}м {remainingSecs}с
                      </span>
                    ) : selectedChunk.defendersCount > selectedChunk.attackersCount ? (
                      <span className="text-cyan-400">
                        До отката в Аванпост: ~{Math.floor(rollbackSeconds / 60)}м {rollbackSeconds % 60}с
                      </span>
                    ) : (
                      <span className="text-amber-400">Баланс сил на чанке</span>
                    )}
                  </span>
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-neutral-900/60 border border-neutral-800 text-center text-xs text-neutral-400">
                На выбранном чанке нет активного штурмового флага. Кликните по любому чанку со значком <strong>[+]</strong>, чтобы поставить флаг!
              </div>
            )}
          </div>

          {/* Interactive Tactical Grid & Live Controls */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Grid 6x5 View (2 Cols) */}
            <div className="lg:col-span-2 bg-neutral-950 p-5 rounded-2xl border border-neutral-800">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-neutral-800 flex-wrap gap-2">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span>Тактическая Сетка Чанков (6x5 Battlefield)</span>
                  </h3>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Колонка 0: Лагерь Нордгарда | Колонка 1-2: Пограничье | Колонка 3-5: Город Авалония
                  </p>
                </div>

                {/* Legend badges */}
                <div className="flex items-center gap-2 text-[10px] font-mono flex-wrap">
                  <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-500/40">
                    Осадный лагерь
                  </span>
                  <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/40">
                    Город
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    Аванпост
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    Возвращён
                  </span>
                  <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/40 animate-pulse">
                    Флаг & Луч
                  </span>
                </div>
              </div>

              {/* Grid 6 columns x 5 rows */}
              <div className="overflow-x-auto pb-2">
                <div className="grid grid-cols-6 gap-2 min-w-[560px]">
                  {chunks.map((chunk) => {
                    const isCamp = chunk.currentOwner === 'attacker_camp';
                    const isTown = chunk.currentOwner === 'defender_town';
                    const isOutpost = chunk.currentOwner === 'defender_outpost';
                    const isAttackerTown = chunk.currentOwner === 'attacker_town';
                    const isAttackerOutpost = chunk.currentOwner === 'attacker_outpost';
                    const isAdjacent = isAdjacentToCamp(chunk);
                    const isSelected = selectedChunk?.id === chunk.id;

                    return (
                      <div
                        key={chunk.id}
                        onClick={() => {
                          if (chunk.hasBanner) {
                            setSelectedChunkId(chunk.id);
                          } else if (isAdjacent && !isCamp && !isCampDisbanded) {
                            handlePlaceBanner(chunk);
                          } else {
                            setSelectedChunkId(chunk.id);
                          }
                        }}
                        className={`relative rounded-xl p-2.5 min-h-[96px] sm:min-h-[108px] border-2 transition-all flex flex-col justify-between cursor-pointer ${
                          isSelected ? 'ring-2 ring-white ring-offset-2 ring-offset-neutral-950 scale-[1.02]' : ''
                        } ${
                          isCamp
                            ? 'bg-gradient-to-br from-orange-950/80 to-neutral-900 border-orange-500/80 text-orange-200'
                            : isAttackerTown
                            ? 'bg-gradient-to-br from-emerald-950/80 to-neutral-900 border-emerald-500/80 text-emerald-200 shadow-lg'
                            : isAttackerOutpost
                            ? 'bg-gradient-to-br from-teal-950/90 to-cyan-950/50 border-teal-400 text-teal-200 shadow-lg'
                            : isOutpost
                            ? 'bg-gradient-to-br from-amber-950/90 to-yellow-950/40 border-amber-400 text-amber-200 shadow-lg shadow-amber-950/50'
                            : isTown
                            ? 'bg-gradient-to-br from-blue-950/80 to-neutral-900 border-blue-600/80 text-blue-200'
                            : isAdjacent && !isCampDisbanded
                            ? 'bg-neutral-900/90 border-dashed border-red-500/60 hover:border-red-400 text-neutral-300 hover:bg-red-950/20'
                            : 'bg-neutral-900/40 border-neutral-800/80 text-neutral-500 opacity-70'
                        }`}
                      >
                        {/* Vertical Beacon Beam Animation if Banner is Active */}
                        {chunk.hasBanner && (
                          <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
                            <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-3 bg-gradient-to-t from-cyan-400 via-sky-300 to-white opacity-80 blur-[2px] animate-pulse" />
                            <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-8 bg-cyan-400/20 blur-md pointer-events-none" />
                          </div>
                        )}

                        {/* Top coordinate & tag */}
                        <div className="flex items-center justify-between text-[11px] font-mono relative z-10">
                          <span className="font-bold opacity-80">
                            [{chunk.gridX},{chunk.gridZ}]
                          </span>
                          {chunk.hasBanner ? (
                            <span className="flex items-center gap-1 px-1.5 py-0.2 rounded bg-red-600 text-white font-black text-[9px] shadow animate-pulse">
                              <Flag className="w-2.5 h-2.5" /> ФЛАГ
                            </span>
                          ) : isCamp ? (
                            <span className="px-1.5 py-0.2 rounded bg-orange-600/80 text-white font-bold text-[9px]">
                              ЛАГЕРЬ
                            </span>
                          ) : isAttackerTown ? (
                            <span className="px-1.5 py-0.2 rounded bg-emerald-600 text-white font-bold text-[9px]">
                              ГОРОД
                            </span>
                          ) : isAttackerOutpost ? (
                            <span className="px-1.5 py-0.2 rounded bg-teal-600 text-white font-bold text-[9px]">
                              АВАНПОСТ
                            </span>
                          ) : isOutpost ? (
                            <span className="px-1.5 py-0.2 rounded bg-amber-500 text-neutral-950 font-black text-[9px]">
                              OUTPOST
                            </span>
                          ) : isTown ? (
                            <span className="px-1.5 py-0.2 rounded bg-blue-600/80 text-white font-bold text-[9px]">
                              ГОРОД
                            </span>
                          ) : isAdjacent && !isCampDisbanded ? (
                            <span className="px-1.5 py-0.2 rounded bg-red-950/80 text-red-300 border border-red-500/40 text-[9px] font-bold">
                              + СМЕЖНЫЙ
                            </span>
                          ) : null}
                        </div>

                        {/* Middle: Active Capture Progress or State */}
                        <div className="relative z-10 my-1">
                          {chunk.hasBanner ? (
                            <div>
                              <div className="flex items-center justify-between text-[10px] font-mono mb-1 font-bold">
                                <span className="text-red-400">⚔️{chunk.attackersCount}</span>
                                <span className="text-amber-300 font-black">
                                  {Math.round(chunk.progress * 100)}%
                                </span>
                                <span className="text-blue-400">🛡️{chunk.defendersCount}</span>
                              </div>
                              <div className="w-full h-1.5 bg-neutral-950 rounded-full overflow-hidden border border-neutral-800">
                                <div
                                  className="h-full bg-gradient-to-r from-red-500 to-amber-400 transition-all duration-300"
                                  style={{ width: `${Math.max(0, Math.min(100, chunk.progress * 100))}%` }}
                                />
                              </div>
                            </div>
                          ) : isCamp ? (
                            <div className="text-[10px] text-orange-300 font-mono flex items-center gap-1">
                              <Tent className="w-3 h-3 text-orange-400 shrink-0" />
                              <span className="truncate">База лагеря</span>
                            </div>
                          ) : isAttackerTown ? (
                            <div className="text-[10px] text-emerald-300 font-mono flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                              <span className="truncate">Возвращён городу</span>
                            </div>
                          ) : isAttackerOutpost ? (
                            <div className="text-[10px] text-teal-300 font-mono flex items-center gap-1">
                              <Landmark className="w-3 h-3 text-teal-400 shrink-0" />
                              <span className="truncate">Возвращён в аванпост</span>
                            </div>
                          ) : isOutpost ? (
                            <div className="text-[10px] text-amber-300 font-mono flex items-center gap-1 font-bold">
                              <Landmark className="w-3 h-3 text-amber-400 shrink-0" />
                              <span className="truncate">Towny Outpost</span>
                            </div>
                          ) : isAdjacent && !isCampDisbanded ? (
                            <div className="text-[10px] text-red-300 font-mono flex items-center gap-1">
                              <Plus className="w-3 h-3 text-red-400" />
                              <span>Поставить флаг</span>
                            </div>
                          ) : (
                            <div className="text-[10px] text-neutral-400 font-mono truncate">
                              {chunk.name}
                            </div>
                          )}
                        </div>

                        {/* Bottom: Initial chunk status tag */}
                        <div className="relative z-10 text-[9px] font-mono text-neutral-400 border-t border-white/5 pt-1 flex items-center justify-between">
                          <span className="opacity-70">
                            {chunk.initialStatus === 'town_chunk'
                              ? '🏛 Чанк города'
                              : chunk.initialStatus === 'outpost'
                              ? '🚩 Аванпост'
                              : '🌲 Дикие земли'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Bottom Instructions / Hint Bar */}
              <div className="mt-4 p-3 bg-neutral-900/80 rounded-xl border border-neutral-800 flex items-center justify-between text-xs text-neutral-300 flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>
                    Кликните по смежному чанку, чтобы <strong>установить Штурмовой Флаг</strong>.
                    Все чанки лагеря сохраняют исходный статус и возвращаются при <strong>/siege disband</strong>!
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsSimRunning(!isSimRunning)}
                    className="p-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-white cursor-pointer"
                    title={isSimRunning ? 'Пауза' : 'Старт'}
                  >
                    {isSimRunning ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
                  </button>
                  <button
                    onClick={() => setSpeedMultiplier(speedMultiplier === 1 ? 3 : 1)}
                    className="px-2 py-1 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-amber-300 font-mono text-[11px] cursor-pointer"
                  >
                    {speedMultiplier}x темп
                  </button>
                  <button
                    onClick={handleResetSimulation}
                    className="p-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-white cursor-pointer"
                    title="Сброс"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Sidebar: Selected Chunk Assault Controls & Real-Time Ratio */}
            <div className="bg-neutral-950 p-5 rounded-2xl border border-neutral-800 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-neutral-800">
                  <div className="flex items-center gap-2">
                    <Flag className="w-4 h-4 text-red-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                      Инспектор Чанка [{selectedChunk.gridX}, {selectedChunk.gridZ}]
                    </h3>
                  </div>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-300">
                    {selectedChunk.id}
                  </span>
                </div>

                {/* Status card */}
                <div className="space-y-3">
                  <div className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-xs space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-neutral-400">Название:</span>
                      <strong className="text-white">{selectedChunk.name}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-400">Владелец:</span>
                      <strong className="font-mono text-cyan-300">
                        {selectedChunk.currentOwner === 'attacker_camp'
                          ? 'Осадный лагерь Нордгарда'
                          : selectedChunk.currentOwner === 'attacker_town'
                          ? 'Город Нордгард (Возвращён)'
                          : selectedChunk.currentOwner === 'attacker_outpost'
                          ? 'Аванпост Нордгарда (Возвращён)'
                          : selectedChunk.currentOwner === 'defender_outpost'
                          ? 'Официальный Outpost Towny'
                          : selectedChunk.currentOwner === 'defender_town'
                          ? 'Город Авалония'
                          : 'Дикие земли (Wilderness)'}
                      </strong>
                    </div>
                    <div className="flex justify-between items-center pt-1 border-t border-neutral-800">
                      <span className="text-neutral-400">Исходный статус:</span>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                        selectedChunk.initialStatus === 'town_chunk'
                          ? 'bg-blue-950 text-blue-300 border border-blue-500/30'
                          : selectedChunk.initialStatus === 'outpost'
                          ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                          : 'bg-neutral-800 text-neutral-300'
                      }`}>
                        {selectedChunk.initialStatus === 'town_chunk'
                          ? 'Чанк города (TOWN_CHUNK)'
                          : selectedChunk.initialStatus === 'outpost'
                          ? 'Аванпост (OUTPOST)'
                          : 'Дикие земли (WILDERNESS)'}
                      </span>
                    </div>
                    <div className="text-[11px] text-neutral-400 italic pt-1">
                      ℹ При /siege disband или завершении осады этот чанк вернётся в этот статус!
                    </div>
                  </div>

                  {selectedChunk.hasBanner ? (
                    <>
                      {/* Attacker Troops Controls */}
                      <div className="p-3 rounded-xl bg-red-950/30 border border-red-500/30 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-red-300 flex items-center gap-1.5">
                            <Swords className="w-3.5 h-3.5" />
                            <span>Атакующие на чанке:</span>
                          </span>
                          <span className="text-sm font-mono font-black text-white">
                            {selectedChunk.attackersCount} бойцов
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleAdjustTroops('attackers', -1)}
                            className="flex-1 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white font-mono font-bold text-xs flex items-center justify-center gap-1 border border-neutral-700 cursor-pointer"
                          >
                            <Minus className="w-3 h-3" /> 1
                          </button>
                          <button
                            onClick={() => handleAdjustTroops('attackers', 1)}
                            className="flex-1 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-mono font-bold text-xs flex items-center justify-center gap-1 shadow-md shadow-red-600/30 cursor-pointer"
                          >
                            <Plus className="w-3 h-3" /> 1
                          </button>
                        </div>
                      </div>

                      {/* Defender Troops Controls */}
                      <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-500/30 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-blue-300 flex items-center gap-1.5">
                            <Shield className="w-3.5 h-3.5" />
                            <span>Защитники на чанке:</span>
                          </span>
                          <span className="text-sm font-mono font-black text-white">
                            {selectedChunk.defendersCount} бойцов
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleAdjustTroops('defenders', -1)}
                            className="flex-1 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white font-mono font-bold text-xs flex items-center justify-center gap-1 border border-neutral-700 cursor-pointer"
                          >
                            <Minus className="w-3 h-3" /> 1
                          </button>
                          <button
                            onClick={() => handleAdjustTroops('defenders', 1)}
                            className="flex-1 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-mono font-bold text-xs flex items-center justify-center gap-1 shadow-md shadow-blue-600/30 cursor-pointer"
                          >
                            <Plus className="w-3 h-3" /> 1
                          </button>
                        </div>
                      </div>

                      {/* Advantage Formula Card */}
                      <div className="p-3.5 rounded-xl bg-neutral-900 border border-neutral-800 space-y-2">
                        <div className="flex items-center justify-between text-xs font-mono">
                          <span className="text-neutral-400">Перевес сил (Ratio):</span>
                          <span className="text-amber-400 font-black">{ratio.toFixed(2)}x</span>
                        </div>
                        <div className="w-full bg-neutral-950 p-2 rounded-lg text-[11px] font-mono text-neutral-300">
                          {selectedChunk.attackersCount > selectedChunk.defendersCount ? (
                            <span className="text-emerald-400">
                              Штурм ускорен: {selectedChunk.attackersCount} ÷ {Math.max(1, selectedChunk.defendersCount)} = {ratio.toFixed(2)}x
                            </span>
                          ) : selectedChunk.defendersCount > selectedChunk.attackersCount ? (
                            <span className="text-cyan-400">
                              Откат защитниками: {selectedChunk.defendersCount} ÷ {Math.max(1, selectedChunk.attackersCount)} = {ratio.toFixed(2)}x
                            </span>
                          ) : (
                            <span className="text-amber-300">Равновесие (1.00x базовая скорость)</span>
                          )}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="p-4 rounded-xl bg-neutral-900/60 border border-neutral-800 text-center space-y-3">
                      <p className="text-xs text-neutral-400">
                        Штурмовой флаг не установлен. Установите его, если чанк граничит с осадным лагерем.
                      </p>
                      {isAdjacentToCamp(selectedChunk) && selectedChunk.currentOwner !== 'attacker_camp' && !isCampDisbanded && (
                        <button
                          onClick={() => handlePlaceBanner(selectedChunk)}
                          className="w-full py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-red-600/20 cursor-pointer"
                        >
                          <Flag className="w-3.5 h-3.5" />
                          <span>Поставить Штурмовой Флаг</span>
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Bottom Quick Command Helper */}
              <div className="mt-4 pt-3 border-t border-neutral-800 text-[11px] text-neutral-400 font-mono flex items-center justify-between">
                <span>Команда выдачи:</span>
                <code className="text-amber-400 bg-neutral-900 px-1.5 py-0.5 rounded">
                  /siege banner give
                </code>
              </div>
            </div>
          </div>

          {/* Real-Time Combat & System Log */}
          <div className="bg-neutral-950 p-4 rounded-2xl border border-neutral-800">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-neutral-800">
              <h4 className="text-xs font-bold text-neutral-300 uppercase tracking-wider font-mono flex items-center gap-2">
                <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Журнал Событий Штурма & Синхронизации Плагинов:</span>
              </h4>
              <span className="text-[11px] font-mono text-neutral-500">Live Paper Broadcasts</span>
            </div>
            <div className="space-y-1.5 max-h-36 overflow-y-auto font-mono text-xs pr-1">
              {systemLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-2 text-neutral-300">
                  <span className="text-neutral-500 shrink-0">[{log.time}]</span>
                  <span
                    className={
                      log.type === 'warn'
                        ? 'text-amber-300'
                        : log.type === 'danger'
                        ? 'text-red-400 font-bold'
                        : log.type === 'success'
                        ? 'text-emerald-300'
                        : 'text-cyan-300'
                    }
                  >
                    {log.text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* TAB 2: Crafting Recipe (3x3 Workbench) */}
      {activeTab === 'recipe' && (
        <div className="bg-neutral-950 p-6 sm:p-8 rounded-2xl border border-neutral-800 shadow-xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-400" />
                <span>Рецепт 3x3 на Верстаке: ⚔ Штурмовой Флаг Осады</span>
              </h3>
              <p className="text-xs sm:text-sm text-neutral-400 mt-1">
                Кастомный предмет в TownySieges (NBT <code className="text-amber-300">siege_banner: assault_v1</code>). Создается перед штурмом на обычном верстаке.
              </p>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText('/siege banner give');
                setCopiedRecipe(true);
                setTimeout(() => setCopiedRecipe(false), 2000);
              }}
              className="px-4 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-mono font-bold transition-all flex items-center gap-2 self-start cursor-pointer border border-neutral-700"
            >
              {copiedRecipe ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedRecipe ? 'Скопировано!' : '/siege banner give'}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            {/* 3x3 Workbench Grid Visual */}
            <div className="bg-neutral-900 p-6 rounded-2xl border-2 border-neutral-800 max-w-sm mx-auto w-full shadow-2xl">
              <div className="text-center font-mono text-xs font-bold text-neutral-400 mb-4 uppercase tracking-wider">
                Сетка крафта 3 × 3 (Crafting Table)
              </div>
              <div className="grid grid-cols-3 gap-3">
                {/* Row 1 */}
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-amber-500/50 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🪙</span>
                  <span className="text-[10px] font-mono text-amber-300 font-bold mt-1">Золотой слиток</span>
                </div>
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-red-500/50 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🧨</span>
                  <span className="text-[10px] font-mono text-red-300 font-bold mt-1">TNT (Динамит)</span>
                </div>
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-amber-500/50 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🪙</span>
                  <span className="text-[10px] font-mono text-amber-300 font-bold mt-1">Золотой слиток</span>
                </div>

                {/* Row 2 */}
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-amber-500/50 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🪙</span>
                  <span className="text-[10px] font-mono text-amber-300 font-bold mt-1">Золотой слиток</span>
                </div>
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-red-500/80 ring-2 ring-red-500/30 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🚩</span>
                  <span className="text-[10px] font-mono text-red-400 font-black mt-1">Красный флаг</span>
                </div>
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-amber-500/50 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🪙</span>
                  <span className="text-[10px] font-mono text-amber-300 font-bold mt-1">Золотой слиток</span>
                </div>

                {/* Row 3 */}
                <div className="aspect-square rounded-xl bg-neutral-950 border border-neutral-800 flex items-center justify-center text-neutral-600 text-xs font-mono">
                  Пусто
                </div>
                <div className="aspect-square rounded-xl bg-neutral-950 border-2 border-orange-500/60 flex flex-col items-center justify-center p-2 text-center shadow-inner">
                  <span className="text-2xl">🔥</span>
                  <span className="text-[10px] font-mono text-orange-300 font-bold mt-1">Стержень ифрита</span>
                </div>
                <div className="aspect-square rounded-xl bg-neutral-950 border border-neutral-800 flex items-center justify-center text-neutral-600 text-xs font-mono">
                  Пусто
                </div>
              </div>
            </div>

            {/* Recipe Details & Output item description */}
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/40">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-red-500/20 text-red-400 text-2xl">
                    🚩
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-white">⚔ Штурмовой Флаг Осады (Assault Banner)</h4>
                    <p className="text-xs text-neutral-300 mt-0.5">
                      100% нестакаемый предмет. Издаёт рейд-горн и запускает маяк на Y=320.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-xs text-neutral-300">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Необходимые материалы:</strong> 4x Золотых слитка, 1x TNT, 1x Красный флаг, 1x Стержень ифрита (Blaze Rod).
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Условия установки:</strong> Игрок атакующей стороны ставит флаг на землю во время 2-часового активного штурма на чанк диких земель или атакуемого города, <em>строго смежный</em> с лагерем.
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Автоматический возврат:</strong> Если лагерь уничтожен мэром командой <code className="text-amber-300">/siege disband</code>, все чанки мгновенно возвращаются в исходный статус (город, аванпост, дикие земли).
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Rules & Mechanics */}
      {activeTab === 'rules' && (
        <div className="bg-neutral-950 p-6 sm:p-8 rounded-2xl border border-neutral-800 shadow-xl space-y-6">
          <div>
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-cyan-400" />
              <span>Правила Почанкового Захвата & Автоматического Возврата Чанков</span>
            </h3>
            <p className="text-xs sm:text-sm text-neutral-400 mt-1">
              Полный регламент работы механики в TownySieges v1.5.0
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-neutral-300">
            <div className="p-5 rounded-2xl bg-neutral-900 border border-neutral-800 space-y-3">
              <h4 className="text-base font-bold text-amber-400 flex items-center gap-2">
                <Landmark className="w-4 h-4" />
                <span>1. Автовозврат чанков осадного лагеря</span>
              </h4>
              <p className="text-xs text-neutral-300 leading-relaxed">
                Чанки осадного лагеря создаются из 3 источников:
              </p>
              <ul className="text-xs space-y-1.5 list-disc list-inside text-neutral-400 font-mono">
                <li><strong className="text-white">TOWN_CHUNK:</strong> регулярный чанк атакующего города</li>
                <li><strong className="text-white">OUTPOST:</strong> официальный аванпост атакующего города</li>
                <li><strong className="text-white">WILDERNESS:</strong> ничейные дикие земли</li>
              </ul>
              <p className="text-xs text-neutral-300 leading-relaxed">
                После завершения осады и штурма (независимо от результата — победа, поражение, ничья или таймер), а также при уничтожении лагеря мэром, <strong>каждый чанк автоматически возвращается в свой точный исходный статус</strong>!
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-neutral-900 border border-neutral-800 space-y-3">
              <h4 className="text-base font-bold text-red-400 flex items-center gap-2">
                <Crown className="w-4 h-4" />
                <span>2. Уничтожение лагеря Мэром (/siege disband)</span>
              </h4>
              <p className="text-xs text-neutral-300 leading-relaxed">
                Мэр атакующего города, <strong>физически стоя на любом чанке своего осадного лагеря</strong>, может в любой момент 24ч подготовки или 2ч штурма расформировать лагерь.
              </p>
              <div className="p-2.5 rounded-lg bg-neutral-950 font-mono text-xs text-amber-300">
                /siege disband (или /siege destroy, /siege cancel)
              </div>
              <p className="text-xs text-neutral-400 leading-relaxed">
                При вводе команды лагерь немедленно снимается, штурмовые флаги удаляются, лучи маяков гаснут, а все территории возвращаются в исходный статус.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-neutral-900 border border-neutral-800 space-y-3">
              <h4 className="text-base font-bold text-cyan-400 flex items-center gap-2">
                <FastForward className="w-4 h-4" />
                <span>3. Единые Админские Команды (/siege admin)</span>
              </h4>
              <p className="text-xs text-neutral-300 leading-relaxed">
                Администраторы могут управлять фазами осад через единый командный интерфейс:
              </p>
              <div className="space-y-1.5 font-mono text-xs">
                <div className="p-2 rounded bg-neutral-950 text-cyan-300">
                  /siege admin skip-prep [город|нация]
                  <div className="text-[10px] text-neutral-400 mt-0.5 font-sans">
                    Мгновенно пропускает 24ч подготовку и начинает 2ч активный штурм!
                  </div>
                </div>
                <div className="p-2 rounded bg-neutral-950 text-rose-300">
                  /siege admin end [город|нация]
                  <div className="text-[10px] text-neutral-400 mt-0.5 font-sans">
                    Досрочно завершает осаду с автоматическим возвратом всех чанков.
                  </div>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-neutral-900 border border-neutral-800 space-y-3">
              <h4 className="text-base font-bold text-emerald-400 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                <span>4. Синхронизация 3-х плагинов (Suite Sync)</span>
              </h4>
              <p className="text-xs text-neutral-300 leading-relaxed">
                Все плагины работают как единый организм через статический API и Bukkit Events:
              </p>
              <ul className="text-xs space-y-1 text-neutral-400">
                <li>• <strong>TownySieges:</strong> координатор таймеров, почанкового захвата и статусов чанков.</li>
                <li>• <strong>TownyExplosionUnblocker:</strong> мгновенно открывает/закрывает разрушения от артиллерии при смене фазы штурма.</li>
                <li>• <strong>TownyArchitecture:</strong> мгновенно применяет 2x стойкость City Wall и активирует военные бонусы казарм.</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
