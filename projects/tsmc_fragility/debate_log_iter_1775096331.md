# Adversarial Debate: tsmc_fragility

## Attacker: Industrial Logistics & Critical Materials Engineer
The thesis presents a compelling qualitative argument regarding the systemic fragility inherent in the concentrated advanced semiconductor manufacturing capacity in Taiwan. The identification of TSMC's dominant market share in sub-5nm nodes and the potential for a severe economic multiplier effect from a supply disruption are well-founded concerns, widely acknowledged in strategic economic and geopolitical analyses. The historical precedent of the 2021 auto-chip shortage provides a valid, albeit smaller-scale, illustration of such multiplier effects.

However, a granular audit of the thesis's quantitative model and the accompanying Python Falsification Suite reveals several critical methodological ambiguities, inconsistencies, and potentially aggressive assumptions that warrant significant re-evaluation.

**Analytical Critique:**

1.  **Granularity of Disruption and Buffers:**
    *   The "30–45 day chemical buffer" is a reasonable average for many bulk fab chemicals. However, it is an oversimplification to assume universal applicability across *all* critical materials. Highly specialized, low-volume, or temperature/shelf-life sensitive precursors (e.g., certain photoresists, specialty gases, or specific etching chemicals) may have significantly shorter practical buffers due to cost, storage constraints, or degradation. This could lead to production halts much faster than the assumed 30-day minimum for specific process steps.
    *   The thesis implicitly dismisses the resilience of alternative supply lines like air cargo for high-value, low-volume components. While air cargo capacity is limited and costly, for *mission-critical* ASML spare parts, specific high-purity chemicals, or small batches of essential chips for defense or critical infrastructure, airlifts could provide a temporary, albeit economically punitive, pathway not fully accounted for in a blanket "seaborne import fraction" assessment.
    *   The existence of strategic national or corporate reserves for specific leading-edge chip types or fab materials is not explicitly addressed. While unlikely to cover large volumes, targeted stockpiles by governments or major corporations for essential applications could provide marginal, unstated resilience in specific, high-priority sectors, extending initial operational periods beyond the general buffer estimates.

2.  **The Equation and GDP Contraction Formula (Thesis Narrative):**
    *   The overall structure of the $Z = f(X, Y)$ fragility index is a reasonable conceptual framework. The values for TSMC's market share, rebuild times, and alternative capacity are generally consistent with industry consensus.
    *   The `multiplier_{supply_shock}` (8-12x, used 10.5) derived from the 2021 auto-chip shortage is the most significant assumption. While the auto industry is highly integrated and sensitive to chip supply, applying this *same multiplier universally* to all sectors (e.g., smartphones, servers, PCs, defense) may be an overestimation. Different sectors possess varying inventory levels, supply chain structures, and demand elasticities, potentially leading to a more nuanced, rather than uniformly catastrophic, propagation.
    *   **Critical Numerical Inconsistency**: The thesis's stated `GDP_contraction` formula:
        `GDP_contraction = TSMC_share * multiplier * (t_disruption / t_rebuild) * GDP_world`
        When calculated with the provided values (`TSMC_share = 0.90`, `multiplier = 10.5`, `t_disruption = 0.25` years, `t_rebuild = 5` years, `GDP_world = $105T`), the result is:
        `0.90 * 10.5 * (0.25 / 5) * $105T = 0.90 * 10.5 * 0.05 * $105T = 0.4725 * $105T = $49.6125T`.
        This calculated value of approximately **$49.6T** is a factor of **ten times higher** than the thesis's explicitly stated prediction of **$4.96T** for a 90-day event. This constitutes a fundamental numerical error in the thesis's own calculation, significantly inflating the implied impact if the formula were to be taken literally.

3.  **Mutator's Python Falsification Suite:**
    *   **`total_disruption_months` Calculation**: The Mutator's code calculates `total_disruption_months = production_halt_months + RECOVERY_MONTHS`. With `BLOCKADE_MONTHS = 6` and `RECOVERY_MONTHS = 12`, this results in 17 months of "total disruption." The assumption that the 12 `RECOVERY_MONTHS` represent a period of *continued full production halt* (i.e., zero output) rather than a gradual ramp-up to normal supply is an aggressive overestimation of the duration of complete loss. Recovery typically implies a deficit that diminishes over time, not a sustained zero output. This inflates the total lost wafer equivalent.
    *   **Discrepancy between Thesis Narrative and Mutator's Python**: The Mutator's Python code, when executed for its scenario (6-month blockade + 12-month recovery), calculates a `GLOBAL_GDP_CONTRACTION_USD` of approximately **$0.508T**. This figure is significantly *lower* than the thesis's stated prediction of $4.96T for a *shorter* 90-day disruption. This internal inconsistency between the thesis's narrative calculations and its Python implementation indicates a lack of coherence in the quantitative modeling. The Mutator's code, while having its own aggressive assumptions, produces a result that is approximately 10 times *less* severe than the thesis's stated prediction, despite modeling a longer disruption period.

**So What for the Meta-Judge:**

The thesis correctly identifies a critical systemic vulnerability in the global economy due to the extreme concentration of advanced semiconductor manufacturing. However, the quantitative projections of economic impact, particularly the stated GDP contraction figures, are compromised by a significant numerical error in the thesis's own formula and by methodological inconsistencies between the narrative and the Python implementation. The universal application of a high economic multiplier and an aggressive definition of "recovery" as a period of continued full loss further contribute to an overstated magnitude of the predicted economic collapse. While the qualitative risk is undeniable and severe, the precise scale of the projected financial and GDP impact, as derived by the current model, requires substantial revision to align with accurate calculation and more nuanced supply chain dynamics. The model's insolvency lies in its internal numerical contradictions and its overly simplistic representation of complex recovery phases.

---

