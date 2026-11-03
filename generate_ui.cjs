const { createCanvas } = require('canvas');
const fs = require('fs');

const canvas = createCanvas(256, 256);
const ctx = canvas.getContext('2d');

// Clear
ctx.clearRect(0, 0, 256, 256);

// Helper for rounded rectangle
function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
  if (fill) {
    ctx.fillStyle = fill;
    ctx.fill();
  }
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.stroke();
  }
}

// Draw slot outline
function drawSlot(x, y, isEmpty = false) {
  // Base
  ctx.fillStyle = isEmpty ? '#00000000' : '#1e1e24'; // slightly lighter than bg
  ctx.fillRect(x, y, 18, 18);
  // Border
  ctx.strokeStyle = '#32323d';
  ctx.lineWidth = 1;
  ctx.strokeRect(x + 0.5, y + 0.5, 17, 17);
  // Highlight top/left
  ctx.fillStyle = '#2c2c35';
  ctx.fillRect(x + 1, y + 1, 16, 1);
  ctx.fillRect(x + 1, y + 1, 1, 16);
  // Shadow bottom/right
  ctx.fillStyle = '#111115';
  ctx.fillRect(x + 1, y + 17, 16, 1);
  ctx.fillRect(x + 17, y + 1, 1, 17);
}

// Draw button outline
function drawButton(x, y, width, height, colorMain, colorLight, colorDark) {
  ctx.fillStyle = colorMain;
  ctx.fillRect(x, y, width, height);
  ctx.fillStyle = colorLight;
  ctx.fillRect(x, y, width, 1);
  ctx.fillRect(x, y, 1, height);
  ctx.fillStyle = colorDark;
  ctx.fillRect(x, y + height - 1, width, 1);
  ctx.fillRect(x + width - 1, y, 1, height);
}

// Minecraft chest UI texture height is roughly 222
// Width is 176

// Main background
roundRect(ctx, 0, 0, 176, 222, 6, '#141419', '#6366f1');

// Header
ctx.beginPath();
ctx.moveTo(6, 0);
ctx.lineTo(170, 0);
ctx.quadraticCurveTo(176, 0, 176, 6);
ctx.lineTo(176, 15);
ctx.lineTo(0, 15);
ctx.lineTo(0, 6);
ctx.quadraticCurveTo(0, 0, 6, 0);
ctx.closePath();
ctx.fillStyle = '#1e1e24';
ctx.fill();

// Accent line
ctx.fillStyle = '#6366f1'; // Indigo accent
ctx.fillRect(0, 15, 176, 1);

// Draw Blueprint area slots: 10,11,12,13,14,15,16 (row 1, col 1-7) etc
for (let row = 1; row <= 3; row++) {
  for (let col = 1; col <= 7; col++) {
    drawSlot(7 + col * 18, 17 + row * 18);
  }
}

// We need to shift everything down slightly to align with vanilla slots?
// Wait, vanilla 54-slot chest:
// Slots start at X=7, Y=17 (row 0)
// Slots row 1: Y=35 (17 + 18)
// Slots row 5: Y=107 (17 + 90)

// Let's re-verify the coordinates.
// Vanilla slots:
// Row 0: Y = 17
// Row 1: Y = 35
// Row 2: Y = 53
// Row 3: Y = 71
// Row 4: Y = 89
// Row 5: Y = 107
// Player inventory: Y = 139 (3 rows)
// Player hotbar: Y = 197

// Top row controls:
// slot 2: town info
drawButton(7 + 2 * 18, 17, 18, 18, '#8b5cf6', '#a78bfa', '#6d28d9');
// slot 4: catalog header
drawButton(7 + 4 * 18, 17, 18, 18, '#3b82f6', '#60a5fa', '#1d4ed8');
// slot 6: skill badge
drawButton(7 + 6 * 18, 17, 18, 18, '#f59e0b', '#fbbf24', '#b45309');

// Bottom row controls (Row 5 -> Y = 107):
// slot 48: close
drawButton(7 + 3 * 18, 107, 18, 18, '#ef4444', '#f87171', '#b91c1c');
// slot 49: active
drawButton(7 + 4 * 18, 107, 18, 18, '#10b981', '#34d399', '#047857');
// slot 50: stats
drawButton(7 + 5 * 18, 107, 18, 18, '#f59e0b', '#fbbf24', '#b45309');
// slot 51: border
drawButton(7 + 6 * 18, 107, 18, 18, '#0ea5e9', '#38bdf8', '#0369a1');
// slot 52: effect
drawButton(7 + 7 * 18, 107, 18, 18, '#d946ef', '#e879f9', '#a21caf');

// Player Inventory Grid (Rows 0-2 of player inv)
for (let row = 0; row < 3; row++) {
  for (let col = 0; col < 9; col++) {
    drawSlot(7 + col * 18, 139 + row * 18);
  }
}
// Hotbar Grid
for (let col = 0; col < 9; col++) {
  drawSlot(7 + col * 18, 197);
}

fs.writeFileSync('menu.png', canvas.toBuffer('image/png'));
console.log('menu.png generated.');

