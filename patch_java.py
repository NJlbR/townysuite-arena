import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    code = f.read()

replacements = [
    ('town-info', 'townIndicator', 'Material.BEACON'),
    ('catalog-header', 'catalogHeader', 'Material.KNOWLEDGE_BOOK'),
    ('skill-badge', 'skillBadge', 'Material.GOLDEN_PICKAXE'),
    ('active-buildings', 'activeStatus', 'Material.NETHER_STAR'),
    ('close-button', 'closeBtn', 'Material.BARRIER'),
    ('stats-button', 'statsBtn', 'Material.EXPERIENCE_BOTTLE'),
    ('border-particles', 'particleBtn', 'Material.GLOWSTONE_DUST'),
    ('effect-particles', 'effectParticleBtn', 'Material.REDSTONE_TORCH')
]

for cfg_key, var_name, default_mat in replacements:
    old_line = f'ItemStack {var_name} = new ItemStack({default_mat});'
    new_line = f'''
        Material {var_name}Mat = Material.matchMaterial(plugin.getConfig().getString("gui.items.{cfg_key}.material", "{default_mat.replace("Material.", "")}"));
        if ({var_name}Mat == null) {var_name}Mat = {default_mat};
        ItemStack {var_name} = new ItemStack({var_name}Mat);
    '''
    code = code.replace(old_line, new_line.strip())

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Java patched")
