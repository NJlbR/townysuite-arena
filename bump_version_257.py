import json
from datetime import datetime

with open("version.json", "r", encoding="utf-8") as f:
    v_data = json.load(f)

v_data["patch"] = 7
v_data["version"] = "2.5.7"
v_data["release_name"] = "Smart Facing Alignment & /build rotate Command"
v_data["last_updated"] = datetime.utcnow().isoformat() + "Z"

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(v_data, f, indent=2)

print("Bumped version to v2.5.7")
