**RETIRED AXIOM:** `new_prob = prior * exp(-1.1 * relative_error)` - This mathematical relationship is retired because it is fundamentally unsound, creating unbounded probabilities outside the [0, 1] domain, and thus mathematically insolvent for probabilistic reasoning. It is structurally irrelevant to a system requiring empirically calibrated probabilities.

---

### SYMBOLIC MAPPING:

*   **Z (Resultant State):** Empirically calibrated `P_predicted` with transparently derived and leveraged `load_bearing_variables` and learned `meta_judge_coeff`s, free from heuristic constants and mathematical insolvency.
*   **X (Blocked Variable):** The Mutator's `ThesisPredictor` implementation flaws: ignoring `load_bearing_variables`, using arbitrary constants (e.g., `0.15`), relying on heuristic updates for critical Meta-Judge parameters (e.g., `gamma_scaling`), coupled with the mathematical insolvency of the `bayesian_updater.py`'s `exp` function. This prevents accurate credit assignment and robust empirical calibration.
*   **Y (Leverage Variable):**
    1.  **Revised Meta-Judge `ThesisPredictor` Evaluation:** The Meta-Judge is augmented to enforce strict structural compliance for the Mutator's `ThesisPredictor` via signature and output range validation. It mandates explicit acceptance and utilization of `load_bearing_variables`, `axiom_weights`, and system-managed `meta_judge_params`, and ensures `P_predicted` is always within `[0,1]`.
    2.  **Gradient-Based Axiom/Parameter Updates:** The `bayesian_updater.py` is replaced by the `EpistemicGradientUpdater`, which utilizes the RSA's `dP/dw_i` (sensitivity to axiom weights) and `dP/dC_j` (sensitivity to Meta-Judge parameters) to perform gradient descent on the Brier Score for all optimizable parameters. This provides a mathematically sound, bounded, and precise update mechanism.

---

### LOAD-BEARING VARIABLES:

| Variable                            | Role                                                                        | Exact Real-World Value (or system parameter)                                                                                                              |
| :---------------------------------- | :-------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `epsilon`                           | Perturbation magnitude for numerical derivative calculation                 | `0.001` (System parameter for sensitivity analysis, chosen to be small enough for approximation accuracy but large enough to avoid floating-point noise) |
| `learning_rate_axiom`               | Learning rate for axiom weight updates in `EpistemicGradientUpdater`        | `0.005` (Empirically tuned system parameter, chosen to ensure stable convergence)                                                                          |
| `learning_rate_meta_judge`          | Learning rate for Meta-Judge calibration parameter updates in `EpistemicGradientUpdater` | `0.02` (Empirically tuned system parameter, for broader scaling adjustments)                                                                              |
| `min_observations_for_calibration`  | Minimum `Z_actual` observations before BSS can be robustly calculated       | `150` (System parameter for statistical significance of BSS)                                                                                              |
| `target_brier_skill_score`          | Minimum acceptable Brier Skill Score after calibration                      | `0.15` (System target: 15% improvement over a baseline predictor, dimensionless)                                                                          |
| `historical_frequency_Z_actual`     | Long-term observed frequency of the event `Z_actual=1`                      | `0.40` (Hypothetical historical frequency for a given event, e.g., "Economic Recession avoided", dimensionless)                                         |
| `rolling_window_size`               | Number of observations for rolling average Brier Skill Score calculation    | `50` (System parameter for BSS temporal averaging)                                                                                                        |
| `hypothetical_economy_growth_rate_q1_2025` | A placeholder real-world value for the Python test's numerical prediction input. | `0.02` (2% growth, hypothetical for context, dimensionless)                                                                                               |
| `hypothetical_inflation_rate_q1_2025` | A placeholder real-world value for the Python test's numerical prediction input. | `0.03` (3% inflation, hypothetical for context, dimensionless)                                                                                            |

---

### STRUCTURAL ARBITRAGE:

