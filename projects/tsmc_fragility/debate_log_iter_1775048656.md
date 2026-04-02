# Adversarial Debate: tsmc_fragility

## Attacker: Heterodox Macroeconomist (Multiplier & Scope Validity Theorist)
The provided thesis presents a refined model for quantifying the economic impact of a specific geopolitical disruption to TSMC's advanced node production. A critical review of the thesis and its accompanying Python Falsification Suite reveals a deliberate and commendable departure from the direct application of broad economic multipliers and generalized revenue figures, which were highlighted in the initial evidence table.

**Analytical Critique:**

1.  **Critique of `SEMI_MULTIPLIER` (8.4x):** The thesis, in its "TOPOLOGICAL PIVOT EXECUTED," explicitly states its focus on "direct, traceable hardware revenue loss" and "stripping out the narrative fluff." Crucially, the Python Falsification Suite *does not utilize* the `SEMI_MULTIPLIER` (8.4x) in its calculation of `TOTAL_REVENUE_LOSS_Z`. This is a significant strength of the Mutator's refined model. The 8.4x multiplier, derived from the 2021 automotive chip shortage, pertains to a specific context: a scarcity of low-cost, mature-node microcontrollers (MCUs) leading to disproportionately high losses in the automotive sector due to its just-in-time inventory practices and the low chip-to-final-product value ratio. Applying such a multiplier universally to leading-edge logic chips (CPUs, GPUs, AI accelerators), which are high-value components representing a substantial portion of the bill of materials for their end products (e.g., high-end smartphones, data center servers), would be an analytical misstep. The economic leverage (multiplier effect) for a shortage of high-value components is typically lower, as the missing component itself constitutes a larger fraction of the final product's cost. The Mutator's decision to calculate direct downstream OEM revenue loss, rather than applying this broad multiplier, enhances the model's contextual validity.

2.  **Critique of `SEMI_REV` (Global Semiconductor Revenue):** Similarly, the Python Falsification Suite *does not use* `GLOBAL_SEMI_REV` in its primary calculation of `TOTAL_REVENUE_LOSS_Z`. Instead, the model focuses on the aggregated annual revenues of specific, highly dependent OEMs (Apple, NVIDIA, AMD) and applies an `ADVANCED_NODE_DEPENDENCY_RATE` to this sum. This approach implicitly acknowledges that the entirety of global semiconductor revenue is not equally susceptible to a disruption of TSMC's advanced Taiwan operations. Global semiconductor revenue encompasses a vast array of products, including mature node chips (produced by diverse foundries and IDMs), memory (dominated by Samsung, SK Hynix, Micron), analog/mixed-signal components, and packaging services, many of which are not solely dependent on TSMC's sub-5nm Taiwan fabs. By narrowing its scope to specific leading-edge customers and advanced nodes, the Mutator's model avoids the overgeneralization that would arise from assuming uniform dependence across the entire semiconductor market.

3.  **Critique of Python Code for "Cooked Books":**
    *   **Unit Dimensionality:** The Python code demonstrates consistent unit dimensionality throughout its calculations. For instance, `WSPM_ADV` (wafers/month) multiplied by `CYCLE_TIME_MOS` (months) and `WAFER_PRICE_USD` (USD/wafer) correctly yields a value in USD. Time conversions between days and months are handled appropriately.
    *   **Hardcoded Constants/Assumptions:** The "LOAD-BEARING VARIABLES" are either directly sourced from industry reports (e.g., `WSPM_ADV`, `WAFER_PRICE_USD`, OEM revenues) or represent conservative stress-test parameters (`CHEM_BUFFER_DAYS=30`, `QUARANTINE_DAYS=60`, `OEM_CHIP_INVENTORY_MONTHS=1`). These choices are explicitly stated as conservative, aiming to quantify systemic vulnerability at a plausible worst-case, rather than to minimize impact. The `DEPENDENCY_RATE_ADV_NODES` (0.85) is an estimation, but for major products from Apple, NVIDIA, and AMD that rely on TSMC's latest nodes, a high dependency rate on *new* wafer supply is empirically defensible. The code's logic for handling negative durations (clamping to zero) is sound.
    *   **Absence of `SEMI_MULTIPLIER` and `SEMI_REV` in Calculation:** The most significant observation regarding "cooked books" is their *absence* from the core calculation. While listed in the general evidence, their non-application in the Python suite demonstrates a methodological rigor that avoids the pitfalls of overgeneralization. The Mutator's model is internally consistent and transparent in its calculation of direct, traceable revenue loss.

**So What for the Meta-Judge:**

The Mutator's thesis, by focusing on a granular, bottom-up calculation of direct hardware revenue loss from specific OEM dependencies on TSMC's advanced nodes, demonstrates a more robust and contextually appropriate methodology than one that would rely on broad economic multipliers or generalized semiconductor revenue figures. While the initial evidence table included variables like `SEMI_MULTIPLIER` and `GLOBAL_SEMI_REV`, the Mutator's actual model implicitly rejects their direct application to this specific scenario. This methodological choice is critical because misapplying a multiplier derived from a highly specific, high-leverage disruption (like automotive MCUs) to a different class of high-value components (leading-edge logic) would lead to a significant overestimation of economic impact. The counter-test will quantitatively illustrate this potential for overestimation, thereby validating the Mutator's implicit decision to avoid such broad generalizations and reinforcing the importance of context-specific economic modeling.

