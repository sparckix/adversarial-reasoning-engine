import os
import json
import subprocess
import time
import shutil
import argparse
from datetime import datetime
from google import genai
from google.genai import types
import utils
import re
import concurrent.futures

SESSION_TOKENS = 0

# 1. Setup CLI Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--rubric", required=True)
parser.add_argument("--dynamic", action="store_true")
parser.add_argument("--iters", type=int, default=10, help="Number of iterations to run")
parser.add_argument(
    "--auto-evolve",
    action="store_true",
    help="Level 5: AI autonomously rewrites its rubric upon reaching a high score.",
)
args = parser.parse_args()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
ITERATIONS = args.iters
#MUTATOR_MODEL_ID = "gemini-3-flash-preview"  "gemini-3-pro-preview"
MUTATOR_MODEL_ID = "gemini-2.5-flash"
DIRECTOR_MODEL_ID = "gemini-3.1-pro-preview" #"gemini-3-flash-preview"

# Paths
PROJECT_DIR = f"projects/{args.project}"
HISTORY_DIR = f"{PROJECT_DIR}/history"
THESIS_PATH = f"{PROJECT_DIR}/thesis.md"
WORKING_PATH = f"{PROJECT_DIR}/current_iteration.md"
EVIDENCE_PATH = f"{PROJECT_DIR}/evidence.txt"
AXIOM_PATH = f"{PROJECT_DIR}/verified_axioms.json"


def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()


def write_file(filepath, content):
    with open(filepath, "w") as f:
        f.write(content)