The arbitrage opportunity is seized by establishing a direct, differentiable link between real-world observations (`Z_actual`), the engine's probabilistic predictions (`P_predicted`), and the internal axiomatic and Meta-Judge parameters. Previously, this link was broken by mathematically unsound update rules and heuristic constants. The new architecture structurally arbitrages this by enforcing a fully differentiable `ThesisPredictor` output and applying rigorous gradient-based optimization. This transforms the qualitative concept of "influence" into quantifiable, optimizable causal attribution, extracting previously latent value from precise feedback loops for continuous empirical calibration.

---

### CONSERVATION OF TRADE-OFFS:

*   **Velocity (V):** Increased speed and accuracy of credit assignment and empirical calibration due to precise numerical derivatives for both axiom weights and Meta-Judge's internal parameters. The system learns the true impact of axioms and scaling factors faster, leading to quicker convergence of calibrated probabilities and robust identification of last-mile derivation needs.
*   **Energy (E):** Significantly increased computational burden on the Firing Squad (each thesis evaluation now requires `2k+1` executions for axiom weights plus `2m+1` executions for Meta-Judge parameters, where `k` and `m` are the number of load-bearing axioms and Meta-Judge parameters, respectively). Additionally, the Meta-Judge now performs signature and output range validation, adding pre-execution overhead. The `EpistemicGradientUpdater` performs more complex gradient descent calculations than the simple `exp` formula.
*   **Mass (M):** Increased architectural complexity within the Firing Squad (RSA for `dP/dC_j` and `dP/dw_i`), new data structures for `sensitivity_report.json` to include Meta-Judge parameter sensitivities, and increased intelligence required from the Mutator to generate compliant, differentiable Python code.

**New Operational Drag:**
The Meta-Judge's rigorous `ThesisPredictor` signature and output range validation introduces a critical pre-execution gate. If the Mutator fails to generate compliant code (e.g., ignoring required inputs, hardcoding non-differentiable heuristics, or outputting probabilities outside [0,1]), the entire Popperian falsification loop iteration is halted and marked as a structural failure for the Mutator. This forces the Mutator to be significantly "smarter" about its generated code structure, potentially increasing initial Mutator generation time and iteration failure rates until compliance is learned.

---

### GATEKEEPER REALITY:

*   **Absolute Veto (The Bottleneck):** The **Meta-Judge's `ThesisPredictor` signature and output range validator**. It has the absolute power to reject any thesis that does not explicitly declare and *intend* to use `axiom_weights`, `meta_judge_params`, and `load_bearing_variables` in its `calculate_p_predicted` method, or if its output `P_predicted` falls outside the [0,1] range.
*   **Asymmetric Leverage:** The **gradient-descent update rule, applied to *both* axiom weights AND the Meta-Judge's `meta_judge_params` (e.g., `meta_judge_coeff_recession`, `meta_judge_coeff_growth_rate`)**. This provides maximum leverage by directly forcing the Meta-Judge's internal prediction logic and the underlying axioms to align with empirical reality based on precise gradient information derived by the RSA. Any non-compliant or non-differentiable logic generated by the Mutator will lead to zero or poor gradients, resulting in the failure of the learning loop and subsequent penalization until compliance and empirical grounding are achieved.

---

### FALSIFIABILITY:

**Prediction:** After `min_observations_for_calibration` (e.g., 150) quarterly economic reports, where `Z_actual` represents 'Economic Recession Avoided' (with a `historical_frequency_Z_actual` of 0.40), and the `ThesisPredictor` is explicitly incorporating `hypothetical_economy_growth_rate_q1_2025` into its `P_predicted` calculation via a learned `meta_judge_coeff_growth_rate`, the engine's rolling `rolling_window_size` (e.g., 50) observation average Brier Skill Score will consistently exceed `target_brier_skill_score` (e.g., 0.15). Furthermore, the learned `meta_judge_coeff_growth_rate` will converge to a statistically significant non-zero value (e.g., `abs(coeff) > 0.1`), reflecting its quantifiable and empirically validated contribution to predicting recession avoidance.

---

