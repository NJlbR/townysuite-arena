package com.towny.sieges.model;

/**
 * Исходный статус чанка до включения в осадный лагерь.
 * После окончания осады/штурма или уничтожения лагеря чанк автоматически
 * возвращается именно к этому статусу.
 */
public enum PreviousChunkStatus {
    /** Обычный присоединённый чанк атакующего города */
    TOWN_CHUNK("Чанк города"),

    /** Официальный аванпост атакующего города */
    OUTPOST("Аванпост"),

    /** Ничейные дикие земли (Wilderness) */
    WILDERNESS("Дикие земли");

    private final String titleRu;

    PreviousChunkStatus(String titleRu) {
        this.titleRu = titleRu;
    }

    public String getTitleRu() {
        return titleRu;
    }
}