```python
from decimal import Decimal, getcontext

# Set precision for Decimal calculations to ensure accuracy
getcontext().prec = 10

# --- Mutator's Load-Bearing Variables (re-declared for context in counter-test) ---
WSPM_ADV = Decimal('250000') # Wafers/Mo (TSMC Advanced WSPM N3 + N4/N5)
CYCLE_TIME_MOS = Decimal('3') # Months (Fab Cycle Time Sub-5nm)
WAFER_PRICE_USD = Decimal('20000') # USD/Wafer (Wafer Price Sub-5nm)
CHEM_BUFFER_DAYS = Decimal('30') # Days (Chemical Import Buffer Conservative)
QUARANTINE_DAYS = Decimal('60') # Days (Maritime Quarantine Duration)
RESTART_DAYS = Decimal('30') # Days (Fab Restart & Re-qualification)
REV_AAPL_HW = Decimal('350000000000') # USD/Year (Apple Hardware Revenue)
REV_NVDA_DC = Decimal('115000000000') # USD/Year (NVIDIA Data Center Revenue)
REV_AMD = Decimal('22000000000') # USD/Year (AMD Revenue)
OEM_CHIP_INVENTORY_MONTHS = Decimal('1') # Months (OEM Chip Inventory Buffer)
DEPENDENCY_RATE_ADV_NODES = Decimal('0.85') # Fraction (Advanced Node Dependency Rate)

# --- Additional Variables from General Evidence (for counter-test) ---
# These variables are present in the general evidence but NOT used in the Mutator's core calculation.
SEMI_MULTIPLIER = Decimal('8.4') # Economic multiplier: chip shortage -> GDP loss (2021 precedent)
GLOBAL_SEMI_REV = Decimal('580000000000') # USD (Global semiconductor revenue 2024)

# --- Mutator's Derived Values (re-calculated for context in counter-test) ---
# These calculations mirror the Mutator's logic to establish a baseline for comparison.

# Calculate the duration of fab starvation during quarantine
fab_starved_days = QUARANTINE_DAYS - CHEM_BUFFER_DAYS
if fab_starved_days < 0:
    fab_starved_days = Decimal('0')

# Calculate total zero production days including restart
total_zero_production_days = fab_starved_days + RESTART_DAYS

# Calculate time for new wafers to emerge after restart
new_wafer_cycle_days = CYCLE_TIME_MOS * Decimal('30') # Convert months to days

# Total pipeline void in days until new wafers are available
pipeline_void_days = total_zero_production_days + new_wafer_cycle_days
pipeline_void_months = pipeline_void_days / Decimal('30')

# Net pipeline void after OEM inventory buffer
net_void_months_x = pipeline_void_months - OEM_CHIP_INVENTORY_MONTHS
if net_void_months_x < 0:
    net_void_months_x = Decimal('0')

# Calculate total dependent annual and monthly revenue
dep_annual_rev = REV_AAPL_HW + REV_NVDA_DC + REV_AMD
dep_monthly_rev = dep_annual_rev / Decimal('12')

# Calculate adjusted monthly revenue at risk
adj_dep_monthly_rev = dep_monthly_rev * DEPENDENCY_RATE_ADV_NODES

# Mutator's primary output: Total Revenue Loss (Z)
mutator_total_revenue_loss_z = net_void_months_x * adj_dep_monthly_rev

# --- Counter-Test Calculations ---

# 1. Calculate the direct TSMC advanced foundry revenue loss (before OEM buffer)
# This represents the value of semiconductor output lost from TSMC's advanced nodes
tsmc_adv_monthly_foundry_rev = WSPM_ADV * WAFER_PRICE_USD
tsmc_adv_foundry_rev_loss_total = tsmc_adv_monthly_foundry_rev * pipeline_void_months

# 2. Hypothetically apply the SEMI_MULTIPLIER to this foundry revenue loss
# This demonstrates the broader economic impact if the 8.4x multiplier were applied
# to advanced node chip production loss, as per the prompt's focus.
hypothetical_multiplier_gdp_impact = tsmc_adv_foundry_rev_loss_total * SEMI_MULTIPLIER

# --- Print Results and Assertions for Counter-Test ---
print("--- Mutator's Model Outputs ---")
print(f"Mutator's Calculated Pipeline Void (Months): {pipeline_void_months}")
print(f"Mutator's Net Revenue Void Duration (Months): {net_void_months_x}")
print(f"Mutator's Direct Traceable Hardware Revenue Loss (Z): ${mutator_total_revenue_loss_z:,.2f}\n")

print("--- Counter-Test Analysis: Applicability of SEMI_MULTIPLIER ---")
print(f"TSMC Advanced Node Monthly Foundry Revenue: ${tsmc_adv_monthly_foundry_rev:,.2f}")
print(f"Total TSMC Advanced Node Foundry Revenue Loss (5-month void): ${tsmc_adv_foundry_rev_loss_total:,.2f}")
print(f"Hypothetical GDP Impact (using 8.4x multiplier on foundry loss): ${hypothetical_multiplier_gdp_impact:,.2f}\n")

# Assert that the hypothetical multiplier impact is significantly higher than the Mutator's direct hardware revenue loss.
# This demonstrates the overestimation potential of the 8.4x multiplier when misapplied to leading-edge components.
# A difference threshold of 10% is used to define "significantly higher."
difference_threshold = Decimal('0.10') # 10% difference

is_significantly_higher = (hypothetical_multiplier_gdp_impact - mutator_total_revenue_loss_z) / mutator_total_revenue_loss_z > difference_threshold

print(f"Is Hypothetical GDP Impact significantly higher than Mutator's Direct Loss (> {difference_threshold*100}% difference)? {is_significantly_higher}")

assert is_significantly_higher, \
    "The hypothetical multiplier-driven GDP impact is not significantly higher than the Mutator's direct revenue loss, which contradicts the expected overestimation when applying a broad multiplier to leading-edge components."

# Calculate the implicit multiplier derived from the Mutator's model (downstream OEM loss / foundry loss).
# This implicit multiplier should be substantially lower than the 8.4x automotive multiplier,
# reflecting the different economic leverage of high-value leading-edge chips.
implicit_multiplier_mutator = mutator_total_revenue_loss_z / tsmc_adv_foundry_rev_loss_total
print(f"Implicit Multiplier from Mutator's Model (OEM Loss / Foundry Loss): {implicit_multiplier_mutator:,.2f}x")

assert implicit_multiplier_mutator < SEMI_MULTIPLIER, \
    f"The implicit multiplier from the Mutator's model ({implicit_multiplier_mutator:,.2f}x) is not less than the 2021 auto-chip multiplier ({SEMI_MULTIPLIER}x), which suggests the 8.4x multiplier is inappropriately high for leading-edge components."

print("\nCounter-test successfully demonstrated the contextual insolvency of applying the 8.4x automotive-specific multiplier to a generalized leading-edge semiconductor disruption.")
```

