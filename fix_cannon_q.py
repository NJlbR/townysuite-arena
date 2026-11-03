with open('tmp/towny-sieges/src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove onPlayerAnimation
animation_handler = """    @EventHandler(priority = EventPriority.HIGH)
    public void onPlayerAnimation(PlayerAnimationEvent event) {
        Player player = event.getPlayer();
        if (cannonManager.isMounted(player)) {
            Long mountTime = cannonManager.getLastMountTime(player.getUniqueId());
            if (mountTime != null && System.currentTimeMillis() - mountTime < 750L) {
                return;
            }
            cannonManager.fireCannon(player);
        }
    }
"""
if animation_handler in content:
    content = content.replace(animation_handler, "")
    print("Removed onPlayerAnimation handler")

# 2. Update onPlayerDropItem to cancel ALL drops while mounted
old_drop_handler = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDropItem(PlayerDropItemEvent event) {
        if (cannonManager.isMounted(event.getPlayer())) {
            ItemStack dropped = event.getItemDrop().getItemStack();
            if (cannonManager.isAimingTool(dropped)) {
                event.setCancelled(true);
            }
        }
    }"""

new_drop_handler = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerDropItem(PlayerDropItemEvent event) {
        if (cannonManager.isMounted(event.getPlayer())) {
            event.setCancelled(true);
        }
    }"""

if old_drop_handler in content:
    content = content.replace(old_drop_handler, new_drop_handler)
    print("Updated onPlayerDropItem to cancel ALL drops")
else:
    print("Could not find old_drop_handler")

with open('tmp/towny-sieges/src/main/java/com/towny/sieges/listener/SiegeProtectionListener.java', 'w', encoding='utf-8') as f:
    f.write(content)
