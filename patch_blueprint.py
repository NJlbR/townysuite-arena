import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/model/BuildingBlueprint.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    private final Map<String, Object> buffs;
    private String wonderCompletedByTown;"""

replacement = """    private final Map<String, Object> buffs;
    private final String particleColorHex;
    private String wonderCompletedByTown;"""

target2 = """            Map<Material, Integer> resources,
            Map<String, Object> buffs) {"""

replacement2 = """            Map<Material, Integer> resources,
            Map<String, Object> buffs,
            String particleColorHex) {"""

target3 = """        this.buffs = buffs != null ? buffs : Collections.emptyMap();
        this.wonderCompletedByTown = null;
    }"""

replacement3 = """        this.buffs = buffs != null ? buffs : Collections.emptyMap();
        this.particleColorHex = particleColorHex;
        this.wonderCompletedByTown = null;
    }
    
    public String getParticleColorHex() { return particleColorHex; }"""

if target in content and target2 in content and target3 in content:
    content = content.replace(target, replacement).replace(target2, replacement2).replace(target3, replacement3)
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/model/BuildingBlueprint.java', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched BuildingBlueprint.java successfully.")
else:
    print("Target content not found!")
