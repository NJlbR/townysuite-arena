package com.towny.respawn.manager;

import com.palmergames.bukkit.towny.object.Nation;
import com.palmergames.bukkit.towny.object.Town;
import com.towny.respawn.TownyRespawnPlugin;
import com.towny.respawn.model.PlayerBed;
import com.towny.respawn.model.RespawnPoint;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.scheduler.BukkitTask;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

public class RespawnManager {

    private final TownyRespawnPlugin plugin;
    private final Set<UUID> pendingRespawnPlayers = ConcurrentHashMap.newKeySet();
    private final Set<UUID> limboPlayers = ConcurrentHashMap.newKeySet();
    private final Map<UUID, Long> lastRespawnTime = new ConcurrentHashMap<>();
    private final Map<UUID, BukkitTask> limboTasks = new ConcurrentHashMap<>();
    private final Map<UUID, GameMode> previousGameModes = new ConcurrentHashMap<>();
    private final Map<UUID, Boolean> previousAllowFlight = new ConcurrentHashMap<>();

    public RespawnManager(TownyRespawnPlugin plugin) {
        this.plugin = plugin;
    }

    public void markPendingRespawn(UUID uuid) {
        pendingRespawnPlayers.add(uuid);
    }

    public void clearPendingRespawn(UUID uuid) {
        pendingRespawnPlayers.remove(uuid);
    }

    public boolean isPendingRespawn(UUID uuid) {
        return pendingRespawnPlayers.contains(uuid);
    }

    public Set<UUID> getLimboPlayers() {
        return Collections.unmodifiableSet(limboPlayers);
    }

    public boolean isLimbo(UUID uuid) {
        return limboPlayers.contains(uuid);
    }

    public void recordRespawn(UUID uuid) {
        lastRespawnTime.put(uuid, System.currentTimeMillis());
    }

    /**
     * Вычисляет оставшееся время КД (в секундах) с момента предыдущего возрождения.
     * По правилу: после возрождения и смерти игрок не может возродиться,
     * пока от предыдущего возрождения не прошло 30 секунд.
     */
    public long getRemainingCooldownSeconds(UUID uuid) {
        Long lastTime = lastRespawnTime.get(uuid);
        if (lastTime == null) return 0L;

        long cooldownSec = plugin.getConfig().getLong("respawn.cooldown-seconds", 30L);
        if (cooldownSec <= 0) {
            cooldownSec = plugin.getConfig().getLong("respawn.delay-seconds", 30L);
        }
        if (cooldownSec <= 0) return 0L;

        long elapsed = System.currentTimeMillis() - lastTime;
        long totalMillis = cooldownSec * 1000L;
        if (elapsed >= totalMillis) {
            return 0L;
        }
        return Math.max(1L, (totalMillis - elapsed + 999L) / 1000L);
    }

    public boolean isOnCooldown(UUID uuid) {
        return getRemainingCooldownSeconds(uuid) > 0L;
    }

    /**
     * Координаты Limbo (высоко в небе под лимитом мира), где игрок парит во время выбора меню,
     * чтобы физически ВООБЩЕ не появляться в игровом мире и не мешать другим игрокам.
     */
    public Location getLimboLocation(Player player) {
        World world = player != null && player.getWorld() != null ? player.getWorld() : Bukkit.getWorlds().get(0);
        String customWorld = plugin.getConfig().getString("limbo.world", "");
        if (customWorld != null && !customWorld.isEmpty()) {
            World cw = Bukkit.getWorld(customWorld);
            if (cw != null) world = cw;
        }
        double configuredY = plugin.getConfig().getDouble("limbo.y-coordinate", 320.0);
        double safeY = Math.min(configuredY, world.getMaxHeight() - 2.0);
        return new Location(world, 0.5, safeY, 0.5, 0.0f, 0.0f);
    }

