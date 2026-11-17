package com.towny.jobs.manager;

import com.palmergames.bukkit.towny.TownyAPI;
import com.palmergames.bukkit.towny.object.Resident;
import com.palmergames.bukkit.towny.object.Town;
import com.towny.jobs.TownyJobsPlugin;
import com.towny.jobs.hook.TownyArchitectureHook;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.permissions.PermissionAttachment;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Persistent town roles, salary settings, builder quotas, and Towny account payroll. */
public final class TownyJobsManager {
    private final TownyJobsPlugin plugin;
    private final TownyArchitectureHook architecture;
    private final File dataFile;
    private YamlConfiguration data;
    private final Map<UUID, PermissionAttachment> attachments = new HashMap<>();
    public TownyJobsManager(TownyJobsPlugin plugin, TownyArchitectureHook architecture) {
        this.plugin = plugin;
        this.architecture = architecture;
        this.dataFile = new File(plugin.getDataFolder(), "jobs-data.yml");
    }

    public void load() {
        if (!plugin.getDataFolder().exists() && !plugin.getDataFolder().mkdirs()) {
            plugin.getLogger().severe("Could not create TownyJobs data directory.");
        }
        data = YamlConfiguration.loadConfiguration(dataFile);
        plugin.reloadConfig();
        if (data.getString("last-payroll-date") == null) {
            data.set("last-payroll-date", LocalDate.now().minusDays(1).toString());
            saveData();
        }
    }

    public void shutdown() {
        saveData();
        for (PermissionAttachment attachment : new ArrayList<>(attachments.values())) {
            try {
                attachment.remove();
            } catch (IllegalArgumentException ignored) {
            }
        }
        attachments.clear();
    }

    public void tick() {
        saveData();
        runDuePayrolls();
    }

    public void refreshActiveConstructionSnapshot() {
        if (!architecture.isAvailable()) return;
        LocalDate today = LocalDate.now();
        for (Town town : getTowns()) {
            if (architecture.hasActiveConstruction(town.getName())) {
                data.set("active-construction." + today + "." + townId(town), true);
            }
        }
        saveData();
    }

    public List<JobRole> getRoles() {
        ConfigurationSection section = plugin.getConfig().getConfigurationSection("roles");
        if (section == null) return Collections.emptyList();
        List<JobRole> roles = new ArrayList<>();
        for (String id : section.getKeys(false)) {
            if (!id.matches("[a-z0-9_-]+")) {
                plugin.getLogger().warning("Ignoring invalid job role key: " + id);
                continue;
            }
            ConfigurationSection role = section.getConfigurationSection(id);
            if (role == null) continue;
            Material icon = Material.matchMaterial(role.getString("icon", "NAME_TAG"));
            if (icon == null || !icon.isItem()) icon = Material.NAME_TAG;
            List<String> permissions = new ArrayList<>(role.getStringList("permissions"));
            String permission = role.getString("permission", "");
            if (!permission.isBlank() && !permissions.contains(permission)) permissions.add(permission);
            String roleNode = "townyjobs.role." + id;
            if (!permissions.contains(roleNode)) permissions.add(roleNode);
            roles.add(new JobRole(id, role.getString("display-name", id), icon,
                    role.getString("towny-rank", "").trim(), permissions));
        }
        return roles;
    }

    public JobRole getRole(String id) {
        if (id == null) return null;
        for (JobRole role : getRoles()) if (role.id.equals(id)) return role;
        return null;
    }

    public Town getPlayerTown(Player player) {
        if (player == null || !Bukkit.getPluginManager().isPluginEnabled("Towny")) return null;
        try {
            Resident resident = TownyAPI.getInstance().getResident(player.getUniqueId());
            return resident != null && resident.hasTown() ? resident.getTownOrNull() : null;
        } catch (Throwable error) {
            return null;
        }
    }

    public Town findTown(String id) {
        if (id == null) return null;
        for (Town town : getTowns()) if (townId(town).equals(id)) return town;
        return null;
    }

    public List<Town> getTowns() {
        try {
            return new ArrayList<>(TownyAPI.getInstance().getTowns());
        } catch (Throwable error) {
            return Collections.emptyList();
        }
    }

    public boolean isMayor(Player player, Town town) {
        if (player == null || town == null || town.getMayor() == null) return false;
        return player.getUniqueId().equals(town.getMayor().getUUID());
    }