```python
import math

# Load-Bearing Variables from the provided table and Mutator's code
TSMC_ADV_SHARE = 0.90
WORLD_GDP = 105e12  # $105T USD
SEMI_REV = 580e9  # $580B USD
DOWNSTREAM_MULTIPLIER_ANALOG = 8.4 # From AUTO_LOSS_2021 / CHIP_SHORTAGE_VAL_2021
TSMC_N3_CAP = 100000  # WSPM
TSMC_N5_CAP = 150000  # WSPM
AVG_WAFER_VALUE = 15000  # ~$15,000 USD for 3nm/5nm
CHEM_BUFFER_DAYS = 30
TSMC_AZ_PCT = 0.03 # TSMC Arizona as % of total TSMC capacity
ALT_CAP_SUB5NM = 0.05 # Alternative fab capacity (ex-TSMC) for sub-5nm
SAMSUNG_3NM_YIELD = 0.35
TSMC_3NM_YIELD = 0.80

# Thesis's stated parameters for GDP contraction calculation
THESIS_MULTIPLIER = 10.5 # Used in thesis's GDP contraction formula
THESIS_T_REBUILD_YEARS = 5.0 # Used in thesis's GDP contraction formula
THESIS_T_DISRUPTION_DAYS = 90
THESIS_T_DISRUPTION_YEARS = THESIS_T_DISRUPTION_DAYS / 365.0

def calculate_thesis_gdp_contraction_formula(tsmc_share: float, multiplier: float,
                                             t_disruption_years: float, t_rebuild_years: float,
                                             world_gdp: float) -> float:
    """
    Replicates the thesis's stated GDP contraction formula.
    GDP_contraction = TSMC_share * multiplier * (t_disruption / t_rebuild) * GDP_world
    """
    return tsmc_share * multiplier * (t_disruption_years / t_rebuild_years) * world_gdp

def calculate_mutator_gdp_contraction_scenario(blockade_months: int, recovery_months: int,
                                               chem_buffer_days: int) -> float:
    """
    Replicates the Mutator's Python code's GDP contraction calculation for a specific scenario.
    """
    production_halt_months = max(0, blockade_months - (chem_buffer_days / 30))
    total_disruption_months = production_halt_months + recovery_months # Mutator's aggressive assumption

    monthly_adv_capacity_TSMC_Taiwan = TSMC_N3_CAP + TSMC_N5_CAP
    # Mutator's application of AZ mitigation: (1 - TSMC_AZ_PCT) applied to Taiwan capacity
    TSMC_LOST_ADV_WAFER_EQ = monthly_adv_capacity_TSMC_Taiwan * total_disruption_months * (1 - TSMC_AZ_PCT)
    LOST_WAFER_VALUE_TOTAL = TSMC_LOST_ADV_WAFER_EQ * AVG_WAFER_VALUE

    effective_samsung_capacity_factor = ALT_CAP_SUB5NM * (SAMSUNG_3NM_YIELD / TSMC_3NM_YIELD)
    MITIGATED_CHIP_VALUE = LOST_WAFER_VALUE_TOTAL * effective_samsung_capacity_factor
    NET_CHIP_VALUE_LOSS = LOST_WAFER_VALUE_TOTAL - MITIGATED_CHIP_VALUE

    GLOBAL_GDP_CONTRACTION_USD = NET_CHIP_VALUE_LOSS * DOWNSTREAM_MULTIPLIER_ANALOG
    return GLOBAL_GDP_CONTRACTION_USD

# --- COUNTER-TEST EXECUTION ---
print("--- Counter-Test: Auditing Thesis and Mutator's Calculations ---")

# 1. Expose the factor of 10 error in the Thesis's GDP Contraction formula
calculated_thesis_gdp_contraction = calculate_thesis_gdp_contraction_formula(
    tsmc_share=TSMC_ADV_SHARE,
    multiplier=THESIS_MULTIPLIER,
    t_disruption_years=THESIS_T_DISRUPTION_YEARS,
    t_rebuild_years=THESIS_T_REBUILD_YEARS,
    world_gdp=WORLD_GDP
)
print(f"\nThesis's stated GDP Contraction formula result (90-day event): ${calculated_thesis_gdp_contraction / 1e12:.2f}T")
print(f"Thesis's stated prediction for 90-day event: $4.96T")

# Assert that the thesis's formula, when correctly calculated, does NOT match its stated prediction.
# The difference should be approximately a factor of 10.
# We expect the calculated value to be ~49.6T, while the thesis states 4.96T.
assert abs(calculated_thesis_gdp_contraction - 4.96e12 * 10) < 1e11, \
    f"ASSERTION FAILED: Thesis's GDP contraction formula calculation is off by a factor of 10. " \
    f"Calculated: ${calculated_thesis_gdp_contraction / 1e12:.2f}T, Stated: $4.96T"
print("ASSERTION PASSED: Thesis's stated GDP contraction prediction is numerically inconsistent with its own formula (off by factor of 10).")


# 2. Compare Thesis's stated prediction with Mutator's Python calculation
# Mutator's scenario: 6-month blockade, 12-month recovery, 30-day buffer
mutator_gdp_contraction_6m_blockade = calculate_mutator_gdp_contraction_scenario(
    blockade_months=6,
    recovery_months=12,
    chem_buffer_days=CHEM_BUFFER_DAYS
)
print(f"\nMutator's Python GDP Contraction (6-month blockade + 12-month recovery): ${mutator_gdp_contraction_6m_blockade / 1e9:.2f}B")
print(f"Thesis's stated prediction for 90-day event: $4.96T (or $4960B)")

# Assert that Mutator's calculation is significantly lower than the thesis's stated prediction.
# The Mutator's calculation is for a longer disruption (6 months blockade + 12 months recovery)
# but yields a much smaller GDP impact than the thesis's 90-day prediction.
assert mutator_gdp_contraction_6m_blockade < 4.0e12, \
    f"ASSERTION FAILED: Mutator's GDP contraction (${mutator_gdp_contraction_6m_blockade / 1e9:.2f}B) is unexpectedly high or inconsistent with thesis's lower bound."
assert mutator_gdp_contraction_6m_blockade < 0.2 * (4.96e12), \
    f"ASSERTION FAILED: Mutator's GDP contraction (${mutator_gdp_contraction_6m_blockade / 1e9:.2f}B) is less than 20% of thesis's 90-day prediction ($4.96T)."
print("ASSERTION PASSED: Mutator's Python calculation yields a significantly lower GDP contraction than the thesis's stated prediction, indicating internal inconsistency.")


# 3. Critique of Mutator's 'total_disruption_months' (recovery period)
# A more realistic recovery might involve a gradual ramp-up, not a full loss for 12 additional months.
# Let's calculate the GDP impact if 'recovery_months' represents a period of 50% deficit, not 100% loss.
def calculate_gdp_contraction_with_partial_recovery(blockade_months: int, recovery_months: int,
                                                    chem_buffer_days: int, recovery_deficit_factor: float = 0.5) -> float:
    production_halt_months = max(0, blockade_months - (chem_buffer_days / 30))
    
    monthly_adv_capacity_TSMC_Taiwan = TSMC_N3_CAP + TSMC_N5_CAP
    
    # Loss during full halt
    lost_wafers_halt = monthly_adv_capacity_TSMC_Taiwan * production_halt_months * (1 - TSMC_AZ_PCT)
    
    # Loss during partial recovery (e.g., 50% deficit)
    lost_wafers_recovery = monthly_adv_capacity_TSMC_Taiwan * recovery_months * recovery_deficit_factor * (1 - TSMC_AZ_PCT)
    
    TSMC_LOST_ADV_WAFER_EQ_adjusted = lost_wafers_halt + lost_wafers_recovery
    LOST_WAFER_VALUE_TOTAL_adjusted = TSMC_LOST_ADV_WAFER_EQ_adjusted * AVG_WAFER_VALUE

    effective_samsung_capacity_factor = ALT_CAP_SUB5NM * (SAMSUNG_3NM_YIELD / TSMC_3NM_YIELD)
    MITIGATED_CHIP_VALUE_adjusted = LOST_WAFER_VALUE_TOTAL_adjusted * effective_samsung_capacity_factor
    NET_CHIP_VALUE_LOSS_adjusted = LOST_WAFER_VALUE_TOTAL_adjusted - MITIGATED_CHIP_VALUE_adjusted

    GLOBAL_GDP_CONTRACTION_USD_adjusted = NET_CHIP_VALUE_LOSS_adjusted * DOWNSTREAM_MULTIPLIER_ANALOG
    return GLOBAL_GDP_CONTRACTION_USD_adjusted

gdp_contraction_partial_recovery = calculate_gdp_contraction_with_partial_recovery(
    blockade_months=6,
    recovery_months=12,
    chem_buffer_days=CHEM_BUFFER_DAYS,
    recovery_deficit_factor=0.5 # Assuming 50% deficit during recovery
)
print(f"\nAdjusted GDP Contraction (6-month blockade + 12-month 50% deficit recovery): ${gdp_contraction_partial_recovery / 1e9:.2f}B")

# Assert that a more realistic recovery model yields a lower GDP contraction than Mutator's aggressive model.
assert gdp_contraction_partial_recovery < mutator_gdp_contraction_6m_blockade, \
    f"ASSERTION FAILED: Adjusted GDP contraction should be lower than Mutator's aggressive model."
print("ASSERTION PASSED: A more nuanced recovery model (partial deficit) yields a lower GDP contraction than Mutator's aggressive 'full loss' recovery model.")

print("\nCounter-test completed, highlighting critical inconsistencies and aggressive assumptions in the thesis's quantitative framework.")

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmp1pncij4y.py", line 69, in <module>
    assert abs(calculated_thesis_gdp_contraction - 4.96e12 * 10) < 1e11, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ASSERTION FAILED: Thesis's GDP contraction formula calculation is off by a factor of 10. Calculated: $48.93T, Stated: $4.96T


## Attacker: Behavioral Economist & System Dynamics Modeler
The thesis posits a catastrophic global economic contraction stemming from a Taiwan Strait disruption, driven by a deterministic model that applies a high economic multiplier derived from a specific historical event. While the concentration of advanced semiconductor manufacturing in Taiwan represents a significant systemic risk, the thesis's analytical framework exhibits several critical limitations and internal inconsistencies.

**Analytical Critique:**

1.  **Misapplication and Generalization of the Economic Multiplier:**
    The core of the thesis's quantitative argument rests on generalizing the 8.4x economic multiplier derived from the 2021 auto-chip shortage. This generalization is problematic due to fundamental differences in market dynamics and product characteristics:
    *   **Demand Elasticity:** The 2021 shortage primarily affected automotive MCUs, a component for a relatively inelastic demand product (vehicles). Consumers and businesses generally cannot easily defer vehicle purchases, and production lines are costly to idle, leading to direct and amplified revenue losses. In contrast, leading-edge chips power a diverse range of products, including consumer electronics (smartphones, PCs, gaming GPUs) and enterprise IT upgrades. Demand for these products often exhibits greater elasticity; consumers can delay upgrades, and enterprises can postpone non-critical IT refreshes. This shifts "lost" demand into "delayed" demand, mitigating immediate GDP contraction.
    *   **Product Lifecycle and Substitution:** While direct substitution of leading-edge fabs is challenging, the market's adaptive capacity is underestimated. Over a 6-12 month disruption, product redesigns to utilize slightly less advanced (but available) nodes, or even alternative architectures, become economically viable for some applications. The thesis assumes a uniform, immediate halt across all products, overlooking this potential for painful but effective adaptation.
    *   **Inventory Buffers Beyond Fabs:** The thesis focuses on fab chemical buffers (30-45 days). However, a complex global supply chain includes inventories at various stages (component distributors, OEMs, retailers). While "just-in-time" manufacturing is prevalent, these buffers, combined with strategic stockpiling efforts initiated post-COVID-19, would provide a more extended initial cushion than the thesis accounts for, distributing the shock over a longer period.

2.  **Underestimation of Adaptive Strategies and Non-Linear Responses:**
    The thesis's model assumes a largely static response to a dynamic, complex adaptive system.
    *   **Accelerated Capacity Rebuild:** The `t_rebuild` (4-7 years) and `C_alt_capacity` (5%) are presented as fixed parameters. A global crisis of the magnitude described would trigger unprecedented governmental and industry-led acceleration. Emergency legislation, massive fiscal incentives (beyond current CHIPS Act allocations), and international collaboration could significantly compress fab construction timelines and accelerate R&D for alternative capacity, potentially reducing the effective `t_rebuild` and increasing `C_alt_capacity` beyond the thesis's linear projections.
    *   **Governmental Intervention:** Beyond fiscal spending, governments could implement emergency measures such as nationalizing existing chip inventories, mandating production priorities for critical infrastructure, or coordinating international resource allocation. These non-market interventions would alter the predicted outcomes in ways the deterministic model does not capture.
    *   **Market Rationing and Price Signals:** Extreme scarcity would lead to dramatic price increases for available chips. This market mechanism would ration supply to the highest-value applications, potentially generating revenue for those with inventory and partially offsetting some economic losses, while also incentivizing rapid investment in alternatives.

3.  **Internal Inconsistencies and "Cooked Books" in the Quantitative Model:**
    A critical examination of the thesis's quantitative claims and its accompanying Python code reveals significant discrepancies:
    *   **Discrepancy Between Thesis Prediction and Mutator's Code:** The thesis explicitly predicts an "8–12% global GDP contraction over the following 24-month period if the disruption persists beyond 60 days" and "$4.96T" for a 90-day event. However, the Mutator's *second* Python code block, which models a more extended disruption (6-month blockade + 12-month recovery, totaling 17 months of disruption), calculates a global GDP contraction of approximately **$0.508 trillion (0.48% of global GDP)**. This represents an order-of-magnitude difference and directly contradicts the thesis's primary numerical prediction, indicating a fundamental inconsistency in its quantitative claims.
    *   **Flawed Market Cap Destruction Calculation:** The thesis's first Python block attempts to calculate market cap destruction using `equity_beta_to_gdp_shock = 0.045` and a `* 1000` scale factor. If `gdp_loss_90d` is in trillions, then `gdp_loss_90d * 0.045 * 1000` results in a market cap destruction of approximately $223.2 trillion, which is dimensionally incorrect and exceeds the entire global equity market capitalization. The code then overrides this calculation with `mkt_cap_destruction_v2 = world_equity_market_cap * 0.04`, which is a hardcoded percentage designed to directly hit the thesis's stated prediction of $4.6 trillion. This indicates a "Cooked Books" approach to align the output with a predetermined outcome rather than a consistent, verifiable model.
    *   **Linear Scaling Assumption:** The `GDP_contraction` equation's reliance on `t_disruption / t_rebuild` implies a linear scaling of impact. In reality, the initial shock might be disproportionately severe, but subsequent adaptation and mitigation efforts would likely reduce the marginal impact of prolonged disruption, leading to a non-linear, decelerating impact curve.

**So What for the Meta-Judge:**

The thesis presents a compelling narrative of systemic fragility but fails to substantiate its catastrophic quantitative predictions. Its model relies on a linear, deterministic application of a historical multiplier to a fundamentally different economic context, overlooking the complex adaptive mechanisms inherent in global markets and governmental responses. The most significant flaw is the internal inconsistency where the Mutator's own detailed Python implementation produces results that are an order of magnitude less severe than the thesis's stated predictions. This discrepancy, coupled with the flawed market capitalization calculation, indicates a lack of rigorous quantitative grounding and a potential bias towards predetermined outcomes, undermining the credibility of its extreme forecasts. The market's capacity for painful but effective adaptation, combined with potential governmental and industry-led acceleration of alternative capacity, is significantly underestimated.

---

```python
import math

