with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

start_sig = "public ExistingStageAlignment detectExistingConstruction"
start_idx = code.find(start_sig)
end_idx = code.find("return bestAlignment;\n    }", start_idx) + len("return bestAlignment;\n    }")

print(code[start_idx:end_idx])