    public boolean mayManage(Player player, Town town) {
        return player != null && (player.hasPermission("townyjobs.admin") || isMayor(player, town));
    }

    public String townId(Town town) {
        return town.getUUID().toString();
    }

    public List<Resident> getResidents(Town town) {
        List<Resident> residents = new ArrayList<>(town.getResidents());
        residents.sort(Comparator.comparing(Resident::getName, String.CASE_INSENSITIVE_ORDER));
        return residents;
    }

    public Set<UUID> getRoleMembers(Town town, String roleId) {
        if (town == null || getRole(roleId) == null) return Collections.emptySet();
        List<String> raw = data.getStringList(rolePath(town, roleId));
        Set<UUID> members = new LinkedHashSet<>();
        for (String value : raw) {
            try {
                members.add(UUID.fromString(value));
            } catch (IllegalArgumentException ignored) {
            }
        }
        return members;
    }

    public boolean hasRole(Town town, UUID playerId, String roleId) {
        return town != null && playerId != null && getRoleMembers(town, roleId).contains(playerId);
    }

    public List<JobRole> getAssignedRoles(Town town, UUID playerId) {
        List<JobRole> result = new ArrayList<>();
        for (JobRole role : getRoles()) if (hasRole(town, playerId, role.id)) result.add(role);
        return result;
    }

    public boolean toggleRole(Town town, Resident resident, String roleId) {
        JobRole role = getRole(roleId);
        if (town == null || resident == null || role == null || !town.hasResident(resident)) return false;
        Set<UUID> members = new LinkedHashSet<>(getRoleMembers(town, roleId));
        UUID playerId = resident.getUUID();
        boolean assigned;
        if (members.remove(playerId)) {
            assigned = false;
            data.set(rolePath(town, roleId), toStrings(members));
            removeTownRankIfOwned(town, resident, role);
        } else {
            assigned = true;
            members.add(playerId);
            data.set(rolePath(town, roleId), toStrings(members));
            addTownRankIfNeeded(town, resident, role);
        }
        try {
            resident.save();
        } catch (Throwable ignored) {
        }
        Player online = Bukkit.getPlayer(playerId);
        if (online != null) syncPlayerPermissions(online);
        saveData();
        return assigned;
    }

    private void addTownRankIfNeeded(Town town, Resident resident, JobRole role) {
        if (role.townyRank.isBlank() || resident.hasTownRank(role.townyRank)) return;
        try {
            if (resident.addTownRank(role.townyRank)) {
                List<String> owned = data.getStringList(managedRanksPath(town, resident.getUUID()));
                if (!owned.contains(role.townyRank)) owned.add(role.townyRank);
                data.set(managedRanksPath(town, resident.getUUID()), owned);
            }
        } catch (Throwable error) {
            plugin.getLogger().warning("Could not assign Towny rank '" + role.townyRank + "' to " + resident.getName() + ": " + error.getMessage());
        }
    }

    private void removeTownRankIfOwned(Town town, Resident resident, JobRole removedRole) {
        if (removedRole.townyRank.isBlank()) return;
        for (JobRole role : getAssignedRoles(town, resident.getUUID())) {
            if (role.townyRank.equalsIgnoreCase(removedRole.townyRank)) return;
        }
        List<String> owned = data.getStringList(managedRanksPath(town, resident.getUUID()));
        if (!owned.removeIf(rank -> rank.equalsIgnoreCase(removedRole.townyRank))) return;
        data.set(managedRanksPath(town, resident.getUUID()), owned);
        try {
            resident.removeTownRank(removedRole.townyRank);
        } catch (Throwable error) {
            plugin.getLogger().warning("Could not remove Towny rank '" + removedRole.townyRank + "' from " + resident.getName() + ": " + error.getMessage());
        }
    }

    public void syncOnlinePlayers() {
        for (Player player : Bukkit.getOnlinePlayers()) syncPlayerPermissions(player);
    }

    public void syncPlayerPermissions(Player player) {
        PermissionAttachment old = attachments.remove(player.getUniqueId());
        if (old != null) {
            try {
                old.remove();
            } catch (IllegalArgumentException ignored) {
            }
        }
        Town town = getPlayerTown(player);
        if (town == null) return;
        List<JobRole> roles = getAssignedRoles(town, player.getUniqueId());
        if (roles.isEmpty()) return;
        PermissionAttachment attachment = player.addAttachment(plugin);
        for (JobRole role : roles) for (String permission : role.permissions) attachment.setPermission(permission, true);
        attachments.put(player.getUniqueId(), attachment);
        player.recalculatePermissions();
    }