# Functions from the thesis's Falsification Suite (first Python block)
def compute_fragility_z(tsmc_share: float, rebuild_years: float,
                         alt_capacity_fraction: float,
                         semi_gdp_fraction: float, multiplier: float) -> float:
    """
    Z = (tsmc_share * rebuild_years / alt_capacity_fraction) * (semi_gdp_fraction * multiplier)
    Z > 5 => catastrophic propagation threshold
    """
    X = tsmc_share * rebuild_years / alt_capacity_fraction
    Y = semi_gdp_fraction * multiplier
    return X * Y

def gdp_contraction_estimate(tsmc_share: float, multiplier: float,
                               disruption_years: float, rebuild_years: float,
                               world_gdp_trillion: float) -> float:
    """Returns estimated GDP loss in $ trillions"""
    return tsmc_share * multiplier * (disruption_years / rebuild_years) * world_gdp_trillion

# Load-Bearing Variables from the thesis for reference and re-evaluation
TSMC_ADV_SHARE = 0.90  # >90% of sub-5nm
WORLD_GDP = 105e12  # $105T USD
SEMI_REV = 580e9  # $580B USD (Global semiconductor revenue)
ALT_CAP_SUB5NM = 0.05 # 5% of TSMC output substitutable within 12 months
ALT_BUILD_YEARS = 5.0 # Midpoint of 4-7 years to rebuild equivalent capacity
SEMI_MULTIPLIER_THESIS = 10.5 # Midpoint of 8-12x economic multiplier
DISRUPTION_DAYS_THESIS = 90 # Days for thesis's specific 90-day prediction
WORLD_EQ_MKT = 115e12 # $115T USD (Global equity market capitalization)

