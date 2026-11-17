package com.towny.jobs.gui;

import com.palmergames.bukkit.towny.object.Resident;
import com.palmergames.bukkit.towny.object.Town;
import com.towny.jobs.TownyJobsPlugin;
import com.towny.jobs.manager.TownyJobsManager;
import com.towny.jobs.manager.TownyJobsManager.JobRole;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.OfflinePlayer;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.SkullMeta;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public final class JobsMenu {
    private static final int[] ROLE_SLOTS = {
            10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34,
            11, 13, 15, 20, 22, 24, 29, 31, 33
    };
    private final TownyJobsPlugin plugin;
    private final TownyJobsManager manager;
    private final Map<UUID, PendingInput> pendingInputs = new ConcurrentHashMap<>();

    public JobsMenu(TownyJobsPlugin plugin, TownyJobsManager manager) {
        this.plugin = plugin;
        this.manager = manager;
    }

    public void open(Player player) {
        Town town = manager.getPlayerTown(player);
        if (town == null) {
            player.sendMessage("§cДля открытия меню нужно состоять в городе Towny.");
            return;
        }
        openMain(player, town);
    }

    public void openMain(Player player, Town town) {
        if (town == null) return;
        String title = color(plugin.getConfig().getString("menu-title", "Работы города"));
        JobsMenuHolder holder = new JobsMenuHolder(JobsMenuHolder.Mode.MAIN, manager.townId(town), "", 0);
        Inventory inventory = Bukkit.createInventory(holder, 54, title);
        holder.setInventory(inventory);

        List<JobRole> roles = manager.getRoles();
        int max = Math.min(roles.size(), ROLE_SLOTS.length);
        for (int i = 0; i < max; i++) {
            JobRole role = roles.get(i);
            List<String> lore = new ArrayList<>();
            lore.add("§7Зарплата: §e" + format(manager.getSalary(town, role.id)) + "§7 в день");
            lore.add("§7Жителей с ролью: §f" + manager.getRoleMembers(town, role.id).size());
            lore.add(" ");
            if (manager.mayManage(player, town)) {
                lore.add("§aЛКМ: изменить зарплату");
                lore.add("§bПКМ: назначить или снять роль");
            } else {
                lore.add("§7Роль города");
            }
            inventory.setItem(ROLE_SLOTS[i], item(role.icon, "§6" + role.displayName, lore));
        }
        if (roles.isEmpty()) {
            inventory.setItem(22, item(Material.BARRIER, "§cРоли не настроены", Collections.singletonList("§7Попросите администратора настроить роли.")));
        } else if (roles.size() > ROLE_SLOTS.length) {
            inventory.setItem(4, item(Material.BOOK, "§eСписок ролей сокращён", Collections.singletonList("§7Показаны первые " + ROLE_SLOTS.length + " ролей.")));
        }

        boolean canManage = manager.mayManage(player, town);
        List<String> payrollLore = new ArrayList<>();
        payrollLore.add("§7Ежедневные выплаты из казны города");
        payrollLore.add("§7Статус: " + status(manager.isPayrollEnabled(town)));
        if (canManage) payrollLore.add("§eНажмите, чтобы переключить");
        inventory.setItem(45, item(Material.GOLD_INGOT, "§6Выплата зарплат", payrollLore));

        List<String> dutyLore = new ArrayList<>();
        dutyLore.add("§7Обязать строителей выполнять норму");
        dutyLore.add("§7Статус: " + status(manager.isBuilderDutyEnabled(town)));
        dutyLore.add("§7Действует только в дни активных строек TownyArchitecture.");
        if (!plugin.getArchitectureHook().isAvailable()) dutyLore.add("§cTownyArchitecture не установлен; норма не применяется.");
        if (canManage) dutyLore.add("§eНажмите, чтобы переключить");
        inventory.setItem(47, item(Material.IRON_PICKAXE, "§6Норма строителей", dutyLore));

        List<String> quotaLore = Arrays.asList(
                "§7Дневная норма: §f" + manager.getBuilderQuota(town) + " блоков",
                canManage ? "§eНажмите, чтобы изменить" : "§7Изменить может только мэр"
        );
        inventory.setItem(49, item(Material.WRITABLE_BOOK, "§6Дневная норма строителя", quotaLore));
        inventory.setItem(53, item(Material.BARRIER, "§cЗакрыть", Collections.singletonList("§7Закрыть меню")));
        player.openInventory(inventory);
    }

    public void openMembers(Player player, Town town, String roleId, int page) {
        JobRole role = manager.getRole(roleId);
        if (town == null || role == null) return;
        List<Resident> residents = manager.getResidents(town);
        int pageCount = Math.max(1, (residents.size() + 44) / 45);
        page = Math.max(0, Math.min(page, pageCount - 1));
        JobsMenuHolder holder = new JobsMenuHolder(JobsMenuHolder.Mode.MEMBERS, manager.townId(town), roleId, page);
        Inventory inventory = Bukkit.createInventory(holder, 54, color("§8Роль города: §e" + role.displayName));
        holder.setInventory(inventory);

        int start = page * 45;
        int end = Math.min(residents.size(), start + 45);
        for (int index = start; index < end; index++) {
            Resident resident = residents.get(index);
            UUID uuid = resident.getUUID();
            boolean assigned = manager.hasRole(town, uuid, roleId);
            ItemStack head = new ItemStack(Material.PLAYER_HEAD);
            SkullMeta meta = (SkullMeta) head.getItemMeta();
            if (meta != null) {
                OfflinePlayer offline = Bukkit.getOfflinePlayer(uuid);
                meta.setOwningPlayer(offline);
                meta.setDisplayName((assigned ? "§a✔ " : "§c✖ ") + resident.getName());
                List<String> lore = new ArrayList<>();
                lore.add(assigned ? "§7Роль назначена" : "§7Роль не назначена");
                lore.add("§eНажмите, чтобы " + (assigned ? "снять роль" : "назначить роль"));
                meta.setLore(lore);
                head.setItemMeta(meta);
            }
            inventory.setItem(index - start, head);
        }
        inventory.setItem(45, item(Material.ARROW, "§eПредыдущая страница", Collections.singletonList("§7Страница " + (page + 1) + "/" + pageCount)));
        inventory.setItem(49, item(Material.BARRIER, "§cНазад", Collections.singletonList("§7К списку ролей")));
        inventory.setItem(53, item(Material.ARROW, "§eСледующая страница", Collections.singletonList("§7Страница " + (page + 1) + "/" + pageCount)));
        player.openInventory(inventory);
    }

    public boolean hasPendingInput(Player player) {
        return pendingInputs.containsKey(player.getUniqueId());
    }

    public void promptSalary(Player player, Town town, JobRole role) {
        pendingInputs.put(player.getUniqueId(), new PendingInput(manager.townId(town), role.id, InputType.SALARY));
        player.closeInventory();
        player.sendMessage("§eВведите дневную зарплату роли §6" + role.displayName + "§e или введите cancel.");
        player.sendMessage("§7Укажите неотрицательную сумму, например 25 или 12.50.");
    }

    public void promptQuota(Player player, Town town) {
        pendingInputs.put(player.getUniqueId(), new PendingInput(manager.townId(town), "", InputType.QUOTA));
        player.closeInventory();
        player.sendMessage("§eВведите минимальное число правильных строительных блоков в день или cancel.");
    }

    public void handleInput(Player player, String message) {
        PendingInput input = pendingInputs.remove(player.getUniqueId());
        if (input == null) return;
        Bukkit.getScheduler().runTask(plugin, () -> {
            if (message.equalsIgnoreCase("cancel")) {
                player.sendMessage("§7Ввод отменён.");
                Town town = manager.findTown(input.townId);
                if (town != null) openMain(player, town);
                return;
            }
            Town town = manager.findTown(input.townId);
            if (town == null || !manager.mayManage(player, town)) {
                player.sendMessage("§cУ вас больше нет прав управлять работами этого города.");
                return;
            }
            try {
                if (input.type == InputType.SALARY) {
                    double amount = Double.parseDouble(message.trim());
                    if (!Double.isFinite(amount) || amount < 0) throw new NumberFormatException();
                    manager.setSalary(town, input.roleId, amount);
                    player.sendMessage("§aДневная зарплата обновлена: §e" + format(amount) + "§a.");
                } else {
                    int quota = Integer.parseInt(message.trim());
                    if (quota < 0) throw new NumberFormatException();
                    manager.setBuilderQuota(town, quota);
                    player.sendMessage("§aДневная норма строителя обновлена: §e" + quota + "§a блоков.");
                }
                openMain(player, town);
            } catch (NumberFormatException error) {
                player.sendMessage("§cНекорректное значение. Введите неотрицательное число или cancel.");
                pendingInputs.put(player.getUniqueId(), input);
            }
        });
    }

    public void clearInput(Player player) {
        pendingInputs.remove(player.getUniqueId());
    }

    public void handleMainClick(Player player, Town town, int slot, ClickType click) {
        if (slot == 53) {
            player.closeInventory();
            return;
        }
        if (slot == 45) {
            if (!manager.mayManage(player, town)) return;
            boolean enabled = !manager.isPayrollEnabled(town);
            manager.setPayrollEnabled(town, enabled);
            player.sendMessage("§aВыплата зарплат " + (enabled ? "включена" : "выключена") + ".");
            openMain(player, town);
            return;
        }
        if (slot == 47) {
            if (!manager.mayManage(player, town)) return;
            boolean enabled = !manager.isBuilderDutyEnabled(town);
            manager.setBuilderDutyEnabled(town, enabled);
            player.sendMessage("§aНорма строителей " + (enabled ? "включена" : "выключена") + ".");
            openMain(player, town);
            return;
        }
        if (slot == 49) {
            if (manager.mayManage(player, town)) promptQuota(player, town);
            return;
        }
        List<JobRole> roles = manager.getRoles();
        for (int index = 0; index < Math.min(roles.size(), ROLE_SLOTS.length); index++) {
            if (ROLE_SLOTS[index] != slot) continue;
            if (!manager.mayManage(player, town)) return;
            JobRole role = roles.get(index);
            if (click.isRightClick()) openMembers(player, town, role.id, 0);
            else promptSalary(player, town, role);
            return;
        }
    }

    private ItemStack item(Material material, String name, List<String> lore) {
        ItemStack stack = new ItemStack(material);
        ItemMeta meta = stack.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(color(name));
            List<String> translated = new ArrayList<>();
            for (String line : lore) translated.add(color(line));
            meta.setLore(translated);
            stack.setItemMeta(meta);
        }
        return stack;
    }

    private String color(String text) {
        return ChatColor.translateAlternateColorCodes('&', text == null ? "" : text);
    }

    private String status(boolean value) {
        return value ? "§aВКЛ" : "§cВЫКЛ";
    }

    private String format(double amount) {
        return String.format(java.util.Locale.US, "%.2f", amount);
    }

    private enum InputType { SALARY, QUOTA }

    private static final class PendingInput {
        private final String townId;
        private final String roleId;
        private final InputType type;

        private PendingInput(String townId, String roleId, InputType type) {
            this.townId = townId;
            this.roleId = roleId;
            this.type = type;
        }
    }
}
