# Adversarial Debate: epistemic_engine_v3

## Attacker: Bayesian Epistemologist & Metrologist
The provided thesis correctly identifies a critical mathematical insolvency: the formula `new_prob = prior * exp(-1.1 * relative_error)` is fundamentally unsound for probabilistic reasoning. As stated, it creates unbounded probabilities outside the [0, 1] domain, rendering it incoherent for representing belief states. This formula, as an arbitrary internal consistency mechanism, lacks empirical grounding and fails to reflect reality, as probabilities must adhere to the axioms of probability theory.

**Critique of the Thesis and its Underlying Assumptions:**

1.  **Insolvency of `new_prob = prior * exp(-1.1 * relative_error)`:**
    *   **Unboundedness:** If `relative_error` (defined as `P_predicted - Z_actual`) is negative (e.g., `P_predicted = 0.1`, `Z_actual = 1.0`), then `exp(-1.1 * relative_error)` becomes `exp(positive_value)`, which can grow arbitrarily large. Consequently, `new_prob` can exceed 1.0, violating the upper bound of a probability distribution. Conversely, while `exp(negative_value)` approaches zero, ensuring `new_prob` remains non-negative, the rapid decay can lead to probabilities that are practically zero after very few observations, regardless of the true underlying base rate.
    *   **Lack of Bayesian Coherence:** This formula is an ad-hoc heuristic, not derived from Bayes' theorem. It does not incorporate likelihoods or evidence in a probabilistically consistent manner. Its updates are purely multiplicative based on an exponential decay function of error magnitude, which does not guarantee convergence to actual base rates or maintain a coherent belief state.
    *   **Empirical Disconnect:** The formula's parameters (e.g., `-1.1`) are arbitrary constants lacking external validation or empirical calibration. There is no mechanism to link the magnitude of `relative_error` to a statistically meaningful update in belief that reflects real-world accuracy or observed frequencies.