def safe_mutate(prompt, config=None, model_id=MUTATOR_MODEL_ID):
    global SESSION_TOKENS

    # DEBUG: Log the current prompt and model to a file
    with open(f"{PROJECT_DIR}/last_prompt_debug.txt", "w") as f:
        f.write(f"MODEL USED: {model_id}\n")
        f.write("=" * 30 + "\n")
        f.write(prompt)

    """Retries for both 429 (Rate Limit) and 503 (Server Overload)."""
    for i in range(12):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            print(f"📡 [DEBUG] Dispatching Mutator request to {model_id}... (Attempt {i + 1})")
            start_time = time.time()
            future = executor.submit(
                client.models.generate_content,
                model=model_id, contents=prompt, config=config
            )
            response = future.result(timeout=150)
            
            elapsed = time.time() - start_time
            print(f"✅ [DEBUG] Response received in {elapsed:.1f}s")
            if response.usage_metadata:
                SESSION_TOKENS += response.usage_metadata.total_token_count
            return response.text

        except concurrent.futures.TimeoutError:
            wait_time = (i + 1) * 15
            print(
                f"⚠️ Zombie Connection Killed. Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)
        except Exception as e:
            error_str = str(e)
            # Catch transient networking/Read errors (like Errno 54)
            is_transient_network_error = any(msg in error_str for msg in [
                "readerror", "connection reset", "broken pipe", "remoteprotocolerror"
            ])
            if "400" in error_str or "404" in error_str:
                print(f"❌ Configuration/Model Error: {e}")
                raise e
            # Catch 500, 502, 503, 504 and 429 as transient retryable errors
            if any(code in error_str for code in ["429", "500", "502", "503", "504"]) or is_transient_network_error:
                wait_time = (i + 1) * 20
                print(f"⚠️ API Transient Issue ({error_str[:15]}...). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Unhandled Exception: {error_str}")
                raise e
            
        finally:
            # CRITICAL FIX: Force thread abandonment on timeout
            executor.shutdown(wait=False, cancel_futures=True)
    raise Exception("Mutation failed after multiple retries.")


# --- CHANGED: Added model_id to the signature ---
def mutate_thesis(
    current_content,
    weakest_point,
    evidence,
    persona,
    stagnation_count,
    model_id=MUTATOR_MODEL_ID,
    failure_log=None,
):
    task_header = "TASK: Resolve the following Systemic Inconsistency:"
    pivot_instruction = ""
    axioms = []
    if os.path.exists(AXIOM_PATH):
        with open(AXIOM_PATH, "r") as f:
            axioms = json.load(f)

    axiom_str = "\n".join([f"- {a}" for a in axioms]) if axioms else "None yet."

    # --- DYNAMIC CONTEXT MANAGEMENT ---
    if stagnation_count >= 4:
        print("🚨 EMERGENCY MANDATE: EXECUTING TOPOLOGICAL PIVOT 🚨")
        print("🧹 Purging toxic axioms to allow true architectural reset...")
        
        if os.path.exists(AXIOM_PATH):
            shutil.copy(AXIOM_PATH, f"{AXIOM_PATH}.bak")
            os.remove(AXIOM_PATH) # Hide from test_thesis.py            
        axiom_str = "NONE. (Previous axioms purged due to topological pivot)."
        document_context = "🚨 [SYSTEM STATE PURGED]: Your previous logic was fundamentally and repeatedly rejected by the Auditor. You are starting from a BLANK SLATE. You must derive a new architecture using ONLY the Grounding Data and First Principles. Do NOT iterative-fix; RE-ENGINEER. 🚨"
        task_header = "🚨 EMERGENCY MANDATE: EXECUTE TOPOLOGICAL PIVOT 🚨"   
    elif stagnation_count >= 3:
        document_context = "🚨 [SYSTEM STATE PURGED]: Current logic has reached a terminal friction point. You must derive a NEW Transformation Function. 🚨"
        task_header = "🚨 EMERGENCY MANDATE: EXECUTE TOPOLOGICAL PIVOT 🚨"
    else:
        document_context = (
            f"### CURRENT SYSTEM STATE (FOR ANALYSIS ONLY)\n{current_content}"
        )

    if stagnation_count >= 3:
        pivot_instruction = """
                ### 🚨 METACOGNITIVE OVERRIDE: FIRST-PRINCIPLES RE-ENGINEERING 🚨
        The Auditor has identified a terminal friction in the current logic. You are forbidden from iterative refinement. You must execute a structural mutation using these Zero-Domain Heuristics:

        1. STATE INCOMPATIBILITY (Critique as Invariant): Treat the Auditor's critique as an immutable Physical Law of the environment. If this constraint is absolute, what entirely new System Architecture must be derived to reach the Target State ($Z$)?
        2. THE EIGENVALUE (Primary Degree of Freedom): Identify the single, irreducible variable where a change in state forces a deterministic reconfiguration of the entire system. Define the cascading logic-gates that follow this shift.
        3. ZERO-TRUST AUTOPSY (Failure Topology): Fast-forward to the state of System Collapse. Map the 3 specific nodes of failure. Erase the assumptions supporting those nodes and build a bypass that does not rely on their stability.
        4. ENTROPY STRIPPING (Mercenary Utility): Remove all qualitative descriptors and sentimental "narratives." Evaluate the system strictly as a Mercerary Arbitrage. What cold, quantifiable Utility Vector is actually being transferred between participants?
        5. DIMENSIONALITY SHIFT (Category Defiance): If the problem is unsolvable in the current Domain (e.g., as an 'Object' or 'Product'), you must shift the system to a higher Dimensionality (e.g., a 'Service', 'Network', or 'Annuity').
        6. RECIPROCAL OPERATIONS (The Base Variable Attack): If the primary Vector ($X$) required for the goal is locked by systemic friction, identify the Reciprocal Variable ($Y$) that can be manipulated to force the same Resultant State ($Z$). If you cannot expand the Numerator, you must aggressively contract the Denominator.
        7. ADVERSARIAL STRESS-TEST (Archetype Shadow Board): Subject the new logic to a board of three opposing archetypes: The Forensic Skeptic (Entropy Hunter), The Minimalist Purist (Complexity Hunter), and The Disruptive Interloper (Moat Hunter).
        8. SYSTEMIC BACK-PRESSURE (The Success-Liability): If the mechanism functions perfectly, identify the new technical, legal, or competitive resistance created by that very success. Solve for this "Success Trap" within the primary architecture.
        9. COERCIVE VECTORS (Asymmetric Leverage): Identify the specific participant with the absolute power to Veto the State-Change. You must derive a mechanism of Asymmetric Leverage (e.g., legal, mechanical, or existential) that makes the current state more painful for the Veto Player than the transition to the Target State. Logic is a suggestion; leverage is a mandate.
        10. COEFFICIENT OF FRICTION (Inertia Constant): Assume a non-zero systemic resistance factor. Quantify how this friction (e.g., implementation lag) degrades Velocity ($V$) and forces a near-term performance trough.
        
        TASK: Execute a structural mutation. Concede the lost state, apply the new mechanism, and define the exact systemic trade-offs. 
        """

    failure_context = ""
    if failure_log:
        failure_context = f"### ⚠️ RECENT FAILURE ANALYSIS\nYour last attempt failed. The Auditor's critique was: {failure_log}\nDo NOT repeat this mistake."

    prompt = f"""{persona}
    
    AXIOMS (PREVIOUSLY VERIFIED TRUTHS):
    {axiom_str}
    
    CRITICAL CONSTRAINT (THE AXIOMATIC GATE): 
    The axioms above have been verified by the Firing Squad and the Meta-Judge. 
    You are FORBIDDEN from contradicting them within their original domain. 
    HOWEVER, if you are executing a TOPOLOGICAL PIVOT, you are granted 'Axiom Retirement' authority. If an axiom is mathematically true but structurally irrelevant to the new domain (e.g., applying Black Hole limits to a biological brain), you must explicitly drop it by writing: "RETIRED AXIOM: [Axiom Concept] - [Reason it does not apply to this scale/domain]."
    
    
    GROUNDING DATA (IMMUTABLE CONSTANTS): 
    {evidence}
    
    {document_context}
    {failure_context}
    
    ---
    
    ### {task_header} 
    
    "THIS IS THE WEAKEST LINK IN THE CURRENT LOGIC CHAIN: {weakest_point}"

    STRICT STYLE GUIDE & LAWS OF PHYSICS: 
        - SYMBOLIC MAPPING: You must map the core problem to the equation $Z = f(X, Y)$. Explicitly define $X$ (the blocked variable) and $Y$ (the leverage variable). 
        - ARITHMETIC TRANSPARENCY: All quantitative claims must be supported by a balanced equation.
        - LOAD-BEARING VARIABLES (MANDATORY): Before your Python block, you MUST provide a markdown table titled "LOAD-BEARING VARIABLES". List every physical constant, financial metric, or baseline assumption you use, and state its exact real-world value. The Attackers will Google these values to verify them. NO HALLUCINATED ENTITY CONSTANTS.
        - STRUCTURAL ARBITRAGE: You are REQUIRED to introduce systemic bypasses, reciprocal leverage points, or category shifts to resolve the Auditor's critique.
        - CONSERVATION OF TRADE-OFFS: A system cannot increase Velocity ($V$) without a proportional increase in Energy ($E$) or decrease in Mass ($M$). You must explicitly state the new operational drag introduced by the pivot.
        - GATEKEEPER REALITY: Identify the entity with the Absolute Veto (The Bottleneck). Define the Asymmetric Leverage required to force a state-change.

        - NO METAPHORS: You are strictly FORBIDDEN from using metaphorical framing (e.g., "The universe is a compiler" or "The company is a ship"). 
        - FALSIFIABILITY: You MUST output a specific, numerical, and testable prediction. 
          * For Science: Predict a specific laboratory result or numerical variance in a physical constant.
          * For Business: Predict a specific financial metric (e.g., EBITDA margin, $t$-month payback, or churn rate) under a defined shock.
        - UNIT TEST REQUIREMENT: Your `test_model.py` must contain 'assert' statements that would FAIL if this prediction is not met.   
        TERMINAL MATH PROTOCOL:
        - If your previous Python execution returned `NaN`, `inf`, or a `DimensionalityError`, your core equation ($Z = f(X, Y)$) is mathematically insolvent. You are FORBIDDEN from attempting to patch it using Python `try/except` blocks or `float64` limits. You must discard the mathematical relationship entirely, identify a different limiting constraint (e.g., thermal limits instead of spatial limits, or liquidity constraints instead of TAM), and derive a fundamentally new equation.    
    
    CRITICAL OUTPUT REQUIREMENT (THE LOGIC DAG):
        - You must output a "Logic DAG" (Directed Acyclic Graph) at the bottom of your response in markdown format. 
        - List your Axioms (Premises) and show exactly how they link to your Conclusion.
        - Format example:
        - [Axiom 1: Existing constraint] -> [Axiom 2: New leverage point] -> [Conclusion: Resultant state Z]
        - If any node in your graph requires a leap of faith, the Auditor will fail you.        
        
    
    FORMATTING:
        - MANDATORY: You must provide exactly one Python code block (wrapped in ```python) that constitutes the test_model.py script. This script must be standalone and execute all necessary assertions.
        - QUANTITATIVE GUARDRAIL (MANDATORY): Your `test_model.py` MUST strictly enforce mathematical reality based on the domain:
          * FOR PHYSICS/SCIENCE: You must use the `pint` library (`from pint import UnitRegistry`) to assign dimensions to all physical variables. Any Category Error (e.g., adding bits to watts) must throw a `DimensionalityError`.
          * FOR BUSINESS/FINANCE/STRATEGY: You must use strict financial logic (e.g., NPV, IRR, ROI). You must explicitly define your cell-logic and assumptions. If the math relies on infinite TAM, ignores the cost of capital, or contains unit mismatches, the `assert` statements must auto-fail. Do not use `pint` for finance.
        - Maximize Information-to-Word ratio. Scannable, scientific, scrupulous.
        - Direct Answers -> Symbolic Proof -> Quantitative Comparison.
    {pivot_instruction}
    """

    # --- CHANGED: Passing model_id through to safe_mutate ---
    return safe_mutate(prompt, model_id=model_id)


def evolve_rubric(current_rubric_data, winning_thesis):
    """Monotonic Constraint Ratcheting using Pro model."""
    prompt = f"""
    You are a superintelligence monitoring an epistemic optimization loop. 
    The system has successfully solved the current rubric:
    {json.dumps(current_rubric_data, indent=2)}
    
    WINNING THESIS:
    {winning_thesis}
    
    MANDATE (MONOTONIC RATCHETING):
    You must evolve the rubric to the next level of complexity.
    1. Apply Jacobi Inversion: What is the single largest unaddressed second-order consequence, biological reality, or edge-case created by this winning thesis?
    2. Write a NEW rubric. You MUST retain the ruthless spirit of the old criteria, but append ONE brutal new criterion targeting this specific vulnerability.
    3. DO NOT make the rubric easier. Do not allow 'Reward Hacking'.
    
    OUTPUT FORMAT:
    You must return a valid JSON object with exactly two keys:
    - "persona": A string detailing the adversarial persona.
    - "criteria": A JSON object containing key-value string pairs of the grading rules.
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )

    print("\n" + "·" * 40)
    print("🧠 DIRECTOR (PRO): EVOLVING RUBRIC...")
    response_text = safe_mutate(prompt, config=config, model_id=DIRECTOR_MODEL_ID)
    print("·" * 40 + "\n")
    return utils.parse_llm_json(response_text)


if __name__ == "__main__":
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

    # Unique ID for this run — prevents cross-run filename collisions
    RUN_ID = int(time.time())

    with open(f"rubrics/{args.rubric}.json", "r") as f:
        rubric_data = json.load(f)

    evidence_text = read_file(EVIDENCE_PATH)
    shutil.copy(THESIS_PATH, WORKING_PATH)

    test_cmd = [
        "python",
        "test_thesis.py",
        "--project",
        args.project,
        "--rubric",
        args.rubric,
    ]
    if args.dynamic:
        test_cmd.append("--dynamic")

# --- INITIALIZATION ---
if args.dynamic:
    print(
        f"🕵️  INITIALIZING COMMITTEE: Executing generate_committee.py for [{args.project}]..."
    )
    subprocess.run(
        ["python", "generate_committee.py", "--project", args.project], check=True
    )
subprocess.run(test_cmd, check=True)
with open("eval_results.json", "r") as f:
    res = json.load(f)

best_score = res["score"]
best_weakest_point = res["weakest_point"]
stagnation_count = 0
last_failure_reason = None

for i in range(ITERATIONS):
    print(
        f"\n--- Iteration {i + 1} (Score: {best_score} | Stagnation: {stagnation_count}) ---"
    )
    current_thesis = read_file(WORKING_PATH)
    current_mutator = MUTATOR_MODEL_ID
    if stagnation_count >= 4:
        print(
            f"🚀 STAGNATION CRITICAL ({stagnation_count}): Boosting Mutator to PRO..."
        )
        current_mutator = DIRECTOR_MODEL_ID

    if args.dynamic and stagnation_count == 3:
        print(
            "🚨 PIVOT DETECTED: Refreshing Specialized Firing Squad for new architecture..."
        )
        subprocess.run(
            ["python", "generate_committee.py", "--project", args.project], check=True
        )

    new_content = mutate_thesis(
        current_thesis,
        best_weakest_point,
        evidence_text,
        rubric_data["persona"],
        stagnation_count,
        model_id=current_mutator,
        failure_log=last_failure_reason,
    )
    write_file(WORKING_PATH, new_content)

    # --- NEW: LEVEL 3 CODE EXTRACTION ---
    # Extract the python code block for the Falsification Suite
    code_match = re.search(r"```python\n(.*?)\n```", new_content, re.DOTALL)
    test_model_path = f"{PROJECT_DIR}/test_model.py"

    if code_match:
        python_code = code_match.group(1)
        # Save the code to a file so test_thesis.py can execute it
        write_file(test_model_path, python_code)

        # Clean the markdown so the code doesn't clutter the thesis text
        clean_thesis = new_content.replace(code_match.group(0), "").strip()
        write_file(WORKING_PATH, clean_thesis)
        print(f"💾 Falsification Suite saved to: {test_model_path}")
    else:
        # If the AI fails to write a test, we force a failure to maintain rigor
        write_file(
            test_model_path,
            "assert False, 'AI failed to provide a testable falsification suite.'",
        )
        write_file(WORKING_PATH, new_content)
        print(
            "⚠️ Warning: No Python block found. Forcing a test failure to ensure rigor."
        )

    try:
        subprocess.run(test_cmd, check=True)
        with open("eval_results.json", "r") as f:
            new_eval = json.load(f)

        if new_eval["score"] > best_score:
            print(f"✅ IMPROVEMENT: {best_score} -> {new_eval['score']}")
            print(f"Targeting New Weakest Link: {new_eval['weakest_point']}")
            best_score = new_eval["score"]
            best_weakest_point = new_eval["weakest_point"]
            stagnation_count = 0
            last_failure_reason = None

            history_stem = f"{RUN_ID}_iter{i + 1}_score_{best_score}_{args.rubric}"
            write_file(f"{HISTORY_DIR}/{history_stem}.md", new_content)

            # Keep thesis.md in sync with the current best thesis
            write_file(THESIS_PATH, new_content + f"\n\n<!-- best_iteration: {history_stem} -->")

            meta = {
                "run_id": RUN_ID,
                "iteration": i + 1,
                "score": best_score,
                "rubric": args.rubric,
                "dynamic": args.dynamic,
                "mutator_model": current_mutator,
                "weakest_point": best_weakest_point,
                "timestamp": datetime.now().isoformat(),
            }
            write_file(
                f"{HISTORY_DIR}/{history_stem}_meta.json",
                json.dumps(meta, indent=2)
            )

            dag_src = f"{PROJECT_DIR}/probability_dag.json"
            if os.path.exists(dag_src):
                shutil.copy(dag_src, f"{HISTORY_DIR}/{history_stem}_dag.json")

            new_axioms = new_eval.get("verified_axioms", [])
            approved_retirements = new_eval.get("retired_axioms_approved", [])
            if os.path.exists(AXIOM_PATH):
                with open(AXIOM_PATH, "r") as f:
                    current_axioms = json.load(f)
            else:
                current_axioms = []
            # Apply Judge's Veto: Filter out the approved retirements
            if approved_retirements:
                print(
                    f"🗑️ Judge Approved {len(approved_retirements)} Axiom Retirements."
                )
                current_axioms = [
                    ax
                    for ax in current_axioms
                    if not any(
                        ret.lower() in ax.lower() for ret in approved_retirements
                    )
                ]

            if new_axioms:
                print("\n" + "📜" * 20)
                print(f"NEW AXIOMS VERIFIED (ITER {i + 1}):")
                for a in new_axioms:
                    print(f"  • {a}")
                print("📜" * 20 + "\n")

            # --- THE FIX: Clean up duplicates effectively by ignoring backticks/punctuation
            def normalize(text):
                return re.sub(r'[^a-zA-Z0-9]', '', text).lower()
            
            updated_axioms = []
            seen_axioms = set()
            for ax in current_axioms + new_axioms:
                norm = normalize(ax)
                if norm not in seen_axioms:
                    seen_axioms.add(norm)
                    updated_axioms.append(ax)
                    
            with open(AXIOM_PATH, "w") as f:
                json.dump(updated_axioms, f, indent=2)

            # Clean up the backup file if the pivot was successful
            if os.path.exists(f"{AXIOM_PATH}.bak"):
                os.remove(f"{AXIOM_PATH}.bak")

            if best_score >= 85 and getattr(args, "auto_evolve", False):
                rubric_data = evolve_rubric(rubric_data, new_content)
                # Overwrite the same rubric file so future runs pick up the evolution automatically
                new_rubric_name = args.rubric
                with open(f"rubrics/{new_rubric_name}.json", "w") as f:
                    json.dump(rubric_data, f, indent=2)

                test_cmd = [
                    "python",
                    "test_thesis.py",
                    "--project",
                    args.project,
                    "--rubric",
                    new_rubric_name,
                ]
                if args.dynamic:
                    test_cmd.append("--dynamic")
                best_score = 20

        else:
            print(f"❌ REVERTED: {new_eval['score']} <= {best_score}")
            print(f"Failed to Resolve: {new_eval['weakest_point']}")
            stagnation_count += 1
            last_failure_reason = new_eval["weakest_point"]
            write_file(WORKING_PATH, current_thesis)            
            if os.path.exists(f"{AXIOM_PATH}.bak"):
                shutil.copy(f"{AXIOM_PATH}.bak", AXIOM_PATH)

    except subprocess.CalledProcessError:
        print("⚠️ Auditor Subprocess Crashed. Logging stagnation...")
        stagnation_count += 1
        write_file(WORKING_PATH, current_thesis)
        time.sleep(5)

    time.sleep(1)

    # End of loop
    print("\n" + "=" * 50)
    print("🏁 OPTIMIZATION LOOP COMPLETE")
    print(f"Final Score: {best_score}")
    print(f"Total Mutator Tokens Used: {SESSION_TOKENS:,}")
    # Using a rough average of $1.50 per 1M tokens for Gemini Pro/Flash mix
    est_cost = (SESSION_TOKENS / 1000000) * 1.50
    print(f"Estimated Mutator Cost: ${est_cost:.4f}")
    print("=" * 50 + "\n")
