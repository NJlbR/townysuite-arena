// Authentic Minecraft Pixel-Art Textures Generator (16x16 pixel patterns)
// Generates authentic Minecraft texture canvases for real in-game block appearance

export type BlockTextureType =
  | 'stone_bricks'
  | 'deepslate'
  | 'deepslate_bricks'
  | 'cobblestone'
  | 'andesite'
  | 'oak_planks'
  | 'spruce_planks'
  | 'dark_oak_planks'
  | 'oak_log'
  | 'spruce_log'
  | 'dark_oak_log'
  | 'sandstone'
  | 'smooth_sandstone'
  | 'red_sandstone'
  | 'quartz_block'
  | 'terracotta'
  | 'basalt'
  | 'obsidian'
  | 'bookshelf'
  | 'lapis_block'
  | 'amethyst_block'
  | 'prismarine'
  | 'prismarine_bricks'
  | 'dark_prismarine'
  | 'sea_lantern'
  | 'gold_block'
  | 'copper_block'
  | 'netherite_block'
  | 'glass'
  | 'white_concrete'
  | 'red_concrete'
  | 'beacon'
  | 'oak_leaves'
  | 'oak_door'
  | 'gray_concrete';

// Cached texture canvases in memory
const textureCanvases: Map<string, HTMLCanvasElement> = new Map();

function create16x16Canvas(): [HTMLCanvasElement, CanvasRenderingContext2D] {
  const canvas = document.createElement('canvas');
  canvas.width = 16;
  canvas.height = 16;
  const ctx = canvas.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  return [canvas, ctx];
}

