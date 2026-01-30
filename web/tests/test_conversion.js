const fs = require('fs');

// Laad het GeoJSON bestand
const data = JSON.parse(fs.readFileSync('public/data/peilgebieden_rijnland.geojson', 'utf8'));

console.log('=== Testing Peilgebieden Conversion ===');
console.log('Features:', data.features.length);

// Test de eerste feature
const feature = data.features[0];
console.log('\n=== First Feature ===');
console.log('Has attributes:', !!feature.attributes);
console.log('Has geometry:', !!feature.geometry);
console.log('Has rings:', !!feature.geometry.rings);
console.log('First coordinate:', feature.geometry.rings[0][0]);

// Test de conversie naar GeoJSON
const properties = feature.attributes || feature.properties || {};
console.log('\n=== Properties ===');
console.log('NAAM:', properties.NAAM);
console.log('CODE:', properties.CODE);
console.log('OPPERVLAKTE:', properties.OPPERVLAKTE);

// Test de coördinaat conversie
const firstCoord = feature.geometry.rings[0][0];
const isRD = Math.abs(firstCoord[0]) > 10000 && Math.abs(firstCoord[1]) > 10000;
console.log('\n=== Coordinate System ===');
console.log('Is RD:', isRD);
console.log('Coordinate:', firstCoord);

console.log('\n=== Conversion Successful ===');
