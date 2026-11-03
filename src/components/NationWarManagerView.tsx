import React, { useState, useEffect } from 'react';
import {
  Crown,
  Flame,
  Shield,
  ShieldAlert,
  Swords,
  Timer,
  FastForward,
  Play,
  Pause,
  RotateCcw,
  Tent,
  Bomb,
  Landmark,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  ExternalLink,
  ChevronRight,
  Crosshair
} from 'lucide-react';
import {
  Nation,
  NationTown,
  NationWarPhase,
  NationWarSession,
  SiegeCampWarLink,
  INITIAL_NATIONS,
  formatTimeHoursMinutesSeconds
} from '../data/nationWarData';
import { soundFx } from '../utils/audioEffects';

interface NationWarManagerViewProps {
  onSelectTownOnMap?: (townId: string) => void;
  onOpenBlueMapWithWar?: () => void;
}

export const NationWarManagerView: React.FC<NationWarManagerViewProps> = ({
  onSelectTownOnMap,
  onOpenBlueMapWithWar
}) => {
  const [nations, setNations] = useState<Nation[]>(INITIAL_NATIONS);

  // Active War State
  const [warSession, setWarSession] = useState<NationWarSession>({
    id: 'war_north_south_session',
    attackerNationId: 'north_alliance',
    defenderNationId: 'south_league',
    declaredByLeader: 'Yaroslav_Great',
    phase: 'PREPARATION',
    preparationTotalSeconds: 86400, // 24 hours
    assaultTotalSeconds: 7200,      // 2 hours
    remainingSeconds: 86400 - 320,  // active countdown
    isTickerPaused: false,
    activeCamps: [
      {
        id: 'camp_1',
        attackerTownName: 'Нордгард',
        defenderTownName: 'Авалония',
        attackerNationId: 'north_alliance',
        defenderNationId: 'south_league',
        placedAt: Date.now() - 320000,
        claimedChunks: 4,
        locationName: 'Фронт долины Нордгард-Авалония',
        mapPercentX: 42,
        mapPercentY: 48
      }
    ],
    explosionCasualties: 0,
    blocksDestroyedTotal: 0
  });

  const [notificationToast, setNotificationToast] = useState<{
    type: 'success' | 'danger' | 'warn' | 'info';
    title: string;
    message: string;
  } | null>({
    type: 'warn',
    title: 'Единый таймер подготовки',
    message: 'Все 6 городов обеих наций переведены в режим подготовки к штурму (единый таймер 24 ч).'
  });

  const [combatLogs, setCombatLogs] = useState<
    { id: string; time: string; text: string; type: 'warn' | 'danger' | 'info' | 'success' }[]
  >([
    {
      id: 'log_1',
      time: '12:00:00',
      text: '👑 Глава Северного Альянса (Yaroslav_Great) объявил войну Южной Лиге (/nation war declare Южная_Лига)!',
      type: 'warn'
    },
    {
      id: 'log_2',
      time: '12:00:01',
      text: '⏳ Все города обеих наций (Новгород, Нордгард, Валгалла, Авалония, Китеж-Град, Солнцедар) синхронизированы под ЕДИНЫЙ 24-часовой таймер подготовки к штурму.',
      type: 'info'
    },
    {
      id: 'log_3',
      time: '12:05:20',
      text: '⛺ Город Нордгард разбил осадный лагерь против Авалонии. Осада не начала отдельный таймер — лагерь синхронизирован с единым таймером нации!',
      type: 'success'
    }
  ]);

  // Second-by-second countdown ticker
  useEffect(() => {
    if (warSession.phase === 'PEACE' || warSession.phase === 'COMPLETED' || warSession.isTickerPaused) {
      return;
    }

    const interval = setInterval(() => {
      setWarSession((prev) => {
        if (prev.remainingSeconds <= 1) {
          if (prev.phase === 'PREPARATION') {
            // Transition from 24h PREPARATION to 2h ACTIVE_ASSAULT
            soundFx.playAssaultAlert();
            addLog(
              '⚡ 24 ЧАСА ПОДГОТОВКИ ИСТЕКЛИ! НАЧАЛСЯ АКТИВНЫЙ 2-ЧАСОВОЙ ШТУРМ! ВСЕ ГОРОДА ОБЕИХ НАЦИЙ ТЕПЕРЬ УЯЗВИМЫ К ВЗРЫВАМ И ПУШКАМ!',
              'danger'
            );
            setNotificationToast({
              type: 'danger',
              title: '⚡ ШТУРМ НАЧАЛСЯ! ВСЕ ГОРОДА УЯЗВИМЫ К ВЗРЫВАМ',
              message: 'Наступила 2-часовая фаза штурма с единым таймером для всех городов. Орудия и взрывы активны!'
            });
            return {
              ...prev,
              phase: 'ACTIVE_ASSAULT',
              remainingSeconds: prev.assaultTotalSeconds
            };
          } else if (prev.phase === 'ACTIVE_ASSAULT') {
            // End of 2h assault
            addLog(
              '🏳 2-часовой штурм завершён! Война окончена, все города обеих наций вернулись в мирный режим с защитой от взрывов.',
              'success'
            );
            setNotificationToast({
              type: 'success',
              title: 'Штурм завершён',
              message: 'Война наций окончена. Защита от взрывов восстановлена.'
            });
            return {
              ...prev,
              phase: 'COMPLETED',
              remainingSeconds: 0
            };
          }
        }
        return {
          ...prev,
          remainingSeconds: prev.remainingSeconds - 1
        };
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [warSession.phase, warSession.isTickerPaused]);

  const addLog = (text: string, type: 'warn' | 'danger' | 'info' | 'success') => {
    const timeStr = new Date().toLocaleTimeString('ru-RU');
    setCombatLogs((prev) => [{ id: `log_${Date.now()}_${Math.random()}`, time: timeStr, text, type }, ...prev.slice(0, 19)]);
  };

  // 1. Declare Nation War
  const handleDeclareWar = () => {
    soundFx.playRaidHorn();
    const newSession: NationWarSession = {
      id: `war_${Date.now()}`,
      attackerNationId: 'north_alliance',
      defenderNationId: 'south_league',
      declaredByLeader: 'Yaroslav_Great',
      phase: 'PREPARATION',
      preparationTotalSeconds: 86400,
      assaultTotalSeconds: 7200,
      remainingSeconds: 86400,
      isTickerPaused: false,
      activeCamps: [
        {
          id: `camp_${Date.now()}`,
          attackerTownName: 'Нордгард',
          defenderTownName: 'Авалония',
          attackerNationId: 'north_alliance',
          defenderNationId: 'south_league',
          placedAt: Date.now(),
          claimedChunks: 3,
          locationName: 'Фронтовая застава Нордгард-Авалония',
          mapPercentX: 42,
          mapPercentY: 48
        }
      ],
      explosionCasualties: 0,
      blocksDestroyedTotal: 0
    };
    setWarSession(newSession);

    // Reset town health to 100
    setNations((prev) =>
      prev.map((nat) => ({
        ...nat,
        towns: nat.towns.map((t) => ({ ...t, healthPercent: 100, recentExplosionHits: 0 }))
      }))
    );

    addLog(
      '👑 Глава Северного Альянса (Yaroslav_Great) объявил Войну Наций Южной Лиге! Все города обеих наций переведены в 24-часовую подготовку с единым таймером.',
      'warn'
    );
    setNotificationToast({
      type: 'warn',
      title: '⚔ ВОЙНА НАЦИЙ ОБЪЯВЛЕНА!',
      message: 'Все города обеих наций переведены в режим подготовки. Единый таймер: 24:00:00.'
    });
  };

  // 2. Fast-forward to 2h Assault
  const handleFastForwardToAssault = () => {
    soundFx.playAssaultAlert();
    setWarSession((prev) => ({
      ...prev,
      phase: 'ACTIVE_ASSAULT',
      remainingSeconds: 7200,
      isTickerPaused: false
    }));
    addLog(
      '⚡ Перемотка времени: Начался АКТИВНЫЙ 2-ЧАСОВОЙ ШТУРМ! Все города обеих наций стали УЯЗВИМЫ К ВЗРЫВАМ (TownyExplosionUnblocker разблокировал пушки и мортиры)!',
      'danger'
    );
    setNotificationToast({
      type: 'danger',
      title: '⚡ ШТУРМ 2 ЧАСА: ВЗРЫВЫ АКТИВИРОВАНЫ!',
      message: 'Все 6 городов обеих наций теперь уязвимы к взрывам орудий и осадного TNT.'
    });
  };

  // 3. Skip 30 minutes
  const handleSkipTime = (seconds: number) => {
    setWarSession((prev) => {
      const nextRemaining = Math.max(1, prev.remainingSeconds - seconds);
      return { ...prev, remainingSeconds: nextRemaining };
    });
    addLog(`⏱ Команда администратора: пропущено ${Math.floor(seconds / 60)} мин единого таймера войны наций (/siege nationwar skip ${seconds}).`, 'info');
  };

  // 4. Toggle pause
  const handleTogglePause = () => {
    setWarSession((prev) => ({ ...prev, isTickerPaused: !prev.isTickerPaused }));
  };

  // 5. End war / peace
  const handleEndWar = () => {
    setWarSession((prev) => ({
      ...prev,
      phase: 'PEACE',
      remainingSeconds: 0,
      activeCamps: []
    }));
    addLog('🏳 Война наций завершена. Заключен мирный договор. Все города защищены от взрывов.', 'success');
    setNotificationToast({
      type: 'success',
      title: 'Мир восстановлен',
      message: 'Война завершена. Иммунитет городов к взрывам включен на 100%.'
    });
  };

  // 6. Place another siege camp
  const handlePlaceSiegeCamp = () => {
    soundFx.playAnvilChime();
    const campPairs = [
      { atk: 'Новгород', def: 'Китеж-Град', loc: 'Перевал Новгород-Китеж', mx: 58, my: 38 },
      { atk: 'Валгалла', def: 'Солнцедар', loc: 'Горная дорога Валгалла-Солнцедар', mx: 64, my: 72 },
      { atk: 'Авалония', def: 'Нордгард', loc: 'Контр-лагерь Авалонии', mx: 32, my: 36 }
    ];
    const pick = campPairs[warSession.activeCamps.length % campPairs.length];
    const newCamp: SiegeCampWarLink = {
      id: `camp_${Date.now()}`,
      attackerTownName: pick.atk,
      defenderTownName: pick.def,
      attackerNationId: 'north_alliance',
      defenderNationId: 'south_league',
      placedAt: Date.now(),
      claimedChunks: 2,
      locationName: pick.loc,
      mapPercentX: pick.mx,
      mapPercentY: pick.my
    };

    setWarSession((prev) => ({
      ...prev,
      activeCamps: [...prev.activeCamps, newCamp]
    }));

    addLog(
      `⛺ Город «${pick.atk}» разбил осадный лагерь против «${pick.def}». Осада между городами не начинает отдельный таймер — продолжается единый таймер войны наций!`,
      'success'
    );
    setNotificationToast({
      type: 'info',
      title: '⛺ Осадный лагерь привязан к войне наций!',
      message: `Лагерь между ${pick.atk} и ${pick.def} использует единый таймер нации (${formatTimeHoursMinutesSeconds(warSession.remainingSeconds)}).`
    });
  };

  // 7. Simulate Artillery Cannon Shot on a Town (Test Explosion Vulnerability)
  const handleTestExplosionOnTown = (town: NationTown) => {
    const isVulnerable = warSession.phase === 'ACTIVE_ASSAULT';

    if (isVulnerable) {
      soundFx.playExplosion();
      const dmg = Math.floor(12 + Math.random() * 10);
      const blocksBroken = Math.floor(18 + Math.random() * 16);

      setNations((prev) =>
        prev.map((nat) => ({
          ...nat,
          towns: nat.towns.map((t) => {
            if (t.id === town.id) {
              const newHp = Math.max(10, t.healthPercent - dmg);
              return {
                ...t,
                healthPercent: newHp,
                recentExplosionHits: t.recentExplosionHits + 1,
                lastDamageTimestamp: Date.now()
              };
            }
            return t;
          })
        }))
      );

      setWarSession((prev) => ({
        ...prev,
        blocksDestroyedTotal: prev.blocksDestroyedTotal + blocksBroken,
        explosionCasualties: prev.explosionCasualties + 1
      }));

      addLog(
        `💥 [УЯЗВИМ К ВЗРЫВАМ] Залп осадной мортиры по городу «${town.name}»! Пробитие стены (-${dmg}% HP), ${blocksBroken} блоков разрушено, активирован кинетический разлет осколков FallingBlock!`,
        'danger'
      );
      setNotificationToast({
        type: 'danger',
        title: `💥 Взрыв нанес урон городу «${town.name}»!`,
        message: `Укрепления повреждены на -${dmg}%. Во время 2ч штурма ВСЕ города обеих наций уязвимы к взрывам!`
      });
    } else {
      addLog(
        `🛡 [ЗАЩИТА СРАБОТАЛА] Залп по городу «${town.name}» заблокирован! Вне 2ч активного штурма города полностью защищены от взрывов (TownyExplosionUnblocker).`,
        'info'
      );
      setNotificationToast({
        type: 'info',
        title: `🛡 Город «${town.name}» защищен от взрывов`,
        message: `Вне активного штурма взрывы не наносят урон. Перейдите в режим штурма (2ч), чтобы разблокировать уязвимость.`
      });
    }
  };

  const getPhaseNameRu = (phase: NationWarPhase) => {
    switch (phase) {
      case 'PEACE':
        return 'Мирное время';
      case 'PREPARATION':
        return 'Подготовка к штурму (24ч)';
      case 'ACTIVE_ASSAULT':
        return 'АКТИВНЫЙ ШТУРМ (2ч)';
      case 'COMPLETED':
        return 'Штурм завершён (Перемирие)';
    }
  };

  const isAssaultActive = warSession.phase === 'ACTIVE_ASSAULT';
  const isPrepActive = warSession.phase === 'PREPARATION';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Toast Notification */}
      {notificationToast && (
        <div
          className={`p-4 rounded-2xl border flex items-start justify-between gap-3 shadow-xl transition-all ${
            notificationToast.type === 'danger'
              ? 'bg-red-950/90 border-red-500/60 text-red-100 shadow-red-950/40'
              : notificationToast.type === 'warn'
              ? 'bg-amber-950/90 border-amber-500/60 text-amber-100 shadow-amber-950/40'
              : notificationToast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/60 text-emerald-100 shadow-emerald-950/40'
              : 'bg-cyan-950/90 border-cyan-500/60 text-cyan-100 shadow-cyan-950/40'
          }`}
        >
          <div className="flex items-start gap-3">
            {notificationToast.type === 'danger' && <Flame className="w-5 h-5 text-red-400 shrink-0 mt-0.5 animate-bounce" />}
            {notificationToast.type === 'warn' && <Timer className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />}
            {notificationToast.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />}
            {notificationToast.type === 'info' && <Tent className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />}
            <div>
              <div className="font-bold text-sm leading-tight text-white">{notificationToast.title}</div>
              <div className="text-xs opacity-90 mt-0.5">{notificationToast.message}</div>
            </div>
          </div>
          <button
            onClick={() => setNotificationToast(null)}
            className="text-neutral-400 hover:text-white text-xs px-2 py-1 rounded bg-neutral-900/40"
          >
            ✕
          </button>
        </div>
      )}

      {/* Minecraft Paper In-Game BossBar Simulation */}
      {(isPrepActive || isAssaultActive) && (
        <div className="bg-neutral-950 p-3 sm:p-4 rounded-2xl border border-neutral-800 shadow-2xl relative overflow-hidden">
          <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400 mb-2">
            <span className="flex items-center gap-1.5 font-bold text-neutral-300">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
              <span>Отображение в игре: BossBar для игроков обеих наций</span>
            </span>
            <span className="text-neutral-400">Цвет: {isAssaultActive ? 'КРАСНЫЙ (DARK_RED)' : 'ЖЕЛТЫЙ (YELLOW)'}</span>
          </div>

          {/* Realistic Minecraft BossBar UI Container */}
          <div
            className={`p-3 rounded-xl border flex flex-col items-center justify-center text-center relative ${
              isAssaultActive
                ? 'bg-gradient-to-r from-red-950 via-rose-900 to-red-950 border-red-500 shadow-lg shadow-red-950/60'
                : 'bg-gradient-to-r from-amber-950 via-yellow-950 to-amber-950 border-amber-500/80 shadow-md'
            }`}
          >
            <div className="text-xs sm:text-sm font-black font-mono tracking-wide text-white drop-shadow-md flex items-center gap-2 flex-wrap justify-center">
              <Swords className="w-4 h-4 text-amber-300 animate-pulse shrink-0" />
              <span>ВОЙНА НАЦИЙ: [Северный Альянс] vs [Южная Лига]</span>
              <span className="text-neutral-300">•</span>
              <span className={isAssaultActive ? 'text-red-300 font-bold' : 'text-amber-300'}>
                {isAssaultActive ? 'АКТИВНЫЙ ШТУРМ' : 'ПОДГОТОВКА'}: {formatTimeHoursMinutesSeconds(warSession.remainingSeconds)}
              </span>
              <Swords className="w-4 h-4 text-amber-300 animate-pulse shrink-0" />
            </div>

            {/* BossBar HP / Countdown Progress Strip */}
            <div className="w-full max-w-xl bg-black/60 rounded-full h-2.5 mt-2 overflow-hidden border border-white/20 relative">
              <div
                className={`h-full transition-all duration-1000 ${
                  isAssaultActive ? 'bg-gradient-to-r from-red-500 via-orange-400 to-red-600 animate-pulse' : 'bg-gradient-to-r from-amber-400 to-yellow-300'
                }`}
                style={{
                  width: `${Math.max(
                    3,
                    (warSession.remainingSeconds /
                      (isAssaultActive ? warSession.assaultTotalSeconds : warSession.preparationTotalSeconds)) *
                      100
                  )}%`
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Top Main Unified War Control Panel */}
      <div className="bg-gradient-to-br from-neutral-900 via-neutral-900/95 to-neutral-950 border border-neutral-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col xl:flex-row xl:items-center justify-between gap-6 pb-6 border-b border-neutral-800">
          <div>
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <div className="p-2.5 rounded-2xl bg-gradient-to-br from-amber-500/20 to-red-500/20 border border-amber-500/30 text-amber-400">
                <Crown className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                    Войны Наций (Nation Wars)
                  </h3>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-mono font-bold border ${
                      isAssaultActive
                        ? 'bg-red-500/20 border-red-500 text-red-300 animate-pulse'
                        : isPrepActive
                        ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                        : 'bg-neutral-800 border-neutral-700 text-neutral-400'
                    }`}
                  >
                    {getPhaseNameRu(warSession.phase)}
                  </span>
                </div>
                <div className="text-xs text-neutral-400 flex items-center gap-2 mt-1 flex-wrap">
                  <span>Объявление войны главой нации</span>
                  <span aria-hidden="true">•</span>
                  <span className="text-amber-400 font-semibold">Единый таймер для всех городов</span>
                  <span aria-hidden="true">•</span>
                  <span className="text-red-400 font-semibold">2ч штурма: все города уязвимы к взрывам</span>
                </div>
              </div>
            </div>
            <p className="text-neutral-300 text-sm max-w-3xl leading-relaxed">
              Когда глава нации объявляет войну другой нации, <strong>все города обеих наций</strong> синхронно переводятся в режим 24-часовой подготовки и последующего 2-часового активного штурма с <strong>единым глобальным таймером</strong>. Любые поставленные осадные лагеря не начинают отдельный таймер, а продолжают единый таймер нации. Во время 2-часового штурма <strong>все города обеих наций становятся уязвимы к орудийным взрывам</strong>!
            </p>
          </div>

          {/* Unified Nation Timer Display Widget */}
          <div className="flex flex-col items-center xl:items-end justify-center shrink-0">
            <div
              className={`p-4 rounded-2xl border flex flex-col items-center text-center min-w-[260px] ${
                isAssaultActive
                  ? 'bg-red-950/80 border-red-500 shadow-xl shadow-red-950/50'
                  : isPrepActive
                  ? 'bg-neutral-950 border-amber-500/60 shadow-lg'
                  : 'bg-neutral-950 border-neutral-800'
              }`}
            >
              <div className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 flex items-center gap-1.5 mb-1">
                <Timer className="w-3.5 h-3.5 text-amber-400" />
                <span>Единый таймер для всех городов</span>
              </div>
              <div
                className={`text-3xl sm:text-4xl font-black font-mono tracking-tight ${
                  isAssaultActive ? 'text-red-400 animate-pulse' : isPrepActive ? 'text-amber-300' : 'text-neutral-500'
                }`}
              >
                {warSession.phase === 'PEACE' ? '00:00:00' : formatTimeHoursMinutesSeconds(warSession.remainingSeconds)}
              </div>
              <div className="text-[10px] text-neutral-400 mt-1">
                {isAssaultActive ? (
                  <span className="text-red-400 font-bold flex items-center gap-1">
                    <Bomb className="w-3 h-3" />
                    <span>ВСЕ ГОРОДА УЯЗВИМЫ К ВЗРЫВАМ (2ч)</span>
                  </span>
                ) : isPrepActive ? (
                  <span>Фаза подготовки: осадные лагеря разрешены</span>
                ) : (
                  <span>Война не активна</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Action Controls & Simulation Bar */}
        <div className="pt-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            {warSession.phase === 'PEACE' || warSession.phase === 'COMPLETED' ? (
              <button
                onClick={handleDeclareWar}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 hover:from-amber-400 hover:to-red-400 text-neutral-950 font-black text-xs sm:text-sm transition-all flex items-center gap-2 shadow-lg shadow-amber-500/20 cursor-pointer"
              >
                <Crown className="w-4 h-4" />
                <span>Объявить Войну Наций (/nation war declare)</span>
              </button>
            ) : (
              <>
                {isPrepActive && (
                  <button
                    onClick={handleFastForwardToAssault}
                    className="px-3.5 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-red-500/20 cursor-pointer"
                    title="Мгновенно завершить 24 часа подготовки и начать 2-часовой штурм"
                  >
                    <Flame className="w-4 h-4" />
                    <span>Начать 2ч Штурм немедленно (Все города уязвимы)</span>
                  </button>
                )}

                <button
                  onClick={() => handleSkipTime(1800)}
                  className="px-3 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-semibold text-xs border border-neutral-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                  title="Промотать 30 минут общего таймера"
                >
                  <FastForward className="w-3.5 h-3.5 text-amber-400" />
                  <span>Промотать 30 мин (/siege skip 1800)</span>
                </button>

                <button
                  onClick={handlePlaceSiegeCamp}
                  className="px-3 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-cyan-300 font-semibold text-xs border border-neutral-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                  title="Разбить осадный лагерь между городами воюющих наций"
                >
                  <Tent className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Разбить осадный лагерь (+1 на фронт)</span>
                </button>

                <button
                  onClick={handleTogglePause}
                  className="p-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 transition-colors cursor-pointer"
                  title={warSession.isTickerPaused ? 'Возобновить отсчет' : 'Пауза отсчета'}
                >
                  {warSession.isTickerPaused ? <Play className="w-4 h-4 text-emerald-400" /> : <Pause className="w-4 h-4" />}
                </button>

                <button
                  onClick={handleEndWar}
                  className="px-3 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-white font-semibold text-xs border border-neutral-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                  title="Заключить мирный договор и сбросить таймеры"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Заключить мир (/siege nationwar end)</span>
                </button>
              </>
            )}
          </div>

          {onOpenBlueMapWithWar && (
            <button
              onClick={onOpenBlueMapWithWar}
              className="px-3.5 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold text-xs transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <span>Показать фронт на BlueMap</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Two Nations Frontline Battle Board */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {nations.map((nation, natIdx) => {
          const isAttacker = nation.id === warSession.attackerNationId;
          const roleTitle = isAttacker ? 'Атакующая сторона (Объявила войну)' : 'Обороняющаяся сторона (Приняла войну)';

          return (
            <div
              key={nation.id}
              className={`rounded-3xl p-6 border transition-all ${
                isAssaultActive
                  ? 'bg-neutral-900/90 border-red-500/40 shadow-xl shadow-red-950/20'
                  : 'bg-neutral-900/90 border-neutral-800 shadow-xl'
              }`}
            >
              {/* Nation Header */}
              <div className="flex items-center justify-between pb-4 border-b border-neutral-800">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-2xl flex items-center justify-center font-black text-lg ${
                      natIdx === 0 ? 'bg-amber-500 text-neutral-950' : 'bg-emerald-500 text-neutral-950'
                    }`}
                  >
                    {natIdx === 0 ? '🦅' : '🦁'}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-xl font-bold text-white tracking-tight">{nation.name}</h4>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${nation.badgeBg}`}>
                        Нация Towny
                      </span>
                    </div>
                    <div className="text-xs text-neutral-400">
                      Король (Глава): <strong className="text-white">{nation.leader}</strong> · Столица: <strong className="text-neutral-200">{nation.capitalName}</strong>
                    </div>
                  </div>
                </div>

                <div className="text-right text-xs font-mono">
                  <div className="text-neutral-400">Казна нации</div>
                  <div className="font-bold text-yellow-400">{nation.bankGold.toLocaleString()} монет</div>
                </div>
              </div>

              {/* Status Banner for this Nation */}
              <div className="py-3 my-3 px-3.5 rounded-xl bg-neutral-950 border border-neutral-800 flex items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-neutral-400">{roleTitle}:</span>
                  <span className="font-bold text-white">{nation.towns.length} городов в войне</span>
                </div>
                <div className="font-mono text-[11px]">
                  {isAssaultActive ? (
                    <span className="text-red-400 font-bold flex items-center gap-1">
                      <Bomb className="w-3.5 h-3.5" />
                      <span>ВЗРЫВЫ АКТИВНЫ</span>
                    </span>
                  ) : isPrepActive ? (
                    <span className="text-amber-400 font-medium">Подготовка к штурму</span>
                  ) : (
                    <span className="text-emerald-400">Мирный иммунитет</span>
                  )}
                </div>
              </div>

              {/* List of Towns in this Nation */}
              <div className="space-y-3 mt-4">
                <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider px-1">
                  Города нации (Единый военный статус):
                </div>

                {nation.towns.map((town) => {
                  return (
                    <div
                      key={town.id}
                      className={`p-4 rounded-2xl border transition-all ${
                        isAssaultActive
                          ? 'bg-neutral-950/80 border-red-500/40 hover:border-red-400'
                          : 'bg-neutral-950/80 border-neutral-800 hover:border-neutral-700'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2.5">
                          <Landmark className="w-4 h-4 text-neutral-400 shrink-0" />
                          <div>
                            <div className="text-sm font-bold text-white flex items-center gap-1.5">
                              <span>Город «{town.name}»</span>
                              {town.isCapital && (
                                <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[10px] font-mono border border-amber-500/40">
                                  Столица
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-neutral-400 font-mono">
                              Мэр: <span className="text-neutral-200">{town.mayor}</span> · {town.residentsCount} жит. · Координаты: X:{town.coordinates.x}, Z:{town.coordinates.z}
                            </div>
                          </div>
                        </div>

                        {/* Explosion Vulnerability Status Indicator */}
                        <div className="text-right">
                          {isAssaultActive ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-red-950 border border-red-500 text-red-300 animate-pulse">
                              <Bomb className="w-3 h-3" />
                              <span>УЯЗВИМ К ВЗРЫВАМ</span>
                            </span>
                          ) : isPrepActive ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-amber-950/60 border border-amber-500/50 text-amber-300">
                              <ShieldAlert className="w-3 h-3" />
                              <span>Подготовка</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-emerald-950/60 border border-emerald-500/50 text-emerald-300">
                              <Shield className="w-3 h-3" />
                              <span>Мир (Иммунитет)</span>
                            </span>
                          )}
                        </div>
                      </div>

                      {/* City Fortification Health Bar */}
                      <div className="space-y-1 mb-3">
                        <div className="flex items-center justify-between text-[11px] font-mono">
                          <span className="text-neutral-400">Прочность укреплений:</span>
                          <span className={town.healthPercent < 50 ? 'text-red-400 font-bold' : 'text-emerald-400 font-bold'}>
                            {town.healthPercent}%
                          </span>
                        </div>
                        <div className="w-full bg-neutral-900 rounded-full h-1.5 overflow-hidden border border-neutral-800">
                          <div
                            className={`h-full transition-all duration-300 ${
                              town.healthPercent < 40
                                ? 'bg-red-500'
                                : town.healthPercent < 75
                                ? 'bg-amber-400'
                                : 'bg-emerald-400'
                            }`}
                            style={{ width: `${town.healthPercent}%` }}
                          />
                        </div>
                      </div>

                      {/* Interactive Artillery & Explosion Test Button */}
                      <div className="flex items-center justify-between gap-2 pt-2 border-t border-neutral-900">
                        <button
                          onClick={() => handleTestExplosionOnTown(town)}
                          className={`w-full py-2 px-3 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-2 cursor-pointer ${
                            isAssaultActive
                              ? 'bg-red-600 hover:bg-red-500 text-white shadow-md shadow-red-600/30'
                              : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700'
                          }`}
                        >
                          <Crosshair className="w-3.5 h-3.5" />
                          <span>
                            {isAssaultActive
                              ? `💥 Испытать выстрел мортиры по «${town.name}» (Разрушить блок)`
                              : `🛡 Проверить защиту от взрыва в «${town.name}»`}
                          </span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Siege Camps & Frontline Section */}
      <div className="bg-neutral-900/90 border border-neutral-800 rounded-3xl p-6 sm:p-8 shadow-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
          <div>
            <div className="flex items-center gap-2">
              <Tent className="w-5 h-5 text-cyan-400" />
              <h4 className="text-xl font-bold text-white tracking-tight">
                Осадные Лагеря Войны Наций ({warSession.activeCamps.length})
              </h4>
            </div>
            <p className="text-neutral-400 text-xs mt-0.5">
              Лагеря ставятся городами воюющих наций. <strong>Отдельный таймер осады города не запускается</strong> — все лагеря наследуют единый таймер нации!
            </p>
          </div>

          <button
            onClick={handlePlaceSiegeCamp}
            className="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-neutral-950 font-bold text-xs transition-colors flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            <Tent className="w-4 h-4" />
            <span>Разбить новый лагерь (/siege camp)</span>
          </button>
        </div>

        {/* Highlight Rule Box */}
        <div className="mt-4 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-200">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-amber-300">Правило непрерывности таймера:</strong> Во время подготовки и штурма при Войне Наций города обеих наций могут свободно ставить осадные лагеря друг на друга. Осада между городами не начинается с нуля — она продолжает единый синхронный таймер нации!
          </div>
        </div>

        {/* Camps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
          {warSession.activeCamps.map((camp, idx) => (
            <div
              key={camp.id}
              className="p-4 rounded-2xl bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="font-bold text-white text-xs font-mono">Лагерь #{idx + 1}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800">
                    {camp.claimedChunks} осадных чанка
                  </span>
                </div>
                <div className="text-xs text-neutral-300 font-medium mb-1">
                  <span className="text-amber-400">{camp.attackerTownName}</span>
                  <span className="text-neutral-500 mx-1.5">➔</span>
                  <span className="text-red-400">{camp.defenderTownName}</span>
                </div>
                <div className="text-[11px] text-neutral-400 font-mono space-y-0.5">
                  <div>Позиция: {camp.locationName}</div>
                  <div className="text-emerald-400">
                    Синхронизация: <strong className="text-white">Единый таймер нации ({formatTimeHoursMinutesSeconds(warSession.remainingSeconds)})</strong>
                  </div>
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-neutral-900 flex items-center justify-between text-[11px]">
                <span className="text-neutral-400">Осадные мортиры:</span>
                <span className={isAssaultActive ? 'text-red-400 font-bold' : 'text-amber-400'}>
                  {isAssaultActive ? 'ГОТОВЫ К ЗАЛПУ' : 'В подготовке'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Wartime Combat Log */}
      <div className="bg-neutral-900/90 border border-neutral-800 rounded-3xl p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-neutral-800">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
            <h4 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Журнал Войны Наций & Артиллерийских событий
            </h4>
          </div>
          <span className="text-xs font-mono text-neutral-400">
            Событий: {combatLogs.length} · Блоков повреждено: <strong className="text-amber-400">{warSession.blocksDestroyedTotal}</strong>
          </span>
        </div>

        <div className="space-y-2 max-h-56 overflow-y-auto font-mono text-xs pr-2 select-text">
          {combatLogs.map((log) => (
            <div
              key={log.id}
              className={`p-2.5 rounded-xl border flex items-start gap-2.5 ${
                log.type === 'danger'
                  ? 'bg-red-950/60 border-red-500/50 text-red-200'
                  : log.type === 'warn'
                  ? 'bg-amber-950/60 border-amber-500/50 text-amber-200'
                  : log.type === 'success'
                  ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-200'
                  : 'bg-neutral-950 border-neutral-800 text-neutral-300'
              }`}
            >
              <span className="text-neutral-500 text-[10px] shrink-0 mt-0.5">[{log.time}]</span>
              <span className="leading-relaxed">{log.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