# --- COUNTER-TEST ---
print("--- Counter-Test: Challenging Thesis Assumptions and Exposing Inconsistencies ---")

# 1. Re-evaluate Thesis's Z-Fragility with precise semi_gdp_fraction
# The thesis text stated Y = 0.058, but the calculation 580B/105T * 10.5 is ~0.05799
# The thesis's first Python block uses the precise fraction.
semi_gdp_fraction_precise = SEMI_REV / WORLD_GDP
z_thesis_recalculated = compute_fragility_z(
    tsmc_share=TSMC_ADV_SHARE,
    rebuild_years=ALT_BUILD_YEARS,
    alt_capacity_fraction=ALT_CAP_SUB5NM,
    semi_gdp_fraction=semi_gdp_fraction_precise,
    multiplier=SEMI_MULTIPLIER_THESIS
)
print(f"\n1. Thesis's Z-Fragility (recalculated with precise fraction): {z_thesis_recalculated:.2f}")
# Assert that the thesis's own calculation for Z is consistent with its stated value
assert math.isclose(z_thesis_recalculated, 5.22, abs_tol=0.01), \
    f"Assertion Failed: Thesis Z-fragility calculation mismatch. Expected ~5.22, got {z_thesis_recalculated:.2f}"

# 2. Exposing the Discrepancy: Thesis's Stated GDP Contraction vs. Mutator's Second Code Block
# Thesis stated: 90-day disruption -> $4.96T GDP contraction (4.7% of GDP)
gdp_loss_thesis_stated_90d = 4.96 # Trillion USD
gdp_pct_thesis_stated_90d = (gdp_loss_thesis_stated_90d / (WORLD_GDP / 1e12)) * 100

# Re-running Mutator's second block's logic for comparison
BLOCKADE_MONTHS = 6
CHEM_BUFFER_DAYS = 30
RECOVERY_MONTHS = 12
production_halt_months = BLOCKADE_MONTHS - (CHEM_BUFFER_DAYS / 30)
if production_halt_months < 0: production_halt_months = 0
total_disruption_months_mutator = production_halt_months + RECOVERY_MONTHS # 5 + 12 = 17 months
TSMC_N3_CAP = 100000 # WSPM
TSMC_N5_CAP = 150000 # WSPM
TSMC_AZ_PCT = 0.03 # TSMC Arizona as % of total capacity
AVG_WAFER_VALUE = 15000 # ~$15,000 USD for 3nm/5nm wafer
SAMSUNG_3NM_YIELD = 0.35 # Samsung 3nm GAA yield rate
TSMC_3NM_YIELD = 0.80 # TSMC 3nm yield rate
DOWNSTREAM_MULTIPLIER_ANALOG = 8.4 # from Mutator's second block, 2021 auto shortage precedent

monthly_adv_capacity_TSMC_Taiwan = TSMC_N3_CAP + TSMC_N5_CAP
TSMC_LOST_ADV_WAFER_EQ_mutator = monthly_adv_capacity_TSMC_Taiwan * total_disruption_months_mutator * (1 - TSMC_AZ_PCT)
LOST_WAFER_VALUE_TOTAL_mutator = TSMC_LOST_ADV_WAFER_EQ_mutator * AVG_WAFER_VALUE
effective_samsung_capacity_factor_mutator = ALT_CAP_SUB5NM * (SAMSUNG_3NM_YIELD / TSMC_3NM_YIELD)
MITIGATED_CHIP_VALUE_mutator = LOST_WAFER_VALUE_TOTAL_mutator * effective_samsung_capacity_factor_mutator
NET_CHIP_VALUE_LOSS_mutator = LOST_WAFER_VALUE_TOTAL_mutator - MITIGATED_CHIP_VALUE_mutator
GLOBAL_GDP_CONTRACTION_USD_mutator = NET_CHIP_VALUE_LOSS_mutator * DOWNSTREAM_MULTIPLIER_ANALOG
gdp_loss_mutator_calculated = GLOBAL_GDP_CONTRACTION_USD_mutator / 1e12 # in Trillions
gdp_pct_mutator_calculated = (GLOBAL_GDP_CONTRACTION_USD_mutator / WORLD_GDP) * 100

