import React, { useState } from 'react';
import { Terminal, Shield, Check, Copy, Folder, AlertCircle, Sparkles, BookOpen, Layers, Wrench, UploadCloud, CheckCircle2, FileCheck, Download, MapPin, Eye, Lock, ShieldAlert, Box, Flame, Clock, Map } from 'lucide-react';
import { PLUGIN_METADATA_V1, PLUGIN_METADATA_V2 } from '../data/javaSources';
import { JAR_BASE64_V1, JAR_BASE64_V2 } from '../data/jarBase64';
import { RESOURCE_PACK_SHA1 } from '../data/resourcePackBase64';
import { downloadJarFile } from '../utils/downloadHelpers';
import { JarIntegrityChecker } from './JarIntegrityChecker';

export const InstallationGuide: React.FC = () => {
  const [selectedBranch, setSelectedBranch] = useState<'v2' | 'v1'>('v2');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [copiedB64, setCopiedB64] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const activeMeta = selectedBranch === 'v2' ? PLUGIN_METADATA_V2 : PLUGIN_METADATA_V1;
  const activeB64 = selectedBranch === 'v2' ? JAR_BASE64_V2 : JAR_BASE64_V1;

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const copyBase64Command = () => {
    const cmd = `rm -f plugins/TownyArchitecture-*.jar\ncat << 'EOF' | base64 -d > plugins/${activeMeta.jarFileName}\n${activeB64}\nEOF\nls -lh plugins/${activeMeta.jarFileName}`;
    navigator.clipboard.writeText(cmd);
    setCopiedB64(true);
    setTimeout(() => setCopiedB64(false), 2500);
  };

  const handleDownload = () => {
    downloadJarFile(selectedBranch, activeMeta.jarFileName);
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 3500);
  };

  const steps = [
    {
      title: `1. Загрузка плагина v${activeMeta.version} в /plugins/`,
      desc: `Скачайте ${activeMeta.jarFileName} через кнопку на сайте или используйте терминал. В панели управления Pterodactyl перейдите в «Файлы» (Files) → папку «plugins», удалите старый jar и загрузите новый файл.`,
      command: `# Способ через веб-панель Pterodactyl:
# 1. Нажмите «Скачать ${activeMeta.jarFileName}»
# 2. В панели хостинга: Files -> plugins -> Upload -> выберите файл ${activeMeta.jarFileName}
# Либо используйте однострочную команду терминала ниже.`,
    },
    {
      title: "2. Назначение строительных участков: /plot set build",
      desc: "Мэр или помощник города встает на чанк города и вводит /plot set build. Чанк регистрируется как строительная площадка. Для зданий 1x2 или Чудес Света (2x2) мэр назначает смежные чанки.",
      command: `/plot set build`,
    },
    {
      title: "3. Выбор проекта в /builds с проверкой уровня Архитектора",
      desc: selectedBranch === 'v2'
        ? "Мэр открывает /builds и выбирает проект. Плагин развертывает трехмерную голограмму (BlockDisplay), проверяет высоту (Y >= 60) и запускает послойное наведение."
        : "Мэр открывает /builds и выбирает проект. Плагин строго проверяет ранг игрока, уровень профессии Архитектора и находит свободный прямоугольник чанков нужного размера (1x1, 1x2 или 2x2).",
      command: `/builds`,
    },
    {
      title: selectedBranch === 'v2' ? "4. Возведение по голограмме и проверка стен (/build facade)" : "4. Размещение блоков и живой HUD (BossBar / Action Bar)",
      desc: selectedBranch === 'v2'
        ? "Игроки ставят блоки на подсвеченные места темных голограмм без физики. Минимум 50% наружных стен обязаны контактировать с воздухом или природными блоками (защита от бункеров). Проверить: /build facade."
        : "Находясь на чанке стройки, игроки видят живой BossBar и Action Bar со шкалами нужных блоков. Блоки можно ставить в любом месте и порядке внутри чанков.",
      command: selectedBranch === 'v2' ? `/build facade` : `/builds info`,
    },
    {
      title: "5. Установка Кастомного Ресурспака (GUI Фон и Невидимые слоты)",
      desc: "Кастомный фон меню /builds рисуется через Minecraft Font Provider (символ \\uE001, pack_format 34 для Purpur 1.20-1.21+). Чтобы ресурспак загружался игрокам автоматически, добавьте в server.properties прямую ссылку на .ZIP и SHA-1 хэш.",
      command: `# В server.properties на сервере:
resource-pack=https://.../TownyArchitecture.zip
resource-pack-sha1=${RESOURCE_PACK_SHA1}
require-resource-pack=false

# Либо локально в клиенте Minecraft:
# Скопируйте TownyArchitecture.zip в %appdata%\\.minecraft\\resourcepacks\\
# Включите в меню: Настройки -> Наборы ресурсов (Resource Packs)`,
    }
  ];

  const commands = [
    {
      cmd: "/plot set build",
      aliases: ["/build plot set build", "/plot set building"],
      perm: "Мэр / Помощник города",
      desc: "Объявляет текущий чанк города строительным участком. Размер: 1 чанк (16x16 блоков). Назначьте несколько смежных чанков для построек 1x2 или 2x2."
    },
    {
      cmd: "/builds",
      aliases: ["/build", "/townbuild", "/tb"],
      perm: "townyarchitecture.use",
      desc: "Открывает интерактивное GUI меню проектов города. Показывает габариты, требуемый уровень Архитектора, материалы и статус Чудес Света."
    },
    {
      cmd: "/build facade",
      aliases: ["/build inspect", "/build walls"],
      perm: "Все граждане",
      desc: "Проверяет контакт внешних стен здания с открытым пространством (воздух/листва/трава). Требуется контакт не менее 50% блоков (защита от подземных бункеров)."
    },
    {
      cmd: "/build stats",
      aliases: ["/build level"],
      perm: "Все граждане",
      desc: "Показывает личную статистику Архитектора: текущий уровень, опыт, прогресс-бар и количество установленных блоков с защитой от абуза."
    },
    {
      cmd: "/builds info",
      aliases: ["/builds status", "/builds progress"],
      perm: "Все граждане",
      desc: "Выводит в чат подробную шкалу прогресса по каждому необходимому материалу для здания на текущем участке."
    },
    {
      cmd: "/builds plot list",
      aliases: ["/build plot list"],
      perm: "Все граждане",
      desc: "Показывает список всех строительных участков города и их статус (свободен / занят проектом)."
    },
    {
      cmd: "/builds repair",
      aliases: ["/build repair"],
      perm: "Все строители города",
      desc: "Диагностирует повреждения здания и выводит список недостающих блоков. Ремонт производится исключительно физической установкой блоков на чанках постройки."
    },
    {
      cmd: "/map",
      aliases: ["/townymap", "/bluemapgui", "/tmap"],
      perm: "townyrespawn.use (Все)",
      desc: "Открывает интерактивную внутриигровую карту мира в стиле BlueMap с чанками, городами Towny, активными осадами TownySieges и точками возрождения."
    },
    {
      cmd: "/map graphics <уровень>",
      aliases: ["/map quality"],
      perm: "townyrespawn.use (Все)",
      desc: "Мгновенная настройка качества графики карты у самого игрока: LOW (2D шерсть), MEDIUM (терракотовые контуры), HIGH (бетон/высоты), HD (BlueMap изометрия)."
    },
    {
      cmd: "/respawn",
      aliases: ["/beds", "/mybeds", "/spawnselect"],
      perm: "townyrespawn.use (Все)",
      desc: "Открывает тактическое меню респавна со списком нескольких кроватей, спавном города (/t spawn) и столицы нации (/n spawn)."
    },
    {
      cmd: "/townyrespawn reload",
      aliases: ["/trespawn reload"],
      perm: "townyrespawn.admin (OP)",
      desc: "Административная перезагрузка конфигурации, точек кроватей и параметров графики без перезапуска сервера."
    },
    {
      cmd: "/siege camp <Город>",
      aliases: ["/siege create", "/siege declare"],
      perm: "Мэр города",
      desc: "Устанавливает начальный чанк осадного лагеря рядом с городом-целью (на нейтральной земле, 3–10 чанков от границ) и запускает 24ч таймер с боссбаром."
    },
    {
      cmd: "/siege expand",
      aliases: ["/siege claim"],
      perm: "Мэр города",
      desc: "Расширяет осадный лагерь на текущий смежный чанк. Стоимость привата и налог существенно выше обычных чанков Towny."
    },
    {
      cmd: "/siege unclaim",
      aliases: ["/siege remove"],
      perm: "Мэр города",
      desc: "Распривачивает дополнительный чанк осадного лагеря (центральный форпост не удаляется)."
    },
    {
      cmd: "/siege info",
      aliases: ["/siege status"],
      perm: "Все игроки",
      desc: "Показывает подробный статус осады вашего города: фаза (подготовка 24ч / активный штурм 2ч), остаток времени, чанки лагеря."
    },
    {
      cmd: "/siege list",
      aliases: ["/sieges"],
      perm: "Все игроки",
      desc: "Выводит список всех активных осад на сервере с таймерами и фазами."
    },
    {
      cmd: "/siege admin start <Город>",
      aliases: ["/siege admin settimer"],
      perm: "townysieges.admin (OP)",
      desc: "Административный запуск активного 2-часового штурма или изменение таймера."
    },
    {
      cmd: "/siege cannon give [игрок]",
      aliases: ["/siege mortar", "/siege pushka"],
      perm: "townysieges.admin (OP)",
      desc: "Выдает осадную мортиру (Nexo/Oraxen CustomModelData 7001). Устанавливается на землю (ПКМ), наводчик садится сверху."
    },
    {
      cmd: "/siege ammo give <regular|ap> [кол-во] [игрок]",
      aliases: ["/siege yadra"],
      perm: "townysieges.admin (OP)",
      desc: "Выдает нестакаемые боеприпасы: ⚪ Обычные ядра (regular) или 🟣 Бронебойные ядра (ap, пробивают обсидиан)."
    },
    {
      cmd: "/siege ammo recipes",
      aliases: ["/siege recipes"],
      perm: "Все игроки",
      desc: "Показывает в чате схему крафта 3x3 на верстаке для мортиры, обычных и бронебойных ядер."
    },
    {
      cmd: "/siege nationwar declare <Нация>",
      aliases: ["/siege nationwar"],
      perm: "Король / Лидер Нации",
      desc: "Объявляет Войну Наций: запускает глобальный 24-часовой таймер с боссбаром и последующий 2-часовой штурм для всех городов обеих наций."
    },
    {
      cmd: "/siege banner give [игрок]",
      aliases: ["/siege flag", "/siege flag give"],
      perm: "townysieges.capture",
      desc: "Выдать кастомный Штурмовой Флаг (Assault Banner) для почанкового захвата укреплений во время штурма."
    },
    {
      cmd: "/siege capture status",
      aliases: ["/siege flags", "/siege capture"],
      perm: "Все игроки",
      desc: "Текущий статус почанковых штурмов: координаты чанков с флагами, прогресс захвата, перевес сил (атакующие/защитники) и откат."
    },
    {
      cmd: "/siege disband",
      aliases: ["/siege destroy", "/siege cancel", "/siege camp disband"],
      perm: "Мэр атакующего города",
      desc: "Мэр атакующего города, стоя на любом чанке своего осадного лагеря, в любой момент осады или штурма уничтожает осадный лагерь с возвращением всех его чанков в исходное состояние (город, аванпост, дикие земли)!"
    },
    {
      cmd: "/siege admin skip-prep [город|нация]",
      aliases: ["/siege admin skipprep", "/siege admin assault", "/siege admin fastforward"],
      perm: "townysieges.admin (OP)",
      desc: "Единая админская команда: мгновенно пропускает 24-часовую подготовку и начинает активный 2-часовой штурм! Синхронизирует разблокировку осадных орудий и стойкость укреплений."
    },
    {
      cmd: "/siege menu",
      aliases: ["/siege gui"],
      perm: "Все игроки (Без прав)",
      desc: "Интерактивное GUI меню (54 слота) с описанием всех 7 систем осады, профилем игрока и навыка «Артиллерист», списком команд и интерактивными 3x3 верстаками крафтов мортиры, ядер и флага."
    },
    {
      cmd: "/siege admin recount",
      aliases: ["/build admin recount", "/ta recount"],
      perm: "townysieges.admin (OP)",
      desc: "Полный перерасчет и актуализация всех расчетов во всех плагинах сюиты: фактическое состояние блоков зданий в мире, % прочности, проверка владельцев чанков и активных осад."
    },
    {
      cmd: "/siege admin end [город|нация]",
      aliases: ["/siege admin stop", "/siege admin cancel"],
      perm: "townysieges.admin (OP)",
      desc: "Единая админская команда: завершает осаду/войну наций со всеми возвратами чанков лагеря в исходный статус."
    },
    {
      cmd: "/teu status",
      aliases: ["/teu reload", "/teu debug"],
      perm: "townyexplosionunblocker.admin (OP)",
      desc: "Управление модулем TownyExplosionUnblocker: статус интеграции с активными осадами, перезагрузка и логгер."
    },
    {
      cmd: "/build wonder reset <id>",
      aliases: ["/build wonder reset"],
      perm: "townyarchitecture.admin (OP)",
      desc: "Административный сброс статуса Чуда Света для тестирования и повторного строительства."
    }
  ];

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Title with Branch Selector */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">
            Руководство по установке и командам
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base">
            Пошаговая инструкция для Paper/Purpur 1.20+ с поддержкой чанков Towny, mcMMO и голограмм Litematica.
          </p>
        </div>

        <div className="inline-flex p-1 rounded-xl bg-neutral-900 border border-neutral-800 self-start sm:self-auto shrink-0">
          <button
            onClick={() => setSelectedBranch('v2')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              selectedBranch === 'v2'
                ? 'bg-amber-500 text-neutral-950 shadow-md shadow-amber-500/20'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Ветка 2.0.0 (3D Litematica)</span>
          </button>
          <button
            onClick={() => setSelectedBranch('v1')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              selectedBranch === 'v1'
                ? 'bg-blue-500 text-neutral-950 shadow-md shadow-blue-500/20'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Box className="w-4 h-4" />
            <span>Ветка 1.5.0 (Чанковая)</span>
          </button>
        </div>
      </div>

      {/* Security & Anti-Bunker Notice */}
      <div className={`border rounded-2xl p-5 sm:p-6 mb-8 ${selectedBranch === 'v2' ? 'bg-amber-950/30 border-amber-500/40' : 'bg-emerald-950/40 border-emerald-500/30'}`}>
        <div className="flex items-start gap-4">
          <div className={`p-2.5 rounded-xl shrink-0 mt-0.5 ${selectedBranch === 'v2' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
            {selectedBranch === 'v2' ? <ShieldAlert className="w-6 h-6" /> : <Shield className="w-6 h-6" />}
          </div>
          <div>
            <h3 className={`text-lg font-bold mb-1 ${selectedBranch === 'v2' ? 'text-amber-300' : 'text-emerald-300'}`}>
              {selectedBranch === 'v2'
                ? 'Ключевые механизмы версии 2.0.0 (Litematica 3D Schematics & Защита Фасадов)'
                : 'Ключевые механизмы версии 1.5.0 (Классическая чанковая система)'}
            </h3>
            <div className="space-y-2 text-sm text-neutral-300">
              {selectedBranch === 'v2' ? (
                <>
                  <p>
                    <strong>3D Голограммы BlockDisplay (Без модов):</strong> Сервер спавнит пакетные сущности BlockDisplay со сниженной яркостью и полупрозрачностью. Игроки наглядно видят каждый проект как трехмерный чертеж Litematica.
                  </p>
                  <p>
                    <strong>Защита от подземных бункеров (50% открытых стен):</strong>
                    <br />
                    • Постройка на глубине ниже Y=60 запрещена.
                    <br />
                    • Как минимум <strong>50% наружных стен</strong> здания должны граничить с открытым миром (воздух, листва, трава, вода, цветы).
                    <br />
                    • Если здание замуровано в толщу камня или окружено искусственным коконом, плагин переводит статус в <span className="text-red-400 font-mono font-bold">ENTOMBED</span> и замораживает городские баффы!
                    <br />
                    • Проверка фасадов игроками: <code className="bg-neutral-800 px-1.5 py-0.5 rounded text-amber-300">/build facade</code>.
                  </p>
                  <p>
                    <strong>Осадный Динамит (Siege TNT):</strong> Разрешает пробитие обсидиановых укреплений во время войны. Поврежденные блоки отключают баффы до физического восстановления игроками.
                  </p>
                </>
              ) : (
                <>
                  <p>
                    <strong>Строгая проверка mcMMO и прав:</strong> Плагин строго проверяет принадлежность к городу, ранг Мэра/Помощника для утверждения чертежей и уровень навыка mcMMO.
                  </p>
                  <p>
                    <strong>Чанковая привязка:</strong> Здания привязаны к чанкам (1x1, 1x2 / 2x1, 2x2 для Чудес Света). Мэр размечает участки командой <code className="bg-neutral-800 px-1.5 py-0.5 rounded text-blue-300">/plot set build</code>.
                  </p>
                  <p>
                    <strong>Зоны действия баффов:</strong> 1x1 — 5 чанков; 2x1 — город; 2x2 — весь мир. При прочности ниже 70% баффы замораживаются.
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Steps list */}
      <div className="space-y-6 mb-12">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-amber-400" />
          <span>Шаги запуска плагина на сервере (Ветка {activeMeta.version})</span>
        </h3>

        <div className="grid grid-cols-1 gap-6">
          {steps.map((step, idx) => (
            <div key={idx} className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 sm:p-6">
              <h4 className="text-base sm:text-lg font-semibold text-amber-300 mb-2">
                {step.title}
              </h4>
              <p className="text-sm text-neutral-300 mb-4 leading-relaxed">
                {step.desc}
              </p>
              <div className="relative group">
                <pre className="bg-neutral-950 p-4 rounded-lg font-mono text-xs sm:text-sm text-neutral-300 overflow-x-auto border border-neutral-800">
                  <code>{step.command}</code>
                </pre>
                <button
                  onClick={() => copyToClipboard(step.command, idx)}
                  className="absolute top-3 right-3 p-2 rounded-md bg-neutral-800 hover:bg-neutral-700 text-neutral-300 hover:text-white transition-colors cursor-pointer"
                  title="Скопировать команду"
                >
                  {copiedIndex === idx ? (
                    <Check className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Terminal Base64 Instant Deploy */}
      <div className="bg-neutral-900 border border-amber-500/30 rounded-2xl p-6 mb-12">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400">
              <Terminal className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-base sm:text-lg font-bold text-white">
                Мгновенная установка через терминал сервера ({activeMeta.jarFileName})
              </h4>
              <p className="text-xs sm:text-sm text-neutral-400">
                Заменяет файл в <code className="text-amber-300">plugins/{activeMeta.jarFileName}</code> напрямую без веб-интерфейса
              </p>
            </div>
          </div>
          <button
            onClick={copyBase64Command}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-bold text-sm shadow-md transition-colors cursor-pointer"
          >
            {copiedB64 ? (
              <>
                <Check className="w-4 h-4" />
                <span>Скопировано в буфер!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Скопировать Base64 команду для {activeMeta.version}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* TownyRespawn Guide Card */}
      <div className="bg-cyan-950/30 border-2 border-cyan-500/50 rounded-2xl p-6 mb-8 shadow-lg shadow-cyan-950/20">
        <div className="flex items-start gap-4">
          <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 shrink-0">
            <Map className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>Новый плагин: TownyRespawn v1.0.0</span>
                <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/30">
                  TownyRespawn-1.0.0.jar
                </span>
              </h3>
            </div>
            <p className="text-sm text-neutral-300 leading-relaxed mb-4">
              Внутриигровая интерактивная карта мира в стиле BlueMap, мульти-кровати и перехват экрана смерти Minecraft:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs mb-4">
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-cyan-300 font-bold block mb-1">🗺 Интерактивная карта /map</span>
                <span className="text-neutral-400">Прямо в GUI инвентаря открывается карта с городами, осадами и респавнами. Игрок сам выбирает уровень графики (LOW, MEDIUM, HIGH, HD) кнопкой в меню.</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-cyan-300 font-bold block mb-1">🛏 Мульти-кровати (Несколько точек)</span>
                <span className="text-neutral-400">Игрок может привязать несколько кроватей (настраивается в config.yml и пермишенами). При клике ПКМ кровать сохраняется в личный список.</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-rose-400 font-bold block mb-1">☠ Перехват возрождения после смерти</span>
                <span className="text-neutral-400">После нажатия «Возродиться» в Minecraft игрок не появляется сразу в мире, а переводится в безопасный режим с открытием карты выбора места респавна.</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-emerald-400 font-bold block mb-1">🌲 Ванильный спавн и спавн сервера</span>
                <span className="text-neutral-400">Доступны отдельные кнопки: «Ванильный респавн» (случайное место в диких землях) и «На спавн сервера» (/spawn), плюс /t spawn и /n spawn.</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 text-xs font-mono">
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-cyan-300">/map</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/map graphics &lt;уровень&gt;</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/respawn</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/townyrespawn reload</span>
            </div>
          </div>
        </div>
      </div>

      {/* TownySieges Guide Card */}
      <div className="bg-orange-950/30 border-2 border-orange-500/50 rounded-2xl p-6 mb-12 shadow-lg shadow-orange-950/20">
        <div className="flex items-start gap-4">
          <div className="p-2.5 rounded-xl bg-orange-500/20 text-orange-400 shrink-0">
            <Flame className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>Новый плагин: TownySieges v1.0.0</span>
                <span className="text-xs px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 font-mono border border-orange-500/30">
                  TownySieges-1.0.0.jar
                </span>
              </h3>
            </div>
            <p className="text-sm text-neutral-300 leading-relaxed mb-4">
              Полноценная система осадных лагерей, объявлений войны и 24-часовых таймеров штурма для Towny:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs mb-4">
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-orange-300 font-bold block mb-1">⛺ Автономный осадный лагерь</span>
                <span className="text-neutral-400">Мэр атакующего города подходит к городу-цели (дистанция 3–10 чанков) и вводит <code>/siege camp &lt;Город&gt;</code>. Чанк лагеря не требует соединения со своими границами.</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-orange-300 font-bold block mb-1">📈 Дорогие чанки и налоги</span>
                <span className="text-neutral-400">Лагерь расширяется смежными чанками (<code>/siege expand</code>). Цена привата (15 000 / 10 000) и ежедневный налог (2 500/чанк) существенно выше обычных чанков Towny.</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-amber-300 font-bold block mb-1">⏱ Боссбар (BossBar) и 24ч таймер</span>
                <span className="text-neutral-400">Жители осаждаемого города получают яркий звуковой сигнал тревоги и постоянный анимированный Боссбар со шкалой прогресса и обратным отсчетом 24 часов до штурма.</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-red-400 font-bold block mb-1">💥 2 часа активного штурма</span>
                <span className="text-neutral-400">Ровно через 24 часа начинается активная фаза штурма (2 часа). Только в это время TownyExplosionUnblocker разрешает пушечным снарядам разрушать блоки в городе!</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 text-xs font-mono">
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-orange-300">/siege camp &lt;Город&gt;</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/siege expand</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/siege unclaim</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/siege info</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-neutral-300">/siege list</span>
              <span className="bg-neutral-950 px-2.5 py-1 rounded border border-neutral-800 text-red-300">/siege admin start &lt;Город&gt;</span>
            </div>
          </div>
        </div>
      </div>

      {/* TownyExplosionUnblocker Guide Card */}
      <div className="bg-red-950/30 border-2 border-red-500/40 rounded-2xl p-6 mb-12">
        <div className="flex items-start gap-4">
          <div className="p-2.5 rounded-xl bg-red-500/20 text-red-400 shrink-0">
            <Shield className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <h3 className="text-lg font-bold text-white">
                Плагин-компаньон: TownyExplosionUnblocker v1.1.0
              </h3>
              <span className="px-2.5 py-0.5 rounded-full bg-red-500/20 text-red-300 text-xs font-mono border border-red-500/40 self-start sm:self-auto">
                TownyExplosionUnblocker-1.1.0.jar
              </span>
            </div>
            <p className="text-sm text-neutral-300 leading-relaxed mb-3">
              Снимает стандартную защиту Towny от взрывов <strong>ИСКЛЮЧИТЕЛЬНО во время 2 часов активной осады TownySieges</strong> и только для снарядов пушек SiegeCannon. В мирное время и во время 24ч подготовки город на 100% защищен от любых взрывов.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-red-300 font-bold block mb-1">/teu status</span>
                <span className="text-neutral-400">Проверка активности и интеграции с активными осадами</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-red-300 font-bold block mb-1">/teu reload</span>
                <span className="text-neutral-400">Перезагрузка config.yml без перезапуска сервера</span>
              </div>
              <div className="bg-neutral-900/80 p-3 rounded-lg border border-neutral-800">
                <span className="font-mono text-red-300 font-bold block mb-1">/teu debug</span>
                <span className="text-neutral-400">Включение детального логирования перехвата взрывов в консоль</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Commands Table */}
      <div className="mb-12">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-amber-400" />
          <span>Команды плагина и права</span>
        </h3>

        <div className="overflow-x-auto rounded-xl border border-neutral-800 bg-neutral-900">
          <table className="w-full text-left text-sm text-neutral-300">
            <thead className="bg-neutral-950 text-neutral-400 uppercase text-xs border-b border-neutral-800">
              <tr>
                <th className="px-4 py-3.5 font-semibold">Команда</th>
                <th className="px-4 py-3.5 font-semibold">Алиасы</th>
                <th className="px-4 py-3.5 font-semibold">Права / Роль</th>
                <th className="px-4 py-3.5 font-semibold">Описание</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800">
              {commands.map((c, i) => (
                <tr key={i} className="hover:bg-neutral-800/40 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-amber-300 whitespace-nowrap">
                    {c.cmd}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-neutral-400">
                    {c.aliases.join(', ')}
                  </td>
                  <td className="px-4 py-3 text-xs">
                    <span className="px-2 py-0.5 rounded bg-neutral-800 border border-neutral-700 text-neutral-300">
                      {c.perm}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs sm:text-sm text-neutral-300 leading-relaxed">
                    {c.desc}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