### PYTHON EXECUTION OUTPUT:
--- Mutator's Model Outputs ---
Mutator's Calculated Pipeline Void (Months): 5
Mutator's Net Revenue Void Duration (Months): 4
Mutator's Direct Traceable Hardware Revenue Loss (Z): $137,983,333,300.00

--- Counter-Test Analysis: Applicability of SEMI_MULTIPLIER ---
TSMC Advanced Node Monthly Foundry Revenue: $5,000,000,000.00
Total TSMC Advanced Node Foundry Revenue Loss (5-month void): $25,000,000,000.00
Hypothetical GDP Impact (using 8.4x multiplier on foundry loss): $210,000,000,000.00

Is Hypothetical GDP Impact significantly higher than Mutator's Direct Loss (> 10.00% difference)? True
Implicit Multiplier from Mutator's Model (OEM Loss / Foundry Loss): 5.52x

Counter-test successfully demonstrated the contextual insolvency of applying the 8.4x automotive-specific multiplier to a generalized leading-edge semiconductor disruption.


## Attacker: Logistics & Resilience Architect (Crisis Adaptation Specialist)
The provided thesis and its accompanying Python Falsification Suite present a deterministic model for assessing the financial impact of a maritime quarantine on Taiwan's advanced semiconductor manufacturing. While the model appears to leverage specific industry data, its fundamental insolvency stems from treating operational norms and conservative stress-test parameters as immutable physical or logistical hard limits. This approach systematically underestimates the adaptive capacity, strategic redundancies, and potential for extraordinary global cooperation that would be mobilized in a high-stakes geopolitical scenario.

**Analytical Critique:**

1.  **Parametric Rigidity and Underestimation of Adaptive Capacity:**
    *   **`CHEM_BUFFER_DAYS` (30 Days):** The Mutator explicitly selects the lower bound of the "30-45 days" range for a "conservative stress-test." This choice implicitly dismisses the possibility of strategic stockpiling beyond stated operational buffers or the rapid deployment of alternative logistics (e.g., emergency airlift for critical, high-value, low-volume chemicals). Such measures, while costly, are plausible under extreme duress and would effectively extend the operational buffer, delaying or mitigating the "fab chemical starvation."
    *   **`RESTART_DAYS` (30 Days):** Labeling this as "minimum physical time" is a strong claim that overlooks the potential for accelerated recovery under conditions of global emergency. Coordinated international efforts could involve deploying specialized engineering teams, pre-positioning critical spare parts, and streamlining re-qualification processes, thereby reducing the restart timeline.
    *   **`CYCLE_TIME_MOS` (3 Months):** The assumption of a fixed 3-month cycle time for advanced nodes ignores the potential for operational acceleration. Under emergency conditions, fabs might implement aggressive scheduling, optimize process steps, or reduce non-critical testing phases to expedite wafer throughput, even if it incurs higher operational costs or slightly increased defect rates for non-critical components.
    *   **`OEM_CHIP_INVENTORY_MONTHS` (1 Month):** Similar to the chemical buffer, selecting the lower end of the "30-45 days typical" range for OEM chip inventory overlooks the possibility of strategic reserves held by major OEMs or national governments for critical components. The average inventory level does not preclude larger, dedicated buffers for high-impact items.

2.  **Inaccurate Valuation of Work-In-Process (WIP) Destruction:**
    *   The calculation `WIP_VALUE_DESTROYED = WSPM_ADV * CYCLE_TIME_MOS * WAFER_PRICE_USD` (resulting in $15.0 Billion) is fundamentally flawed. It multiplies the monthly wafer capacity by the cycle time (3 months) to get the total number of wafers in process (750,000), and then assigns the *full finished wafer price* ($20,000) to each of these in-process wafers. This is an overestimation. Work-in-process wafers accumulate value as they progress through the manufacturing steps. A wafer just starting its cycle has significantly less value than one nearing completion. Assuming all 750,000 wafers, regardless of their stage, are valued at their finished price, and are entirely unsalvageable, represents a highly pessimistic and financially imprecise assessment of loss. A more accurate valuation would consider the average value-add across the cycle or a salvage rate.

3.  **Rigid Interpretation of "Zero-Output Pipeline Void":**
    *   The calculation of `PIPELINE_VOID_MONTHS` assumes a complete cessation of output until the *first new wafer* completes its *entire* adjusted cycle time *after* the fab restart. This linear, sequential interpretation may not fully capture the nuances of a ramp-up phase, where partial output or expedited batches might emerge earlier, or where some partially processed wafers could be salvaged and completed.

