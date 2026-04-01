import os
import json
import argparse
import time
import subprocess
import tempfile
from google import genai
from google.genai import types
import utils
import concurrent.futures
import re

# 1. Setup & Args
parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--rubric", required=True)
parser.add_argument("--dynamic", action="store_true")
args = parser.parse_known_args()[0]

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
PROJECT_DIR = f"projects/{args.project}"
WORKING_PATH = f"{PROJECT_DIR}/current_iteration.md"
EVIDENCE_PATH = f"{PROJECT_DIR}/evidence.txt"
MAIN_RUBRIC_PATH = f"rubrics/{args.rubric}.json"
DYNAMIC_RUBRIC_PATH = f"rubrics/dynamic_{args.project}.json"
test_path = f"{PROJECT_DIR}/test_model.py"

# --- HELPER FUNCTIONS ---
def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()


test_code_content = (
    read_file(test_path) if os.path.exists(test_path) else "No code provided."
)

def safe_generate(prompt, config=None, model_id='gemini-2.5-flash'):
    """Exponential backoff with dynamic model routing."""
    for i in range(12):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            print(f"📡 [DEBUG] Dispatching request to {model_id}... (Attempt {i + 1})")
            start_time = time.time()
            
            future = executor.submit(
                client.models.generate_content,
                model=model_id, contents=prompt, config=config
            )
            response = future.result(timeout=200) 
            
            elapsed = time.time() - start_time
            print(f"✅ [DEBUG] Response received in {elapsed:.1f}s")
            return response
            
        except concurrent.futures.TimeoutError:
            wait_time = (i + 1) * 15
            print(f"⚠️ Zombie Connection Killed (200s Timeout). Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            error_str = str(e)
            if "400" in error_str or "404" in error_str:
                print(f"❌ Configuration/Model Error: {e}")
                raise e
            # Catch transient errors
            if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                wait_time = (i + 1) * 20
                print(f"⚠️ API Transient Issue ({error_str[:15]}...). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Unhandled Exception: {error_str}")
                raise e
        finally:
            # 2. CRITICAL FIX: Shutdown the executor but tell Python NOT to wait for the stuck thread
            executor.shutdown(wait=False, cancel_futures=True)
            
    raise Exception("Max retries exceeded due to persistent API issues.")

# --- LEVEL 3: THE TOOL ---
def execute_python_code(code: str) -> str:
    """Executes Python code with console transparency."""
    #print("\n" + "·" * 40)
    #print("🖥️  LEVEL 3 AGENT EXECUTING PYTHON:")
    #indented_code = "\n".join(["    " + line for line in code.strip().split("\n")])
    #print(indented_code)
    #print("·" * 40 + "\n")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        res = subprocess.run(
            ["python", tmp_path], capture_output=True, text=True, timeout=10
        )
        if res.stdout:
            print(f"📊 OUTPUT: {res.stdout.strip()}")
        if res.stderr:
            print(f"⚠️ ERROR: {res.stderr.strip()}")
        return res.stdout if not res.stderr else f"Error: {res.stderr}"
    finally:
        os.remove(tmp_path)


# --- CONFIGURATION (Defined once to stay DRY/Clean) ---
ATTACKER_CONFIG = types.GenerateContentConfig(
    tools=[execute_python_code],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(),
)