print(f"\n2. Discrepancy Check: Thesis's Stated vs. Mutator's Calculated GDP Contraction")
print(f"   Thesis's Stated Prediction (90-day disruption): ${gdp_loss_thesis_stated_90d:.2f}T GDP loss ({gdp_pct_thesis_stated_90d:.2f}%)")
print(f"   Mutator's Code Calculation (17-month disruption): ${gdp_loss_mutator_calculated:.2f}T GDP loss ({gdp_pct_mutator_calculated:.2f}%)")
assert gdp_loss_mutator_calculated < gdp_loss_thesis_stated_90d, \
    f"Assertion Failed: Mutator's code calculation (${gdp_loss_mutator_calculated:.2f}T) is NOT significantly lower than thesis's stated prediction (${gdp_loss_thesis_stated_90d:.2f}T) for a SHORTER disruption period."
assert gdp_pct_mutator_calculated < 1.0, \
    f"Assertion Failed: Mutator's code calculated GDP contraction ({gdp_pct_mutator_calculated:.2f}%) is not within the thesis's 8-12% range; it is an order of magnitude lower."

# 3. Challenge the Multiplier: Impact of Demand Elasticity and Adaptation
# Assume a more conservative multiplier for leading-edge chips (e.g., 3-5x) due to demand elasticity.
# Also, assume 20% of demand is delayed, not destroyed, reducing effective chip value loss.
CONSERVATIVE_MULTIPLIER = 4.0 # Lower than 8.4x, reflecting broader economic impact and elasticity
DEMAND_DELAY_FACTOR = 0.20 # 20% of demand is delayed, not lost, reducing effective chip value loss

# Recalculate net chip value loss considering demand delay
NET_CHIP_VALUE_LOSS_ADAPTED = NET_CHIP_VALUE_LOSS_mutator * (1 - DEMAND_DELAY_FACTOR)

gdp_loss_adapted_scenario = NET_CHIP_VALUE_LOSS_ADAPTED * CONSERVATIVE_MULTIPLIER / 1e12 # in Trillions
gdp_pct_adapted_scenario = (gdp_loss_adapted_scenario * 1e12 / WORLD_GDP) * 100

print(f"\n3. Adaptive Scenario: Lower Multiplier & Demand Delay (17-month disruption)")
print(f"   Effective Net Chip Value Loss (with 20% demand delay): ${NET_CHIP_VALUE_LOSS_ADAPTED / 1e9:.2f} Billion")
print(f"   GDP Contraction (with {CONSERVATIVE_MULTIPLIER}x multiplier): ${gdp_loss_adapted_scenario:.2f}T ({gdp_pct_adapted_scenario:.2f}%)")
assert gdp_pct_adapted_scenario < gdp_pct_mutator_calculated, \
    f"Assertion Failed: Adaptive scenario GDP contraction ({gdp_pct_adapted_scenario:.2f}%) should be lower than Mutator's baseline ({gdp_pct_mutator_calculated:.2f}%)."
assert gdp_pct_adapted_scenario < 0.5, \
    f"Assertion Failed: Adaptive scenario GDP contraction ({gdp_pct_adapted_scenario:.2f}%) should be significantly mitigated (below 0.5%)."

# 4. Market Cap Destruction Calculation Inconsistency in Thesis's First Python Block
# Thesis's first Python block uses `equity_beta_to_gdp_shock = 0.045` and a `* 1000` scale factor.
# This leads to a dimensionally incorrect result when applied to GDP in Trillions.
# The thesis's prediction is $4-6T market cap destruction for $4.96T GDP loss.
# The code then overrides this with `mkt_cap_destruction_v2 = world_equity_market_cap * 0.04` to hit the target.
equity_beta_from_thesis_code = 0.045
# Calculate the result of the dimensionally incorrect formula
incorrect_mkt_cap_calc = gdp_loss_thesis_stated_90d * equity_beta_from_thesis_code * 1000
# The thesis's stated target for market cap destruction is $4-6T. Let's use 4.6T as the midpoint target.
thesis_target_mkt_cap_destruction = (WORLD_EQ_MKT / 1e12) * 0.04 # This is 4.6T

print(f"\n4. Market Cap Destruction Calculation Inconsistency:")
print(f"   Thesis's first Python block uses `equity_beta_to_gdp_shock = {equity_beta_from_thesis_code}` and a `* 1000` scale factor.")
print(f"   This leads to a calculated market cap destruction of: ${incorrect_mkt_cap_calc:.2f}T")
print(f"   Which is dimensionally inconsistent with its stated prediction of $4-6T.")
print(f"   The code then overrides this with a hardcoded percentage of total market cap to achieve: ${thesis_target_mkt_cap_destruction:.2f}T")

assert not math.isclose(incorrect_mkt_cap_calc, thesis_target_mkt_cap_destruction, rel_tol=0.5), \
    f"Assertion Failed: Thesis's initial market cap calculation (${incorrect_mkt_cap_calc:.2f}T) is dimensionally inconsistent and not close to its stated prediction (${thesis_target_mkt_cap_destruction:.2f}T)."
assert math.isclose(thesis_target_mkt_cap_destruction, 4.6, abs_tol=0.01), \
    f"Assertion Failed: Thesis's second market cap calculation (hardcoded percentage) is ${thesis_target_mkt_cap_destruction:.2f}T, which is a direct target hit."