    public void clearPlayerPermissions(Player player) {
        PermissionAttachment attachment = attachments.remove(player.getUniqueId());
        if (attachment != null) {
            try {
                player.removeAttachment(attachment);
            } catch (IllegalArgumentException ignored) {
            }
        }
    }

    public double getSalary(Town town, String roleId) {
        return town == null ? 0.0 : Math.max(0.0, data.getDouble("towns." + townId(town) + ".salary." + roleId, 0.0));
    }

    public void setSalary(Town town, String roleId, double amount) {
        if (town == null || getRole(roleId) == null || !Double.isFinite(amount) || amount < 0) return;
        data.set("towns." + townId(town) + ".salary." + roleId, Math.round(amount * 100.0) / 100.0);
        saveData();
    }

    public boolean isPayrollEnabled(Town town) {
        return town != null && data.getBoolean("towns." + townId(town) + ".payroll-enabled", false);
    }

    public void setPayrollEnabled(Town town, boolean enabled) {
        data.set("towns." + townId(town) + ".payroll-enabled", enabled);
        saveData();
    }

    public boolean isBuilderDutyEnabled(Town town) {
        return town != null && data.getBoolean("towns." + townId(town) + ".builder-duty-enabled", false);
    }

    public void setBuilderDutyEnabled(Town town, boolean enabled) {
        data.set("towns." + townId(town) + ".builder-duty-enabled", enabled);
        saveData();
    }

    public int getBuilderQuota(Town town) {
        return town == null ? 0 : Math.max(0, data.getInt("towns." + townId(town) + ".builder-daily-quota",
                plugin.getConfig().getInt("default-builder-daily-quota", 100)));
    }

    public void setBuilderQuota(Town town, int quota) {
        if (town == null || quota < 0) return;
        data.set("towns." + townId(town) + ".builder-daily-quota", quota);
        saveData();
    }

    public void recordBlueprintPlacement(Player player, org.bukkit.event.block.BlockPlaceEvent event) {
        Town town = getPlayerTown(player);
        if (town == null) return;
        String roleId = plugin.getConfig().getString("builder-quota-role", "builder");
        if (!hasRole(town, player.getUniqueId(), roleId)) return;
        if (!architecture.isCorrectCompletedBlueprintBlock(player, event, town.getName())) return;
        LocalDate today = LocalDate.now();
        String townId = townId(town);
        data.set("active-construction." + today + "." + townId, true);
        String countPath = "work." + today + "." + townId + "." + player.getUniqueId();
        data.set(countPath, data.getLong(countPath) + 1L);
    }

    private void runDuePayrolls() {
        LocalDate dueThrough = LocalDate.now().minusDays(1);
        LocalDate last;
        try {
            last = LocalDate.parse(data.getString("last-payroll-date", dueThrough.toString()));
        } catch (DateTimeParseException error) {
            last = dueThrough;
        }
        int catchUpDays = 0;
        while (last.isBefore(dueThrough) && catchUpDays++ < 31) {
            LocalDate day = last.plusDays(1);
            for (Town town : getTowns()) processTownPayroll(town, day);
            data.set("last-payroll-date", day.toString());
            saveData();
            last = day;
        }
    }

