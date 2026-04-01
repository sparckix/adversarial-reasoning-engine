import math

# LOAD-BEARING VARIABLES
OAI_REV = 3.7e9  # OpenAI Q4 2024 Revenue Run Rate
OAI_BURN = 8.0e9  # OpenAI Total Annual Burn
OAI_CURRENT_CASH = 10.0e9  # OpenAI Oct 2024 Cash Reserves
GPT5_TRAIN = 1.25e9  # GPT-5 Class Estimated Training Cost
GPT5_AMORT_YEARS = 2  # Annual amortization period for GPT-5 training
NON_INFERENCE_REV_SHARE = 0.25  # Estimated percentage of OpenAI revenue from non-token sources
AZURE_GM_OSS = 0.70  # Hyperscaler Gross Margin on OSS (Llama 3.1 MaaS)
GPT4O_AVG_PRICE = 10.00  # OpenAI GPT-4o inference price (May 2024 input/output avg)
LONG_CONTEXT_REV_SHARE = 0.30 # Estimated share of enterprise inference revenue derived from long-context, RAG-heavy workloads
COMPUTE_PER_MTOK = 0.04  # Inference compute cost per 1M tokens (H100) for provisioned capacity
C_OPS_PER_MTOK = 0.05  # Hyperscaler Operational Overhead per 1M tokens
C_OSS_CORE_FEATURE_PER_MTOK = 0.06  # OSS Core Feature Integration Cost per 1M tokens
C_HS_INTEGRATION_PER_MTOK = 0.04  # Hyperscaler Enterprise Integration Cost per 1M tokens
LC_KV_CACHE_PENALTY = 2.5  # Long Context KV Cache Throughput Penalty Factor
HS_KV_CACHE_GAIN = 0.40  # Hyperscaler KV Cache Optimization Gain

# Derived Variables & Calculations

# 1. Calculate Lab's Total Annual Cost Burden
Annual_GPT5_Amortization = GPT5_TRAIN / GPT5_AMORT_YEARS
Total_Annual_Cost_to_Cover = OAI_BURN + Annual_GPT5_Amortization

# 2. Calculate Current Inference Revenue & Inferred Token Volume
Non_Inference_Revenue_Value = OAI_REV * NON_INFERENCE_REV_SHARE
Current_Inference_Revenue_Forecast = OAI_REV * (1 - NON_INFERENCE_REV_SHARE)
# Annual_Million_Inference_Tokens_Estimate is used as a baseline for ASP calculation, not a future forecast
Annual_Million_Inference_Tokens_Estimate = Current_Inference_Revenue_Forecast / GPT4O_AVG_PRICE # in Millions of tokens

# 3. Define Proprietary Lab's Required Blended ASP (X)
Inference_Revenue_Needed_for_Breakeven = Total_Annual_Cost_to_Cover - Non_Inference_Revenue_Value
X_Required_ASP_Per_MTOK = Inference_Revenue_Needed_for_Breakeven / Annual_Million_Inference_Tokens_Estimate

# 4. Define Hyperscaler-Controlled Market Blended ASP (Y)
Annual_Million_Long_Context_Inference_Tokens_Estimate = Annual_Million_Inference_Tokens_Estimate * LONG_CONTEXT_REV_SHARE
Annual_Million_Short_Context_Inference_Tokens_Estimate = Annual_Million_Inference_Tokens_Estimate * (1 - LONG_CONTEXT_REV_SHARE)

# Y_SHORT: Market Price Ceiling for Short-Context
C_HS_OSS_SHORT = COMPUTE_PER_MTOK + C_OPS_PER_MTOK + C_OSS_CORE_FEATURE_PER_MTOK + C_HS_INTEGRATION_PER_MTOK
Y_SHORT = C_HS_OSS_SHORT / (1 - AZURE_GM_OSS)

# Y_LONG: Market Price Ceiling for Long-Context (KV Cache Impacted)
COMPUTE_PER_MTOK_LC_HS = COMPUTE_PER_MTOK * LC_KV_CACHE_PENALTY * (1 - HS_KV_CACHE_GAIN)
C_HS_OSS_LONG = COMPUTE_PER_MTOK_LC_HS + C_OPS_PER_MTOK + C_OSS_CORE_FEATURE_PER_MTOK + C_HS_INTEGRATION_PER_MTOK
Y_LONG = C_HS_OSS_LONG / (1 - AZURE_GM_OSS)