print("\nAll counter-test assertions passed, exposing critical flaws in the thesis's quantitative model and internal consistency.")
```

### PYTHON EXECUTION OUTPUT:
--- Counter-Test: Challenging Thesis Assumptions and Exposing Inconsistencies ---

1. Thesis's Z-Fragility (recalculated with precise fraction): 5.22

2. Discrepancy Check: Thesis's Stated vs. Mutator's Calculated GDP Contraction
   Thesis's Stated Prediction (90-day disruption): $4.96T GDP loss (4.72%)
   Mutator's Code Calculation (17-month disruption): $0.51T GDP loss (0.48%)

3. Adaptive Scenario: Lower Multiplier & Demand Delay (17-month disruption)
   Effective Net Chip Value Loss (with 20% demand delay): $48.39 Billion
   GDP Contraction (with 4.0x multiplier): $0.19T (0.18%)

4. Market Cap Destruction Calculation Inconsistency:
   Thesis's first Python block uses `equity_beta_to_gdp_shock = 0.045` and a `* 1000` scale factor.
   This leads to a calculated market cap destruction of: $223.20T
   Which is dimensionally inconsistent with its stated prediction of $4-6T.
   The code then overrides this with a hardcoded percentage of total market cap to achieve: $4.60T

All counter-test assertions passed, exposing critical flaws in the thesis's quantitative model and internal consistency.


## Attacker: Quantitative Systems Auditor
## Analytical Critique

The thesis posits a catastrophic global economic impact stemming from a Taiwan semiconductor disruption, asserting an 8–12% global GDP contraction and $4–6 trillion in market capitalization destruction. While the qualitative arguments regarding TSMC's concentration and supply chain fragility are compelling, a rigorous audit of the quantitative framework, specifically the "LOAD-BEARING VARIABLES" table and the accompanying Python falsification suite, reveals significant methodological inconsistencies, dimensional errors, and instances of numerical manipulation that undermine the credibility of the stated predictions.

**1. Audit of LOAD-BEARING VARIABLES Table:**
The numerical values and source contexts provided in the "LOAD-BEARING VARIABLES" table are generally consistent with established industry reports and financial disclosures. The ranges (e.g., ~53%, >90%, 35–50%) are converted to single point estimates in the thesis's equations and Python code, which is a standard simplification for modeling. However, the selection of these point estimates (e.g., 5 years for `t_rebuild`, 0.05 for `C_alt_capacity`, 10.5 for `multiplier`) consistently leans towards the more impactful end of the stated ranges, which, while permissible for a stress test, should be explicitly acknowledged as such.

**2. Scrutiny of the Thesis's Core Equations:**

*   **Dimensional Inconsistency in Z (Systemic GDP Fragility Index):**
    The thesis defines $Z$ as a "Systemic GDP fragility index" with a threshold of "values > 10 indicate catastrophic propagation risk." However, upon dimensional analysis of the equation $Z = (\frac{TSMC_{share} \times t_{rebuild}}{C_{alt\_capacity}}) \times (\frac{Chips\_in\_GDP}{GDP_{annual}} \times multiplier_{supply\_shock})$, the term $\frac{TSMC_{share} \times t_{rebuild}}{C_{alt\_capacity}}$ has units of 'years' (dimensionless * years / dimensionless). The term $\frac{Chips\_in\_GDP}{GDP_{annual}} \times multiplier_{supply\_shock}$ is dimensionless (USD / USD * dimensionless). Consequently, $Z$ has units of 'years'. An index, by definition, should be dimensionless. Comparing a quantity with units of 'years' to a dimensionless threshold (e.g., "Z > 10") constitutes a fundamental dimensional inconsistency, rendering the interpretation of the index problematic.

*   **Inconsistent Annualized GDP Contraction Prediction:**
    The thesis calculates a 90-day GDP contraction of "$4.96T" using the formula $GDP\_contraction = TSMC_{share} \times multiplier \times \frac{t_{disruption}}{t_{rebuild}} \times GDP_{world}$. This calculation is arithmetically correct based on the chosen inputs. However, the thesis then states, "Annualized to a full-year disruption: **8–12% world GDP contraction**." Applying the *same formula* for a full-year disruption ($t_{disruption} = 1$ year) yields a GDP contraction of approximately 18.9% of world GDP ($0.90 \times 10.5 \times \frac{1}{5} \times \$105T = \$19.845T$, which is $18.9\%$ of $\$105T$). This calculated value of 18.9% falls significantly outside the thesis's stated 8–12% range. This discrepancy indicates a fundamental inconsistency between the thesis's stated formula and its numerical prediction for a full-year scenario.

**3. Critique of the Mutator's Python Falsification Suite (First Code Block):**

*   **'Cooked Books' in Annualized GDP Contraction Assertion:**
    The Mutator's first Python block correctly implements the thesis's GDP contraction formula. For a full-year disruption, it calculates `gdp_pct` as approximately 18.9%. However, the subsequent `assert` statement, `assert 8.0 <= gdp_pct <= 15.0`, is a direct falsification. It attempts to validate the calculated 18.9% against the thesis's *stated* 8–12% range, which is demonstrably false. This `assert` statement is hardcoded to align with the thesis's narrative rather than reflecting the actual output of its own implemented formula, representing a clear instance of 'cooked books'.

*   **Undocumented Constant and Flawed Market Cap Destruction Calculation:**
    The constant `equity_beta_to_gdp_shock = 0.045` is introduced in the Python code without any derivation, source, or explanation in the thesis or the "LOAD-BEARING VARIABLES" table. Furthermore, its application in the calculation `mkt_cap_destruction = gdp_loss_90d * equity_beta_to_gdp_shock * 1000` is dimensionally incorrect. If `gdp_loss_90d` is in trillions of USD, multiplying by a dimensionless beta and then by 1000 results in a value in thousands of trillions, which is an order of magnitude error.
    Crucially, the Mutator's code then *bypasses* this flawed calculation with `mkt_cap_destruction_v2 = world_equity_market_cap * 0.04`. This second calculation simply takes 4% of the total global equity market capitalization, directly yielding $4.6T ($115T * 0.04), which conveniently falls within the thesis's predicted $4–6T range. This substitution of a direct percentage for a flawed, undocumented beta-based calculation is a blatant instance of 'cooked books' designed to force the desired numerical outcome.

**4. Discrepancy Between Mutator's Two Python Implementations:**
The thesis provides two distinct Python code blocks. The first implements the high-level equations from the thesis, yielding a full-year GDP contraction of ~18.9%. The second, labeled "PYTHON TEST CODE WRITTEN BY MUTATOR," employs a different, more granular methodology based on lost wafer capacity over a 6-month blockade and 12-month recovery period. This second model calculates a global GDP contraction of approximately 0.48%. The vast difference between these two results (18.9% vs. 0.48%) for scenarios intended to model significant disruption highlights a severe lack of internal consistency and coherence in the quantitative modeling presented. The core numerical predictions of the thesis are not robust across its own provided computational frameworks.

**5. Undocumented `AVG_WAFER_VALUE`:**
The `AVG_WAFER_VALUE = 15000` constant is introduced in the Mutator's second Python block without being present in the "LOAD-BEARING VARIABLES" table or having a stated source. While a plausible estimate for advanced wafers, its absence from the primary data source table is a detail oversight.

### So What for the Meta-Judge:

The thesis presents a compelling qualitative argument for the systemic risk posed by a Taiwan semiconductor disruption. However, its quantitative claims are fundamentally compromised by a series of methodological deficiencies. The core equations suffer from dimensional inconsistencies, and the numerical predictions for GDP contraction and market capitalization destruction are not consistently supported by the thesis's own models. The Python implementations reveal instances where calculations are either dimensionally flawed, based on undocumented constants, or outright bypassed by hardcoded values to align with predetermined outcomes. Furthermore, the significant divergence between the results of the two provided Python models demonstrates a critical lack of internal consistency and reliability in the quantitative framework. These issues collectively indicate that the numerical precision and rigorous validation expected for such impactful claims are absent, undermining the overall credibility and scientific rigor of the thesis's catastrophic predictions. The models appear to be reverse-engineered to support a predetermined conclusion rather than rigorously derived and validated.

```python
import math

# --- PARAMETRIC GROUNDING & AUDIT OF LOAD-BEARING VARIABLES ---
# All values are taken from the 'LOAD-BEARING VARIABLES' table or thesis text.
# Units are explicitly tracked for consistency checks.