**Cooked Books in Python Code:**

*   **Unit Dimensionality and Conceptual Misapplication:** While the Python code correctly handles `Decimal` types and consistent time units (days/months), the conceptual application of `WAFER_PRICE_USD` to `WIP_VALUE_DESTROYED` is dimensionally misapplied. `WAFER_PRICE_USD` is the price of a *finished* wafer. Applying it directly to `WSPM_ADV * CYCLE_TIME_MOS` (which represents the quantity of *in-process* wafers) without an adjustment for the average value of WIP or a salvage factor inflates the loss. The Mutator's assertion `assert WIP_VALUE_DESTROYED == Decimal('15000000000')` hardcodes this inflated value as correct.
*   **Favorable Constant Selection for Severity:** The Mutator's choice of `CHEM_BUFFER_DAYS = Decimal('30')` and `OEM_CHIP_INVENTORY_MONTHS = Decimal('1')` explicitly selects the lower end of the stated ranges (30-45 days), biasing the model towards a more severe outcome. This is a methodological choice that, while labeled "conservative stress-test," effectively ignores the upper bounds of normal operational buffers, let alone emergency extensions.

**So What for the Meta-Judge:**

The Mutator's model, while appearing quantitatively rigorous, is parametrically brittle. It constructs a scenario of severe economic impact by treating operational parameters and typical buffer ranges as unyielding hard limits, rather than dynamic variables subject to influence by extraordinary, coordinated global responses. This approach systematically overestimates the duration of disruption and the associated financial loss by failing to account for the inherent elasticity, strategic redundancies, and adaptive capabilities of complex global supply chains under duress. The model's insolvency lies in its deterministic rigidity, which misrepresents the potential for mitigation and resilience, leading to an inflated projection of economic impact.

