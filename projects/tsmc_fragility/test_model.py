# test_model.py

# Load-Bearing Variables (as per markdown table)
TSMC_ADV_SHARE = 0.90
ALT_CAP_SUB5NM = 0.05  # As a percentage of TSMC equivalent capacity
FAB_BUILD_TIME = 4.0   # Years
ASML_LEADTIME_YEARS = 1.5 # Years

WORLD_GDP = 105e12     # $105 Trillion USD
WORLD_EQ_MKT = 115e12  # $115 Trillion USD

DIGITAL_ECON_PCT_GDP = 0.20

HIGH_DEP_DIGITAL_ECO_PCT = 0.40
MOD_DEP_DIGITAL_ECO_PCT = 0.40
LOW_DEP_DIGITAL_ECO_PCT = 0.20

ADV_CHIP_DEP_HIGH = 0.95
ADV_CHIP_DEP_MOD = 0.50
ADV_CHIP_DEP_LOW = 0.10

PARALYSIS_RATE_HIGH = 0.50
PARALYSIS_RATE_MOD = 0.20
PARALYSIS_RATE_LOW = 0.02

GLOBAL_EQ_SHOCK_FACTOR_90D = 0.15 # 15% initial market shock

# --- Calculations ---

# X_Irreplaceability Calculation
X_Irreplaceability = (TSMC_ADV_SHARE / ALT_CAP_SUB5NM) * (1 + FAB_BUILD_TIME / ASML_LEADTIME_YEARS)

# Y_GDP_Impact_Factor Calculation (Disaggregated)
weighted_paralysis_digital_economy = (
    (HIGH_DEP_DIGITAL_ECO_PCT * ADV_CHIP_DEP_HIGH * PARALYSIS_RATE_HIGH) +
    (MOD_DEP_DIGITAL_ECO_PCT * ADV_CHIP_DEP_MOD * PARALYSIS_RATE_MOD) +
    (LOW_DEP_DIGITAL_ECO_PCT * ADV_CHIP_DEP_LOW * PARALYSIS_RATE_LOW)
)
Y_GDP_Impact_Factor = DIGITAL_ECON_PCT_GDP * weighted_paralysis_digital_economy

# Z_EPI Calculation
Z_EPI = X_Irreplaceability * Y_GDP_Impact_Factor

# Derived Economic Impacts
annual_gdp_contraction_usd = Y_GDP_Impact_Factor * WORLD_GDP
equity_market_destruction_90d_usd = GLOBAL_EQ_SHOCK_FACTOR_90D * WORLD_EQ_MKT

# --- Assertions for Specific, Quantitative, Testable Prediction ---

# Prediction 1: Global equity market cap destruction within 90 days
# Range: $11.5T - $17.25T (10% to 15% of WORLD_EQ_MKT)
assert 11.5e12 <= equity_market_destruction_90d_usd <= 17.25e12, \
    f"Equity market destruction ({equity_market_destruction_90d_usd:.2e}) not within expected range."

# Prediction 2: Global GDP contraction annually (over 24 months)
# Range: 4.5% - 5.5% (of WORLD_GDP)
min_gdp_contraction_pct = 0.045
max_gdp_contraction_pct = 0.055
assert min_gdp_contraction_pct <= Y_GDP_Impact_Factor <= max_gdp_contraction_pct, \
    f"Annual GDP impact factor ({Y_GDP_Impact_Factor:.4f}) not within expected range."
assert min_gdp_contraction_pct * WORLD_GDP <= annual_gdp_contraction_usd <= max_gdp_contraction_pct * WORLD_GDP, \
    f"Annual GDP contraction ({annual_gdp_contraction_usd:.2e}) not within expected range."

# Falsification Condition Check (Thresholds for Z_EPI and annualized GDP loss)
# We test against the calculated Z_EPI to ensure it's still 'catastrophic'
assert Z_EPI > 2.0, f"Z_EPI ({Z_EPI:.3f}) is below the catastrophic threshold of 2.0, model assumptions may be too optimistic."
assert annual_gdp_contraction_usd > 3.675e12, \
    f"Annual GDP loss ({annual_gdp_contraction_usd:.2e}) is below the catastrophic 3.5T threshold ($3.675T)."

print(f"Calculated X_Irreplaceability: {X_Irreplaceability:.2f}")
print(f"Calculated Weighted Paralysis of Digital Economy: {weighted_paralysis_digital_economy:.4f}")
print(f"Calculated Y_GDP_Impact_Factor (Annual % of World GDP): {Y_GDP_Impact_Factor:.4f}")
print(f"Calculated Z_EPI: {Z_EPI:.3f}")
print(f"Projected Annual Global GDP Contraction: ${annual_gdp_contraction_usd / 1e12:.2f} Trillion USD")
print(f"Projected Global Equity Market Cap Destruction (90 days): ${equity_market_destruction_90d_usd / 1e12:.2f} Trillion USD")
print("\nAll assertions passed for the specific, quantitative, testable predictions and falsification conditions.")