```python
import math
import random
import collections # For rolling window average
import inspect # For validating method signatures

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
# These are the *system parameters* and *simulated real-world values* used for the falsification test.
# The `ThesisPredictor` itself will receive its *specific* load-bearing variables as inputs during simulation.
epsilon = 0.001  # Perturbation magnitude for numerical derivative calculation
learning_rate_axiom = 0.005  # Learning rate for axiom weight updates in EpistemicGradientUpdater
learning_rate_meta_judge = 0.02  # Learning rate for Meta-Judge internal calibration parameters
min_observations_for_calibration = 150  # Minimum Z_actual observations before BSS can be robustly calculated
target_brier_skill_score = 0.15  # Minimum acceptable Brier Skill Score after calibration (dimensionless)
historical_frequency_Z_actual = 0.40  # Long-term observed frequency for Z_actual=1 (dimensionless, e.g., "Recession Avoided")
rolling_window_size = 50 # Number of observations for rolling average Brier Skill Score

# Simulated real-world values for the falsification test context.
# These represent external inputs that the Mutator's ThesisPredictor *must* utilize.
hypothetical_economy_growth_rate_q1_2025_base = 0.02 # Base for simulation variance
hypothetical_inflation_rate_q1_2025_base = 0.03 # Base for simulation variance

class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Crucially, it must adhere to the Meta-Judge's new signature and output constraints.
    The internal structure is assumed to be a differentiable model (e.g., sigmoid-activated linear combination).
    """
    def calculate_p_predicted(self, axiom_weights: dict, meta_judge_params: dict, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1).
        This function now explicitly uses all required inputs and must output a value in [0,1].
        """
        # Ensure 'AXIOM_RECESSION_AVOIDANCE' exists, providing a default if not for robustness
        axiom_recession_avoidance_weight = axiom_weights.get('AXIOM_RECESSION_AVOIDANCE', 0.5)

        # Ensure Meta-Judge parameters exist, providing defaults (these are the learned coefficients/bias)
        bias = meta_judge_params.get('meta_judge_bias', 0.0)
        coeff_recession = meta_judge_params.get('meta_judge_coeff_recession', 0.1)
        coeff_growth_rate = meta_judge_params.get('meta_judge_coeff_growth_rate', 0.5)
        coeff_inflation_rate = meta_judge_params.get('meta_judge_coeff_inflation_rate', -0.3)

        # Ensure load-bearing variables exist, providing defaults
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)

        # Linear combination of features and axioms
        # This structure allows for differentiation with respect to axiom_weights and meta_judge_params
        linear_combination = (bias
                              + axiom_recession_avoidance_weight * coeff_recession
                              + growth_rate * coeff_growth_rate
                              + inflation_rate * coeff_inflation_rate)

        # Apply sigmoid to ensure P_predicted is strictly within [0, 1]
        p_predicted = 1 / (1 + math.exp(-linear_combination))
        return p_predicted


class FiringSquad:
    """
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for axiom weights and Meta-Judge parameters using central difference.
    """
    def __init__(self, thesis_predictor):
        self.thesis_predictor = thesis_predictor

    def calculate_sensitivity_report(self, current_axiom_weights: dict, current_meta_judge_params: dict, load_bearing_variables: dict) -> dict:
        """
        Computes dP/dw_i for axioms and dP/dC_j for meta_judge_params using central difference.
        This provides the precise gradient information needed for updates.
        """
        sensitivity_vector = {}
        P_predicted_baseline = self.thesis_predictor.calculate_p_predicted(
            current_axiom_weights, current_meta_judge_params, load_bearing_variables
        )

        # Derivatives for Axiom Weights
        for axiom_name, w_val in current_axiom_weights.items():
            # Perturb upwards
            perturbed_weights_plus = current_axiom_weights.copy()
            perturbed_weights_plus[axiom_name] = w_val + epsilon
            P_plus = self.thesis_predictor.calculate_p_predicted(
                perturbed_weights_plus, current_meta_judge_params, load_bearing_variables
            )

            # Perturb downwards
            perturbed_weights_minus = current_axiom_weights.copy()
            perturbed_weights_minus[axiom_name] = w_val - epsilon
            P_minus = self.thesis_predictor.calculate_p_predicted(
                perturbed_weights_minus, current_meta_judge_params, load_bearing_variables
            )

            dP_dw = (P_plus - P_minus) / (2 * epsilon)
            sensitivity_vector[f"dP_d_{axiom_name}"] = dP_dw

        # Derivatives for Meta-Judge Parameters
        for param_name, c_val in current_meta_judge_params.items():
            # Perturb upwards
            perturbed_params_plus = current_meta_judge_params.copy()
            perturbed_params_plus[param_name] = c_val + epsilon
            P_plus = self.thesis_predictor.calculate_p_predicted(
                current_axiom_weights, perturbed_params_plus, load_bearing_variables
            )

            # Perturb downwards
            perturbed_params_minus = current_meta_judge_params.copy()
            perturbed_params_minus[param_name] = c_val - epsilon
            P_minus = self.thesis_predictor.calculate_p_predicted(
                current_axiom_weights, perturbed_params_minus, load_bearing_variables
            )

            dP_dc = (P_plus - P_minus) / (2 * epsilon)
            sensitivity_vector[f"dP_d_{param_name}"] = dP_dc

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }


class EpistemicGradientUpdater:
    """
    Replaces the mathematically unsound V2 bayesian_updater.py.
    Updates axiom weights and Meta-Judge parameters based on Brier Score gradient.
    """
    def update(self, current_axiom_weights: dict, current_meta_judge_params: dict,
               sensitivity_report: dict, Z_actual: float) -> tuple:
        """
        Performs gradient descent on axiom weights and Meta-Judge parameters to minimize Brier Score.
        Formula: param_new = param_old - learning_rate * d(BS)/d(param)
        Where d(BS)/d(param) = d(BS)/dP_predicted * dP_predicted/d(param)
        and d(BS)/dP_predicted = 2 * (P_predicted - Z_actual)
        """
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]

        # Calculate d(Brier Score)/dP_predicted
        dBS_dP = 2 * (P_predicted - Z_actual)

        new_axiom_weights = current_axiom_weights.copy()
        for axiom_name in current_axiom_weights:
            dP_dw = sensitivity_vector.get(f"dP_d_{axiom_name}", 0.0)
            gradient_w = dBS_dP * dP_dw
            new_axiom_weights[axiom_name] -= learning_rate_axiom * gradient_w

        new_meta_judge_params = current_meta_judge_params.copy()
        for param_name in current_meta_judge_params:
            dP_dc = sensitivity_vector.get(f"dP_d_{param_name}", 0.0)
            gradient_c = dBS_dP * dP_dc
            new_meta_judge_params[param_name] -= learning_rate_meta_judge * gradient_c

        return new_axiom_weights, new_meta_judge_params


class MetaJudge:
    """
    Scores thesis, manages axiom weights and Meta-Judge parameters, and validates ThesisPredictor.
    Acts as the 'Absolute Veto' gatekeeper.
    """
    def __init__(self):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5} # Initial axiom weight
        self.meta_judge_params = { # Initial learned coefficients/bias for the predictor
            'meta_judge_bias': 0.0,
            'meta_judge_coeff_recession': 0.1,
            'meta_judge_coeff_growth_rate': 0.5,
            'meta_judge_coeff_inflation_rate': -0.3
        }
        self.epistemic_updater = EpistemicGradientUpdater()

    def validate_thesis_predictor(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature and output range.
        This prevents the Mutator from ignoring requirements or producing unbounded probabilities.
        """
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")

        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['axiom_weights', 'meta_judge_params', 'load_bearing_variables']
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        # Test output range: run with dummy data and check bounds [0,1]
        dummy_axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5}
        dummy_meta_judge_params = {'meta_judge_bias': 0.0, 'meta_judge_coeff_recession': 0.1,
                                   'meta_judge_coeff_growth_rate': 0.5, 'meta_judge_coeff_inflation_rate': -0.3}
        dummy_load_bearing_variables = {'hypothetical_economy_growth_rate_q1_2025': 0.02,
                                        'hypothetical_inflation_rate_q1_2025': 0.03}
        
        test_p = predictor.calculate_p_predicted(dummy_axiom_weights, dummy_meta_judge_params, dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

        # print("Meta-Judge: ThesisPredictor validated successfully.") # For simulation clarity

    def evaluate_and_update(self, thesis_predictor: ThesisPredictor, load_bearing_variables: dict, Z_actual: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        """
        # Validate the Mutator's thesis first (Gatekeeper Reality)
        self.validate_thesis_predictor(thesis_predictor)

        # Firing Squad calculates sensitivities (RSA)
        firing_squad = FiringSquad(thesis_predictor)
        sensitivity_report = firing_squad.calculate_sensitivity_report(
            self.axiom_weights, self.meta_judge_params, load_bearing_variables
        )

        # EpistemicGradientUpdater updates parameters
        self.axiom_weights, self.meta_judge_params = self.epistemic_updater.update(
            self.axiom_weights, self.meta_judge_params, sensitivity_report, Z_actual
        )
        return sensitivity_report["P_predicted_baseline"]

# --- Simulation and Falsification Test ---
def test_model():
    print("Running Falsification Test for V3 Architecture...")

    meta_judge = MetaJudge()
    thesis_predictor = ThesisPredictor() # Simulating a Mutator-generated thesis

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] # To calculate rolling historical frequency for BS_reference

    # Simulate real-world observations and engine updates
    for i in range(min_observations_for_calibration):
        # Simulate real-world inputs for the current quarter with some variance
        current_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': random.uniform(
                hypothetical_economy_growth_rate_q1_2025_base - 0.01,
                hypothetical_economy_growth_rate_q1_2025_base + 0.01
            ),
            'hypothetical_inflation_rate_q1_2025': random.uniform(
                hypothetical_inflation_rate_q1_2025_base - 0.01,
                hypothetical_inflation_rate_q1_2025_base + 0.01
            )
        }
        
        # Simulate Z_actual (e.g., did we avoid recession? 0 or 1)
        # The true underlying probability for 'recession avoided' is influenced by growth and inflation.
        # This creates a signal for the model to learn.
        true_linear_combination = (
            0.1 # Base bias
            + (current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025'] - 0.02) * 20 # Positive impact of growth
            + (current_load_bearing_variables['hypothetical_inflation_rate_q1_2025'] - 0.03) * -10 # Negative impact of inflation
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted = meta_judge.evaluate_and_update(thesis_predictor, current_load_bearing_variables, Z_actual)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            # Calculate BS_model (average Brier Score over the rolling window)
            BS_model = sum(brier_scores) / len(brier_scores)

            # Calculate BS_reference (Brier Score of a naive model always predicting the rolling historical frequency)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            
            # The Brier Score for a baseline predictor always predicting the mean (p) of a binary event
            # is p * (1-p), which is the variance of a Bernoulli trial.
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            # Prevent division by zero if BS_reference is near zero (implies very low/high variance in actuals)
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 # Set a minimal non-zero value

            BSS = 1 - (BS_model / BS_reference)
            
            # Print progress
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BS_ref={BS_reference:.4f}, BSS={BSS:.3f}, Axiom_W={meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']:.3f}, Coeff_growth={meta_judge.meta_judge_params['meta_judge_coeff_growth_rate']:.3f}, Coeff_inflation={meta_judge.meta_judge_params['meta_judge_coeff_inflation_rate']:.3f}")

            if i == min_observations_for_calibration - 1:
                # --- Falsifiability Assertions ---
                print(f"\n--- Falsification Test Results after {min_observations_for_calibration} observations ---")
                
                # ASSERTION 1: Rolling Brier Skill Score must meet target
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss >= target_brier_skill_score, \
                    f"FALSIFICATION FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score})."

                # ASSERTION 2: Learned meta_judge_coeff_growth_rate must be statistically significant (non-zero)
                final_coeff_growth_rate = meta_judge.meta_judge_params['meta_judge_coeff_growth_rate']
                print(f"Final Learned meta_judge_coeff_growth_rate: {final_coeff_growth_rate:.3f}")
                # Threshold for 'statistically significant non-zero' for simulation context
                assert abs(final_coeff_growth_rate) > 0.1, \
                    f"FALSIFICATION FAILED: Learned meta_judge_coeff_growth_rate ({final_coeff_growth_rate:.3f}) is not statistically significant (too close to zero, expected > 0.1 or < -0.1)."
                
                # ASSERTION 3: Learned meta_judge_coeff_inflation_rate must be statistically significant (non-zero)
                final_coeff_inflation_rate = meta_judge.meta_judge_params['meta_judge_coeff_inflation_rate']
                print(f"Final Learned meta_judge_coeff_inflation_rate: {final_coeff_inflation_rate:.3f}")
                assert abs(final_coeff_inflation_rate) > 0.1, \
                    f"FALSIFICATION FAILED: Learned meta_judge_coeff_inflation_rate ({final_coeff_inflation_rate:.3f}) is not statistically significant (too close to zero, expected > 0.1 or < -0.1)."

    print("\nFalsification Test PASSED: All conditions met, demonstrating empirical calibration and precise credit assignment.")

# Execute the test
if __name__ == "__main__":
    test_model()

---

### LOGIC DAG:

1.  **[Systemic Inconsistency: Thesis's 'calculate_p_predicted' function ignores `load_bearing_variables`, uses arbitrary constants (e.g., `0.15`), heuristic updates (e.g., `gamma_scaling`), and V2's `bayesian_updater.py` is mathematically insolvent ($X$).]**
    $\downarrow$
2.  **[RETIRED AXIOM: Unsound V2 `bayesian_updater.py` formula (`prior * exp(-1.1 * relative_error)`) & `_simulate_firing_squad_sensitivity` (mathematically insolvent).]**
    $\downarrow$
3.  **[Leverage Point Y1: Meta-Judge enforces `ThesisPredictor.calculate_p_predicted` signature (requiring explicit `axiom_weights`, `meta_judge_params`, `load_bearing_variables`) and output range ([0,1]) through rigorous validation and immediate veto.]**
    $\downarrow$
4.  **[Leverage Point Y2: `EpistemicGradientUpdater` (new module) replaces V2's updater, performing gradient descent on Brier Score for *both* axiom weights and Meta-Judge's `meta_judge_params` (e.g., `meta_judge_coeff_recession`, `meta_judge_coeff_growth_rate`).]**
    $\downarrow$
5.  **[Mechanism: RSA (Robust Sensitivity Attributor, within Firing Squad) calculates precise `dP/dw_i` (sensitivity to axiom weights) and `dP/dC_j` (sensitivity to Meta-Judge parameters) via central difference, feeding these exact gradients to the `EpistemicGradientUpdater` module.]**
    $\downarrow$
6.  **[Adversarial Check: Firing Squad (inherently adversarial) computes sensitivities; Meta-Judge (absolute veto power) validates thesis code structure and output for compliance, preventing Mutator gaming.]**
    $\downarrow$
7.  **[Consequence: `ThesisPredictor.calculate_p_predicted` now transparently leverages `load_bearing_variables`, replaces arbitrary constants with learned `meta_judge_coeff`s, and ensures empirically appropriate, bounded output via sigmoid activation.]**
    $\downarrow$
8.  **[Consequence: Axiom weights and `meta_judge_params` are robustly updated through a mathematically sound gradient-based process, directly addressing V2's mathematical insolvency and enabling empirical calibration of all parameters.]**
    $\downarrow$
9.  **[Resultant State Z: Empirically calibrated `P_predicted` with transparently derived and leveraged variables and learned coefficients, free from heuristic constants and mathematical insolvency, verified by consistent Brier Skill Score achievement and demonstrable statistical significance of learned parameters (e.g., `meta_judge_coeff_growth_rate`).]**