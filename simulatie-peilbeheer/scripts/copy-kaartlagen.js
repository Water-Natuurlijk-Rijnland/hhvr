#!/usr/bin/env node

/**
 * Script om kaartlagen te kopiëren naar de public folder voor GitHub Pages
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sourceDir = path.resolve(__dirname, '../../peilbesluiten/rijnland_kaartlagen');
const targetDir = path.resolve(__dirname, '../public/peilbesluiten/rijnland_kaartlagen');

function copyDirectory(src, dest) {
  if (!fs.existsSync(src)) {
    console.log(`⚠️  Source directory niet gevonden: ${src}`);
    return false;
  }

  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else if (entry.isFile() && entry.name.endsWith('.geojson')) {
      // Alleen GeoJSON bestanden kopiëren
      fs.copyFileSync(srcPath, destPath);
      console.log(`✓ Kopieerd: ${entry.name}`);
    }
  }

  return true;
}

console.log('📁 Kopiëren van kaartlagen...');
console.log(`Van: ${sourceDir}`);
console.log(`Naar: ${targetDir}`);

const success = copyDirectory(sourceDir, targetDir);

if (success) {
  console.log('✅ Kaartlagen succesvol gekopieerd!');
} else {
  console.log('⚠️  Kaartlagen niet gevonden - applicatie gebruikt server fallback');
}

