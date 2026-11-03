import { ChangelogSection } from './ChangelogSection';
import React, { useState } from 'react';
import { Download, Check, Copy, Shield, Server, Box, Sparkles, Terminal, FileCode2, Zap, Award, CheckCircle2, Palette, Layers, Eye, Compass, ShieldAlert, Cpu, Flame, Clock, Landmark } from 'lucide-react';
import { PLUGIN_METADATA_V1, PLUGIN_METADATA_V2 } from '../data/javaSources';
import { JAR_BASE64_V1, JAR_BASE64_V2 } from '../data/jarBase64';
import { downloadJarFile, downloadBundleZip, downloadResourcePackZip, downloadTownySiegesJar, downloadTownySiegesBundle, downloadUnblockerJar, downloadUnblockerBundle } from '../utils/downloadHelpers';
import { RESOURCE_PACK_SHA1, RESOURCE_PACK_SIZE } from '../data/resourcePackBase64';
import { TOWNY_SIEGES_METADATA } from '../data/townySiegesData';
import { UNBLOCKER_METADATA } from '../data/unblockerData';

interface JarDownloadHeroProps {
  onNavigateTab: (tab: 'editor' | 'guide' | 'sources') => void;
}

export const JarDownloadHero: React.FC<JarDownloadHeroProps> = ({ onNavigateTab }) => {
  const [selectedBranch, setSelectedBranch] = useState<'v2' | 'v1'>('v2');
  const [copiedSha, setCopiedSha] = useState(false);
  const [copiedRpSha, setCopiedRpSha] = useState(false);
  const [copiedB64, setCopiedB64] = useState(false);
  const [downloadedJar, setDownloadedJar] = useState(false);
  const [downloadedBundle, setDownloadedBundle] = useState(false);
  const [downloadedRp, setDownloadedRp] = useState(false);

  const activeMeta = selectedBranch === 'v2' ? PLUGIN_METADATA_V2 : PLUGIN_METADATA_V1;
  const activeB64 = selectedBranch === 'v2' ? JAR_BASE64_V2 : JAR_BASE64_V1;

  const handleCopySha = () => {
    navigator.clipboard.writeText(activeMeta.sha256);
    setCopiedSha(true);
    setTimeout(() => setCopiedSha(false), 2000);
  };

  const handleCopyRpSha = () => {
    navigator.clipboard.writeText(RESOURCE_PACK_SHA1);
    setCopiedRpSha(true);
    setTimeout(() => setCopiedRpSha(false), 2000);
  };

  const handleDownloadRp = (e: React.MouseEvent) => {
    e.preventDefault();
    downloadResourcePackZip('TownyArchitecture.zip');
    setDownloadedRp(true);
    setTimeout(() => setDownloadedRp(false), 4000);
  };

  const handleCopyBase64 = () => {
    const cmd = `base64 -d << 'EOF' > plugins/${activeMeta.jarFileName}\n${activeB64}\nEOF`;
    navigator.clipboard.writeText(cmd);
    setCopiedB64(true);
    setTimeout(() => setCopiedB64(false), 2500);
  };

  const handleDownloadJar = (e: React.MouseEvent) => {
    e.preventDefault();
    downloadJarFile(selectedBranch, activeMeta.jarFileName);
    setDownloadedJar(true);
    setTimeout(() => setDownloadedJar(false), 4000);
  };

  const handleDownloadBundle = (e: React.MouseEvent) => {
    e.preventDefault();
    downloadBundleZip(selectedBranch, activeMeta.bundleFileName);
    setDownloadedBundle(true);
    setTimeout(() => setDownloadedBundle(false), 4000);
  };

  return (
    <div id="download-hero" className="w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Branch Selector Switcher */}
      <div className="mb-6 p-2 rounded-2xl bg-neutral-900/90 border border-neutral-800 backdrop-blur-sm">
        <div className="text-xs font-semibold uppercase tracking-wider text-neutral-400 px-3 py-1 flex items-center justify-between">
          <span>Выберите ветку релиза плагина для скачивания и аудита:</span>
          <span className="text-[11px] text-amber-400 font-mono">Доступны 2 независимые ветки</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1">
          <button
            id="btn-branch-v2"
            onClick={() => setSelectedBranch('v2')}
            className={`flex items-center gap-3 p-3.5 rounded-xl text-left transition-all cursor-pointer ${
              selectedBranch === 'v2'
                ? 'bg-amber-500/15 border-2 border-amber-500/80 text-white shadow-lg shadow-amber-500/10'
                : 'bg-neutral-950/60 border border-neutral-800 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50'
            }`}
          >
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
              selectedBranch === 'v2' ? 'bg-amber-500 text-neutral-950 font-black' : 'bg-neutral-800 text-neutral-400'
            }`}>
              <Layers className="w-5 h-5" />
            </div>
            <div className="truncate">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-white">Ветка 2.0.0 (3D Litematica & BlockDisplay)</span>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider border border-emerald-500/40">
                  Текущая
                </span>
              </div>
              <div className="text-xs text-neutral-400 mt-0.5 truncate">
                Голограммы BlockDisplay 1.20+, автосканирование чанка и привязка к существующим этапам, послойный вид, анти-бункер
              </div>
            </div>
          </button>

          <button
            id="btn-branch-v1"
            onClick={() => setSelectedBranch('v1')}
            className={`flex items-center gap-3 p-3.5 rounded-xl text-left transition-all cursor-pointer ${
              selectedBranch === 'v1'
                ? 'bg-blue-500/15 border-2 border-blue-500/80 text-white shadow-lg shadow-blue-500/10'
                : 'bg-neutral-950/60 border border-neutral-800 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50'
            }`}
          >
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
              selectedBranch === 'v1' ? 'bg-blue-500 text-neutral-950 font-black' : 'bg-neutral-800 text-neutral-400'
            }`}>
              <Box className="w-5 h-5" />
            </div>
            <div className="truncate">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-white">Ветка 1.5.0 (Классическая чанковая)</span>
                <span className="px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-300 text-[10px] font-mono border border-neutral-700">
                  Сохранена
                </span>
              </div>
              <div className="text-xs text-neutral-400 mt-0.5 truncate">
                Ресурсный подсчет блоков внутри чанков, аудит целостности, частицы границ, Чудеса Света
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Top Banner */}
      <div className={`bg-gradient-to-r ${selectedBranch === 'v2' ? 'from-amber-500/15 via-emerald-500/10 to-blue-500/10 border-amber-500/30' : 'from-blue-500/15 via-indigo-500/10 to-neutral-900 border-blue-500/30'} border rounded-2xl p-6 sm:p-8 mb-8 backdrop-blur-sm transition-all`}>
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Готовый релиз v{activeMeta.version} скомпилирован и проверен
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight mb-3">
              TownyArchitecture <span className={`${selectedBranch === 'v2' ? 'text-amber-400' : 'text-blue-400'} font-mono text-2xl font-normal`}>v{activeMeta.version}.JAR</span>
            </h1>
            <p className="text-neutral-300 text-base sm:text-lg leading-relaxed mb-4">
              {selectedBranch === 'v2' ? (
                <>
                  Революционный движок строительства в стиле <strong>Litematica</strong> на базе ванильных <strong>BlockDisplay</strong> (1.20+).
                  Мэр утверждает схему здания в <code className="text-amber-300">/builds</code>, игроки видят точные полупрозрачные призрачные блоки,
                  а система <strong>контроля фасадов</strong> строго требует минимум 50% контакта стен с открытым воздухом, исключая подземные бункеры!
                </>
              ) : (
                <>
                  Полноценный классический плагин градостроительства для Towny.
                  Мэр назначает чанки стройплощадки через <code className="text-blue-300">/plot set build</code>, жители застраивают нужные материалы с защитой от абуза опыта (High-Water Mark),
                  а город получает постоянные зональные баффы.
                </>
              )}
            </p>

            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-1 bg-neutral-800/80 border border-neutral-700 text-neutral-300 text-xs rounded-md">
                Paper / Purpur 1.20 - 1.21+
              </span>
              <span className="px-2.5 py-1 bg-neutral-800/80 border border-neutral-700 text-neutral-300 text-xs rounded-md">
                Towny 0.98+
              </span>
              <span className="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs rounded-md">
                {selectedBranch === 'v2' ? 'Vanilla BlockDisplay (Без модов)' : 'Автономный (Без AuraSkills/mcMMO)'}
              </span>
              <span className={`px-2.5 py-1 ${selectedBranch === 'v2' ? 'bg-amber-500/10 border-amber-500/30 text-amber-300' : 'bg-blue-500/10 border-blue-500/30 text-blue-300'} border text-xs rounded-md font-mono`}>
                Размер: {activeMeta.fileSizeFormatted}
              </span>
            </div>
          </div>

          {/* Action Downloads */}
          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 shrink-0 lg:w-80">
            <button
              id="btn-download-jar"
              onClick={handleDownloadJar}
              className={`inline-flex items-center justify-center gap-3 px-6 py-4 rounded-xl ${selectedBranch === 'v2' ? 'bg-amber-500 hover:bg-amber-400 text-neutral-950 shadow-amber-500/20' : 'bg-blue-500 hover:bg-blue-400 text-neutral-950 shadow-blue-500/20'} font-bold text-base shadow-lg transition-all transform active:scale-95 cursor-pointer`}
            >
              {downloadedJar ? <CheckCircle2 className="w-5 h-5 text-neutral-950" /> : <Download className="w-5 h-5 stroke-[2.5]" />}
              <span>{downloadedJar ? `Скачан (${activeMeta.fileSizeFormatted})` : `Скачать ${activeMeta.jarFileName}`}</span>
            </button>

            <button
              id="btn-download-bundle"
              onClick={handleDownloadBundle}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-neutral-800 hover:bg-neutral-700 border border-neutral-600 text-white text-sm font-medium transition-all cursor-pointer"
            >
              {downloadedBundle ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Box className="w-4 h-4 text-emerald-400" />}
              <span>{downloadedBundle ? 'Bundle скачан (.ZIP)' : `Скачать Bundle ${activeMeta.version} (.ZIP)`}</span>
            </button>
            <button
              id="btn-download-rp"
              onClick={handleDownloadRp}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 text-purple-200 text-sm font-semibold transition-all cursor-pointer shadow-lg shadow-purple-500/10"
            >
              {downloadedRp ? <CheckCircle2 className="w-5 h-5 text-emerald-400" /> : <Palette className="w-5 h-5 text-purple-400" />}
              <span>{downloadedRp ? 'Ресурспак скачан (.ZIP)' : 'Скачать Ресурспак GUI (.ZIP)'}</span>
            </button>

            <button
              id="btn-copy-sha"
              onClick={handleCopySha}
              className="flex items-center justify-between px-3.5 py-2.5 bg-neutral-900/90 border border-neutral-700/80 rounded-lg text-xs text-neutral-400 hover:text-neutral-200 transition-colors"
              title="Нажмите, чтобы скопировать контрольную сумму SHA-256 плагина JAR"
            >
              <span className="truncate mr-2 font-mono">
                SHA-256: {activeMeta.sha256.substring(0, 14)}...
              </span>
              {copiedSha ? (
                <span className="text-emerald-400 flex items-center gap-1 shrink-0">
                  <Check className="w-3.5 h-3.5" /> Скопировано
                </span>
              ) : (
                <span className="flex items-center gap-1 shrink-0 text-neutral-500 hover:text-neutral-300">
                  <Copy className="w-3.5 h-3.5" /> Копия
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Feature Highlights of Selected Branch */}
      {selectedBranch === 'v2' && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-5 mb-8">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2 flex-wrap">
                <span>Особые правила ветки 2.0.0: Система Защиты Фасадов (Анти-Бункер)</span>
                <span className="text-[11px] px-2 py-0.5 rounded bg-amber-900/60 text-amber-300 border border-amber-700 font-mono">
                  wall-contact-min-percent: 50%
                </span>
              </div>
              <p className="text-xs text-neutral-300 mt-1 leading-relaxed">
                В версии 2.0.0 реализован строгий аудит наружных стен здания. Как минимум <strong>50% блоков внешней оболочки</strong> постройки обязаны контактировать с естественным окружением (воздух, листва, трава, цветы). 
                Постройки под землей (Y &lt; 60), закапывание здания в каменные кубы или замуровывание стен блокируется: плагин переводит здание в статус <span className="text-red-400 font-mono font-bold">ENTOMBED</span> (Замуровано), замораживая все городские баффы до восстановления открытых фасадов!
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                <span className="px-2 py-1 rounded bg-neutral-900 text-neutral-300 border border-neutral-700 font-mono">
                  /build facade
                </span>
                <span className="text-neutral-400">— команда для игроков для инспекции контакта стен здания с открытым миром</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Resource Pack Setup Card */}
      <div className="bg-gradient-to-r from-purple-950/30 via-neutral-900 to-neutral-900 border border-purple-500/30 rounded-xl p-5 mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-start sm:items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300 shrink-0 mt-0.5 sm:mt-0">
              <Palette className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2 flex-wrap">
                <span>Кастомный Ресурспак GUI (Фон Меню и Невидимые Слоты)</span>
                <span className="text-[11px] px-2 py-0.5 rounded bg-purple-900/60 text-purple-300 border border-purple-700">
                  Paper / Purpur 1.20 - 1.21+ (pack_format 34)
                </span>
              </div>
              <p className="text-xs text-neutral-300 mt-1">
                Фон генерируется через Minecraft Font Provider (символ <code className="text-purple-300 bg-purple-950/60 px-1 py-0.5 rounded">\uE001</code>). Не требует OptiFine. Подходит как для <code className="text-amber-300">server.properties</code>, так и для ручной папки <code className="text-neutral-200">.minecraft/resourcepacks</code>.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <button
              id="btn-copy-rp-sha"
              onClick={handleCopyRpSha}
              className="inline-flex items-center gap-2 px-3.5 py-2 bg-neutral-800 hover:bg-neutral-700 border border-neutral-600 text-neutral-200 rounded-lg text-xs font-mono transition-colors"
              title="Скопировать SHA-1 для server.properties"
            >
              {copiedRpSha ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-neutral-400" />}
              <span>{copiedRpSha ? 'SHA-1 скопирован!' : `SHA-1: ${RESOURCE_PACK_SHA1.substring(0, 10)}...`}</span>
            </button>

            <button
              onClick={handleDownloadRp}
              className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-purple-600/20 transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadedRp ? 'Скачан!' : 'Скачать ZIP (2.5 KB)'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* TownySieges Master Warfare Plugin Card */}
      <div className="bg-gradient-to-r from-orange-950/40 via-neutral-900 to-amber-950/30 border-2 border-orange-500/60 rounded-2xl p-6 sm:p-7 mb-8 shadow-xl shadow-orange-950/20">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/20 border border-orange-500/40 text-orange-400 text-xs font-bold uppercase tracking-wider mb-3">
              <Flame className="w-3.5 h-3.5 animate-pulse" />
              Новый плагин: TownySieges v1.0.0 (Осадные Лагеря и Таймеры Штурма)
            </div>
            <h3 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
              <span>TownySieges</span>
              <span className="text-xs px-2.5 py-1 rounded bg-orange-500/20 text-orange-300 font-mono border border-orange-500/30">
                v1.0.0.JAR
              </span>
            </h3>
            <p className="text-neutral-300 text-sm leading-relaxed mt-2">
              Плагин тактических осад для Towny: Мэр ставит <strong>осадный лагерь</strong> на нейтральной земле рядом с городом-целью (<code className="text-orange-300">/siege camp &lt;Город&gt;</code>) без необходимости присоединения к своему городу. Лагерь можно расширять смежными чанками (<code className="text-orange-300">/siege expand</code>) с повышенной стоимостью и налогом.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4 text-xs">
              <div className="flex items-center gap-2 text-amber-400">
                <Clock className="w-4 h-4 shrink-0" />
                <span><strong>24 часа подготовки</strong> с ярким Боссбаром (BossBar) и таймером</span>
              </div>
              <div className="flex items-center gap-2 text-red-400">
                <Zap className="w-4 h-4 shrink-0" />
                <span><strong>2 часа активного штурма</strong>: орудия и пушки разрушают блоки</span>
              </div>
              <div className="flex items-center gap-2 text-orange-400">
                <Landmark className="w-4 h-4 shrink-0" />
                <span>Автономные чанки лагеря, повышенная цена и налог</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <Shield className="w-4 h-4 shrink-0" />
                <span>В мирное время город на 100% защищен от любых взрывов</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2.5 shrink-0 lg:w-72">
            <button
              id="btn-download-sieges-jar"
              onClick={(e) => {
                e.preventDefault();
                downloadTownySiegesJar();
              }}
              className="inline-flex items-center justify-center gap-2.5 px-5 py-3.5 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-xl font-bold text-sm shadow-lg shadow-orange-600/30 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4 stroke-[2.5]" />
              <span>Скачать TownySieges .JAR (37 KB)</span>
            </button>

            <button
              onClick={(e) => {
                e.preventDefault();
                downloadTownySiegesBundle();
              }}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-200 rounded-xl text-xs font-medium transition-colors cursor-pointer"
            >
              <Box className="w-3.5 h-3.5 text-neutral-400" />
              <span>Скачать Bundle (.ZIP с исходниками)</span>
            </button>

            <div className="text-[11px] text-neutral-400 text-center font-mono">
              /siege camp &lt;Цель&gt; | /siege expand | /siege info
            </div>
          </div>
        </div>
      </div>

      {/* TownyExplosionUnblocker Companion Plugin Card */}
      <div className="bg-gradient-to-r from-red-950/40 via-neutral-900 to-amber-950/30 border-2 border-red-500/50 rounded-2xl p-6 sm:p-7 mb-8 shadow-xl shadow-red-950/20">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/20 border border-red-500/40 text-red-400 text-xs font-bold uppercase tracking-wider mb-3">
              <Zap className="w-3.5 h-3.5 animate-pulse" />
              Плагин-компаньон: TownyExplosionUnblocker v1.1.0
            </div>
            <h3 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
              <span>TownyExplosionUnblocker</span>
              <span className="text-xs px-2.5 py-1 rounded bg-red-500/20 text-red-300 font-mono border border-red-500/30">
                v1.1.0.JAR
              </span>
            </h3>
            <p className="text-neutral-300 text-sm leading-relaxed mt-2">
              Специализированный модуль снятия защиты Towny от взрывов <strong>ИСКЛЮЧИТЕЛЬНО для динамита/снарядов пушек SiegeCannon во время 2 часов активной осады TownySieges</strong> (по PDC, метаданным, тегам и кастомным именам). В остальное время плагин неактивен, и город полностью защищен.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4 text-xs">
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Разрешает урон пушек SiegeCannon ТОЛЬКО во время 2ч активного штурма</span>
              </div>
              <div className="flex items-center gap-2 text-red-400">
                <Shield className="w-4 h-4 shrink-0" />
                <span>Блокирует обычный TNT, криперов, кристаллы и неактивные осады</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2.5 shrink-0 lg:w-72">
            <button
              id="btn-download-unblocker-jar"
              onClick={(e) => {
                e.preventDefault();
                downloadUnblockerJar();
              }}
              className="inline-flex items-center justify-center gap-2.5 px-5 py-3.5 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold text-sm shadow-lg shadow-red-600/30 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4 stroke-[2.5]" />
              <span>Скачать Unblocker .JAR (15 KB)</span>
            </button>

            <button
              onClick={(e) => {
                e.preventDefault();
                downloadUnblockerBundle();
              }}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-200 rounded-xl text-xs font-medium transition-colors cursor-pointer"
            >
              <Box className="w-3.5 h-3.5 text-neutral-400" />
              <span>Скачать Bundle (.ZIP)</span>
            </button>

            <div className="text-[11px] text-neutral-500 text-center font-mono">
              Команда: /teu reload | status | debug
            </div>
          </div>
        </div>
      </div>

      {/* 3D Cannon Blockbench Model Showcase Card */}
      <div className="bg-gradient-to-r from-amber-950/40 via-neutral-900 to-amber-900/20 border-2 border-amber-500/40 rounded-2xl p-6 sm:p-7 mb-8 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-400 text-xs font-bold uppercase tracking-wider mb-3">
              <Box className="w-3.5 h-3.5" />
              3D Модель Осадной Пушки (1x1 Блок) для Blockbench
            </div>
            <h3 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
              <span>Siege Cannon 1×1 Model</span>
              <span className="text-xs px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 font-mono border border-amber-500/30">
                .bbmodel / .json
              </span>
            </h3>
            <p className="text-neutral-300 text-sm leading-relaxed mt-2">
              Полностью готовая 3D модель осадной пушки на колесах, строго вписанная в габариты 16×16×16 вокселей (1x1 блок).
              Включает проект Blockbench (.bbmodel), JSON модель для ресурспака и CustomModelData: 7001.
            </p>
            <div className="flex flex-wrap items-center gap-3 mt-3 text-xs text-neutral-400">
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-amber-300 font-mono">20 кубов</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300 font-mono">CustomModelData: 7001</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300 font-mono">Item Display / ArmorStand</span>
            </div>
          </div>

          <div className="flex flex-col gap-2.5 shrink-0 lg:w-72">
            <button
              onClick={() => {
                const nav = (window as any).__setAppTab;
                if (nav) nav('cannon');
                else import('../utils/downloadHelpers').then(m => m.downloadCannonBbmodel());
              }}
              className="inline-flex items-center justify-center gap-2 px-5 py-3.5 bg-amber-500 hover:bg-amber-400 text-neutral-950 rounded-xl font-bold text-sm shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
            >
              <Eye className="w-4 h-4" />
              <span>3D Просмотр и Скачать</span>
            </button>

            <button
              onClick={(e) => {
                e.preventDefault();
                import('../utils/downloadHelpers').then(m => m.downloadCannonBbmodel());
              }}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-200 rounded-xl text-xs font-medium transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-amber-400" />
              <span>Скачать .bbmodel (Blockbench)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Direct Server Install Snippet */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg ${selectedBranch === 'v2' ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-blue-500/10 border-blue-500/30 text-blue-400'} border flex items-center justify-center shrink-0`}>
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white flex items-center gap-2">
                <span>Установка на хостинг Pterodactyl / Linux</span>
                <span className={`text-[11px] px-2 py-0.5 rounded ${selectedBranch === 'v2' ? 'bg-amber-950 text-amber-300 border-amber-800' : 'bg-blue-950 text-blue-300 border-blue-800'} border font-mono`}>
                  Ветка {activeMeta.version}
                </span>
              </div>
              <div className="text-xs text-neutral-400">
                Распаковка в папку <code className="text-amber-300">plugins/{activeMeta.jarFileName}</code> одной командой в терминале сервера.
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              id="btn-copy-base64"
              onClick={handleCopyBase64}
              className={`inline-flex items-center gap-2 px-4 py-2.5 ${selectedBranch === 'v2' ? 'bg-amber-500/10 hover:bg-amber-500/20 border-amber-500/40 text-amber-300' : 'bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/40 text-blue-300'} border rounded-lg text-xs font-semibold transition-colors`}
              title="Скопировать команду распаковки Base64 для терминала сервера"
            >
              {copiedB64 ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copiedB64 ? 'Команда скопирована!' : `Скопировать Base64 команду для ${activeMeta.version}`}</span>
            </button>

            <button
              onClick={() => onNavigateTab('guide')}
              className="px-3.5 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs rounded-lg transition-colors border border-neutral-700"
            >
              Инструкция
            </button>
          </div>
        </div>
      </div>

      {/* Feature Pillar Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl p-5 hover:border-amber-500/40 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4">
            <Eye className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white mb-2">
            {selectedBranch === 'v2' ? '3D Голограммы BlockDisplay' : 'Чанковые Участки Towny'}
          </h3>
          <p className="text-sm text-neutral-400 leading-relaxed">
            {selectedBranch === 'v2' 
              ? 'Ванильные полупрозрачные блоки без клиентских модов. Игроки четко видят, какой блок и в какую координату нужно поставить.'
              : 'Мэр назначает чанки через /plot set build. Плагин строго проверяет владение чанками, права мэра и помощников.'}
          </p>
        </div>

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl p-5 hover:border-emerald-500/40 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
            <Zap className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white mb-2">Навык «Архитектор»</h3>
          <p className="text-sm text-neutral-400 leading-relaxed">
            Опыт начисляется за установку строительных блоков по чертежам с защитой от абуза (High-Water Mark).
            Статистика доступна в <code className="text-emerald-300">/build stats</code>.
          </p>
        </div>

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl p-5 hover:border-red-500/40 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 mb-4">
            <Shield className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white mb-2">
            {selectedBranch === 'v2' ? 'Осады и Осадный TNT' : 'Зоны Баффов и Осады'}
          </h3>
          <p className="text-sm text-neutral-400 leading-relaxed">
            {selectedBranch === 'v2'
              ? 'Осадный динамит (Siege TNT) способен разрушать обсидиановые укрепления. Поврежденные здания теряют баффы до восстановления блоков!'
              : '1x1 чанк — радиус 5 чанков; 2x1 — город; 2x2 — вся карта. Баффы только жителям. При прочности < 70% баффы замораживаются.'}
          </p>
        </div>

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl p-5 hover:border-purple-500/40 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
            <Award className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white mb-2">Мировые Чудеса (2x2)</h3>
          <p className="text-sm text-neutral-400 leading-relaxed">
            Уникальные строения 2x2 (1 на весь мир). Даруют мощнейшие баффы (Спешка II, Сопротивление)
            гражданам своего города в любой точке карты!
          </p>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => onNavigateTab('editor')}
          className="flex items-center gap-4 p-4 rounded-xl bg-neutral-900/80 hover:bg-neutral-800/90 border border-neutral-800 text-left transition-all group cursor-pointer"
        >
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
            <FileCode2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white group-hover:text-amber-300 transition-colors">
              Редактор config.yml & buildings.yml
            </div>
            <div className="text-xs text-neutral-400">Настройка баффов, параметров стен и скачивание YAML</div>
          </div>
        </button>

        <button
          onClick={() => onNavigateTab('guide')}
          className="flex items-center gap-4 p-4 rounded-xl bg-neutral-900/80 hover:bg-neutral-800/90 border border-neutral-800 text-left transition-all group cursor-pointer"
        >
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white group-hover:text-emerald-300 transition-colors">
              Инструкция установки и команды
            </div>
            <div className="text-xs text-neutral-400">Команды /builds, /build facade, права и настройка</div>
          </div>
        </button>

        <button
          onClick={() => onNavigateTab('sources')}
          className="flex items-center gap-4 p-4 rounded-xl bg-neutral-900/80 hover:bg-neutral-800/90 border border-neutral-800 text-left transition-all group cursor-pointer"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
              Просмотр исходного Java кода
            </div>
            <div className="text-xs text-neutral-400">Исходные классы веток v2.0.0 (18 классов) и v1.5.0 (14 классов)</div>
          </div>
        </button>
      </div>

      {/* Version History & Changelog */}
      <div className="mt-12">
        <ChangelogSection />
      </div>
    </div>
  );
};