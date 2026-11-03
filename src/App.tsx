import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { PluginsDownloadHub } from './components/PluginsDownloadHub';
import { TownyRespawnSimulator } from './components/TownyRespawnSimulator';
import { ChunkSiegeCaptureSimulator } from './components/ChunkSiegeCaptureSimulator';
import { JarDownloadHero } from './components/JarDownloadHero';
import { InstallationGuide } from './components/InstallationGuide';
import { ConfigBlueprintEditor } from './components/ConfigBlueprintEditor';
import { JavaSourceViewer } from './components/JavaSourceViewer';
import { ModelPreviewHub } from './components/ModelPreviewHub';
import { PLUGIN_METADATA } from './data/javaSources';
import { Download, Shield, Terminal, CheckCircle2, Map, Box, Sparkles, ChevronRight, Castle, Flag, Flame, Swords } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'download' | 'simulator' | 'sieges' | 'editor' | 'guide' | 'sources' | 'cannon'>('download');

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col font-sans selection:bg-amber-500 selection:text-neutral-950">
      {/* Navigation Header */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Body */}
      <main className="flex-1">
        {activeTab === 'download' && (
          <>
            <PluginsDownloadHub />

            {/* Tactical Chunk Capture Interactive Showcase Banner */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div className="bg-gradient-to-r from-red-950/60 via-neutral-900 to-neutral-900 border border-red-500/40 rounded-2xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
                <div className="absolute top-0 right-0 w-80 h-80 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />
                <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                  <div className="max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono font-medium mb-3">
                      <Flag className="w-3.5 h-3.5 text-red-400" />
                      <span>TownySieges v1.5.0</span>
                      <span className="px-1.5 py-0.2 bg-red-500 text-white font-bold rounded text-[10px]">NEW</span>
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2">
                      <span>Почанковый Захват, Штурмовой Флаг и /siege disband</span>
                    </h2>
                    <p className="text-sm text-neutral-300 mt-2 leading-relaxed">
                      Интерактивный симулятор установки Штурмового Флага с лучом маяка, расчетом коэффициента перевеса сил, откатом прогресса за защитников (создание официальных Аванпостов Outpost), а также командами расформирования лагеря <b>/siege disband</b> и пропуском подготовки <b>/siege admin skip-prep</b>.
                    </p>
                    <div className="flex flex-wrap gap-2 mt-4 text-xs font-mono">
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-950 border border-neutral-800 text-red-400 font-semibold flex items-center gap-1.5">
                        <Flag className="w-3.5 h-3.5" /> Луч Маяка & BossBar
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-950 border border-neutral-800 text-amber-400 font-semibold flex items-center gap-1.5">
                        <Swords className="w-3.5 h-3.5" /> Формула Перевеса Сил
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-950 border border-neutral-800 text-cyan-400 font-semibold flex items-center gap-1.5">
                        <Shield className="w-3.5 h-3.5" /> Возврат Чанков & Аванпосты
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto shrink-0">
                    <button
                      onClick={() => setActiveTab('sieges')}
                      className="px-6 py-3.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm shadow-lg shadow-red-600/25 transition-all flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <Flag className="w-4 h-4" />
                      <span>Открыть Симулятор Штурма →</span>
                    </button>
                  </div>
                </div>
              </div>
            </section>

            {/* Featured 3D Models & Architecture Showcase Section */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="bg-gradient-to-r from-neutral-900 via-neutral-900/95 to-amber-950/40 border border-amber-500/30 rounded-2xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
                <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
                <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                  <div className="max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-medium mb-3">
                      <Box className="w-3.5 h-3.5" />
                      <span>Раздел 3D Моделей</span>
                      <span className="px-1.5 py-0.2 bg-amber-400 text-neutral-950 font-bold rounded text-[10px]">3D</span>
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2">
                      <span>Предпросмотр 3D Моделей и Архитектура</span>
                    </h2>
                    <p className="text-sm text-neutral-300 mt-2 leading-relaxed">
                      Интерактивный 3D-просмотрщик моделей Blockbench (32-ф пушка, мортира, баллиста, таран), послойные схемы 7 зданий полиса с изометрической проекцией, а также профессиональные мануалы по постройке красивых зданий (правило 3D-глубины, градиенты стен, нависающие крыши).
                    </p>
                    <div className="flex flex-wrap gap-2 mt-4 text-xs font-mono">
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-950 border border-neutral-800 text-amber-400 font-semibold flex items-center gap-1.5">
                        <Box className="w-3.5 h-3.5" /> 4 3D Орудия Blockbench
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-950 border border-neutral-800 text-cyan-400 font-semibold flex items-center gap-1.5">
                        <Castle className="w-3.5 h-3.5" /> 7 Зданий со слайдером слоев
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-950 border border-neutral-800 text-neutral-300 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Мануалы и палитры блоков
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto shrink-0">
                    <button
                      onClick={() => setActiveTab('cannon')}
                      className="px-6 py-3.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-sm shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <Box className="w-4 h-4" />
                      <span>Открыть раздел 3D моделей →</span>
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <TownyRespawnSimulator />
            <JarDownloadHero
              onNavigateTab={(tab) => setActiveTab(tab)}
            />
          </>
        )}

        {activeTab === 'simulator' && (
          <TownyRespawnSimulator />
        )}

        {activeTab === 'sieges' && (
          <ChunkSiegeCaptureSimulator />
        )}

        {activeTab === 'editor' && (
          <ConfigBlueprintEditor />
        )}

        {activeTab === 'guide' && (
          <InstallationGuide />
        )}

        {activeTab === 'sources' && (
          <JavaSourceViewer />
        )}

        {activeTab === 'cannon' && (
          <ModelPreviewHub />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-800 bg-neutral-950/80 py-8 text-neutral-400 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white font-mono">Towny Suite 2026</span>
            <span className="text-neutral-500">4 Plugins</span>
            <span className="text-neutral-600">•</span>
            <span>Для Paper / Purpur 1.20+</span>
          </div>
          <div className="flex items-center gap-4 flex-wrap">
            <button
              onClick={() => setActiveTab('simulator')}
              className="hover:text-cyan-400 transition-colors font-medium text-neutral-300 flex items-center gap-1"
            >
              <Map className="w-3.5 h-3.5" />
              <span>BlueMap & /respawn</span>
            </button>
            <button
              onClick={() => setActiveTab('cannon')}
              className="hover:text-amber-400 transition-colors font-semibold text-amber-400 flex items-center gap-1"
            >
              <Box className="w-3.5 h-3.5" />
              <span>Предпросмотр моделей</span>
            </button>
            <button
              onClick={() => setActiveTab('guide')}
              className="hover:text-neutral-200 transition-colors"
            >
              Команды и права
            </button>
            <button
              onClick={() => setActiveTab('editor')}
              className="hover:text-neutral-200 transition-colors"
            >
              Редактор YAML
            </button>
            <button
              onClick={() => setActiveTab('sources')}
              className="hover:text-neutral-200 transition-colors"
            >
              Исходный код
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
