with open('tmp/minecraft-build/src/main/resources/config.yml', 'r', encoding='utf-8') as f:
    cfg = f.read()

gui_config = """
# Настройки меню (/builds) для поддержки ресурспаков
gui:
  title: "&f\\uE000\\uE001\\uE002&8Чертежи и постройки" # Заголовок инвентаря. Используйте символ ресурспака или обычный текст
  size: 54
  fill-empty-slots: false # Установите false, чтобы не заполнять пустоты стеклом (для кастомных текстур)
  
  # Настройка расположения и внешнего вида кнопок
  items:
    town-info:
      slot: 2
      material: PAPER
      custom-model-data: 1
    catalog-header:
      slot: 4
      material: PAPER
      custom-model-data: 1
    skill-badge:
      slot: 6
      material: PAPER
      custom-model-data: 1
    active-buildings:
      slot: 49
      material: PAPER
      custom-model-data: 1
    close-button:
      slot: 48
      material: PAPER
      custom-model-data: 1
    stats-button:
      slot: 50
      material: PAPER
      custom-model-data: 1
    border-particles:
      slot: 51
      material: PAPER
      custom-model-data: 1
    effect-particles:
      slot: 52
      material: PAPER
      custom-model-data: 1

  # Слоты, в которых будут выводиться чертежи зданий (из buildings.yml)
  blueprint-slots: [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34]
"""

parts = cfg.split('# Настройки меню (/builds) для поддержки ресурспаков')
new_cfg = parts[0] + gui_config

with open('tmp/minecraft-build/src/main/resources/config.yml', 'w', encoding='utf-8') as f:
    f.write(new_cfg)

print("Config patched")