// Generate Authentic Minecraft 16x16 Pixel Texture Canvas
export function getMinecraftTextureCanvas(type: BlockTextureType): HTMLCanvasElement {
  if (typeof document === 'undefined') {
    return null as any;
  }

  if (textureCanvases.has(type)) {
    return textureCanvases.get(type)!;
  }

  const [c, ctx] = create16x16Canvas();

  switch (type) {
    case 'stone_bricks': {
      // 4 stone brick rows with mortar lines
      ctx.fillStyle = '#7a7e85';
      ctx.fillRect(0, 0, 16, 16);
      
      // Brick borders (mortar)
      ctx.fillStyle = '#404347';
      ctx.fillRect(0, 7, 16, 1);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillRect(7, 0, 1, 7);
      ctx.fillRect(15, 0, 1, 7);
      ctx.fillRect(3, 8, 1, 7);
      ctx.fillRect(11, 8, 1, 7);

      // Highlights on top/left of each brick
      ctx.fillStyle = '#9aa0a8';
      ctx.fillRect(0, 0, 7, 1);
      ctx.fillRect(0, 0, 1, 7);
      ctx.fillRect(8, 0, 7, 1);
      ctx.fillRect(8, 0, 1, 7);
      ctx.fillRect(0, 8, 3, 1);
      ctx.fillRect(4, 8, 7, 1);
      ctx.fillRect(12, 8, 3, 1);

      // Noise speckles
      ctx.fillStyle = '#5c6066';
      [[2,2], [5,4], [10,2], [13,5], [2,11], [6,13], [14,10]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      ctx.fillStyle = '#8e949c';
      [[3,3], [11,3], [5,10], [13,12]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'deepslate':
    case 'deepslate_bricks': {
      // Dark slate layered strata
      ctx.fillStyle = '#2f343b';
      ctx.fillRect(0, 0, 16, 16);
      // Slate striations
      ctx.fillStyle = '#20242a';
      ctx.fillRect(0, 3, 16, 2);
      ctx.fillRect(0, 9, 16, 2);
      ctx.fillRect(0, 14, 16, 2);
      ctx.fillStyle = '#3d444d';
      ctx.fillRect(0, 1, 16, 1);
      ctx.fillRect(0, 7, 16, 1);
      ctx.fillRect(0, 12, 16, 1);
      // Noise
      ctx.fillStyle = '#1c1f24';
      [[2,5],[6,11],[12,4],[14,13],[8,8]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      ctx.fillStyle = '#49525c';
      [[3,2],[9,7],[13,1],[4,12]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'cobblestone': {
      ctx.fillStyle = '#6b6f75';
      ctx.fillRect(0, 0, 16, 16);
      // Cobble stones irregular outlines
      ctx.fillStyle = '#3a3d42';
      [[0,4,7,1],[6,0,1,5],[7,8,9,1],[10,0,1,8],[0,12,8,1],[8,8,1,8]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      // Highlights
      ctx.fillStyle = '#8f959e';
      [[1,1,3,2],[8,1,4,3],[2,6,4,3],[9,9,5,3],[1,13,4,2]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      // Dark cracks
      ctx.fillStyle = '#2c2f33';
      [[4,2],[11,4],[3,9],[12,12],[6,14]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'andesite': {
      ctx.fillStyle = '#848688';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#5d6063';
      [[1,2],[4,5],[8,3],[13,1],[2,9],[7,11],[11,8],[14,14],[3,14],[9,15]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      ctx.fillStyle = '#a1a4a8';
      [[3,1],[7,4],[12,2],[1,8],[6,10],[10,7],[13,12],[4,13]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      ctx.fillStyle = '#444648';
      [[2,3],[9,4],[14,2],[8,12],[12,9]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'spruce_planks': {
      // Rich brown wooden planks with horizontal seams
      ctx.fillStyle = '#4c3319';
      ctx.fillRect(0, 0, 16, 16);
      // Plank dividers
      ctx.fillStyle = '#2d1e0f';
      ctx.fillRect(0, 3, 16, 1);
      ctx.fillRect(0, 7, 16, 1);
      ctx.fillRect(0, 11, 16, 1);
      ctx.fillRect(0, 15, 16, 1);
      // Wood grain lines
      ctx.fillStyle = '#5d3f20';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 4, 16, 1);
      ctx.fillRect(0, 8, 16, 1);
      ctx.fillRect(0, 12, 16, 1);
      ctx.fillStyle = '#3a2713';
      [[4,1],[11,2],[7,5],[2,9],[13,10],[8,13]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      // Nails
      ctx.fillStyle = '#1e140a';
      [[1,1],[14,1],[1,5],[14,5],[1,9],[14,9],[1,13],[14,13]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'dark_oak_planks': {
      ctx.fillStyle = '#301c0c';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#1c1007';
      ctx.fillRect(0, 3, 16, 1);
      ctx.fillRect(0, 7, 16, 1);
      ctx.fillRect(0, 11, 16, 1);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#3f2512';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 4, 16, 1);
      ctx.fillRect(0, 8, 16, 1);
      ctx.fillRect(0, 12, 16, 1);
      break;
    }

    case 'oak_planks': {
      ctx.fillStyle = '#9e7e48';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#654f2a';
      ctx.fillRect(0, 3, 16, 1);
      ctx.fillRect(0, 7, 16, 1);
      ctx.fillRect(0, 11, 16, 1);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#b79357';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 4, 16, 1);
      ctx.fillRect(0, 8, 16, 1);
      ctx.fillRect(0, 12, 16, 1);
      ctx.fillStyle = '#4f3d1e';
      [[1,1],[14,1],[1,5],[14,5],[1,9],[14,9],[1,13],[14,13]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'oak_log':
    case 'spruce_log':
    case 'dark_oak_log': {
      // Bark texture with vertical ridges
      const base = type === 'dark_oak_log' ? '#2c1a0c' : type === 'spruce_log' ? '#3b2716' : '#5c4528';
      const dark = type === 'dark_oak_log' ? '#180e06' : type === 'spruce_log' ? '#22150a' : '#382a17';
      const light = type === 'dark_oak_log' ? '#3d2512' : type === 'spruce_log' ? '#4d341e' : '#725734';
      ctx.fillStyle = base;
      ctx.fillRect(0, 0, 16, 16);
      // Vertical bark stripes
      ctx.fillStyle = dark;
      ctx.fillRect(1, 0, 1, 16);
      ctx.fillRect(5, 0, 2, 16);
      ctx.fillRect(9, 0, 1, 16);
      ctx.fillRect(13, 0, 2, 16);
      ctx.fillStyle = light;
      ctx.fillRect(3, 0, 2, 16);
      ctx.fillRect(7, 0, 2, 16);
      ctx.fillRect(11, 0, 2, 16);
      ctx.fillRect(15, 0, 1, 16);
      break;
    }

    case 'sandstone':
    case 'smooth_sandstone': {
      ctx.fillStyle = '#d8cb9a';
      ctx.fillRect(0, 0, 16, 16);
      // Sand grain strata
      ctx.fillStyle = '#bfae79';
      ctx.fillRect(0, 4, 16, 1);
      ctx.fillRect(0, 9, 16, 1);
      ctx.fillRect(0, 14, 16, 1);
      ctx.fillStyle = '#e5dab1';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 5, 16, 1);
      ctx.fillRect(0, 10, 16, 1);
      ctx.fillStyle = '#9e8f60';
      [[3,2],[11,6],[5,11],[13,13]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      break;
    }

    case 'red_sandstone': {
      ctx.fillStyle = '#aa4c17';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#87350c';
      ctx.fillRect(0, 4, 16, 1);
      ctx.fillRect(0, 9, 16, 1);
      ctx.fillRect(0, 14, 16, 1);
      ctx.fillStyle = '#c76228';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 5, 16, 1);
      ctx.fillRect(0, 10, 16, 1);
      break;
    }

    case 'quartz_block': {
      ctx.fillStyle = '#ece9df';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#d5cfbf';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#f7f6f1';
      [[2,2],[7,5],[11,3],[4,10],[12,11]].forEach(([x,y]) => ctx.fillRect(x,y,2,2));
      break;
    }

    case 'terracotta': {
      ctx.fillStyle = '#985e43';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#834c34';
      [[1,3],[7,1],[12,4],[3,8],[10,7],[2,13],[11,12]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      ctx.fillStyle = '#aa6f52';
      [[4,2],[9,3],[14,6],[1,9],[8,11],[5,14],[13,14]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      break;
    }

    case 'basalt': {
      ctx.fillStyle = '#4c4c51';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#2f2f34';
      ctx.fillRect(2, 0, 2, 16);
      ctx.fillRect(7, 0, 2, 16);
      ctx.fillRect(12, 0, 2, 16);
      ctx.fillStyle = '#636369';
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(5, 0, 1, 16);
      ctx.fillRect(10, 0, 1, 16);
      break;
    }

    case 'obsidian': {
      ctx.fillStyle = '#100c1e';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#1e1438';
      [[1,2],[7,3],[11,1],[3,8],[12,7],[2,12],[10,13]].forEach(([x,y]) => ctx.fillRect(x,y,3,2));
      ctx.fillStyle = '#3b1d60';
      [[2,3],[8,4],[4,9],[11,14]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      ctx.fillStyle = '#5c2d8e';
      [[3,3],[9,4]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'bookshelf': {
      // Wood frame + Books
      ctx.fillStyle = '#9e7e48';
      ctx.fillRect(0, 0, 16, 16);
      // Shelves
      ctx.fillStyle = '#4f3d1e';
      ctx.fillRect(1, 1, 14, 6);
      ctx.fillRect(1, 9, 14, 6);
      // Books in top shelf
      const colors = ['#b91c1c', '#1d4ed8', '#047857', '#b45309', '#6b21a8'];
      let bx = 2;
      for (let i = 0; i < 4; i++) {
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(bx, 2, 2, 5);
        ctx.fillStyle = '#fef08a';
        ctx.fillRect(bx, 3, 2, 1);
        bx += 3;
      }
      // Books in bottom shelf
      bx = 2;
      for (let i = 0; i < 4; i++) {
        ctx.fillStyle = colors[(i + 2) % colors.length];
        ctx.fillRect(bx, 10, 2, 5);
        ctx.fillStyle = '#fef08a';
        ctx.fillRect(bx, 12, 2, 1);
        bx += 3;
      }
      break;
    }

    case 'lapis_block': {
      ctx.fillStyle = '#183a8f';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#102766';
      [[0,0,16,1],[0,0,1,16],[15,0,1,16],[0,15,16,1]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      ctx.fillStyle = '#2654be';
      [[2,2],[6,5],[10,3],[3,9],[11,8],[6,12]].forEach(([x,y]) => ctx.fillRect(x,y,3,2));
      ctx.fillStyle = '#f59e0b'; // Gold specks in lapis lazuli
      [[4,3],[12,4],[3,11],[9,13]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'amethyst_block': {
      ctx.fillStyle = '#834aa8';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#5d2b7d';
      [[0,0,16,1],[0,0,1,16],[15,0,1,16],[0,15,16,1]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      ctx.fillStyle = '#ab6cd6';
      [[2,2,4,4],[8,2,3,3],[3,8,3,4],[9,8,5,5]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      ctx.fillStyle = '#d8b4fe';
      [[3,3],[9,3],[4,9],[11,9]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'prismarine':
    case 'prismarine_bricks': {
      ctx.fillStyle = '#52968a';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#336159';
      ctx.fillRect(0, 7, 16, 1);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillRect(7, 0, 1, 8);
      ctx.fillRect(15, 0, 1, 8);
      ctx.fillRect(3, 8, 1, 8);
      ctx.fillRect(11, 8, 1, 8);
      ctx.fillStyle = '#73bba7';
      [[1,1],[9,2],[4,9],[12,10]].forEach(([x,y]) => ctx.fillRect(x,y,3,2));
      break;
    }

    case 'dark_prismarine': {
      ctx.fillStyle = '#2b4d45';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#172b26';
      // Grid squares
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 5, 16, 1);
      ctx.fillRect(0, 10, 16, 1);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(5, 0, 1, 16);
      ctx.fillRect(10, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillStyle = '#3a665c';
      [[2,2],[7,2],[12,2],[2,7],[7,7],[12,7],[2,12],[7,12],[12,12]].forEach(([x,y]) => ctx.fillRect(x,y,2,2));
      break;
    }

    case 'sea_lantern': {
      ctx.fillStyle = '#aaf1e3';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#e8fffa';
      ctx.fillRect(3, 3, 10, 10);
      ctx.fillStyle = '#5fbfae';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(6, 6, 4, 4);
      break;
    }

    case 'gold_block': {
      ctx.fillStyle = '#f5c328';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#ba8b12';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#fde68a';
      [[2,2,4,4],[8,2,5,3],[3,8,4,5],[9,8,4,4]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      ctx.fillStyle = '#ffffff';
      [[3,3],[9,3]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'copper_block': {
      ctx.fillStyle = '#c06b4f';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#8a432e';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#df896d';
      [[2,2,4,4],[8,2,5,3],[3,8,4,5],[9,8,4,4]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      break;
    }

    case 'netherite_block': {
      ctx.fillStyle = '#3b3437';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#241f21';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      ctx.fillStyle = '#4f464a';
      [[2,2,4,4],[8,2,5,3],[3,8,4,5],[9,8,4,4]].forEach(([x,y,w,h]) => ctx.fillRect(x,y,w,h));
      break;
    }

    case 'glass': {
      ctx.fillStyle = '#a5d8f0';
      ctx.fillRect(0, 0, 16, 16);
      // Border frame
      ctx.fillStyle = '#4fa3d1';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      // Minecraft glass diagonal glint highlights
      ctx.fillStyle = '#ffffff';
      [[2,2],[3,3],[4,4],[12,10],[13,11],[14,12]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'white_concrete': {
      ctx.fillStyle = '#e4e7e8';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#d0d5d7';
      [[2,3],[8,6],[12,2],[4,11],[13,13]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      break;
    }

    case 'red_concrete': {
      ctx.fillStyle = '#9e2b27';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#821e1a';
      [[2,3],[8,6],[12,2],[4,11],[13,13]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      break;
    }

    case 'oak_leaves': {
      // Lush green foliage pixel pattern with slight transparent spots and leaf textures
      ctx.fillStyle = '#225916';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#3a8326';
      [[1,1],[5,2],[9,1],[13,3],[3,6],[7,5],[11,7],[2,10],[8,11],[13,10],[4,14],[10,14]].forEach(([x,y]) => ctx.fillRect(x,y,2,2));
      ctx.fillStyle = '#54a338';
      [[2,2],[10,2],[7,6],[14,4],[3,11],[9,12]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      ctx.fillStyle = '#14380b';
      [[0,4],[4,0],[8,8],[12,0],[15,5],[0,12],[6,13],[12,15]].forEach(([x,y]) => ctx.fillRect(x,y,1,1));
      break;
    }

    case 'oak_door': {
      // Oak door with dark handle and inset panels
      ctx.fillStyle = '#9e7e48';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#654f2a';
      // Inset window / top panel
      ctx.fillRect(2, 2, 5, 5);
      ctx.fillRect(9, 2, 5, 5);
      // Bottom panels
      ctx.fillRect(2, 9, 5, 5);
      ctx.fillRect(9, 9, 5, 5);
      // Highlights
      ctx.fillStyle = '#b79357';
      ctx.fillRect(2, 2, 5, 1);
      ctx.fillRect(9, 2, 5, 1);
      ctx.fillRect(2, 9, 5, 1);
      ctx.fillRect(9, 9, 5, 1);
      // Iron handle
      ctx.fillStyle = '#1f2937';
      ctx.fillRect(13, 7, 2, 3);
      ctx.fillStyle = '#94a3b8';
      ctx.fillRect(13, 7, 1, 1);
      break;
    }

    case 'gray_concrete': {
      ctx.fillStyle = '#54595d';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#464a4e';
      [[2,3],[8,6],[12,2],[4,11],[13,13]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      ctx.fillStyle = '#63686d';
      [[1,8],[6,2],[11,9],[3,14]].forEach(([x,y]) => ctx.fillRect(x,y,2,1));
      break;
    }

    case 'beacon': {
      // Beacon diamond / glass core with sky cyan glow
      ctx.fillStyle = '#38bdf8';
      ctx.fillRect(0, 0, 16, 16);
      ctx.fillStyle = '#bae6fd';
      ctx.fillRect(2, 2, 12, 12);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(5, 5, 6, 6);
      ctx.fillStyle = '#0284c7';
      ctx.fillRect(0, 0, 16, 1);
      ctx.fillRect(0, 0, 1, 16);
      ctx.fillRect(15, 0, 1, 16);
      ctx.fillRect(0, 15, 16, 1);
      break;
    }
  }

  textureCanvases.set(type, c);
  return c;
}

// Map material names from buildingVariantsData.ts to authentic Minecraft block texture types
export function getTextureTypeForMaterial(materialName: string, elementName: string): BlockTextureType {
  const m = (materialName + ' ' + elementName).toLowerCase();

  if (m.includes('лист') || m.includes('растительн') || m.includes('эко') || m.includes('leaves')) return 'oak_leaves';
  if (m.includes('двер') || m.includes('door') || m.includes('проем')) return 'oak_door';
  if (m.includes('серый бетон') || m.includes('gray_concrete')) return 'gray_concrete';
  if (m.includes('маяк') || m.includes('фонар') || m.includes('beacon')) {
    if (m.includes('морск')) return 'sea_lantern';
    return 'beacon';
  }
  if (m.includes('стекл') || m.includes('витраж') || m.includes('бойниц')) return 'glass';
  if (m.includes('красный крест') || m.includes('red_concrete')) return 'red_concrete';
  if (m.includes('белый бетон') || m.includes('штукатурк')) return 'white_concrete';
  if (m.includes('кварц')) return 'quartz_block';
  if (m.includes('терракот') || m.includes('черепиц')) return 'terracotta';
  if (m.includes('красный песчаник')) return 'red_sandstone';
  if (m.includes('песчаник') || m.includes('алтар')) return 'sandstone';
  if (m.includes('глубинный сланец') || m.includes('сланец') || m.includes('стилобат') || m.includes('цоколь')) {
    if (m.includes('кирпич')) return 'deepslate_bricks';
    return 'deepslate';
  }
  if (m.includes('булыжник')) return 'cobblestone';
  if (m.includes('андезит')) return 'andesite';
  if (m.includes('базальт')) return 'basalt';
  if (m.includes('обсидиан')) return 'obsidian';
  if (m.includes('книжн')) return 'bookshelf';
  if (m.includes('лазурит')) return 'lapis_block';
  if (m.includes('аметист')) return 'amethyst_block';
  if (m.includes('темный призмарин')) return 'dark_prismarine';
  if (m.includes('призмарин')) return 'prismarine';
  if (m.includes('золот') || m.includes('колокол')) return 'gold_block';
  if (m.includes('медн') || m.includes('купол')) return 'copper_block';
  if (m.includes('незерит') || m.includes('шпиль')) return 'netherite_block';
  if (m.includes('темный дуб') || m.includes('бревн') || m.includes('пилястр')) {
    if (m.includes('бревн') || m.includes('пилястр') || m.includes('каркас')) return 'dark_oak_log';
    return 'dark_oak_planks';
  }
  if (m.includes('ел')) {
    if (m.includes('бревн')) return 'spruce_log';
    return 'spruce_planks';
  }
  if (m.includes('дуб') || m.includes('дерев') || m.includes('навес') || m.includes('гонт')) return 'oak_planks';
  
  // Default fortified stone bricks
  return 'stone_bricks';
}
