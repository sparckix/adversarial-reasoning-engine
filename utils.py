import json
def parse_llm_json(raw_text):
    clean_text = raw_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:-3]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:-3]
    return json.loads(clean_text)