    /**
     * Помещает умершего игрока в скрытое состояние (Limbo):
     * - Игрок ВООБЩЕ не появляется в игровом мире для других игроков (скрыт через hidePlayer, невидим, без коллизии).
     * - Игрок парит в безопасной точке в небе без гравитации, урона и физического взаимодействия.
     * - Переводится в режим ADVENTURE на время выбора в меню.
     * - Запускается фоновый тикер КД на 30 секунд.
     */
    public void enterLimbo(Player player) {
        if (player == null || !player.isOnline()) return;
        UUID uuid = player.getUniqueId();
        limboPlayers.add(uuid);
        markPendingRespawn(uuid);

        // Сохраняем исходный режим игры и право полета
        previousGameModes.put(uuid, player.getGameMode());
        previousAllowFlight.put(uuid, player.getAllowFlight());

        // Полная изоляция от игрового мира
        player.setGameMode(GameMode.ADVENTURE);
        player.setAllowFlight(true);
        player.setFlying(true);
        player.setGravity(false);
        player.setInvisible(true);
        player.setCollidable(false);
        player.setInvulnerable(true);
        player.setSilent(true);
        player.setFireTicks(0);
        try {
            player.setVisualFire(false);
        } catch (Throwable ignored) {}
        try {
            player.setCanPickupItems(false);
        } catch (Throwable ignored) {}

        // Скрываем игрока абсолютно для всех других игроков на сервере
        for (Player other : Bukkit.getOnlinePlayers()) {
            if (!other.equals(player)) {
                try {
                    other.hidePlayer(plugin, player);
                } catch (Throwable ignored) {}
            }
        }

        // Запуск фонового тикера для отсчета КД и обновления подсказок в интерфейсе
        startLimboTicker(player);
    }

