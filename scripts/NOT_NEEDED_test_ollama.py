import json
import ollama

# Raw rug title that needs fallback parsing
raw_title = 'Decorative hand Knotted transitional design Afghan rug 100% wool pile and cotton foundation size 9ft by 12ft new'

# Define strict system prompt with schema guidelines
system_prompt = """
You are a data extraction assistant. Extract rug attributes from the title into JSON.
Return ONLY valid JSON matching this schema:
{
    "country_of_origin": string or null,
    "regional_style": string or null,
    "width_ft": float or null,
    "length_ft": float or null
}
Do not include any intro, markdown, or extra conversational text.
"""

response = ollama.chat(
    model='llama3.2',
    format='json',  # Enforces JSON output format from Ollama
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f'Extract attributes from: "{raw_title}"'}
    ]
)

# Parse JSON response into a Python dictionary
parsed = json.loads(response['message']['content'])
print(json.dumps(parsed, indent=4))