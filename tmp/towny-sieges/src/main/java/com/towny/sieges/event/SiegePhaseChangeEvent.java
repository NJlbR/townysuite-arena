package com.towny.sieges.event;

import com.towny.sieges.model.SiegeCamp;
import org.bukkit.event.Event;
import org.bukkit.event.HandlerList;

/**
 * Событие смены фазы осады (например, переход из 24ч подготовки в 2ч активный штурм
 * или завершение осады). Слушается TownyExplosionUnblocker и TownyArchitecture
 * для мгновенной синхронизации орудийных взрывов и оборонительных баффов.
 */
public class SiegePhaseChangeEvent extends Event {

    private static final HandlerList HANDLERS = new HandlerList();

    private final SiegeCamp camp;
    private final SiegeCamp.Status oldStatus;
    private final SiegeCamp.Status newStatus;
    private final boolean assaultActive;

    public SiegePhaseChangeEvent(SiegeCamp camp, SiegeCamp.Status oldStatus, SiegeCamp.Status newStatus) {
        this.camp = camp;
        this.oldStatus = oldStatus;
        this.newStatus = newStatus;
        this.assaultActive = (newStatus == SiegeCamp.Status.ACTIVE_SIEGE);
    }

    public SiegeCamp getCamp() {
        return camp;
    }

    public SiegeCamp.Status getOldStatus() {
        return oldStatus;
    }

    public SiegeCamp.Status getNewStatus() {
        return newStatus;
    }

    public boolean isAssaultActive() {
        return assaultActive;
    }

    public String getAttackingTown() {
        return camp != null ? camp.getAttackingTown() : "";
    }

    public String getDefendingTown() {
        return camp != null ? camp.getDefendingTown() : "";
    }

    @Override
    public HandlerList getHandlers() {
        return HANDLERS;
    }

    public static HandlerList getHandlerList() {
        return HANDLERS;
    }
}