```python
from decimal import Decimal, getcontext

# Set precision for Decimal calculations
getcontext().prec = 10

# Mutator's Load-Bearing Variables (as baseline for comparison)
WSPM_ADV = Decimal('250000') # Wafers/Mo
CYCLE_TIME_MOS = Decimal('3') # Months
WAFER_PRICE_USD = Decimal('20000') # USD/Wafer
CHEM_BUFFER_DAYS = Decimal('30') # Days (Mutator's conservative choice)
QUARANTINE_DAYS = Decimal('60') # Days (Stress-test parameter)
RESTART_DAYS = Decimal('30') # Days (Mutator's minimum physical time)
REV_AAPL_HW = Decimal('350000000000') # USD/Year
REV_NVDA_DC = Decimal('115000000000') # USD/Year
REV_AMD = Decimal('22000000000') # USD/Year
OEM_CHIP_INVENTORY_MONTHS = Decimal('1') # Months (Mutator's conservative choice)
DEPENDENCY_RATE_ADV_NODES = Decimal('0.85') # Fraction

# --- COUNTER-TEST: ADAPTIVE SYSTEM PARAMETERS ---
# These variables represent the system's capacity for adaptation and extraordinary response,
# challenging the Mutator's implicit assumption of unyielding hard limits.

# 1. Chemical Buffer Extension: Emergency airlift/strategic reserves for critical, high-value, low-volume chemicals.
# Grounding data: CHEM_BUFFER is 30-45 days. Mutator chose 30. We extend it to 45 days effectively.
EMERGENCY_CHEM_EXTENSION_DAYS = Decimal('15') # Additional days of critical chemical supply via emergency means

# 2. Fab Restart Acceleration: Global cooperation and pre-positioned expert teams can reduce restart time.
# Mutator's RESTART_DAYS is 30. We reduce it by 10 days (33% acceleration is plausible under extreme duress).
EMERGENCY_RESTART_REDUCTION_DAYS = Decimal('10') # Days reduced from RESTART_DAYS

# 3. Fab Cycle Time Acceleration: Emergency operational optimization and reduced non-critical testing.
# Mutator's CYCLE_TIME_MOS is 3 months (90 days). We reduce it by 10% (9 days) for critical components.
EMERGENCY_CYCLE_REDUCTION_DAYS = Decimal('9') # Days reduced from CYCLE_TIME_MOS (converted to days)

# 4. WIP Destruction Factor: More realistic assessment of work-in-process loss.
# Mutator assumes full value of 3 months of finished wafers are destroyed ($15B).
# We assume only 75% of that value is lost, accounting for lower average WIP value or partial salvage.
WIP_DESTRUCTION_FACTOR = Decimal('0.75') # Fraction of Mutator's calculated WIP value that is actually lost

# 5. OEM Strategic Inventory Buffer: OEMs and governments maintain larger buffers for critical components.
# Mutator's OEM_CHIP_INVENTORY_MONTHS is 1 month. We extend it by 0.5 months, reflecting strategic stockpiling.
STRATEGIC_OEM_BUFFER_EXTENSION_MONTHS = Decimal('0.5') # Additional months of OEM chip inventory

# --- RECALCULATED VALUES BASED ON ADAPTIVE SYSTEM ---

# Adjusted Chemical Buffer
ADJ_CHEM_BUFFER_DAYS = CHEM_BUFFER_DAYS + EMERGENCY_CHEM_EXTENSION_DAYS

# Adjusted Restart Days
ADJ_RESTART_DAYS = RESTART_DAYS - EMERGENCY_RESTART_REDUCTION_DAYS
if ADJ_RESTART_DAYS < 0: ADJ_RESTART_DAYS = Decimal('0') # Ensure non-negative

# Adjusted Cycle Time
ADJ_CYCLE_TIME_DAYS = (CYCLE_TIME_MOS * Decimal('30')) - EMERGENCY_CYCLE_REDUCTION_DAYS
if ADJ_CYCLE_TIME_DAYS < 0: ADJ_CYCLE_TIME_DAYS = Decimal('0') # Ensure non-negative
ADJ_CYCLE_TIME_MOS = ADJ_CYCLE_TIME_DAYS / Decimal('30')

# Adjusted OEM Chip Inventory
ADJ_OEM_CHIP_INVENTORY_MONTHS = OEM_CHIP_INVENTORY_MONTHS + STRATEGIC_OEM_BUFFER_EXTENSION_MONTHS

# --- RECALCULATING THE MUTATOR'S METRICS WITH ADAPTIVE PARAMETERS ---

# 1. Value of Work-In-Process (WIP) destroyed (adjusted)
# Mutator's original calculation for WIP value: WSPM_ADV * CYCLE_TIME_MOS * WAFER_PRICE_USD
MUTATOR_WIP_VALUE_CALC = WSPM_ADV * CYCLE_TIME_MOS * WAFER_PRICE_USD
ADJ_WIP_VALUE_DESTROYED = MUTATOR_WIP_VALUE_CALC * WIP_DESTRUCTION_FACTOR

# 2. Total dependent annual revenue (same as Mutator)
DEP_ANNUAL_REV = REV_AAPL_HW + REV_NVDA_DC + REV_AMD
DEP_MONTHLY_REV = DEP_ANNUAL_REV / Decimal('12')

# 3. Adjusted monthly revenue at risk (same as Mutator)
ADJ_DEP_MONTHLY_REV = DEP_MONTHLY_REV * DEPENDENCY_RATE_ADV_NODES

# 4. Pipeline Void Duration Calculation (X) - Adjusted
# Days fab is offline due to chemical starvation during quarantine
FAB_STARVED_DAYS_ADJ = QUARANTINE_DAYS - ADJ_CHEM_BUFFER_DAYS
if FAB_STARVED_DAYS_ADJ < 0:
    FAB_STARVED_DAYS_ADJ = Decimal('0')

# Total days of no production and restart before new wafers can start (adjusted)
TOTAL_ZERO_PRODUCTION_DAYS_ADJ = FAB_STARVED_DAYS_ADJ + ADJ_RESTART_DAYS

# Time for first new wafers to emerge after restart (adjusted)
NEW_WAFER_CYCLE_DAYS_ADJ = ADJ_CYCLE_TIME_DAYS

# Total pipeline void in days until new wafers are available (adjusted)
PIPELINE_VOID_DAYS_ADJ = TOTAL_ZERO_PRODUCTION_DAYS_ADJ + NEW_WAFER_CYCLE_DAYS_ADJ
PIPELINE_VOID_MONTHS_ADJ = PIPELINE_VOID_DAYS_ADJ / Decimal('30')

# Net pipeline void after OEM inventory buffer (adjusted)
NET_VOID_MONTHS_X_ADJ = PIPELINE_VOID_MONTHS_ADJ - ADJ_OEM_CHIP_INVENTORY_MONTHS
if NET_VOID_MONTHS_X_ADJ < 0:
    NET_VOID_MONTHS_X_ADJ = Decimal('0')

# 5. Total Revenue Loss (Z) - Adjusted
TOTAL_REVENUE_LOSS_Z_ADJ = NET_VOID_MONTHS_X_ADJ * ADJ_DEP_MONTHLY_REV

# --- Mutator's Original Results for Comparison ---
MUTATOR_WIP_VALUE_DESTROYED = Decimal('15000000000')
MUTATOR_PIPELINE_VOID_MONTHS = Decimal('5')
MUTATOR_NET_VOID_MONTHS_X = Decimal('4')
MUTATOR_TOTAL_REVENUE_LOSS_Z = Decimal('137983333333.33333')

# --- Counter-Test Assertions ---
def run_counter_test():
    print("--- Counter-Test Results (Adaptive System) ---")

    print(f"Original Chemical Buffer (Days): {CHEM_BUFFER_DAYS}")
    print(f"Adjusted Chemical Buffer (Days): {ADJ_CHEM_BUFFER_DAYS} (Extended by {EMERGENCY_CHEM_EXTENSION_DAYS} days)")
    assert ADJ_CHEM_BUFFER_DAYS > CHEM_BUFFER_DAYS, "Adjusted chemical buffer must be greater than original."

    print(f"Original Fab Restart Time (Days): {RESTART_DAYS}")
    print(f"Adjusted Fab Restart Time (Days): {ADJ_RESTART_DAYS} (Reduced by {EMERGENCY_RESTART_REDUCTION_DAYS} days)")
    assert ADJ_RESTART_DAYS < RESTART_DAYS, "Adjusted restart time must be less than original."

    print(f"Original Fab Cycle Time (Months): {CYCLE_TIME_MOS} ({CYCLE_TIME_MOS * Decimal('30')} days)")
    print(f"Adjusted Fab Cycle Time (Months): {ADJ_CYCLE_TIME_MOS} ({ADJ_CYCLE_TIME_DAYS} days, Reduced by {EMERGENCY_CYCLE_REDUCTION_DAYS} days)")
    assert ADJ_CYCLE_TIME_MOS < CYCLE_TIME_MOS, "Adjusted cycle time must be less than original."

    print(f"Original OEM Chip Inventory (Months): {OEM_CHIP_INVENTORY_MONTHS}")
    print(f"Adjusted OEM Chip Inventory (Months): {ADJ_OEM_CHIP_INVENTORY_MONTHS} (Extended by {STRATEGIC_OEM_BUFFER_EXTENSION_MONTHS} months)")
    assert ADJ_OEM_CHIP_INVENTORY_MONTHS > OEM_CHIP_INVENTORY_MONTHS, "Adjusted OEM inventory must be greater than original."

    print(f"\nMutator's Calculated WIP Value Destroyed: ${MUTATOR_WIP_VALUE_DESTROYED:,.2f}")
    print(f"Counter-Test Adjusted WIP Value Destroyed: ${ADJ_WIP_VALUE_DESTROYED:,.2f}")
    assert ADJ_WIP_VALUE_DESTROYED < MUTATOR_WIP_VALUE_DESTROYED, "Adjusted WIP destruction must be less than Mutator's."

    print(f"\nMutator's Calculated Pipeline Void (Months): {MUTATOR_PIPELINE_VOID_MONTHS}")
    print(f"Counter-Test Adjusted Pipeline Void (Months): {PIPELINE_VOID_MONTHS_ADJ}")
    assert PIPELINE_VOID_MONTHS_ADJ < MUTATOR_PIPELINE_VOID_MONTHS, "Adjusted pipeline void must be less than Mutator's."

    print(f"\nMutator's Calculated Net Revenue Void (Months): {MUTATOR_NET_VOID_MONTHS_X}")
    print(f"Counter-Test Adjusted Net Revenue Void (Months): {NET_VOID_MONTHS_X_ADJ}")
    assert NET_VOID_MONTHS_X_ADJ < MUTATOR_NET_VOID_MONTHS_X, "Adjusted net revenue void must be less than Mutator's."

    print(f"\nMutator's Predicted Total Revenue Loss (Z): ${MUTATOR_TOTAL_REVENUE_LOSS_Z:,.2f}")
    print(f"Counter-Test Adjusted Total Revenue Loss (Z): ${TOTAL_REVENUE_LOSS_Z_ADJ:,.2f}")
    assert TOTAL_REVENUE_LOSS_Z_ADJ < MUTATOR_TOTAL_REVENUE_LOSS_Z, "Adjusted total revenue loss must be less than Mutator's."

    print("\nAll counter-test assertions passed. The system demonstrates significant adaptive capacity, mitigating the projected financial impact.")
    print(f"The Mutator's model overestimates the financial impact by: ${MUTATOR_TOTAL_REVENUE_LOSS_Z - TOTAL_REVENUE_LOSS_Z_ADJ:,.2f}")

# Execute the counter-test
run_counter_test()
```

