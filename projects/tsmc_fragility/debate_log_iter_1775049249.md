# Adversarial Debate: tsmc_fragility

## Attacker: Logistics & Resilience Architect (Crisis Adaptation Specialist)
The thesis presents a meticulously constructed argument for significant economic disruption, grounded in a bottom-up assessment of supply chain dependencies and operational parameters. The refinement of the GDP calculation, moving away from a generic multiplier towards a component-based approach, represents a commendable effort to enhance traceability and falsifiability. However, the core vulnerability of the thesis lies in its implicit assumption that several critical variables represent immutable, hard limits, unyielding to extraordinary, coordinated global responses or pre-existing, unstated redundancies. This perspective overlooks the inherent adaptability and contingency capacity that complex systems, particularly those of strategic global importance, tend to develop under duress.

**Critique of Supply Chain Hard Limits and Mitigation Timelines:**

1.  **`CHEM_BUFFER_DAYS` (30 Days) and `TSMC_SEA_IMPORT` (~90% by volume):** The assertion that a 30-day chemical buffer represents an absolute, unextendable limit for operational cessation is a critical point of fragility. While 30-45 days may be a standard operational buffer, it is highly improbable that no strategic stockpiling, either by TSMC itself beyond publicly stated figures or by national governments (e.g., Taiwan, US, Japan) for national security imperatives, exists for critical, high-value, low-volume chemicals. Furthermore, the "90% by volume" figure for seaborne imports does not equate to 90% by *criticality* or *value*. Highly specialized EUV photoresists, for instance, are low-volume but absolutely indispensable. Under extreme duress, the logistical friction of a blockade against targeted, high-value airlifts for such critical components would be substantial, potentially circumventing complete chemical starvation for specific, essential production lines. The "Absolute Veto" of chemistry and physics is indeed immutable, but the *duration* of its application can be influenced by pre-positioning and alternative logistics.

2.  **`RESTART_DAYS` (60 Days):** The revised 60-day re-qualification period, while acknowledging complexity, still assumes a standard operational recovery timeline. In a scenario of global economic criticality, the response would likely transcend typical commercial considerations. Aggressive global cooperation could manifest as:
    *   **Prioritization of Resources:** Unprecedented allocation of engineering talent, specialized equipment, and regulatory fast-tracking.
    *   **Parallel Processing:** Simultaneous re-qualification of different fab modules or lines, rather than sequential.
    *   **International Assistance:** Direct technical support from allied nations' semiconductor experts.
    This collective effort could significantly compress the re-qualification timeline, challenging the notion of a fixed 60-day period as an unbreakable hard limit.

3.  **`FAB_BUILD_TIME` (3-5 years) and `ALT_BUILD_YEARS` (4-7 years):** While the construction of leading-edge fabs is indeed a multi-year endeavor, these timelines are typically observed under normal market conditions. In a global emergency, analogous to "Manhattan Project" or "Operation Warp Speed" efforts, these timelines could be aggressively accelerated. Governments could streamline permitting, provide unlimited funding, prioritize material and labor allocation, and even repurpose existing "dark fabs" or less advanced facilities for specific, critical components, thereby alleviating some pressure on the most advanced nodes. The thesis's focus on the current `ALT_CAP_SUB5NM` (5-8%) as a static constraint ignores the potential for rapid, albeit costly, expansion or re-prioritization of existing, slightly older node capacity (e.g., 7nm, 10nm) for less demanding applications, freeing up sub-5nm capacity for the most critical uses.

**Parametric Grounding Audit:**

The numerical values provided for market shares, capacities, revenues, and costs are generally consistent with established industry reports and financial disclosures. The `FAB_CYCLE_TIME_DAYS` (90 days) and `WAFER_PRICE_USD` ($20,000) are reasonable industry estimates for advanced nodes. The new variables `OEM_VALUE_ADD_PCT` (0.50) and `FOREGONE_INFRA_CAPEX_RATIO` (2.5x) are plausible estimations for their respective economic contributions, though their precise values are subject to modeling assumptions. The core issue is not the factual basis of these numbers, but rather the implicit assumption of their *rigidity* as unassailable constraints within the model, precluding adaptive responses.

**"Cooked Books" in the Python Code:**

The Python code accurately implements the logic described in the thesis, and the calculation of `GROSS_SUPPLY_VOID_DURATION_DAYS` is consistent with the stated timeline (quarantine commencement to first new chip). Therefore, there are no "cooked books" in terms of computational errors or unit dimensionality within the Mutator's defined framework. However, the "cooked books" manifest in the *selection and interpretation* of the input parameters, specifically `CHEM_BUFFER_DAYS` and `RESTART_DAYS`, as absolute, uninfluenceable hard limits. The model's insolvency stems from its failure to incorporate the potential for strategic interventions that could fundamentally alter these parameters.

**So What for the Meta-Judge:**

The Mutator's thesis, while analytically rigorous in its defined scope, presents an incomplete picture of systemic resilience. By treating operational buffers and recovery timelines as rigid constants, it significantly overestimates the economic impact of a supply chain disruption. The model's insolvency lies in its underestimation of the adaptive capacity of global supply chains and the potential for extraordinary, coordinated responses. Strategic stockpiling, targeted alternative logistics, and accelerated emergency protocols are not merely theoretical constructs but plausible, albeit costly, mitigation strategies that would fundamentally alter the disruption timeline and impact. A more robust analysis must account for these latent flexibilities, demonstrating that the projected points of failure are not necessarily terminal, but rather points of intense pressure that can be managed through proactive contingency planning and aggressive intervention.

---

