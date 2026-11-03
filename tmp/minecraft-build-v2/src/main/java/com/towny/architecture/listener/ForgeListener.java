package com.towny.architecture.listener;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.manager.ForgeManager;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.block.Block;
import org.bukkit.block.CreatureSpawner;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.inventory.ItemStack;

public class ForgeListener implements Listener {

    private final TownyArchitecturePlugin plugin;

    public ForgeListener(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Block block = event.getBlock();
        if (block.getType() != Material.SPAWNER) return;

        Player player = event.getPlayer();
        ItemStack tool = player.getInventory().getItemInMainHand();

        if (plugin.getForgeManager().isSuperPickaxe(tool)) {
            if (block.getState() instanceof CreatureSpawner spawner) {
                EntityType mobType = spawner.getSpawnedType();
                if (mobType == null) mobType = EntityType.PIG;

                // Prevent standard spawner destruction / exp drop
                event.setDropItems(false);
                event.setExpToDrop(0);

                // Drop captured spawner with mob egg stored
                ItemStack droppedSpawner = plugin.getForgeManager().createCapturedSpawnerItem(mobType);
                block.getWorld().dropItemNaturally(block.getLocation().add(0.5, 0.5, 0.5), droppedSpawner);

                // Destroy Super Pickaxe (1-time use!)
                if (tool.getAmount() > 1) {
                    tool.setAmount(tool.getAmount() - 1);
                } else {
                    player.getInventory().setItemInMainHand(null);
                }
                player.updateInventory();

                // Sound & particles
                block.getWorld().playSound(block.getLocation(), Sound.BLOCK_ANVIL_DESTROY, 1.2f, 1.0f);
                block.getWorld().playSound(block.getLocation(), Sound.ENTITY_ITEM_BREAK, 1.0f, 0.7f);
                block.getWorld().spawnParticle(Particle.EXPLOSION_LARGE, block.getLocation().add(0.5, 0.5, 0.5), 1);
                block.getWorld().spawnParticle(Particle.FIREWORKS_SPARK, block.getLocation().add(0.5, 0.5, 0.5), 35, 0.4, 0.4, 0.4, 0.1);

                String mobNameRu = ForgeManager.getRussianEntityName(mobType);
                player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
                player.sendMessage(ChatColor.GOLD + "⚡ [Кузница] Вы успешно добыли " + ChatColor.LIGHT_PURPLE + "Спавнер Мобов (" + mobNameRu + ")" + ChatColor.GOLD + "!");
                player.sendMessage(ChatColor.YELLOW + "• Супер-Кирка полностью разрушилась после использования.");
                player.sendMessage(ChatColor.GREEN + "• Вы можете поставить этот спавнер в любом месте!");
                player.sendMessage(ChatColor.GOLD + "═════════════════════════════════════════════");
            }
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent event) {
        if (event.getBlockPlaced().getType() != Material.SPAWNER) return;

        ItemStack item = event.getItemInHand();
        if (plugin.getForgeManager().isCapturedSpawner(item)) {
            EntityType mobType = plugin.getForgeManager().getCapturedSpawnerType(item);
            Block block = event.getBlockPlaced();

            if (block.getState() instanceof CreatureSpawner spawner) {
                spawner.setSpawnedType(mobType);
                spawner.update(true);

                String mobNameRu = ForgeManager.getRussianEntityName(mobType);
                event.getPlayer().sendMessage(ChatColor.GREEN + "✔ [Кузница] Установлен спавнер мобов: " + ChatColor.YELLOW + mobNameRu + ChatColor.GREEN + "!");
                event.getPlayer().playSound(block.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.4f);
            }
        }
    }
}