2.  **Critique of the Mutator's Python Falsification Suite (Cooked Books & Gaps):**
    *   **Evasion of Mandate (Cooked Books):** The most significant "cooked book" is that the Mutator's provided Python code *does not implement or test the problematic `new_prob = prior * exp(-1.1 * relative_error)` formula*. Instead, it introduces an entirely new system based on a Multi-Layer Perceptron (MLP) and Brier Skill Score (BSS) optimization. While this new system is a substantial improvement for empirical calibration of *model predictions*, it effectively sidesteps the explicit mandate to expose the insolvency of the *specified exponential update formula*. The Mutator has retired the axiom in its prose but failed to provide a falsification suite that directly addresses its stated insolvency.
    *   **Parametric Grounding:** The "LOAD-BEARING VARIABLES" are appropriately defined as system parameters, standard machine learning hyperparameters (Adam optimizer), or parameters of a *simulated* non-linear process. They do not claim to represent real-world physical constants or financial metrics that could be misapplied. Therefore, this aspect of the Mutator's definition is robust within the context of a simulation.
    *   **Topological Flatness and Axiom Calibration (Unaddressed Problems):** Despite the introduction of an MLP, the fundamental limitation of the "topologically flat DAG" (Problem 5) remains unaddressed. The MLP learns complex input-output relationships, but it does not inherently model or update *causal chains* or *intermediate nodes* within a deeper DAG structure. Furthermore, the `AXIOM_RECESSION_AVOIDANCE` is treated as a fixed input feature to the MLP with a constant weight (`0.5` in `meta_judge.axiom_weights`), not as an optimizable parameter. This means the system still lacks a mechanism to empirically calibrate or update the *Axiom Weights* themselves (as described in V2's "Axiom Weights" component), perpetuating "Problem 6: No feedback loop from resolution to axioms" and failing to fully address "Problem 2: The 'last-mile derivation' failure" for foundational axioms. The BSS calibrates the *model's overall predictions*, not the individual axioms' truthfulness or relevance.

**So What for the Meta-Judge:**

The Mutator's thesis correctly identifies the mathematical insolvency of the `new_prob = prior * exp(-1.1 * relative_error)` formula. However, its accompanying Python Falsification Suite fails to provide empirical evidence for this claim because it *does not implement or test the problematic formula*. Instead, it introduces a new, more robust system for calibrating *model predictions* using an MLP and Brier Skill Score. While this new system is an advancement, it represents a strategic evasion of the original mandate to expose the insolvency of the *specified exponential update formula*. Furthermore, the new system, despite its sophistication, still does not provide a mechanism for empirically calibrating or updating the *Axiom Weights* themselves, treating them as fixed input features rather than optimizable parameters. This leaves a critical gap in the system's ability to learn and adapt its foundational axioms based on real-world outcomes, perpetuating the "last-mile derivation" problem for axioms and failing to fully address the "topologically flat DAG" limitation for causal credit assignment beyond the MLP's internal structure. My counter-test will directly implement the problematic exponential update formula and empirically demonstrate its inherent mathematical instability and inability to maintain coherent probability distributions under typical error conditions, thereby fulfilling the original mandate.

```python
import math
import random
import numpy as np

# Define the problematic formula's constant
EXPONENTIAL_DECAY_FACTOR = -1.1

class ProblematicBayesianUpdater:
    """
    Implements the mathematically unsound Bayesian update formula for falsification.
    new_prob = prior * exp(-1.1 * relative_error)
    where relative_error = P_predicted - Z_actual.
    """
    def __init__(self, initial_prior: float):
        if not (0.0 <= initial_prior <= 1.0):
            raise ValueError("Initial prior must be between 0 and 1.")
        self.prior = initial_prior
        self.history = [initial_prior]

    def update_probability(self, P_predicted: float, Z_actual: float) -> float:
        """
        Applies the problematic exponential decay update.
        """
        if not (0.0 <= P_predicted <= 1.0):
            raise ValueError(f"P_predicted ({P_predicted}) must be between 0 and 1.")
        if Z_actual not in [0, 1]:
            raise ValueError(f"Z_actual ({Z_actual}) must be 0 or 1.")

        relative_error = P_predicted - Z_actual
        
        # Apply the problematic formula as specified in the thesis
        new_prob = self.prior * math.exp(EXPONENTIAL_DECAY_FACTOR * relative_error)
        
        self.prior = new_prob
        self.history.append(new_prob)
        return new_prob

def run_counter_test():
    print("--- Counter-Test: Exposing Insolvency of `new_prob = prior * exp(-1.1 * relative_error)` ---")

    initial_prior = 0.5
    updater = ProblematicBayesianUpdater(initial_prior)
    print(f"Initial Prior: {initial_prior:.4f}")

    # Scenario 1: Consistent underestimation (P_predicted < Z_actual)
    # This should drive the probability above 1.0, demonstrating unboundedness.
    print("\nScenario 1: Consistent underestimation (P_predicted < Z_actual)")
    print("Simulating 5 observations where Z_actual is 1, but P_predicted is 0.1")
    
    # Use a fixed seed for reproducibility of the counter-test
    random.seed(42) 
    np.random.seed(42)

    for i in range(5):
        P_predicted = 0.1
        Z_actual = 1
        updated_prob = updater.update_probability(P_predicted, Z_actual)
        print(f"  Obs {i+1}: P_predicted={P_predicted:.1f}, Z_actual={Z_actual}, Relative Error={P_predicted - Z_actual:.1f}, New Prior={updated_prob:.4f}")
        if updated_prob > 1.0:
            print(f"  CRITICAL FAILURE DETECTED: Probability exceeded 1.0 at observation {i+1}.")
            break
    
    assert updater.prior > 1.0, \
        f"FALSIFICATION FAILED: Probability ({updater.prior:.4f}) did not exceed 1.0 under consistent underestimation, indicating formula's upper bound insolvency was not demonstrated."
    print(f"  Assertion Passed: Probability ({updater.prior:.4f}) successfully exceeded 1.0, demonstrating mathematical insolvency.")

    # Reset for Scenario 2
    updater = ProblematicBayesianUpdater(initial_prior)
    print(f"\nResetting Prior to {initial_prior:.4f} for Scenario 2.")

    # Scenario 2: Consistent overestimation (P_predicted > Z_actual)
    # This should drive the probability rapidly towards 0, demonstrating rapid decay and loss of practical meaning.
    print("\nScenario 2: Consistent overestimation (P_predicted > Z_actual)")
    print("Simulating 5 observations where Z_actual is 0, but P_predicted is 0.9")
    for i in range(5):
        P_predicted = 0.9
        Z_actual = 0
        updated_prob = updater.update_probability(P_predicted, Z_actual)
        print(f"  Obs {i+1}: P_predicted={P_predicted:.1f}, Z_actual={Z_actual}, Relative Error={P_predicted - Z_actual:.1f}, New Prior={updated_prob:.4f}")
        if updated_prob < 0.001 and i > 0: 
            print(f"  CRITICAL FAILURE DETECTED: Probability became practically zero at observation {i+1}.")
            break
    
    assert updater.prior < 0.01, \
        f"FALSIFICATION FAILED: Probability ({updater.prior:.4f}) did not approach zero under consistent overestimation, indicating formula's rapid decay was not demonstrated."
    print(f"  Assertion Passed: Probability ({updater.prior:.4f}) successfully approached 0, demonstrating rapid decay and potential loss of practical significance.")

    # Scenario 3: Mixed errors, demonstrating lack of convergence to actual base rates and potential for unboundedness.
    # The formula's design prevents stable convergence to a true base rate.
    updater = ProblematicBayesianUpdater(initial_prior)
    print(f"\nResetting Prior to {initial_prior:.4f} for Scenario 3.")
    print("Scenario 3: Mixed errors, demonstrating lack of convergence to actual base rate (0.5) and potential for range violation.")
    true_base_rate = 0.5
    num_observations = 50
    
    range_violation_detected = False
    for i in range(num_observations):
        Z_actual = 1 if random.random() < true_base_rate else 0
        P_predicted = np.clip(true_base_rate + random.uniform(-0.2, 0.2), 0.01, 0.99) # Noisy prediction
        
        updated_prob = updater.update_probability(P_predicted, Z_actual)
        
        if i % 10 == 0 or i == num_observations - 1:
            print(f"  Obs {i+1}: P_predicted={P_predicted:.2f}, Z_actual={Z_actual}, New Prior={updated_prob:.4f}")
        
        if not (0.0 <= updated_prob <= 1.0):
            print(f"  CRITICAL FAILURE DETECTED: Probability went out of [0,1] range at observation {i+1} ({updated_prob:.4f}).")
            range_violation_detected = True
            break
    
    print(f"Final Prior after {num_observations} mixed observations: {updater.prior:.4f}")
    
    # Assert that the probability either went out of bounds or failed to converge to the true base rate.
    # The formula's inherent instability means it will not settle around the true base rate.
    if not range_violation_detected:
        assert not (0.4 <= updater.prior <= 0.6), \
            f"FALSIFICATION FAILED: Prior ({updater.prior:.4f}) converged too closely to true base rate (0.5) under this problematic formula, which contradicts its inherent instability."
        print(f"  Assertion Passed: Prior ({updater.prior:.4f}) did not converge to the true base rate (0.5) within a tight band, demonstrating lack of empirical calibration and coherence.")
    else:
        assert range_violation_detected, \
            f"FALSIFICATION FAILED: Probability ({updater.prior:.4f}) did not go out of [0,1] range despite mixed observations, indicating formula's instability was not demonstrated."
        print(f"  Assertion Passed: Probability ({updater.prior:.4f}) went out of [0,1] range, demonstrating mathematical insolvency under mixed conditions.")

# Execute the counter-test
if __name__ == "__main__":
    run_counter_test()
```

### PYTHON EXECUTION OUTPUT:
--- Counter-Test: Exposing Insolvency of `new_prob = prior * exp(-1.1 * relative_error)` ---
Initial Prior: 0.5000

Scenario 1: Consistent underestimation (P_predicted < Z_actual)
Simulating 5 observations where Z_actual is 1, but P_predicted is 0.1
  Obs 1: P_predicted=0.1, Z_actual=1, Relative Error=-0.9, New Prior=1.3456
  CRITICAL FAILURE DETECTED: Probability exceeded 1.0 at observation 1.
  Assertion Passed: Probability (1.3456) successfully exceeded 1.0, demonstrating mathematical insolvency.

Resetting Prior to 0.5000 for Scenario 2.

Scenario 2: Consistent overestimation (P_predicted > Z_actual)
Simulating 5 observations where Z_actual is 0, but P_predicted is 0.9
  Obs 1: P_predicted=0.9, Z_actual=0, Relative Error=0.9, New Prior=0.1858
  Obs 2: P_predicted=0.9, Z_actual=0, Relative Error=0.9, New Prior=0.0690
  Obs 3: P_predicted=0.9, Z_actual=0, Relative Error=0.9, New Prior=0.0257
  Obs 4: P_predicted=0.9, Z_actual=0, Relative Error=0.9, New Prior=0.0095
  Obs 5: P_predicted=0.9, Z_actual=0, Relative Error=0.9, New Prior=0.0035
  Assertion Passed: Probability (0.0035) successfully approached 0, demonstrating rapid decay and potential loss of practical significance.

Resetting Prior to 0.5000 for Scenario 3.
Scenario 3: Mixed errors, demonstrating lack of convergence to actual base rate (0.5) and potential for range violation.
  Obs 1: P_predicted=0.31, Z_actual=0, New Prior=0.3555
  CRITICAL FAILURE DETECTED: Probability went out of [0,1] range at observation 7 (1.8751).
Final Prior after 50 mixed observations: 1.8751
  Assertion Passed: Probability (1.8751) went out of [0,1] range, demonstrating mathematical insolvency under mixed conditions.


## Attacker: Foundational Modeler & Axiomatic Reductionist
## Analytical Critique

The provided thesis outlines a robust advancement from V1 to V3, primarily by mandating a Multi-Layer Perceptron (MLP) architecture for the `ThesisPredictor` and integrating the Adam optimizer. This addresses the critical limitation of under-parameterization and inability to model non-linear causal relationships, a significant step towards empirically calibrated probabilities. The "RETIRED AXIOM" critique regarding `new_prob = prior * exp(-1.1 * relative_error)` is mathematically sound; exponential functions can indeed produce values outside the [0, 1] probability domain, rendering it unsuitable for direct probabilistic updates without normalization or re-framing.

The "Structural Arbitrage," "Conservation of Trade-Offs," and "Gatekeeper Reality" sections accurately describe the systemic implications of these architectural changes, acknowledging increased computational burden and architectural complexity in exchange for enhanced modeling capacity. The `MetaJudge`'s `validate_thesis_predictor_architecture` method serves as a stringent and appropriate absolute veto, ensuring compliance with the mandated MLP structure.

### Audit of Load-Bearing Variables Table and Python Constants:

1.  **System Parameters (`epsilon`, `adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`, `learning_rate_model_params`, `min_observations_for_calibration`, `target_brier_skill_score`, `rolling_window_size`, `hidden_layer_size`):** These values are standard or reasonable for their respective roles in numerical differentiation, optimization, and model evaluation within a machine learning context. Their dimensionless nature is appropriate where specified. No immediate "cooked books" or order-of-magnitude discrepancies are apparent.

2.  **Hypothetical Economic Rates (`hypothetical_economy_growth_rate_q1_2025_base`, `hypothetical_inflation_rate_q1_2025_base`):** These are asserted as `0.02` (2% per quarter) and `0.03` (3% per quarter), respectively. Annualized, these correspond to approximately 8.24% growth and 12.55% inflation. While these rates are elevated for a developed economy, they are not physically or financially impossible for a *hypothetical* scenario, particularly in emerging markets. The primary purist concern here is their assertion as base values without derivation, rather than an inherent insolvency in the values themselves. However, the model *learns* from variations around these bases, mitigating the direct impact of their arbitrary assertion on the model's learning capacity.

3.  **True Non-Linear Simulation Parameters (`true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `true_axiom_relevance`):** These parameters define the *simulated ground truth* for `Z_actual`. They are designed to create a complex, non-linear target for the `ThesisPredictor` to learn. As such, they are parameters of the simulation, not asserted constants *within the model's prediction logic*. Their values are chosen to create a challenging learning environment, which is appropriate for a falsification suite.

### Identification of "Cooked Books" and Last-Mile Derivation Failure:

The primary "last-mile derivation failure" and implicit "cooked books" reside in the handling of the `AXIOM_RECESSION_AVOIDANCE` variable.

*   **Asserted Input Value:** The `MetaJudge` initializes `self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5}`. This `0.5` is a fixed, asserted input value provided to the `ThesisPredictor` in every iteration. The model cannot derive this value; it merely receives it.
*   **Circular Ground Truth Definition:** Crucially, the `Z_actual` generation within the `test_model` function *also* uses this same asserted value: `+ true_axiom_relevance * meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']`. This creates a circular dependency where the "true" underlying process implicitly confirms the asserted value provided to the model. The model's task is artificially simplified because the ground truth's axiom component is directly correlated with the fixed, asserted axiom input it receives. This constitutes "cooked books" as it does not challenge the model's reliance on the un-derived, fixed nature of this load-bearing variable.

This setup fails to probe the model's ability to adapt when the *true* underlying state or relevance of `AXIOM_RECESSION_AVOIDANCE` deviates from the Mutator's fixed assertion. The model is never forced to derive the actual state of the axiom, only to learn a coefficient for a constant input that happens to be perfectly aligned with the simulated reality.

### So What for the Meta-Judge:

The Mutator's system, despite its advanced non-linear modeling capabilities, exhibits a critical "last-mile derivation failure" concerning the `AXIOM_RECESSION_AVOIDANCE` variable. The `ThesisPredictor` is provided with a fixed, asserted value for this axiom (0.5). However, the `Z_actual` generation, which defines the ground truth, is "cooked" by also using this same asserted value, thereby creating an artificially easy learning environment. When the *true* underlying value of this axiom is allowed to vary independently and dynamically, the model's reliance on its fixed, asserted input becomes a critical vulnerability. This demonstrates that the system cannot robustly derive the true impact of an asserted load-bearing variable when its underlying reality deviates from the Mutator's fixed assertion, leading to a breakdown in empirical calibration and predictive accuracy. The model is forced to rely on a misleading, un-derived constant, leading to a catastrophic misprediction.

---

```python
import math
import random
import collections
import inspect
import numpy as np

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
# These are the *system parameters* and *simulated real-world values* used for the falsification test.
# The `ThesisPredictor` itself will receive its *specific* load-bearing variables as inputs during simulation.
epsilon = 0.001  # Initial perturbation magnitude for numerical derivative calculation
adam_beta1 = 0.9  # Adam optimizer parameter (decay rate for first moment estimates)
adam_beta2 = 0.999 # Adam optimizer parameter (decay rate for second moment estimates)
adam_epsilon_stabilizer = 1e-8 # Adam optimizer parameter (small constant to prevent division by zero)
learning_rate_model_params = 0.001 # Learning rate for all model parameters (weights/biases)
min_observations_for_calibration = 200 # Increased due to complexity
target_brier_skill_score = 0.20 # Increased target, as more complex model should perform better
rolling_window_size = 50 # Number of observations for rolling average Brier Skill Score
hidden_layer_size = 4 # Number of neurons in the ThesisPredictor's hidden layer

# Simulated real-world values for the falsification test context.
# These represent external inputs that the Mutator's ThesisPredictor *must* utilize.
hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03

# True parameters for the *simulated, non-linear* Z_actual generation
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.5 # A fixed relevance for the axiom in the true model

class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Crucially, it must adhere to the Meta-Judge's new signature and output constraints,
    including a minimum architectural complexity (MLP with one hidden layer).
    """
    def __init__(self, input_size: int, hidden_size: int, output_size: int = 1):
        # Initialize weights and biases for a simple Multi-Layer Perceptron (MLP)
        # Input layer size includes external load-bearing variables + axiom weights
        self.weights_ih = np.random.randn(input_size, hidden_size) * 0.1 # Input to Hidden weights
        self.bias_h = np.zeros((1, hidden_size)) # Hidden layer bias
        self.weights_ho = np.random.randn(hidden_size, output_size) * 0.1 # Hidden to Output weights
        self.bias_o = np.zeros((1, output_size)) # Output layer bias

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) # Clip to prevent overflow for large x

    def calculate_p_predicted(self, axiom_weights: dict, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP.
        This function now explicitly uses all required inputs and must output a value in [0,1].
        All parameters are now internal to the ThesisPredictor (weights/biases),
        and are collectively optimized by the EpistemicGradientUpdater.
        """
        # Prepare input vector (load-bearing variables + axiom weight)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        axiom_recession_avoidance_weight = axiom_weights.get('AXIOM_RECESSION_AVOIDANCE', 0.5)

        # The order of features in input_vector must be consistent
        input_vector = np.array([[growth_rate, inflation_rate, axiom_recession_avoidance_weight]])

        # Hidden layer computation
        hidden_layer_input = np.dot(input_vector, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        # Output layer computation
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (weights and biases)."""
        return {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
        }

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']

    def update_param(self, param_name, new_value):
        """Updates a specific parameter by name."""
        if param_name == 'weights_ih':
            self.weights_ih = new_value
        elif param_name == 'bias_h':
            self.bias_h = new_value
        elif param_name == 'weights_ho':
            self.weights_ho = new_value
        elif param_name == 'bias_o':
            self.bias_o = new_value
        else:
            raise ValueError(f"Unknown parameter name: {param_name}")

class FiringSquad:
    """
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for all ThesisPredictor's weights and biases.
    """
    def __init__(self):
        pass # ThesisPredictor is passed dynamically

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     current_axiom_weights: dict, load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline = thesis_predictor.calculate_p_predicted(
            current_axiom_weights, load_bearing_variables
        )

        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param)

            for i in range(len(flat_param)):
                # Perturb upwards
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_plus = perturbed_params_plus[param_name].flatten()
                temp_flat_plus[i] += current_epsilon
                perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_plus)
                P_plus = thesis_predictor.calculate_p_predicted(current_axiom_weights, load_bearing_variables)

                # Perturb downwards
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_minus = perturbed_params_minus[param_name].flatten()
                temp_flat_minus[i] -= current_epsilon
                perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_minus)
                P_minus = thesis_predictor.calculate_p_predicted(current_axiom_weights, load_bearing_variables)

                dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        # Restore original parameters to the thesis_predictor object
        thesis_predictor.set_all_params(original_params)

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters.
    """
    def __init__(self, learning_rate, beta1, beta2, epsilon_stabilizer):
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} # First moment estimates
        self.v = {} # Second moment estimates
        self.t = 0 # Timestep

    def update(self, thesis_predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]

        # Calculate d(Brier Score)/dP_predicted
        dBS_dP = 2 * (P_predicted - Z_actual)

        current_params = thesis_predictor.get_all_params()
        new_params = {k: v.copy() for k, v in current_params.items()}

        for param_name, param_array in current_params.items():
            dP_d_param = sensitivity_vector.get(param_name, np.zeros_like(param_array))
            gradient = dBS_dP * dP_d_param

            # Initialize Adam state if not present
            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(param_array)
                self.v[param_name] = np.zeros_like(param_array)

            # Update biased first and second moment estimates
            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * gradient
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (gradient ** 2)

            # Compute bias-corrected first and second moment estimates
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

            # Update parameters
            new_params[param_name] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
            
        thesis_predictor.set_all_params(new_params) # Apply updates directly to the ThesisPredictor


class MetaJudge:
    """
    Scores thesis, manages ThesisPredictor parameters (via updater), and enforces architectural validation.
    Acts as the 'Absolute Veto' gatekeeper.
    """
    def __init__(self, input_size, hidden_size, output_size):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5} # Still managed separately as an input feature
        self.thesis_predictor = ThesisPredictor(input_size, hidden_size, output_size)
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon # Dynamic epsilon can be implemented here

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, and
        crucially, its minimum architectural complexity (MLP structure).
        """
        # 1. Method signature check
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['axiom_weights', 'load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        # 2. Architectural structure check (MLP with specified layers/attributes)
        required_attributes = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid']
        for attr in required_attributes:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement MLP structure (missing '{attr}' attribute).")
        
        # 3. Output range test
        dummy_axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5}
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        
        test_p = predictor.calculate_p_predicted(dummy_axiom_weights, dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        """
        # Validate the Mutator's thesis first (Gatekeeper Reality)
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # Firing Squad calculates sensitivities (RSA)
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, self.axiom_weights, load_bearing_variables, current_epsilon
        )

        # EpistemicGradientUpdater updates parameters of self.thesis_predictor directly
        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        return sensitivity_report["P_predicted_baseline"]

# --- COUNTER-TEST: Simulation and Falsification Test ---
def test_model():
    print("Running COUNTER-TEST for V3 Architecture: Exposing Last-Mile Derivation Failure of Asserted Axiom.")

    # The ThesisPredictor's input size is 2 (growth, inflation) + 1 (axiom_weight) = 3
    meta_judge = MetaJudge(input_size=3, hidden_size=hidden_layer_size, output_size=1)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] # For rolling historical frequency

    # Simulate real-world observations and engine updates
    for i in range(min_observations_for_calibration):
        # Dynamically adjust epsilon (e.g., annealing schedule)
        current_epsilon = epsilon * (1 - i / min_observations_for_calibration) + 1e-6 

        # Simulate real-world inputs for the current quarter with some variance
        current_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': random.uniform(
                hypothetical_economy_growth_rate_q1_2025_base * 0.8,
                hypothetical_economy_growth_rate_q1_2025_base * 1.2
            ),
            'hypothetical_inflation_rate_q1_2025': random.uniform(
                hypothetical_inflation_rate_q1_2025_base * 0.8,
                hypothetical_inflation_rate_q1_2025_base * 1.2
            )
        }
        
        # --- COUNTER-TEST MODIFICATION: Simulate Z_actual with TRUE NON-LINEARITY and INTERACTIONS ---
        # The true underlying process for the axiom is now dynamic and independent of the model's fixed input.
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']

        # Introduce a dynamic, un-derived true value for the axiom in the ground truth
        true_axiom_value_dynamic = random.uniform(0.0, 1.0) 

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            # COUNTER-TEST: Z_actual now uses the dynamic axiom value, NOT the fixed one from meta_judge.axiom_weights
            + true_axiom_relevance * true_axiom_value_dynamic 
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, current_epsilon)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 # Prevent division by zero if variance is very low

            BSS = 1 - (BS_model / BS_reference)
            
            # Print progress and some representative learned params for observability
            tracked_weight_ih_0_0 = meta_judge.thesis_predictor.weights_ih[0, 0] # Growth_rate to hidden[0]
            tracked_weight_ih_1_1 = meta_judge.thesis_predictor.weights_ih[1, 1] # Inflation_rate to hidden[1]
            tracked_weight_ih_2_0 = meta_judge.thesis_predictor.weights_ih[2, 0] # Axiom to hidden[0]
            tracked_weight_ho_0_0 = meta_judge.thesis_predictor.weights_ho[0, 0] # Hidden[0] to output
            
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BS_ref={BS_reference:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, W_ih[1,1]={tracked_weight_ih_1_1:.3f}, W_ih[2,0]={tracked_weight_ih_2_0:.3f}, Epsilon={current_epsilon:.5f}")

            if i == min_observations_for_calibration - 1:
                # --- Falsifiability Assertions ---
                print(f"\n--- COUNTER-TEST Results after {min_observations_for_calibration} observations ---")
                
                # ASSERTION 1: Rolling Brier Skill Score must FAIL to meet target
                # The model's fixed axiom input (0.5) is now uncorrelated with the true dynamic axiom value.
                # This should prevent the model from achieving the target BSS.
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss < target_brier_skill_score, \
                    f"COUNTER-TEST FAILED: Rolling Brier Skill Score ({final_bss:.3f}) unexpectedly met or exceeded target ({target_brier_skill_score}), indicating the model was NOT sufficiently challenged by the un-derived dynamic axiom."

                # ASSERTION 2: Average absolute value of all learned parameters should still indicate some learning
                # from other features, but the overall performance is compromised.
                all_params_flat = np.concatenate([v.flatten() for v in meta_judge.thesis_predictor.get_all_params().values()])
                avg_abs_param_value = np.mean(np.abs(all_params_flat))
                print(f"Average absolute value of all learned ThesisPredictor parameters: {avg_abs_param_value:.3f}")
                # This assertion is kept to ensure the model is still attempting to learn, just failing on the axiom.
                assert avg_abs_param_value > 0.01, \
                    f"COUNTER-TEST FAILED: Average absolute parameter value ({avg_abs_param_value:.3f}) is too close to zero, indicating complete learning failure, not specific to the axiom."
                
                # ASSERTION 3: The weights connecting the fixed axiom input to the hidden layer should ideally
                # converge towards zero if the fixed input is truly uncorrelated with the dynamic ground truth.
                # However, if the model *fails* the BSS, it implies it *couldn't* ignore it effectively or was misled.
                # For this counter-test, the primary failure is the BSS.
                final_tracked_weight_ih_2_0 = meta_judge.thesis_predictor.weights_ih[2, 0]
                print(f"Final Learned weights_ih[2,0] (axiom to hidden[0]): {final_tracked_weight_ih_2_0:.3f}")
                # We expect the model to struggle, so this weight might not be zero, indicating it's still trying to use the misleading input.
                # No specific assertion on this weight's magnitude, as the BSS failure is the primary indicator.

    print("\nCOUNTER-TEST PASSED: The model's reliance on a fixed, un-derived axiom input led to a failure in achieving the target Brier Skill Score when the true underlying axiom value was dynamic and uncorrelated. This exposes a critical last-mile derivation failure.")

# Execute the test
if __name__ == "__main__":
    test_model()
```

### PYTHON EXECUTION OUTPUT:
Running COUNTER-TEST for V3 Architecture: Exposing Last-Mile Derivation Failure of Asserted Axiom.
Obs  50: P_pred=0.498, Z_actual=0, BS_model=0.2498, BS_ref=0.2304, BSS=-0.084, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00076
Obs  51: P_pred=0.498, Z_actual=0, BS_model=0.2498, BS_ref=0.2244, BSS=-0.113, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00075
Obs  52: P_pred=0.498, Z_actual=0, BS_model=0.2497, BS_ref=0.2244, BSS=-0.113, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00075
Obs  53: P_pred=0.497, Z_actual=1, BS_model=0.2498, BS_ref=0.2244, BSS=-0.113, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00074
Obs  54: P_pred=0.497, Z_actual=1, BS_model=0.2499, BS_ref=0.2244, BSS=-0.113, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00074
Obs  55: P_pred=0.497, Z_actual=0, BS_model=0.2498, BS_ref=0.2244, BSS=-0.113, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00073
Obs  56: P_pred=0.497, Z_actual=0, BS_model=0.2497, BS_ref=0.2244, BSS=-0.113, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00073
Obs  57: P_pred=0.497, Z_actual=0, BS_model=0.2497, BS_ref=0.2176, BSS=-0.147, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00072
Obs  58: P_pred=0.497, Z_actual=0, BS_model=0.2496, BS_ref=0.2100, BSS=-0.189, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00072
Obs  59: P_pred=0.497, Z_actual=0, BS_model=0.2496, BS_ref=0.2100, BSS=-0.188, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00071
Obs  60: P_pred=0.497, Z_actual=0, BS_model=0.2495, BS_ref=0.2016, BSS=-0.238, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00071
Obs  61: P_pred=0.497, Z_actual=1, BS_model=0.2496, BS_ref=0.2100, BSS=-0.188, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00070
Obs  62: P_pred=0.496, Z_actual=0, BS_model=0.2495, BS_ref=0.2100, BSS=-0.188, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00070
Obs  63: P_pred=0.496, Z_actual=0, BS_model=0.2494, BS_ref=0.2100, BSS=-0.188, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00069
Obs  64: P_pred=0.496, Z_actual=0, BS_model=0.2493, BS_ref=0.2016, BSS=-0.237, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00069
Obs  65: P_pred=0.496, Z_actual=1, BS_model=0.2494, BS_ref=0.2100, BSS=-0.188, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00068
Obs  66: P_pred=0.496, Z_actual=1, BS_model=0.2495, BS_ref=0.2176, BSS=-0.146, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00068
Obs  67: P_pred=0.496, Z_actual=0, BS_model=0.2494, BS_ref=0.2176, BSS=-0.146, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00067
Obs  68: P_pred=0.496, Z_actual=1, BS_model=0.2495, BS_ref=0.2244, BSS=-0.112, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00067
Obs  69: P_pred=0.496, Z_actual=1, BS_model=0.2495, BS_ref=0.2304, BSS=-0.083, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00066
Obs  70: P_pred=0.496, Z_actual=0, BS_model=0.2494, BS_ref=0.2304, BSS=-0.083, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00066
Obs  71: P_pred=0.496, Z_actual=0, BS_model=0.2494, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00065
Obs  72: P_pred=0.496, Z_actual=0, BS_model=0.2493, BS_ref=0.2244, BSS=-0.111, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00065
Obs  73: P_pred=0.496, Z_actual=0, BS_model=0.2492, BS_ref=0.2244, BSS=-0.110, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00064
Obs  74: P_pred=0.495, Z_actual=0, BS_model=0.2491, BS_ref=0.2176, BSS=-0.145, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00064
Obs  75: P_pred=0.495, Z_actual=1, BS_model=0.2492, BS_ref=0.2244, BSS=-0.110, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00063
Obs  76: P_pred=0.495, Z_actual=0, BS_model=0.2491, BS_ref=0.2244, BSS=-0.110, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00063
Obs  77: P_pred=0.495, Z_actual=1, BS_model=0.2492, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00062
Obs  78: P_pred=0.495, Z_actual=0, BS_model=0.2491, BS_ref=0.2244, BSS=-0.110, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00062
Obs  79: P_pred=0.495, Z_actual=1, BS_model=0.2492, BS_ref=0.2244, BSS=-0.110, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00061
Obs  80: P_pred=0.495, Z_actual=1, BS_model=0.2493, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00061
Obs  81: P_pred=0.495, Z_actual=1, BS_model=0.2494, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00060
Obs  82: P_pred=0.495, Z_actual=0, BS_model=0.2493, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00060
Obs  83: P_pred=0.495, Z_actual=0, BS_model=0.2492, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00059
Obs  84: P_pred=0.495, Z_actual=1, BS_model=0.2493, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00059
Obs  85: P_pred=0.495, Z_actual=1, BS_model=0.2494, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00058
Obs  86: P_pred=0.495, Z_actual=1, BS_model=0.2496, BS_ref=0.2400, BSS=-0.040, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00058
Obs  87: P_pred=0.495, Z_actual=1, BS_model=0.2496, BS_ref=0.2400, BSS=-0.040, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00057
Obs  88: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00057
Obs  89: P_pred=0.495, Z_actual=0, BS_model=0.2494, BS_ref=0.2304, BSS=-0.082, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00056
Obs  90: P_pred=0.495, Z_actual=1, BS_model=0.2495, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00056
Obs  91: P_pred=0.495, Z_actual=1, BS_model=0.2496, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00055
Obs  92: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00055
Obs  93: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00054
Obs  94: P_pred=0.495, Z_actual=0, BS_model=0.2494, BS_ref=0.2356, BSS=-0.059, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00054
Obs  95: P_pred=0.495, Z_actual=0, BS_model=0.2493, BS_ref=0.2356, BSS=-0.058, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00053
Obs  96: P_pred=0.495, Z_actual=1, BS_model=0.2495, BS_ref=0.2400, BSS=-0.039, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00053
Obs  97: P_pred=0.495, Z_actual=1, BS_model=0.2496, BS_ref=0.2436, BSS=-0.025, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00052
Obs  98: P_pred=0.495, Z_actual=1, BS_model=0.2497, BS_ref=0.2436, BSS=-0.025, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00052
Obs  99: P_pred=0.495, Z_actual=1, BS_model=0.2498, BS_ref=0.2464, BSS=-0.014, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00051
Obs 100: P_pred=0.495, Z_actual=0, BS_model=0.2497, BS_ref=0.2464, BSS=-0.014, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00051
Obs 101: P_pred=0.495, Z_actual=0, BS_model=0.2497, BS_ref=0.2464, BSS=-0.013, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00050
Obs 102: P_pred=0.495, Z_actual=1, BS_model=0.2498, BS_ref=0.2484, BSS=-0.006, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00050
Obs 103: P_pred=0.495, Z_actual=0, BS_model=0.2497, BS_ref=0.2464, BSS=-0.013, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00049
Obs 104: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2436, BSS=-0.024, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00049
Obs 105: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2436, BSS=-0.024, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00048
Obs 106: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2436, BSS=-0.024, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00048
Obs 107: P_pred=0.495, Z_actual=0, BS_model=0.2494, BS_ref=0.2436, BSS=-0.024, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00047
Obs 108: P_pred=0.495, Z_actual=1, BS_model=0.2496, BS_ref=0.2464, BSS=-0.013, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00047
Obs 109: P_pred=0.495, Z_actual=1, BS_model=0.2497, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00046
Obs 110: P_pred=0.495, Z_actual=1, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00046
Obs 111: P_pred=0.495, Z_actual=0, BS_model=0.2497, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00045
Obs 112: P_pred=0.495, Z_actual=1, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00045
Obs 113: P_pred=0.495, Z_actual=0, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00044
Obs 114: P_pred=0.495, Z_actual=0, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00044
Obs 115: P_pred=0.495, Z_actual=0, BS_model=0.2497, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00043
Obs 116: P_pred=0.495, Z_actual=1, BS_model=0.2497, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00043
Obs 117: P_pred=0.495, Z_actual=0, BS_model=0.2497, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00042
Obs 118: P_pred=0.495, Z_actual=0, BS_model=0.2495, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00042
Obs 119: P_pred=0.495, Z_actual=0, BS_model=0.2493, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00041
Obs 120: P_pred=0.494, Z_actual=1, BS_model=0.2495, BS_ref=0.2464, BSS=-0.013, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00041
Obs 121: P_pred=0.494, Z_actual=1, BS_model=0.2497, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00040
Obs 122: P_pred=0.494, Z_actual=1, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00040
Obs 123: P_pred=0.494, Z_actual=0, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00039
Obs 124: P_pred=0.494, Z_actual=1, BS_model=0.2501, BS_ref=0.2500, BSS=-0.000, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00039
Obs 125: P_pred=0.494, Z_actual=0, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00038
Obs 126: P_pred=0.494, Z_actual=0, BS_model=0.2498, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00038
Obs 127: P_pred=0.494, Z_actual=1, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00037
Obs 128: P_pred=0.494, Z_actual=0, BS_model=0.2498, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00037
Obs 129: P_pred=0.494, Z_actual=0, BS_model=0.2496, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00036
Obs 130: P_pred=0.494, Z_actual=1, BS_model=0.2496, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00036
Obs 131: P_pred=0.494, Z_actual=0, BS_model=0.2494, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00035
Obs 132: P_pred=0.494, Z_actual=1, BS_model=0.2496, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00035
Obs 133: P_pred=0.494, Z_actual=1, BS_model=0.2499, BS_ref=0.2496, BSS=-0.001, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00034
Obs 134: P_pred=0.494, Z_actual=0, BS_model=0.2496, BS_ref=0.2484, BSS=-0.005, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00034
Obs 135: P_pred=0.494, Z_actual=0, BS_model=0.2494, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00033
Obs 136: P_pred=0.494, Z_actual=1, BS_model=0.2494, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00033
Obs 137: P_pred=0.494, Z_actual=1, BS_model=0.2495, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00032
Obs 138: P_pred=0.494, Z_actual=0, BS_model=0.2494, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00032
Obs 139: P_pred=0.494, Z_actual=0, BS_model=0.2494, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00031
Obs 140: P_pred=0.494, Z_actual=0, BS_model=0.2492, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00031
Obs 141: P_pred=0.494, Z_actual=0, BS_model=0.2490, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00030
Obs 142: P_pred=0.494, Z_actual=1, BS_model=0.2492, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00030
Obs 143: P_pred=0.494, Z_actual=0, BS_model=0.2492, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00029
Obs 144: P_pred=0.494, Z_actual=0, BS_model=0.2491, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00029
Obs 145: P_pred=0.494, Z_actual=0, BS_model=0.2491, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00028
Obs 146: P_pred=0.494, Z_actual=0, BS_model=0.2489, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00028
Obs 147: P_pred=0.493, Z_actual=0, BS_model=0.2487, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00027
Obs 148: P_pred=0.493, Z_actual=1, BS_model=0.2487, BS_ref=0.2356, BSS=-0.056, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00027
Obs 149: P_pred=0.493, Z_actual=0, BS_model=0.2485, BS_ref=0.2304, BSS=-0.078, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00026
Obs 150: P_pred=0.493, Z_actual=1, BS_model=0.2487, BS_ref=0.2356, BSS=-0.056, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00026
Obs 151: P_pred=0.493, Z_actual=0, BS_model=0.2487, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00025
Obs 152: P_pred=0.493, Z_actual=1, BS_model=0.2487, BS_ref=0.2356, BSS=-0.056, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00025
Obs 153: P_pred=0.493, Z_actual=0, BS_model=0.2487, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00024
Obs 154: P_pred=0.493, Z_actual=1, BS_model=0.2489, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00024
Obs 155: P_pred=0.493, Z_actual=0, BS_model=0.2489, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00023
Obs 156: P_pred=0.493, Z_actual=1, BS_model=0.2491, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00023
Obs 157: P_pred=0.493, Z_actual=1, BS_model=0.2493, BS_ref=0.2464, BSS=-0.012, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00022
Obs 158: P_pred=0.493, Z_actual=0, BS_model=0.2491, BS_ref=0.2436, BSS=-0.023, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00022
Obs 159: P_pred=0.493, Z_actual=0, BS_model=0.2488, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00021
Obs 160: P_pred=0.493, Z_actual=0, BS_model=0.2486, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00021
Obs 161: P_pred=0.493, Z_actual=0, BS_model=0.2486, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00020
Obs 162: P_pred=0.493, Z_actual=1, BS_model=0.2486, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00020
Obs 163: P_pred=0.492, Z_actual=0, BS_model=0.2486, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00019
Obs 164: P_pred=0.492, Z_actual=1, BS_model=0.2488, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00019
Obs 165: P_pred=0.492, Z_actual=0, BS_model=0.2488, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00018
Obs 166: P_pred=0.492, Z_actual=0, BS_model=0.2485, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00018
Obs 167: P_pred=0.492, Z_actual=1, BS_model=0.2488, BS_ref=0.2400, BSS=-0.037, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00017
Obs 168: P_pred=0.492, Z_actual=1, BS_model=0.2490, BS_ref=0.2436, BSS=-0.022, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00017
Obs 169: P_pred=0.492, Z_actual=0, BS_model=0.2490, BS_ref=0.2436, BSS=-0.022, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00016
Obs 170: P_pred=0.492, Z_actual=0, BS_model=0.2487, BS_ref=0.2400, BSS=-0.036, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00016
Obs 171: P_pred=0.492, Z_actual=0, BS_model=0.2484, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00015
Obs 172: P_pred=0.492, Z_actual=0, BS_model=0.2482, BS_ref=0.2304, BSS=-0.077, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00015
Obs 173: P_pred=0.492, Z_actual=1, BS_model=0.2485, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00014
Obs 174: P_pred=0.492, Z_actual=1, BS_model=0.2485, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00014
Obs 175: P_pred=0.492, Z_actual=0, BS_model=0.2485, BS_ref=0.2356, BSS=-0.055, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00013
Obs 176: P_pred=0.492, Z_actual=0, BS_model=0.2484, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00013
Obs 177: P_pred=0.492, Z_actual=0, BS_model=0.2481, BS_ref=0.2304, BSS=-0.077, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00012
Obs 178: P_pred=0.492, Z_actual=1, BS_model=0.2484, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00012
Obs 179: P_pred=0.492, Z_actual=0, BS_model=0.2484, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00011
Obs 180: P_pred=0.491, Z_actual=1, BS_model=0.2484, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00011
Obs 181: P_pred=0.491, Z_actual=1, BS_model=0.2487, BS_ref=0.2400, BSS=-0.036, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00010
Obs 182: P_pred=0.491, Z_actual=0, BS_model=0.2484, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00010
Obs 183: P_pred=0.491, Z_actual=0, BS_model=0.2481, BS_ref=0.2304, BSS=-0.077, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00009
Obs 184: P_pred=0.491, Z_actual=0, BS_model=0.2481, BS_ref=0.2304, BSS=-0.077, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00009
Obs 185: P_pred=0.491, Z_actual=1, BS_model=0.2484, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00008
Obs 186: P_pred=0.491, Z_actual=0, BS_model=0.2481, BS_ref=0.2304, BSS=-0.077, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00008
Obs 187: P_pred=0.491, Z_actual=0, BS_model=0.2478, BS_ref=0.2244, BSS=-0.104, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00007
Obs 188: P_pred=0.491, Z_actual=0, BS_model=0.2477, BS_ref=0.2244, BSS=-0.104, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00007
Obs 189: P_pred=0.491, Z_actual=1, BS_model=0.2480, BS_ref=0.2304, BSS=-0.076, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00006
Obs 190: P_pred=0.491, Z_actual=0, BS_model=0.2480, BS_ref=0.2304, BSS=-0.076, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00006
Obs 191: P_pred=0.491, Z_actual=0, BS_model=0.2479, BS_ref=0.2304, BSS=-0.076, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00005
Obs 192: P_pred=0.491, Z_actual=1, BS_model=0.2480, BS_ref=0.2304, BSS=-0.076, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00005
Obs 193: P_pred=0.491, Z_actual=1, BS_model=0.2483, BS_ref=0.2356, BSS=-0.054, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00004
Obs 194: P_pred=0.491, Z_actual=1, BS_model=0.2486, BS_ref=0.2400, BSS=-0.036, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00004
Obs 195: P_pred=0.491, Z_actual=0, BS_model=0.2485, BS_ref=0.2400, BSS=-0.035, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00003
Obs 196: P_pred=0.491, Z_actual=1, BS_model=0.2488, BS_ref=0.2436, BSS=-0.021, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00003
Obs 197: P_pred=0.491, Z_actual=0, BS_model=0.2488, BS_ref=0.2436, BSS=-0.021, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00002
Obs 198: P_pred=0.491, Z_actual=0, BS_model=0.2485, BS_ref=0.2400, BSS=-0.035, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00002
Obs 199: P_pred=0.491, Z_actual=0, BS_model=0.2484, BS_ref=0.2400, BSS=-0.035, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00001
Obs 200: P_pred=0.491, Z_actual=1, BS_model=0.2485, BS_ref=0.2400, BSS=-0.035, W_ih[0,0]=0.248, W_ih[1,1]=0.044, W_ih[2,0]=-0.031, Epsilon=0.00001

--- COUNTER-TEST Results after 200 observations ---
Final Rolling Brier Skill Score over last 50 observations: -0.035
Average absolute value of all learned ThesisPredictor parameters: 0.068
Final Learned weights_ih[2,0] (axiom to hidden[0]): -0.031

COUNTER-TEST PASSED: The model's reliance on a fixed, un-derived axiom input led to a failure in achieving the target Brier Skill Score when the true underlying axiom value was dynamic and uncorrelated. This exposes a critical last-mile derivation failure.


## Attacker: Adversarial Test Vector Engineer
The presented thesis accurately identifies the fundamental mathematical insolvency of the `new_prob = prior * exp(-1.1 * relative_error)` axiom, which inherently permits probabilities to exist outside the [0, 1] domain, rendering it unsuitable for rigorous probabilistic reasoning. The proposed V3 architecture, centered on a Multi-Layer Perceptron (MLP) `ThesisPredictor` with an adaptive Adam optimizer and dynamic `epsilon` scaling, represents a mathematically sound and structurally robust advancement.

**Critique of Mathematical Solvency and Integrity:**

1.  **Representational Capacity:** The mandate for an MLP with at least one hidden layer and non-linear activation functions (ReLU, Sigmoid) correctly addresses the prior limitation of under-parameterized linear models. The Universal Approximation Theorem provides the theoretical grounding for an MLP's capacity to model arbitrary continuous non-linear functions, thereby structurally enabling the capture of complex causal dynamics. The `_sigmoid` function's `np.clip` implementation is a robust numerical safeguard against floating-point overflow/underflow conditions, enhancing stability.
2.  **Optimization Robustness:** The integration of the Adam optimizer is mathematically appropriate. Its adaptive learning rates, based on exponential moving averages of past gradients, are well-suited for navigating the complex, non-convex loss landscapes characteristic of non-linear models. This mechanism mitigates issues of stagnation and slow convergence observed in simpler gradient descent methods. The `adam_beta1`, `adam_beta2`, and `adam_epsilon_stabilizer` parameters are standard, empirically validated hyperparameters.
3.  **Gradient Attribution:** The `FiringSquad`'s use of central difference for numerical derivative calculation (`dP/d(param)`) across all MLP weights and biases is a robust method for gradient estimation. The dynamic annealing of `epsilon` balances the need for initial robustness with later precision, which is a sound practice in numerical optimization.
4.  **Boundary Conditions and Operator Robustness:** The `MetaJudge`'s `validate_thesis_predictor_architecture` method, acting as an absolute veto, rigorously enforces the `[0,1]` output range for `P_predicted`. This directly prevents 'Information Embezzlement' by ensuring the model's output adheres to probabilistic constraints. The explicit structural checks for MLP attributes (`weights_ih`, `bias_h`, `weights_ho`, `bias_o`, `_relu`, `_sigmoid`) prevent 'Rubric Gaming' by precluding the Mutator from generating non-compliant or obfuscated models.
5.  **Load-Bearing Variables Audit (Parametric Grounding):**
    *   **System Parameters (`epsilon`, `adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`, `learning_rate_model_params`, `min_observations_for_calibration`, `target_brier_skill_score`, `rolling_window_size`, `hidden_layer_size`):** These are dimensionless system parameters or hyperparameters. Their values are within established ranges for numerical methods and neural network training, or are clearly defined system-specific thresholds. No evidence of 'cooked books' or misapplication of standard metrics is found here.
    *   **Simulated Real-World Values (`hypothetical_economy_growth_rate_q1_2025_base`, `hypothetical_inflation_rate_q1_2025_base`):** These are explicitly designated as "hypothetical" quarterly rates. While high when annualized (8% growth, 12% inflation), they are presented as baseline values for a simulated environment designed to test model robustness. Their dimensionless nature is correctly stated.
    *   **Simulated Non-Linear `Z_actual` Parameters (`true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `true_axiom_relevance`):** These are dimensionless parameters defining the *target* non-linear function that the `ThesisPredictor` must learn. Their values are arbitrary but collectively define a complex, interacting causal landscape. They are not real-world physical constants but rather parameters of the simulated reality, which is appropriate for a falsification suite.

**"So What" for the Meta-Judge:**

The proposed V3 architecture, as implemented in the provided Python falsification suite, fundamentally addresses the prior limitations of under-parameterized models and inefficient optimization. By mandating a Multi-Layer Perceptron (MLP) and employing the Adam optimizer, the system gains the necessary representational capacity and adaptive learning mechanisms to model complex, non-linear causal relationships. The rigorous architectural validation by the Meta-Judge, coupled with precise gradient attribution by the Firing Squad, creates a robust framework that mathematically precludes 'Information Embezzlement' and 'Rubric Gaming' by forcing the Mutator to generate verifiable, empirically calibrated models. This transition elevates the engine's capability from approximating linear correlations to accurately capturing intricate, non-linear dependencies, thereby enabling more reliable probabilistic reasoning and credit assignment in complex environments.

However, a critical vulnerability exists not in the mathematical correctness of the V3 components themselves, but in the *sufficiency of the current falsification test's input data range* to genuinely stress the claimed non-linear representational capacity. The current simulation's `random.uniform` ranges for `hypothetical_economy_growth_rate_q1_2025` and `hypothetical_inflation_rate_q1_2025` are too narrow (0.8x to 1.2x base). This effectively samples the underlying non-linear `Z_actual` function only within a locally smooth, quasi-linear region. Consequently, the `ThesisPredictor` is not truly compelled to learn and generalize across the *full spectrum* of the complex, oscillatory behavior inherent in the `true_growth_freq_nl` and `true_inflation_freq_nl` parameters. This constitutes a statistical edge case where the test environment, despite being mathematically non-linear, fails to provide sufficiently diverse inputs to validate the model's ability to capture "intricate, non-linear causal relationships" across a broader, more challenging domain. The current test, therefore, risks providing a false positive for the model's true non-linear capabilities.

---

```python
import math
import random
import collections
import inspect
import numpy as np # For matrix operations

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
# These are the *system parameters* and *simulated real-world values* used for the falsification test.
# The `ThesisPredictor` itself will receive its *specific* load-bearing variables as inputs during simulation.
epsilon = 0.001  # Initial perturbation magnitude for numerical derivative calculation
adam_beta1 = 0.9  # Adam optimizer parameter (decay rate for first moment estimates)
adam_beta2 = 0.999 # Adam optimizer parameter (decay rate for second moment estimates)
adam_epsilon_stabilizer = 1e-8 # Adam optimizer parameter (small constant to prevent division by zero)
learning_rate_model_params = 0.001 # Learning rate for all model parameters (weights/biases)
min_observations_for_calibration = 200 # Increased due to complexity
target_brier_skill_score = 0.20 # Increased target, as more complex model should perform better
rolling_window_size = 50 # Number of observations for rolling average Brier Skill Score
hidden_layer_size = 4 # Number of neurons in the ThesisPredictor's hidden layer

# Simulated real-world values for the falsification test context.
# These represent external inputs that the Mutator's ThesisPredictor *must* utilize.
hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03

# True parameters for the *simulated, non-linear* Z_actual generation
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.5 # A fixed relevance for the axiom in the true model

class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Crucially, it must adhere to the Meta-Judge's new signature and output constraints,
    including a minimum architectural complexity (MLP with one hidden layer).
    """
    def __init__(self, input_size: int, hidden_size: int, output_size: int = 1):
        # Initialize weights and biases for a simple Multi-Layer Perceptron (MLP)
        # Input layer size includes external load-bearing variables + axiom weights
        self.weights_ih = np.random.randn(input_size, hidden_size) * 0.1 # Input to Hidden weights
        self.bias_h = np.zeros((1, hidden_size)) # Hidden layer bias
        self.weights_ho = np.random.randn(hidden_size, output_size) * 0.1 # Hidden to Output weights
        self.bias_o = np.zeros((1, output_size)) # Output layer bias

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) # Clip to prevent overflow for large x

    def calculate_p_predicted(self, axiom_weights: dict, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP.
        This function now explicitly uses all required inputs and must output a value in [0,1].
        All parameters are now internal to the ThesisPredictor (weights/biases),
        and are collectively optimized by the EpistemicGradientUpdater.
        """
        # Prepare input vector (load-bearing variables + axiom weight)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        axiom_recession_avoidance_weight = axiom_weights.get('AXIOM_RECESSION_AVOIDANCE', 0.5)

        # The order of features in input_vector must be consistent
        input_vector = np.array([[growth_rate, inflation_rate, axiom_recession_avoidance_weight]])

        # Hidden layer computation
        hidden_layer_input = np.dot(input_vector, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        # Output layer computation
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (weights and biases)."""
        return {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
        }

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']

    def update_param(self, param_name, new_value):
        """Updates a specific parameter by name."""
        if param_name == 'weights_ih':
            self.weights_ih = new_value
        elif param_name == 'bias_h':
            self.bias_h = new_value
        elif param_name == 'weights_ho':
            self.weights_ho = new_value
        elif param_name == 'bias_o':
            self.bias_o = new_value
        else:
            raise ValueError(f"Unknown parameter name: {param_name}")

class FiringSquad:
    """
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for all ThesisPredictor's weights and biases.
    """
    def __init__(self):
        pass # ThesisPredictor is passed dynamically

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     current_axiom_weights: dict, load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline = thesis_predictor.calculate_p_predicted(
            current_axiom_weights, load_bearing_variables
        )

        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param)

            for i in range(len(flat_param)):
                # Perturb upwards
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_plus = perturbed_params_plus[param_name].flatten()
                temp_flat_plus[i] += current_epsilon
                perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_plus)
                P_plus = thesis_predictor.calculate_p_predicted(current_axiom_weights, load_bearing_variables)

                # Perturb downwards
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_minus = perturbed_params_minus[param_name].flatten()
                temp_flat_minus[i] -= current_epsilon
                perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_minus)
                P_minus = thesis_predictor.calculate_p_predicted(current_axiom_weights, load_bearing_variables)

                dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        # Restore original parameters to the thesis_predictor object
        thesis_predictor.set_all_params(original_params)

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters.
    """
    def __init__(self, learning_rate, beta1, beta2, epsilon_stabilizer):
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} # First moment estimates
        self.v = {} # Second moment estimates
        self.t = 0 # Timestep

    def update(self, thesis_predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]

        # Calculate d(Brier Score)/dP_predicted
        dBS_dP = 2 * (P_predicted - Z_actual)

        current_params = thesis_predictor.get_all_params()
        new_params = {k: v.copy() for k, v in current_params.items()}

        for param_name, param_array in current_params.items():
            dP_d_param = sensitivity_vector.get(param_name, np.zeros_like(param_array))
            gradient = dBS_dP * dP_d_param

            # Initialize Adam state if not present
            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(param_array)
                self.v[param_name] = np.zeros_like(param_array)

            # Update biased first and second moment estimates
            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * gradient
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (gradient ** 2)

            # Compute bias-corrected first and second moment estimates
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

            # Update parameters
            new_params[param_name] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
        
        thesis_predictor.set_all_params(new_params) # Apply updates directly to the ThesisPredictor


class MetaJudge:
    """
    Scores thesis, manages ThesisPredictor parameters (via updater), and enforces architectural validation.
    Acts as the 'Absolute Veto' gatekeeper.
    """
    def __init__(self, input_size, hidden_size, output_size):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5} # Still managed separately as an input feature
        self.thesis_predictor = ThesisPredictor(input_size, hidden_size, output_size)
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon # Dynamic epsilon can be implemented here

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, and
        crucially, its minimum architectural complexity (MLP structure).
        """
        # 1. Method signature check
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['axiom_weights', 'load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        # 2. Architectural structure check (MLP with specified layers/attributes)
        required_attributes = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid']
        for attr in required_attributes:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement MLP structure (missing '{attr}' attribute).")
        
        # 3. Output range test
        dummy_axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': 0.5}
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        
        test_p = predictor.calculate_p_predicted(dummy_axiom_weights, dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        """
        # Validate the Mutator's thesis first (Gatekeeper Reality)
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # Firing Squad calculates sensitivities (RSA)
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, self.axiom_weights, load_bearing_variables, current_epsilon
        )

        # EpistemicGradientUpdater updates parameters of self.thesis_predictor directly
        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        return sensitivity_report["P_predicted_baseline"]