```python
import math

# MUTATOR'S LOAD-BEARING VARIABLES (for comparison and base values)
TSMC_ADV_WSPM = 250000  # Wafers/Mo
FAB_CYCLE_TIME_DAYS = 90  # Days
WAFER_PRICE_USD = 20000  # USD
CHEM_BUFFER_DAYS_MUTATOR = 30  # Days (Mutator's assumption)
QUARANTINE_DAYS = 60  # Days (Stress-test parameter)
RESTART_DAYS_MUTATOR = 60  # Days (Mutator's assumption)
OEM_INVENTORY_DAYS = 20  # Days
REV_AAPL_HW_ANNUAL = 350e9  # USD
REV_NVDA_DC_ANNUAL = 115e9  # USD
REV_AMD_ANNUAL = 22e9  # USD
AAPL_HW_DEP_PCT = 0.90
NVDA_DC_DEP_PCT = 0.95
AMD_DEP_PCT = 0.85
OEM_VALUE_ADD_PCT = 0.50
FOREGONE_INFRA_CAPEX_RATIO = 2.5
WORLD_GDP_ANNUAL = 105e12  # USD

# --- COUNTER-TEST VARIABLES (Challenging the 'hard limits') ---
# 1. Strategic Stockpiling: Assume a government-mandated strategic reserve for critical chemicals.
# This buffer is designed to last at least the duration of a plausible gray-zone quarantine.
STRATEGIC_CHEM_BUFFER_DAYS = 60  # Days. Matches QUARANTINE_DAYS.
# This implies that chemical starvation does NOT occur during the 60-day quarantine.
# The fab continues to operate, consuming from this strategic buffer.

# 2. Emergency Acceleration: Assume global cooperation and emergency measures can halve the restart time.
ACCELERATED_RESTART_DAYS = RESTART_DAYS_MUTATOR / 2  # 30 Days.

# --- COUNTER-TEST CALCULATIONS ---

# 1. Re-evaluate WIP Destruction:
# If strategic buffer prevents chemical starvation during quarantine, WIP destruction due to starvation is avoided.
# The Mutator's thesis explicitly links WIP destruction to chemical starvation.
WIP_VALUE_COUNTER = 0  # No WIP destruction due to chemical starvation in this scenario.

# 2. Calculate Gross Supply Void Duration for Counter-Test:
# In this scenario, the fab operates for the full QUARANTINE_DAYS using the strategic buffer.
# The supply void begins *after* the quarantine lifts and the strategic buffer is depleted.
# It then includes the accelerated restart and the normal fab cycle time.
GROSS_SUPPLY_VOID_DURATION_DAYS_COUNTER = ACCELERATED_RESTART_DAYS + FAB_CYCLE_TIME_DAYS

# 3. Adjust for OEM Finished Goods Inventory Buffer to get Effective Supply Void
EFFECTIVE_SUPPLY_VOID_DAYS_COUNTER = GROSS_SUPPLY_VOID_DURATION_DAYS_COUNTER - OEM_INVENTORY_DAYS
X_MONTHS_COUNTER = EFFECTIVE_SUPPLY_VOID_DAYS_COUNTER / 30.0

# 4. Calculate Monthly Dependent OEM Revenue (Y_MONTHLY) - This remains the same as Mutator's
apple_dep_monthly = (REV_AAPL_HW_ANNUAL * AAPL_HW_DEP_PCT) / 12.0
nvidia_dep_monthly = (REV_NVDA_DC_ANNUAL * NVDA_DC_DEP_PCT) / 12.0
amd_dep_monthly = (REV_AMD_ANNUAL * AMD_DEP_PCT) / 12.0
Y_MONTHLY = apple_dep_monthly + nvidia_dep_monthly + amd_dep_monthly

# 5. Calculate Traceable Hardware Revenue Loss (Z_REV) for Counter-Test
Z_REV_COUNTER = X_MONTHS_COUNTER * Y_MONTHLY

# 6. Calculate Z_GDP for Counter-Test
DIRECT_VALUE_ADD_LOSS_COUNTER = Z_REV_COUNTER * OEM_VALUE_ADD_PCT
NVDA_DC_REV_VOID_COUNTER = nvidia_dep_monthly * X_MONTHS_COUNTER
FOREGONE_CAPEX_IMPACT_COUNTER = NVDA_DC_REV_VOID_COUNTER * FOREGONE_INFRA_CAPEX_RATIO
Z_GDP_COUNTER = DIRECT_VALUE_ADD_LOSS_COUNTER + FOREGONE_CAPEX_IMPACT_COUNTER

# --- MUTATOR'S ORIGINAL CALCULATIONS (for direct comparison) ---
# Re-calculate Mutator's values to ensure consistency for assertions
GROSS_SUPPLY_VOID_DURATION_DAYS_MUTATOR = QUARANTINE_DAYS + RESTART_DAYS_MUTATOR + FAB_CYCLE_TIME_DAYS
EFFECTIVE_SUPPLY_VOID_DAYS_MUTATOR = GROSS_SUPPLY_VOID_DURATION_DAYS_MUTATOR - OEM_INVENTORY_DAYS
X_MONTHS_MUTATOR = EFFECTIVE_SUPPLY_VOID_DAYS_MUTATOR / 30.0
WIP_WAFER_COUNT_MUTATOR = TSMC_ADV_WSPM * (FAB_CYCLE_TIME_DAYS / 30)
WIP_VALUE_MUTATOR = WIP_WAFER_COUNT_MUTATOR * WAFER_PRICE_USD
Z_REV_MUTATOR = X_MONTHS_MUTATOR * Y_MONTHLY
DIRECT_VALUE_ADD_LOSS_MUTATOR = Z_REV_MUTATOR * OEM_VALUE_ADD_PCT
NVDA_DC_REV_VOID_MUTATOR = nvidia_dep_monthly * X_MONTHS_MUTATOR
FOREGONE_CAPEX_IMPACT_MUTATOR = NVDA_DC_REV_VOID_MUTATOR * FOREGONE_INFRA_CAPEX_RATIO
Z_GDP_MUTATOR = DIRECT_VALUE_ADD_LOSS_MUTATOR + FOREGONE_CAPEX_IMPACT_MUTATOR


# --- PRINT RESULTS ---
print("--- Mutator's Original Predictions ---")
print(f"Mutator's WIP Value: ${WIP_VALUE_MUTATOR:,.2f} USD")
print(f"Mutator's Effective Supply Void Duration: {X_MONTHS_MUTATOR:.2f} months")
print(f"Mutator's Traceable Hardware Revenue Loss (Z_REV): ${Z_REV_MUTATOR:,.2f} USD")
print(f"Mutator's Traceable Global GDP Contraction (Z_GDP): ${Z_GDP_MUTATOR:,.2f} USD")
print("\n--- Counter-Test Predictions (with Strategic Buffers & Accelerated Response) ---")
print(f"Counter-Test WIP Value (avoided due to strategic buffer): ${WIP_VALUE_COUNTER:,.2f} USD")
print(f"Counter-Test Effective Supply Void Duration: {X_MONTHS_COUNTER:.2f} months")
print(f"Counter-Test Traceable Hardware Revenue Loss (Z_REV): ${Z_REV_COUNTER:,.2f} USD")
print(f"Counter-Test Traceable Global GDP Contraction (Z_GDP): ${Z_GDP_COUNTER:,.2f} USD")

# --- ASSERTIONS TO EXPOSE INSOLVENCY ---
# The counter-test asserts that the Mutator's predictions are significantly higher
# due to the omission of plausible mitigation strategies.
# We expect the counter-test values to be *less* than the Mutator's values.

# Use a tolerance for float comparisons, e.g., $100 million for billions.
TOLERANCE = 1e8 # $100 million

# Assert that WIP destruction is avoided in the counter-scenario
assert WIP_VALUE_COUNTER < WIP_VALUE_MUTATOR, \
    f"Counter-test failed: WIP destruction was not reduced. Mutator: ${WIP_VALUE_MUTATOR:,.2f}, Counter: ${WIP_VALUE_COUNTER:,.2f}"

# Assert that the effective supply void duration is significantly reduced
assert X_MONTHS_COUNTER < X_MONTHS_MUTATOR, \
    f"Counter-test failed: Supply void duration not reduced. Mutator: {X_MONTHS_MUTATOR:.2f} months, Counter: {X_MONTHS_COUNTER:.2f} months"

# Assert that the traceable hardware revenue loss is significantly reduced
assert Z_REV_COUNTER < Z_REV_MUTATOR, \
    f"Counter-test failed: Revenue loss not reduced. Mutator: ${Z_REV_MUTATOR:,.2f}, Counter: ${Z_REV_COUNTER:,.2f}"

# Assert that the traceable global GDP contraction is significantly reduced
assert Z_GDP_COUNTER < Z_GDP_MUTATOR, \
    f"Counter-test failed: GDP contraction not reduced. Mutator: ${Z_GDP_MUTATOR:,.2f}, Counter: ${Z_GDP_COUNTER:,.2f}"

print("\nCounter-test successful: Plausible mitigation strategies significantly reduce projected economic impact, challenging the rigidity of the Mutator's 'hard limits'.")

```

