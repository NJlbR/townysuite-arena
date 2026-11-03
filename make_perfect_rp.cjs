const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const baseDir = 'tmp_rp';
fs.rmSync(baseDir, { recursive: true, force: true });
fs.mkdirSync(`${baseDir}/assets/minecraft/font`, { recursive: true });
fs.mkdirSync(`${baseDir}/assets/minecraft/models/item`, { recursive: true });
fs.mkdirSync(`${baseDir}/assets/townyarchitecture/models/item`, { recursive: true });
fs.mkdirSync(`${baseDir}/assets/townyarchitecture/textures/gui`, { recursive: true });
fs.mkdirSync(`${baseDir}/assets/townyarchitecture/textures/item`, { recursive: true });

// 1. Generate menu.png (256x256 RGBA)
// Canvas is 256x256. Vanilla 6-row container is 176x222 at (0, 0).
const canvas = createCanvas(256, 256);
const ctx = canvas.getContext('2d');
ctx.clearRect(0, 0, 256, 256);

// Helper for drawing 18x18 slot with sleek modern aesthetics
function drawSlot(x, y, isBtn, accentColor) {
  if (isBtn && accentColor) {
    // Dark slot base
    ctx.fillStyle = '#1c1c28';
    ctx.fillRect(x, y, 18, 18);
    // Subtle translucent accent tint
    ctx.fillStyle = accentColor;
    ctx.globalAlpha = 0.22;
    ctx.fillRect(x + 1, y + 1, 16, 16);
    ctx.globalAlpha = 1.0;
    // Crisp 1px accent border
    ctx.strokeStyle = accentColor;
    ctx.lineWidth = 1;
    ctx.strokeRect(x + 0.5, y + 0.5, 17, 17);
    return;
  }
  // Standard slot
  ctx.fillStyle = '#181822';
  ctx.fillRect(x, y, 18, 18);
  // Recessed inner borders
  ctx.fillStyle = '#0f0f15';
  ctx.fillRect(x, y, 18, 1);
  ctx.fillRect(x, y, 1, 18);
  ctx.fillStyle = '#2d2d3c';
  ctx.fillRect(x + 1, y + 17, 17, 1);
  ctx.fillRect(x + 17, y + 1, 1, 17);
}

// Container background 176x222 at (0, 0)
// Outer panel
ctx.fillStyle = '#181820';
ctx.fillRect(0, 0, 176, 222);

// Outer subtle 1px border
ctx.strokeStyle = '#383848';
ctx.lineWidth = 1;
ctx.strokeRect(0.5, 0.5, 175, 221);

// Header bar (y = 0..16)
ctx.fillStyle = '#121216';
ctx.fillRect(1, 1, 174, 15);
// Indigo accent line at y = 16
ctx.fillStyle = '#6366f1';
ctx.fillRect(0, 16, 176, 1);

// Row 0 Controls (y = 17): Beacon (col 2), Book (col 4), Pickaxe (col 6)
drawSlot(7 + 2 * 18, 17, true, '#8b5cf6'); // Purple (Town Info)
drawSlot(7 + 4 * 18, 17, true, '#3b82f6'); // Blue (Catalog)
drawSlot(7 + 6 * 18, 17, true, '#f59e0b'); // Amber (Skill)

// Rows 1 to 4: Blueprint Grid Slots (y = 35, 53, 71, 89)
for (let row = 1; row <= 4; row++) {
  for (let col = 1; col <= 7; col++) {
    drawSlot(7 + col * 18, 17 + row * 18);
  }
}

// Row 5 Controls (y = 107)
drawSlot(7 + 3 * 18, 107, true, '#ef4444'); // Red (Close)
drawSlot(7 + 4 * 18, 107, true, '#10b981'); // Emerald (Active)
drawSlot(7 + 5 * 18, 107, true, '#f59e0b'); // Amber (Stats)
drawSlot(7 + 6 * 18, 107, true, '#0ea5e9'); // Sky (Borders)
drawSlot(7 + 7 * 18, 107, true, '#d946ef'); // Fuchsia (Effects)

// Player inventory separator line at y = 126
ctx.fillStyle = '#262634';
ctx.fillRect(6, 126, 164, 1);

// Player inventory slots (3 rows at y = 138, 156, 174 matching vanilla item y = 139, 157, 175)
for (let row = 0; row < 3; row++) {
  for (let col = 0; col < 9; col++) {
    drawSlot(7 + col * 18, 138 + row * 18);
  }
}

// Hotbar slots (y = 196 matching vanilla item y = 197)
for (let col = 0; col < 9; col++) {
  drawSlot(7 + col * 18, 196);
}

fs.writeFileSync(`${baseDir}/assets/townyarchitecture/textures/gui/menu.png`, canvas.toBuffer('image/png'));

// 2. 1x1 transparent invisible.png
const invCanvas = createCanvas(1, 1);
fs.writeFileSync(`${baseDir}/assets/townyarchitecture/textures/item/invisible.png`, invCanvas.toBuffer('image/png'));

// 3. pack.mcmeta with full modern format compatibility
const mcmeta = {
  pack: {
    pack_format: 34,
    supported_formats: {
      min_inclusive: 15,
      max_inclusive: 48
    },
    description: "TownyArchitecture Modern GUI"
  }
};
fs.writeFileSync(`${baseDir}/pack.mcmeta`, JSON.stringify(mcmeta, null, 2));

// 4. font default.json
// ascent = 13 ensures y_screen = 6 + (7 - 13) = 0.0F, aligning the top of menu.png at y = 0
// advance of \uE000 = -8 shifts cursor to x = 0
// advance of \uE002 = -168 brings cursor from x = 176 back to standard title x = 8
const fontJson = {
  providers: [
    {
      type: "space",
      advances: {
        "\uE000": -8,
        "\uE002": -168
      }
    },
    {
      type: "bitmap",
      file: "townyarchitecture:gui/menu.png",
      ascent: 13,
      height: 256,
      chars: [
        "\uE001"
      ]
    }
  ]
};
fs.writeFileSync(`${baseDir}/assets/minecraft/font/default.json`, JSON.stringify(fontJson, null, 2));

// 5. paper.json and invisible.json models
const paperModel = {
  parent: "item/generated",
  textures: {
    layer0: "item/paper"
  },
  overrides: [
    { predicate: { custom_model_data: 1 }, model: "townyarchitecture:item/invisible" }
  ]
};
fs.writeFileSync(`${baseDir}/assets/minecraft/models/item/paper.json`, JSON.stringify(paperModel, null, 2));

const invModel = {
  parent: "item/generated",
  textures: {
    layer0: "townyarchitecture:item/invisible"
  }
};
fs.writeFileSync(`${baseDir}/assets/townyarchitecture/models/item/invisible.json`, JSON.stringify(invModel, null, 2));

console.log('Resource pack files written with ascent: 13.');