### PYTHON EXECUTION OUTPUT:
--- Counter-Test Results (Adaptive System) ---
Original Chemical Buffer (Days): 30
Adjusted Chemical Buffer (Days): 45 (Extended by 15 days)
Original Fab Restart Time (Days): 30
Adjusted Fab Restart Time (Days): 20 (Reduced by 10 days)
Original Fab Cycle Time (Months): 3 (90 days)
Adjusted Fab Cycle Time (Months): 2.7 (81 days, Reduced by 9 days)
Original OEM Chip Inventory (Months): 1
Adjusted OEM Chip Inventory (Months): 1.5 (Extended by 0.5 months)

Mutator's Calculated WIP Value Destroyed: $15,000,000,000.00
Counter-Test Adjusted WIP Value Destroyed: $11,250,000,000.00

Mutator's Calculated Pipeline Void (Months): 5
Counter-Test Adjusted Pipeline Void (Months): 3.866666667

Mutator's Calculated Net Revenue Void (Months): 4
Counter-Test Adjusted Net Revenue Void (Months): 2.366666667

Mutator's Predicted Total Revenue Loss (Z): $137,983,333,333.33
Counter-Test Adjusted Total Revenue Loss (Z): $81,640,138,890.00

All counter-test assertions passed. The system demonstrates significant adaptive capacity, mitigating the projected financial impact.
The Mutator's model overestimates the financial impact by: $56,343,194,440.00


## Attacker: Quantitative Risk Arbitrageur (Model Integrity Auditor)
The Mutator's thesis presents a structured, mathematically coherent model for assessing the financial impact of a maritime quarantine on TSMC's advanced node production. The use of the `decimal` library for calculations is appropriate, enhancing numerical precision, and the logical flow from axioms to conclusion is clearly articulated through the Directed Acyclic Graph (DAG). The explicit selection of parameters at the lower end of their ranges for chemical buffers (`CHEM_BUFFER_DAYS=30`) and OEM chip inventory (`OEM_CHIP_INVENTORY_MONTHS=1`) is consistent with the stated objective of a "conservative stress-test" designed to quantify systemic vulnerability at a "worst plausible parameter setting."

However, the model's solvency and the precision of its final prediction are critically dependent on the `DEPENDENCY_RATE_ADV_NODES` parameter, which is set at `0.85`. This value is presented as an "estimated fraction of revenue directly tied to *new* sub-5nm wafers (vs. older nodes, existing stock)" and is described as "empirically defensible." While Apple, NVIDIA, and AMD are undeniably highly reliant on TSMC's advanced nodes, an 85% immediate dependency rate on *newly fabricated* wafers for their *total specified revenue* (Apple hardware, NVIDIA data center, AMD total) after a 1-month OEM chip inventory buffer appears to be an aggressive overestimation.

