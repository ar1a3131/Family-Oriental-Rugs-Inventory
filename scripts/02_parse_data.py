import json
import os
import re
import ollama

# 1. Load your existing JSON data
input_filepath = "generated_data/oriental_rugs.json"  # Change if your raw file is named differently
output_filepath = "generated_data/rugs_parsed_complete.json"

if not os.path.exists(input_filepath):
    raise FileNotFoundError(f"Could not find input file: {input_filepath}")

with open(input_filepath, "r", encoding="utf-8") as f:
    rug_records = json.load(f)

total_records = len(rug_records)
print(f"🚀 Loaded {total_records} records. Starting extraction pipeline...\n")

# Expanded system prompt for complete metadata extraction
system_prompt = """
You are an expert data extraction assistant specializing in e-commerce catalog parsing. Your task is to process a list of rug listing objects containing title/description strings ("name") and extract specific attributes into a structured JSON object.

### Extraction Rules:

1. is_sold (boolean): 
   - Set to `true` if the title/name starts with or explicitly contains "(SOLD)", "(sold)", "sold", or similar status indicators. Otherwise, set to `false`.

2. width_ft (float or null): 
   - Extract the rug width in feet. Convert inches to decimal feet if necessary (e.g., 8ft 6" = 8.5). If not mentioned, return null.

3. length_ft (float or null): 
   - Extract the rug length in feet. Convert inches to decimal feet if necessary (e.g., 10ft 6" = 10.5). If not mentioned, return null.

4. regional_style (string or null): 
   - Extract the specific design/style name (e.g., "Heriz", "Shirvan", "Serapi", "Oushak", "Kazak", "Tabriz", "Sarouk", "Art Deco"). Capitalize properly. If not mentioned, return null.

5. country_of_origin (string or null): 
   - Extract the country or overarching geographical origin (e.g., "Persian", "Caucasian", "Afghan", "Turkish", "Chinese", "Indian"). Capitalize properly. If not mentioned, return null.

6. weave_type (string or null): 
   - Extract the weave style (e.g., "Hand-Knotted", "Hand-Woven"). Default to "Hand-Knotted" if "hand knotted" is present in the name. If not mentioned, return null.

7. materials (array of strings): 
   - Extract primary material fibers (e.g., ["Wool"], ["Silk"], ["Wool", "Silk"], ["Cotton"]).

8. year_produced (string or null): 
   - Extract the estimated era/year (e.g., "1900s", "1880s", "1930s", "New"). Convert terms like "circa 1900" to "1900s".

9. primary_color (string or null): 
   - Extract key color descriptions mentioned in the text (e.g., "Navy Blue", "Soft Blue", "Gold", "Emerald Green"). If no explicit color is mentioned, return null.

10. extraction_confidence (float): 
    - Provide a score from 0.0 to 100.0 representing your confidence in the accuracy of the extracted data based on clarity of the description.

---

### Input Data Format:
Each item contains an `id`, `name`, `original_price`, `sale_price`, `image_url`, and `source_page`.

### Expected Output Format:
Return ONLY a valid JSON array containing the original item fields alongside the newly generated `parsed_data` block. Do not include markdown commentary, explanations, or text outside the JSON response.

Example Output Structure:
[
  {
    "id": 20,
    "name": "(SOLD) Hand Knotted authentic antique Persian Heriz Serapies size 11ft 2\" by 14ft 6\" circa 1900s 100% wool pile and cotton foundation",
    "original_price": "$45,000.00",
    "sale_price": "$29,000.00",
    "image_url": "https://img1.wsimg.com/isteam/ip/6297fd88-bda9-4967-b377-b62716f47e9a/ols/1000024780-8bd8813.jpg",
    "source_page": 2,
    "parsed_data": {
      "is_sold": true,
      "width_ft": 11.17,
      "length_ft": 14.5,
      "regional_style": "Heriz Serapi",
      "country_of_origin": "Persian",
      "weave_type": "Hand-Knotted",
      "materials": [
        "Wool",
        "Cotton"
      ],
      "year_produced": "1900s",
      "primary_color": null,
      "extraction_confidence": 95.0
    }
  }
]

---

### Input Data to Process:
[
    {
        "id": 17,
        "name": "Colletble antique hand knotted authentic Coucasian shirvan design 100% pure wool circan 1900 size 3ft by 4ft",
        "original_price": "$2,900.00",
        "sale_price": "$1,750.00",
        "image_url": "https://img1.wsimg.com/isteam/ip/6297fd88-bda9-4967-b377-b62716f47e9a/ols/1000026960.jpg",
        "source_page": 2
    }
]
"""

# Common typo quick-fixes before sending to parser/LLM
TYPO_FIXES = {
    r'\btrible\b': 'tribal',
    r'\bknotted100%\b': 'knotted 100%',
}

for idx, record in enumerate(rug_records, 1):
    rec_id = record.get("id", idx)
    raw_name = record.get("name", "")
    
    # Pre-clean typos in title string
    cleaned_name = raw_name
    for typo_pattern, replacement in TYPO_FIXES.items():
        cleaned_name = re.sub(typo_pattern, replacement, cleaned_name, flags=re.IGNORECASE)

    parsed = record.get("parsed_data", {})

    # Check if key attributes are missing and need LLM evaluation
    needs_fallback = (
        parsed.get("width_ft") is None or 
        parsed.get("regional_style") is None or
        "weave_type" not in parsed or
        "year_produced" not in parsed
    )

    if needs_fallback:
        print(f"[{idx}/{total_records}] 🧠 [Ollama Fallback] Processing Record ID {rec_id}...")
        
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

            # Standardize & map attributes
            parsed["width_ft"] = parsed.get("width_ft") or llm_results.get("width_ft")
            parsed["length_ft"] = parsed.get("length_ft") or llm_results.get("length_ft")
            parsed["regional_style"] = llm_results.get("regional_style") or parsed.get("regional_style")
            parsed["country_of_origin"] = llm_results.get("country_of_origin") or parsed.get("country_of_origin")
            
            # New fields
            parsed["weave_type"] = llm_results.get("weave_type")
            parsed["materials"] = llm_results.get("materials")
            parsed["year_produced"] = llm_results.get("year_produced")
            parsed["primary_color"] = llm_results.get("primary_color")
            
            parsed["extraction_confidence"] = 90.0

        except Exception as e:
            print(f"  ❌ Error on ID {rec_id}: {e}")
    else:
        print(f"[{idx}/{total_records}] ⚡ [Regex Passed] Record ID {rec_id}")

    record["parsed_data"] = parsed

# Save complete results
os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
with open(output_filepath, "w", encoding="utf-8") as f:
    json.dump(rug_records, f, indent=4, ensure_ascii=False)

print(f"\n🎉 Finished! Saved complete dataset to '{output_filepath}'.")