with open('tmp/minecraft-build-v2/src/main/resources/buildings.yml', 'r', encoding='utf-8') as f:
    c = f.read()

new_buildings = '''  town_hall:
    name: "Town Hall"
    name-ru: "Мэрия"
    description: "Сердце города (2x2). Центр дипломатии и обороны. Обладает Щитом Мэрии, прочность которого усиливается за каждую построенную в городе стену! В военное время урон сначала поглощается щитом."
    icon: "BELL"
    required-skill-level: 25
    is-world-wonder: false
    chunk-footprint:
      width-chunks: 2
      length-chunks: 2
    dimensions:
      height-y: 8
    resources:
      STONE_BRICKS: 480
      DEEPSLATE_BRICKS: 288
      DARK_OAK_PLANKS: 360
      GOLD_BLOCK: 8
      BELL: 1
      LANTERN: 16
      GLASS: 48
      IRON_BARS: 32
    buffs:
      hero-of-the-village: 1
    particle-color: "#FFD700"

  city_wall:
    name: "Fortified City Wall"
    name-ru: "Городская Стена"
    description: "Фортификационный вал (2x1). Модульная стена с угловыми стыковочными башнями и зубцами. Каждая построенная стена дает +100 ед. к Щиту Мэрии вашего города в военное время! Стены стыкуются в единую цепь."
    icon: "BRICKS"
    required-skill-level: 10
    is-world-wonder: false
    chunk-footprint:
      width-chunks: 2
      length-chunks: 1
    dimensions:
      height-y: 6
    resources:
      STONE_BRICKS: 360
      COBBLESTONE: 240
      CRACKED_STONE_BRICKS: 64
      IRON_BARS: 16
      LANTERN: 4
    buffs: {}
    particle-color: "#808080"
'''

if 'town_hall:' not in c:
    with open('tmp/minecraft-build-v2/src/main/resources/buildings.yml', 'w', encoding='utf-8') as f:
        f.write(c.strip() + '\n' + new_buildings)
    print("Appended town_hall and city_wall to buildings.yml!")
else:
    print("town_hall already present!")
