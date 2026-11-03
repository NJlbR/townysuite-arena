import json
from datetime import datetime

with open("version.json", "r", encoding="utf-8") as f:
    v_data = json.load(f)

v_data["patch"] = 4
v_data["version"] = "2.5.4"
v_data["release_name"] = "Strict Anchor Plot & Perfect Rotation Alignment"
v_data["last_updated"] = datetime.utcnow().isoformat() + "Z"

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(v_data, f, indent=2)

print("Bumped version to v2.5.4")
