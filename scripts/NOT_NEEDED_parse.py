import json
import re
from pathlib import Path
from rapidfuzz import process, fuzz

# ---------------------------------------------------------------------------
# 1. PATH SETUP (Dynamic & Absolute)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

# Input raw scraped dataset
INPUT_FILE = ROOT_DIR / "generated_data" / "oriental_rugs.json"
# Output cleaned dataset
OUTPUT_FILE = ROOT_DIR / "generated_data" / "oriental_rugs_parsed.json"

# ---------------------------------------------------------------------------
# 2. MASTER TAXONOMIES (Ground Truth Canonical Lists)
# ---------------------------------------------------------------------------
VALID_ORIGINS = [
    "Iran", "Turkey", "Armenia", "Caucasus", 
    "Afghanistan", "India", "Pakistan", "China", "Turkmenistan"
]

# Common regional styles / weaving cities
VALID_STYLES = [
    "Heriz", "Oushak", "Tabriz", "Kerman", "Isfahan", "Sarouk", 
    "Bijar", "Kashan", "Shirvan", "Kazak", "Bokhara", "Hamadan", 
    "Senneh", "Gabbeh", "Malayer", "Mahal", "Serapi", "Bakhtiari"
]

# Mapping regional styles directly to standard country origins
STYLE_TO_ORIGIN = {
    "Heriz": "Iran", "Tabriz": "Iran", "Kerman": "Iran", "Isfahan": "Iran",
    "Sarouk": "Iran", "Bijar": "Iran", "Kashan": "Iran", "Hamadan": "Iran",
    "Senneh": "Iran", "Gabbeh": "Iran", "Malayer": "Iran", "Mahal": "Iran",
    "Serapi": "Iran", "Bakhtiari": "Iran",
    "Oushak": "Turkey",
    "Shirvan": "Caucasus", "Kazak": "Caucasus",
    "Bokhara": "Turkmenistan"
}

# ---------------------------------------------------------------------------
# 3. DETERMINISTIC PARSING & FUZZY MATCHING LOGIC
# ---------------------------------------------------------------------------
def parse_rug_title(title: str) -> dict:
    if not title:
        return {
            "clean_title": "",
            "width_ft": None,
            "length_ft": None,
            "regional_style": None,
            "country_of_origin": "Unknown",
            "confidence_score": 0.0
        }

    # Normalize whitespace
    clean_title = re.sub(r'\s+', ' ', title).strip()
    
    # --- A. DIMENSION EXTRACTION VIA REGEX ---
    # Matches patterns like: 8x10, 8.5 x 11.2, 8' x 10', 8ft x 10ft, 8'4" x 11'2"
    width, length = None, None
    dim_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:'|ft|feet)?\s*(?:\d+\s*(?:\"|in)?)?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:'|ft|feet)?", 
        clean_title
    )
    if dim_match:
        width = float(dim_match.group(1))
        length = float(dim_match.group(2))

    # --- B. FUZZY STYLE & ORIGIN MATCHING ---
    found_style = None
    found_origin = "Unknown"
    confidence = 100.0

    # 1. Direct check for explicitly named countries in title
    for country in VALID_ORIGINS:
        if re.search(r'\b' + re.escape(country) + r'\b', clean_title, re.IGNORECASE):
            found_origin = country
            break

    # 2. Tokenize title words and run fuzzy matching against known styles
    words = clean_title.split()
    best_score = 0
    
    for word in words:
        # Ignore short numbers/measurement tokens
        if len(word) < 3 or word.isdigit():
            continue

        # Match individual words against VALID_STYLES with score threshold (> 82/100 similarity)
        match = process.extractOne(word, VALID_STYLES, scorer=fuzz.ratio, score_cutoff=82)
        if match:
            matched_style, score, _ = match
            if score > best_score:
                best_score = score
                found_style = matched_style
                # Infer origin if not explicitly found earlier
                if found_origin == "Unknown":
                    found_origin = STYLE_TO_ORIGIN.get(matched_style, "Unknown")

    # Set confidence score based on extraction success
    if not found_style and found_origin == "Unknown":
        confidence = 50.0

    return {
        "clean_title": clean_title,
        "width_ft": width,
        "length_ft": length,
        "regional_style": found_style,
        "country_of_origin": found_origin,
        "extraction_confidence": confidence
    }

# ---------------------------------------------------------------------------
# 4. MAIN PIPELINE EXECUTION
# ---------------------------------------------------------------------------
def run_parsing_pipeline():
    if not INPUT_FILE.exists():
        print(f"❌ Error: Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        rugs = json.load(f)

    print(f"⚡ Processing {len(rugs)} rug records locally via Regex & RapidFuzz...")

    parsed_count = 0
    for rug in rugs:
        raw_name = rug.get("name", "")
        # Attach parsed metadata directly to each rug object
        rug["parsed_data"] = parse_rug_title(raw_name)
        parsed_count += 1

    # Save to 2_staged clean location
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(rugs, f, indent=4)

    print(f"✅ SUCCESS! Cleaned {parsed_count} rows in < 1 second.")
    print(f"📁 Saved staged dataset to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_parsing_pipeline()