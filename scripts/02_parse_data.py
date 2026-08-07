import json
import os
import re
import ollama

input_filepath = "generated_data/oriental_rugs.json"
output_filepath = "generated_data/rugs_parsed_complete.json"

if not os.path.exists(input_filepath):
    raise FileNotFoundError(f"Could not find input file: {input_filepath}")

with open(input_filepath, "r", encoding="utf-8") as f:
    rug_records = json.load(f)

total_records = len(rug_records)
print(f"🚀 Loaded {total_records} records. Starting extraction pipeline...\n")

# Revised System Prompt (Strictly standardized examples and rules)
system_prompt = """
You are an expert data extraction assistant specializing in e-commerce catalog parsing. Your task is to process a rug listing object containing title/description strings ("name") and extract specific attributes into a structured JSON object.

### Extraction Rules:

1. is_sold (boolean): 
   - Set to `true` if the title/name explicitly contains "(SOLD)", "(sold)", "sold", or similar status indicators. Otherwise, set to `false`.

2. width_ft (string or null): 
   - Extract the rug width in feet and inches format as stated (e.g., "8'", "8ft", "5'10\"", "3ft"). Do not output decimal floats. If not mentioned, return null.

3. length_ft (string or null): 
   - Extract the rug length in feet and inches format as stated (e.g., "10'", "11'4\"", "7'8\"", "15ft 5\""). Do not output decimal floats. If not mentioned, return null.

4. regional_style (string or null): 
   - Extract the specific design/style name (e.g., "Heriz", "Shirvan", "Serapi", "Oushak", "Caucasian", "Tabriz", "Sarouk", "Art Deco", "Herati", "European", "Bibikabad", "Kermanshah"). Capitalize properly. If not mentioned, return null.
   If you see "Kazakh", "kazak", "Kazak", or "Caucasian Kazak", assign regional_style to "Caucasian".

5. country_of_origin (string or null): 
   - Extract the modern FULL COUNTRY NAME. 
   - MAP DEMONYMS AND REGIONS TO OFFICIAL COUNTRY NAMES:
     - "Persian" / "Persia" -> "Iran"
     - "Caucasian" / "Caucasus" -> "Azerbaijan"
     - "Afghan" -> "Afghanistan"
     - "Turkish" / "Anatolian" -> "Turkey"
     - "Chinese" -> "China"
     - "Indian" -> "India"
     - "Moroccan" -> "Morocco"
   - Capitalize properly. If not mentioned, return null.

6. weave_type (string or null): 
   - Extract weave style (e.g., "Hand-Knotted", "Hand-Woven", "Needle Point"). Default to "Hand-Knotted" if "hand knotted" is present in the name. If not mentioned, return null.

7. materials (array of strings): 
   - Extract primary material fibers mentioned (e.g., ["Wool"], ["Silk"], ["Wool", "Silk"], ["Wool", "Cotton"]).

8. year_produced (string or null): 
   - Extract the estimated era/year (e.g., "1900s", "1880s", "1930s", "Vintage", "New"). Convert terms like "circa 1900" or "circan 1900" to "1900s".

9. primary_color (string or null): 
   - Extract key color descriptions mentioned (e.g., "Navy Blue", "Soft Colors", "Emerald Green", "Gold"). Use words only. If not mentioned, return null.

10. city (string or null):
    - Extract the specific city/town of origin if mentioned or implied by style (e.g., "Kashan", "Shirvan", "Kermanshah", "Herat", "Tabriz", "Bijar"). If not mentioned, return null.

11. design (string or null):
    - Extract design pattern motifs if mentioned (e.g., "Heriz", "Somakh", "Medallion", "Geometric", "Floral", "Tribal", "Runner"). If not mentioned, return null.

---

### Expected Output Schema:
{
  "is_sold": false,
  "width_ft": "8ft",
  "length_ft": "11'4\"",
  "regional_style": "Heriz",
  "country_of_origin": "Iran",
  "weave_type": "Hand-Knotted",
  "materials": ["Wool", "Cotton"],
  "year_produced": "1930s",
  "primary_color": "Soft Colors",
  "city": "Heriz",
  "design": "Heriz"
}
"""

TYPO_FIXES = {
    r'\btrible\b': 'tribal',
    r'\bknotted100%\b': 'knotted 100%',
    r'\bBeluchi\b': 'Baloch',
    r'\bcircan\b': 'circa',
    r'\bCoucasian\b': 'Caucasian',
    r'\bColletble\b': 'Collectible',
    r'\bbibikabat\b': 'Bibikabad',
    r'""': '"',  # Strip accidental double escaped quote marks in titles
}

# Country mapping table for post-processing safety
COUNTRY_MAP = {
    "persia": "Iran",
    "persian": "Iran",
    "caucasian": "Azerbaijan",
    "caucasus": "Azerbaijan",
    "afghan": "Afghanistan",
    "turkish": "Turkey",
    "anatolian": "Turkey",
    "chinese": "China",
    "indian": "India",
    "moroccan": "Morocco"
}

for idx, record in enumerate(rug_records, 1):
    rec_id = record.get("id", idx)
    raw_name = record.get("name", "")
    
    cleaned_name = raw_name
    for typo_pattern, replacement in TYPO_FIXES.items():
        cleaned_name = re.sub(typo_pattern, replacement, cleaned_name, flags=re.IGNORECASE)

    # Always process through LLM if parsed_data is empty or missing vital metadata
    print(f"[{idx}/{total_records}] 🧠 [Ollama Processing] Record ID {rec_id}...")
    
    try:
        response = ollama.chat(
            model="llama3.2",
            format="json",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Extract attributes from: "{cleaned_name}"'}
            ]
        )
        
        llm_results = json.loads(response["message"]["content"])
        extracted = llm_results.get("parsed_data", llm_results)

        # Enforce country name normalization programmatically as a safeguard
        raw_country = extracted.get("country_of_origin")
        if raw_country and raw_country.lower() in COUNTRY_MAP:
            raw_country = COUNTRY_MAP[raw_country.lower()]

        parsed = {
            "is_sold": extracted.get("is_sold", "(SOLD)" in cleaned_name.upper()),
            "width_ft": extracted.get("width_ft"),
            "length_ft": extracted.get("length_ft"),
            "regional_style": extracted.get("regional_style"),
            "country_of_origin": raw_country,
            "weave_type": extracted.get("weave_type"),
            "materials": extracted.get("materials"),
            "year_produced": extracted.get("year_produced"),
            "primary_color": extracted.get("primary_color"),
            "city": extracted.get("city"),
            "design": extracted.get("design")
        }

    except Exception as e:
        print(f"  ❌ Error on ID {rec_id}: {e}")
        parsed = record.get("parsed_data", {})

    record["name"] = cleaned_name
    record["parsed_data"] = parsed

# Save complete results
os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
with open(output_filepath, "w", encoding="utf-8") as f:
    json.dump(rug_records, f, indent=4, ensure_ascii=False)

print(f"\n🎉 Finished! Saved complete dataset to '{output_filepath}'.")