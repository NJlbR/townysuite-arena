import { JAR_BASE64, JAR_BASE64_V1, JAR_BASE64_V2, JAR_FILE_NAME } from '../data/jarBase64';
import { BUNDLE_BASE64, BUNDLE_BASE64_V1, BUNDLE_BASE64_V2, BUNDLE_FILE_NAME } from '../data/bundleBase64';
import { RESOURCE_PACK_BASE64 } from '../data/resourcePackBase64';
import { UNBLOCKER_JAR_BASE64, UNBLOCKER_BUNDLE_BASE64, UNBLOCKER_METADATA } from '../data/unblockerData';
import { TOWNY_SIEGES_JAR_BASE64, TOWNY_SIEGES_BUNDLE_BASE64, TOWNY_SIEGES_METADATA } from '../data/townySiegesData';
import { TOWNY_RESPAWN_JAR_BASE64, TOWNY_RESPAWN_BUNDLE_BASE64, TOWNY_RESPAWN_METADATA } from '../data/townyRespawnData';
import { CANNON_BBMODEL_BASE64, CANNON_JSON_BASE64, CANNON_VANILLA_JSON_BASE64, CANNON_CUSTOM_JSON_BASE64, CANNON_WOOD_PNG_BASE64, CANNON_METAL_PNG_BASE64, CANNON_RP_BASE64, CANNON_METADATA } from '../data/cannonModelData';

import { SUITE_ALL_PLUGINS_ZIP_BASE64 } from '../data/suiteZipBase64';

/**
 * Converts a Base64 string to a Uint8Array binary buffer.
 */
function publicAssetUrl(path: string): string {
  const relativePath = path.startsWith('/') ? path.slice(1) : path;
  return `${import.meta.env.BASE_URL}${relativePath}`;
}

function base64ToUint8Array(base64: string): Uint8Array {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

/**
 * Downloads 3D Cannon Blockbench Project (.bbmodel) directly from memory.
 */
export function downloadCannonBbmodel(filename = CANNON_METADATA.fileBbmodelName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_BBMODEL_BASE64);
    const blob = new Blob([bytes], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon .bbmodel download:', err);
    window.location.href = publicAssetUrl(`models/${filename}`);
    return false;
  }
}

/**
 * Downloads 3D Cannon Minecraft JSON Model (.json) directly from memory.
 */
export function downloadCannonJson(filename = CANNON_METADATA.fileJsonName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_JSON_BASE64);
    const blob = new Blob([bytes], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon .json download:', err);
    window.location.href = publicAssetUrl(`models/${filename}`);
    return false;
  }
}

/**
 * Downloads 3D Cannon Custom Textures JSON Model (.json) directly from memory.
 */
export function downloadCannonCustomJson(filename = CANNON_METADATA.fileCustomJsonName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_CUSTOM_JSON_BASE64);
    const blob = new Blob([bytes], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon custom .json download:', err);
    window.location.href = publicAssetUrl(`models/${filename}`);
    return false;
  }
}

/**
 * Downloads 3D Cannon Wood Texture PNG directly from memory.
 */
export function downloadCannonWoodPng(filename = CANNON_METADATA.fileWoodPngName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_WOOD_PNG_BASE64);
    const blob = new Blob([bytes], { type: 'image/png' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon wood PNG download:', err);
    window.location.href = publicAssetUrl(`models/${filename}`);
    return false;
  }
}

/**
 * Downloads 3D Cannon Metal Texture PNG directly from memory.
 */
export function downloadCannonMetalPng(filename = CANNON_METADATA.fileMetalPngName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_METAL_PNG_BASE64);
    const blob = new Blob([bytes], { type: 'image/png' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon metal PNG download:', err);
    window.location.href = publicAssetUrl(`models/${filename}`);
    return false;
  }
}

/**
 * Downloads 3D Cannon Vanilla Textures JSON Model (.json) directly from memory.
 */
export function downloadCannonVanillaJson(filename = CANNON_METADATA.fileVanillaJsonName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_VANILLA_JSON_BASE64);
    const blob = new Blob([bytes], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon vanilla .json download:', err);
    window.location.href = publicAssetUrl(`models/${filename}`);
    return false;
  }
}

export const downloadCannonPng = downloadCannonWoodPng;

/**
 * Downloads 3D Cannon Resource Pack ZIP (.zip) directly from memory.
 */
