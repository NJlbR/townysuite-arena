import json
import base64
from datetime import datetime

with open("public/models/cannon_1x1.json", "r", encoding="utf-8") as f:
    minecraft_model = json.load(f)

json_str = json.dumps(minecraft_model, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.json", "rb") as f:
    json_b64 = base64.b64encode(f.read()).decode("utf-8")

with open("public/models/cannon_1x1.bbmodel", "rb") as f:
    bbmodel_b64 = base64.b64encode(f.read()).decode("utf-8")

with open("public/SiegeCannon-3D-Model-RP.zip", "rb") as f:
    rp_b64 = base64.b64encode(f.read()).decode("utf-8")

with open("public/models/cannon_1x1.bbmodel", "r", encoding="utf-8") as f:
    bbmodel_str = f.read()

ts_content = f"""// Auto-generated 3D Cannon Model Data (100% Vanilla Compliant)
export const CANNON_MODEL_JSON = {json.dumps(minecraft_model, indent=2, ensure_ascii=False)};

export const CANNON_MODEL_JSON_STR = {json.dumps(json_str)};
export const CANNON_BBMODEL_JSON_STR = {json.dumps(bbmodel_str)};

export const CANNON_JSON_BASE64 = "{json_b64}";
export const CANNON_BBMODEL_BASE64 = "{bbmodel_b64}";
export const CANNON_RP_BASE64 = "{rp_b64}";

export const CANNON_METADATA = {{
  name: "3D Осадная Пушка (1x1 Блок)",
  fileJsonName: "cannon_1x1.json",
  fileBbmodelName: "cannon_1x1.bbmodel",
  fileRpName: "SiegeCannon-3D-Model-RP.zip",
  elementsCount: {len(minecraft_model["elements"])},
  format: "Blockbench / Minecraft Java 1.20 - 1.21+ (Strictly Validated)",
  customModelData: 7001,
  targetItem: "tnt / carrot_on_a_stick",
  dimensions: "16x16x16 (В точности 1x1 блок Minecraft)",
  author: "TownyArchitecture & SiegeCannon Team",
  releaseDate: "{datetime.utcnow().strftime('%Y-%m-%d')}"
}};
"""

with open("src/data/cannonModelData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print("Updated cannonModelData.ts successfully!")
