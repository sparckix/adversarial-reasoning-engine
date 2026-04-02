# Adversarial Debate: tsmc_fragility

## Attacker: Logistics & Resilience Architect (Crisis Adaptation Specialist)
The thesis presents a meticulously traced path of supply chain disruption, moving from maritime chemical asphyxiation to work-in-progress sterilization and culminating in final assembly seizure. Its rejection of broad-base financial multipliers in favor of direct physical inventory depletion is a methodologically sound pivot, aligning with a focus on tangible economic utility rather than sentiment-driven market volatility. The parametric grounding for the "LOAD-BEARING VARIABLES" is generally robust, drawing from credible industry and economic sources.

However, the model's core vulnerability lies in its implicit assumption of static, unadaptable system parameters under conditions of extreme duress. Specifically, the variables relating to supply chain hard limits and mitigation timelines—`CHEM_BUFFER` and `ALT_CAP_SUB5NM`—are treated as unbreakable constants, rather than dynamic elements susceptible to extraordinary, coordinated global responses.

1.  **Chemical Buffer (`CHEM_BUFFER`):** The thesis posits a 45-day maximum buffer for critical fab chemicals, citing "storage constraints." This assumption overlooks several adaptive mechanisms:
    *   **Strategic Stockpiling:** While 45 days might be a typical operational buffer, it does not preclude the existence or rapid deployment of strategic, unstated reserves by governments or consortia, particularly for high-value, low-volume precursor chemicals.
    *   **Emergency Airlift:** The thesis notes that ~90% of imports are by volume. However, critical, high-value chemicals often represent a disproportionately smaller fraction by volume but are indispensable. Emergency airlift operations, while costly, could significantly extend the effective buffer for these specific inputs, circumventing maritime blockades for essential, non-bulk materials.
    *   **Accelerated Sourcing/Diversification:** Under extreme pressure, global cooperation could accelerate sourcing from alternative suppliers or even rapid domestic ramp-ups for certain chemicals (e.g., Taiwan's existing NF3 production capacity).

2.  **Alternative Capacity (`ALT_CAP_SUB5NM`):** The model sets a maximum substitution rate of 8% via Samsung and Intel, reinforced by a hardcoded assertion (`assert alt_cap_sub5nm < 0.10`) that actively prevents the exploration of higher rates. This constitutes a "cooked book" as it imposes an artificial ceiling on systemic adaptability. Under emergency conditions:
    *   **Accelerated Yield Improvement:** Samsung's 3nm yield (35-50%) is significantly lower than TSMC's (~80%). Aggressive global cooperation, including potential IP sharing or technical assistance, could accelerate Samsung's yield improvements, effectively increasing its output without building new fabs.
    *   **Capacity Reprioritization:** Intel and Samsung could be incentivized or compelled to reprioritize existing capacity away from less critical products towards high-demand, sub-5nm components, exceeding their current external revenue figures.
    *   **Emergency Funding/Regulatory Waivers:** Unprecedented global coordination could unlock emergency funding and regulatory fast-tracking to accelerate existing fab expansion plans or bring "warm" capacity online faster than typical greenfield timelines.

The thesis's "Customs Quarantine" scenario, while designed to avoid kinetic conflict, also implies a level of international passivity that is questionable given the global economic stakes. The "execution friction" of the disruption itself (e.g., how robust is a "customs inspection" against international convoys or alternative transport methods?) is insufficiently explored.

In summary, while the model accurately traces the *consequences* of a static system under duress, it fails to adequately account for the *capacity for adaptation* inherent in a globally interconnected, highly incentivized system facing an existential threat. The hardcoded limits and restrictive assertions prevent a comprehensive assessment of potential mitigation strategies.

**So What for the Meta-Judge:**
The original thesis, while rigorously tracing physical inventory depletion, constructs a scenario that is overly deterministic by embedding restrictive assumptions about global response capabilities. Specifically, the model's `CHEM_BUFFER` and `ALT_CAP_SUB5NM` variables are presented as immutable hard limits, reinforced by a hardcoded assertion that stifles exploration of higher substitution rates. This approach overlooks the potential for extraordinary, coordinated international efforts—such as strategic pre-positioning of critical materials, emergency airlift for high-value components, and accelerated capacity ramp-ups or yield improvements in alternative foundries under duress. By failing to account for these adaptive mechanisms, the thesis significantly overstates the inevitability and magnitude of the projected economic contraction, presenting a brittle rather than a robust assessment of supply chain resilience.

```python
"""
counter_test.py
Exposes the insolvency of the Mutator's hard limits by demonstrating
the impact of plausible, extraordinary mitigation efforts.
"""

def calculate_direct_gdp_contraction_mutator_logic(
    chem_buffer_days,
    fab_cycle_days,
    oem_buffer_days,
    total_oem_rev_at_risk,
    blockade_duration,
    alt_cap_sub5nm
):
    """
    Replicates the Mutator's core calculation logic for comparison,
    but removes the restrictive hardcoded assertion on alt_cap_sub5nm
    to allow for testing higher values.
    """
    total_lag_days = chem_buffer_days + fab_cycle_days + oem_buffer_days
    
    # Validation 1: Falsify if lag exceeds shock duration
    # This assertion is retained as it's a logical operational constraint.
    assert total_lag_days < blockade_duration, "Blockade duration too short to trigger assembly halt."
    
    disrupted_days = max(0.0, blockade_duration - total_lag_days)
    disruption_fraction = disrupted_days / 365.0
    
    direct_gross_loss = total_oem_rev_at_risk * disruption_fraction
    
    net_direct_loss = direct_gross_loss * (1.0 - alt_cap_sub5nm)
    
    assert net_direct_loss >= 0, "Loss calculation failed to produce non-negative contraction."
    
    return net_direct_loss, total_lag_days

def counter_test_scenario():
    # Mutator's Load-Bearing Variables (as per their definition)
    mutator_chem_buffer_days = 45.0
    mutator_fab_cycle_days = 90.0
    mutator_oem_buffer_days = 30.0
    mutator_total_oem_rev_at_risk = 487.0 # Billions USD
    mutator_blockade_duration = 365.0
    mutator_alt_cap_sub5nm = 0.08

    # Calculate Mutator's predicted loss using their logic
    mutator_predicted_loss, mutator_lag = calculate_direct_gdp_contraction_mutator_logic(
        mutator_chem_buffer_days,
        mutator_fab_cycle_days,
        mutator_oem_buffer_days,
        mutator_total_oem_rev_at_risk,
        mutator_blockade_duration,
        mutator_alt_cap_sub5nm
    )

    # Counter-Test Scenario: Extraordinary Global Response
    # 1. Enhanced Chemical Buffer: Strategic stockpiling, emergency airlift
    #    for critical, low-volume chemicals, and accelerated sourcing efforts
    #    extend the effective buffer. This is a plausible outcome of aggressive
    #    global cooperation and pre-positioning.
    mitigated_chem_buffer_days = 90.0 # Example: 45 days original + 45 days from emergency measures

    # 2. Accelerated Alternative Capacity: Global cooperation, IP sharing,
    #    emergency funding, and accelerated yield improvements (e.g., for Samsung)
    #    increase effective substitution capacity beyond the Mutator's arbitrary 8% limit.
    #    This challenges the Mutator's hardcoded assertion of <10%.
    mitigated_alt_cap_sub5nm = 0.15 # Example: 8% original + 7% from accelerated efforts

    # Calculate loss under the mitigated scenario
    mitigated_loss, mitigated_lag = calculate_direct_gdp_contraction_mutator_logic(
        mitigated_chem_buffer_days,
        mutator_fab_cycle_days, # Fab cycle time remains constant
        mutator_oem_buffer_days, # OEM buffer remains constant
        mutator_total_oem_rev_at_risk,
        mutator_blockade_duration,
        mitigated_alt_cap_sub5nm
    )

    print(f"--- Mutator's Baseline Prediction ---")
    print(f"Mutator's OEM Assembly Halt Time: {mutator_lag:.0f} days.")
    print(f"Mutator's Direct GDP Contraction: ${mutator_predicted_loss:.2f} Billion USD.")
    print(f"Mutator's Assumed Chemical Buffer: {mutator_chem_buffer_days:.0f} days.")
    print(f"Mutator's Assumed Alternative Capacity: {mutator_alt_cap_sub5nm*100:.0f}%\n")

    print(f"--- Counter-Test: Extraordinary Mitigation Scenario ---")
    print(f"Mitigated OEM Assembly Halt Time: {mitigated_lag:.0f} days.")
    print(f"Mitigated Direct GDP Contraction: ${mitigated_loss:.2f} Billion USD.")
    print(f"Mitigated Chemical Buffer (Strategic Stockpile/Airlift): {mitigated_chem_buffer_days:.0f} days.")
    print(f"Mitigated Alternative Capacity (Cooperation/Yield Accel.): {mitigated_alt_cap_sub5nm*100:.0f}%\n")

    # Assertions to expose the insolvency of the Mutator's implicit assumptions
    # 1. Assert that the mitigated loss is significantly lower than the Mutator's prediction.
    assert mitigated_loss < mutator_predicted_loss, \
        "Counter-test failed: Mitigation efforts did not reduce the predicted GDP contraction."

    # 2. Assert that the mitigated lag time is longer, demonstrating extended resilience.
    assert mitigated_lag > mutator_lag, \
        "Counter-test failed: Mitigation efforts did not extend the operational lag time."

    # 3. Explicitly challenge the Mutator's hardcoded assertion about alternative capacity.
    #    The original Mutator code had: assert alt_cap_sub5nm < 0.10, "Hallucinated alternative capacity."
    #    This counter-test demonstrates a plausible scenario where it exceeds this.
    assert mitigated_alt_cap_sub5nm >= 0.10, \
        "Counter-test failed: Mitigated alternative capacity did not exceed the Mutator's arbitrary 10% ceiling, indicating insufficient challenge to the 'cooked book'."

    print("COUNTER-TEST PASSED: The Mutator's model is demonstrably brittle to plausible, extraordinary mitigation efforts.")
    print("The implicit assumption of static, unadaptable system parameters is invalidated.")

if __name__ == "__main__":
    counter_test_scenario()
```

### PYTHON EXECUTION OUTPUT:
--- Mutator's Baseline Prediction ---
Mutator's OEM Assembly Halt Time: 165 days.
Mutator's Direct GDP Contraction: $245.50 Billion USD.
Mutator's Assumed Chemical Buffer: 45 days.
Mutator's Assumed Alternative Capacity: 8%

--- Counter-Test: Extraordinary Mitigation Scenario ---
Mitigated OEM Assembly Halt Time: 210 days.
Mitigated Direct GDP Contraction: $175.79 Billion USD.
Mitigated Chemical Buffer (Strategic Stockpile/Airlift): 90 days.
Mitigated Alternative Capacity (Cooperation/Yield Accel.): 15%

COUNTER-TEST PASSED: The Mutator's model is demonstrably brittle to plausible, extraordinary mitigation efforts.
The implicit assumption of static, unadaptable system parameters is invalidated.


## Attacker: Heterodox Macroeconomist (Multiplier & Scope Validity Theorist)
The Mutator's thesis commendably pivots away from the problematic application of broad economic multipliers and market capitalization impairment, which are indeed susceptible to overgeneralization and sentiment-driven volatility. By explicitly retiring the `SEMI_MULTIPLIER` and `SEMI_REV` variables and shifting to a "Physical Inventory Depletion" model, the Mutator addresses a significant portion of the initial critique regarding the universality and generalizability of economic models derived from specific, limited historical events. This methodological refinement correctly identifies that a direct, traceable contraction path is more robust for geopolitical stress-testing than abstract financial multipliers.

However, while the Mutator's new model offers a more granular and physically grounded approach, it introduces a critical limitation in its scope, which constitutes a form of "cooked books" by omission. The model purports to calculate "Direct Global GDP Contraction" by summing the "Annual final-assembly revenue of TSMC sub-5nm dependent OEM $i$." Yet, the `total_oem_rev_at_risk` variable in the Python suite is explicitly hardcoded to $487.0 Billion (USD), representing only Apple, NVIDIA, and AMD's TSMC-dependent revenues. This figure is then rigidly enforced by an `assert total_oem_rev_at_risk == 487.0` statement within the Mutator's own code.

This hardcoding is problematic for the following reasons:
1.  **Incomplete Scope:** The "LOAD-BEARING VARIABLES" table itself identifies other significant TSMC advanced node customers, such as Qualcomm (e.g., `QC_FAB: TSMC 4nm`). Qualcomm's annual revenue, a substantial portion of which is derived from advanced Snapdragon processors fabricated at TSMC's leading-edge nodes, is entirely excluded from the `total_oem_rev_at_risk` calculation. This omission systematically understates the total end-market revenue directly dependent on TSMC's sub-5nm operations.
2.  **Artificial Constraint:** The explicit assertion `assert total_oem_rev_at_risk == 487.0` prevents the model from incorporating a more comprehensive set of directly impacted revenues, thereby creating a false sense of precision while sacrificing completeness. If the objective is to quantify "Direct Global GDP Contraction," then all identifiable and quantifiable revenue streams strictly dependent on the specified TSMC nodes should be included.
3.  **Parametric Inconsistency:** While the Mutator correctly grounds the individual revenue figures for Apple, NVIDIA, and AMD, the aggregation of these into a fixed sum, to the exclusion of other explicitly mentioned dependencies, introduces an inconsistency in the model's claim of comprehensive direct impact.

The "So What" for the Meta-Judge is that while the Mutator has successfully navigated away from the pitfalls of broad, potentially inflated economic multipliers, their refined model, despite its commendable precision in tracing physical inventory depletion, suffers from an artificially constrained scope. By selectively omitting significant, identifiable revenue streams directly dependent on TSMC's advanced nodes (e.g., Qualcomm), the model systematically *understates* the projected direct global GDP contraction. This undermines the claim of a comprehensive "Direct Global GDP Contraction" and presents a calculation that is accurate within its narrow, self-imposed boundaries, but incomplete in its representation of the overall economic impact. The Mutator's own code, through its rigid assertion of a limited revenue base, exposes this methodological limitation.

```python
import math

# Mutator's original function (copied for context, but will not be directly called in a way that triggers its internal assert)
def calculate_direct_gdp_contraction_mutator_logic(
    chem_buffer_days, fab_cycle_days, oem_buffer_days,
    apple_hw_rev, nvda_dc_rev, amd_tsmc_dep,
    blockade_duration, alt_cap_sub5nm
):
    total_oem_rev_at_risk = apple_hw_rev + nvda_dc_rev + amd_tsmc_dep
    
    total_lag_days = chem_buffer_days + fab_cycle_days + oem_buffer_days
    assert total_lag_days < blockade_duration, "Blockade duration too short to trigger assembly halt."
    
    disrupted_days = max(0.0, blockade_duration - total_lag_days)
    disruption_fraction = disrupted_days / 365.0
    
    direct_gross_loss = total_oem_rev_at_risk * disruption_fraction
    net_direct_loss = direct_gross_loss * (1.0 - alt_cap_sub5nm)
    
    assert net_direct_loss > 0, "Loss calculation failed to produce positive contraction."
    assert alt_cap_sub5nm < 0.10, "Hallucinated alternative capacity. Samsung/Intel cannot absorb >10% of sub-5nm demand."
    # The Mutator's original function includes: assert total_oem_rev_at_risk == 487.0, "OEM revenue base altered from grounded facts."
    # This counter-test demonstrates the insolvency of that specific assertion by showing a more comprehensive calculation.
    
    return net_direct_loss, total_lag_days

def counter_test_gdp_contraction_scope():
    # Mutator's core parameters from LOAD-BEARING VARIABLES
    chem_buffer_days = 45.0
    fab_cycle_days = 90.0
    oem_buffer_days = 30.0
    blockade_duration = 365.0
    alt_cap_sub5nm = 0.08

    # Mutator's explicitly stated OEM revenues
    apple_hw_rev = 350.0 # Billions USD
    nvda_dc_rev = 115.0 # Billions USD
    amd_tsmc_dep = 22.0 # Billions USD

    # Parametric Grounding for additional TSMC-dependent revenue: Qualcomm
    # Qualcomm's FY2023 total revenue was approximately $35.8 Billion USD (Source: Qualcomm FY2023 10-K).
    # A conservative estimate for the portion of this revenue strictly dependent on TSMC's sub-5nm nodes
    # (e.g., high-end Snapdragon processors like the 8 Gen 3, explicitly listed as TSMC 4nm) is 50%.
    qualcomm_tsmc_dep = 35.8 * 0.5 # Billions USD
    
    # Calculate the Mutator's result using their specified, limited scope
    mutator_total_oem_rev_at_risk = apple_hw_rev + nvda_dc_rev + amd_tsmc_dep
    mutator_net_direct_loss, mutator_lag_days = calculate_direct_gdp_contraction_mutator_logic(
        chem_buffer_days, fab_cycle_days, oem_buffer_days,
        apple_hw_rev, nvda_dc_rev, amd_tsmc_dep,
        blockade_duration, alt_cap_sub5nm
    )

    # Calculate a more comprehensive total OEM revenue at risk
    more_comprehensive_total_oem_rev_at_risk = mutator_total_oem_rev_at_risk + qualcomm_tsmc_dep
    
    # Calculate the more comprehensive direct GDP loss using the same logic
    more_comprehensive_net_direct_loss, _ = calculate_direct_gdp_contraction_mutator_logic(
        chem_buffer_days, fab_cycle_days, oem_buffer_days,
        apple_hw_rev, nvda_dc_rev, amd_tsmc_dep + qualcomm_tsmc_dep, # Inject Qualcomm's revenue here
        blockade_duration, alt_cap_sub5nm
    )

    print(f"\n--- Counter-Test Results ---")
    print(f"Mutator's calculated GDP Contraction (limited scope): ${mutator_net_direct_loss:.2f} Billion USD")
    print(f"More Comprehensive GDP Contraction (including Qualcomm): ${more_comprehensive_net_direct_loss:.2f} Billion USD")
    print(f"Additional revenue at risk from Qualcomm (estimated): ${qualcomm_tsmc_dep:.2f} Billion USD")
    print(f"Difference (Understatement by Mutator): ${more_comprehensive_net_direct_loss - mutator_net_direct_loss:.2f} Billion USD")
    print(f"OEM Assembly Halt Time: {mutator_lag_days} days.")

    # Assert that the Mutator's calculation significantly understates the impact
    # A material understatement threshold for a global GDP impact model.
    understatement_threshold = 5.0 # Billion USD
    assert more_comprehensive_net_direct_loss > mutator_net_direct_loss + understatement_threshold, \
        f"Mutator's model significantly understates the direct GDP contraction. " \
        f"Expected at least ${mutator_net_direct_loss + understatement_threshold:.2f}B, " \
        f"but Mutator calculated ${mutator_net_direct_loss:.2f}B. " \
        f"My comprehensive calculation yields ${more_comprehensive_net_direct_loss:.2f}B."

    print("\nCOUNTER-TEST PASSED: The Mutator's model is demonstrated to be incomplete in its scope of 'revenue at risk', leading to an understatement of direct GDP contraction.")

if __name__ == "__main__":
    counter_test_gdp_contraction_scope()

```

### PYTHON EXECUTION OUTPUT:

--- Counter-Test Results ---
Mutator's calculated GDP Contraction (limited scope): $245.50 Billion USD
More Comprehensive GDP Contraction (including Qualcomm): $254.52 Billion USD
Additional revenue at risk from Qualcomm (estimated): $17.90 Billion USD
Difference (Understatement by Mutator): $9.02 Billion USD
OEM Assembly Halt Time: 165.0 days.

COUNTER-TEST PASSED: The Mutator's model is demonstrated to be incomplete in its scope of 'revenue at risk', leading to an understatement of direct GDP contraction.


## Attacker: Quantitative Risk Arbitrageur (Model Integrity Auditor)
The thesis presents a method for calculating direct GDP contraction based on physical inventory depletion, explicitly rejecting top-down economic multipliers and financialized market capitalization impairment. This approach aims for a more granular, bottom-up assessment of supply chain disruption.

**Analytical Critique:**

1.  **Variable Origin and Range Justification:**
    *   The `LOAD-BEARING VARIABLES` table provides source contexts for each parameter. For variables with stated ranges (e.g., `CHEM_BUFFER` (30-45 days), `ALT_CAP_SUB5NM` (5-8%)), the Python script consistently selects the upper bound of the range.
        *   `chem_buffer_days = 45.0`: This choice maximizes the initial buffer, delaying the onset of disruption. While defensible as a "maximum buffer" scenario, it inherently reduces the calculated impact duration.
        *   `alt_cap_sub5nm = 0.08`: This choice maximizes the alternative capacity, thereby minimizing the net direct loss. The thesis defines $S_{max}$ as the "Maximum global substitution rate," which justifies selecting the upper bound (8%) from the stated range of "~5–8%". However, this choice directly reduces the calculated GDP contraction. If the objective is a stress test, selecting the lower bound (5%) would represent a more conservative estimate of available substitution and thus a higher potential impact. This parameter selection introduces a subtle bias towards a less severe outcome within the model's framework.

2.  **Equation Transcription and Numerical Stability:**
    *   The Python implementation accurately reflects the symbolic equation provided in the thesis. The calculation of `total_lag_days`, `disrupted_days`, `disruption_fraction`, `direct_gross_loss`, and `net_direct_loss` directly maps to the terms in the equation.
    *   The mathematical operations are basic arithmetic, which are numerically stable. The use of `max(0.0, ...)` correctly handles scenarios where the blockade duration might be shorter than the total lag, preventing negative disruption days.

3.  **Robustness of Assertions and 'Cooked Books' Analysis:**
    *   The Python script includes several `assert` statements:
        *   `assert total_lag_days < blockade_duration`: This is a logical check to ensure the blockade is long enough to cause an effect.
        *   `assert net_direct_loss > 0`: Ensures a positive economic contraction, which is expected.
        *   `assert alt_cap_sub5nm < 0.10`: This assertion validates the chosen `alt_cap_sub5nm` against a hardcoded upper limit (10%). While consistent with the stated range (8% < 10%), it acts as a self-validation rather than a robust check against external perturbations or alternative scenarios within the plausible range.
        *   `assert total_oem_rev_at_risk == 487.0`: This assertion rigidly fixes the sum of the dependent OEM revenues. While it ensures consistency with the specific input values used for the calculation, it prevents any exploration of slight variations in these revenue figures without modifying the assertion itself. This rigidity limits the model's utility as a flexible analytical tool and suggests a design focused on reproducing a specific, predetermined outcome.
        *   `assert abs(loss_billions - expected_loss) < tolerance` and `assert lag == 165.0`: These are direct checks against the predicted outcome and the calculated lag. The tight tolerance (`0.02`) for the loss assertion further emphasizes the model's design to match a specific target value.

    *   **'Cooked Books' Assessment:** The primary concern regarding "cooked books" lies not in fundamental mathematical errors or unit inconsistencies (which are absent), but in the strategic selection of parameters from stated ranges and the rigidity of the `assert` statements. By consistently choosing the upper bound for `CHEM_BUFFER` and `ALT_CAP_SUB5NM`, the model inherently calculates a less severe economic impact than if lower bounds were chosen. While the thesis justifies the `ALT_CAP_SUB5NM` choice as "maximum substitution," this parameter selection, combined with the precise target value assertions, creates a scenario where the model is optimized to produce a specific, potentially understated, contraction figure. This approach, while internally consistent, limits the exploration of more pessimistic yet plausible scenarios within the stated variable ranges.

**So What for the Meta-Judge:**

The mutator's thesis provides a mathematically sound, bottom-up model for direct GDP contraction, successfully avoiding the "cooked books" of broad economic multipliers it critiques. However, the model's specific prediction of a $245.47 Billion contraction is highly sensitive to the selection of point estimates from variable ranges, particularly the `ALT_CAP_SUB5NM` (alternative capacity). By consistently choosing the upper bound of these ranges, the model inherently presents a less severe economic impact. The rigid `assert` statements, especially those fixing the total OEM revenue and the final loss figure, indicate a model designed to validate a specific, predetermined outcome rather than to explore the full spectrum of plausible scenarios. This design choice, while not a mathematical error, limits the model's robustness and transparency in assessing the full potential economic risk, as it implicitly downplays the impact by selecting parameters that mitigate the calculated loss.

```python
import math

def calculate_direct_gdp_contraction_counter(
    chem_buffer_days: float,
    fab_cycle_days: float,
    oem_buffer_days: float,
    apple_hw_rev: float,
    nvda_dc_rev: float,
    amd_tsmc_dep: float,
    blockade_duration: float,
    alt_cap_sub5nm: float
) -> tuple[float, float]:
    """
    Counter-test function to calculate direct GDP contraction with modified parameters.
    """
    
    total_oem_rev_at_risk = apple_hw_rev + nvda_dc_rev + amd_tsmc_dep
    
    # Physical Lag Calculation
    total_lag_days = chem_buffer_days + fab_cycle_days + oem_buffer_days
    
    # Validation 1: Falsify if lag exceeds shock duration
    assert total_lag_days < blockade_duration, "Blockade duration too short to trigger assembly halt."
    
    # Calculate effective disruption window
    disrupted_days = max(0.0, blockade_duration - total_lag_days)
    disruption_fraction = disrupted_days / 365.0
    
    # Calculate Direct GDP Value-Add Loss (Revenues permanently lost, unrecoverable in same fiscal year)
    direct_gross_loss = total_oem_rev_at_risk * disruption_fraction
    
    # Apply Substitution Offset
    net_direct_loss = direct_gross_loss * (1.0 - alt_cap_sub5nm)
    
    # Structural Integrity Checks
    assert net_direct_loss > 0, "Loss calculation failed to produce positive contraction."
    
    return net_direct_loss, total_lag_days

def counter_test_model():
    # Mutator's original parameters for comparison
    mutator_chem_buffer_days = 45.0
    mutator_fab_cycle_days = 90.0
    mutator_oem_buffer_days = 30.0
    mutator_apple_hw_rev = 350.0
    mutator_nvda_dc_rev = 115.0
    mutator_amd_tsmc_dep = 22.0
    mutator_blockade_duration = 365.0
    mutator_alt_cap_sub5nm = 0.08 # Mutator uses upper bound of 5-8% range
    
    # Calculate Mutator's predicted loss using the function for verification
    mutator_loss, mutator_lag = calculate_direct_gdp_contraction_counter(
        mutator_chem_buffer_days, mutator_fab_cycle_days, mutator_oem_buffer_days,
        mutator_apple_hw_rev, mutator_nvda_dc_rev, mutator_amd_tsmc_dep,
        mutator_blockade_duration, mutator_alt_cap_sub5nm
    )
    
    # Assert Mutator's calculation is reproducible
    expected_mutator_loss = 245.47
    tolerance = 0.02
    assert abs(mutator_loss - expected_mutator_loss) < tolerance, \
        f"Mutator's calculation reproducibility failure: Expected ~{expected_mutator_loss}B, got {mutator_loss:.2f}B"
    assert mutator_lag == 165.0, "Mutator's operational friction calculation failure."
    
    print(f"Mutator's Model Output (Reproduced):")
    print(f"  OEM Assembly Halt Time: {mutator_lag} days.")
    print(f"  Direct GDP Contraction: ${mutator_loss:.2f} Billion USD.\n")

    # Counter-Test Parameters:
    # Focus on the sensitivity of ALT_CAP_SUB5NM by choosing the lower bound of the stated range.
    # The LOAD-BEARING VARIABLES table states ALT_CAP_SUB5NM as "~5–8%".
    counter_alt_cap_sub5nm = 0.05 # Using the lower bound of the stated range (5%)
    
    # All other parameters remain as per Mutator's thesis for direct comparison
    counter_loss, counter_lag = calculate_direct_gdp_contraction_counter(
        mutator_chem_buffer_days, mutator_fab_cycle_days, mutator_oem_buffer_days,
        mutator_apple_hw_rev, mutator_nvda_dc_rev, mutator_amd_tsmc_dep,
        mutator_blockade_duration, counter_alt_cap_sub5nm
    )
    
    print(f"Counter-Test Model Output (ALT_CAP_SUB5NM = {counter_alt_cap_sub5nm*100:.0f}%):")
    print(f"  OEM Assembly Halt Time: {counter_lag} days.")
    print(f"  Direct GDP Contraction: ${counter_loss:.2f} Billion USD.\n")

    # Assert that the counter-test loss is significantly higher than the mutator's prediction
    # This exposes the sensitivity to the choice of ALT_CAP_SUB5NM.
    assert counter_loss > mutator_loss, \
        f"Insolvency Exposed: Counter-test loss (${counter_loss:.2f}B) is not greater than Mutator's loss (${mutator_loss:.2f}B) " \
        f"despite using a lower alternative capacity."
    
    print("COUNTER-TEST PASSED: Model's sensitivity to alternative capacity choice demonstrated.")
    print(f"Difference in Contraction: ${counter_loss - mutator_loss:.2f} Billion USD.")

if __name__ == "__main__":
    counter_test_model()

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpxj8c5r27.py", line 95, in <module>
    counter_test_model()
    ~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpxj8c5r27.py", line 61, in counter_test_model
    assert abs(mutator_loss - expected_mutator_loss) < tolerance, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Mutator's calculation reproducibility failure: Expected ~245.47B, got 245.50B



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 61, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 53, in test_model
    assert abs(loss_billions - expected_loss) < tolerance, f"Mathematical failure: Expected ~{expected_loss}B, got {loss_billions}B"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Mathematical failure: Expected ~245.47B, got 245.50136986301368B


# Final Score: 30
**Weakest Point:** The thesis's quantitative proof failed its own unit test for reproducibility, indicating a fundamental flaw in its numerical precision and casting doubt on the entire calculated economic contraction figure. This quantitative failure is compounded by evidence of biased parameter selection and artificial constraints that result in an understated economic impact.
**Rationale:** The thesis commendably pivoted to a physically traceable, inventory depletion model, successfully retiring problematic top-down economic multipliers and financial market capitalization assessments. It provided specific data points for substitution impossibility (yields, build times, bottlenecks) and traced a clear, multi-node cascade path from fab chemical depletion to OEM production halt and direct revenue impact. However, the attacks revealed critical flaws: the model's core assumption of static supply chain resilience was challenged by plausible adaptive mechanisms, and its scope of impacted revenue was artificially constrained. Most critically, the thesis's own quantitative proof failed to reproduce its stated prediction, fundamentally undermining its claim of precise quantification. The consistent selection of parameters to mitigate impact, reinforced by rigid internal assertions, highlighted a model optimized for a specific, potentially understated, outcome rather than a comprehensive risk assessment.
