import json
import re
import os

# Strict mapping of rug keywords to canonical city/region names and country origins
CITY_MAPPINGS = {
    # Iran / Persia
    "tabriz": {"city": "Tabriz", "country": "Iran"},
    "heriz": {"city": "Heriz", "country": "Iran"},
    "kashan": {"city": "Kashan", "country": "Iran"},
    "isfahan": {"city": "Isfahan", "country": "Iran"},
    "esfahan": {"city": "Isfahan", "country": "Iran"},
    "kerman": {"city": "Kerman", "country": "Iran"},
    "shiraz": {"city": "Shiraz", "country": "Iran"},
    "hamadan": {"city": "Hamadan", "country": "Iran"},
    "hamedan": {"city": "Hamadan", "country": "Iran"},
    "sarouk": {"city": "Sarouk", "country": "Iran"},
    "sarouk/farahan": {"city": "Sarouk", "country": "Iran"},
    "farahan": {"city": "Farahan", "country": "Iran"},
    "bijar": {"city": "Bijar", "country": "Iran"},
    "bidjar": {"city": "Bijar", "country": "Iran"},
    "qum": {"city": "Qum", "country": "Iran"},
    "qom": {"city": "Qum", "country": "Iran"},
    "nain": {"city": "Nain", "country": "Iran"},
    "mashhad": {"city": "Mashhad", "country": "Iran"},
    "meshhed": {"city": "Mashhad", "country": "Iran"},
    "sultanabad": {"city": "Sultanabad", "country": "Iran"},
    "malayer": {"city": "Malayer", "country": "Iran"},
    "bakhtiari": {"city": "Bakhtiari", "country": "Iran"},
    "senneh": {"city": "Sanandaj", "country": "Iran"},
    "khorasan": {"city": "Khorasan", "country": "Iran"},

    # Turkey / Anatolia
    "oushak": {"city": "Uşak", "country": "Turkey"},
    "ushak": {"city": "Uşak", "country": "Turkey"},
    "hereke": {"city": "Hereke", "country": "Turkey"},
    "konya": {"city": "Konya", "country": "Turkey"},
    "bergama": {"city": "Bergama", "country": "Turkey"},
    "sivas": {"city": "Sivas", "country": "Turkey"},
    "kars": {"city": "Kars", "country": "Turkey"},
    "milas": {"city": "Milas", "country": "Turkey"},

    # Caucasus
    "shirvan": {"city": "Shirvan", "country": "Caucasus"},
    "dagestan": {"city": "Dagestan", "country": "Caucasus"},
    "karabagh": {"city": "Karabagh", "country": "Caucasus"},
    "kuba": {"city": "Kuba", "country": "Caucasus"},

    # Afghanistan & Central Asia
    "bukhara": {"city": "Bukhara", "country": "Uzbekistan"},
    "bokhara": {"city": "Bukhara", "country": "Uzbekistan"},
    "herat": {"city": "Herat", "country": "Afghanistan"},
    "kabul": {"city": "Kabul", "country": "Afghanistan"},
    "kandahar": {"city": "Kandahar", "country": "Afghanistan"},
    "ashgabat": {"city": "Ashgabat", "country": "Turkmenistan"},

    # India & Pakistan
    "agra": {"city": "Agra", "country": "India"},
    "amritsar": {"city": "Amritsar", "country": "India"},
    "jaipur": {"city": "Jaipur", "country": "India"},
    "kashmir": {"city": "Kashmir", "country": "India"},
    "multan": {"city": "Multan", "country": "Pakistan"},
    "lahore": {"city": "Lahore", "country": "Pakistan"}
}


def extract_city_from_text(item):
    """
    Scans item title and description for exact city keyword matches.
    """
    parsed = item.get('parsed_data', {})
    
    # Exclude regional_style here to avoid matching non-city descriptors
    search_text = " ".join([
        str(item.get('name', '')),
        str(item.get('description', ''))
    ]).lower()

    for keyword, info in CITY_MAPPINGS.items():
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, search_text):
            return info

    return None


# --- MAIN EXECUTION ---
input_filename = 'generated_data/rugs_with_image_analysis.json'
output_filename = 'rug-map/static/rugs_with_image_analysis.json'

print(f"Loading dataset from {input_filename}...")
with open(input_filename, 'r', encoding='utf-8') as f:
    rug_data = json.load(f)

total_items = len(rug_data)
matched_count = 0
city_counts = {}

print(f"Processing {total_items} rug records...\n")

for index, item in enumerate(rug_data):
    parsed_block = item.get('parsed_data', {})
    
    match = extract_city_from_text(item)
    
    if match:
        parsed_block['city'] = match['city']
        matched_count += 1
        city_counts[match['city']] = city_counts.get(match['city'], 0) + 1
    else:
        # Strictly set to "Unknown" if no match in CITY_MAPPINGS
        parsed_block['city'] = "Unknown"

    item['parsed_data'] = parsed_block

# Save enriched output
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(rug_data, f, indent=2)


print(f"\nFinished!")
print(f"• Successfully matched cities for {matched_count}/{total_items} rugs ({round(matched_count/total_items * 100, 1)}%)")
print(f"• Set remaining {total_items - matched_count} rugs to 'Unknown'\n")
print("Top cities identified:")
for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  - {city}: {count} rugs")