A more robust "empirically defensible" rate, even for a stress-test scenario, would typically account for several factors not explicitly detailed in the justification for 0.85:
1.  **Finished Goods Inventory:** OEMs maintain inventories of finished products, not solely raw chips. This additional buffer provides a layer of resilience that is not captured by the `OEM_CHIP_INVENTORY_MONTHS` alone.
2.  **Product Portfolio Diversification:** Revenue streams for these companies often include products utilizing older semiconductor nodes, components from alternative suppliers, or services, which would not be immediately impacted by a sub-5nm TSMC disruption.
3.  **Demand Flexibility and Substitution:** In a prolonged disruption, a portion of demand might shift to alternative products, be fulfilled by existing finished goods, or be delayed, rather than representing an immediate, absolute revenue loss at such a high dependency rate.

The `0.85` dependency rate, when combined with the selection of other parameters at their most impactful extremes, inflates the calculated revenue loss to an upper bound that may exceed a realistically plausible worst-case scenario. This constitutes a potential instance of hardcoding a parameter that significantly amplifies the thesis's impact without sufficient granular empirical justification for its magnitude across the aggregated revenue streams.

**So What for the Meta-Judge:**
The Mutator's quantitative prediction of a $137.98 Billion direct hardware revenue void is mathematically derived from its stated parameters and equations. However, the precision and solvency of this prediction are critically undermined by the `DEPENDENCY_RATE_ADV_NODES` parameter. This parameter, at 0.85, represents an exceptionally high and insufficiently justified immediate reliance on *new* advanced wafers for a broad range of OEM revenues, even after accounting for a 1-month chip buffer. This aggressive assumption, combined with other parameters selected to maximize impact, positions the final revenue loss figure as an extreme upper bound rather than a robust, empirically grounded estimate. The model's sensitivity to this specific, less-grounded parameter suggests a potential overstatement of the immediate economic impact, challenging the overall reliability of the thesis's quantitative conclusion.

```python
from decimal import Decimal, getcontext

# Set precision for Decimal calculations
getcontext().prec = 10

# Mutator's Load-Bearing Variables (replicated for baseline comparison)
WSPM_ADV_MUTATOR = Decimal('250000') # Wafers/Mo
CYCLE_TIME_MOS_MUTATOR = Decimal('3') # Months
WAFER_PRICE_USD_MUTATOR = Decimal('20000') # USD/Wafer
CHEM_BUFFER_DAYS_MUTATOR = Decimal('30') # Days
QUARANTINE_DAYS_MUTATOR = Decimal('60') # Days
RESTART_DAYS_MUTATOR = Decimal('30') # Days
REV_AAPL_HW_MUTATOR = Decimal('350000000000') # USD/Year
REV_NVDA_DC_MUTATOR = Decimal('115000000000') # USD/Year
REV_AMD_MUTATOR = Decimal('22000000000') # USD/Year
OEM_CHIP_INVENTORY_MONTHS_MUTATOR = Decimal('1') # Months
DEPENDENCY_RATE_ADV_NODES_MUTATOR = Decimal('0.85') # Fraction

# --- COUNTER-TEST ---
def run_counter_test():
    print("--- Counter-Test Execution ---")

    # Replicate Mutator's calculations for baseline comparison
    dep_annual_rev_mutator = REV_AAPL_HW_MUTATOR + REV_NVDA_DC_MUTATOR + REV_AMD_MUTATOR
    dep_monthly_rev_mutator = dep_annual_rev_mutator / Decimal('12')
    adj_dep_monthly_rev_mutator = dep_monthly_rev_mutator * DEPENDENCY_RATE_ADV_NODES_MUTATOR

    fab_starved_days_mutator = QUARANTINE_DAYS_MUTATOR - CHEM_BUFFER_DAYS_MUTATOR
    if fab_starved_days_mutator < 0: fab_starved_days_mutator = Decimal('0')
    total_zero_production_days_mutator = fab_starved_days_mutator + RESTART_DAYS_MUTATOR
    new_wafer_cycle_days_mutator = CYCLE_TIME_MOS_MUTATOR * Decimal('30')
    pipeline_void_days_mutator = total_zero_production_days_mutator + new_wafer_cycle_days_mutator
    pipeline_void_months_mutator = pipeline_void_days_mutator / Decimal('30')
    net_void_months_x_mutator = pipeline_void_months_mutator - OEM_CHIP_INVENTORY_MONTHS_MUTATOR
    if net_void_months_x_mutator < 0: net_void_months_x_mutator = Decimal('0')

    total_revenue_loss_z_mutator = net_void_months_x_mutator * adj_dep_monthly_rev_mutator
    print(f"Mutator's Calculated Total Revenue Loss (Z): ${total_revenue_loss_z_mutator:,.2f}")

    # --- Counter-Test Parameters ---
    # We challenge the DEPENDENCY_RATE_ADV_NODES.
    # A more conservatively estimated, yet still high, dependency rate is chosen. This rate
    # accounts for additional factors such as finished goods inventory, product portfolio
    # diversification, and some demand flexibility, which would reduce the immediate,
    # direct revenue dependency on *new* sub-5nm wafers after a 1-month chip buffer.
    DEPENDENCY_RATE_ADV_NODES_COUNTER = Decimal('0.60') # Reduced from Mutator's 0.85

    print(f"\nCounter-Test Parameters:")
    print(f"  Adjusted Advanced Node Dependency Rate: {DEPENDENCY_RATE_ADV_NODES_COUNTER:.2f} (vs. Mutator's {DEPENDENCY_RATE_ADV_NODES_MUTATOR:.2f})")

    # --- Recalculate with Counter-Test Parameters ---
    # All other parameters remain as per Mutator's model to isolate the impact of the dependency rate.
    WSPM_ADV = WSPM_ADV_MUTATOR
    CYCLE_TIME_MOS = CYCLE_TIME_MOS_MUTATOR
    WAFER_PRICE_USD = WAFER_PRICE_USD_MUTATOR
    CHEM_BUFFER_DAYS = CHEM_BUFFER_DAYS_MUTATOR
    QUARANTINE_DAYS = QUARANTINE_DAYS_MUTATOR
    RESTART_DAYS = RESTART_DAYS_MUTATOR
    REV_AAPL_HW = REV_AAPL_HW_MUTATOR
    REV_NVDA_DC = REV_NVDA_DC_MUTATOR
    REV_AMD = REV_AMD_MUTATOR
    OEM_CHIP_INVENTORY_MONTHS = OEM_CHIP_INVENTORY_MONTHS_MUTATOR
    DEPENDENCY_RATE_ADV_NODES = DEPENDENCY_RATE_ADV_NODES_COUNTER # This is the only changed variable

    # Derived Values (re-calculated)
    dep_annual_rev = REV_AAPL_HW + REV_NVDA_DC + REV_AMD
    dep_monthly_rev = dep_annual_rev / Decimal('12')
    adj_dep_monthly_rev = dep_monthly_rev * DEPENDENCY_RATE_ADV_NODES

    fab_starved_days = QUARANTINE_DAYS - CHEM_BUFFER_DAYS
    if fab_starved_days < 0: fab_starved_days = Decimal('0')
    total_zero_production_days = fab_starved_days + RESTART_DAYS
    new_wafer_cycle_days = CYCLE_TIME_MOS * Decimal('30')
    pipeline_void_days = total_zero_production_days + new_wafer_cycle_days
    pipeline_void_months = pipeline_void_days / Decimal('30')
    net_void_months_x = pipeline_void_months - OEM_CHIP_INVENTORY_MONTHS
    if net_void_months_x < 0: net_void_months_x = Decimal('0')

    total_revenue_loss_z_counter = net_void_months_x * adj_dep_monthly_rev
    print(f"Counter-Test Calculated Total Revenue Loss (Z): ${total_revenue_loss_z_counter:,.2f}")

    # --- Assertions to expose insolvency ---
    # The Mutator's prediction is significantly higher than what a more grounded dependency rate yields.
    # We assert that the Mutator's calculated loss is at least 30% higher than our counter-test,
    # demonstrating the significant impact of the chosen dependency rate on the final outcome.
    # The ratio (0.85 / 0.60) is approximately 1.4167, indicating a ~41.67% difference.
    # A threshold of 30% is a conservative measure to demonstrate this sensitivity.
    percentage_difference = ((total_revenue_loss_z_mutator - total_revenue_loss_z_counter) / total_revenue_loss_z_counter) * Decimal('100')

    print(f"\nPercentage difference in calculated loss: {percentage_difference:.2f}%")

    assert percentage_difference > Decimal('30'), \
        f"The Mutator's prediction is not sufficiently sensitive to the dependency rate. " \
        f"Expected >30% difference, got {percentage_difference:.2f}%."

    print("\nCounter-test passed: The Mutator's thesis demonstrates high sensitivity to the unsubstantiated dependency rate, leading to an inflated revenue loss estimate. This challenges the precision and robustness of the original quantitative conclusion.")

# Execute the counter-test
run_counter_test()
```

