// src/lib/styleMap.js

/**
 * Standardized rug style definitions.
 */
export const STYLE_CONFIG = {
  kilim: { label: 'Kilim / Flatweave', badgeColor: '#3b82f6' },
  runner: { label: 'Runner', badgeColor: '#10b981' },
  heriz: { label: 'Heriz / Serapi', badgeColor: '#ef4444' },
  kazak: { label: 'Kazak', badgeColor: '#f59e0b' },
  turkman: { label: 'Turkman / Turkmen', badgeColor: '#8b5cf6' },
  shirvan: { label: 'Shirvan', badgeColor: '#ec4899' },
  artdeco: { label: 'Art Deco / Modern', badgeColor: '#06b6d4' },
  tabriz: { label: 'Tabriz', badgeColor: '#d97706' },
  kashan: { label: 'Kashan', badgeColor: '#6366f1' },
  bijar: { label: 'Bijar', badgeColor: '#b91c1c' },
  pictorial: { label: 'Pictorial / Tree of Life', badgeColor: '#059669' },
  unassigned: { label: 'Unassigned / Other', badgeColor: '#64748b' }
};

/**
 * Maps raw rug data strings (from rug.parsed_data.style, rug.name, or category)
 * to standard style keys.
 */
export function getRugNormalizedStyles(rug) {
  const detected = new Set();

  // Combine relevant text fields for keyword inspection
  const searchText = `
    ${rug?.parsed_data?.style || ''} 
    ${rug?.parsed_data?.type || ''} 
    ${rug?.name || ''} 
    ${rug?.description || ''}
  `.toLowerCase();

  if (searchText.includes('kilim') || searchText.includes('flatweave') || searchText.includes('flat weave')) {
    detected.add('kilim');
  }
  if (searchText.includes('runner') || searchText.includes('gallery')) {
    detected.add('runner');
  }
  if (searchText.includes('heriz') || searchText.includes('serapi')) {
    detected.add('heriz');
  }
  if (searchText.includes('kazak')) {
    detected.add('kazak');
  }
  if (searchText.includes('turkman') || searchText.includes('turkmen') || searchText.includes('tekke') || searchText.includes('bokhara')) {
    detected.add('turkman');
  }
  if (searchText.includes('shirvan')) {
    detected.add('shirvan');
  }
  if (searchText.includes('art deco') || searchText.includes('deco') || searchText.includes('mid-century') || searchText.includes('modern')) {
    detected.add('artdeco');
  }
  if (searchText.includes('tabriz')) {
    detected.add('tabriz');
  }
  if (searchText.includes('kashan')) {
    detected.add('kashan');
  }
  if (searchText.includes('bijar') || searchText.includes('bidjar')) {
    detected.add('bijar');
  }
  if (searchText.includes('pictorial') || searchText.includes('tree of life') || searchText.includes('hunting')) {
    detected.add('pictorial');
  }

  // Fallback if no specific style keywords matched
  if (detected.size === 0) {
    detected.add('unassigned');
  }

  return Array.from(detected);
}