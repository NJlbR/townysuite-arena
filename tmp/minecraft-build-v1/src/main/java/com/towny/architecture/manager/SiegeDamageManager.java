package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.ActiveBuilding;
import com.towny.architecture.model.BuildingBlueprint;
import com.towny.architecture.util.RussianTranslator;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.entity.EntityExplodeEvent;

import java.util.Map;

public class SiegeDamageManager implements Listener {
    private final TownyArchitecturePlugin plugin;

    public SiegeDamageManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onExplosion(EntityExplodeEvent event) {
        for (Block b : event.blockList()) {
            plugin.getBuildingManager().handleBlockBroken(null, b.getLocation(), b.getType());
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockExplosion(BlockExplodeEvent event) {
        for (Block b : event.blockList()) {
            plugin.getBuildingManager().handleBlockBroken(null, b.getLocation(), b.getType());
        }
    }

    /**
     * Informs players that repairs can ONLY be performed by physically placing missing blocks!
     */
    public void showRepairInstructions(Player player, ActiveBuilding building) {
        BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(building.getBlueprintId());
        String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();

        if (building.getHealthPercent() >= 100.0 && building.isFullyBuilt()) {
            player.sendMessage(ChatColor.GREEN + "[TownyArchitecture] Здание «" + bpName + "» в идеальном состоянии (Прочность: 100%).");
            return;
        }

        player.sendMessage(ChatColor.GOLD + "══════ Восстановление здания «" + bpName + "» ══════");
        player.sendMessage(ChatColor.RED + "✖ Мгновенный ремонт командами отключен!");
        player.sendMessage(ChatColor.YELLOW + "Для восстановления прочности постройки установите недостающие блоки на ее чанках:");

        boolean anyMissing = false;
        for (Map.Entry<Material, Integer> entry : building.getRequiredMaterials().entrySet()) {
            Material mat = entry.getKey();
            int needed = entry.getValue();
            int placed = building.getPlacedCount(mat);
            if (placed < needed) {
                anyMissing = true;
                player.sendMessage(ChatColor.GRAY + " - " + ChatColor.WHITE + RussianTranslator.getMaterialRu(mat) + ": " +
                        ChatColor.RED + "нужно еще " + (needed - placed) + " шт. " +
                        ChatColor.DARK_GRAY + "(" + placed + "/" + needed + ")");
            }
        }

        if (!anyMissing) {
            player.sendMessage(ChatColor.GREEN + "✔ Все блоки на месте. Выполняется автоматическая синхронизация.");
        }

        player.sendMessage(ChatColor.GOLD + "Текущая прочность: " + 
                (building.getHealthPercent() >= 70.0 ? ChatColor.GREEN : ChatColor.RED) + 
                String.format("%.1f", building.getHealthPercent()) + "% " +
                ChatColor.GRAY + "(баффы активны только при прочности >= 70%)");
        player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
    }
}
