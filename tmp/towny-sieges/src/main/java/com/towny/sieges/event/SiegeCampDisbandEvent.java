package com.towny.sieges.event;

import com.towny.sieges.model.SiegeCamp;
import org.bukkit.entity.Player;
import org.bukkit.event.Event;
import org.bukkit.event.HandlerList;

/**
 * Событие уничтожения / расформирования осадного лагеря мэром атакующего города.
 * Запускает синхронное восстановление всех чанков лагеря в исходный статус,
 * очистку орудий и мгновенное выключение осадного режима взрывов.
 */
public class SiegeCampDisbandEvent extends Event {

    private static final HandlerList HANDLERS = new HandlerList();

    private final SiegeCamp camp;
    private final Player mayor;
    private final boolean adminForced;

    public SiegeCampDisbandEvent(SiegeCamp camp, Player mayor, boolean adminForced) {
        this.camp = camp;
        this.mayor = mayor;
        this.adminForced = adminForced;
    }

    public SiegeCamp getCamp() {
        return camp;
    }

    public Player getMayor() {
        return mayor;
    }

    public boolean isAdminForced() {
        return adminForced;
    }

    @Override
    public HandlerList getHandlers() {
        return HANDLERS;
    }

    public static HandlerList getHandlerList() {
        return HANDLERS;
    }
}
