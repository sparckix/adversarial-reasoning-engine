# Adversarial Debate: tsmc_fragility

## Attacker: Industrial Logistics & Critical Materials Engineer
The Mutator's thesis correctly identifies the critical systemic importance of TSMC's advanced node manufacturing capacity and the profound economic ramifications of its disruption. The topological pivot from a sector-specific multiplier to a systemic leverage factor for leading-edge silicon is conceptually sound, acknowledging the foundational role of these components in modern digital infrastructure. The arithmetic correction of the previous GDP contraction formula's textual explanation is also a necessary improvement.

However, a critical audit of the "LOAD-BEARING VARIABLES" and the Python Falsification Suite reveals instances of parametric grounding that exhibit circular derivation, which compromises the objectivity of the quantitative predictions.

**Critique of Parametric Grounding and "Cooked Books":**

1.  **`SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP = 15.0`**: This is the most significant point of analytical fragility. The thesis explicitly states this factor is "Derived to meet 8-12% GDP contraction target." This constitutes a circular derivation. Instead of being an independently established empirical or theoretical constant, it is reverse-engineered from the desired output range. While the *concept* of a higher systemic leverage for leading-edge chips compared to mature nodes (e.g., 2021 auto-chip shortage's 8.4x multiplier) is valid, the *specific numerical value* of 15x lacks independent justification beyond fulfilling the model's target outcome. This introduces a significant bias towards the catastrophic prediction.

2.  **`DIRECT_DOWNSTREAM_REVENUE_AT_RISK = ~$667B USD`**: While the individual components for Apple, NVIDIA, AMD, and Qualcomm are well-supported, the "$150B" attributed to "estimated other major leading-edge customers" is an aggregated estimate without specific breakdown. While plausible in magnitude, its lack of granular substantiation makes it a potential area for overestimation or underestimation of direct dependence. A more conservative or disaggregated approach might reveal nuances in the degree of reliance or potential for partial mitigation among these "other" customers.

3.  **`EQUITY_BETA_TO_GDP_SHOCK = 1.6`**: Similar to the systemic leverage factor, this beta is stated as "Derived: $4-6T Mkt Cap / $2.5T GDP loss = 1.6-2.4; using 1.6 as lower bound." This is another instance of a constant being derived from the model's desired output range rather than from independent financial market analysis or historical precedent for such a specific, unprecedented shock. While using a lower bound might appear conservative, the method of derivation itself is self-referential, potentially anchoring the market impact prediction to a pre-determined outcome.

4.  **Unaddressed Granularity**: The thesis, despite its stated focus, does not deeply address the "universal applicability of the '30–45 day chemical buffer' across all critical materials and fabs." While a general buffer exists, specific, highly specialized precursors (e.g., certain photoresists, specialty gases, or rare earth elements for polishing slurries) might have shorter effective buffers due to single-source dependencies, specific storage requirements, or extremely long lead times for replenishment, even under normal conditions. Similarly, the resilience of air cargo for high-value/low-volume components under a *blockade* scenario is not fully explored. A comprehensive blockade would likely impact air freight capacity and security, potentially rendering it ineffective for critical, time-sensitive materials. The existence of strategic national or corporate reserves for specific leading-edge chip types or fab materials is also not quantitatively integrated beyond the `ALT_CAP_SUB5NM_PCT`, which primarily refers to manufacturing capacity, not stockpiles.

**So What for the Meta-Judge:**

The Mutator's model, while highlighting a genuinely critical systemic vulnerability, relies on key multipliers that are explicitly derived to achieve a pre-determined catastrophic outcome. This circular reasoning undermines the objectivity and robustness of the specific quantitative predictions for GDP contraction and market capitalization destruction. While the *direction* of the predicted impact (severe economic disruption) is undoubtedly correct given the foundational nature of leading-edge silicon, the *magnitude* is subject to significant analytical bias introduced by these self-referential constants. A more robust analysis requires these critical multipliers to be grounded in independent empirical data or theoretical frameworks, rather than being reverse-engineered from the desired output range. The model's specific numerical claims are therefore highly sensitive to these "cooked" variables, demonstrating a fragility in its quantitative assertions.

---

```python
import math

# LOAD-BEARING VARIABLES (from Mutator's table, for comparison)
TSMC_ADV_SHARE = 0.90
ALT_CAP_SUB5NM_PCT = 0.05
FAB_BUILD_TIME_AVG = 4.0  # years
ASML_LEADTIME_YEARS = 1.5  # years
WORLD_GDP_T = 105.0 # Trillions USD
WORLD_EQ_MKT_T = 115.0 # Trillions USD

# Mutator's "Cooked" Variables for reference
MUTATOR_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP = 15.0
MUTATOR_DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B = 667.0 # Billions USD
MUTATOR_EQUITY_BETA_TO_GDP_SHOCK = 1.6

# --- COUNTER-TEST VARIABLES (Adjusted for more independent grounding) ---
# 1. Adjusted SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP:
# Acknowledging higher leverage than 2021 auto (8.4x) but not reverse-engineered to hit 8-12% GDP target.
# 10.0x is still significant but removes the circular dependency of 15x.
COUNTER_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP = 10.0

# 2. Adjusted DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B:
# Reducing the "estimated other major leading-edge customers" from $150B to $100B,
# reflecting a more conservative estimate of absolute dependence, acknowledging potential minor diversification
# or less direct reliance for some aggregated "other" revenue.
# Apple: $350B, NVIDIA: $115B, AMD: $22B, Qualcomm: $30B, Other: $100B
COUNTER_DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B = 350.0 + 115.0 + 22.0 + 30.0 + 100.0 # Billions USD

# 3. Adjusted EQUITY_BETA_TO_GDP_SHOCK:
# Using a more general, independently observed equity market beta to GDP shocks,
# rather than one derived from the desired output. A beta of 1.2 is a common long-term average for broad markets.
COUNTER_EQUITY_BETA_TO_GDP_SHOCK = 1.2


def compute_z_epi(tsmc_adv_share: float, alt_cap_sub5nm_pct: float,
                   fab_build_time_avg: float, asml_leadtime_years: float,
                   direct_downstream_revenue_at_risk_b: float, world_gdp_t: float,
                   systemic_leverage_factor_final_gdp: float) -> float:
    """
    Calculates the Systemic Economic Paralysis Index (Z_EPI).
    Z_EPI = X_Irreplaceability * Y_Propagation_Coefficient
    """
    X_irreplaceability = (tsmc_adv_share / alt_cap_sub5nm_pct) * \
                         (1 + (fab_build_time_avg / asml_leadtime_years))

    Y_propagation_coefficient = (direct_downstream_revenue_at_risk_b / (world_gdp_t * 1000)) * \
                                 systemic_leverage_factor_final_gdp
    
    return X_irreplaceability * Y_propagation_coefficient

def gdp_contraction_estimate_annual(direct_downstream_revenue_at_risk_b: float,
                                     systemic_leverage_factor_final_gdp: float) -> float:
    """Returns estimated annual GDP loss in $ trillions"""
    return (direct_downstream_revenue_at_risk_b * systemic_leverage_factor_final_gdp) / 1000 # Convert B to T

def equity_market_cap_destruction(gdp_loss_trillion: float, equity_beta: float) -> float:
    """
    Estimates equity market cap destruction based on GDP loss and equity beta.
    Assumes GDP loss is over a specific short period for equity shock calculation.
    """
    return gdp_loss_trillion * equity_beta

print("--- Mutator's Thesis Calculations (for reference) ---")
z_epi_mutator = compute_z_epi(
    tsmc_adv_share=TSMC_ADV_SHARE,
    alt_cap_sub5nm_pct=ALT_CAP_SUB5NM_PCT,
    fab_build_time_avg=FAB_BUILD_TIME_AVG,
    asml_leadtime_years=ASML_LEADTIME_YEARS,
    direct_downstream_revenue_at_risk_b=MUTATOR_DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    world_gdp_t=WORLD_GDP_T,
    systemic_leverage_factor_final_gdp=MUTATOR_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
print(f"Mutator's Calculated Z_EPI: {z_epi_mutator:.2f}")

annual_gdp_loss_mutator_t = gdp_contraction_estimate_annual(
    direct_downstream_revenue_at_risk_b=MUTATOR_DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    systemic_leverage_factor_final_gdp=MUTATOR_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
annual_gdp_loss_mutator_pct = (annual_gdp_loss_mutator_t / WORLD_GDP_T) * 100
print(f"Mutator's Annual GDP loss: ${annual_gdp_loss_mutator_t:.2f}T ({annual_gdp_loss_mutator_pct:.2f}% of World GDP)")

gdp_loss_90d_mutator_t = annual_gdp_loss_mutator_t * (90/365)
mkt_cap_destruction_mutator_t = equity_market_cap_destruction(gdp_loss_90d_mutator_t, MUTATOR_EQUITY_BETA_TO_GDP_SHOCK)
print(f"Mutator's 90-day Mkt Cap Destruction: ~${mkt_cap_destruction_mutator_t:.2f}T")

print("\n--- Counter-Test: Re-evaluating with Independently Grounded Multipliers ---")

# --- COUNTER-TEST Z_EPI CALCULATION ---
z_epi_counter = compute_z_epi(
    tsmc_adv_share=TSMC_ADV_SHARE,
    alt_cap_sub5nm_pct=ALT_CAP_SUB5NM_PCT,
    fab_build_time_avg=FAB_BUILD_TIME_AVG,
    asml_leadtime_years=ASML_LEADTIME_YEARS,
    direct_downstream_revenue_at_risk_b=COUNTER_DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    world_gdp_t=WORLD_GDP_T,
    systemic_leverage_factor_final_gdp=COUNTER_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
print(f"Counter-Test Calculated Z_EPI: {z_epi_counter:.2f}")

# Assert that the Z_EPI is significantly lower than Mutator's, challenging the "catastrophic" threshold of 5.0
# if the multipliers are not "cooked".
assert z_epi_counter < 5.0, \
    f"Counter-Test Z_EPI ({z_epi_counter:.2f}) should be below the Mutator's catastrophic threshold of 5.0 " \
    f"when using independently grounded multipliers, exposing the sensitivity to 'cooked' variables."

# --- COUNTER-TEST ANNUAL GDP CONTRACTION ---
annual_gdp_loss_counter_t = gdp_contraction_estimate_annual(
    direct_downstream_revenue_at_risk_b=COUNTER_DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    systemic_leverage_factor_final_gdp=COUNTER_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
annual_gdp_loss_counter_pct = (annual_gdp_loss_counter_t / WORLD_GDP_T) * 100
print(f"Counter-Test Annual GDP loss: ${annual_gdp_loss_counter_t:.2f}T ({annual_gdp_loss_counter_pct:.2f}% of World GDP)")

# Assert that the annual GDP contraction falls outside the Mutator's target 8-12% range.
assert annual_gdp_loss_counter_pct < 8.0, \
    f"Counter-Test Annual GDP contraction ({annual_gdp_loss_counter_pct:.2f}%) should be below " \
    f"the Mutator's 8-12% target range, demonstrating the insolvency of the target-driven 15x multiplier."

# --- COUNTER-TEST 90-DAY BLOCKADE GDP CONTRACTION ---
gdp_loss_90d_counter_t = annual_gdp_loss_counter_t * (90/365)
print(f"Counter-Test 90-day GDP loss estimate: ${gdp_loss_90d_counter_t:.2f}T")

# Assert that 90-day GDP loss is lower than Mutator's lower bound for market cap impact.
assert gdp_loss_90d_counter_t < 2.0, \
    f"Counter-Test 90-day GDP loss (${gdp_loss_90d_counter_t:.2f}T) should be below Mutator's threshold of $2T, " \
    f"impacting subsequent market cap destruction estimates."

# --- COUNTER-TEST MARKET CAP DESTRUCTION (90-day prediction) ---
mkt_cap_destruction_counter_t = equity_market_cap_destruction(gdp_loss_90d_counter_t, COUNTER_EQUITY_BETA_TO_GDP_SHOCK)
print(f"Counter-Test Equity destruction (90-day): ~${mkt_cap_destruction_counter_t:.2f}T")

# Assert that market cap destruction falls below the Mutator's predicted range.
assert mkt_cap_destruction_counter_t < 3.5, \
    f"Counter-Test Market cap destruction (${mkt_cap_destruction_counter_t:.2f}T) should be below " \
    f"the Mutator's lower bound of $3.5T, challenging the magnitude of the predicted market shock."

print("\nCounter-test assertions passed. The Mutator's specific quantitative claims are shown to be highly sensitive to, and likely inflated by, self-derived multipliers.")

```

### PYTHON EXECUTION OUTPUT:
--- Mutator's Thesis Calculations (for reference) ---
Mutator's Calculated Z_EPI: 6.29
Mutator's Annual GDP loss: $10.01T (9.53% of World GDP)
Mutator's 90-day Mkt Cap Destruction: ~$3.95T

--- Counter-Test: Re-evaluating with Independently Grounded Multipliers ---
Counter-Test Calculated Z_EPI: 3.88
Counter-Test Annual GDP loss: $6.17T (5.88% of World GDP)
Counter-Test 90-day GDP loss estimate: $1.52T
Counter-Test Equity destruction (90-day): ~$1.83T

Counter-test assertions passed. The Mutator's specific quantitative claims are shown to be highly sensitive to, and likely inflated by, self-derived multipliers.


## Attacker: Quantitative Systems Auditor
### Analytical Critique of the Thesis and Python Falsification Suite

The revised thesis correctly identifies a critical conceptual flaw in the previous model: the misapplication of a sector-specific, mature-node economic multiplier (`SEMI_MULTIPLIER`) to a systemic, leading-edge disruption scenario. The topological pivot to a "systemic, interdependent value chain multiplier" for leading-edge silicon is a conceptually sound advancement, acknowledging the foundational role of advanced semiconductors in modern digital economies.

However, a rigorous examination of the "LOAD-BEARING VARIABLES" and the Python falsification suite reveals instances where numerical precision and rigorous derivation are compromised by the introduction of constants explicitly "derived to meet" predetermined output targets. This practice, while achieving the desired numerical outcomes within the model, fundamentally undermines the claim of absolute numerical precision and independent validation.

**1. Scrutiny of $X_{Irreplaceability}$ (Irreplaceable Advanced Capacity Factor):**
*   **`TSMC_ADV_SHARE` (~90%)**: This value is consistent with industry analyst consensus regarding TSMC's dominance in sub-5nm production.
*   **`ALT_CAP_SUB5NM_PCT` (~5-8%)**: The chosen value of 5% is at the lower end of the stated range but is plausible given the significant challenges Samsung and Intel face in matching TSMC's advanced node volume and yield.
*   **`FAB_BUILD_TIME` (3-5 years, average 4 years)**: This range and average are consistent with reported timelines for leading-edge fab construction.
*   **`ASML_LEADTIME` (12-18 months, average 1.5 years)**: This range and average are consistent with ASML's stated lead times for EUV equipment.
*   **Calculation**: The numerical derivation of $X_{Irreplaceability} = 66.0$ is arithmetically precise based on the chosen input values. The underlying parameters appear to be grounded in established industry consensus.

**2. Scrutiny of $Y_{Propagation\_Coefficient}$ (Economic Downstream Impact Multiplier):**
*   **`DIRECT_DOWNSTREAM_REVENUE_AT_RISK` (~$667B USD)**: This aggregate figure is a critical input. While the individual components for Apple, NVIDIA, and AMD are well-supported by their respective financial reports and industry estimates, the "estimated other major leading-edge customers ($150B)" component lacks specific enumeration. For a "detail-oriented mathematician," this significant portion of the at-risk revenue, representing approximately 22.5% of the total, introduces an element of opacity. While the overall magnitude may be plausible, the absence of explicit sources or a breakdown for this segment reduces the verifiability of the input.
*   **`WORLD_GDP` (~$105T USD)**: This is a standard IMF projection and is appropriately applied.
*   **`SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` (15x)**: This is the primary instance of a "cooked book." The thesis explicitly states this factor is "Derived to meet 8-12% GDP contraction target from $667B OEM revenue loss." While the conceptual argument for a higher leverage factor for leading-edge chips is valid, deriving the specific numerical value *to achieve a predetermined output range* constitutes a reverse-engineered constant. It is not an independently validated economic parameter but rather a tuning variable that ensures the model's output aligns with the desired catastrophic prediction. This methodological choice compromises the rigor of the quantitative claim.

**3. Scrutiny of `EQUITY_BETA_TO_GDP_SHOCK` (1.6x):**
*   Similar to the `SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP`, this constant is stated as "Derived: $4-6T Mkt Cap / $2.5T GDP loss = 1.6-2.4; using 1.6 as lower bound." This again indicates a parameter chosen to fit a target output range rather than an independently established financial metric for a systemic shock of this magnitude. While the range 1.6-2.4 might be plausible for severe economic contractions, the explicit derivation to meet the prediction range is a form of tuning.

**4. Python Falsification Suite (Code Review):**
*   **Unit Consistency**: The Python code demonstrates correct handling of units (Billions vs. Trillions) through explicit scaling factors (e.g., `world_gdp_t * 1000` to convert Trillions to Billions, and division by 1000 to convert Billions to Trillions). This is numerically sound.
*   **Variable Mapping**: All variables from the "LOAD-BEARING VARIABLES" table are correctly mapped to their corresponding float inputs in the Python code. Ranges are appropriately converted to single point estimates (e.g., averages).
*   **Calculation Accuracy**: The arithmetic operations within the `compute_z_epi`, `gdp_contraction_estimate_annual`, and `equity_market_cap_destruction` functions are numerically accurate given the input constants.
*   **Assertions**: The `assert` statements are designed to verify that the calculated outputs fall within the predicted ranges (e.g., `8.0 <= annual_gdp_loss_pct <= 12.0`, `mkt_cap_destruction_t >= 3.5` and `mkt_cap_destruction_t <= 6.0`). However, because the `SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` and `EQUITY_BETA_TO_GDP_SHOCK` were explicitly derived to meet these ranges, these assertions function as self-fulfilling prophecies rather than independent validations of the model's predictive power.

**Conclusion on "Cooked Books":**
The primary "cooked books" reside in the derivation and application of `SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` and `EQUITY_BETA_TO_GDP_SHOCK`. These constants are not independently established or empirically validated but are instead reverse-engineered to ensure the model's outputs align with the desired catastrophic predictions. While the conceptual framework for a higher systemic impact is robust, the numerical instantiation of these critical parameters lacks the rigorous, independent grounding expected in formal verification. The model demonstrates what parameters are *required* to achieve a specific outcome, rather than rigorously predicting an outcome from independently verifiable parameters.

---

### So What for the Meta-Judge

The thesis successfully pivots from a dimensionally and contextually flawed economic multiplier, acknowledging the unique systemic criticality of leading-edge semiconductor manufacturing. However, this conceptual improvement is numerically compromised by the introduction of key constants (`SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` and `EQUITY_BETA_TO_GDP_SHOCK`) that are explicitly "derived to meet" predetermined output targets. This methodological choice transforms the model's quantitative predictions from independently verifiable forecasts into a demonstration of the parameter values necessary to achieve a desired catastrophic outcome. While the qualitative risk of a TSMC disruption remains profoundly high, the claimed "absolute numerical precision" and "rigorous derivation" of the specific economic impacts are undermined by this circular reasoning. The model, in its current form, is a calibrated instrument for illustrating a pre-conceived conclusion, rather than a truly predictive one.

---

### COUNTER-TEST

```python
"""
Counter-test harness to expose the insolvency of the Mutator's equation
due to reverse-engineered constants.
This test will use independently derived (or conservatively estimated)
systemic leverage and equity beta factors to demonstrate that the Mutator's
own target-based assertions fail when these constants are not tuned.
All monetary values in USD trillions unless noted.
"""

# Mutator's LOAD-BEARING VARIABLES (from table and thesis)
TSMC_ADV_SHARE = 0.90
ALT_CAP_SUB5NM_PCT = 0.05
FAB_BUILD_TIME_AVG = 4.0  # years
ASML_LEADTIME_YEARS = 1.5  # years
DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B = 667.0 # Billions USD
WORLD_GDP_T = 105.0 # Trillions USD
WORLD_EQ_MKT_T = 115.0 # Trillions USD

# Mutator's TUNED constants (explicitly stated as "derived to meet target")
MUTATOR_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP = 15.0 # 15x
MUTATOR_EQUITY_BETA_TO_GDP_SHOCK = 1.6 # Derived: $4-6T Mkt Cap / $2.5T GDP loss = 1.6-2.4; using 1.6 as lower bound

# AUDITED, INDEPENDENTLY JUSTIFIED CONSTANTS for counter-test
# 1. AUDIT_SYSTEMIC_LEVERAGE_FACTOR:
#    The previous model's mature-node multiplier was 8.4x. While leading-edge is higher,
#    a 15x jump without independent empirical grounding is suspect.
#    We propose a still high, but less aggressively tuned, factor of 12.0x.
#    This reflects the "foundational infrastructure" argument without being explicitly
#    derived to hit the 8-12% GDP target.
AUDIT_SYSTEMIC_LEVERAGE_FACTOR = 12.0

# 2. AUDIT_EQUITY_BETA_TO_GDP_SHOCK:
#    The Mutator's beta is derived to fit a target market cap loss.
#    A general equity beta to GDP for severe shocks is often in the 1.0-2.0 range.
#    We propose a value of 1.4, which is substantial but not tuned to the $4-6T range.
AUDIT_EQUITY_BETA_TO_GDP_SHOCK = 1.4


def compute_z_epi(tsmc_adv_share: float, alt_cap_sub5nm_pct: float,
                   fab_build_time_avg: float, asml_leadtime_years: float,
                   direct_downstream_revenue_at_risk_b: float, world_gdp_t: float,
                   systemic_leverage_factor: float) -> float:
    """
    Calculates the Systemic Economic Paralysis Index (Z_EPI).
    Z_EPI = X_Irreplaceability * Y_Propagation_Coefficient
    """
    # X_Irreplaceability
    X_irreplaceability = (tsmc_adv_share / alt_cap_sub5nm_pct) * \
                         (1 + (fab_build_time_avg / asml_leadtime_years))

    # Y_Propagation_Coefficient
    Y_propagation_coefficient = (direct_downstream_revenue_at_risk_b / (world_gdp_t * 1000)) * \
                                 systemic_leverage_factor
    
    return X_irreplaceability * Y_propagation_coefficient

def gdp_contraction_estimate_annual(direct_downstream_revenue_at_risk_b: float,
                                     systemic_leverage_factor: float) -> float:
    """Returns estimated annual GDP loss in $ trillions"""
    return (direct_downstream_revenue_at_risk_b * systemic_leverage_factor) / 1000 # Convert B to T

def equity_market_cap_destruction(gdp_loss_trillion: float, equity_beta: float) -> float:
    """
    Estimates equity market cap destruction based on GDP loss and equity beta.
    Assumes GDP loss is over a specific short period for equity shock calculation.
    """
    return gdp_loss_trillion * equity_beta

print("--- Mutator's Model (with Tuned Constants) ---")
# --- BASE CASE Z_EPI CALCULATION (Mutator's) ---
z_epi_mutator = compute_z_epi(
    tsmc_adv_share=TSMC_ADV_SHARE,
    alt_cap_sub5nm_pct=ALT_CAP_SUB5NM_PCT,
    fab_build_time_avg=FAB_BUILD_TIME_AVG,
    asml_leadtime_years=ASML_LEADTIME_YEARS,
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    world_gdp_t=WORLD_GDP_T,
    systemic_leverage_factor=MUTATOR_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
print(f"Mutator's Calculated Z_EPI = {z_epi_mutator:.2f}")
assert z_epi_mutator > 5.0, f"Mutator's Z_EPI should exceed catastrophic threshold of 5.0: {z_epi_mutator:.2f}"

# --- ANNUAL GDP CONTRACTION (Mutator's) ---
annual_gdp_loss_t_mutator = gdp_contraction_estimate_annual(
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    systemic_leverage_factor=MUTATOR_SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
annual_gdp_loss_pct_mutator = (annual_gdp_loss_t_mutator / WORLD_GDP_T) * 100
print(f"Mutator's Annual GDP loss: ${annual_gdp_loss_t_mutator:.2f}T ({annual_gdp_loss_pct_mutator:.2f}% of World GDP)")
assert 8.0 <= annual_gdp_loss_pct_mutator <= 12.0, \
    f"Mutator's Annual GDP contraction should be 8-12%: {annual_gdp_loss_pct_mutator:.2f}%"

# --- 90-DAY BLOCKADE GDP CONTRACTION (Mutator's) ---
gdp_loss_90d_t_mutator = annual_gdp_loss_t_mutator * (90/365)
print(f"Mutator's 90-day GDP loss estimate: ${gdp_loss_90d_t_mutator:.2f}T")
assert gdp_loss_90d_t_mutator >= 2.0, f"Mutator's 90-day GDP loss should exceed $2T: ${gdp_loss_90d_t_mutator:.2f}T"

# --- MARKET CAP DESTRUCTION (Mutator's) ---
mkt_cap_destruction_t_mutator = equity_market_cap_destruction(gdp_loss_90d_t_mutator, MUTATOR_EQUITY_BETA_TO_GDP_SHOCK)
print(f"Mutator's Equity destruction (90-day): ~${mkt_cap_destruction_t_mutator:.2f}T")
assert mkt_cap_destruction_t_mutator >= 3.5, f"Mutator's Market cap destruction should exceed $3.5T"
assert mkt_cap_destruction_t_mutator <= 6.0, f"Mutator's Market cap destruction should not exceed $6.0T for 90-day event"
print("Mutator's model passes its own assertions (as expected, due to tuning).\n")


print("--- Counter-Test: Audited Model (with Independently Justified Constants) ---")
# --- BASE CASE Z_EPI CALCULATION (Audited) ---
z_epi_audited = compute_z_epi(
    tsmc_adv_share=TSMC_ADV_SHARE,
    alt_cap_sub5nm_pct=ALT_CAP_SUB5NM_PCT,
    fab_build_time_avg=FAB_BUILD_TIME_AVG,
    asml_leadtime_years=ASML_LEADTIME_YEARS,
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    world_gdp_t=WORLD_GDP_T,
    systemic_leverage_factor=AUDIT_SYSTEMIC_LEVERAGE_FACTOR
)
print(f"Audited Calculated Z_EPI = {z_epi_audited:.2f}")
# We expect this to still be high, but the specific target-driven assertions will fail.
assert z_epi_audited > 4.0, f"Audited Z_EPI should still indicate high risk: {z_epi_audited:.2f}"

# --- ANNUAL GDP CONTRACTION (Audited) ---
annual_gdp_loss_t_audited = gdp_contraction_estimate_annual(
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    systemic_leverage_factor=AUDIT_SYSTEMIC_LEVERAGE_FACTOR
)
annual_gdp_loss_pct_audited = (annual_gdp_loss_t_audited / WORLD_GDP_T) * 100
print(f"Audited Annual GDP loss: ${annual_gdp_loss_t_audited:.2f}T ({annual_gdp_loss_pct_audited:.2f}% of World GDP)")

# CRITICAL ASSERTION: Expose the "cooked books" for GDP contraction
# The Mutator's model *requires* 8-12%. Our audited, non-tuned factor will likely fall outside.
try:
    assert 8.0 <= annual_gdp_loss_pct_audited <= 12.0, \
        f"Audited Annual GDP contraction ({annual_gdp_loss_pct_audited:.2f}%) does NOT meet Mutator's 8-12% target range."
    print("Audited Annual GDP contraction unexpectedly met Mutator's target range.")
except AssertionError as e:
    print(f"ASSERTION FAILED (as expected): {e}")


# --- 90-DAY BLOCKADE GDP CONTRACTION (Audited) ---
gdp_loss_90d_t_audited = annual_gdp_loss_t_audited * (90/365)
print(f"Audited 90-day GDP loss estimate: ${gdp_loss_90d_t_audited:.2f}T")
assert gdp_loss_90d_t_audited >= 1.5, f"Audited 90-day GDP loss should exceed $1.5T: ${gdp_loss_90d_t_audited:.2f}T"


# --- MARKET CAP DESTRUCTION (Audited) ---
mkt_cap_destruction_t_audited = equity_market_cap_destruction(gdp_loss_90d_t_audited, AUDIT_EQUITY_BETA_TO_GDP_SHOCK)
print(f"Audited Equity destruction (90-day): ~${mkt_cap_destruction_t_audited:.2f}T")

# CRITICAL ASSERTION: Expose the "cooked books" for market cap destruction
# The Mutator's model *requires* $3.5-6.0T. Our audited, non-tuned factors will likely fall outside.
try:
    assert mkt_cap_destruction_t_audited >= 3.5 and mkt_cap_destruction_t_audited <= 6.0, \
        f"Audited Market cap destruction (~${mkt_cap_destruction_t_audited:.2f}T) does NOT meet Mutator's $3.5-6.0T target range."
    print("Audited Market cap destruction unexpectedly met Mutator's target range.")
except AssertionError as e:
    print(f"ASSERTION FAILED (as expected): {e}")

print("\nCounter-test complete. The insolvency of the Mutator's equation is exposed by demonstrating that its target-based assertions fail when key constants are not specifically tuned to achieve those targets.")

```

### PYTHON EXECUTION OUTPUT:
--- Mutator's Model (with Tuned Constants) ---
Mutator's Calculated Z_EPI = 6.29
Mutator's Annual GDP loss: $10.01T (9.53% of World GDP)
Mutator's 90-day GDP loss estimate: $2.47T
Mutator's Equity destruction (90-day): ~$3.95T
Mutator's model passes its own assertions (as expected, due to tuning).

--- Counter-Test: Audited Model (with Independently Justified Constants) ---
Audited Calculated Z_EPI = 5.03
Audited Annual GDP loss: $8.00T (7.62% of World GDP)
ASSERTION FAILED (as expected): Audited Annual GDP contraction (7.62%) does NOT meet Mutator's 8-12% target range.
Audited 90-day GDP loss estimate: $1.97T
Audited Equity destruction (90-day): ~$2.76T
ASSERTION FAILED (as expected): Audited Market cap destruction (~$2.76T) does NOT meet Mutator's $3.5-6.0T target range.

Counter-test complete. The insolvency of the Mutator's equation is exposed by demonstrating that its target-based assertions fail when key constants are not specifically tuned to achieve those targets.


## Attacker: Behavioral Economist & System Dynamics Modeler
The thesis presents a significant conceptual advancement by acknowledging and rectifying the fundamental numerical inconsistencies and contextual misapplication of the `SEMI_MULTIPLIER` from its predecessor. The topological pivot, shifting from a sector-specific, static multiplier to a systemic, interdependent value chain multiplier for leading-edge silicon, is a robust and appropriate adjustment for modeling complex adaptive systems. The recognition that leading-edge chips are foundational infrastructure, rather than mere components, correctly identifies a critical chokepoint in the global digital economy. The `Z_{EPI}` equation is a well-structured attempt to quantify this systemic risk, incorporating both irreplaceability and propagation coefficients. Furthermore, the parametric grounding of the load-bearing variables is generally sound, drawing from reputable industry and financial sources, and the Python code demonstrates improved dimensional consistency.

However, the model's predictive independence is compromised by the explicit derivation of the `SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` (15x) to align with a predetermined 8-12% global GDP contraction target. This methodological choice, while yielding a plausible outcome, functions as a tuning parameter rather than an independently validated constant. Such *ex-post facto* parameterization diminishes the model's capacity for unbiased prediction and masks the underlying non-linear dynamics and potential adaptive responses inherent in complex systems.

Specifically, the model's current formulation overlooks several critical aspects of behavioral adaptation and governmental intervention:
1.  **Demand-Side Adjustments:** The model implicitly assumes a direct and immediate cessation of downstream revenue. In reality, demand elasticity, delayed purchases, inventory utilization, and strategic re-prioritization of existing chip supplies could mitigate the immediate shock, even if painfully. Consumers might defer upgrades, and businesses might optimize existing infrastructure, introducing non-linearities not captured by a static revenue-at-risk calculation.
2.  **Adaptive Strategies:** While the "Falsification condition" mentions diversification and yield parity as long-term mitigants, the core model does not dynamically incorporate the potential for accelerated governmental or industry-led adaptive strategies. Emergency fiscal injections (like the predicted CHIPS Act spending), rapid re-tooling efforts (even for less advanced nodes), or international cooperation could alter the `FAB_BUILD_TIME` or `ALT_BUILD_YEARS` parameters, or even reduce the effective `SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` by buffering critical sectors. The model treats these timelines as fixed, which is a simplification in a crisis scenario.
3.  **Temporal Dynamics:** The linear extrapolation of a 90-day GDP loss to market capitalization destruction, while using a beta, simplifies the complex, non-linear feedback loops that characterize financial market responses to systemic shocks. Initial panic might lead to an overshooting of losses, followed by a partial recovery or a prolonged stagnation, rather than a simple linear decay.

In summary, while the thesis makes substantial improvements in identifying the critical systemic risk, its reliance on a tuned leverage factor and its limited integration of adaptive mechanisms within the core predictive model introduce a deterministic bias. The model's sensitivity to this "cooked book" parameter, and its omission of dynamic adaptive responses, represent significant areas for refinement to enhance its robustness as a tool for complex adaptive systems analysis.

**So What for the Meta-Judge:**
The thesis successfully pivots to a more appropriate conceptual framework for assessing leading-edge semiconductor risk, correcting prior arithmetic and contextual errors. However, its primary predictive mechanism for global GDP contraction relies on a `SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP` that is explicitly tuned to achieve a predetermined outcome range. This methodological choice, while producing a plausible result, undermines the model's independent predictive validity and overlooks the potential for non-linear behavioral and governmental adaptive responses that could significantly alter the predicted economic trajectory. The model, therefore, presents a deterministic outcome rather than a truly emergent one, which is a critical limitation for an analysis of complex adaptive systems.

```python
import math

# LOAD-BEARING VARIABLES (from table)
TSMC_ADV_SHARE = 0.90
ALT_CAP_SUB5NM_PCT = 0.05
FAB_BUILD_TIME_AVG = 4.0  # years
ASML_LEADTIME_YEARS = 1.5  # years
DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B = 667.0 # Billions USD
WORLD_GDP_T = 105.0 # Trillions USD
SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP = 15.0 # 15x (Mutator's value, explicitly derived to meet target)
WORLD_EQ_MKT_T = 115.0 # Trillions USD
EQUITY_BETA_TO_GDP_SHOCK = 1.6 # Derived: $4-6T Mkt Cap / $2.5T GDP loss = 1.6-2.4; using 1.6 as lower bound

def compute_z_epi(tsmc_adv_share: float, alt_cap_sub5nm_pct: float,
                   fab_build_time_avg: float, asml_leadtime_years: float,
                   direct_downstream_revenue_at_risk_b: float, world_gdp_t: float,
                   systemic_leverage_factor_final_gdp: float) -> float:
    """
    Calculates the Systemic Economic Paralysis Index (Z_EPI).
    Z_EPI = X_Irreplaceability * Y_Propagation_Coefficient
    """
    # X_Irreplaceability
    X_irreplaceability = (tsmc_adv_share / alt_cap_sub5nm_pct) * \
                         (1 + (fab_build_time_avg / asml_leadtime_years))

    # Y_Propagation_Coefficient
    Y_propagation_coefficient = (direct_downstream_revenue_at_risk_b / (world_gdp_t * 1000)) * \
                                 systemic_leverage_factor_final_gdp
    
    return X_irreplaceability * Y_propagation_coefficient

def gdp_contraction_estimate_annual(direct_downstream_revenue_at_risk_b: float,
                                     systemic_leverage_factor_final_gdp: float) -> float:
    """Returns estimated annual GDP loss in $ trillions"""
    return (direct_downstream_revenue_at_risk_b * systemic_leverage_factor_final_gdp) / 1000 # Convert B to T

def equity_market_cap_destruction(gdp_loss_trillion: float, equity_beta: float) -> float:
    """
    Estimates equity market cap destruction based on GDP loss and equity beta.
    Assumes GDP loss is over a specific short period for equity shock calculation.
    """
    return gdp_loss_trillion * equity_beta

# --- Mutator's BASE CASE Z_EPI CALCULATION ---
z_epi_base = compute_z_epi(
    tsmc_adv_share=TSMC_ADV_SHARE,
    alt_cap_sub5nm_pct=ALT_CAP_SUB5NM_PCT,
    fab_build_time_avg=FAB_BUILD_TIME_AVG,
    asml_leadtime_years=ASML_LEADTIME_YEARS,
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    world_gdp_t=WORLD_GDP_T,
    systemic_leverage_factor_final_gdp=SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
print(f"Mutator's Calculated Z_EPI = {z_epi_base:.2f}")
assert z_epi_base > 5.0, f"Mutator's Z_EPI should exceed catastrophic threshold of 5.0: {z_epi_base:.2f}"

# --- Mutator's ANNUAL GDP CONTRACTION (TARGET 8-12%) ---
annual_gdp_loss_t_mutator = gdp_contraction_estimate_annual(
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    systemic_leverage_factor_final_gdp=SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP
)
annual_gdp_loss_pct_mutator = (annual_gdp_loss_t_mutator / WORLD_GDP_T) * 100
print(f"Mutator's Annual GDP loss from full disruption: ${annual_gdp_loss_t_mutator:.2f}T ({annual_gdp_loss_pct_mutator:.2f}% of World GDP)")
assert 8.0 <= annual_gdp_loss_pct_mutator <= 12.0, \
    f"Mutator's Annual GDP contraction should be 8-12%: {annual_gdp_loss_pct_mutator:.2f}%"

# --- Mutator's 90-DAY BLOCKADE GDP CONTRACTION (for market cap impact) ---
gdp_loss_90d_t_mutator = annual_gdp_loss_t_mutator * (90/365)
print(f"Mutator's 90-day GDP loss estimate: ${gdp_loss_90d_t_mutator:.2f}T")
assert gdp_loss_90d_t_mutator >= 2.0, f"Mutator's 90-day GDP loss should exceed $2T: ${gdp_loss_90d_t_mutator:.2f}T"

# --- Mutator's MARKET CAP DESTRUCTION (90-day prediction) ---
mkt_cap_destruction_t_mutator = equity_market_cap_destruction(gdp_loss_90d_t_mutator, EQUITY_BETA_TO_GDP_SHOCK)
print(f"Mutator's Equity destruction (90-day): ~${mkt_cap_destruction_t_mutator:.2f}T")
assert mkt_cap_destruction_t_mutator >= 3.5, f"Mutator's Market cap destruction should exceed $3.5T"
assert mkt_cap_destruction_t_mutator <= 6.0, f"Mutator's Market cap destruction should not exceed $6.0T for 90-day event"

print("\nMutator's assertions passed. Now, Counter-Test for 'Cooked Books'.")

# --- COUNTER-TEST: Exposing the 'Cooked Book' SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP ---

# The Mutator explicitly states SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP = 15x is "derived to meet 8-12% GDP contraction target".
# This implies it is a tuning parameter rather than an independently validated constant.
# We will test the sensitivity of the model to this parameter by using a slightly different,
# yet still high, leverage factor that is not explicitly tuned to the 8-12% range.

# Scenario: A slightly more conservative (but still high) systemic leverage factor.
# This factor (e.g., 12.0x) is still significantly higher than the 2021 auto-chip multiplier (8.4x),
# acknowledging the increased systemic importance of leading-edge chips, but it is not 15x.
HYPOTHETICAL_SYSTEMIC_LEVERAGE_FACTOR = 12.0

print(f"\n--- Counter-Test Scenario: Using a hypothetical systemic leverage factor of {HYPOTHETICAL_SYSTEMIC_LEVERAGE_FACTOR}x ---")

annual_gdp_loss_t_hypothetical = gdp_contraction_estimate_annual(
    direct_downstream_revenue_at_risk_b=DIRECT_DOWNSTREAM_REVENUE_AT_RISK_B,
    systemic_leverage_factor_final_gdp=HYPOTHETICAL_SYSTEMIC_LEVERAGE_FACTOR
)
annual_gdp_loss_pct_hypothetical = (annual_gdp_loss_t_hypothetical / WORLD_GDP_T) * 100

print(f"Hypothetical Annual GDP loss: ${annual_gdp_loss_t_hypothetical:.2f}T ({annual_gdp_loss_pct_hypothetical:.2f}% of World GDP)")

# Assert that this hypothetical scenario *fails* the Mutator's 8-12% GDP contraction target.
# This demonstrates the sensitivity and the 'tuning' of the Mutator's 15x factor.
try:
    assert 8.0 <= annual_gdp_loss_pct_hypothetical <= 12.0, \
        f"Counter-Test PASSED: Hypothetical GDP contraction ({annual_gdp_loss_pct_hypothetical:.2f}%) falls outside Mutator's 8-12% target range, exposing the sensitivity of the model to the 'tuned' SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP."
except AssertionError as e:
    print(e)

print("\nCounter-Test complete. The model's sensitivity to its 'tuned' parameters is demonstrated.")

```

### PYTHON EXECUTION OUTPUT:
Mutator's Calculated Z_EPI = 6.29
Mutator's Annual GDP loss from full disruption: $10.01T (9.53% of World GDP)
Mutator's 90-day GDP loss estimate: $2.47T
Mutator's Equity destruction (90-day): ~$3.95T

Mutator's assertions passed. Now, Counter-Test for 'Cooked Books'.

--- Counter-Test Scenario: Using a hypothetical systemic leverage factor of 12.0x ---
Hypothetical Annual GDP loss: $8.00T (7.62% of World GDP)
Counter-Test PASSED: Hypothetical GDP contraction (7.62%) falls outside Mutator's 8-12% target range, exposing the sensitivity of the model to the 'tuned' SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP.

Counter-Test complete. The model's sensitivity to its 'tuned' parameters is demonstrated.



## Level 3 Unit Test Results
✅ PASS: The thesis survived its own falsification suite.
Output: Calculated Z_EPI = 6.29
Annual GDP loss from full disruption: $10.01T (9.53% of World GDP)
90-day GDP loss estimate: $2.47T
Equity destruction (90-day): ~$3.95T

All assertions passed. The previous inconsistencies are resolved via topological pivot.


# Final Score: 65
**Weakest Point:** The circular derivation of the SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP (15x) and EQUITY_BETA_TO_GDP_SHOCK (1.6x) parameters. These critical multipliers are explicitly 'tuned' to meet predetermined catastrophic output targets rather than being independently validated, severely compromising the objectivity and robustness of the specific quantitative predictions for GDP contraction and market capitalization destruction.
**Rationale:** The thesis made substantial improvements by addressing previous arithmetic errors and executing a crucial 'topological pivot' from a flawed sector-specific multiplier to a conceptually sound 'systemic, interdependent value chain multiplier' for leading-edge silicon. The retirement of the SEMI_MULTIPLIER axiom was justified, as it accurately identified the contextual inadequacy of a mature-node multiplier for an advanced-node systemic disruption. Furthermore, the new Z_EPI equation appropriately captures irreplaceability and propagation coefficients, and the trigger specificity and falsification conditions are robust and well-defined, leveraging observable, external data points. However, the primary weakness, rigorously exposed by all three attackers, lies in the 'cooked book' derivation of key quantitative parameters, specifically SYSTEMIC_LEVERAGE_FACTOR_FINAL_GDP (15x) and EQUITY_BETA_TO_GDP_SHOCK (1.6x). These were explicitly tuned to achieve predetermined catastrophic output targets (8-12% GDP contraction, $4-6T market cap destruction), thereby undermining the model's independent predictive validity. While the direction of impact (severe economic disruption) is undeniably correct given the foundational nature of leading-edge silicon, the claimed magnitude is subject to this methodological bias. The model also somewhat understates the potential for demand destruction, inventory drawdown, and offsetting equity re-ratings, which contributed to an anti-catastrophism penalty.
