import os
import json
import argparse
from google import genai
from google.genai import types
import utils
import time
import concurrent.futures
parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
args = parser.parse_known_args()[0]

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
#MODEL_ID = "gemini-3.1-pro-preview"
#MODEL_ID = 'gemini-3-flash-preview'
MODEL_ID = "gemini-2.5-flash"


PROJECT_DIR = f"projects/{args.project}"
THESIS_PATH = f"{PROJECT_DIR}/thesis.md"
EVIDENCE_PATH = f"{PROJECT_DIR}/evidence.txt"

def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def safe_generate_committee(prompt, config=None):
    """Retries for 503 (High Demand) and 429 (Rate Limits)."""
    for i in range(12):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            print(f"📡 [DEBUG] Dispatching request to {MODEL_ID}... (Attempt {i+1})")
            start_time = time.time()
            
            future = executor.submit(
                client.models.generate_content,
                model=MODEL_ID, contents=prompt, config=config
            )
            response = future.result(timeout=150) 
            
            elapsed = time.time() - start_time
            print(f"✅ [DEBUG] Response received in {elapsed:.1f}s")
            return response
            
        except concurrent.futures.TimeoutError:
            wait_time = (i + 1) * 15
            print(f"⚠️ Zombie Connection Killed (150s Timeout). Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            error_str = str(e)
            if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                wait_time = (i + 1) * 15
                print(f"⚠️ API Transient Issue ({error_str[:15]}...). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Unhandled Exception: {error_str}")
                raise e
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
            
    raise Exception("Max retries exceeded.")

def generate_dynamic_attackers(thesis_text, evidence_text):
    prompt = f"""
    You are an elite epistemological expert, knowledgable across domains.
    Read the thesis and the immutable evidence.
    Identify the 3 most vulnerable assumptions.
    
    Generate a JSON array of 3 distinct, highly specialized 'Attacker' personas to audit this specific document.
    They must be adversarial, mathematically rigorous, and focused exclusively on edge cases and execution friction.
    One of these attackers MUST focus exclusively on the mathematical solvency of the Python falsification suite and the LOAD-BEARING VARIABLES table
    Do NOT give them scoring criteria. They exist only to find logical flaws.
    
    EVIDENCE: {evidence_text}
    THESIS: {thesis_text}
    """
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "role": {"type": "STRING", "description": "e.g., Hospital CFO, Enterprise IT Architect"},
                    "persona": {"type": "STRING", "description": "Detailed psychological priming. How do they attack?"},
                    "focus_area": {"type": "STRING", "description": "The specific vulnerability they must target."}
                },
                "required": ["role", "persona", "focus_area"]
            }
        }
    )
    
    response = safe_generate_committee(prompt, config=config)
    return utils.parse_llm_json(response.text)
         
    

if __name__ == "__main__":
    print(f"🕵️ Generating Specialized Firing Squad for [{args.project}]...")
    thesis = read_file(THESIS_PATH)
    evidence = read_file(EVIDENCE_PATH)
    
    attackers_data = generate_dynamic_attackers(thesis, evidence)
    
    output_path = f"rubrics/dynamic_{args.project}.json"
    with open(output_path, "w") as f:
        json.dump({"committee": attackers_data}, f, indent=2)
        
    print(f"✅ Firing Squad generated and saved to {output_path}")