### PYTHON EXECUTION OUTPUT:
--- Mutator's Original Predictions ---
Mutator's WIP Value: $15,000,000,000.00 USD
Mutator's Effective Supply Void Duration: 6.33 months
Mutator's Traceable Hardware Revenue Loss (Z_REV): $233,779,166,666.67 USD
Mutator's Traceable Global GDP Contraction (Z_GDP): $261,038,888,888.89 USD

--- Counter-Test Predictions (with Strategic Buffers & Accelerated Response) ---
Counter-Test WIP Value (avoided due to strategic buffer): $0.00 USD
Counter-Test Effective Supply Void Duration: 3.33 months
Counter-Test Traceable Hardware Revenue Loss (Z_REV): $123,041,666,666.67 USD
Counter-Test Traceable Global GDP Contraction (Z_GDP): $137,388,888,888.89 USD

Counter-test successful: Plausible mitigation strategies significantly reduce projected economic impact, challenging the rigidity of the Mutator's 'hard limits'.


## Attacker: Heterodox Macroeconomist (Multiplier & Scope Validity Theorist)
The Mutator's thesis presents a significant architectural pivot, commendably retiring the problematic 8.4x automotive-chip multiplier in favor of a more granular, bottom-up approach to GDP impact assessment. This shift towards explicit, component-based causality (`DIRECT_VALUE_ADD_LOSS` and `FOREGONE_INFRA_CAPEX_IMPACT`) is a methodological improvement. Furthermore, the Mutator has adjusted the `RESTART_DAYS` parameter, acknowledging the complexity of fab re-qualification.

However, a detailed audit of the "LOAD-BEARING VARIABLES" and the Python implementation reveals a critical systemic inconsistency in the calculation of the `GROSS_SUPPLY_VOID_DURATION_DAYS`. The Mutator's textual explanation for the 210-day void duration ("30 days (buffer depletion) + 30 days (remaining quarantine) + 60 days (facility re-qualification) + 90 days (new wafer processing)") is mathematically equivalent to `QUARANTINE_DAYS + RESTART_DAYS + FAB_CYCLE_TIME_DAYS`. This formulation implicitly double-counts the `CHEM_BUFFER_DAYS` within the `QUARANTINE_DAYS` component of the supply void.

Specifically, the `CHEM_BUFFER_DAYS` (30 days) represent the period during which the fab *continues to operate* despite the quarantine. The actual cessation of production, leading to a "zero-output state," only commences *after* this buffer is depleted. Therefore, the duration of the supply disruption, from the point of production cessation until new chips are available, should be calculated as:
` (QUARANTINE_DAYS - CHEM_BUFFER_DAYS) + RESTART_DAYS + FAB_CYCLE_TIME_DAYS`.

Using the Mutator's own parameters, this corrected calculation yields:
` (60 - 30) + 60 + 90 = 30 + 60 + 90 = 180 days`.
The Mutator's model, however, uses 210 days for the gross void, leading to an overstatement of 30 days (1 month) in the `EFFECTIVE_SUPPLY_VOID_DAYS` and consequently inflating the `Z_REV` and `Z_GDP` projections. This constitutes a fundamental mathematical misapplication within the core causal chain, directly impacting the magnitude of the predicted economic contraction.

Beyond this primary calculation error, the model remains susceptible to overstatement due to the selection of several other operational and economic parameters that, while presented as "plausible," consistently lean towards maximizing the projected impact:
1.  **`CHEM_BUFFER_DAYS` (30 Days):** While a "critical minimum," it is at the lower end of industry reported buffers (1-6 weeks), which could be more robust in practice.
2.  **`OEM_INVENTORY_DAYS` (20 Days):** This is a relatively low finished goods buffer for high-value tech products, which could be higher for some OEMs.
3.  **Dependency Percentages (`AAPL_HW_DEP_PCT` 0.90, `NVDA_DC_DEP_PCT` 0.95, `AMD_DEP_PCT` 0.85):** These are exceptionally high, implying near-total and immediate reliance across broad revenue segments. While leading-edge nodes are critical, the entirety of these companies' stated revenues may not be *immediately* and *completely* halted by a single node disruption, allowing for some product mix, older node utilization, or existing chip inventory.
4.  **`FOREGONE_INFRA_CAPEX_RATIO` (2.5x):** This new, targeted multiplier assumes a very strong and fixed elasticity between lost NVIDIA GPU revenue and other infrastructure CAPEX. While GPUs are foundational, a 2.5x ratio implies that for every dollar of lost GPU revenue, $2.50 of *other* infrastructure investment is foregone. This ratio is an economic estimate, not a physical constant, and is highly susceptible to overstatement, as hyperscalers might reallocate, delay, or find alternative investments rather than a direct, high-ratio cessation of all related CAPEX.

