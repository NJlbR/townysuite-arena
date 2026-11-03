import React, { useState } from 'react';
import { Download, Copy, Check, Sliders, Plus, Trash2, FileText, Sparkles, RefreshCw } from 'lucide-react';

interface BlueprintItem {
  id: string;
  name: string;
  nameRu: string;
  description: string;
  icon: string;
  requiredMcmmoLevel: number;
  isWorldWonder: boolean;
  widthChunks: number;
  lengthChunks: number;
  widthX: number;
  heightY: number;
  lengthZ: number;
  resources: { material: string; count: number }[];
  buffSummary: string;
}

export const ConfigBlueprintEditor: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'settings' | 'buildings' | 'yaml'>('buildings');
  const [copiedYaml, setCopiedYaml] = useState(false);

  // Settings state
  const [enforceTownyClaims, setEnforceTownyClaims] = useState(true);
  const [enforceMcmmoLevel, setEnforceMcmmoLevel] = useState(true);
  const [mcmmoSkillName, setMcmmoSkillName] = useState('BUILDING');
  const [mcmmoXpPerBlock, setMcmmoXpPerBlock] = useState(15);
  const [buffSuspensionHealth, setBuffSuspensionHealth] = useState(70.0);
  const [buffCheckInterval, setBuffCheckInterval] = useState(5);

  // Blueprints state
  const [blueprints, setBlueprints] = useState<BlueprintItem[]>([
    {
      id: 'hospital',
      name: 'City Hospital',
      nameRu: 'Городская Больница',
      description: 'Дарует всем гражданам города +1 постоянное Сердце (2 HP) и регенерацию.',
      icon: 'RED_WOOL',
      requiredMcmmoLevel: 20,
      isWorldWonder: false,
      widthChunks: 1,
      lengthChunks: 1,
      widthX: 12,
      heightY: 8,
      lengthZ: 12,
      resources: [
        { material: 'STONE_BRICKS', count: 128 },
        { material: 'WHITE_CONCRETE', count: 64 },
        { material: 'RED_WOOL', count: 32 },
        { material: 'GLASS', count: 32 }
      ],
      buffSummary: 'Health Boost (+1 Сердце), Regeneration I'
    },
    {
      id: 'barracks',
      name: 'Military Barracks',
      nameRu: 'Военные Казармы',
      description: 'Увеличивает силу и выносливость защитников города при отражении осад (1x2 чанка).',
      icon: 'IRON_SWORD',
      requiredMcmmoLevel: 35,
      isWorldWonder: false,
      widthChunks: 1,
      lengthChunks: 2,
      widthX: 14,
      heightY: 9,
      lengthZ: 28,
      resources: [
        { material: 'STONE_BRICKS', count: 160 },
        { material: 'COBBLESTONE', count: 80 },
        { material: 'OAK_PLANKS', count: 60 },
        { material: 'IRON_BLOCK', count: 4 }
      ],
      buffSummary: 'Strength I, Speed I'
    },
    {
      id: 'library',
      name: 'Arcane Library',
      nameRu: 'Библиотека Чар',
      description: 'Дает бонус к получаемому опыту mcMMO во всех профессиях для жителей города.',
      icon: 'ENCHANTING_TABLE',
      requiredMcmmoLevel: 50,
      isWorldWonder: false,
      widthChunks: 1,
      lengthChunks: 1,
      widthX: 10,
      heightY: 10,
      lengthZ: 10,
      resources: [
        { material: 'BOOKSHELF', count: 64 },
        { material: 'OBSIDIAN', count: 16 },
        { material: 'DARK_OAK_PLANKS', count: 96 },
        { material: 'LAPIS_BLOCK', count: 8 }
      ],
      buffSummary: 'XP Boost (+25% mcMMO)'
    },
    {
      id: 'watchtower',
      name: 'City Watchtower',
      nameRu: 'Дозорная Башня',
      description: 'Предупреждает о приближении врагов и дает жителям ночное зрение.',
      icon: 'SPYGLASS',
      requiredMcmmoLevel: 15,
      isWorldWonder: false,
      widthChunks: 1,
      lengthChunks: 1,
      widthX: 8,
      heightY: 24,
      lengthZ: 8,
      resources: [
        { material: 'STONE_BRICKS', count: 180 },
        { material: 'COBBLESTONE', count: 90 },
        { material: 'LADDER', count: 24 },
        { material: 'LANTERN', count: 8 }
      ],
      buffSummary: 'Night Vision'
    },
    {
      id: 'sun_pyramid',
      name: 'Great Sun Pyramid',
      nameRu: 'Великая Пирамида Солнца',
      description: 'ЧУДО СВЕТА. На весь мир может быть только 1! Требует 2x2 чанка (4 участка).',
      icon: 'GOLD_BLOCK',
      requiredMcmmoLevel: 80,
      isWorldWonder: true,
      widthChunks: 2,
      lengthChunks: 2,
      widthX: 32,
      heightY: 28,
      lengthZ: 32,
      resources: [
        { material: 'SANDSTONE', count: 350 },
        { material: 'GOLD_BLOCK', count: 16 },
        { material: 'BEACON', count: 1 },
        { material: 'NETHERITE_INGOT', count: 1 }
      ],
      buffSummary: 'Haste II, Resistance I (Мировое Чудо)'
    },
    {
      id: 'town_hall',
      name: 'Town Hall',
      nameRu: 'Мэрия Города',
      description: 'Сердце города (2x2 чанка). Обладает Щитом Мэрии, защищающим полис в военное время!',
      icon: 'BELL',
      requiredMcmmoLevel: 25,
      isWorldWonder: false,
      widthChunks: 2,
      lengthChunks: 2,
      widthX: 32,
      heightY: 8,
      lengthZ: 32,
      resources: [
        { material: 'STONE_BRICKS', count: 738 },
        { material: 'DARK_OAK_PLANKS', count: 640 },
        { material: 'DEEPSLATE_BRICKS', count: 172 },
        { material: 'GLASS', count: 60 },
        { material: 'IRON_BARS', count: 46 },
        { material: 'LANTERN', count: 8 },
        { material: 'GOLD_BLOCK', count: 8 },
        { material: 'BELL', count: 1 }
      ],
      buffSummary: 'Hero of the Village I, Town Shield (+300 HP)'
    },
    {
      id: 'city_wall',
      name: 'Fortified City Wall',
      nameRu: 'Городская Стена',
      description: 'Фортификационный вал (2x1 чанка). 2x взрывоустойчивость и +100 HP к Щиту Мэрии за каждую стену!',
      icon: 'BRICKS',
      requiredMcmmoLevel: 10,
      isWorldWonder: false,
      widthChunks: 2,
      lengthChunks: 1,
      widthX: 32,
      heightY: 6,
      lengthZ: 16,
      resources: [
        { material: 'STONE_BRICKS', count: 1054 },
        { material: 'COBBLESTONE', count: 254 },
        { material: 'CRACKED_STONE_BRICKS', count: 164 },
        { material: 'IRON_BARS', count: 20 },
        { material: 'LANTERN', count: 4 }
      ],
      buffSummary: 'Wall Fortification (2x Blast Res), +100 Shield HP'
    }
  ]);

  const generateConfigYaml = () => {
    return `# ========================================================
# TownyArchitecture Plugin Configuration
# Auto-generated by Config Studio
# ========================================================

settings:
  enforce-towny-claims: ${enforceTownyClaims}
  enforce-mcmmo-level: ${enforceMcmmoLevel}
  mcmmo-skill-name: "${mcmmoSkillName}"
  mcmmo-xp-per-block: ${mcmmoXpPerBlock}
  buff-suspension-health-percent: ${buffSuspensionHealth}
  buff-check-interval-seconds: ${buffCheckInterval}
  particles-enabled: false
  thin-contours-enabled: true
  bossbar-progress-enabled: true
  sound-effects-enabled: true

messages:
  prefix: "&6[TownyBuilds]&r "
  no-permission: "&cУ вас нет прав на использование этой команды!"
  not-in-town: "&cВы должны состоять в городе для использования этой функции!"
  not-mayor-or-builder: "&cТолько мэр, помощник или назначенный строитель могут возводить городские здания!"
  outside-town-bounds: "&cВыделенная территория выходит за пределы границ вашего города!"
  mcmmo-level-too-low: "&cВаш уровень mcMMO Стройки (%level%) ниже требуемого (%required%)!"
  wonder-already-built: "&4[!] Это Чудо Света уже воздвигнуто городом %town% и заблокировано навсегда!"
  project-started: "&aПроект здания &e%name% &aутвержден! Размещайте необходимые блоки в контуре."
  building-completed: "&6&l[ГОРОД]&a Строительство &e%name% &aзавершено! Все пассивные баффы активированы!"
  building-damaged: "&c&l[ОСАДА]&e Здание &6%name% &cповреждено (%health%%)! Баффы отключены до починки!"
  building-repaired: "&aЗдание &e%name% &aвосстановлено до 100%%! Баффы снова действуют."`;
  };

  const generateBuildingsYaml = () => {
    let yaml = `# ========================================================\n# TownyArchitecture Blueprints Database\n# ========================================================\n\nblueprints:\n`;
    blueprints.forEach(bp => {
      yaml += `  ${bp.id}:\n`;
      yaml += `    name: "${bp.name}"\n`;
      yaml += `    name-ru: "${bp.nameRu}"\n`;
      yaml += `    description: "${bp.description}"\n`;
      yaml += `    icon: "${bp.icon}"\n`;
      yaml += `    required-mcmmo-level: ${bp.requiredMcmmoLevel}\n`;
      yaml += `    is-world-wonder: ${bp.isWorldWonder}\n`;
      yaml += `    chunk-footprint:\n`;
      yaml += `      width-chunks: ${bp.widthChunks}\n`;
      yaml += `      length-chunks: ${bp.lengthChunks}\n`;
      yaml += `    dimensions:\n`;
      yaml += `      width-x: ${bp.widthX}\n`;
      yaml += `      height-y: ${bp.heightY}\n`;
      yaml += `      length-z: ${bp.lengthZ}\n`;
      yaml += `    resources:\n`;
      bp.resources.forEach(r => {
        yaml += `      ${r.material}: ${r.count}\n`;
      });
      yaml += `    buffs:\n`;
      if (bp.id === 'hospital') {
        yaml += `      health-boost-hearts: 1\n      regeneration-level: 1\n`;
      } else if (bp.id === 'barracks') {
        yaml += `      strength-level: 1\n      speed-level: 1\n`;
      } else if (bp.id === 'sun_pyramid') {
        yaml += `      haste-level: 2\n      resistance-level: 1\n`;
      } else {
        yaml += `      speed-level: 1\n`;
      }
      yaml += `\n`;
    });
    return yaml;
  };

  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/yaml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const copyYaml = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedYaml(true);
    setTimeout(() => setCopiedYaml(false), 2000);
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Sliders className="w-7 h-7 text-amber-400" />
            Визуальный редактор конфигов
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base">
            Настройте параметры сервера и чертежи зданий, затем скачайте готовые <code className="text-amber-300">config.yml</code> и <code className="text-amber-300">buildings.yml</code>.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => downloadFile(generateConfigYaml(), 'config.yml')}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium border border-neutral-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-amber-400" />
            config.yml
          </button>
          <button
            onClick={() => downloadFile(generateBuildingsYaml(), 'buildings.yml')}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium border border-neutral-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            buildings.yml
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-neutral-800 mb-6">
        <button
          onClick={() => setActiveTab('buildings')}
          className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
            activeTab === 'buildings'
              ? 'border-amber-400 text-amber-400'
              : 'border-transparent text-neutral-400 hover:text-neutral-200'
          }`}
        >
          Каталог чертежей ({blueprints.length})
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
            activeTab === 'settings'
              ? 'border-amber-400 text-amber-400'
              : 'border-transparent text-neutral-400 hover:text-neutral-200'
          }`}
        >
          Настройки ядра (config.yml)
        </button>
        <button
          onClick={() => setActiveTab('yaml')}
          className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
            activeTab === 'yaml'
              ? 'border-amber-400 text-amber-400'
              : 'border-transparent text-neutral-400 hover:text-neutral-200'
          }`}
        >
          Предпросмотр YAML
        </button>
      </div>

      {/* Tab: Buildings */}
      {activeTab === 'buildings' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {blueprints.map((bp) => (
              <div key={bp.id} className="bg-neutral-900 border border-neutral-800 rounded-xl p-5">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-white">{bp.nameRu}</span>
                      {bp.isWorldWonder && (
                        <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold uppercase tracking-wider">
                          Чудо Света
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-neutral-400">{bp.name} (id: {bp.id})</div>
                  </div>
                  <span className="px-2 py-1 rounded bg-neutral-800 text-neutral-300 text-xs font-mono">
                    {bp.icon}
                  </span>
                </div>

                <p className="text-xs text-neutral-300 mb-4">{bp.description}</p>

                <div className="grid grid-cols-3 gap-2 text-xs mb-4">
                  <div className="bg-neutral-950 p-2 rounded border border-neutral-800/80">
                    <span className="text-neutral-500 block">Участок:</span>
                    <span className="text-emerald-400 font-mono font-bold">{bp.widthChunks}×{bp.lengthChunks} чанк</span>
                  </div>
                  <div className="bg-neutral-950 p-2 rounded border border-neutral-800/80">
                    <span className="text-neutral-500 block">Размер (X×Z×Y):</span>
                    <span className="text-white font-mono">{bp.widthX}×{bp.lengthZ}×{bp.heightY}</span>
                  </div>
                  <div className="bg-neutral-950 p-2 rounded border border-neutral-800/80">
                    <span className="text-neutral-500 block">mcMMO Стройка:</span>
                    <span className="text-amber-400 font-bold">{bp.requiredMcmmoLevel}+</span>
                  </div>
                </div>

                <div className="mb-3">
                  <span className="text-xs text-neutral-500 block mb-1.5">Требуемые материалы:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {bp.resources.map((r, i) => (
                      <span key={i} className="px-2 py-1 bg-neutral-800 text-neutral-300 rounded text-[11px] font-mono">
                        {r.material}: <strong className="text-amber-300">{r.count}</strong>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="text-xs text-emerald-400 bg-emerald-950/20 border border-emerald-900/40 p-2 rounded">
                  ✦ Баффы: {bp.buffSummary}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Settings */}
      {activeTab === 'settings' && (
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <label className="flex items-center justify-between p-3 rounded-lg bg-neutral-950 border border-neutral-800 cursor-pointer">
                <div>
                  <div className="text-sm font-semibold text-white">Проверка чанков города Towny</div>
                  <div className="text-xs text-neutral-400">Требовать, чтобы обе точки /pos 1 и /pos 2 находились в городе игрока</div>
                </div>
                <input
                  type="checkbox"
                  checked={enforceTownyClaims}
                  onChange={(e) => setEnforceTownyClaims(e.target.checked)}
                  className="w-5 h-5 accent-amber-500 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg bg-neutral-950 border border-neutral-800 cursor-pointer">
                <div>
                  <div className="text-sm font-semibold text-white">Проверка РПГ-навыка mcMMO</div>
                  <div className="text-xs text-neutral-400">Блокировать старт строительства, если уровень навыка ниже порога</div>
                </div>
                <input
                  type="checkbox"
                  checked={enforceMcmmoLevel}
                  onChange={(e) => setEnforceMcmmoLevel(e.target.checked)}
                  className="w-5 h-5 accent-amber-500 rounded"
                />
              </label>

              <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-800">
                <div className="text-sm font-semibold text-white mb-1">Название навыка mcMMO</div>
                <div className="text-xs text-neutral-400 mb-2">Навык, используемый для проверки (BUILDING, REPAIR или MINING)</div>
                <input
                  type="text"
                  value={mcmmoSkillName}
                  onChange={(e) => setMcmmoSkillName(e.target.value)}
                  className="w-full px-3 py-1.5 bg-neutral-900 border border-neutral-700 rounded text-sm text-white font-mono"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-800">
                <div className="text-sm font-semibold text-white mb-1">Опыт mcMMO за 1 установленный блок</div>
                <div className="text-xs text-neutral-400 mb-2">Начисляется игроку при каждом блоке в контуре постройки</div>
                <input
                  type="number"
                  value={mcmmoXpPerBlock}
                  onChange={(e) => setMcmmoXpPerBlock(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 bg-neutral-900 border border-neutral-700 rounded text-sm text-white font-mono"
                />
              </div>

              <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-800">
                <div className="text-sm font-semibold text-white mb-1">Порог отключения баффов при осаде (%): {buffSuspensionHealth}%</div>
                <div className="text-xs text-neutral-400 mb-2">Если прочность здания ниже этого % от взрывов, баффы замораживаются</div>
                <input
                  type="range"
                  min="20"
                  max="90"
                  step="5"
                  value={buffSuspensionHealth}
                  onChange={(e) => setBuffSuspensionHealth(parseFloat(e.target.value))}
                  className="w-full accent-amber-500"
                />
              </div>

              <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-800">
                <div className="text-sm font-semibold text-white mb-1">Интервал обновления баффов (секунды): {buffCheckInterval}с</div>
                <div className="text-xs text-neutral-400 mb-2">Частота наложения эффектов зелий гражданам онлайн</div>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={buffCheckInterval}
                  onChange={(e) => setBuffCheckInterval(parseInt(e.target.value) || 5)}
                  className="w-full accent-emerald-500"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: YAML Preview */}
      {activeTab === 'yaml' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-amber-400">config.yml</span>
              <button
                onClick={() => copyYaml(generateConfigYaml())}
                className="text-xs text-neutral-400 hover:text-white flex items-center gap-1"
              >
                {copiedYaml ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />} Копия
              </button>
            </div>
            <pre className="text-xs font-mono text-neutral-300 max-h-96 overflow-y-auto whitespace-pre-wrap p-2 bg-neutral-900 rounded">
              {generateConfigYaml()}
            </pre>
          </div>

          <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-emerald-400">buildings.yml</span>
              <button
                onClick={() => copyYaml(generateBuildingsYaml())}
                className="text-xs text-neutral-400 hover:text-white flex items-center gap-1"
              >
                {copiedYaml ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />} Копия
              </button>
            </div>
            <pre className="text-xs font-mono text-neutral-300 max-h-96 overflow-y-auto whitespace-pre-wrap p-2 bg-neutral-900 rounded">
              {generateBuildingsYaml()}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
