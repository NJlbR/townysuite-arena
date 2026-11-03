import os
import json

# Minimal set of files to make it work
sources = [
    {
        "path": "src/main/java/com/towny/architecture/TownyArchitecturePlugin.java",
        "name": "TownyArchitecturePlugin.java",
        "content": """package com.towny.architecture;
import org.bukkit.plugin.java.JavaPlugin;
public class TownyArchitecturePlugin extends JavaPlugin {
    @Override
    public void onEnable() {
        getLogger().info("TownyArchitecture v2.8.9 успешно активирован!");
    }
}""",
        "category": "core"
    },
    {
        "path": "src/main/java/com/towny/architecture/manager/HologramDisplayManager.java",
        "name": "HologramDisplayManager.java",
        "content": """package com.towny.architecture.manager;
import org.bukkit.*;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.util.Transformation;
import org.joml.AxisAngle4f;
import org.joml.Vector3f;
public class HologramDisplayManager {
    public static final Color GLOW_BLUE = Color.fromRGB(0, 229, 255);
    public static final Color GLOW_RED = Color.fromRGB(255, 30, 30);
    public Transformation createBlockTransformation() {
        return new Transformation(new Vector3f(0,0,0), new AxisAngle4f(), new Vector3f(1.0f, 1.0f, 1.0f), new AxisAngle4f());
    }
}""",
        "category": "core"
    }
]

meta = {
  "name": "TownyArchitecture",
  "version": "2.8.9",
  "jarFileName": "TownyArchitecture-2.8.9.jar",
  "jarDownloadUrl": "/TownyArchitecture-2.8.9.jar",
  "jarSizeFormatted": "120 KB",
  "jarSizeBytes": 120000,
  "fileSizeFormatted": "120 KB",
  "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "bundleFileName": "TownyArchitecture-v2.8.9-bundle.zip",
  "bundleDownloadUrl": "/TownyArchitecture-v2.8.9-bundle.zip",
  "bundleSizeFormatted": "120 KB",
  "bundleSizeBytes": 120000,
  "description": "Городские постройки v2.8.9 - Тонкие светящиеся рёбра (Contact Edges) без частиц.",
  "releaseDate": "2026-10-30",
  "category": "Core / Building"
}

with open('./src/data/javaSources.ts', 'w', encoding='utf-8') as f:
    f.write(f"export const JAVA_SOURCES = {json.dumps(sources, ensure_ascii=False, indent=2)};\\n")
    f.write(f"export const JAVA_SOURCES_V2 = {json.dumps(sources, ensure_ascii=False, indent=2)};\\n")
    f.write(f"export const JAVA_SOURCES_V1 = {json.dumps(sources, ensure_ascii=False, indent=2)};\\n")
    f.write(f"export const PLUGIN_METADATA = {json.dumps(meta, ensure_ascii=False, indent=2)};\\n")
    f.write(f"export const PLUGIN_METADATA_V2 = {json.dumps(meta, ensure_ascii=False, indent=2)};\\n")
    f.write(f"export const PLUGIN_METADATA_V1 = {json.dumps(meta, ensure_ascii=False, indent=2)};\\n")
