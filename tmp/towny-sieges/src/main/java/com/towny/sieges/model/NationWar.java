package com.towny.sieges.model;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * Model for Nation War:
 * - Unified 24h preparation countdown across ALL towns of both nations.
 * - Unified 2h active assault phase: ALL towns of both nations are vulnerable to explosions!
 * - Siege camps placed during the war inherit and continue the unified nation timer.
 */
public class NationWar {

    public enum Status {
        PREPARATION,    // 24h: unified countdown, camps can be claimed, explosions blocked
        ACTIVE_ASSAULT, // 2h: active assault phase, explosions unblocked across ALL towns of both nations!
        COMPLETED       // Concluded
    }

    private final String warId;
    private final String attackerNation;
    private final String defenderNation;
    private final String declaredByLeader;

    private final Set<String> attackerTowns = new LinkedHashSet<>();
    private final Set<String> defenderTowns = new LinkedHashSet<>();
    private final List<String> linkedCampIds = new ArrayList<>();

    private long createdAtMillis;
    private long preparationEndsAtMillis;
    private long activeEndsAtMillis;
    private Status status;

    public NationWar(String warId, String attackerNation, String defenderNation, String declaredByLeader,
                     Set<String> attackerTowns, Set<String> defenderTowns,
                     long prepSeconds, long assaultSeconds) {
        this.warId = warId;
        this.attackerNation = attackerNation;
        this.defenderNation = defenderNation;
        this.declaredByLeader = declaredByLeader;
        if (attackerTowns != null) this.attackerTowns.addAll(attackerTowns);
        if (defenderTowns != null) this.defenderTowns.addAll(defenderTowns);
        this.createdAtMillis = System.currentTimeMillis();
        this.preparationEndsAtMillis = this.createdAtMillis + (prepSeconds * 1000L);
        this.activeEndsAtMillis = this.preparationEndsAtMillis + (assaultSeconds * 1000L);
        this.status = Status.PREPARATION;
    }

    public NationWar(String warId, String attackerNation, String defenderNation, String declaredByLeader,
                     Set<String> attackerTowns, Set<String> defenderTowns, List<String> linkedCampIds,
                     long createdAtMillis, long preparationEndsAtMillis, long activeEndsAtMillis, Status status) {
        this.warId = warId;
        this.attackerNation = attackerNation;
        this.defenderNation = defenderNation;
        this.declaredByLeader = declaredByLeader;
        if (attackerTowns != null) this.attackerTowns.addAll(attackerTowns);
        if (defenderTowns != null) this.defenderTowns.addAll(defenderTowns);
        if (linkedCampIds != null) this.linkedCampIds.addAll(linkedCampIds);
        this.createdAtMillis = createdAtMillis;
        this.preparationEndsAtMillis = preparationEndsAtMillis;
        this.activeEndsAtMillis = activeEndsAtMillis;
        this.status = status;
    }

    public boolean isTownParticipating(String townName) {
        if (townName == null) return false;
        for (String t : attackerTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        for (String t : defenderTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        return false;
    }

    public boolean isAttackerTown(String townName) {
        if (townName == null) return false;
        for (String t : attackerTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        return false;
    }

    public boolean isTownAttacker(String townName) {
        return isAttackerTown(townName);
    }

    public boolean isDefenderTown(String townName) {
        if (townName == null) return false;
        for (String t : defenderTowns) {
            if (t.equalsIgnoreCase(townName)) return true;
        }
        return false;
    }

    public boolean isTownDefender(String townName) {
        return isDefenderTown(townName);
    }

    public boolean isActiveAssault() {
        return status == Status.ACTIVE_ASSAULT;
    }

    public boolean isPreparation() {
        return status == Status.PREPARATION;
    }

    public String getWarId() { return warId; }
    public String getAttackerNation() { return attackerNation; }
    public String getDefenderNation() { return defenderNation; }
    public String getDeclaredByLeader() { return declaredByLeader; }
    public Set<String> getAttackerTowns() { return attackerTowns; }
    public Set<String> getDefenderTowns() { return defenderTowns; }
    public List<String> getLinkedCampIds() { return linkedCampIds; }
    public long getCreatedAtMillis() { return createdAtMillis; }
    public long getPreparationEndsAtMillis() { return preparationEndsAtMillis; }
    public void setPreparationEndsAtMillis(long ms) { this.preparationEndsAtMillis = ms; }
    public long getActiveEndsAtMillis() { return activeEndsAtMillis; }
    public void setActiveEndsAtMillis(long ms) { this.activeEndsAtMillis = ms; }
    public Status getStatus() { return status; }
    public void setStatus(Status s) { this.status = s; }

    public void addLinkedCamp(String campId) {
        if (!linkedCampIds.contains(campId)) {
            linkedCampIds.add(campId);
        }
    }

    public long getRemainingSeconds() {
        long now = System.currentTimeMillis();
        if (status == Status.PREPARATION) {
            return Math.max(0, (preparationEndsAtMillis - now) / 1000L);
        } else if (status == Status.ACTIVE_ASSAULT) {
            return Math.max(0, (activeEndsAtMillis - now) / 1000L);
        }
        return 0L;
    }

    public String getFormattedRemainingTime() {
        long sec = getRemainingSeconds();
        long h = sec / 3600;
        long m = (sec % 3600) / 60;
        long s = sec % 60;
        return String.format("%02d:%02d:%02d", h, m, s);
    }
}
