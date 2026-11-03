package com.towny.architecture.util;

import com.towny.architecture.model.ActiveBuilding;
import org.bukkit.Material;

import java.util.HashMap;
import java.util.Map;

public class RussianTranslator {
    private static final Map<Material, String> MATERIAL_NAMES = new HashMap<>();
    private static final Map<Material, String> SHORT_NAMES = new HashMap<>();

    static {
        register(Material.STONE_BRICKS, "Каменный кирпич", "Кам. кирпич");
        register(Material.WHITE_CONCRETE, "Белый бетон", "Бел. бетон");
        register(Material.RED_WOOL, "Красная шерсть", "Кр. шерсть");
        register(Material.GLASS, "Стекло", "Стекло");
        register(Material.COBBLESTONE, "Булыжник", "Булыжник");
        register(Material.OAK_PLANKS, "Дубовые доски", "Дуб. доски");
        register(Material.IRON_BLOCK, "Железный блок", "Жел. блок");
        register(Material.BOOKSHELF, "Книжная полка", "Книжн. полка");
        register(Material.OBSIDIAN, "Обсидиан", "Обсидиан");
        register(Material.DARK_OAK_PLANKS, "Доски темного дуба", "Темн. доски");
        register(Material.LAPIS_BLOCK, "Лазуритовый блок", "Лазурит");
        register(Material.LADDER, "Лестница", "Лестница");
        register(Material.LANTERN, "Фонарь", "Фонарь");
        register(Material.SANDSTONE, "Песчаник", "Песчаник");
        register(Material.SMOOTH_SANDSTONE, "Гладкий песчаник", "Глад. песчаник");
        register(Material.GOLD_BLOCK, "Золотой блок", "Зол. блок");
        register(Material.BEACON, "Маяк", "Маяк");
        register(Material.NETHERITE_INGOT, "Незеритовый слиток", "Незерит");
        register(Material.NETHERITE_BLOCK, "Незеритовый блок", "Незер. блок");
        register(Material.DIAMOND_BLOCK, "Алмазный блок", "Алмаз. блок");
        register(Material.EMERALD_BLOCK, "Изумрудный блок", "Изумр. блок");
        register(Material.BRICKS, "Кирпичи", "Кирпич");
        register(Material.SEA_LANTERN, "Морской фонарь", "Мор. фонарь");
        register(Material.GLOWSTONE, "Светокамень", "Светокамень");
        register(Material.QUARTZ_BLOCK, "Кварцевый блок", "Кварц");
        register(Material.PRISMARINE, "Призмарин", "Призмарин");
        register(Material.COPPER_BLOCK, "Медный блок", "Медн. блок");
        register(Material.IRON_SWORD, "Железный меч", "Жел. меч");
        register(Material.ENCHANTING_TABLE, "Стол зачарования", "Стол зач.");
        register(Material.GOLDEN_APPLE, "Золотое яблоко", "Зол. яблоко");
    }

    private static void register(Material mat, String full, String shortName) {
        MATERIAL_NAMES.put(mat, full);
        SHORT_NAMES.put(mat, shortName);
    }

    public static String getMaterialRu(Material mat) {
        if (mat == null) return "Неизвестный блок";
        String name = MATERIAL_NAMES.get(mat);
        if (name != null) return name;

        // Fallback: prettier formatting of enum name
        String raw = mat.name().toLowerCase().replace('_', ' ');
        return Character.toUpperCase(raw.charAt(0)) + raw.substring(1);
    }

    public static String getShortMaterialRu(Material mat) {
        if (mat == null) return "?";
        String name = SHORT_NAMES.get(mat);
        if (name != null) return name;
        return getMaterialRu(mat);
    }

    public static String getStatusRu(ActiveBuilding.Status status) {
        if (status == null) return "Неизвестно";
        switch (status) {
            case CONSTRUCTING:
                return "В процессе постройки";
            case ACTIVE:
                return "Действует (Активно)";
            case DAMAGED:
                return "Повреждено (Требует ремонта)";
            case ENTOMBED:
                return "Фасад заблокирован (<50% открытости, баффы отключены)";
            default:
                return status.name();
        }
    }

    public static String formatBuffRu(String key, Object val) {
        if (key == null || val == null) return "";
        switch (key) {
            case "health-boost-hearts":
                return "+" + val + " Дополнительное Сердце (HP)";
            case "regeneration-level":
                return "Регенерация " + toRoman((int) val);
            case "strength-level":
                return "Сила " + toRoman((int) val);
            case "speed-level":
                return "Скорость " + toRoman((int) val);
            case "fast-digging-level":
                return "Спешка (Ускоренная добыча) " + toRoman((int) val);
            case "damage-resistance-level":
                return "Сопротивление урону " + toRoman((int) val);
            default:
                return key + ": " + val;
        }
    }

    public static String toRoman(int num) {
        switch (num) {
            case 1: return "I";
            case 2: return "II";
            case 3: return "III";
            case 4: return "IV";
            case 5: return "V";
            default: return String.valueOf(num);
        }
    }
}
