import base64
import json
import requests
import ollama

# Ollama vision analysis

def analyze_rug_image(image_url, current_style=None):
    try:
        # 1. Fetch image from URL
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            print(f"  [!] Failed to download image (Status: {response.status_code})")
            return None
        
        # 2. Convert raw image bytes to base64
        base64_image = base64.b64encode(response.content).decode('utf-8')
        
        # Construct prompt text dynamically based on whether regional_style is missing
        style_prompt = ""
        if not current_style or str(current_style).lower() in ['null', 'none', '', 'nan']:
            style_prompt = '- "suggested_style": Suggest a classification based on visual style (e.g., "Turkmen", "Geometric", "Floral", "Medallion", "Tribal", "Heriz", "Kazak").\n'
        
        prompt = f"""
Analyze this rug image and output strictly valid JSON with the following keys:
- "colors": List of primary/secondary colors visible in the rug (e.g., ["Navy Blue", "Rust Red", "Ivory"]).
- "condition": Visual assessment of condition (e.g., "Excellent", "Good", "Minor Wear/Fading", "Distressed").
- "patterns": List of specific visual motifs/patterns seen (e.g., ["Birds", "Plants", "Pomegranates", "Boteh/Paisley", "Medallion", "Geometric Stars", "Animals", "Pictoral", "Prayer", "Turkmen", "Caucasian", "Tribal/Geometric", "Persian", "Modern"]).
{style_prompt}
Do not include any intro, outro, or markdown outside the raw JSON object.
"""

        # 3. Call Ollama vision model using 'llava'
        res = ollama.chat(
            model='llava',  # Updated to llava to bypass mllama backend errors
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [base64_image]
            }],
            format='json'  # Forces Ollama to enforce valid JSON formatting
        )
        
        # Parse output into Python dict
        return json.loads(res['message']['content'])
        
    except Exception as e:
        print(f"  [!] Error processing image: {e}")
        return None


# --- MAIN EXECUTION ---
input_filename = 'generated_data/rugs_parsed_complete.json'
output_filename = 'generated_data/rugs_with_image_analysis.json'

print(f"Loading {input_filename}...")
with open(input_filename, 'r', encoding='utf-8') as f:
    rug_data = json.load(f)

print(f"Loaded {len(rug_data)} items. Starting vision processing...\n")

# Process items (Currently slicing rug_data[:3] for testing!)
for index, item in enumerate(rug_data):
    image_url = item.get('image_url')
    item_id = item.get('id', index)
    
    # Check parsed_data dictionary structure
    parsed_block = item.get('parsed_data', {})
    current_style = parsed_block.get('regional_style')
    
    print(f"[{index + 1}/{len(rug_data)}] Processing Item ID: {item_id}...")
    
    if image_url:
        vision_result = analyze_rug_image(image_url, current_style=current_style)
        
        if vision_result and isinstance(vision_result, dict):
            # Update specific target fields in parsed_data
            parsed_block['colors'] = vision_result.get('colors', [])
            parsed_block['condition'] = vision_result.get('condition', None)
            parsed_block['patterns'] = vision_result.get('patterns', [])
            
            # Fill missing regional_style if null
            if not current_style and 'suggested_style' in vision_result:
                parsed_block['regional_style'] = vision_result['suggested_style']
                print(f"  [+] Inferred missing style: {vision_result['suggested_style']}")

            item['parsed_data'] = parsed_block
            print("  [✓] Updated visual attributes successfully.")
    else:
        print("  [-] No image_url available.")

# Save updated JSON output
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(rug_data, f, indent=2)

print(f"\nSaved updated dataset to {output_filename}")