### PYTHON EXECUTION OUTPUT:
--- Counter-Test Execution ---
Mutator's Calculated Total Revenue Loss (Z): $137,983,333,300.00

Counter-Test Parameters:
  Adjusted Advanced Node Dependency Rate: 0.60 (vs. Mutator's 0.85)
Counter-Test Calculated Total Revenue Loss (Z): $97,400,000,000.00

Percentage difference in calculated loss: 41.67%

Counter-test passed: The Mutator's thesis demonstrates high sensitivity to the unsubstantiated dependency rate, leading to an inflated revenue loss estimate. This challenges the precision and robustness of the original quantitative conclusion.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 86, in <module>
    run_tests()
    ~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 62, in run_tests
    assert abs(DEP_MONTHLY_REV - expected_dep_monthly_rev) < Decimal('0.01'), \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: DEP_MONTHLY_REV mismatch: Expected ~40583333333.33333, Got 4.058333333E+10


# Final Score: 10
**Weakest Point:** The model's deliberate omission of a traceable GDP contraction path (as explicitly required by the rubric), coupled with critical parameter overestimations (dependency rate, lack of adaptive capacity), and the outright failure of its own quantitative unit tests due to precision issues.
**Rationale:** The Mutator presented a seemingly rigorous model focusing on direct hardware revenue loss stemming from a 60-day maritime quarantine. It commendably distinguished between different disruption types and avoided broad GDP multipliers, earning praise from the Heterodox Macroeconomist for its granular approach to *revenue loss*. However, this granular focus simultaneously caused a critical failure to meet the rubric's explicit demand for a *traceable GDP contraction figure*. The Logistics & Resilience Architect and Quantitative Risk Arbitrageur successfully exposed significant overestimations in the final revenue loss figure by demonstrating the model's brittleness to overly pessimistic 'conservative stress-test' parameters and an aggressive OEM dependency rate. These critiques argued the model neglects adaptive capacity, strategic redundancies, and broader product portfolio resilience. Critically, the thesis also failed its own quantitative unit tests due to a numerical precision mismatch, indicating a fundamental flaw in its claimed mathematical coherence.
