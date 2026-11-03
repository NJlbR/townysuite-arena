import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """                activeBuildings.put(instId, bld);
            }
        }
    }"""

replacement = """                activeBuildings.put(instId, bld);
            }
        }
        
        // Автопроверка и синхронизация лимитов Чудес Света (на случай сбоев/лагов)
        for (BuildingBlueprint bp : blueprints.values()) {
            if (bp.isWorldWonder()) bp.setWonderCompletedByTown(null);
        }
        for (ActiveBuilding bld : activeBuildings.values()) {
            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            if (bp != null && bp.isWorldWonder() && bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
                bp.setWonderCompletedByTown(bld.getTownName());
            }
        }
        saveData(); // Сохраняем актуализированные лимиты
    }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched loadData successfully.")
else:
    print("Target content not found!")