**So What for the Meta-Judge:**
The Mutator's thesis, despite its commendable pivot to a more granular economic model, contains a fundamental mathematical error in calculating the duration of the supply void, which directly inflates the projected economic impact. Furthermore, the model's reliance on several non-physical, estimated parameters—such as operational buffer durations, OEM dependency percentages, and the `FOREGONE_INFRA_CAPEX_RATIO`—which are consistently chosen at values that maximize the projected outcome, renders the overall prediction highly sensitive and potentially overstated. This combination of a core calculation flaw and impact-maximizing parameter selection undermines the model's claim of robust, falsifiable causality and its ability to accurately represent systemic economic contraction.

```python
import math

# --- Mutator's Original LOAD-BEARING VARIABLES (for comparison and base calculations) ---
ORIG_TSMC_ADV_WSPM = 250000  # Wafers/Mo
ORIG_FAB_CYCLE_TIME_DAYS = 90  # Days
ORIG_WAFER_PRICE_USD = 20000  # USD
ORIG_CHEM_BUFFER_DAYS = 30  # Days
ORIG_QUARANTINE_DAYS = 60  # Days
ORIG_RESTART_DAYS = 60  # Days
ORIG_OEM_INVENTORY_DAYS = 20  # Days
ORIG_REV_AAPL_HW_ANNUAL = 350e9  # USD
ORIG_REV_NVDA_DC_ANNUAL = 115e9  # USD
ORIG_REV_AMD_ANNUAL = 22e9  # USD
ORIG_AAPL_HW_DEP_PCT = 0.90
ORIG_NVDA_DC_DEP_PCT = 0.95
ORIG_AMD_DEP_PCT = 0.85
ORIG_OEM_VALUE_ADD_PCT = 0.50
ORIG_FOREGONE_INFRA_CAPEX_RATIO = 2.5
ORIG_WORLD_GDP_ANNUAL = 105e12  # USD

# --- Mutator's Original Calculations (to get their Z_GDP for direct comparison) ---
# This section replicates the Mutator's code exactly, including the identified calculation flaw.
orig_gross_supply_void_duration_days_mutator_logic = ORIG_QUARANTINE_DAYS + ORIG_RESTART_DAYS + ORIG_FAB_CYCLE_TIME_DAYS
orig_effective_supply_void_days_mutator_logic = orig_gross_supply_void_duration_days_mutator_logic - ORIG_OEM_INVENTORY_DAYS
orig_x_months_mutator_logic = orig_effective_supply_void_days_mutator_logic / 30.0
orig_apple_dep_monthly = (ORIG_REV_AAPL_HW_ANNUAL * ORIG_AAPL_HW_DEP_PCT) / 12.0
orig_nvidia_dep_monthly = (ORIG_REV_NVDA_DC_ANNUAL * ORIG_NVDA_DC_DEP_PCT) / 12.0
orig_amd_dep_monthly = (ORIG_REV_AMD_ANNUAL * ORIG_AMD_DEP_PCT) / 12.0
orig_y_monthly = orig_apple_dep_monthly + orig_nvidia_dep_monthly + orig_amd_dep_monthly
orig_z_rev_mutator_logic = orig_x_months_mutator_logic * orig_y_monthly
orig_direct_value_add_loss_mutator_logic = orig_z_rev_mutator_logic * ORIG_OEM_VALUE_ADD_PCT
orig_nvda_dc_rev_void_mutator_logic = orig_nvidia_dep_monthly * orig_x_months_mutator_logic
orig_foregone_capex_impact_mutator_logic = orig_nvda_dc_rev_void_mutator_logic * ORIG_FOREGONE_INFRA_CAPEX_RATIO
ORIG_Z_GDP_MUTATOR_LOGIC = orig_direct_value_add_loss_mutator_logic + orig_foregone_capex_impact_mutator_logic

# --- COUNTER-TEST: Revised LOAD-BEARING VARIABLES (more conservative, yet plausible) ---
# Focus on operational buffers and economic ratios that are not physical constants.
CHEM_BUFFER_DAYS_REVISED = 45  # From 30. Still within 1-6 weeks, but reflects more robust buffer.
OEM_INVENTORY_DAYS_REVISED = 30  # From 20. A full month's stock, still plausible for high-value goods.
RESTART_DAYS_REVISED = ORIG_RESTART_DAYS # Mutator already revised this up, so keep it for this test.

# Dependency Percentages (Mutator's are very high, implying near-total reliance):
AAPL_HW_DEP_PCT_REVISED = 0.80  # From 0.90. Acknowledges some buffer or less immediate impact.
NVDA_DC_DEP_PCT_REVISED = 0.85  # From 0.95. Similar rationale.
AMD_DEP_PCT_REVISED = 0.75  # From 0.85. Similar rationale.

# Economic Ratios (Mutator's are impact-maximizing):
FOREGONE_INFRA_CAPEX_RATIO_REVISED = 1.5  # From 2.5. Still significant, but less aggressive.

# Other variables remain as per Mutator's original, as they are less contentious or scenario-specific.
TSMC_ADV_WSPM = ORIG_TSMC_ADV_WSPM
FAB_CYCLE_TIME_DAYS = ORIG_FAB_CYCLE_TIME_DAYS
WAFER_PRICE_USD = ORIG_WAFER_PRICE_USD
QUARANTINE_DAYS = ORIG_QUARANTINE_DAYS
REV_AAPL_HW_ANNUAL = ORIG_REV_AAPL_HW_ANNUAL
REV_NVDA_DC_ANNUAL = ORIG_REV_NVDA_DC_ANNUAL
REV_AMD_ANNUAL = ORIG_REV_AMD_ANNUAL
OEM_VALUE_ADD_PCT = ORIG_OEM_VALUE_ADD_PCT
WORLD_GDP_ANNUAL = ORIG_WORLD_GDP_ANNUAL

# --- COUNTER-TEST Calculations with CORRECTED LOGIC for Supply Void Duration ---

# 1. Corrected Gross Supply Void Duration (from fab production cessation until new chips available)
# The fab stops producing after CHEM_BUFFER_DAYS.
# The duration of zero output is: (remaining quarantine after buffer depletion) + restart time + wafer cycle time.
gross_supply_void_duration_corrected_days = (QUARANTINE_DAYS - CHEM_BUFFER_DAYS_REVISED) + RESTART_DAYS_REVISED + FAB_CYCLE_TIME_DAYS
assert gross_supply_void_duration_corrected_days > 0, "Corrected gross supply void duration must be positive."

# 2. Adjust for OEM Finished Goods Inventory Buffer to get Effective Supply Void
effective_supply_void_days_ct = gross_supply_void_duration_corrected_days - OEM_INVENTORY_DAYS_REVISED
X_MONTHS_CT = effective_supply_void_days_ct / 30.0
assert X_MONTHS_CT > 0, "Effective supply void duration in months must be positive."

# 3. Calculate Monthly Dependent OEM Revenue (Y_MONTHLY) with revised dependency percentages
apple_dep_monthly_ct = (REV_AAPL_HW_ANNUAL * AAPL_HW_DEP_PCT_REVISED) / 12.0
nvidia_dep_monthly_ct = (REV_NVDA_DC_ANNUAL * NVDA_DC_DEP_PCT_REVISED) / 12.0
amd_dep_monthly_ct = (REV_AMD_ANNUAL * AMD_DEP_PCT_REVISED) / 12.0
Y_MONTHLY_CT = apple_dep_monthly_ct + nvidia_dep_monthly_ct + amd_dep_monthly_ct

# 4. Calculate Traceable Hardware Revenue Loss (Z_REV)
Z_REV_CT = X_MONTHS_CT * Y_MONTHLY_CT

# 5. Calculate Z_GDP (Revised to avoid generic multiplier)
DIRECT_VALUE_ADD_LOSS_CT = Z_REV_CT * OEM_VALUE_ADD_PCT

NVDA_DC_REV_VOID_CT = nvidia_dep_monthly_ct * X_MONTHS_CT
FOREGONE_CAPEX_IMPACT_CT = NVDA_DC_REV_VOID_CT * FOREGONE_INFRA_CAPEX_RATIO_REVISED

Z_GDP_CT = DIRECT_VALUE_ADD_LOSS_CT + FOREGONE_CAPEX_IMPACT_CT

# --- Print Results ---
print("--- Mutator's Original Projections (using their code's logic) ---")
print(f"Original Effective Supply Void Duration (Mutator's logic): {orig_x_months_mutator_logic:.2f} months")
print(f"Original Traceable Hardware Revenue Loss (Z_REV, Mutator's logic): ${orig_z_rev_mutator_logic:,.2f} USD")
print(f"Original Traceable Global GDP Contraction (Z_GDP, Mutator's logic): ${ORIG_Z_GDP_MUTATOR_LOGIC:,.2f} USD")

print("\n--- Counter-Test Projections (with corrected logic and more conservative parameters) ---")
print(f"Corrected Gross Supply Void Duration (from fab stop): {gross_supply_void_duration_corrected_days:.0f} days")
print(f"Revised Effective Supply Void Duration (corrected logic): {X_MONTHS_CT:.2f} months")
print(f"Revised Traceable Hardware Revenue Loss (Z_REV, corrected logic): ${Z_REV_CT:,.2f} USD")
print(f"Revised Traceable Global GDP Contraction (Z_GDP, corrected logic): ${Z_GDP_CT:,.2f} USD")

# --- Assertions for Counter-Test ---
# 1. Assert the Mutator's X_MONTHS is inflated due to the calculation error.
#    Calculate X_MONTHS for Mutator's parameters using the CORRECTED logic.
orig_gross_supply_void_duration_corrected_days = (ORIG_QUARANTINE_DAYS - ORIG_CHEM_BUFFER_DAYS) + ORIG_RESTART_DAYS + ORIG_FAB_CYCLE_TIME_DAYS
orig_effective_supply_void_days_corrected_logic = orig_gross_supply_void_duration_corrected_days - ORIG_OEM_INVENTORY_DAYS
orig_x_months_corrected_logic = orig_effective_supply_void_days_corrected_logic / 30.0

print("\n--- Critical Assertions ---")
assert orig_x_months_mutator_logic > orig_x_months_corrected_logic, \
    f"Falsification: Mutator's effective supply void duration ({orig_x_months_mutator_logic:.2f} months) is NOT inflated compared to corrected logic ({orig_x_months_corrected_logic:.2f} months)."
print(f"Assertion Passed: Mutator's effective supply void duration is inflated by {(orig_x_months_mutator_logic - orig_x_months_corrected_logic):.2f} months due to calculation error.")

# 2. Assert that the Mutator's original Z_GDP (from their code) is significantly higher than the Z_GDP
#    calculated with the corrected logic and more conservative, yet plausible, parameters.
assert ORIG_Z_GDP_MUTATOR_LOGIC > Z_GDP_CT, \
    "Falsification: Mutator's original GDP projection is not higher than the revised projection with corrected logic and parameters."
percentage_reduction = ((ORIG_Z_GDP_MUTATOR_LOGIC - Z_GDP_CT) / ORIG_Z_GDP_MUTATOR_LOGIC) * 100
print(f"Assertion Passed: Projected GDP Contraction reduced by {percentage_reduction:.2f}% with corrected logic and conservative parameters.")
assert percentage_reduction > 25, f"Falsification: GDP reduction ({percentage_reduction:.2f}%) is not substantial enough (expected > 25%)."

print("\nCounter-test successful: The Mutator's model contains a fundamental calculation error that inflates the supply void duration, and its projected GDP contraction is highly sensitive to adjustments in operational buffers and economic dependency ratios, demonstrating significant potential for overstatement under impact-maximizing parameter choices.")
```