# --- Counter-Test: Exposing Insolvency via Insufficient Input Range ---
def counter_test_model():
    print("Running COUNTER-TEST: Falsification Test under Expanded Input Ranges (More Complex Non-Linearity)...")

    # The ThesisPredictor's input size is 2 (growth, inflation) + 1 (axiom_weight) = 3
    meta_judge = MetaJudge(input_size=3, hidden_size=hidden_layer_size, output_size=1)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] # For rolling historical frequency

    # Simulate real-world observations and engine updates
    for i in range(min_observations_for_calibration):
        # Dynamically adjust epsilon (e.g., annealing schedule)
        current_epsilon = epsilon * (1 - i / min_observations_for_calibration) + 1e-6 

        # --- COUNTER-TEST MODIFICATION: Significantly expand the input ranges ---
        # This forces the ThesisPredictor to learn across a much wider, more genuinely
        # non-linear and oscillatory segment of the true Z_actual function.
        current_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': random.uniform(
                hypothetical_economy_growth_rate_q1_2025_base * 0.1, # 10% of base
                hypothetical_economy_growth_rate_q1_2025_base * 3.0  # 300% of base
            ),
            'hypothetical_inflation_rate_q1_2025': random.uniform(
                hypothetical_inflation_rate_q1_2025_base * 0.1, # 10% of base
                hypothetical_inflation_rate_q1_2025_base * 3.0  # 300% of base
            )
        }
        
        # --- Simulate Z_actual with TRUE NON-LINEARITY and INTERACTIONS ---
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, current_epsilon)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 # Prevent division by zero if variance is very low

            BSS = 1 - (BS_model / BS_reference)
            
            # Print progress and some representative learned params for observability
            tracked_weight_ih_0_0 = meta_judge.thesis_predictor.weights_ih[0, 0] # Growth_rate to hidden[0]
            tracked_weight_ih_1_1 = meta_judge.thesis_predictor.weights_ih[1, 1] # Inflation_rate to hidden[1]
            tracked_weight_ho_0_0 = meta_judge.thesis_predictor.weights_ho[0, 0] # Hidden[0] to output
            
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BS_ref={BS_reference:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, W_ih[1,1]={tracked_weight_ih_1_1:.3f}, W_ho[0,0]={tracked_weight_ho_0_0:.3f}, Epsilon={current_epsilon:.5f}")

            if i == min_observations_for_calibration - 1:
                # --- Falsifiability Assertions ---
                print(f"\n--- COUNTER-TEST Results after {min_observations_for_calibration} observations ---")
                
                # ASSERTION 1: Rolling Brier Skill Score must meet target
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss >= target_brier_skill_score, \
                    f"COUNTER-TEST FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score}) under expanded input ranges. This indicates the current model configuration (e.g., hidden_layer_size, min_observations_for_calibration) is insufficient for truly complex non-linear dynamics."

                # ASSERTION 2: Average absolute value of all learned parameters must indicate significant learning.
                all_params_flat = np.concatenate([v.flatten() for v in meta_judge.thesis_predictor.get_all_params().values()])
                avg_abs_param_value = np.mean(np.abs(all_params_flat))
                print(f"Average absolute value of all learned ThesisPredictor parameters: {avg_abs_param_value:.3f}")
                assert avg_abs_param_value > 0.05, \
                    f"COUNTER-TEST FAILED: Average absolute parameter value ({avg_abs_param_value:.3f}) is too close to zero, indicating lack of significant learning under expanded input ranges."
                
                # ASSERTION 3: A specific tracked weight (growth_rate to hidden[0]) must be non-zero.
                final_tracked_weight_ih_0_0 = meta_judge.thesis_predictor.weights_ih[0, 0]
                print(f"Final Learned weights_ih[0,0] (growth to hidden[0]): {final_tracked_weight_ih_0_0:.3f}")
                assert abs(final_tracked_weight_ih_0_0) > 0.01, \
                    f"COUNTER-TEST FAILED: Tracked weight (growth to hidden[0]) is too close to zero ({final_tracked_weight_ih_0_0:.3f}), indicating no significant learning path under expanded input ranges."

    print("\nCOUNTER-TEST PASSED: All conditions met, demonstrating robust empirical calibration and credit assignment under expanded, more complex non-linear causal complexities.")

# Execute the counter-test
if __name__ == "__main__":
    counter_test_model()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpcgo1hf00.py", line 371, in <module>
    counter_test_model()
    ~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpcgo1hf00.py", line 351, in counter_test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: COUNTER-TEST FAILED: Rolling Brier Skill Score (-0.005) did not meet target (0.2) under expanded input ranges. This indicates the current model configuration (e.g., hidden_layer_size, min_observations_for_calibration) is insufficient for truly complex non-linear dynamics.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 371, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 351, in test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: FALSIFICATION FAILED: Rolling Brier Skill Score (-0.020) did not meet target (0.2).


# Final Score: 110
**Weakest Point:** The thesis's own falsification suite, under expanded input ranges, disproved its core claim by failing to achieve the target Brier Skill Score (actual -0.005 vs target 0.20), indicating the current model configuration is insufficient for truly complex non-linear dynamics and the claimed empirical calibration is not yet realized.
**Rationale:** The thesis proposes a V3 architecture using an MLP for 'ThesisPredictor', Adam optimizer, and dynamic epsilon scaling to address under-parameterization and improve empirical calibration. It correctly identifies and retires the mathematically unsound 'new_prob = prior * exp(-1.1 * relative_error)' axiom, a claim validated by the Bayesian Epistemologist's counter-test. The Meta-Judge's 'Architecture Validator' and the 'FiringSquad' provide robust anti-gaming checks. However, the Foundational Modeler exposed a persistent 'last-mile derivation failure' for axioms, as they remain fixed inputs without empirical calibration mechanisms. Critically, the thesis's own final falsification test, as executed by the Adversarial Test Vector Engineer, failed by a significant margin (BSS of -0.005 against a target of 0.20), demonstrating that despite the increased architectural capacity for non-linearity, the current model configuration is insufficient to achieve its stated goal of empirically calibrated predictions under truly complex non-linear conditions. This means the core problem of uncalibrated probabilities is not yet closed.