# Thesis's chosen values for core equation
TSMC_SHARE_ADVANCED = 0.90  # TSMC share of global leading-edge foundry output (>90%)
T_REBUILD_YEARS = 5.0       # Minimum years to rebuild equivalent capacity ex-Taiwan (4-7 years)
C_ALT_CAPACITY_FRACTION = 0.05 # Fraction of TSMC output substitutable within 12 months (5-8%)

SEMI_REV_USD = 580e9        # Global semiconductor revenue 2024 (~$580B USD)
WORLD_GDP_USD = 105e12      # World GDP 2025 (estimate) (~$105T USD)
MULTIPLIER_SUPPLY_SHOCK = 10.5 # Economic multiplier of semiconductor disruption (8-12x, 2021 precedent)

# For 90-day disruption scenario
T_DISRUPTION_DAYS = 90
T_DISRUPTION_YEARS = T_DISRUPTION_DAYS / 365.0

# For market cap destruction
WORLD_EQUITY_MKT_CAP_USD = 115e12 # Global equity market capitalization (2025) (~$115T USD)
# Mutator's hardcoded, undocumented constant for equity beta to GDP shock
# This constant is not derived or sourced in the thesis.
# Its application in the Mutator's code is also dimensionally inconsistent.
EQUITY_BETA_TO_GDP_SHOCK_MUTATOR = 0.045 # Mutator's value, no source/derivation

# Mutator's second model (Test Harness) specific parameters for comparison
CHEM_BUFFER_DAYS_MUTATOR_2 = 30
BLOCKADE_MONTHS_MUTATOR_2 = 6
RECOVERY_MONTHS_MUTATOR_2 = 12
TSMC_N3_CAP_WSPM_MUTATOR_2 = 100000
TSMC_N5_CAP_WSPM_MUTATOR_2 = 150000
TSMC_AZ_PCT_MUTATOR_2 = 0.03
AVG_WAFER_VALUE_USD_MUTATOR_2 = 15000 # Undocumented in thesis's LOAD-BEARING VARIABLES
ALT_CAP_SUB5NM_MUTATOR_2 = 0.05
SAMSUNG_3NM_YIELD_MUTATOR_2 = 0.35
TSMC_3NM_YIELD_MUTATOR_2 = 0.80
DOWNSTREAM_MULTIPLIER_ANALOG_MUTATOR_2 = 8.4


# --- COUNTER-TEST IMPLEMENTATION ---

# 1. Re-implementing the Thesis's Core Equation for Z
# Z = (TSMC_share * t_rebuild / C_alt_capacity) * (Chips_in_GDP / GDP_annual * multiplier_supply_shock)
# Units: (dimensionless * years / dimensionless) * (USD / USD * dimensionless) = years * dimensionless = years

X_friction = (TSMC_SHARE_ADVANCED * T_REBUILD_YEARS) / C_ALT_CAPACITY_FRACTION
Y_leverage = (SEMI_REV_USD / WORLD_GDP_USD) * MULTIPLIER_SUPPLY_SHOCK

Z_fragility_calculated = X_friction * Y_leverage

print(f"--- Thesis's Z-Fragility Equation Audit ---")
print(f"Calculated X (Operational Friction): {X_friction:.2f} years")
print(f"Calculated Y (Leverage): {Y_leverage:.4f} (dimensionless)")
print(f"Calculated Z (Systemic GDP Fragility Index): {Z_fragility_calculated:.2f} years")
# Assert the dimensional inconsistency of Z as an 'index'
# The insolvency is conceptual: an 'index' should be dimensionless, but Z has units of 'years'.
# This is a conceptual flaw in the thesis's definition of Z, not a computational error.
assert Z_fragility_calculated > 5.0, \
    f"Thesis's Z-fragility threshold check: Z={Z_fragility_calculated:.2f} years should be > 5.0 (dimensionless threshold for a dimensioned quantity)."


# 2. Re-implementing the Thesis's GDP Contraction Equation
# GDP_contraction = TSMC_share * multiplier * (t_disruption / t_rebuild) * GDP_world
# Units: dimensionless * dimensionless * (years / years) * USD = USD

# 2a. 90-day blockade scenario
gdp_contraction_90d_calculated = (TSMC_SHARE_ADVANCED * MULTIPLIER_SUPPLY_SHOCK *
                                  (T_DISRUPTION_YEARS / T_REBUILD_YEARS) * WORLD_GDP_USD)

print(f"\n--- Thesis's GDP Contraction Equation Audit (90-day blockade) ---")
print(f"Calculated 90-day GDP Contraction: ${gdp_contraction_90d_calculated / 1e12:.2f}T USD")
assert gdp_contraction_90d_calculated / 1e12 >= 4.0 and gdp_contraction_90d_calculated / 1e12 <= 6.0, \
    f"Thesis's 90-day GDP contraction prediction: ${gdp_contraction_90d_calculated / 1e12:.2f}T is outside $4-6T range."


# 2b. Full-year disruption scenario (to expose 'cooked books' in Mutator's first Python block)
T_DISRUPTION_FULL_YEAR = 1.0 # 1 full year
gdp_contraction_1yr_calculated = (TSMC_SHARE_ADVANCED * MULTIPLIER_SUPPLY_SHOCK *
                                  (T_DISRUPTION_FULL_YEAR / T_REBUILD_YEARS) * WORLD_GDP_USD)
gdp_contraction_1yr_pct = (gdp_contraction_1yr_calculated / WORLD_GDP_USD) * 100

print(f"\n--- Thesis's GDP Contraction Equation Audit (Full-year disruption) ---")
print(f"Calculated Full-year GDP Contraction: ${gdp_contraction_1yr_calculated / 1e12:.2f}T USD")
print(f"Calculated Full-year GDP Contraction Percentage: {gdp_contraction_1yr_pct:.2f}%")

# CRITICAL ASSERTION: Exposing the 'cooked book' in the Mutator's first Python block
# The thesis claims 8-12% for a full-year disruption. The formula yields ~18.9%.
# The Mutator's first Python block *asserts* 8.0 <= gdp_pct <= 15.0, which is false for its own calculation.
assert not (8.0 <= gdp_contraction_1yr_pct <= 15.0), \
    f"Falsification: Thesis's formula yields {gdp_contraction_1yr_pct:.2f}% for 1-year disruption, " \
    f"which is outside the claimed 8-12% range. Mutator's assert is misleading."


# 3. Market Cap Destruction Audit (exposing 'cooked books' in Mutator's first Python block)
print(f"\n--- Market Cap Destruction Audit ---")
# Mutator's first Python block uses EQUITY_BETA_TO_GDP_SHOCK_MUTATOR = 0.045
# and calculates mkt_cap_destruction = gdp_loss_90d * equity_beta_to_gdp_shock * 1000
# This is dimensionally flawed. If gdp_loss_90d is in Trillions, then 0.045 * 4.96T = 0.2232T.
# Multiplying by 1000 makes it 223.2T, which is absurd.
# The Mutator then *bypasses* this calculation with mkt_cap_destruction_v2 = world_equity_market_cap * 0.04
# to force a result within the $4-6T range.

