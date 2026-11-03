import React from 'react';
import { Download, Sliders, BookOpen, Code2, Server, Box, Map, Flag } from 'lucide-react';
import { PLUGIN_METADATA } from '../data/javaSources';
import { downloadJarFile } from '../utils/downloadHelpers';

interface NavbarProps {
  activeTab: 'download' | 'simulator' | 'sieges' | 'editor' | 'guide' | 'sources' | 'cannon';
  setActiveTab: (tab: 'download' | 'simulator' | 'sieges' | 'editor' | 'guide' | 'sources' | 'cannon') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="sticky top-0 z-50 bg-neutral-950/90 backdrop-blur-md border-b border-neutral-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('download')}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 via-amber-500 to-orange-500 flex items-center justify-center text-neutral-950 font-black text-lg shadow-md shadow-amber-500/20">
              ⛏
            </div>
            <div>
              <div className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                <span>Towny Plugin Suite</span>
                <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[11px] font-mono font-normal">
                  4 Plugins
                </span>
              </div>
              <div className="text-xs text-neutral-400 hidden sm:block">
                Minecraft Paper 1.20+ · Architecture, Respawn, Sieges & Unblocker
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab('download')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'download'
                  ? 'bg-neutral-800 text-amber-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Download className="w-4 h-4" />
              <span>Загрузка JAR</span>
            </button>

            <button
              onClick={() => setActiveTab('simulator')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'simulator'
                  ? 'bg-neutral-800 text-cyan-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Map className="w-4 h-4 text-cyan-400" />
              <span className="hidden sm:inline">BlueMap & Войны Наций</span>
              <span className="sm:hidden">Войны</span>
            </button>

            <button
              onClick={() => setActiveTab('sieges')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'sieges'
                  ? 'bg-neutral-800 text-red-400 border border-neutral-700 shadow-sm shadow-red-500/10'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Flag className="w-4 h-4 text-red-400" />
              <span className="hidden sm:inline">Штурм и Флаги</span>
              <span className="sm:hidden">Штурм</span>
              <span className="px-1.5 py-0.2 bg-red-500/20 text-red-400 font-bold rounded text-[10px]">
                NEW
              </span>
            </button>

            <button
              onClick={() => setActiveTab('editor')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'editor'
                  ? 'bg-neutral-800 text-amber-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Sliders className="w-4 h-4" />
              <span className="hidden sm:inline">Редактор</span>
              <span className="sm:hidden">Конфиг</span>
            </button>

            <button
              onClick={() => setActiveTab('guide')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'guide'
                  ? 'bg-neutral-800 text-amber-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Команды</span>
            </button>

            <button
              onClick={() => setActiveTab('sources')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'sources'
                  ? 'bg-neutral-800 text-amber-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Code2 className="w-4 h-4" />
              <span className="hidden sm:inline">Java Код</span>
              <span className="sm:hidden">Код</span>
            </button>

            <button
              onClick={() => setActiveTab('cannon')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors relative ${
                activeTab === 'cannon'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm shadow-amber-500/20'
                  : 'text-neutral-300 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Box className="w-4 h-4 text-amber-400" />
              <span className="hidden lg:inline font-semibold">Предпросмотр моделей</span>
              <span className="hidden sm:inline lg:hidden font-semibold">Модели 3D</span>
              <span className="sm:hidden font-semibold">Модели</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-neutral-950 font-mono">
                3D
              </span>
            </button>

            {/* Quick direct download button */}
            <button
              id="btn-navbar-download-jar"
              onClick={() => downloadJarFile()}
              className="ml-2 hidden md:inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-xs shadow-sm transition-all cursor-pointer"
              title="Скачать чистый бинарник JAR напрямую из памяти"
            >
              <Download className="w-3.5 h-3.5" />
              <span>.JAR</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
