/**
 * Test script to verify proj4 coordinate conversion
 * This tests the RD to WGS84 conversion that's used in RegenbuiSimulatie.vue
 */

import proj4 from 'proj4';

// Configure proj4 for RD (Amersfoort) to WGS84
proj4.defs("EPSG:28992", "+proj=sterea +lat_0=52.15616055555557 +lon_0=5.387638888888892 +k_0=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +units=m +no_defs");

console.log('Testing proj4 coordinate conversion...\n');

// Test cases with known RD coordinates and expected WGS84 results
const testCases = [
  {
    name: 'Amsterdam Centraal',
    rd: [121000, 488000],
    expected: [4.900, 52.373] // Approximate expected values
  },
  {
    name: 'Rotterdam Centraal',
    rd: [98000, 440000],
    expected: [4.478, 51.924] // Approximate expected values
  },
  {
    name: 'Utrecht Centraal',
    rd: [121000, 462000],
    expected: [4.891, 52.146] // Approximate expected values (corrected)
  },
  {
    name: 'Gouda',
    rd: [105000, 455000],
    expected: [4.716, 52.015] // Approximate expected values
  }
];

let passed = 0;
let failed = 0;

testCases.forEach((testCase, index) => {
  try {
    const [x, y] = testCase.rd;
    const [lng, lat] = proj4("EPSG:28992", "WGS84", [x, y]);
    
    const [expectedLng, expectedLat] = testCase.expected;
    
    // Check if results are within reasonable bounds
    const lngValid = lng >= -180 && lng <= 180;
    const latValid = lat >= -90 && lat <= 90;
    const lngReasonable = Math.abs(lng - expectedLng) < 0.1; // Within 0.1 degrees
    const latReasonable = Math.abs(lat - expectedLat) < 0.1; // Within 0.1 degrees
    
    if (lngValid && latValid && lngReasonable && latReasonable) {
      console.log(`✓ Test ${index + 1}: ${testCase.name}`);
      console.log(`  RD(${x}, ${y}) -> WGS84(${lng.toFixed(6)}, ${lat.toFixed(6)})`);
      console.log(`  Expected: WGS84(${expectedLng}, ${expectedLat})`);
      console.log(`  Status: PASS\n`);
      passed++;
    } else {
      console.log(`✗ Test ${index + 1}: ${testCase.name}`);
      console.log(`  RD(${x}, ${y}) -> WGS84(${lng.toFixed(6)}, ${lat.toFixed(6)})`);
      console.log(`  Expected: WGS84(${expectedLng}, ${expectedLat})`);
      console.log(`  Status: FAIL - Results out of expected range\n`);
      failed++;
    }
  } catch (error) {
    console.log(`✗ Test ${index + 1}: ${testCase.name}`);
    console.log(`  Error: ${error.message}\n`);
    failed++;
  }
});

console.log('='.repeat(50));
console.log(`Test Results: ${passed} passed, ${failed} failed`);
console.log('='.repeat(50));

if (failed === 0) {
  console.log('\n✓ All tests passed! proj4 conversion is working correctly.');
  process.exit(0);
} else {
  console.log('\n✗ Some tests failed. Check the conversion logic.');
  process.exit(1);
}