    private void startLimboTicker(Player player) {
        UUID uuid = player.getUniqueId();
        cancelLimboTicker(uuid);

        final boolean[] wasOnCooldown = new boolean[]{ getRemainingCooldownSeconds(uuid) > 0 };

        BukkitTask task = Bukkit.getScheduler().runTaskTimer(plugin, () -> {
            if (!player.isOnline() || !isLimbo(uuid)) {
                cancelLimboTicker(uuid);
                return;
            }

            long remainingCd = getRemainingCooldownSeconds(uuid);
            if (remainingCd > 0) {
                wasOnCooldown[0] = true;
                String bar = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.cooldown-actionbar",
                                "&c⏳ КД на возрождение: &e{seconds} &cсек. &7(подождите перед выбором точки)"))
                        .replace("{seconds}", String.valueOf(remainingCd));
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, new TextComponent(bar));
                } catch (Throwable ignored) {}
            } else {
                if (wasOnCooldown[0]) {
                    wasOnCooldown[0] = false;
                    try {
                        player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_PLING, 1.0f, 1.6f);
                    } catch (Throwable ignored) {}
                }
                String barReady = ChatColor.translateAlternateColorCodes('&',
                        plugin.getConfig().getString("messages.cooldown-ready",
                                "&a✔ Возрождение готово! Выберите точку в меню."));
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, new TextComponent(barReady));
                } catch (Throwable ignored) {}
            }

            // Гарантируем сокрытие для всех подключившихся игроков
            for (Player other : Bukkit.getOnlinePlayers()) {
                if (!other.equals(player) && other.canSee(player)) {
                    try {
                        other.hidePlayer(plugin, player);
                    } catch (Throwable ignored) {}
                }
            }

            // Обновляем иконку КД в открытом меню
            plugin.getGuiManager().updateCooldownHeader(player);

        }, 0L, 20L);

        limboTasks.put(uuid, task);
    }

    public void cancelLimboTicker(UUID uuid) {
        BukkitTask task = limboTasks.remove(uuid);
        if (task != null) {
            task.cancel();
        }
    }

    /**
     * Выход из Limbo и мгновенное возрождение на выбранной точке:
     * - Игрок телепортируется на целевую точку.
     * - Возвращается исходный режим игры, видимость для всех игроков и нормальная гравитация/физика.
     * - НЕТ никакой блокировки после респавна! Игрок сразу полноценно двигается, прыгает и играет.
     * - Засекается время текущего возрождения (КД 30 секунд для будущих смертей).
     * - Проигрывается негромкий звук в мире для окружающих игроков.
     */
    public void exitLimboAndRespawn(Player player, RespawnPoint point) {
        if (player == null || point == null) return;
        UUID uuid = player.getUniqueId();

        cancelLimboTicker(uuid);
        limboPlayers.remove(uuid);
        clearPendingRespawn(uuid);

        Location target = point.getTargetLocation();
        if (target == null) {
            target = getServerSpawnLocation(player);
        }

        // Очищаем любые негативные эффекты
        player.removePotionEffect(PotionEffectType.BLINDNESS);
        player.removePotionEffect(PotionEffectType.SLOW);
        player.removePotionEffect(PotionEffectType.DAMAGE_RESISTANCE);
        player.removePotionEffect(PotionEffectType.FIRE_RESISTANCE);
        player.removePotionEffect(PotionEffectType.REGENERATION);

        // Восстанавливаем сохраненный режим игры и полет
        GameMode savedMode = previousGameModes.remove(uuid);
        if (savedMode != null) {
            player.setGameMode(savedMode);
        } else {
            player.setGameMode(GameMode.SURVIVAL);
        }
        boolean savedFlight = previousAllowFlight.getOrDefault(uuid, false);
        player.setFlying(false);
        player.setAllowFlight(savedFlight);

        // Возвращаем видимость и стандартное состояние в мире
        player.setGravity(true);
        player.setInvisible(false);
        player.setCollidable(true);
        player.setInvulnerable(false);
        player.setSilent(false);
        try {
            player.setCanPickupItems(true);
        } catch (Throwable ignored) {}

        // Делаем игрока снова видимым для всех игроков на сервере
        for (Player other : Bukkit.getOnlinePlayers()) {
            if (!other.equals(player)) {
                try {
                    other.showPlayer(plugin, player);
                } catch (Throwable ignored) {}
            }
        }

        // Мгновенная телепортация на целевую точку
        player.teleport(target);
        player.closeInventory();

        // Засекаем время этого возрождения для КД в 30 секунд на случай повторной смерти!
        recordRespawn(uuid);

        // Негромкий звук в мире для оповещения окружающих игроков
        if (plugin.getConfig().getBoolean("respawn.sound.enabled", true) && target.getWorld() != null) {
            String soundName = plugin.getConfig().getString("respawn.sound.name", "BLOCK_BEACON_ACTIVATE");
            float volume = (float) plugin.getConfig().getDouble("respawn.sound.volume", 0.5);
            float pitch = (float) plugin.getConfig().getDouble("respawn.sound.pitch", 1.4);
            try {
                Sound sound = Sound.valueOf(soundName);
                target.getWorld().playSound(target, sound, SoundCategory.BLOCKS, volume, pitch);
            } catch (Throwable ignored) {
                target.getWorld().playSound(target, Sound.BLOCK_BEACON_ACTIVATE, SoundCategory.BLOCKS, 0.5f, 1.4f);
            }
        }

        // Сообщение игроку
        String prefix = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.prefix", "&b&l[TownyRespawn]&r "));
        String msg = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("messages.respawn-selected", "&aВы успешно возродились: &f{location}&a!"))
                .replace("{location}", point.getDisplayName());
        player.sendMessage(prefix + msg);

        // Титул при появлении
        player.sendTitle("§a✔ Возрождение", "§f" + point.getDisplayName(), 5, 20, 10);
    }

    public Location getServerSpawnLocation(Player player) {
        World world = player != null ? player.getWorld() : Bukkit.getWorlds().get(0);
        if (plugin.getConfig().getBoolean("respawn.server-spawn.custom-coords.enabled", false)) {
            String wName = plugin.getConfig().getString("respawn.server-spawn.custom-coords.world", world.getName());
            World w = Bukkit.getWorld(wName);
            if (w != null) {
                double x = plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.x", 0.5);
                double y = plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.y", 70.0);
                double z = plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.z", 0.5);
                float yaw = (float) plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.yaw", 0.0);
                float pitch = (float) plugin.getConfig().getDouble("respawn.server-spawn.custom-coords.pitch", 0.0);
                return new Location(w, x, y, z, yaw, pitch);
            }
        }
        return world.getSpawnLocation().add(0.5, 0.1, 0.5);
    }

    public Location findSafeVanillaWildSpawn(Player player) {
        World world = player != null ? player.getWorld() : Bukkit.getWorlds().get(0);
        int min = plugin.getConfig().getInt("respawn.vanilla-respawn.wild-radius-min", 200);
        int max = plugin.getConfig().getInt("respawn.vanilla-respawn.wild-radius-max", 1500);
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        int angle = rnd.nextInt(360);
        int dist = min + rnd.nextInt(Math.max(1, max - min));
        int x = (int) (Math.cos(Math.toRadians(angle)) * dist);
        int z = (int) (Math.sin(Math.toRadians(angle)) * dist);
        int y = world.getHighestBlockYAt(x, z);
        if (y < world.getMinHeight() + 5) y = 70;
        return new Location(world, x + 0.5, y + 1.0, z + 0.5);
    }
}
