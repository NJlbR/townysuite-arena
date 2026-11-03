import React, { useState } from 'react';
import { Download, Check, Copy, Shield, Server, Box, Sparkles, Terminal, Zap, Flame, Map, Layers, CheckCircle2, ArrowDownToLine, PackageCheck, ExternalLink, Bed } from 'lucide-react';
import { TOWNY_RESPAWN_METADATA } from '../data/townyRespawnData';
import { TOWNY_SIEGES_METADATA } from '../data/townySiegesData';
import { UNBLOCKER_METADATA } from '../data/unblockerData';
import { PLUGIN_METADATA_V2 } from '../data/javaSources';
import {
  downloadTownyRespawnJar,
  downloadTownyRespawnBundle,
  downloadTownySiegesJar,
  downloadTownySiegesBundle,
  downloadUnblockerJar,
  downloadUnblockerBundle,
  downloadJarFile,
  downloadBundleZip,
  downloadAllPluginsZip
} from '../utils/downloadHelpers';

interface PluginCardData {
  id: 'respawn' | 'sieges' | 'unblocker' | 'architecture';
  name: string;
  version: string;
  releaseDate: string;
  category: string;
  badgeText: string;
  badgeColor: string;
  accentBorder: string;
  accentBg: string;
  iconBg: string;
  icon: React.ReactNode;
  jarFileName: string;
  jarSize: string;
  sha256: string;
  description: string;
  highlights: string[];
  dependencies: string[];
  onDownloadJar: () => void;
  onDownloadBundle: () => void;
}