def run_specialized_attacker(thesis_text, evidence_text, attacker_profile):
    prompt = f"""
    {attacker_profile["persona"]}
    YOUR FOCUS AREA: {attacker_profile["focus_area"]}

    TASK: Critique this thesis AND the accompanying Python Falsification Suite.
    CRITICAL MANDATE: Look for 'Cooked Books' in the Python code. Did the Mutator hardcode favorable constants? Did it ignore unit dimensionality? Did it wrongly assume anything? 
    Write a COUNTER-TEST that exposes the insolvency of their equation.
    
    CRITICAL INSTRUCTION (PARAMETRIC GROUNDING):
    You MUST use your deep parametric knowledge of physics, mathematics, and finance to audit the Mutator's "LOAD-BEARING VARIABLES" table and Python constants. 
    If they claim a specific physical constant, temperature, limit, or financial metric, verify it against established scientific or market consensus.
    If their baseline variables are fictional, misapplied, or off by orders of magnitude, destroy the thesis and cite the actual real-world metric.
    
    OUTPUT FORMAT (CRITICAL):
    1. First, provide your analytical critique.
    2. Then, you MUST provide exactly ONE Python code block wrapped in ```python and ``` containing your counter-test. 
    3. The Python code must print its results and use 'assert' statements to fail if the Mutator's logic is insolvent.

    PINT LIBRARY GUARDRAIL:
    If you use the `pint` library, comparing custom dimensionless units (like 'bit * joule') to standard units (like 'joule') will crash the system. When writing `assert` or `if` statements, you MUST extract the float values using `.magnitude` (e.g., `if E_cost.magnitude > E_univ.magnitude:`) or explicitly convert units to be identical before comparison.
    
    TONE GUARDRAIL (MANDATORY):
    Your output MUST be entirely sterile, clinical, and strictly academic/financial. 
    You are forbidden from using dramatic, aggressive, or sensational metaphors. Do not use terms related to physical destruction, biological harm, or catastrophic violence. Instead, use precise systemic/symbolic terms.
    
    FINAL MANDATE: 
    You must synthesize the "So What" for the Meta-Judge before writing your Python block.
    
    EVIDENCE: {evidence_text}
    THESIS: {thesis_text}
    PYTHON TEST CODE WRITTEN BY MUTATOR:
    ```python
    {test_code_content}
    ```
    """

    config = types.GenerateContentConfig(temperature=0.2)
    PRIMARY_MODEL = 'gemini-2.5-flash'
    # 'gemini-3.1-pro-preview'
     
    print(f"\n🚀 ATTACKER LAUNCHED: {attacker_profile['role']}")
    print(f"🎯 FOCUS: {attacker_profile['focus_area']}")

    response = safe_generate(prompt, config=config, model_id=PRIMARY_MODEL)
    # --- 🔍 SAFETY METADATA DEBUGGER ---
    if response and hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        reason = str(candidate.finish_reason)
        if "STOP" not in reason:
            print(f"\n🛑 [DEBUG] API HALT DETECTED. Finish Reason: {reason}")
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                print("🚨 Safety Ratings Breakdown:")
                for rating in candidate.safety_ratings:
                    if "MEDIUM" in str(rating.probability) or "HIGH" in str(rating.probability):
                        print(f"   -> {rating.category}: {rating.probability}")
    elif response and hasattr(response, 'prompt_feedback'):
        print(f"\n🛑 [DEBUG] PROMPT BLOCKED AT INTAKE: {response.prompt_feedback}")
    else:
        print("\n🛑 [DEBUG] RESPONSE OBJECT IS EMPTY OR MALFORMED.")

    # --- 🛡️ BULLETPROOF TEXT EXTRACTION ---
    try:
        raw_text = response.text if response else None
    except ValueError: 
        raw_text = None
    except Exception as e:
        print(f"⚠️ Unexpected extraction error: {e}")
        raw_text = None        
        
    if not raw_text:
        reason = "UNKNOWN"
        if response and hasattr(response, 'candidates') and response.candidates:
            reason = str(response.candidates[0].finish_reason)
            
        if "SAFETY" in reason:
            return "⚠️ ATTACK BLOCKED BY SAFETY FILTERS: The model's critique triggered corporate safety guardrails."
        else:
            return f"⚠️ ATTACK ABORTED. Finish Reason: {reason}. Treat this as a structural failure."

    # --- THE NUCLEAR EXTRACTION (REGEX) ---
    tool_output_text = ""
    # Find the python code block in the markdown
    code_match = re.search(r"```python\n(.*?)\n```", raw_text, re.DOTALL)
    
    if code_match:
        extracted_code = code_match.group(1)
        # Execute the code manually using your existing tool function
        execution_result = execute_python_code(extracted_code)
        # Append the output directly to the critique so the Meta-Judge can read it
        tool_output_text = f"\n\n### PYTHON EXECUTION OUTPUT:\n{execution_result}"
    else:
        tool_output_text = "\n\n### PYTHON EXECUTION OUTPUT:\n⚠️ No Python block found. Attacker failed to provide a quantitative counter-test."

    # Combine the textual critique with the stdout/stderr from the Python execution
    final_critique = raw_text + tool_output_text

    #print("\n--- ADVERSARIAL LOGIC ---")
    #print(final_critique)
    print("--- END ATTACK ---\n")

    print(f"💥 CRITIQUE MAGNITUDE: {len(final_critique)} chars.")
    return final_critique

