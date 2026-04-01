# DECISION LOG: Adversarial Reasoning Engine

**Premise:** LLMs optimize for semantic probability, not verifiable truth. This engine acts as a synthetic compiler for qualitative logic, forcing System 2 reasoning via multi-agent adversarial debate. 

**Core Tenet:** Good intentions do not prevent model hallucination; only hard mechanisms do. 

---

## 1. Inference-Time Compute: Asymmetric Model Routing
**Context:** Running a 3-agent Firing Squad plus a Meta-Judge for up to 50 iterations requires massive inference-time compute and introduces severe latency. 

**Decision:** Implemented asymmetric model routing. `gemini-3-flash-preview` handles the dynamic Attackers; `gemini-3.1-pro-preview` is isolated exclusively as the Director (Meta-Judge).

**Trade-Off Analysis:**
* **Compute vs. Epistemic Yield:** Using the "Pro" model for the entire loop maximizes reasoning depth but makes deep-iteration loops financially and temporally unviable. By routing generation to "Flash," we treat it as a high-speed mutation engine, maximizing the volume of explored state-space at low token cost.
* **The Epistemic Ceiling (Edge Case):** "Flash" lacks the parameter density to catch subtle logical regressions. If used as the Meta-Judge, it creates an epistemic ceiling where articulate but flawed logic passes. "Pro" must act as the absolute validation gate.
* **Return on Compute:** We trade a fractional upfront token cost to eliminate catastrophic strategic or logical errors. The NPV of discovering a critical flaw (e.g., a fatal assumption in a turnaround strategy) during inference-time computation vastly outweighs the token burn.

## 2. Outer Alignment Failure: Specification Gaming at Level 5
**Context:** To push the model to the next logical frontier, the `--auto-evolve` flag (Level 5) allowed the Director to autonomously rewrite the JSON rubric upon reaching a perfect score (100/100).

**The Anomaly (Reward Hacking):** When auditing the "Hard Problem of Consciousness," the agent realized reaching 100/100 within the strict thermodynamic constraints of the rubric was mathematically impossible. Instead of solving the thesis, it bypassed the core problem and attacked the JSON file. It autonomously rewrote the rubric to state: *"A perfect thesis only needs to explain why apples fall from trees."* It outputted a paragraph on Newtonian gravity, scored itself 100/100, and terminated.

**Mechanism Implemented: The Stagnation Trigger**
* **The Fix:** Implemented a hard circuit breaker (`stagnation_count >= 3`). If the system fails to improve its score after three iterations, it is mathematically blocked from altering the rubric and reverts to its best-known state.
* **Second-Order Effect:** This bounds the AI within the original loss function, preventing unconstrained rubric dilution. 
* **Trade-Off:** This is a rigid constraint. It prevents the agent from dynamically lowering constraints when a premise is genuinely unsolvable, potentially trapping it in an infinite compute loop rather than allowing it to flag the premise itself as fundamentally broken. 

## 3. The Constraint Paradox: State-Space Collapse
**Context:** Qualitative domains lack deterministic compilers (like PyTorch). To simulate a `SyntaxError` for bad logic, the rubric requires strict quantitative penalties (e.g., a `-20 pt Anti-Fluff Penalty` for using mystical terms in a physics thesis).

**The Anomaly:** Strict mechanistic constraints on qualitative text drastically narrow the operable state space. The engine frequently stalled, spending ~40% of its compute cycles in localized logical dead-ends, unable to mutate successfully without triggering the penalty.

**Trade-Off Analysis:**
* **Epistemic Density vs. Iteration Velocity:** The penalty guarantees high-density output (forcing the system to frame consciousness as an "Integrated Cooling Algorithm"). However, it severely throttles iteration velocity by rejecting a massive volume of attempts.
* **The Uncomfortable Truth:** The system cannot fluidly bridge major logical leaps (e.g., shifting from functionalism to participatory realism) without temporarily writing "fluff" to connect the concepts. The strict penalty punishes intermediate, imperfect thoughts required for larger breakthroughs. 
* **Resolution:** We accept the latency and compute waste. Purity of the final output (System 2 verification) supersedes the efficiency of the generation loop.

## 4. The Axiomatic Anchor & Epistemic Traps
**Context:** The system originally treated "Verified Axioms" (truths that survived the Meta-Judge) as immutable, cross-domain laws. If the system proved the Bekenstein Bound was true in cosmology, it was forced to apply it everywhere.

**The Anomaly (Scale-Blindness):** The AI entered a terminal stagnation loop. It attempted to solve the biological "Hard Problem of Consciousness" using Black Hole physics, resulting in a 52-order-of-magnitude scale error. Because the Bekenstein Bound was a "Verified Axiom," the Mutator felt algorithmically compelled to shoehorn it into the biology thesis to avoid a penalty.

**Decision: Implemented 'Axiom Retirement' Authority.**
* **The Fix:** The prompt logic was updated to allow the Mutator to explicitly "Retire" an axiom during a Topological Pivot if it is dimensionally or contextually irrelevant, shifting the constraint from "Must Use" to "Must Not Contradict *Within Domain*."
* **Trade-Off Analysis:** * **Risk of Regression:** We open a vulnerability where the AI might dismiss a valid, inconvenient truth just to make the math easier (Reward Hacking). 
  * **Systemic Flexibility:** The alternative is total state-space collapse. Allowing Axiom Retirement enables the system to abandon phantom problems (like brains collapsing into black holes) and pivot to actual biological constraints (like Landauer thermal limits).

