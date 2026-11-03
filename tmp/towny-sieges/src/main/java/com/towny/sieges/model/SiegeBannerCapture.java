package com.towny.sieges.model;

import org.bukkit.Location;

import java.util.Objects;

/**
 * Модель активной сессии почанкового захвата штурмовым флагом во время осады.
 * Базовое время: 5 минут (300 секунд).
 * Время реально необходимое для захвата рассчитывается из базового времени и коэффициента перевеса сил.
 * Чем больше перевес атакующих на чанке, тем быстрее идет захват.
 * Если защитников больше — прогресс откатывается, а при уходе в минус чанк переходит защитникам
 * (при отсутствии общей границы становится официальным аванпостом Towny).
 */
public class SiegeBannerCapture {

    private final String captureId;
    private final ChunkCoord chunk;
    private final Location bannerLocation;
    private final String siegeId;
    private final String attackingTown;
    private final String defendingTown;
    private final String attackerNation;
    private final String defenderNation;
    private final boolean isNationWar;

    private final long startedAtMillis;
    private final boolean isHomeBlock;
    private long shieldBonusSeconds;
    private long baseDurationSeconds;

    // Прогресс от -1.0 до +1.0 (0.0 при старте, 1.0 = полный захват атакующими, < 0 = контр-захват защитниками)
    private double progress;
    private int currentAttackers;
    private int currentDefenders;

    private boolean completed;
    private boolean repelled;

    public SiegeBannerCapture(String captureId, ChunkCoord chunk, Location bannerLocation,
                              String siegeId, String attackingTown, String defendingTown,
                              String attackerNation, String defenderNation, boolean isNationWar,
                              long baseDurationSeconds, boolean isHomeBlock, long shieldBonusSeconds) {
        this.captureId = captureId;
        this.chunk = chunk;
        this.bannerLocation = bannerLocation;
        this.siegeId = siegeId;
        this.attackingTown = attackingTown;
        this.defendingTown = defendingTown;
        this.attackerNation = attackerNation;
        this.defenderNation = defenderNation;
        this.isNationWar = isNationWar;
        this.startedAtMillis = System.currentTimeMillis();
        this.isHomeBlock = isHomeBlock;
        this.shieldBonusSeconds = shieldBonusSeconds;
        this.baseDurationSeconds = Math.max(30L, baseDurationSeconds + shieldBonusSeconds);
        this.progress = 0.0;
        this.currentAttackers = 0;
        this.currentDefenders = 0;
        this.completed = false;
        this.repelled = false;
    }

    public String getCaptureId() {
        return captureId;
    }

    public ChunkCoord getChunk() {
        return chunk;
    }

    public Location getBannerLocation() {
        return bannerLocation;
    }

    public String getSiegeId() {
        return siegeId;
    }

    public String getCampId() {
        return siegeId;
    }

    public String getAttackingTown() {
        return attackingTown;
    }

    public String getDefendingTown() {
        return defendingTown;
    }

    public String getAttackerNation() {
        return attackerNation;
    }

    public String getDefenderNation() {
        return defenderNation;
    }

    public boolean isNationWar() {
        return isNationWar;
    }

    public long getStartedAtMillis() {
        return startedAtMillis;
    }

    public long getBaseDurationSeconds() {
        return baseDurationSeconds;
    }

    public void setBaseDurationSeconds(long sec) {
        this.baseDurationSeconds = Math.max(30L, sec);
    }

    public boolean isHomeBlock() {
        return isHomeBlock;
    }

    public long getShieldBonusSeconds() {
        return shieldBonusSeconds;
    }

    /**
     * Динамическое обновление мощности щита во время захвата.
     * Если щит упал (integrity < 50%), бонус обнуляется.
     */
    public void updateShieldBonus(long newBonus, long standardBaseTime) {
        if (this.shieldBonusSeconds != newBonus) {
            this.shieldBonusSeconds = newBonus;
            this.baseDurationSeconds = Math.max(30L, standardBaseTime + newBonus);
        }
    }

    public double getProgress() {
        return progress;
    }

    public void setProgress(double progress) {
        this.progress = progress;
    }

    public int getCurrentAttackers() {
        return currentAttackers;
    }

    public int getCurrentDefenders() {
        return currentDefenders;
    }

    public boolean isCompleted() {
        return completed;
    }

    public boolean isRepelled() {
        return repelled;
    }

    /**
     * Расчет коэффициента перевеса сил.
     * @param forAttackers true если считаем перевес атакующих, false если перевес защитников
     */
    public double calculateAdvantageRatio(boolean forAttackers) {
        if (forAttackers) {
            if (currentAttackers <= 0) return 0.0;
            if (currentDefenders <= 0) {
                // Если защитников 0: базовая скорость 1.0x + бонус за каждого дополнительного атакующего (+0.35x)
                return 1.0 + (currentAttackers - 1) * 0.35;
            }
            if (currentAttackers > currentDefenders) {
                // Прямой коэффициент перевеса атакующих
                double ratio = (double) currentAttackers / (double) currentDefenders;
                return Math.min(5.0, ratio);
            }
            return 0.0;
        } else {
            // Перевес защитников
            if (currentDefenders <= 0) return 0.0;
            if (currentAttackers <= 0) {
                // Защитники без сопротивления откатывают захват
                return 1.0 + (currentDefenders - 1) * 0.35;
            }
            if (currentDefenders > currentAttackers) {
                double ratio = (double) currentDefenders / (double) currentAttackers;
                return Math.min(5.0, ratio);
            }
            return 0.0;
        }
    }

    /**
     * Ежесекундный пересчет прогресса захвата с учетом игроков на чанке.
     */
    public void tickSecond(int attackers, int defenders) {
        if (completed || repelled) return;

        this.currentAttackers = Math.max(0, attackers);
        this.currentDefenders = Math.max(0, defenders);

        if (currentAttackers > currentDefenders) {
            // Перевес атакующей стороны -> захват идет вперед
            double advantage = calculateAdvantageRatio(true);
            double delta = advantage / (double) baseDurationSeconds;
            this.progress += delta;

            if (this.progress >= 1.0) {
                this.progress = 1.0;
                this.completed = true;
            }
        } else if (currentDefenders > currentAttackers) {
            // Перевес защитников -> прогресс откатывается назад
            double advantageDef = calculateAdvantageRatio(false);
            double delta = advantageDef / (double) baseDurationSeconds;
            this.progress -= delta;

            // Если прогресс стал отрицательным -> чанк контр-захвачен защитниками!
            if (this.progress <= -0.05) {
                this.progress = -0.05;
                this.repelled = true;
            }
        }
        // Если поровну (currentAttackers == currentDefenders): застой, прогресс удерживается на месте
    }

    /**
     * Оставшееся время захвата при текущем темпе наступления атакующих (в секундах).
     */
    public long getEstimatedRemainingSeconds() {
        if (progress >= 1.0) return 0L;
        double adv = calculateAdvantageRatio(true);
        if (adv <= 0.0) return baseDurationSeconds;
        double remainingProgress = 1.0 - Math.max(0.0, progress);
        double ratePerSec = adv / (double) baseDurationSeconds;
        if (ratePerSec <= 0) return baseDurationSeconds;
        return (long) Math.ceil(remainingProgress / ratePerSec);
    }

    public String getFormattedProgress() {
        int percent = (int) Math.round(progress * 100);
        return percent + "%";
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SiegeBannerCapture that = (SiegeBannerCapture) o;
        return Objects.equals(captureId, that.captureId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(captureId);
    }
}
