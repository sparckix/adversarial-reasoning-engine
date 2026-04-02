import math

def calculate_bounded_error(z_predicted: float, z_actual: float, n_scale: float) -> float:
    """
    Computes absolute error bounded by hyperbolic tangent.
    Resolves negative outcome mathematically natively. Zero division impossible.
    """
    assert n_scale > 0, "Normalization scale must be positive non-zero."
    raw_magnitude = abs(z_predicted - z_actual)
    return math.tanh(raw_magnitude / n_scale)

def calculate_capped_latency_penalty(rag_latency: float, max_latency: float, weight: float) -> float:
    """
    Computes latency penalty with a strict mathematical ceiling of 1.0 * weight.
    """
    assert max_latency > 0, "Max latency must be positive non-zero."
    normalized_latency = rag_latency / max_latency
    capped_latency = min(1.0, normalized_latency)
    return capped_latency * weight

def evaluate_axiom_survival(
    z_predicted: float,
    z_actual: float,
    n_scale: float,
    rag_latency: float,
    max_latency: float,
    latency_weight: float,
    empirical_sensitivities: dict,
    survival_threshold: float
) -> dict:
    """
    Updates the axiomatic logic gates based on Exogenous Empirical Sensitivity.
    """
    e_bounded = calculate_bounded_error(z_predicted, z_actual, n_scale)
    p_lat = calculate_capped_latency_penalty(rag_latency, max_latency, latency_weight)
    
    axiom_states = {}
    for axiom_id, sensitivity in empirical_sensitivities.items():
        # Baseline truth (1.0) minus empirical error responsibility minus operational drag
        viability_score = 1.0 - (e_bounded * sensitivity) - p_lat
        
        # Binary state update
        axiom_states[axiom_id] = {
            "score": round(viability_score, 3),
            "state": 1 if viability_score >= survival_threshold else 0
        }
        
    return axiom_states, round(e_bounded, 3), round(p_lat, 3)

def test_model():
    # TEST SCENARIO 1: Negative actuals (Math Insolvency Bypass)
    Z_PRED = -1.5  # Billions
    Z_ACT = -2.1   # Billions
    N_SCALE = 5.0  # Billions threshold
    
    # TEST SCENARIO 2: Unbounded Latency (Weakest Link Pivot)
    RAG_LATENCY = 6.0  # Seconds
    MAX_LATENCY = 5.0  # Seconds
    LAT_WEIGHT = 0.15
    SURVIVAL_THRESHOLD = 0.50
    
    # Adversarially calculated sensitivities (Mutator cannot access this generation process)
    EMPIRICAL_SENSITIVITIES = {
        "Axiom_A_Core_Logic": 1.0,  # Highly responsible for the prediction
        "Axiom_B_Fluff": 0.0        # Prediction didn't change when removed
    }
    
    results, e_bounded, p_lat = evaluate_axiom_survival(
        Z_PRED, Z_ACT, N_SCALE, RAG_LATENCY, MAX_LATENCY, LAT_WEIGHT, EMPIRICAL_SENSITIVITIES, SURVIVAL_THRESHOLD
    )
    
    # ASSERTIONS (Strict Quantitative Falsifiability)
    # 1. Math Insolvency Resolution (Error must evaluate, not error out on division by zero/negatives)
    assert e_bounded == 0.119, f"Expected Bounded Error 0.119, got {e_bounded}"
    
    # 2. Latency Unbounded Fix (Penalty must be exactly 0.15, not 0.18 which would occur without min cap)
    assert p_lat == 0.150, f"Expected Capped Penalty 0.150, got {p_lat}"
    
    # 3. Axiom State Checks
    assert results["Axiom_A_Core_Logic"]["score"] == 0.731, f"Expected Axiom A score 0.731, got {results['Axiom_A_Core_Logic']['score']}"
    assert results["Axiom_A_Core_Logic"]["state"] == 1, "Axiom A should survive."
    
    assert results["Axiom_B_Fluff"]["score"] == 0.850, "Fluff avoids error penalty, but still absorbs latency penalty."
    
    # 4. Collapse Test: Severe prediction failure
    collapse_results, e_bounded_collapse, _ = evaluate_axiom_survival(
        10.0, -2.1, N_SCALE, 1.0, MAX_LATENCY, LAT_WEIGHT, {"Axiom_C": 1.0}, SURVIVAL_THRESHOLD
    )
    # Error should asymptote near 1.0 (tanh(12.1/5.0) = ~0.984)
    assert e_bounded_collapse == 0.984, "Bounded error failed to approach 1.0 under massive failure."
    assert collapse_results["Axiom_C"]["state"] == 0, "Axiom C should be purged under severe predictive failure."

    print("ALL TESTS PASSED: Mathematical solvency and structural bounds verified.")

if __name__ == "__main__":
    test_model()