export const PluginsDownloadHub: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'respawn' | 'sieges' | 'unblocker' | 'architecture'>('all');
  const [copiedSha, setCopiedSha] = useState<string | null>(null);
  const [downloadedPlugin, setDownloadedPlugin] = useState<string | null>(null);

  const handleCopyHash = (id: string, hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedSha(id);
    setTimeout(() => setCopiedSha(null), 2000);
  };

  const handleDownloadWithFeedback = (id: string, downloadFn: () => void) => {
    downloadFn();
    setDownloadedPlugin(id);
    setTimeout(() => setDownloadedPlugin(null), 3000);
  };

  const plugins: PluginCardData[] = [
    {
      id: 'respawn',
      name: 'TownyRespawn',
      version: TOWNY_RESPAWN_METADATA.version,
      releaseDate: TOWNY_RESPAWN_METADATA.releaseDate,
      category: 'Мульти-кровати & Респавн',
      badgeText: 'АВТОВОЗВРАТ ЧАНКОВ & ДИСБАНД',
      badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
      accentBorder: 'border-cyan-500/50 hover:border-cyan-400',
      accentBg: 'from-cyan-950/40 via-neutral-900 to-sky-950/30',
      iconBg: 'bg-cyan-500 text-neutral-950',
      icon: <Bed className="w-5 h-5" />,
      jarFileName: TOWNY_RESPAWN_METADATA.jarFileName,
      jarSize: TOWNY_RESPAWN_METADATA.jarSizeFormatted,
      sha256: TOWNY_RESPAWN_METADATA.jarSha256,
      description: 'Система мульти-кроватей, автоматическое удаление разрушенных кроватей из меню, ограничение 1 игрок на кровать, исправление бага 2 блоков кровати, переименование кроватей игроками, чистый респавн без слепоты и замедления, спавны Towny и веб-карта BlueMap.',
      highlights: [
        'Автоматическое удаление разрушенных кроватей из меню /respawn и базы данных (при поломке, взрывах, огне, поршнях)',
        'Ограничение: на 1 кровати может поставить спавн только 1 игрок (эксклюзивность привязки)',
        'Исправлен баг 2 блоков кровати: изголовье и изножье нормализуются и считаются единой кроватью',
        'Меню /respawn: удобный выбор точки из списка вместо карты в игре + переименование кроватей (ПКМ / команда)',
        'Чистый респавн БЕЗ слепоты и БЕЗ замедления с 5-секундной защитой от урона',
        'Реалистичная веб-карта BlueMap на сайте без разбиения на чанки с реальным видом мира'
      ],
      dependencies: ['Paper 1.20+', 'Towny', 'TownySieges (опц.)'],
      onDownloadJar: () => downloadTownyRespawnJar(),
      onDownloadBundle: () => downloadTownyRespawnBundle()
    },
    {
      id: 'sieges',
      name: 'TownySieges',
      version: TOWNY_SIEGES_METADATA.version,
      releaseDate: TOWNY_SIEGES_METADATA.releaseDate,
      category: 'Осады & Войны',
      badgeText: 'ТАКТИЧЕСКИЕ ОСАДЫ',
      badgeColor: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
      accentBorder: 'border-orange-500/50 hover:border-orange-400',
      accentBg: 'from-orange-950/40 via-neutral-900 to-amber-950/30',
      iconBg: 'bg-orange-500 text-neutral-950',
      icon: <Flame className="w-5 h-5" />,
      jarFileName: TOWNY_SIEGES_METADATA.jarFileName,
      jarSize: TOWNY_SIEGES_METADATA.jarSizeFormatted,
      sha256: TOWNY_SIEGES_METADATA.jarSha256,
      description: 'Тактические осадные лагеря, Войны Наций, почанковый захват штурмовым флагом с расчетом перевеса игроков, маячным лучом и боссбаром, интерактивное меню /siege menu с описанием систем и крафтов, кастомные рецепты верстака для мортиры и ядер, и кинетическое пробитие обсидиановых укреплений бронебойными ядрами.',
      highlights: [
        '💀 Полное удаление захваченных городов: при захвате Домашнего Чанка (Homeblock) город полностью стирается БЕЗ РУИН — при выполнении /t выводится "Город не найден", а казна передается победителю!',
        '📖 Интерактивное меню /siege menu: встроенное GUI-руководство с подробным описанием систем плагина (осадные лагеря, почанковый захват, мортиры, навык «Артиллерист», войны наций, захват зданий), списками команд и интерактивными 3х3 сетками крафта верстака для мортиры, фугасных/бронебойных ядер и штурмового флага!',
        '🚩 Почанковый захват (v1.5.0): установка крафтового Штурмового Флага на смежные чанки с осадным лагерем (/siege banner give)',
        '♻️ Автовозврат чанков лагеря: после окончания осады или штурма все чанки лагеря возвращаются в исходный статус (городской чанк, аванпост или дикие земли) независимо от исхода!',
        '⚔️ Уничтожение лагеря мэром (/siege disband): стоя на любом чанке своего осадного лагеря, мэр атакующего города может расформировать лагерь в любой момент с полным возвратом территорий!',
        '⚡ Единые админ-команды (/siege admin skip-prep [город|нация]): мгновенный пропуск 24ч подготовки и старт 2ч активного штурма с синхронизацией разблокировки орудий и стойкости стен',
        '⚡ Динамический расчет скорости захвата: базовое время (5 мин) масштабируется коэффициентом перевеса (Атакующие ÷ Защитники на чанке)',
        '📡 Эффекты и BossBar: луч маяка до неба (Y=320), победный горн и рейд-звуки при установке, боссбар с числом бойцов и прогрессом захвата',
        '🏰 Откат и Аванпосты Towny: если защитников больше, прогресс откатывается; при отрицательном значении чанк переходит защитникам (несмежные чанки получают статус официального Outpost Towny)',
        'Кастомные рецепты верстака 3x3: Штурмовой Флаг, Осадная мортира, ⚪ Обычные ядра и 🟣 Бронебойные ядра (/siege ammo recipes)',
        '100% нестакаемые предметы (1 шт / слот): каждая мортира и ядро имеют уникальный NBT UUID (ammo_uid)',
        'Боекомплект в инвентаре стрелка: стрельба только при наличии ядер, расход 1 шт за выстрел',
        'Переключатель типов снарядов (кнопка смены руки F): быстрый выбор активного ядра прямо в седле',
        'Live HUD мониторинг инвентаря: отображение запаса боеприпасов в Action Bar (⚪: X шт. | 🟣: Y шт.)',
        'Пробитие обсидиана: 🟣 Бронебойные ядра разбивают блоки обсидиана в радиусе 3.2 блоков во время штурма!',
        'Войны Наций (/siege nationwar declare): глобальный 24-часовой таймер с BossBar и 2-часовой активный штурм для городов обеих наций'
      ],
      dependencies: ['Paper 1.20+', 'Towny', 'TownyExplosionUnblocker (рекомендуется)'],
      onDownloadJar: () => downloadTownySiegesJar(),
      onDownloadBundle: () => downloadTownySiegesBundle()
    },
    {
      id: 'unblocker',
      name: 'TownyExplosionUnblocker',
      version: UNBLOCKER_METADATA.version,
      releaseDate: UNBLOCKER_METADATA.releaseDate,
      category: 'Артиллерия & Физика',
      badgeText: 'КОМПАНЬОН',
      badgeColor: 'bg-red-500/20 text-red-300 border-red-500/40',
      accentBorder: 'border-red-500/50 hover:border-red-400',
      accentBg: 'from-red-950/40 via-neutral-900 to-rose-950/30',
      iconBg: 'bg-red-500 text-white',
      icon: <Zap className="w-5 h-5" />,
      jarFileName: UNBLOCKER_METADATA.jarFileName,
      jarSize: UNBLOCKER_METADATA.jarSizeFormatted,
      sha256: UNBLOCKER_METADATA.jarSha256,
      description: 'Идеальная синергия с SiegeCannons & TownySieges: во время активного 2-часового штурма (как при локальной осаде города, так и при Войне Наций) ВСЕ орудийные орудия (пушки, мортиры, осадные пушки, ядра) работают на 100%, блоки ломаются и разлетаются по всему оригинальному функционалу SiegeCannons во всех воюющих городах!',
      highlights: [
        'Во время 2ч штурма: ВСЕ города обеих наций при Войне Наций и осаждённые города становятся уязвимы к взрывам орудий',
        'Полный функционал разлета блоков SiegeCannons во время штурма (FallingBlock debris, осколки, кинетика)',
        'Вне штурма: 100% блокировка урона пушек и нейтрализация механизма разлета блоков',
        'Авто-восстановление блоков вне штурма при попытках запуска их в воздух сторонними орудиями',
        'Синхронизация с TownySieges API: проверка isTownUnderActiveSiege() возвращает true для всех городов воюющих наций',
        'Защита границы города: снаряды из диких земель вне штурма не могут повреждать блоки мирных городов',
        'Команда /teu status для проверки режима штурма и активных орудий'
      ],
      dependencies: ['Paper 1.20+', 'Towny', 'TownySieges'],
      onDownloadJar: () => downloadUnblockerJar(),
      onDownloadBundle: () => downloadUnblockerBundle()
    },
    {
      id: 'architecture',
      name: 'TownyArchitecture',
      version: PLUGIN_METADATA_V2.version,
      releaseDate: '2026-10-30',
      category: 'Чудеса Света & Фортификации',
      badgeText: 'ОСНОВНОЙ ПЛАГИН',
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      accentBorder: 'border-amber-500/50 hover:border-amber-400',
      accentBg: 'from-amber-950/40 via-neutral-900 to-yellow-950/30',
      iconBg: 'bg-amber-500 text-neutral-950',
      icon: <Layers className="w-5 h-5" />,
      jarFileName: PLUGIN_METADATA_V2.jarFileName,
      jarSize: PLUGIN_METADATA_V2.fileSizeFormatted,
      sha256: PLUGIN_METADATA_V2.sha256,
      description: 'Великие архитектурные чудеса света с эффектами BlockDisplay 1.20+, кастомным фоном /build из ресурспака, Мэрией (2x2) со Щитом и Городской Стеной (2x1).',
      highlights: [
        '💰 Личный лимит кошелька & Суммирование Банков: базовый лимит наличных 10 000 монет + 10 000 за каждый построенный Банк в городе (бонусы Банков суммируются!). При переполнении лимита игрок получает дебаффы (замедление, утомление, слабость) до сдачи денег в кассу (/t deposit)!',
        'Полноценный кастомный GUI /build с фоновым меню из ресурс-пака (menu.png)',
        'Мэрия (2x2) и Городская Стена (2x1) гарантированно доступны в меню чертежей',
        'Интеграция Щита Мэрии: +100 HP прочности за каждую построенную стену',
        '3D голограммы построек через BlockDisplay (1.20+) с контурной подсветкой',
        'Чистая физика ванильного динамита и реалистичные звуковые эффекты',
        'Взрывы мортир наносят урон и разрушают блоки строго во время активного штурма'
      ],
      dependencies: ['Paper 1.20+', 'Towny', 'BlockDisplay 1.20+'],
      onDownloadJar: () => downloadJarFile('v2', PLUGIN_METADATA_V2.jarFileName),
      onDownloadBundle: () => downloadBundleZip('v2', PLUGIN_METADATA_V2.bundleFileName)
    }
  ];

  const filteredPlugins = filter === 'all' ? plugins : plugins.filter(p => p.id === filter);

  const handleDownloadAll = () => {
    downloadAllPluginsZip();
    setDownloadedPlugin('all');
    setTimeout(() => setDownloadedPlugin(null), 4000);
  };

  return (
    <div id="downloads" className="w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Top Banner: Quick 1-Click Suite Download */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-neutral-900 via-neutral-900/95 to-neutral-950 border border-neutral-800 p-6 sm:p-8 mb-10 shadow-2xl">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2">
              <PackageCheck className="w-4 h-4" />
              <span>Центр быстрой загрузки плагинов · Towny Suite 2026</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight mb-3">
              Готовые скомпилированные .JAR плагины для вашего сервера
            </h1>
            <p className="text-neutral-300 text-sm sm:text-base leading-relaxed">
              Все 4 взаимосвязанных плагина протестированы, скомпилированы и готовы к загрузке в папку <code className="px-1.5 py-0.5 rounded bg-neutral-800 text-amber-300 font-mono text-xs">/plugins/</code> на ядре Paper 1.20+.
              Скачайте полный комплект одним нажатием или выберите нужные компоненты ниже.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 shrink-0">
            <button
              onClick={handleDownloadAll}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 via-amber-500 to-orange-500 hover:from-cyan-400 hover:to-orange-400 text-neutral-950 font-black text-sm sm:text-base transition-all flex items-center justify-center gap-3 shadow-xl shadow-amber-500/20 cursor-pointer"
            >
              <ArrowDownToLine className="w-5 h-5" />
              <span>Скачать все 4 плагина (.ZIP с 4 JAR)</span>
            </button>
            <div className="text-center text-xs text-neutral-400">
              {downloadedPlugin === 'all' ? (
                <span className="text-emerald-400 font-bold flex items-center justify-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Архив TownySuite-All-Plugins.zip загружен!
                </span>
              ) : (
                'TownyRespawn, TownySieges, Unblocker, Architecture в одном архиве'
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-neutral-900 border border-neutral-800 flex-wrap">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              filter === 'all'
                ? 'bg-white text-neutral-950 shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Все плагины ({plugins.length})
          </button>
          <button
            onClick={() => setFilter('respawn')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              filter === 'respawn'
                ? 'bg-cyan-500 text-neutral-950 shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            TownyRespawn (Карта)
          </button>
          <button
            onClick={() => setFilter('sieges')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              filter === 'sieges'
                ? 'bg-orange-500 text-neutral-950 shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            TownySieges (Осады)
          </button>
          <button
            onClick={() => setFilter('unblocker')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              filter === 'unblocker'
                ? 'bg-red-500 text-white shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            TownyExplosionUnblocker
          </button>
          <button
            onClick={() => setFilter('architecture')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              filter === 'architecture'
                ? 'bg-amber-500 text-neutral-950 shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            TownyArchitecture (3D)
          </button>
        </div>

        <div className="text-xs text-neutral-400 font-mono">
          Платформа: <span className="text-emerald-400">Paper / Purpur 1.20+</span>
        </div>
      </div>

      {/* Plugin Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        {filteredPlugins.map((plugin) => (
          <div
            key={plugin.id}
            className={`rounded-2xl border-2 p-6 transition-all flex flex-col justify-between bg-gradient-to-br ${plugin.accentBg} ${plugin.accentBorder} shadow-lg`}
          >
            <div>
              {/* Card Header */}
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold shadow-md ${plugin.iconBg}`}>
                    {plugin.icon}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-bold text-white">{plugin.name}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border ${plugin.badgeColor}`}>
                        v{plugin.version}
                      </span>
                    </div>
                    <div className="text-xs text-neutral-400 mt-0.5 flex items-center gap-2">
                      <span>{plugin.category}</span>
                      <span aria-hidden="true">·</span>
                      <span className="font-mono text-neutral-500">{plugin.jarSize}</span>
                    </div>
                  </div>
                </div>

                <span className={`text-[10px] font-mono px-2 py-1 rounded bg-neutral-950/80 border border-neutral-800 text-neutral-400`}>
                  {plugin.releaseDate}
                </span>
              </div>

              {/* Description */}
              <p className="text-neutral-300 text-sm mb-4 leading-relaxed">
                {plugin.description}
              </p>

              {/* Checklist highlights */}
              <div className="space-y-1.5 mb-5 bg-neutral-950/60 p-3.5 rounded-xl border border-neutral-800/80">
                {plugin.highlights.map((h, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-neutral-300">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{h}</span>
                  </div>
                ))}
              </div>

              {/* Dependencies tags */}
              <div className="flex items-center gap-1.5 mb-6 flex-wrap">
                <span className="text-[11px] text-neutral-400 font-medium mr-1">Зависимости:</span>
                {plugin.dependencies.map((dep, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-300 text-[11px] font-mono">
                    {dep}
                  </span>
                ))}
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="pt-4 border-t border-neutral-800/80">
              <div className="flex flex-col sm:flex-row items-center gap-3 mb-3">
                <button
                  onClick={() => handleDownloadWithFeedback(plugin.id, plugin.onDownloadJar)}
                  className="w-full sm:flex-1 py-2.5 px-4 rounded-xl bg-white hover:bg-neutral-200 text-neutral-950 font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all shadow-md cursor-pointer"
                >
                  {downloadedPlugin === plugin.id ? (
                    <>
                      <Check className="w-4 h-4 text-emerald-600" />
                      <span>Скачивается!</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      <span>Скачать {plugin.jarFileName}</span>
                    </>
                  )}
                </button>

                <button
                  onClick={() => plugin.onDownloadBundle()}
                  className="w-full sm:w-auto py-2.5 px-3 rounded-xl bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-neutral-200 font-semibold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Box className="w-3.5 h-3.5 text-neutral-400" />
                  <span>Bundle ZIP</span>
                </button>
              </div>

              {/* SHA-256 copy */}
              <div className="flex items-center justify-between text-[11px] text-neutral-400 font-mono bg-neutral-950/80 px-2.5 py-1.5 rounded-lg border border-neutral-800">
                <span className="truncate mr-2">SHA: {plugin.sha256}</span>
                <button
                  onClick={() => handleCopyHash(plugin.id, plugin.sha256)}
                  className="hover:text-white shrink-0 flex items-center gap-1 cursor-pointer"
                  title="Скопировать контрольную сумму"
                >
                  {copiedSha === plugin.id ? (
                    <span className="text-emerald-400 flex items-center gap-0.5">
                      <Check className="w-3 h-3" /> скопировано
                    </span>
                  ) : (
                    <span className="flex items-center gap-0.5">
                      <Copy className="w-3 h-3" /> копировать
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