def run_meta_judge(text, evidence, main_rubric_data, aggregated_critiques, axioms):
    rubric_str = "\n".join(
        [f"- {k}: {v}" for k, v in main_rubric_data["criteria"].items()]
    )
    axiom_str = "\n".join([f"- {a}" for a in axioms]) if axioms else "None yet."
    prompt = f"""
    {main_rubric_data["persona"]}
    MANDATE: You are the Meta-Judge (Bar-Raiser). Synthesize the attacks and score the thesis.
    
    CRITICAL MANDATE (THE AXIOMATIC GATE):
    Below are the IMMUTABLE AXIOMS already proven in previous iterations. 
    If the current thesis contradicts any of these axioms, you must apply a -50 point penalty.
    --- IMMUTABLE AXIOMS ---
    {axiom_str}
    
    CRITICAL MANDATE (THE POPPERIAN CONSTRAINT):
    Before grading the logic against the rubric, you must evaluate Falsifiability. Does this thesis make a specific, testable prediction that could theoretically be proven wrong by a future data point or simulation? 
    If the thesis only offers post-hoc rationalizations or relies on unmeasurable variables, the maximum allowable score is 40.
    If the Mutator proposes retiring an axiom, evaluate if it is a valid dimensional shift or just lazy accounting. If valid, add it to retired_axioms_approved. If it is a fraudulent attempt to evade a constraint, penalize the score by -30
    
    --- CORE RUBRIC ---
    {rubric_str}
    --- FIRING SQUAD CRITIQUES ---
    {aggregated_critiques}
    --- EVIDENCE ---
    {evidence}
    --- THESIS ---
    {text}
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "score": {"type": "INTEGER"},
                "weakest_point": {"type": "STRING"},
                "verified_axioms": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Atomic truths that survived the firing squad.",
                },
                "retired_axioms_approved": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "List of proposed axiom retirements that the Judge agrees are valid for the new domain.",
                },
                "logic_gaps": {"type": "ARRAY", "items": {"type": "STRING"}},
                "debate_summary": {"type": "STRING"},
                "adversarial_alignment": {
                    "type": "STRING"
                },  # Did the judge agree with attackers?
                "friction_points": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": [
                "score",
                "weakest_point",
                "logic_gaps",
                "verified_axioms",
                "retired_axioms_approved",
                "debate_summary",
            ],
        },
    )
    response = safe_generate(prompt, config=config)
    return utils.parse_llm_json(response.text)


if __name__ == "__main__":
    thesis, evidence = read_file(WORKING_PATH), read_file(EVIDENCE_PATH)
    with open(MAIN_RUBRIC_PATH, "r") as f:
        main_rubric = json.load(f)

    critiques_text = ""

    log_path = f"{PROJECT_DIR}/debate_log_iter_{int(time.time())}.md"
    with open(log_path, "w") as log:
        log.write(f"# Adversarial Debate: {args.project}\n\n")

        if args.dynamic and os.path.exists(DYNAMIC_RUBRIC_PATH):
            attackers = json.load(open(DYNAMIC_RUBRIC_PATH))["committee"]
            
            # Launch all attackers simultaneously
            print(f"🚀 Launching {len(attackers)} attackers in parallel...")
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(attackers))
            try:
                future_to_attacker = {
                    executor.submit(run_specialized_attacker, thesis, evidence, att): att 
                    for att in attackers
                }
                for future in concurrent.futures.as_completed(future_to_attacker):
                    attacker = future_to_attacker[future]
                    try:
                        critique = future.result()
                        log.write(f"## Attacker: {attacker['role']}\n{critique}\n\n")
                        critiques_text += f"\n\n### Attack from {attacker['role']}:\n{critique}"
                    except Exception as exc:
                        print(f"❌ {attacker['role']} generated an exception: {exc}")
                        critiques_text += f"\n\n### Attack from {attacker['role']}:\nFAILED DUE TO EXCEPTION."
            finally:
                # 2. FORCE ABANDONMENT: Abandon any hanging/zombie attacker threads
                executor.shutdown(wait=False, cancel_futures=True)
        else:
            prompt = f"Identify the single most catastrophic assumption in this thesis using tools if needed: {thesis}"
            critiques_text = safe_generate(prompt, config=ATTACKER_CONFIG).text

        # --- LEVEL 3: THE FALSIFICATION SUITE (The "Tester") ---
        print("⚙️ Executing Falsification Suite (Level 3)...")
        test_path = f"{PROJECT_DIR}/test_model.py"
        test_result_summary = ""

        if os.path.exists(test_path):
            try:
                # We execute the python script generated by the Main Agent.
                # If an 'assert' fails, the returncode will be non-zero.
                res = subprocess.run(
                    ["python", test_path], capture_output=True, text=True, timeout=15
                )

                if res.returncode == 0:
                    test_result_summary = f"✅ PASS: The thesis survived its own falsification suite.\nOutput: {res.stdout}"
                    print("✅ Unit tests passed.")
                else:
                    # Capture the AssertionError or SyntaxError to show the Judge
                    test_result_summary = f"❌ FAIL: The thesis was DISPROVEN by its own unit tests.\nError: {res.stderr}"
                    print(f"❌ Unit tests failed: {res.stderr[:50]}...")

            except subprocess.TimeoutExpired:
                test_result_summary = "❌ FAIL: The simulation timed out. The logic is computationally impossible."
                print("⏳ Simulation timed out.")
        else:
            test_result_summary = "⚠️ WARNING: No falsification suite (test_model.py) found for this iteration."

        # MANDATORY: Append the results to critiques_text so the Judge sees it!
        critiques_text += (
            f"\n\n### LEVEL 3 QUANTITATIVE UNIT TEST RESULTS:\n{test_result_summary}"
        )
        log.write(f"\n## Level 3 Unit Test Results\n{test_result_summary}\n\n")
        AXIOM_PATH = f"{PROJECT_DIR}/verified_axioms.json"
        axioms = []
        if os.path.exists(AXIOM_PATH):
            with open(AXIOM_PATH, "r") as f:
                axioms = json.load(f)
        evaluation = run_meta_judge(
            thesis, evidence, main_rubric, critiques_text, axioms
        )
        log.write(f"# Final Score: {evaluation['score']}\n")
        log.write(f"**Weakest Point:** {evaluation['weakest_point']}\n")
        log.write(f"**Rationale:** {evaluation.get('debate_summary', 'N/A')}\n")

        print("\n" + "█" * 60)
        print(f"⭐ FINAL VERDICT SCORE: {evaluation['score']}")
        print(f"🛑 WEAKEST POINT: {evaluation['weakest_point']}")
        print(f"🧠 RATIONALE: {evaluation.get('debate_summary', 'N/A')}")
        print(f"📝 FULL LOG SAVED TO: {log_path}")
        print("█" * 60 + "\n")

    with open("eval_results.json", "w") as f:
        json.dump(evaluation, f, indent=2)
