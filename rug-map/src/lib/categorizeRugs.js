import { CITY_COORDS } from '$lib/cityCoords.js';
import { REGION_COORDS } from '$lib/regionCoords.js';
import { COUNTRY_COORDS } from '$lib/countryCoords.js';

// Helper function to match raw text to coordinates
function findMatchingCoordKey(targetStr, coordsObject) {
  if (!targetStr || typeof targetStr !== 'string') return null;
  const cleanTarget = targetStr.trim().toLowerCase();
  
  if (coordsObject[targetStr]) return targetStr;

  return Object.keys(coordsObject).find(key => 
    cleanTarget.includes(key.toLowerCase()) || key.toLowerCase().includes(cleanTarget)
  ) || null;
}

// Main categorization function
export function categorizeRugs(rugs) {
  const cityGroups = {};
  const regionGroups = {};
  const countryGroups = {};
  const unmapped = [];

  rugs.forEach(rug => {
    const parsed = rug.parsed_data || {};
    const rawCity = parsed.city && parsed.city !== 'Unknown' ? parsed.city : null;
    const rawRegion = parsed.region || parsed.regional_style || null;
    const rawCountry = parsed.country || parsed.country_of_origin || null;

    // 1. Try City
    const matchedCity = rawCity ? findMatchingCoordKey(rawCity, CITY_COORDS) : null;
    if (matchedCity) {
      cityGroups[matchedCity] = cityGroups[matchedCity] || [];
      cityGroups[matchedCity].push(rug);
      return;
    }

    // 2. Try Region
    const matchedRegion = rawRegion ? findMatchingCoordKey(rawRegion, REGION_COORDS) : null;
    if (matchedRegion) {
      regionGroups[matchedRegion] = regionGroups[matchedRegion] || [];
      regionGroups[matchedRegion].push(rug);
      return;
    }

    // 3. Try Country
    const matchedCountry = rawCountry ? findMatchingCoordKey(rawCountry, COUNTRY_COORDS || {}) : null;
    if (matchedCountry) {
      countryGroups[matchedCountry] = countryGroups[matchedCountry] || [];
      countryGroups[matchedCountry].push(rug);
      return;
    }

    // 4. Fallback: Unspecified
    unmapped.push(rug);
  });

  return { cityGroups, regionGroups, countryGroups, unmapped };
}