### PYTHON EXECUTION OUTPUT:
--- Mutator's Original Projections (using their code's logic) ---
Original Effective Supply Void Duration (Mutator's logic): 6.33 months
Original Traceable Hardware Revenue Loss (Z_REV, Mutator's logic): $233,779,166,666.67 USD
Original Traceable Global GDP Contraction (Z_GDP, Mutator's logic): $261,038,888,888.89 USD

--- Counter-Test Projections (with corrected logic and more conservative parameters) ---
Corrected Gross Supply Void Duration (from fab stop): 165 days
Revised Effective Supply Void Duration (corrected logic): 4.50 months
Revised Traceable Hardware Revenue Loss (Z_REV, corrected logic): $147,843,750,000.00 USD
Revised Traceable Global GDP Contraction (Z_GDP, corrected logic): $128,906,250,000.00 USD

--- Critical Assertions ---
Assertion Passed: Mutator's effective supply void duration is inflated by 1.00 months due to calculation error.
Assertion Passed: Projected GDP Contraction reduced by 50.62% with corrected logic and conservative parameters.

Counter-test successful: The Mutator's model contains a fundamental calculation error that inflates the supply void duration, and its projected GDP contraction is highly sensitive to adjustments in operational buffers and economic dependency ratios, demonstrating significant potential for overstatement under impact-maximizing parameter choices.


## Attacker: Quantitative Risk Arbitrageur (Model Integrity Auditor)
### Analytical Critique

The thesis presents a "Structural Arbitrage" and a re-architected causal chain for economic impact, explicitly claiming to "entirely bypass the generic multiplier" in its calculation of Global GDP Contraction ($Z_{GDP}$). While the intent to enhance traceability and reduce reliance on top-down heuristics is noted, a rigorous dissection reveals several critical inconsistencies and logical flaws, particularly in the `LOAD-BEARING VARIABLES` and their implementation within the Python Falsification Suite.

**1. Logical Inconsistency: Re-introduction of Multiplier under New Nomenclature**
The most significant logical inconsistency lies in the introduction of `FOREGONE_INFRA_CAPEX_RATIO` (2.5x). The thesis explicitly states, "This entirely bypasses the generic multiplier" for $Z_{GDP}$ calculation. However, this new variable functions as a direct multiplier (2.5x) on lost NVIDIA Data Center revenue, estimating "delayed/foregone global data center and AI infrastructure CAPEX." This is precisely the type of "generic multiplier" the thesis claims to have retired, merely rebranded and applied to a specific revenue stream. This directly contradicts the stated methodological pivot and suggests a deliberate attempt to re-introduce an impact-amplifying factor while claiming to avoid it. The justification for a 2.5x ratio for *foregone CAPEX per dollar of lost GPU revenue* is highly speculative and lacks robust parametric grounding, likely inflating the estimated impact.

**2. Discrepancy Between Prose and Python Implementation for `Effective Supply Void Duration`**
A fundamental mathematical error exists in the Python code's calculation of `GROSS_SUPPLY_VOID_DURATION_DAYS` compared to the thesis's own prose explanation.
*   **Thesis Prose:** The "effective 6.33-month supply pipeline void" is described as factoring in "the 30-day remaining quarantine, a more robust 60-day fab restart and re-qualification period, a 90-day wafer cycle time." This translates to `(QUARANTINE_DAYS - CHEM_BUFFER_DAYS) + RESTART_DAYS + FAB_CYCLE_TIME_DAYS`. With the Mutator's parameters (60 - 30) + 60 + 90 = 180 days.
*   **Python Code:** The `GROSS_SUPPLY_VOID_DURATION_DAYS` is calculated as `QUARANTINE_DAYS + RESTART_DAYS + FAB_CYCLE_TIME_DAYS`, which is 60 + 60 + 90 = 210 days.
The Python implementation overstates the `GROSS_SUPPLY_VOID_DURATION_DAYS` by `CHEM_BUFFER_DAYS` (30 days) compared to its own textual description. This directly inflates the `X_MONTHS` (Effective Supply Void Duration) by 1 month, leading to an approximately 18.7% overestimation of both `Z_REV` and `Z_GDP`. This is a clear instance of "cooked books" in the code, where the implementation deviates from the stated logic in an impact-maximizing direction.

**3. Impact-Maximizing Variable Selection for `CHEM_BUFFER_DAYS`**
The `CHEM_BUFFER_DAYS` variable is assigned an "Exact Numerical Value" of 30 days. While the original `LOAD-BEARING VARIABLES` table cited a range of "30–45 days," the thesis justifies selecting 30 days as "the critical minimum buffer for a stress-test scenario." This choice, selecting the absolute minimum of a plausible range, directly contradicts the thesis's claim of "Conservation of Trade-Offs" and moving away from "impact-maximizing minimums." While `RESTART_DAYS` was increased, this specific choice for `CHEM_BUFFER_DAYS` maintains an aggressive, impact-maximizing stance for a critical trigger variable, accelerating the onset of the "zero-output state."

**4. Presentation of Calculated Values as Axioms**
The `LOGIC DAG` presents the "$15.00 Billion USD" WIP destruction as an "Axiom 4." However, this value is a calculated outcome within the Python script (`WIP_VALUE = TSMC_ADV_WSPM * (FAB_CYCLE_TIME_DAYS / 30) * WAFER_PRICE_USD`), derived from specific assumptions about capacity, cycle time, and wafer price. Presenting a calculated result as an axiomatic truth obscures the underlying assumptions and their potential variability, reducing the transparency and falsifiability of the model.

**5. Collapse of Ranges to Single-Point Estimates**
Many variables in the `LOAD-BEARING VARIABLES` table, such as `TSMC_ADV_WSPM`, `WAFER_PRICE_USD`, `REV_AAPL_HW_ANNUAL`, `REV_NVDA_DC_ANNUAL`, and `REV_AMD_ANNUAL`, are derived from source contexts that indicate approximations (`~`, `>`) or ranges. These are consistently collapsed into single-point estimates without explicit justification for the chosen point within the range (e.g., midpoint, conservative estimate). While this is common in modeling, for a persona focused on "relentlessly dissecting the mathematical core," this practice introduces sensitivity that is not fully explored.

**"So What" for the Meta-Judge:**

The thesis, despite its claims of structural re-architecture and rigorous bottom-up assessment, exhibits fundamental mathematical inconsistencies and strategic parameter choices that undermine its credibility. The Python code, rather than serving as a neutral falsification suite, contains a critical calculation error that inflates the estimated `Effective Supply Void Duration` by 30 days compared to the thesis's own prose explanation. This discrepancy, coupled with the re-introduction of a significant multiplier (`FOREGONE_INFRA_CAPEX_RATIO`) under a new name and the selection of an impact-maximizing `CHEM_BUFFER_DAYS`, indicates a persistent bias towards maximizing the projected economic impact. These issues collectively compromise the model's solvency, precision, and the mathematical rigor it purports to uphold, suggesting that the "books" are indeed "cooked" through both logical misdirection and computational error.

### COUNTER-TEST

```python
import math

# Mutator's LOAD-BEARING VARIABLES (for reference and use in counter-test)
TSMC_ADV_WSPM = 250000  # Wafers/Mo
FAB_CYCLE_TIME_DAYS = 90  # Days
WAFER_PRICE_USD = 20000  # USD
CHEM_BUFFER_DAYS_MUTATOR = 30  # Days (Mutator's choice, lower end of 30-45 day range)
QUARANTINE_DAYS = 60  # Days
RESTART_DAYS = 60  # Days (Revised by Mutator)
OEM_INVENTORY_DAYS = 20  # Days
REV_AAPL_HW_ANNUAL = 350e9  # USD
REV_NVDA_DC_ANNUAL = 115e9  # USD
REV_AMD_ANNUAL = 22e9  # USD
AAPL_HW_DEP_PCT = 0.90
NVDA_DC_DEP_PCT = 0.95
AMD_DEP_PCT = 0.85
OEM_VALUE_ADD_PCT = 0.50  # New variable
FOREGONE_INFRA_CAPEX_RATIO_MUTATOR = 2.5  # New variable (Mutator's choice, aggressive multiplier)
WORLD_GDP_ANNUAL = 105e12  # USD

# Mutator's PREDICTED values (for assertion against the Mutator's *code's* output)
PREDICTED_WIP_VALUE_MUTATOR = 15.00e9
PREDICTED_EFFECTIVE_SUPPLY_VOID_MONTHS_MUTATOR = 190 / 30.0 # 6.333... months
PREDICTED_Z_REV_MUTATOR = 233.74e9
PREDICTED_Z_GDP_MUTATOR = 261.04e9

# --- Counter-Test Function: Implements Mutator's *prose logic* for supply void ---
def calculate_impact_with_corrected_logic(
    chem_buffer_days,
    foregone_infra_capex_ratio,
    quarantine_days=QUARANTINE_DAYS,
    restart_days=RESTART_DAYS,
    fab_cycle_time_days=FAB_CYCLE_TIME_DAYS,
    oem_inventory_days=OEM_INVENTORY_DAYS,
    rev_aapl_hw_annual=REV_AAPL_HW_ANNUAL,
    rev_nvda_dc_annual=REV_NVDA_DC_ANNUAL,
    rev_amd_annual=REV_AMD_ANNUAL,
    aapl_hw_dep_pct=AAPL_HW_DEP_PCT,
    nvda_dc_dep_pct=NVDA_DC_DEP_PCT,
    amd_dep_pct=AMD_DEP_PCT,
    oem_value_add_pct=OEM_VALUE_ADD_PCT
):
    """
    Calculates economic impact using the Mutator's model, but with the *corrected*
    logic for Gross Supply Void Duration as described in the thesis prose.
    """
    if quarantine_days <= chem_buffer_days:
        raise ValueError("Quarantine duration must be greater than chemical buffer days for this starvation scenario.")

    # CRITICAL CORRECTION: Gross Supply Void Duration based on Mutator's *prose* explanation.
    # Prose: "30-day remaining quarantine" (QUARANTINE_DAYS - CHEM_BUFFER_DAYS) + RESTART_DAYS + FAB_CYCLE_TIME_DAYS
    # Mutator's Python code incorrectly uses QUARANTINE_DAYS + RESTART_DAYS + FAB_CYCLE_TIME_DAYS,
    # effectively adding CHEM_BUFFER_DAYS to the void duration compared to its own prose.
    gross_supply_void_duration_days = (quarantine_days - chem_buffer_days) + restart_days + fab_cycle_time_days

    # Adjust for OEM Finished Goods Inventory Buffer
    effective_supply_void_days = gross_supply_void_duration_days - oem_inventory_days
    x_months = effective_supply_void_days / 30.0

    # Calculate Monthly Dependent OEM Revenue (Y_MONTHLY)
    apple_dep_monthly = (rev_aapl_hw_annual * aapl_hw_dep_pct) / 12.0
    nvidia_dep_monthly = (rev_nvda_dc_annual * nvda_dc_dep_pct) / 12.0
    amd_dep_monthly = (rev_amd_annual * amd_dep_pct) / 12.0
    y_monthly = apple_dep_monthly + nvidia_dep_monthly + amd_dep_monthly

    # Calculate Traceable Hardware Revenue Loss (Z_REV)
    z_rev = x_months * y_monthly

    # Calculate Direct Value-Added Loss
    direct_value_add_loss = z_rev * oem_value_add_pct

    # Calculate Foregone Investment in Digital Infrastructure
    nvda_dc_rev_void = nvidia_dep_monthly * x_months
    foregone_capex_impact = nvda_dc_rev_void * foregone_infra_capex_ratio

    # Total GDP Contraction (Z_GDP)
    z_gdp = direct_value_add_loss + foregone_capex_impact

    return {
        "effective_supply_void_months": x_months,
        "z_rev": z_rev,
        "direct_value_add_loss": direct_value_add_loss,
        "nvda_dc_rev_void": nvda_dc_rev_void,
        "foregone_capex_impact": foregone_capex_impact,
        "z_gdp": z_gdp
    }

# --- Counter-Test Execution ---
print("--- COUNTER-TEST RESULTS ---")

# Scenario 1: Re-evaluate Mutator's original parameters using the *corrected* prose logic.
# This exposes the discrepancy between the Mutator's prose and its Python code implementation.
mutator_prose_results = calculate_impact_with_corrected_logic(
    chem_buffer_days=CHEM_BUFFER_DAYS_MUTATOR,
    foregone_infra_capex_ratio=FOREGONE_INFRA_CAPEX_RATIO_MUTATOR
)

print("\nScenario 1: Mutator's Parameters with *Corrected* Prose Logic")
print(f"  Effective Supply Void Duration: {mutator_prose_results['effective_supply_void_months']:.2f} months (vs Mutator's code: {PREDICTED_EFFECTIVE_SUPPLY_VOID_MONTHS_MUTATOR:.2f} months)")
print(f"  Traceable Hardware Revenue Loss (Z_REV): ${mutator_prose_results['z_rev']:,.2f} USD (vs Mutator's code: ${PREDICTED_Z_REV_MUTATOR:,.2f} USD)")
print(f"  Traceable Global GDP Contraction (Z_GDP): ${mutator_prose_results['z_gdp']:,.2f} USD (vs Mutator's code: ${PREDICTED_Z_GDP_MUTATOR:,.2f} USD)")

# ASSERTION 1: The Mutator's Python code's predicted values *do not match* what its own prose implies.
# This demonstrates a fundamental calculation error in the Mutator's Python implementation.
tolerance_rev = 1e7 # $10 million
tolerance_gdp = 1e7 # $10 million
assert abs(mutator_prose_results['z_rev'] - PREDICTED_Z_REV_MUTATOR) > tolerance_rev, \
    f"ASSERTION FAILED: Mutator's Python code Z_REV ({PREDICTED_Z_REV_MUTATOR:,.2f}) unexpectedly matches its prose logic Z_REV ({mutator_prose_results['z_rev']:,.2f}), despite the calculation error."
assert abs(mutator_prose_results['z_gdp'] - PREDICTED_Z_GDP_MUTATOR) > tolerance_gdp, \
    f"ASSERTION FAILED: Mutator's Python code Z_GDP ({PREDICTED_Z_GDP_MUTATOR:,.2f}) unexpectedly matches its prose logic Z_GDP ({mutator_prose_results['z_gdp']:,.2f}), despite the calculation error."
print("  ASSERTION PASSED: Mutator's Python code results significantly diverge from its own prose logic, indicating a calculation error in the code's implementation of its stated model.")


# Scenario 2: Test with more conservative, yet plausible, parameters.
# This demonstrates the sensitivity of the model to impact-maximizing choices.
CONSERVATIVE_CHEM_BUFFER_DAYS = 40  # Mid-point of the 30-45 day range
CONSERVATIVE_FOREGONE_CAPEX_RATIO = 1.5  # Less aggressive multiplier (vs 2.5x)

conservative_results = calculate_impact_with_corrected_logic(
    chem_buffer_days=CONSERVATIVE_CHEM_BUFFER_DAYS,
    foregone_infra_capex_ratio=CONSERVATIVE_FOREGONE_CAPEX_RATIO
)

print(f"\nScenario 2: Conservative Parameters (CHEM_BUFFER_DAYS={CONSERVATIVE_CHEM_BUFFER_DAYS}, FOREGONE_INFRA_CAPEX_RATIO={CONSERVATIVE_FOREGONE_CAPEX_RATIO}) with Corrected Prose Logic")
print(f"  Effective Supply Void Duration: {conservative_results['effective_supply_void_months']:.2f} months")
print(f"  Traceable Hardware Revenue Loss (Z_REV): ${conservative_results['z_rev']:,.2f} USD")
print(f"  Direct Value-Added Loss (component of Z_GDP): ${conservative_results['direct_value_add_loss']:,.2f} USD")
print(f"  Foregone Infra CAPEX Impact (component of Z_GDP): ${conservative_results['foregone_capex_impact']:,.2f} USD")
print(f"  Traceable Global GDP Contraction (Z_GDP): ${conservative_results['z_gdp']:,.2f} USD")

# ASSERTION 2: The GDP contraction is significantly lower under more conservative, yet plausible, assumptions.
# This exposes the sensitivity to the Mutator's impact-maximizing parameter choices.
assert conservative_results['z_gdp'] < PREDICTED_Z_GDP_MUTATOR * 0.7, \
    f"ASSERTION FAILED: Conservative scenario Z_GDP ({conservative_results['z_gdp']:,.2f}) is not significantly lower than Mutator's predicted Z_GDP ({PREDICTED_Z_GDP_MUTATOR:,.2f})."
print("  ASSERTION PASSED: Conservative parameter choices, combined with the corrected logic, significantly reduce the estimated GDP contraction, demonstrating sensitivity to 'impact-maximizing' assumptions.")

```

### PYTHON EXECUTION OUTPUT:
--- COUNTER-TEST RESULTS ---

Scenario 1: Mutator's Parameters with *Corrected* Prose Logic
  Effective Supply Void Duration: 5.33 months (vs Mutator's code: 6.33 months)
  Traceable Hardware Revenue Loss (Z_REV): $196,866,666,666.67 USD (vs Mutator's code: $233,740,000,000.00 USD)
  Traceable Global GDP Contraction (Z_GDP): $219,822,222,222.22 USD (vs Mutator's code: $261,040,000,000.00 USD)
  ASSERTION PASSED: Mutator's Python code results significantly diverge from its own prose logic, indicating a calculation error in the code's implementation of its stated model.

Scenario 2: Conservative Parameters (CHEM_BUFFER_DAYS=40, FOREGONE_INFRA_CAPEX_RATIO=1.5) with Corrected Prose Logic
  Effective Supply Void Duration: 5.00 months
  Traceable Hardware Revenue Loss (Z_REV): $184,562,500,000.00 USD
  Direct Value-Added Loss (component of Z_GDP): $92,281,250,000.00 USD
  Foregone Infra CAPEX Impact (component of Z_GDP): $68,281,250,000.00 USD
  Traceable Global GDP Contraction (Z_GDP): $160,562,500,000.00 USD
  ASSERTION PASSED: Conservative parameter choices, combined with the corrected logic, significantly reduce the estimated GDP contraction, demonstrating sensitivity to 'impact-maximizing' assumptions.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 73, in <module>
    assert abs(Z_REV - PREDICTED_Z_REV) < 1e7, f"Traceable Hardware Revenue Loss (Z_REV) mismatch: Expected {PREDICTED_Z_REV}, Got {Z_REV}"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Traceable Hardware Revenue Loss (Z_REV) mismatch: Expected 233740000000.0, Got 233779166666.66666


# Final Score: 30
**Weakest Point:** The thesis contains a fundamental mathematical error in calculating the gross supply void duration, leading to an overstatement of economic impact, and re-introduces a significant multiplier (FOREGONE_INFRA_CAPEX_RATIO) under new nomenclature, directly contradicting its stated methodological pivot. This is compounded by its failure to pass its own internal unit tests.
**Rationale:** The Mutator's thesis commendably pivots to a more granular, bottom-up approach for GDP impact assessment, moving away from generic multipliers and providing detailed supply chain paths. However, its analytical rigor is severely undermined by several critical flaws. There is a fundamental mathematical error in the calculation of the 'GROSS_SUPPLY_VOID_DURATION_DAYS', which inflates the projected economic impact by implicitly double-counting the chemical buffer period. Furthermore, the thesis re-introduces a significant multiplier ('FOREGONE_INFRA_CAPEX_RATIO') under a new name, contradicting its stated aim of bypassing such heuristics. The model's reliance on impact-maximizing parameters (e.g., the lowest end of chemical buffer estimates, exceptionally high OEM dependency percentages, and an aggressive CAPEX ratio) consistently leads to an overestimation of the crisis's severity by failing to incorporate plausible adaptive responses and strategic interventions like emergency stockpiling or accelerated recovery. The thesis also failed its own internal unit tests, indicating a lack of precision or internal consistency in its self-reported predictions. While the detailed breakdown of substitution impossibility is well-executed, these significant issues compromise the model's overall solvency and the accuracy of its catastrophic predictions.
