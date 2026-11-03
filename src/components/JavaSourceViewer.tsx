import React, { useState } from 'react';
import { JAVA_SOURCES_V2, PLUGIN_METADATA_V2 } from '../data/javaSources';
import { UNBLOCKER_METADATA } from '../data/unblockerData';
import { TOWNY_SIEGES_METADATA } from '../data/townySiegesData';
import { FileCode, Folder, Copy, Check, Terminal, Shield, Download, Search, Sparkles } from 'lucide-react';
import { downloadUnblockerJar, downloadTownySiegesJar } from '../utils/downloadHelpers';

interface FileEntry {
  name: string;
  path: string;
  category: string;
  plugin: string;
  content: string;
}

export const JavaSourceViewer: React.FC = () => {
  const [selectedPlugin, setSelectedPlugin] = useState<'all' | 'unblocker' | 'sieges' | 'architecture'>('unblocker');
  const [searchQuery, setSearchQuery] = useState('');
  const [copied, setCopied] = useState(false);

  // Hardcoded / dynamically populated files for unblocker and sieges
  const unblockerFiles: FileEntry[] = [
    {
      name: "CannonExplosionListener.java",
      path: "src/main/java/com/towny/explosion/listener/CannonExplosionListener.java",
      category: "Listeners",
      plugin: "TownyExplosionUnblocker",
      content: `package com.towny.explosion.listener;

import com.palmergames.bukkit.towny.TownyAPI;
import com.palmergames.bukkit.towny.object.Town;
import com.palmergames.bukkit.towny.object.TownBlock;
import com.towny.explosion.TownyExplosionUnblockerPlugin;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.entity.TNTPrimed;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntitySpawnEvent;

import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Redesigned from scratch: Strict Mortar & Siege Condition Explosion Controller.
 *
 * Fundamental Rules:
 * 1. ZERO town damage outside active siege.
 * 2. During ACTIVE_SIEGE, ONLY verified mortars (мортиры) damage town blocks.
 * 3. Regular cannons, player TNT, and other weapons CANNOT damage towns.
 */
public class CannonExplosionListener implements Listener {
    private final TownyExplosionUnblockerPlugin plugin;
    private final Map<UUID, List<Block>> capturedBlastBlocks = new ConcurrentHashMap<>();
    private final Map<UUID, Float> capturedYield = new ConcurrentHashMap<>();

    public CannonExplosionListener(TownyExplosionUnblockerPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onExplosionLate(EntityExplodeEvent event) {
        if (!plugin.isUnblockerEnabled()) return;

        Entity entity = event.getEntity();
        Location loc = event.getLocation();

        // 1. Strict Mortar check: only authentic mortars can damage towns
        boolean isMortar = plugin.getCannonDetector().isMortarProjectile(entity);

        // 2. Strict Town & Siege status at explosion origin
        boolean originInTown = isLocationInTown(loc);
        String originTown = originInTown ? getTownNameAt(loc) : null;
        boolean originActiveSiege = originTown != null && isTownUnderActiveSiege(originTown);

        // ABSOLUTE RULE 1:
        // If explosion originated in a town:
        // Must be during ACTIVE_SIEGE AND from a verified MORTAR.
        if (originInTown) {
            if (!originActiveSiege || !isMortar) {
                event.blockList().clear();
                event.setCancelled(true);
                return;
            }
        }

        // ABSOLUTE RULE 2:
        // Inspect EVERY individual block in event.blockList().
        // Town blocks are protected unless town is in ACTIVE_SIEGE and weapon is MORTAR.
        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;
            Location bLoc = b.getLocation();
            if (isLocationInTown(bLoc)) {
                String bTown = getTownNameAt(bLoc);
                boolean bUnderSiege = bTown != null && isTownUnderActiveSiege(bTown);

                if (!bUnderSiege || !isMortar) {
                    it.remove();
                }
            }
        }

        if (event.blockList().isEmpty()) {
            if (originInTown) event.setCancelled(true);
            return;
        }

        // ABSOLUTE RULE 3:
        // Uncancel ONLY if verified mortar and in active siege
        if (event.isCancelled()) {
            if (isMortar && originActiveSiege) {
                event.setCancelled(false);
            } else {
                event.blockList().clear();
            }
        }
    }
}`
    },
    {
      name: "CannonDetector.java",
      path: "src/main/java/com/towny/explosion/util/CannonDetector.java",
      category: "Detector",
      plugin: "TownyExplosionUnblocker",
      content: `package com.towny.explosion.util;

import com.towny.explosion.TownyExplosionUnblockerPlugin;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.TNTPrimed;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Strict Mortar & Siege Artillery Detector.
 * Only projectiles explicitly confirmed as Mortars (Мортиры) are recognized.
 * Ordinary cannons, player TNT, creepers, crystals, beds, and vanilla explosives
 * are strictly rejected.
 */
public class CannonDetector {
    private final TownyExplosionUnblockerPlugin plugin;
    private final Set<UUID> trackedMortarTnts = ConcurrentHashMap.newKeySet();

    public CannonDetector(TownyExplosionUnblockerPlugin plugin) {
        this.plugin = plugin;
    }

    public boolean isMortarProjectile(Entity entity) {
        if (entity == null) return false;

        EntityType type = entity.getType();
        if (isBlacklistedVanillaEntity(type)) return false;

        UUID uuid = entity.getUniqueId();
        if (trackedMortarTnts.contains(uuid)) return true;

        String customName = entity.getCustomName();
        if (customName != null) {
            String lower = customName.toLowerCase();
            if (lower.contains("мортир") || lower.contains("mortar")) return true;
        }

        Set<String> tags = entity.getScoreboardTags();
        if (tags != null) {
            for (String tag : tags) {
                if (tag != null) {
                    String lower = tag.toLowerCase();
                    if (lower.contains("mortar") || lower.contains("мортир")) return true;
                }
            }
        }

        return entity.hasMetadata("mortar") || entity.hasMetadata("mortar_shell") || entity.hasMetadata("siege_mortar");
    }
}`
    },
    {
      name: "config.yml",
      path: "src/main/resources/config.yml",
      category: "Config",
      plugin: "TownyExplosionUnblocker",
      content: `# TownyExplosionUnblocker Configuration
enabled: true
debug-logging: false

siege-integration:
  # Разрешать взрывы в городах ТОЛЬКО во время 2 часов активного штурма (ACTIVE_SIEGE)
  require-active-siege: true

detection:
  mortar-metadata-keys:
    - "mortar"
    - "mortar_shell"
    - "siege_mortar"
    - "is_mortar"`
    }
  ];

  const siegesFiles: FileEntry[] = [
    {
      name: "SiegeProtectionListener.java",
      path: "src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java",
      category: "Listeners",
      plugin: "TownySieges",
      content: `package com.towny.sieges.listener;

import com.towny.sieges.TownySiegesPlugin;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityExplodeEvent;

import java.util.Iterator;

public class SiegeProtectionListener implements Listener {
    private final TownySiegesPlugin plugin;

    public SiegeProtectionListener(TownySiegesPlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onEntityExplode(EntityExplodeEvent event) {
        Location loc = event.getLocation();
        Entity entity = event.getEntity();
        boolean isMortar = isMortarProjectile(entity);

        String centerTown = plugin.getTownyHook().getTownNameAt(loc);
        boolean centerInTown = centerTown != null;
        boolean centerUnderSiege = centerInTown && plugin.getSiegeManager().isTownUnderActiveSiege(centerTown);

        // If in town and not in active assault or not a mortar -> CANCEL!
        if (centerInTown && (!centerUnderSiege || !isMortar)) {
            event.blockList().clear();
            event.setCancelled(true);
            return;
        }

        Iterator<Block> it = event.blockList().iterator();
        while (it.hasNext()) {
            Block b = it.next();
            if (b == null) continue;
            String bTown = plugin.getTownyHook().getTownNameAt(b.getLocation());
            if (bTown != null) {
                boolean bUnderSiege = plugin.getSiegeManager().isTownUnderActiveSiege(bTown);
                if (!bUnderSiege || !isMortar) {
                    it.remove();
                }
            }
        }
    }
}`
    },
    {
      name: "SiegeCommand.java",
      path: "src/main/java/com/towny/sieges/command/SiegeCommand.java",
      category: "Commands",
      plugin: "TownySieges",
      content: `// /siege skip [секунды / город]
// Позволяет OP моментально пропустить 24ч подготовки и активировать штурм для тестов!
if (sub.equals("skip")) {
    if (!sender.hasPermission("townysieges.admin") && !sender.isOp()) {
        sender.sendMessage(ChatColor.RED + "Нет прав.");
        return true;
    }
    if (args.length == 1) {
        // Мгновенный перевод всех осад в активный 2-часовой штурм
        for (SiegeCamp camp : plugin.getSiegeManager().getAllSieges()) {
            camp.setStatus(SiegeCamp.Status.ACTIVE_SIEGE);
        }
        sender.sendMessage(ChatColor.GREEN + "[TownySieges] Фаза подготовки пропущена! Активирован штурм.");
        return true;
    }
}`
    }
  ];

  const archFiles: FileEntry[] = JAVA_SOURCES_V2.map(f => ({
    name: f.name,
    path: f.path,
    category: f.category,
    plugin: "TownyArchitecture",
    content: f.content
  }));

  const allFiles: FileEntry[] = [...unblockerFiles, ...siegesFiles, ...archFiles];

  const filteredFiles = allFiles.filter(f => {
    if (selectedPlugin === 'unblocker' && f.plugin !== 'TownyExplosionUnblocker') return false;
    if (selectedPlugin === 'sieges' && f.plugin !== 'TownySieges') return false;
    if (selectedPlugin === 'architecture' && f.plugin !== 'TownyArchitecture') return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return f.name.toLowerCase().includes(q) || f.path.toLowerCase().includes(q) || f.content.toLowerCase().includes(q);
    }
    return true;
  });

  const [activeFile, setActiveFile] = useState<FileEntry>(filteredFiles[0] || unblockerFiles[0]);

  const handleCopy = () => {
    if (activeFile) {
      navigator.clipboard.writeText(activeFile.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded text-xs font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Java Source Repository
            </span>
            <span className="text-xs text-neutral-400 font-mono">Paper / Purpur 1.20+</span>
          </div>
          <h1 className="text-2xl font-bold text-white font-mono flex items-center gap-2">
            <FileCode className="w-6 h-6 text-amber-400" />
            Исходный код компонентов Towny Suite
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Проверенная реализация: мортиры, осадные лагеря, защита городов и пропуск времени для тестов.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => downloadUnblockerJar()}
            className="px-3.5 py-2 bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-700 rounded-lg text-xs font-mono flex items-center gap-2 transition-colors"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            Unblocker JAR
          </button>
          <button
            onClick={() => downloadTownySiegesJar()}
            className="px-3.5 py-2 bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-700 rounded-lg text-xs font-mono flex items-center gap-2 transition-colors"
          >
            <Download className="w-4 h-4 text-red-400" />
            Sieges JAR
          </button>
        </div>
      </div>

      {/* Filter Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-1.5 p-1 bg-neutral-900 border border-neutral-800 rounded-lg w-full sm:w-auto">
          <button
            onClick={() => setSelectedPlugin('unblocker')}
            className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
              selectedPlugin === 'unblocker' ? 'bg-amber-500 text-neutral-950 font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            💥 ExplosionUnblocker
          </button>
          <button
            onClick={() => setSelectedPlugin('sieges')}
            className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
              selectedPlugin === 'sieges' ? 'bg-red-500 text-white font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            ⚔ TownySieges
          </button>
          <button
            onClick={() => setSelectedPlugin('architecture')}
            className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
              selectedPlugin === 'architecture' ? 'bg-cyan-500 text-neutral-950 font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            🏰 TownyArchitecture
          </button>
          <button
            onClick={() => setSelectedPlugin('all')}
            className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
              selectedPlugin === 'all' ? 'bg-neutral-700 text-white font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Все файлы
          </button>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-neutral-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск по классам и методам..."
            className="w-full bg-neutral-900 border border-neutral-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-amber-500/50"
          />
        </div>
      </div>

      {/* Main Grid: File Tree + Code Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* File List */}
        <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl p-3 flex flex-col gap-1 max-h-[600px] overflow-y-auto">
          <div className="text-[11px] font-mono text-neutral-500 px-2 py-1 uppercase tracking-wider">
            Файлы ({filteredFiles.length})
          </div>
          {filteredFiles.map((file) => {
            const isSelected = activeFile?.path === file.path;
            return (
              <button
                key={file.path}
                onClick={() => setActiveFile(file)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-mono flex items-center justify-between gap-2 transition-colors ${
                  isSelected
                    ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                    : 'text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <FileCode className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-amber-400' : 'text-neutral-500'}`} />
                  <span className="truncate">{file.name}</span>
                </div>
                <span className="text-[10px] text-neutral-500 uppercase shrink-0 font-sans">
                  {file.category}
                </span>
              </button>
            );
          })}
        </div>

        {/* Code View */}
        <div className="lg:col-span-3 bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden flex flex-col">
          {/* Code Window Header */}
          <div className="bg-neutral-950 px-4 py-3 border-b border-neutral-800 flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 truncate">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/80 inline-block"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/80 inline-block"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-green-500/80 inline-block"></span>
              <span className="text-xs font-mono text-neutral-400 ml-2 truncate">
                {activeFile?.path || 'Файл не выбран'}
              </span>
            </div>

            <button
              onClick={handleCopy}
              className="px-2.5 py-1 bg-neutral-900 hover:bg-neutral-800 text-neutral-300 border border-neutral-700/60 rounded text-xs font-mono flex items-center gap-1.5 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Скопировано</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Копировать</span>
                </>
              )}
            </button>
          </div>

          {/* Code Content */}
          <div className="p-4 bg-neutral-950/70 overflow-x-auto max-h-[550px] font-mono text-xs leading-relaxed text-neutral-300 select-text">
            <pre>
              <code>{activeFile?.content || '// Выберите файл слева для просмотра кода'}</code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