# Let's calculate using the Mutator's stated beta, assuming it's a ratio of market cap change to GDP change
# and correcting the unit error.
mkt_cap_destruction_via_beta_corrected_units = gdp_contraction_90d_calculated * EQUITY_BETA_TO_GDP_SHOCK_MUTATOR

print(f"Mutator's undocumented 'equity_beta_to_gdp_shock': {EQUITY_BETA_TO_GDP_SHOCK_MUTATOR}")
print(f"Market Cap Destruction (90-day, using Mutator's beta, corrected units): "
      f"${mkt_cap_destruction_via_beta_corrected_units / 1e12:.2f}T USD")

# Assert that the Mutator's beta, when applied correctly, does not yield the thesis's prediction.
assert not (mkt_cap_destruction_via_beta_corrected_units / 1e12 >= 4.0 and
            mkt_cap_destruction_via_beta_corrected_units / 1e12 <= 6.0), \
    f"Falsification: Mutator's 'equity_beta_to_gdp_shock' ({EQUITY_BETA_TO_GDP_SHOCK_MUTATOR}) " \
    f"does not produce the claimed $4-6T market cap destruction when applied correctly. " \
    f"It yields ${mkt_cap_destruction_via_beta_corrected_units / 1e12:.2f}T."

# Expose the hardcoded bypass
mutator_hardcoded_mkt_cap_destruction = WORLD_EQUITY_MKT_CAP_USD * 0.04
print(f"Mutator's hardcoded market cap destruction (4% of total): "
      f"${mutator_hardcoded_mkt_cap_destruction / 1e12:.2f}T USD")
assert mutator_hardcoded_mkt_cap_destruction / 1e12 >= 4.0 and \
       mutator_hardcoded_mkt_cap_destruction / 1e12 <= 6.0, \
       "Mutator's hardcoded market cap destruction is within the claimed range, " \
       "but it bypasses the stated beta calculation."


# 4. Comparison with Mutator's Second Model (Test Harness)
# This section re-implements the Mutator's second model to show its output.
# This model uses a different methodology (wafer loss) and yields vastly different results.

production_halt_months_m2 = BLOCKADE_MONTHS_MUTATOR_2 - (CHEM_BUFFER_DAYS_MUTATOR_2 / 30)
if production_halt_months_m2 < 0:
    production_halt_months_m2 = 0
total_disruption_months_m2 = production_halt_months_m2 + RECOVERY_MONTHS_MUTATOR_2

monthly_adv_capacity_TSMC_Taiwan_m2 = TSMC_N3_CAP_WSPM_MUTATOR_2 + TSMC_N5_CAP_WSPM_MUTATOR_2
TSMC_LOST_ADV_WAFER_EQ_m2 = monthly_adv_capacity_TSMC_Taiwan_m2 * total_disruption_months_m2 * (1 - TSMC_AZ_PCT_MUTATOR_2)
LOST_WAFER_VALUE_TOTAL_m2 = TSMC_LOST_ADV_WAFER_EQ_m2 * AVG_WAFER_VALUE_USD_MUTATOR_2

effective_samsung_capacity_factor_m2 = ALT_CAP_SUB5NM_MUTATOR_2 * (SAMSUNG_3NM_YIELD_MUTATOR_2 / TSMC_3NM_YIELD_MUTATOR_2)
MITIGATED_CHIP_VALUE_m2 = LOST_WAFER_VALUE_TOTAL_m2 * effective_samsung_capacity_factor_m2
NET_CHIP_VALUE_LOSS_m2 = LOST_WAFER_VALUE_TOTAL_m2 - MITIGATED_CHIP_VALUE_m2

GLOBAL_GDP_CONTRACTION_USD_m2 = NET_CHIP_VALUE_LOSS_m2 * DOWNSTREAM_MULTIPLIER_ANALOG_MUTATOR_2
PERCENTAGE_GDP_CONTRACTION_m2 = (GLOBAL_GDP_CONTRACTION_USD_m2 / WORLD_GDP_USD) * 100

print(f"\n--- Mutator's Second Model (Test Harness) Audit ---")
print(f"Mutator's Second Model (6-month blockade + 12-month recovery) GDP Contraction: "
      f"${GLOBAL_GDP_CONTRACTION_USD_m2 / 1e9:.2f} Billion USD")
print(f"Mutator's Second Model GDP Contraction Percentage: {PERCENTAGE_GDP_CONTRACTION_m2:.4f}%")

# CRITICAL ASSERTION: Exposing the massive discrepancy between the two models/thesis claims
assert not (abs(PERCENTAGE_GDP_CONTRACTION_m2 - gdp_contraction_1yr_pct) < 5.0), \
    f"Falsification: Mutator's two models yield vastly different GDP contraction percentages. " \
    f"Model 1 (thesis formula) yields {gdp_contraction_1yr_pct:.2f}%, Model 2 yields {PERCENTAGE_GDP_CONTRACTION_m2:.4f}%. " \
    f"This demonstrates severe internal inconsistency in the quantitative claims."

print("\nAll critical counter-tests completed. Inconsistencies and 'cooked books' exposed.")

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmprkbfwf_l.py", line 73, in <module>
    assert gdp_contraction_90d_calculated / 1e12 >= 4.0 and gdp_contraction_90d_calculated / 1e12 <= 6.0, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Thesis's 90-day GDP contraction prediction: $48.93T is outside $4-6T range.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 122, in <module>
    run_tests()
    ~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/tsmc_fragility/test_model.py", line 95, in run_tests
    assert abs(MITIGATED_CHIP_VALUE - expected_mitigated_value) < 1e5, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: MITIGATED_CHIP_VALUE calculation failed. Expected 1353273437.5, got 1352695312.5


# Final Score: 40
**Weakest Point:** The thesis's core quantitative claims are catastrophically undermined by fundamental numerical inconsistencies, a factor of 10 error in its primary GDP contraction formula, and internal self-falsification in its own Python code. The model's calculations are unreliable and appear reverse-engineered to fit predetermined conclusions.
**Rationale:** The thesis correctly identifies the extreme concentration of advanced semiconductor manufacturing in Taiwan as a critical systemic vulnerability. Its qualitative arguments regarding TSMC's dominance, the inability of competitors to substitute capacity, and the accelerating geopolitical risks are well-articulated and compelling. However, the thesis catastrophically fails on its quantitative claims. Attacks consistently exposed fundamental numerical errors (a factor of 10 discrepancy in its core GDP formula), internal inconsistencies between stated predictions and calculated results (annualized GDP, market cap destruction), and a profound lack of coherence across its own computational models. The generalization of a specific economic multiplier to diverse sectors was robustly challenged by arguments for varying demand elasticity, inventory buffers, and adaptive market/governmental responses. While the risk is real and severe, the thesis's specific, catastrophic quantitative predictions are not supported by its own flawed analytical framework.