    private void processTownPayroll(Town town, LocalDate day) {
        String townId = townId(town);
        String processedPath = "towns." + townId + ".processed-payroll." + day;
        if (data.getBoolean(processedPath, false) || !isPayrollEnabled(town)) {
            data.set(processedPath, true);
            return;
        }

        boolean enforceBuilderQuota = isBuilderDutyEnabled(town)
                && data.getBoolean("active-construction." + day + "." + townId, false);
        String quotaRole = plugin.getConfig().getString("builder-quota-role", "builder");
        int quota = getBuilderQuota(town);
        Map<UUID, Resident> residents = new LinkedHashMap<>();
        for (Resident resident : getResidents(town)) residents.put(resident.getUUID(), resident);

        List<Payout> payouts = new ArrayList<>();
        double total = 0;
        for (Resident resident : residents.values()) {
            UUID uuid = resident.getUUID();
            double amount = 0;
            boolean builderFailed = false;
            for (JobRole role : getAssignedRoles(town, uuid)) {
                double salary = getSalary(town, role.id);
                if (salary <= 0) continue;
                if (enforceBuilderQuota && role.id.equalsIgnoreCase(quotaRole)
                        && data.getLong("work." + day + "." + townId + "." + uuid, 0L) < quota) {
                    builderFailed = true;
                    continue;
                }
                amount += salary;
            }
            if (builderFailed) notifyQuotaFailure(uuid, town, quota, day);
            if (amount <= 0) continue;
            String paidPath = "towns." + townId + ".payouts." + day + "." + uuid;
            if (data.getBoolean(paidPath, false)) continue;
            payouts.add(new Payout(uuid, resident, amount));
            total += amount;
        }

        if (payouts.isEmpty()) {
            data.set(processedPath, true);
            return;
        }

        try {
            double balance = town.getAccount().getHoldingBalance();
            if (balance + 0.000001 < total) {
                notifyMayor(town, "§cTownyJobs: выплата за " + day + " пропущена — в казне не хватает средств на всю зарплату.");
                plugin.getLogger().info("Skipped TownyJobs payroll for " + town.getName() + " on " + day + ": insufficient treasury.");
                data.set(processedPath, true);
                return;
            }
            for (Payout payout : payouts) {
                String reason = "TownyJobs daily salary " + day;
                boolean withdrawn = town.getAccount().withdraw(payout.amount, reason);
                if (!withdrawn) {
                    // The initial full-payroll balance check passed, but another transaction may have raced us.
                    notifyMayor(town, "§cTownyJobs: выплата остановлена — не удалось списать средства из казны.");
                    break;
                }
                boolean deposited = payout.resident.getAccount().deposit(payout.amount, reason);
                if (!deposited) {
                    town.getAccount().deposit(payout.amount, "TownyJobs refund after failed salary deposit " + day);
                    plugin.getLogger().warning("Refunded failed TownyJobs salary to town " + town.getName() + " for resident " + payout.resident.getName());
                    continue;
                }
                data.set("towns." + townId + ".payouts." + day + "." + payout.uuid, true);
                Player online = Bukkit.getPlayer(payout.uuid);
                if (online != null) online.sendMessage("§aTownyJobs: город выплатил §e" + String.format(java.util.Locale.US, "%.2f", payout.amount) + "§a за " + day + ".");
            }
            data.set(processedPath, true);
            saveData();
        } catch (Throwable error) {
            plugin.getLogger().severe("TownyJobs payroll failed for " + town.getName() + " on " + day + ": " + error.getMessage());
        }
    }

    private void notifyQuotaFailure(UUID playerId, Town town, int quota, LocalDate day) {
        Player player = Bukkit.getPlayer(playerId);
        if (player != null) player.sendMessage("§cTownyJobs: зарплата строителя за " + day + " удержана (норма: " + quota + " правильно установленных блоков).");
    }

    private void notifyMayor(Town town, String message) {
        if (town.getMayor() == null) return;
        Player mayor = Bukkit.getPlayer(town.getMayor().getUUID());
        if (mayor != null) mayor.sendMessage(message);
    }

    private String rolePath(Town town, String roleId) {
        return "towns." + townId(town) + ".roles." + roleId;
    }

    private String managedRanksPath(Town town, UUID playerId) {
        return "towns." + townId(town) + ".managed-ranks." + playerId;
    }

    private List<String> toStrings(Collection<UUID> ids) {
        List<String> result = new ArrayList<>();
        for (UUID id : ids) result.add(id.toString());
        return result;
    }

    public void saveData() {
        if (data == null) return;
        try {
            data.save(dataFile);
        } catch (IOException error) {
            plugin.getLogger().severe("Could not save TownyJobs data: " + error.getMessage());
        }
    }

    private static final class Payout {
        private final UUID uuid;
        private final Resident resident;
        private final double amount;

        private Payout(UUID uuid, Resident resident, double amount) {
            this.uuid = uuid;
            this.resident = resident;
            this.amount = amount;
        }
    }

    public static final class JobRole {
        public final String id;
        public final String displayName;
        public final Material icon;
        public final String townyRank;
        public final List<String> permissions;

        public JobRole(String id, String displayName, Material icon, String townyRank, List<String> permissions) {
            this.id = id;
            this.displayName = displayName;
            this.icon = icon;
            this.townyRank = townyRank;
            this.permissions = Collections.unmodifiableList(permissions);
        }
    }
}