# Total Inference Revenue the Proprietary Lab can attain from the market
Total_Inference_Revenue_Attainable = (Annual_Million_Short_Context_Inference_Tokens_Estimate * Y_SHORT) + \
                                     (Annual_Million_Long_Context_Inference_Tokens_Estimate * Y_LONG)

Y_Effective_Market_ASP_Per_MTOK = Total_Inference_Revenue_Attainable / Annual_Million_Inference_Tokens_Estimate

# 5. Unit Economic Inversion & Solvency Destruction (Z)
Z_ASP_Delta = Y_Effective_Market_ASP_Per_MTOK - X_Required_ASP_Per_MTOK
Z_Total_Annual_Loss = Z_ASP_Delta * Annual_Million_Inference_Tokens_Estimate

# Calculate Cash Exhaustion and Solvency Date
OAI_CASH_AFTER_GPT5_TRAIN_OUTLAY = OAI_CURRENT_CASH - GPT5_TRAIN
Months_to_Insolvency = OAI_CASH_AFTER_GPT5_TRAIN_OUTLAY / (abs(Z_Total_Annual_Loss) / 12)

# --- Python Assertions for Test_Model.py ---
assert Total_Annual_Cost_to_Cover > 0, "Total Annual Cost to Cover must be positive."
assert Annual_GPT5_Amortization > 0, "Annual GPT-5 amortization must be positive."
assert Annual_Million_Inference_Tokens_Estimate > 0, "Estimated annual inference tokens must be positive."

assert Y_SHORT > C_HS_OSS_SHORT, "Hyperscaler short-context price must be above its fully loaded cost."
assert Y_LONG > C_HS_OSS_LONG, "Hyperscaler long-context price must be above its long-context fully loaded cost."

# The core insolvency assertion:
assert Z_ASP_Delta < 0, "The proprietary lab's attainable ASP must be lower than its required ASP."
assert Z_Total_Annual_Loss < 0, "The proprietary lab must be operating at an annual loss."
assert Months_to_Insolvency < 24, "Insolvency must occur within 24 months given current burn rates (April 2026 is ~18 months from Oct 2024)."

# Assert that the market-driven ASP is insufficient to cover the required ASP
assert Y_Effective_Market_ASP_Per_MTOK < X_Required_ASP_Per_MTOK, \
    "Effective market ASP must be less than the required ASP for the proprietary lab."

# Print results for the forensic report
print(f"--- Proprietary Lab Solvency Analysis (ASP Unit Economic Inversion) ---")
print(f"Annual GPT-5 Amortization: ${Annual_GPT5_Amortization / 1e9:.3f}B")
print(f"Total Annual Cost to Cover (Burn + Amortization): ${Total_Annual_Cost_to_Cover / 1e9:.3f}B")
print(f"Non-Inference Revenue Value: ${Non_Inference_Revenue_Value / 1e9:.3f}B")
print(f"")
print(f"Proprietary Lab's Inference Revenue Needed for Breakeven: ${Inference_Revenue_Needed_for_Breakeven / 1e9:.3f}B")
print(f"Annual Million Inference Tokens (Baseline for ASP): {Annual_Million_Inference_Tokens_Estimate / 1e6:.2f}B")
print(f"")
print(f"X (Blocked Variable): Proprietary Lab's Required Blended ASP per Million Tokens: ${X_Required_ASP_Per_MTOK:.4f}")
print(f"")
print(f"Hyperscaler's Market Price Ceilings:")
print(f"  - Short-Context (Y_SHORT): ${Y_SHORT:.3f} / 1M tokens")
print(f"  - Long-Context (Y_LONG, KV Cache Impacted): ${Y_LONG:.3f} / 1M tokens")
print(f"Total Inference Revenue Attainable from Market: ${Total_Inference_Revenue_Attainable / 1e9:.3f}B")
print(f"Y (Leverage Variable): Hyperscaler-Defined Effective Market Blended ASP per Million Tokens: ${Y_Effective_Market_ASP_Per_MTOK:.4f}")
print(f"")
print(f"Z (Dependent Variable): Blended ASP Delta (Market Attainable - Lab Required): ${Z_ASP_Delta:.4f} / 1M tokens")
print(f"Proprietary Lab's Overall Annual Operating Loss: ${Z_Total_Annual_Loss / 1e9:.3f}B")
print(f"Cash After GPT-5 Training Outlay: ${OAI_CASH_AFTER_GPT5_TRAIN_OUTLAY / 1e9:.3f}B")
print(f"Months to Insolvency: {Months_to_Insolvency:.2f} months")