export function downloadCannonRp(filename = CANNON_METADATA.fileRpName): boolean {
  try {
    const bytes = base64ToUint8Array(CANNON_RP_BASE64);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Cannon RP download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownySieges JAR directly from memory.
 */
export function downloadTownySiegesJar(filename = TOWNY_SIEGES_METADATA.jarFileName): boolean {
  try {
    const bytes = base64ToUint8Array(TOWNY_SIEGES_JAR_BASE64);
    const blob = new Blob([bytes], { type: 'application/java-archive' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory TownySieges JAR download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownySieges Bundle ZIP directly from memory.
 */
export function downloadTownySiegesBundle(filename = TOWNY_SIEGES_METADATA.bundleFileName): boolean {
  try {
    const bytes = base64ToUint8Array(TOWNY_SIEGES_BUNDLE_BASE64);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory TownySieges bundle download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownyRespawn JAR directly from memory.
 */
export function downloadTownyRespawnJar(filename = TOWNY_RESPAWN_METADATA.jarFileName): boolean {
  try {
    const bytes = base64ToUint8Array(TOWNY_RESPAWN_JAR_BASE64);
    const blob = new Blob([bytes], { type: 'application/java-archive' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory TownyRespawn JAR download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownyRespawn Bundle ZIP directly from memory.
 */
export function downloadTownyRespawnBundle(filename = TOWNY_RESPAWN_METADATA.bundleFileName): boolean {
  try {
    const bytes = base64ToUint8Array(TOWNY_RESPAWN_BUNDLE_BASE64);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory TownyRespawn bundle download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownyExplosionUnblocker JAR directly from memory.
 */
export function downloadUnblockerJar(filename = UNBLOCKER_METADATA.jarFileName): boolean {
  try {
    const bytes = base64ToUint8Array(UNBLOCKER_JAR_BASE64);
    const blob = new Blob([bytes], { type: 'application/java-archive' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Unblocker JAR download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownyExplosionUnblocker Bundle ZIP directly from memory.
 */
export function downloadUnblockerBundle(filename = UNBLOCKER_METADATA.bundleFileName): boolean {
  try {
    const bytes = base64ToUint8Array(UNBLOCKER_BUNDLE_BASE64);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Unblocker bundle download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads the resource pack ZIP directly from memory.
 * Bypasses all network proxies, iframe restrictions, and prevents downloading HTML error pages.
 */
export function downloadResourcePackZip(filename = 'TownyArchitecture.zip'): boolean {
  try {
    const bytes = base64ToUint8Array(RESOURCE_PACK_BASE64);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Resource Pack download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}

/**
 * Downloads TownyArchitecture JAR directly from memory.
 */
export function downloadJarFile(version: 'v2' | 'v1' = 'v2', filename?: string): boolean {
  const actualFilename = filename || (version === 'v2' ? JAR_FILE_NAME : 'TownyArchitecture-1.5.0.jar');
  const b64Data = version === 'v2' ? JAR_BASE64_V2 : JAR_BASE64_V1;

  try {
    const bytes = base64ToUint8Array(b64Data);
    const blob = new Blob([bytes], { type: 'application/java-archive' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = actualFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory JAR download:', err);
    window.location.href = publicAssetUrl(actualFilename);
    return false;
  }
}

/**
 * Downloads TownyArchitecture bundle ZIP directly from memory.
 */
export function downloadBundleZip(version: 'v2' | 'v1' = 'v2', filename?: string): boolean {
  const actualFilename = filename || (version === 'v2' ? BUNDLE_FILE_NAME : 'TownyArchitecture-v1.5.0-bundle.zip');
  const b64Data = version === 'v2' ? BUNDLE_BASE64_V2 : BUNDLE_BASE64_V1;

  try {
    const bytes = base64ToUint8Array(b64Data);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = actualFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory Bundle download:', err);
    window.location.href = publicAssetUrl(actualFilename);
    return false;
  }
}

/**
 * Downloads the all-in-one suite ZIP archive containing all 4 distinct JAR plugins.
 */
export function downloadAllPluginsZip(filename = 'TownySuite-All-Plugins.zip'): boolean {
  try {
    const bytes = base64ToUint8Array(SUITE_ALL_PLUGINS_ZIP_BASE64);
    const blob = new Blob([bytes], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
    
    return true;
  } catch (err) {
    console.error('Failed to trigger in-memory All Plugins ZIP download:', err);
    window.location.href = publicAssetUrl(filename);
    return false;
  }
}
