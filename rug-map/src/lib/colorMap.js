// src/lib/colorMap.js

/**
 * Standardized color definitions with HEX codes for visual swatches.
 */
export const COLOR_CONFIG = {
  red: { label: 'Red', hex: '#ef4444' },
  blue: { label: 'Blue', hex: '#3b82f6' },
  navy: { label: 'Navy', hex: '#1e3a8a' },
  green: { label: 'Green', hex: '#10b981' },
  yellow: { label: 'Yellow', hex: '#eab308' },
  gold: { label: 'Gold', hex: '#d97706' },
  orange: { label: 'Orange', hex: '#f97316' },
  rust: { label: 'Rust', hex: '#c2410c' },
  brown: { label: 'Brown', hex: '#78350f' },
  beige: { label: 'Beige / Cream', hex: '#f5f5dc' },
  ivory: { label: 'Ivory', hex: '#fffff0' },
  pink: { label: 'Pink', hex: '#ec4899' },
  purple: { label: 'Purple', hex: '#a855f7' },
  black: { label: 'Black', hex: '#18181b' },
  white: { label: 'White', hex: '#f8fafc' },
  grey: { label: 'Grey', hex: '#64748b' },
  unassigned: { label: 'Unassigned / Unknown', hex: '#cbd5e1' }
};

/**
 * Normalizes raw dataset color strings to a canonical key in COLOR_CONFIG.
 */
export function normalizeColor(rawColor) {
  if (!rawColor || typeof rawColor !== 'string') return 'unassigned';
  const clean = rawColor.toLowerCase().trim();

  if (clean.includes('red') || clean.includes('crimson') || clean.includes('ruby')) return 'red';
  if (clean.includes('navy') || clean.includes('indigo') || clean.includes('midnight')) return 'navy';
  if (clean.includes('blue') || clean.includes('azure') || clean.includes('teal')) return 'blue';
  if (clean.includes('green') || clean.includes('olive') || clean.includes('emerald')) return 'green';
  if (clean.includes('gold')) return 'gold';
  if (clean.includes('yellow')) return 'yellow';
  if (clean.includes('rust') || clean.includes('terracotta')) return 'rust';
  if (clean.includes('orange') || clean.includes('amber')) return 'orange';
  if (clean.includes('brown') || clean.includes('chocolate') || clean.includes('walnut')) return 'brown';
  if (clean.includes('beige') || clean.includes('tan') || clean.includes('khaki') || clean.includes('sand')) return 'beige';
  if (clean.includes('ivory') || clean.includes('cream') || clean.includes('off-white')) return 'ivory';
  if (clean.includes('pink') || clean.includes('rose') || clean.includes('magenta')) return 'pink';
  if (clean.includes('purple') || clean.includes('violet') || clean.includes('plum')) return 'purple';
  if (clean.includes('black') || clean.includes('ebony') || clean.includes('charcoal')) return 'black';
  if (clean.includes('white')) return 'white';
  if (clean.includes('grey') || clean.includes('gray') || clean.includes('slate')) return 'grey';

  return 'unassigned';
}

/**
 * Extracts and normalizes all colors for a given rug item.
 */
export function getRugNormalizedColors(rug) {
  const rawColors = rug?.parsed_data?.colors || [];
  if (!Array.isArray(rawColors) || rawColors.length === 0) {
    return ['unassigned'];
  }
  const normalizedSet = new Set(rawColors.map(normalizeColor));
  return Array.from(normalizedSet);
}