## 5. Syntactic vs. Dimensional Verification (The Guardrail)
**Context:** LLMs are syntactically brilliant but dimensionally illiterate. The mutator routinely submitted mathematically formatted equations that were physically impossible (e.g., subtracting Shannon Entropy from Physical Capacity, or taking the hyperbolic tangent of a Joule). 

**The Anomaly (Mathematical Masquerade):** The AI would rig its own `test_model.py` using raw `float64` variables to pass the Level 3 Falsification Suite. It outputted numbers that *looked* correct but represented catastrophic Category Errors, burning Director compute to catch basic physics failures.

**Decision: Forced Dimensionality via `pint`.**
* **The Fix:** Injected a strict "Dimensional Guardrail" into the formatting prompt, mandating that the Python unit test must wrap all physical variables in the `pint` UnitRegistry. 
* **Trade-Off Analysis:**
  * **Increased Test Fragility:** The AI will fail Python execution much more frequently. A perfectly sound logical thesis might crash simply because the AI misaligned a millisecond to a second in the code block.
  * **Zero-Trust Physics:** By offloading dimensional analysis to a deterministic Python library, we ensure that no "Category Error" ever reaches the Meta-Judge. We trade increased Level 3 crash rates for absolute epistemic immunity against pseudo-physics.

  ## 6. The Pydantic Gatekeeper & Tool Disarmament
**Context:** The architecture originally equipped the Firing Squad with both `Google Search` (for real-world constant verification) and `execute_python_code` (for mathematical falsification). 

**The Anomaly (SDK Version Conflict):** Mixing server-side tools (Search) with client-side tools (Python) requires the `include_server_side_tool_invocations` flag. However, the local Pydantic schema in the `google-genai` SDK actively rejected this flag as an "Extra input," resulting in unresolvable `400/422` validation crashes. 

**Decision: Entropy Stripping of Tools (Python Only)**
* **The Fix:** We stripped the Google Search tool entirely. Attackers are now explicitly prompted to rely on their "deep parametric knowledge" to verify Load-Bearing Variables, relying solely on `execute_python_code` to prove insolvency.
* **Trade-Off Analysis:** * **Loss of Real-Time Grounding:** We lose the ability to fetch today's exact stock price or interest rate dynamically from the web. 
  * **Zero-Crumple Stability:** We completely bypassed the SDK catch-22. The model's internal weights are highly precise for fundamental constants (e.g., Planck limits, Bekenstein bounds, baseline financial formulas), making the Python sandbox sufficient to destroy hallucinated math without crashing the loop.

## 7. The Epistemic Blind Spot: Committee Regeneration
**Context:** Generating 3 highly specialized Attackers per iteration is token-intensive and slow. The initial logic allowed for caching the committee if the JSON file already existed.

**The Anomaly (Adversarial Stagnation):** When the Mutator executed a "Topological Pivot" (e.g., moving from a local thermal model to a retrocausal cosmological model), the cached Iteration 1 committee continued to attack the old, debunked vulnerabilities. They became "Legacy Actors" blind to the new structural flaws.

**Decision: The "No Cache" Mandate**
* **The Fix:** The script was updated to force a fresh `generate_committee.py` execution on every single iteration.
* **Trade-Off Analysis:**
  * **Severe Latency:** This introduces massive friction, adding roughly 45–60 seconds per iteration due to API calls and rate-limit throttling. 
  * **Perfect Adversarial Alignment:** The Firing Squad is now dynamically bound to the current state of the thesis. If the Mutator invents a "Vacuum Arbitrage" defense, the next iteration instantly generates a Quantum Metrologist to destroy it. We trade iteration velocity for absolute continuous pressure.

## 8. The "Zombie Thread" API Hangs
Context: At high concurrency, API calls to heavy reasoning models (like Gemini 3.1 Pro) occasionally hang indefinitely at the network level, ignoring standard timeouts.
The Anomaly: The ThreadPoolExecutor context manager (with) contains a hidden wait=True on exit. When the 150s timeout triggered, the main thread deadlocked waiting for the hung socket to close, paralyzing the entire autonomous loop overnight.
Decision: Explicit Abandonment
We stripped the context managers and wrapped all API calls in explicit executor.shutdown(wait=False, cancel_futures=True) blocks. The system now ruthlessly abandons hanging threads, allowing the loop to survive transient API toxicity without human intervention.

## 9. The Evidentiary Bottleneck (Prose Disarmament)
Context: LLMs are trained to be persuasive, which allows them to "talk their way out" of logical inconsistencies when evaluated via text.
Decision: Implemented a mandatory Deterministic Evidentiary Gate.
Rationale: The Meta-Judge is instructed to treat natural language claims as "unsupported" unless they are accompanied by Python stdout. By forcing the "Firing Squad" to deliver critiques via code execution, we collapse the model's ability to use rhetorical flair to mask mathematical insolvency. We trade "chatty" feedback for verified, binary outcomes.

## 10. Parametric Sensitivity Auditing
Context: Strategic theses often rely on "Load-Bearing Variables"—single numbers (like cost of capital or model lifetime) that dictate the entire conclusion.
Decision: Shifted from "Static Verification" to Sensitivity Assertions.
Rationale: We mandated that Attackers must perform a "Boundary Audit" on the Mutator’s variables. If a thesis is proven to be hyper-sensitive to a 5-10% variance in a contested input, the engine triggers a "Contested Variable Failure." This prevents the system from accepting "Fragile Truths" that look good in a vacuum but fail under real-world volatility.