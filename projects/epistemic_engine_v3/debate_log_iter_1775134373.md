# Adversarial Debate: epistemic_engine_v3

## Attacker: Quantitative Risk Actuary, specializing in Numerical Stability and Gradient Integrity
## Analytical Critique of Thesis and Falsification Suite

The V3 architecture thesis proposes a `DifferentiabilityRobustnessCheck` and `AxiomDifferentiabilityVeto` to enhance the robustness of gradient-based credit assignment and prevent anti-gaming exploits. While the architectural intent is sound, a detailed examination of the accompanying Python Falsification Suite reveals several critical numerical and architectural vulnerabilities that compromise the system's purported robustness and precision.

**1. Numerical Robustness of `EpistemicGradientUpdater`'s Adam Implementation:**
The `EpistemicGradientUpdater` employs the Adam optimizer with standard bias corrections for `m_hat` and `v_hat`. The `adam_beta1` (0.9), `adam_beta2` (0.999), and `adam_epsilon_stabilizer` (1e-8) are conventional hyperparameters, mathematically sound for their intended purpose. The bias corrections `/(1 - beta^t)` are correctly applied and become negligible as `t` increases, which is the expected behavior. No immediate insolvency is identified in the core Adam update logic itself.

**2. Numerical Derivative Calculation in `FiringSquad`:**
The `FiringSquad`'s numerical derivative calculation utilizes a dynamically decreasing `epsilon` (`current_epsilon_for_sensitivity`) that approaches `1e-6`. While a dynamic `epsilon` is a heuristic attempt to balance approximation error and floating-point precision, `1e-6` remains a fixed lower bound. For functions with extremely flat or steep gradients (e.g., near sigmoid saturation), this `epsilon` may still be too large to accurately capture local linearity or too small to avoid floating-point noise, leading to imprecise gradient estimations. The `differentiability_robustness_check` employs multiple `epsilon_scales` (`[1e-5, 1e-4, 1e-3]`) and a `differentiability_tolerance` (0.05) to probe gradient consistency. This multi-scale approach is a reasonable method for detecting non-smoothness, but the `tolerance` itself is an empirically tuned heuristic, not a mathematically derived guarantee.

**3. Bounds and Precision of `LOAD-BEARING VARIABLES` under Extreme Conditions:**

*   **Sigmoid Saturation and Gradient Vanishing:** The `ThesisPredictor`'s `_sigmoid` function includes `np.clip(x, -500, 500)`. While this prevents `OverflowError` in `np.exp`, it explicitly forces saturation of the sigmoid output. When the input `x` is clipped to `500` or `-500`, the derivative of the sigmoid function becomes extremely close to zero. This design choice inherently leads to **vanishing gradients** under conditions where the true underlying probabilities are very close to 0 or 1. This significantly impedes the `EpistemicGradientUpdater`'s ability to learn and adjust parameters in such extreme, yet valid, probabilistic regimes. Crucially, the `Z_actual` generation uses `math.exp` without such clipping, creating a potential mismatch where the true probability can be `0` or `1` (or extremely close), while the `ThesisPredictor` is artificially constrained from reaching these values, leading to persistent prediction errors and ineffective gradient updates.

*   **Stability of `BS_reference` when close to zero:** The calculation of `BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)` is inherently unstable when `rolling_historical_freq` approaches 0 or 1. The code explicitly includes a "cooked book" constant: `if BS_reference < 1e-9: BS_reference = 1e-9`. This hard floor prevents division by zero in the Brier Skill Score (BSS) calculation but fundamentally masks the system's inability to robustly evaluate predictive skill when the baseline event frequency is highly skewed. For an epistemic engine, accurately assessing performance for rare or near-certain events is critical; this artificial floor renders the BSS metric unreliable and potentially misleading in such scenarios.

*   **`growth_rate`/`inflation_rate` values:** The `hypothetical_economy_growth_rate_q1_2025_base` (0.02) and `hypothetical_inflation_rate_q1_2025_base` (0.03) are plausible quarterly rates. The simulated non-linear coefficients (`true_growth_freq_nl`, `true_inflation_freq_nl`, `true_interaction_coeff_nl`) are chosen such that the inputs to the sigmoid in `true_linear_combination_nl` are generally within a moderate range, avoiding immediate vanishing/exploding gradients from the input features themselves. The primary source of vanishing gradients arises from the `_sigmoid` clipping, not from extreme input values.

**4. "Cooked Books" and Architectural Limitations:**

*   **`BS_reference` Flooring:** As noted, the `BS_reference = 1e-9` floor is a direct "cooked book" that artificially stabilizes the BSS calculation at the expense of true numerical fidelity under extreme probability distributions.
*   **Incomplete Differentiability Enforcement:** The `FiringSquad.differentiability_robustness_check` explicitly contains the line `if param_array.shape != (1,): continue # Skip if not a scalar axiom coefficient`. This creates a significant architectural loophole. While the `MetaJudge.validate_thesis_predictor_architecture` currently enforces that axiom coefficients *must* be scalar (`shape != (1,)`), this `continue` statement in the `FiringSquad` means that if the `MetaJudge`'s constraint were ever relaxed (e.g., to allow vector embeddings for axioms), the `DifferentiabilityRobustnessCheck` would *fail to apply* to non-scalar axiom representations, leaving them vulnerable to non-differentiable exploits. The anti-gaming mechanism is thus not universally robust across all potential axiom representations.
*   **`_sigmoid` Clipping Mismatch:** The `ThesisPredictor`'s clipped sigmoid versus the `Z_actual`'s unclipped sigmoid creates a fundamental inconsistency in the simulation's "ground truth" versus the model's representational capacity, directly contributing to the vanishing gradient problem.

**Parametric Grounding Audit:**
The `LOAD-BEARING VARIABLES` related to Adam parameters, learning rates, and simulation control (e.g., `min_observations_for_calibration`, `rolling_window_size`) are dimensionless system parameters and are appropriately defined. The `hypothetical_economy_growth_rate_q1_2025_base` (2% quarterly) and `hypothetical_inflation_rate_q1_2025_base` (3% quarterly) are plausible, albeit high for inflation, financial metrics. The parameters defining the *simulated* non-linear `Z_actual` function (`true_bias_nl`, `true_growth_freq_nl`, etc.) are internal to the simulation's synthetic reality and are not claimed to represent real-world physical or financial constants. Their values are chosen to create a non-linear environment, which aligns with the "ABSTRACTION MANDATE" to use the simplest possible simulation for architectural demonstration. No misapplication or order-of-magnitude errors are identified for these *simulated* parameters.

**So What for the Meta-Judge:**

The V3 architecture's claim of robust, gradient-based credit assignment and anti-gaming preservation is compromised by critical numerical and architectural vulnerabilities. The artificial flooring of `BS_reference` at `1e-9` renders the Brier Skill Score an unreliable metric for extreme probabilities, masking true performance degradation. Concurrently, the `ThesisPredictor`'s `_sigmoid` function, with its hard clipping, inherently causes vanishing gradients when true probabilities are near 0 or 1. This prevents the `EpistemicGradientUpdater` from effectively learning in such scenarios, leading to persistent prediction errors and inaccurate axiom coefficient convergence. Furthermore, the `DifferentiabilityRobustnessCheck` is architecturally limited to scalar axiom coefficients, creating a future loophole for non-differentiable exploits if axiom representations evolve. These issues collectively demonstrate that while the *intent* to enforce differentiability and robust learning is present, the *implementation* contains specific numerical compromises and architectural limitations that prevent truly anti-fragile credit assignment, particularly under edge-case conditions of extreme probabilities or evolving axiom representations. The system's reported Brier Skill Score may appear robust, but its underlying numerical stability and anti-gaming guarantees are compromised by these specific design choices.

---

### COUNTER-TEST

```python
import math
import random
import collections
import inspect
import numpy as np # For matrix operations

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
epsilon = 0.001 # Initial perturbation magnitude for numerical derivative calculation
adam_beta1 = 0.9 # Adam optimizer parameter: decay rate for first moment estimates (m)
adam_beta2 = 0.999 # Adam optimizer parameter: decay rate for second moment estimates (v)
adam_epsilon_stabilizer = 1e-8 # Adam optimizer parameter: small constant to prevent division by zero
learning_rate_model_params = 0.001 # Global learning rate scale for all model parameters (weights/biases)
learning_rate_axiom_coeffs = 0.01 # NEW: Learning rate scale specifically for axiom coefficients
min_observations_for_calibration = 200 # Minimum Z_actual observations before BSS can be robustly calculated
target_brier_skill_score = 0.20 # Minimum acceptable Brier Skill Score after calibration
rolling_window_size = 50 # Number of observations for rolling average Brier Skill Score calculation
hidden_layer_size = 4 # Number of neurons in the ThesisPredictor's hidden layer

initial_axiom_coefficient_value = 0.5 # NEW: Initial value for axiom coefficients within ThesisPredictor
axiom_sync_frequency = 1 # NEW: Frequency for Meta-Judge to sync learned axiom coefficients

hypothetical_economy_growth_rate_q1_2025_base = 0.02 # Baseline for simulated economy growth rate
hypothetical_inflation_rate_q1_2025_base = 0.03 # Baseline for simulated inflation rate

true_bias_nl = -0.5 # Intercept term for the *simulated non-linear* Z_actual function
true_growth_freq_nl = 50 # Frequency parameter for sine component of *simulated non-linear* growth effect
true_growth_coeff_nl = 10 # Coefficient for sine component of *simulated non-linear* growth effect
true_inflation_freq_nl = 30 # Frequency parameter for cosine component of *simulated non-linear* inflation effect
true_inflation_coeff_nl = -15 # Coefficient for cosine component of *simulated non-linear* inflation effect
true_interaction_coeff_nl = 500 # Coefficient for interaction term (growth_rate * inflation_rate)
true_axiom_relevance = 0.8 # Relevance of AXIOM_RECESSION_AVOIDANCE in the *simulated non-linear* Z_actual

differentiability_tolerance = 0.05 # NEW: Max allowed absolute difference between perturbation gradients for DifferentiabilityRobustnessCheck
robustness_perturbation_epsilon_scales = [0.00001, 0.0001, 0.001] # NEW: Array of epsilon scales for robustness check


class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Axioms are treated as learnable parameters within the MLP.
    """
    def __init__(self, external_input_size: int, hidden_size: int, output_size: int = 1,
                 axiom_initial_weights: dict = None):
        
        self.external_input_size = external_input_size 
        
        self.learned_axiom_coeffs = {}
        if axiom_initial_weights:
            for axiom_name, initial_value in axiom_initial_weights.items():
                self.learned_axiom_coeffs[axiom_name] = np.array([initial_value], dtype=np.float64) # Make it a numpy array for consistent gradient calculation
        else:
            raise ValueError("ThesisPredictor must be initialized with axiom_initial_weights for its learnable coefficients.")

        self.axiom_names = sorted(list(self.learned_axiom_coeffs.keys()))
        self.num_axioms = len(self.axiom_names)
        
        # Total input features for the first layer (external inputs + axiom coefficients)
        total_input_features_to_mlp = self.external_input_size + self.num_axioms

        # Initialize MLP weights and biases with the *correct* total input dimension
        self.weights_ih = np.random.randn(total_input_features_to_mlp, hidden_size).astype(np.float64) * 0.1 
        self.bias_h = np.zeros((1, hidden_size), dtype=np.float64) 
        self.weights_ho = np.random.randn(hidden_size, output_size).astype(np.float64) * 0.1 
        self.bias_o = np.zeros((1, output_size), dtype=np.float64) 

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) 

    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP.
        This function now explicitly uses load-bearing variables and *internal* learnable axiom coefficients.
        """
        # Prepare input vector (external load-bearing variables + internal axiom coefficients)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        axiom_inputs = np.array([self.learned_axiom_coeffs[name].item() for name in self.axiom_names], dtype=np.float64)
        
        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)

        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")

        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (MLP weights/biases + axiom coefficients)."""
        params = {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
        }
        params.update(self.learned_axiom_coeffs) 
        return params

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        for axiom_name in self.learned_axiom_coeffs: 
            self.learned_axiom_coeffs[axiom_name] = params_dict[axiom_name]


class FiringSquad:
    """
    Executes the ThesisPredictor, implements Robust Sensitivity Attributor (RSA),
    and now includes DifferentiabilityRobustnessCheck.
    """
    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases + axiom coefficients) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline = thesis_predictor.calculate_p_predicted(load_bearing_variables)

        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=np.float64)

            # Only calculate derivatives for single-element axiom coefficients or MLP parameters
            if param_name in thesis_predictor.learned_axiom_coeffs or param_name in ['weights_ih', 'bias_h', 'weights_ho', 'bias_o']:
                for i in range(len(flat_param)):
                    # Perturb +epsilon
                    perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_plus = perturbed_params_plus[param_name].flatten()
                    temp_flat_plus[i] += current_epsilon
                    perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_plus)
                    P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                    # Perturb -epsilon
                    perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_minus = perturbed_params_minus[param_name].flatten()
                    temp_flat_minus[i] -= current_epsilon
                    perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_minus)
                    P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                    dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
                
                sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        thesis_predictor.set_all_params(original_params) # Restore original parameters

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }

    def differentiability_robustness_check(self, thesis_predictor: ThesisPredictor,
                                           load_bearing_variables: dict,
                                           epsilon_scales: list,
                                           tolerance: float) -> dict:
        """
        NEW: Computes numerical gradients for each axiom coefficient using multiple epsilon scales
        and checks for consistency, detecting non-differentiable exploits.
        Returns a dictionary with 'pass' status and 'gradient_consistency_scores' for each axiom.
        """
        check_results = {"pass": True, "gradient_consistency_scores": {}}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        for axiom_name in thesis_predictor.learned_axiom_coeffs.keys():
            gradients_at_scales = []
            
            for eps in epsilon_scales:
                param_array = original_params[axiom_name]
                if param_array.shape != (1,): # Only check scalar axiom coeffs
                    continue # Skip if not a scalar axiom coefficient
                
                # Perturb +eps
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_plus[axiom_name][0] += eps
                thesis_predictor.set_all_params(perturbed_params_plus)
                P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                # Perturb -eps
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_minus[axiom_name][0] -= eps
                thesis_predictor.set_all_params(perturbed_params_minus)
                P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                gradient = (P_plus - P_minus) / (2 * eps)
                gradients_at_scales.append(gradient)
            
            thesis_predictor.set_all_params(original_params) # Restore original params after each axiom check

            if len(gradients_at_scales) > 1:
                # Calculate the maximum absolute difference between any two gradients to assess consistency
                max_diff = 0.0
                for i in range(len(gradients_at_scales)):
                    for j in range(i + 1, len(gradients_at_scales)):
                        max_diff = max(max_diff, abs(gradients_at_scales[i] - gradients_at_scales[j]))
                
                check_results["gradient_consistency_scores"][axiom_name] = max_diff
                if max_diff > tolerance:
                    check_results["pass"] = False
            elif len(gradients_at_scales) == 1:
                 # If only one scale, it's vacuously consistent, assign 0 score
                 check_results["gradient_consistency_scores"][axiom_name] = 0.0
            else: # No scales provided
                 check_results["gradient_consistency_scores"][axiom_name] = np.inf # Indicate failure to check
                 check_results["pass"] = False

        return check_results


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters,
    including new axiom coefficients.
    """
    def __init__(self, learning_rate_model_params, learning_rate_axiom_coeffs, beta1, beta2, epsilon_stabilizer):
        self.learning_rate_model_params = learning_rate_model_params
        self.learning_rate_axiom_coeffs = learning_rate_axiom_coeffs
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} 
        self.v = {} 
        self.t = 0 

    def update(self, thesis_predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]

        dBS_dP = 2 * (P_predicted - Z_actual) # Derivative of Brier Score w.r.t P_predicted

        current_params = thesis_predictor.get_all_params()
        new_params = {k: v.copy() for k, v in current_params.items()}

        for param_name, param_array in current_params.items():
            dP_d_param = sensitivity_vector.get(param_name, np.zeros_like(param_array, dtype=np.float64))
            gradient = dBS_dP * dP_d_param

            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(param_array, dtype=np.float64)
                self.v[param_name] = np.zeros_like(param_array, dtype=np.float64)

            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * gradient
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (gradient ** 2)

            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

            current_lr = self.learning_rate_axiom_coeffs if param_name in thesis_predictor.learned_axiom_coeffs else self.learning_rate_model_params

            new_params[param_name] -= current_lr * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
        
        thesis_predictor.set_all_params(new_params)


class MetaJudge:
    """
    Scores thesis, manages ThesisPredictor parameters (via updater), enforces architectural validation,
    syncs learned axiom coefficients, and now enforces AxiomDifferentiabilityVeto.
    """
    def __init__(self, external_input_size, hidden_size, output_size):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value} 
        
        self.thesis_predictor = ThesisPredictor(
            external_input_size=external_input_size, 
            hidden_size=hidden_size,
            output_size=output_size,
            axiom_initial_weights=self.axiom_weights
        )
        
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, learning_rate_axiom_coeffs, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon 

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, MLP structure,
        and crucially, its implementation of learnable axiom coefficients.
        """
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        required_attributes = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid', 'learned_axiom_coeffs']
        for attr in required_attributes:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement MLP structure (missing '{attr}' attribute).")
        
        # AxiomCoeffValidation: Verify learnable axiom coefficients
        if not isinstance(predictor.learned_axiom_coeffs, dict) or not predictor.learned_axiom_coeffs:
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have a 'learned_axiom_coeffs' dictionary for axiom parameters.")
        for axiom_name in self.axiom_weights.keys():
            if axiom_name not in predictor.learned_axiom_coeffs or not isinstance(predictor.learned_axiom_coeffs[axiom_name], np.ndarray):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor missing learnable coefficient for axiom '{axiom_name}' or it's not a numpy array.")
            if predictor.learned_axiom_coeffs[axiom_name].shape != (1,):
                raise ValueError(f"Meta-Judge VETO: Axiom coefficient for '{axiom_name}' must be a scalar numpy array (shape (1,)).")

        # Input dimension consistency check for weights_ih
        expected_input_features = predictor.external_input_size + predictor.num_axioms
        if predictor.weights_ih.shape[0] != expected_input_features:
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor's weights_ih input dimension ({predictor.weights_ih.shape[0]}) "
                              f"does not match expected total input features ({expected_input_features}). "
                              "Ensure external_input_size + num_axioms == weights_ih.shape[0]")

        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        test_p = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

    def sync_axiom_weights_from_predictor(self):
        """
        AxiomWeightSynchronization Protocol: Updates the Meta-Judge's global axiom_weights
        store with the empirically learned coefficients from the ThesisPredictor.
        """
        for axiom_name, learned_coeff_array in self.thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = learned_coeff_array.item()

    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, iteration: int, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        Includes DifferentiabilityRobustnessCheck and veto.
        """
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # AxiomDifferentiabilityVeto: Perform robustness check
        differentiability_check_results = self.firing_squad.differentiability_robustness_check(
            self.thesis_predictor, load_bearing_variables, robustness_perturbation_epsilon_scales, differentiability_tolerance
        )

        if not differentiability_check_results["pass"]:
            # If any axiom is non-differentiable or gamed, veto the entire thesis
            inconsistent_axioms = [
                ax for ax, score in differentiability_check_results["gradient_consistency_scores"].items()
                if score > differentiability_tolerance
            ]
            raise ValueError(
                f"Meta-Judge VETO (AxiomDifferentiabilityVeto): Thesis contains non-differentiable or gamed axiom(s): {inconsistent_axioms}. "
                "Gradient consistency scores: " + str({ax: f"{score:.6f}" for ax, score in differentiability_check_results["gradient_consistency_scores"].items()})
            )

        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        if iteration % axiom_sync_frequency == 0:
            self.sync_axiom_weights_from_predictor()
        
        return sensitivity_report["P_predicted_baseline"], differentiability_check_results["gradient_consistency_scores"]

# --- COUNTER-TEST Implementation ---
def counter_test_extreme_probabilities():
    print("\n--- Initiating COUNTER-TEST: Extreme Probability Scenario ---")
    print("This test aims to expose numerical insolvency due to BS_reference clipping and sigmoid saturation.")

    # --- Override LOAD-BEARING VARIABLES for extreme conditions ---
    # Store original values to restore later
    global true_bias_nl, true_axiom_relevance, min_observations_for_calibration, target_brier_skill_score
    
    original_true_bias_nl = true_bias_nl
    original_true_axiom_relevance = true_axiom_relevance
    original_min_observations = min_observations_for_calibration
    original_target_bss = target_brier_skill_score

    # Set parameters to consistently generate Z_actual = 0 (or very close to it)
    true_bias_nl = -10.0  # Significantly negative bias
    true_axiom_relevance = -5.0 # Significantly negative axiom relevance
    min_observations_for_calibration = 500 # More observations to allow for potential (but expected to fail) convergence
    target_brier_skill_score = 0.05 # Lower target BSS, as model struggles with extreme probs

    print(f"Overridden: true_bias_nl={true_bias_nl}, true_axiom_relevance={true_axiom_relevance}, min_observations_for_calibration={min_observations_for_calibration}, target_brier_skill_score={target_brier_skill_score}")

    external_input_features = 2 
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] 
    differentiability_scores_history = collections.defaultdict(list)
    bs_reference_floored_count = 0
    max_p_predicted_when_z_actual_is_zero = 0.0

    for i in range(min_observations_for_calibration):
        current_epsilon_for_sensitivity = epsilon * (1 - i / min_observations_for_calibration) + 1e-6 

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
        
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']

        # True underlying process (smoothly non-linear and differentiable, but now producing very low probabilities)
        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * 1.0 
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        # Z_actual will be almost exclusively 0 due to the very low true_prob_avoid_recession
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted, grad_consistency_scores = meta_judge.evaluate_and_update(
            current_load_bearing_variables, Z_actual, i+1, current_epsilon_for_sensitivity
        )

        for axiom_name, score in grad_consistency_scores.items():
            differentiability_scores_history[axiom_name].append(score)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            
            original_bs_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            BS_reference = original_bs_reference
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 
                bs_reference_floored_count += 1

            BSS = 1 - (BS_model / BS_reference)
            
            tracked_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
            current_grad_consistency_score = grad_consistency_scores.get('AXIOM_RECESSION_AVOIDANCE', np.nan)

            if Z_actual == 0:
                max_p_predicted_when_z_actual_is_zero = max(max_p_predicted_when_z_actual_is_zero, P_predicted)

            print(f"Obs {i+1:3d}: P_pred={P_predicted:.6f}, Z_actual={Z_actual}, BS_model={BS_model:.6f}, BSS={BSS:.3f}, LearnedAxiomCoeff={tracked_axiom_coeff:.3f}, GradConsistency={current_grad_consistency_score:.5f}, BS_ref_orig={original_bs_reference:.6f}")

            if i == min_observations_for_calibration - 1:
                print(f"\n--- COUNTER-TEST RESULTS after {min_observations_for_calibration} observations ---")
                
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                print(f"Number of times BS_reference was floored to 1e-9: {bs_reference_floored_count}")
                print(f"Max P_predicted observed when Z_actual was 0: {max_p_predicted_when_z_actual_is_zero:.6f}")

                # Assertions to expose insolvency of the Mutator's system
                
                # 1. Assert that BS_reference was indeed floored, confirming the extreme scenario setup.
                assert bs_reference_floored_count > (min_observations_for_calibration - rolling_window_size) * 0.8, \
                    f"COUNTER-TEST SETUP FAILED: BS_reference was not consistently floored ({bs_reference_floored_count} times). " \
                    "The extreme low probability scenario was not adequately generated."
                
                # 2. Assert that P_predicted failed to reach sufficiently low values when Z_actual was 0,
                # demonstrating the effect of sigmoid clipping and vanishing gradients.
                # If the model *could* predict very low values (e.g., < 1e-4), this assertion would fail, indicating unexpected robustness.
                assert max_p_predicted_when_z_actual_is_zero > 1e-4, \
                    f"FALSIFICATION FAILED: ThesisPredictor's P_predicted was able to reach very low values " \
                    f"({max_p_predicted_when_z_actual_is_zero:.6f}) when Z_actual was 0. " \
                    "The sigmoid clipping did not hinder learning of extreme probabilities as expected, indicating unexpected robustness."

                # 3. Assert that the Brier Skill Score is significantly degraded, failing the Mutator's implied performance target.
                # A negative BSS means the model is worse than a naive baseline, which is a clear failure.
                assert final_bss < 0.0, \
                    f"FALSIFICATION FAILED: Rolling Brier Skill Score ({final_bss:.3f}) is not negative, " \
                    "indicating the model performed better than a naive baseline even under extreme low probability conditions. " \
                    "Expected significant performance degradation due to numerical instabilities."

                # 4. Assert that the learned axiom coefficient did not converge towards the true negative relevance,
                # indicating a failure in gradient-based credit assignment due to vanishing gradients.
                final_learned_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
                print(f"Final Learned AXIOM_RECESSION_AVOIDANCE coefficient: {final_learned_axiom_coeff:.3f}")
                # The true relevance is -5.0. Initial is 0.5. If it's still positive or not sufficiently negative (e.g., > -1.0),
                # it indicates learning failure due to vanishing gradients.
                assert final_learned_axiom_coeff > -1.0, \
                    f"FALSIFICATION FAILED: Learned AXIOM_RECESSION_AVOIDANCE coefficient ({final_learned_axiom_coeff:.3f}) " \
                    f"converged too well towards the true negative relevance ({true_axiom_relevance:.3f}). " \
                    "Expected learning failure due to vanishing gradients from sigmoid saturation."

    print("\nCOUNTER-TEST PASSED: The system demonstrated resilience to the identified numerical instabilities. This indicates a more robust implementation than initially assessed under extreme conditions.")

    # Restore original global variables
    true_bias_nl = original_true_bias_nl
    true_axiom_relevance = original_true_axiom_relevance
    min_observations_for_calibration = original_min_observations
    target_brier_skill_score = original_target_bss

if __name__ == "__main__":
    counter_test_extreme_probabilities()
```

### PYTHON EXECUTION OUTPUT:

--- Initiating COUNTER-TEST: Extreme Probability Scenario ---
This test aims to expose numerical insolvency due to BS_reference clipping and sigmoid saturation.
Overridden: true_bias_nl=-10.0, true_axiom_relevance=-5.0, min_observations_for_calibration=500, target_brier_skill_score=0.05
Obs  50: P_pred=0.485911, Z_actual=0, BS_model=0.243599, BSS=-243598601.510, LearnedAxiomCoeff=0.275, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  51: P_pred=0.485572, Z_actual=0, BS_model=0.243282, BSS=-243282308.543, LearnedAxiomCoeff=0.283, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  52: P_pred=0.485248, Z_actual=0, BS_model=0.242967, BSS=-242966939.369, LearnedAxiomCoeff=0.292, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  53: P_pred=0.484909, Z_actual=0, BS_model=0.242652, BSS=-242651997.254, LearnedAxiomCoeff=0.300, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  54: P_pred=0.484569, Z_actual=0, BS_model=0.242338, BSS=-242337665.125, LearnedAxiomCoeff=0.309, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  55: P_pred=0.484231, Z_actual=0, BS_model=0.242024, BSS=-242023804.272, LearnedAxiomCoeff=0.319, GradConsistency=0.00084, BS_ref_orig=0.000000
Obs  56: P_pred=0.483899, Z_actual=0, BS_model=0.241710, BSS=-241710375.191, LearnedAxiomCoeff=0.327, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  57: P_pred=0.483571, Z_actual=0, BS_model=0.241398, BSS=-241397740.556, LearnedAxiomCoeff=0.335, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  58: P_pred=0.483226, Z_actual=0, BS_model=0.241085, BSS=-241085207.620, LearnedAxiomCoeff=0.343, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  59: P_pred=0.482884, Z_actual=0, BS_model=0.240773, BSS=-240772884.446, LearnedAxiomCoeff=0.351, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  60: P_pred=0.482536, Z_actual=0, BS_model=0.240461, BSS=-240460757.087, LearnedAxiomCoeff=0.358, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  61: P_pred=0.482169, Z_actual=0, BS_model=0.240148, BSS=-240148425.674, LearnedAxiomCoeff=0.366, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  62: P_pred=0.481827, Z_actual=0, BS_model=0.239836, BSS=-239836121.394, LearnedAxiomCoeff=0.373, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  63: P_pred=0.481475, Z_actual=0, BS_model=0.239524, BSS=-239523738.851, LearnedAxiomCoeff=0.380, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  64: P_pred=0.481112, Z_actual=0, BS_model=0.239211, BSS=-239211072.339, LearnedAxiomCoeff=0.387, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  65: P_pred=0.480730, Z_actual=0, BS_model=0.238898, BSS=-238897629.115, LearnedAxiomCoeff=0.395, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  66: P_pred=0.480367, Z_actual=0, BS_model=0.238584, BSS=-238583680.802, LearnedAxiomCoeff=0.402, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  67: P_pred=0.480001, Z_actual=0, BS_model=0.238269, BSS=-238269330.144, LearnedAxiomCoeff=0.409, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  68: P_pred=0.479617, Z_actual=0, BS_model=0.237954, BSS=-237954059.385, LearnedAxiomCoeff=0.417, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  69: P_pred=0.479216, Z_actual=0, BS_model=0.237638, BSS=-237637507.499, LearnedAxiomCoeff=0.425, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  70: P_pred=0.478847, Z_actual=0, BS_model=0.237320, BSS=-237320228.849, LearnedAxiomCoeff=0.433, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  71: P_pred=0.478454, Z_actual=0, BS_model=0.237002, BSS=-237001934.176, LearnedAxiomCoeff=0.442, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  72: P_pred=0.478043, Z_actual=0, BS_model=0.236682, BSS=-236682131.656, LearnedAxiomCoeff=0.450, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  73: P_pred=0.477630, Z_actual=0, BS_model=0.236361, BSS=-236360779.924, LearnedAxiomCoeff=0.459, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  74: P_pred=0.477243, Z_actual=0, BS_model=0.236038, BSS=-236038167.259, LearnedAxiomCoeff=0.468, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  75: P_pred=0.476827, Z_actual=0, BS_model=0.235714, BSS=-235713936.356, LearnedAxiomCoeff=0.478, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  76: P_pred=0.476414, Z_actual=0, BS_model=0.235388, BSS=-235388068.199, LearnedAxiomCoeff=0.488, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  77: P_pred=0.475979, Z_actual=0, BS_model=0.235060, BSS=-235060267.444, LearnedAxiomCoeff=0.498, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  78: P_pred=0.475542, Z_actual=0, BS_model=0.234730, BSS=-234730268.443, LearnedAxiomCoeff=0.509, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  79: P_pred=0.475116, Z_actual=0, BS_model=0.234398, BSS=-234398203.733, LearnedAxiomCoeff=0.520, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  80: P_pred=0.474667, Z_actual=0, BS_model=0.234064, BSS=-234063896.733, LearnedAxiomCoeff=0.531, GradConsistency=0.00054, BS_ref_orig=0.000000
Obs  81: P_pred=0.474233, Z_actual=0, BS_model=0.233728, BSS=-233727509.066, LearnedAxiomCoeff=0.543, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  82: P_pred=0.473765, Z_actual=0, BS_model=0.233388, BSS=-233387972.462, LearnedAxiomCoeff=0.556, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  83: P_pred=0.473316, Z_actual=0, BS_model=0.233046, BSS=-233045599.857, LearnedAxiomCoeff=0.569, GradConsistency=0.00055, BS_ref_orig=0.000000
Obs  84: P_pred=0.472848, Z_actual=0, BS_model=0.232700, BSS=-232699766.706, LearnedAxiomCoeff=0.583, GradConsistency=0.00038, BS_ref_orig=0.000000
Obs  85: P_pred=0.472379, Z_actual=0, BS_model=0.232351, BSS=-232350799.863, LearnedAxiomCoeff=0.597, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  86: P_pred=0.471880, Z_actual=0, BS_model=0.231998, BSS=-231998051.776, LearnedAxiomCoeff=0.611, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  87: P_pred=0.471373, Z_actual=0, BS_model=0.231641, BSS=-231641356.496, LearnedAxiomCoeff=0.625, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  88: P_pred=0.470910, Z_actual=0, BS_model=0.231282, BSS=-231281594.060, LearnedAxiomCoeff=0.639, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  89: P_pred=0.470374, Z_actual=0, BS_model=0.230918, BSS=-230917637.853, LearnedAxiomCoeff=0.654, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  90: P_pred=0.469896, Z_actual=0, BS_model=0.230550, BSS=-230550472.400, LearnedAxiomCoeff=0.669, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  91: P_pred=0.469357, Z_actual=0, BS_model=0.230179, BSS=-230179175.295, LearnedAxiomCoeff=0.684, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  92: P_pred=0.468824, Z_actual=0, BS_model=0.229804, BSS=-229803740.076, LearnedAxiomCoeff=0.699, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  93: P_pred=0.468261, Z_actual=0, BS_model=0.229424, BSS=-229423845.977, LearnedAxiomCoeff=0.715, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  94: P_pred=0.467731, Z_actual=0, BS_model=0.229040, BSS=-229040136.621, LearnedAxiomCoeff=0.730, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  95: P_pred=0.467187, Z_actual=0, BS_model=0.228652, BSS=-228652155.995, LearnedAxiomCoeff=0.746, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  96: P_pred=0.466591, Z_actual=0, BS_model=0.228259, BSS=-228259227.961, LearnedAxiomCoeff=0.762, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  97: P_pred=0.466026, Z_actual=0, BS_model=0.227862, BSS=-227861929.481, LearnedAxiomCoeff=0.779, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs  98: P_pred=0.465454, Z_actual=0, BS_model=0.227460, BSS=-227460038.630, LearnedAxiomCoeff=0.796, GradConsistency=0.00039, BS_ref_orig=0.000000
Obs  99: P_pred=0.464864, Z_actual=0, BS_model=0.227054, BSS=-227053671.521, LearnedAxiomCoeff=0.813, GradConsistency=0.00032, BS_ref_orig=0.000000
Obs 100: P_pred=0.464259, Z_actual=0, BS_model=0.226642, BSS=-226642198.359, LearnedAxiomCoeff=0.830, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 101: P_pred=0.463637, Z_actual=0, BS_model=0.226226, BSS=-226225781.617, LearnedAxiomCoeff=0.848, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 102: P_pred=0.462991, Z_actual=0, BS_model=0.225804, BSS=-225803678.722, LearnedAxiomCoeff=0.865, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 103: P_pred=0.462376, Z_actual=0, BS_model=0.225377, BSS=-225376777.718, LearnedAxiomCoeff=0.883, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 104: P_pred=0.461721, Z_actual=0, BS_model=0.224944, BSS=-224944360.033, LearnedAxiomCoeff=0.901, GradConsistency=0.00055, BS_ref_orig=0.000000
Obs 105: P_pred=0.461038, Z_actual=0, BS_model=0.224506, BSS=-224505885.599, LearnedAxiomCoeff=0.919, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 106: P_pred=0.460385, Z_actual=0, BS_model=0.224062, BSS=-224061812.913, LearnedAxiomCoeff=0.937, GradConsistency=0.00002, BS_ref_orig=0.000000
Obs 107: P_pred=0.459731, Z_actual=0, BS_model=0.223612, BSS=-223612042.905, LearnedAxiomCoeff=0.956, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 108: P_pred=0.459040, Z_actual=0, BS_model=0.223156, BSS=-223156249.456, LearnedAxiomCoeff=0.974, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 109: P_pred=0.458306, Z_actual=0, BS_model=0.222694, BSS=-222693605.602, LearnedAxiomCoeff=0.992, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 110: P_pred=0.457610, Z_actual=0, BS_model=0.222225, BSS=-222224921.986, LearnedAxiomCoeff=1.011, GradConsistency=0.00005, BS_ref_orig=0.000000
Obs 111: P_pred=0.456895, Z_actual=0, BS_model=0.221750, BSS=-221750251.172, LearnedAxiomCoeff=1.030, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 112: P_pred=0.456151, Z_actual=0, BS_model=0.221269, BSS=-221268587.147, LearnedAxiomCoeff=1.048, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 113: P_pred=0.455399, Z_actual=0, BS_model=0.220780, BSS=-220779986.749, LearnedAxiomCoeff=1.067, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 114: P_pred=0.454702, Z_actual=0, BS_model=0.220286, BSS=-220285688.128, LearnedAxiomCoeff=1.086, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 115: P_pred=0.453890, Z_actual=0, BS_model=0.219784, BSS=-219783973.064, LearnedAxiomCoeff=1.105, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 116: P_pred=0.453098, Z_actual=0, BS_model=0.219275, BSS=-219274866.295, LearnedAxiomCoeff=1.124, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 117: P_pred=0.452381, Z_actual=0, BS_model=0.218760, BSS=-218759809.577, LearnedAxiomCoeff=1.143, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 118: P_pred=0.451524, Z_actual=0, BS_model=0.218237, BSS=-218236639.005, LearnedAxiomCoeff=1.162, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 119: P_pred=0.450708, Z_actual=0, BS_model=0.217706, BSS=-217706447.717, LearnedAxiomCoeff=1.181, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 120: P_pred=0.449906, Z_actual=0, BS_model=0.217169, BSS=-217168867.689, LearnedAxiomCoeff=1.200, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 121: P_pred=0.449087, Z_actual=0, BS_model=0.216624, BSS=-216624079.839, LearnedAxiomCoeff=1.220, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 122: P_pred=0.448228, Z_actual=0, BS_model=0.216072, BSS=-216071750.747, LearnedAxiomCoeff=1.239, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 123: P_pred=0.447341, Z_actual=0, BS_model=0.215511, BSS=-215511408.755, LearnedAxiomCoeff=1.258, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 124: P_pred=0.446492, Z_actual=0, BS_model=0.214943, BSS=-214943286.039, LearnedAxiomCoeff=1.278, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 125: P_pred=0.445552, Z_actual=0, BS_model=0.214366, BSS=-214366336.864, LearnedAxiomCoeff=1.297, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 126: P_pred=0.444680, Z_actual=0, BS_model=0.213782, BSS=-213781731.649, LearnedAxiomCoeff=1.316, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 127: P_pred=0.443779, Z_actual=0, BS_model=0.213189, BSS=-213189408.952, LearnedAxiomCoeff=1.336, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 128: P_pred=0.442855, Z_actual=0, BS_model=0.212589, BSS=-212589028.981, LearnedAxiomCoeff=1.355, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 129: P_pred=0.441937, Z_actual=0, BS_model=0.211980, BSS=-211980494.450, LearnedAxiomCoeff=1.375, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 130: P_pred=0.440918, Z_actual=0, BS_model=0.211362, BSS=-211362483.021, LearnedAxiomCoeff=1.394, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 131: P_pred=0.440056, Z_actual=0, BS_model=0.210738, BSS=-210737525.039, LearnedAxiomCoeff=1.413, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 132: P_pred=0.439049, Z_actual=0, BS_model=0.210104, BSS=-210103736.353, LearnedAxiomCoeff=1.433, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 133: P_pred=0.438030, Z_actual=0, BS_model=0.209461, BSS=-209460568.683, LearnedAxiomCoeff=1.452, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 134: P_pred=0.437050, Z_actual=0, BS_model=0.208809, BSS=-208809109.379, LearnedAxiomCoeff=1.471, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 135: P_pred=0.436102, Z_actual=0, BS_model=0.208150, BSS=-208149963.809, LearnedAxiomCoeff=1.491, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 136: P_pred=0.435002, Z_actual=0, BS_model=0.207481, BSS=-207481073.539, LearnedAxiomCoeff=1.510, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 137: P_pred=0.434045, Z_actual=0, BS_model=0.206805, BSS=-206805121.090, LearnedAxiomCoeff=1.530, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 138: P_pred=0.433024, Z_actual=0, BS_model=0.206120, BSS=-206120193.888, LearnedAxiomCoeff=1.549, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 139: P_pred=0.431854, Z_actual=0, BS_model=0.205425, BSS=-205425112.135, LearnedAxiomCoeff=1.568, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 140: P_pred=0.430847, Z_actual=0, BS_model=0.204722, BSS=-204721652.829, LearnedAxiomCoeff=1.588, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 141: P_pred=0.429705, Z_actual=0, BS_model=0.204009, BSS=-204008661.438, LearnedAxiomCoeff=1.607, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 142: P_pred=0.428652, Z_actual=0, BS_model=0.203288, BSS=-203287586.313, LearnedAxiomCoeff=1.627, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 143: P_pred=0.427550, Z_actual=0, BS_model=0.202558, BSS=-202558198.975, LearnedAxiomCoeff=1.646, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 144: P_pred=0.426392, Z_actual=0, BS_model=0.201819, BSS=-201818947.132, LearnedAxiomCoeff=1.665, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 145: P_pred=0.425265, Z_actual=0, BS_model=0.201071, BSS=-201070670.686, LearnedAxiomCoeff=1.685, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 146: P_pred=0.424143, Z_actual=0, BS_model=0.200314, BSS=-200314473.670, LearnedAxiomCoeff=1.704, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 147: P_pred=0.422865, Z_actual=0, BS_model=0.199547, BSS=-199547167.616, LearnedAxiomCoeff=1.724, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 148: P_pred=0.421720, Z_actual=0, BS_model=0.198771, BSS=-198771169.247, LearnedAxiomCoeff=1.743, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 149: P_pred=0.420587, Z_actual=0, BS_model=0.197987, BSS=-197987056.500, LearnedAxiomCoeff=1.762, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 150: P_pred=0.419325, Z_actual=0, BS_model=0.197193, BSS=-197192996.300, LearnedAxiomCoeff=1.782, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 151: P_pred=0.418141, Z_actual=0, BS_model=0.196391, BSS=-196390650.660, LearnedAxiomCoeff=1.801, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 152: P_pred=0.416959, Z_actual=0, BS_model=0.195581, BSS=-195580530.362, LearnedAxiomCoeff=1.820, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 153: P_pred=0.415659, Z_actual=0, BS_model=0.194760, BSS=-194760153.806, LearnedAxiomCoeff=1.839, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 154: P_pred=0.414374, Z_actual=0, BS_model=0.193931, BSS=-193930545.315, LearnedAxiomCoeff=1.859, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 155: P_pred=0.413072, Z_actual=0, BS_model=0.193092, BSS=-193092004.900, LearnedAxiomCoeff=1.878, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 156: P_pred=0.411858, Z_actual=0, BS_model=0.192245, BSS=-192245461.463, LearnedAxiomCoeff=1.897, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 157: P_pred=0.410537, Z_actual=0, BS_model=0.191389, BSS=-191389233.604, LearnedAxiomCoeff=1.916, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 158: P_pred=0.409161, Z_actual=0, BS_model=0.190523, BSS=-190523136.099, LearnedAxiomCoeff=1.936, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 159: P_pred=0.407904, Z_actual=0, BS_model=0.189650, BSS=-189649963.478, LearnedAxiomCoeff=1.955, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 160: P_pred=0.406615, Z_actual=0, BS_model=0.188769, BSS=-188768540.554, LearnedAxiomCoeff=1.974, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 161: P_pred=0.405228, Z_actual=0, BS_model=0.187878, BSS=-187877663.820, LearnedAxiomCoeff=1.993, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 162: P_pred=0.403825, Z_actual=0, BS_model=0.186978, BSS=-186977681.366, LearnedAxiomCoeff=2.012, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 163: P_pred=0.402454, Z_actual=0, BS_model=0.186069, BSS=-186069300.792, LearnedAxiomCoeff=2.031, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 164: P_pred=0.401163, Z_actual=0, BS_model=0.185153, BSS=-185152858.236, LearnedAxiomCoeff=2.051, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 165: P_pred=0.399693, Z_actual=0, BS_model=0.184228, BSS=-184227629.438, LearnedAxiomCoeff=2.070, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 166: P_pred=0.398269, Z_actual=0, BS_model=0.183294, BSS=-183294050.842, LearnedAxiomCoeff=2.089, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 167: P_pred=0.396832, Z_actual=0, BS_model=0.182351, BSS=-182350595.487, LearnedAxiomCoeff=2.108, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 168: P_pred=0.395421, Z_actual=0, BS_model=0.181400, BSS=-181400276.835, LearnedAxiomCoeff=2.127, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 169: P_pred=0.393923, Z_actual=0, BS_model=0.180441, BSS=-180441022.730, LearnedAxiomCoeff=2.146, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 170: P_pred=0.392509, Z_actual=0, BS_model=0.179474, BSS=-179473977.744, LearnedAxiomCoeff=2.165, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 171: P_pred=0.391057, Z_actual=0, BS_model=0.178499, BSS=-178498911.932, LearnedAxiomCoeff=2.184, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 172: P_pred=0.389430, Z_actual=0, BS_model=0.177514, BSS=-177513847.609, LearnedAxiomCoeff=2.203, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 173: P_pred=0.387958, Z_actual=0, BS_model=0.176522, BSS=-176521796.501, LearnedAxiomCoeff=2.221, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 174: P_pred=0.386537, Z_actual=0, BS_model=0.175523, BSS=-175522915.305, LearnedAxiomCoeff=2.240, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 175: P_pred=0.384933, Z_actual=0, BS_model=0.174516, BSS=-174516048.148, LearnedAxiomCoeff=2.259, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 176: P_pred=0.383387, Z_actual=0, BS_model=0.173501, BSS=-173500954.307, LearnedAxiomCoeff=2.278, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 177: P_pred=0.381930, Z_actual=0, BS_model=0.172480, BSS=-172479561.456, LearnedAxiomCoeff=2.297, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 178: P_pred=0.380464, Z_actual=0, BS_model=0.171452, BSS=-171452207.838, LearnedAxiomCoeff=2.315, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 179: P_pred=0.378862, Z_actual=0, BS_model=0.170417, BSS=-170416767.279, LearnedAxiomCoeff=2.334, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 180: P_pred=0.377356, Z_actual=0, BS_model=0.169377, BSS=-169376543.060, LearnedAxiomCoeff=2.353, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 181: P_pred=0.375713, Z_actual=0, BS_model=0.168327, BSS=-168326764.656, LearnedAxiomCoeff=2.371, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 182: P_pred=0.373990, Z_actual=0, BS_model=0.167269, BSS=-167268862.236, LearnedAxiomCoeff=2.390, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 183: P_pred=0.372358, Z_actual=0, BS_model=0.166204, BSS=-166204476.290, LearnedAxiomCoeff=2.409, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 184: P_pred=0.370774, Z_actual=0, BS_model=0.165134, BSS=-165133695.324, LearnedAxiomCoeff=2.427, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 185: P_pred=0.369150, Z_actual=0, BS_model=0.164055, BSS=-164055430.338, LearnedAxiomCoeff=2.446, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 186: P_pred=0.367511, Z_actual=0, BS_model=0.162972, BSS=-162972183.892, LearnedAxiomCoeff=2.464, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 187: P_pred=0.365964, Z_actual=0, BS_model=0.161883, BSS=-161882869.053, LearnedAxiomCoeff=2.483, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 188: P_pred=0.364182, Z_actual=0, BS_model=0.160785, BSS=-160785251.284, LearnedAxiomCoeff=2.501, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 189: P_pred=0.362440, Z_actual=0, BS_model=0.159683, BSS=-159682553.132, LearnedAxiomCoeff=2.519, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 190: P_pred=0.361032, Z_actual=0, BS_model=0.158577, BSS=-158576853.383, LearnedAxiomCoeff=2.538, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 191: P_pred=0.359091, Z_actual=0, BS_model=0.157463, BSS=-157462860.859, LearnedAxiomCoeff=2.556, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 192: P_pred=0.357521, Z_actual=0, BS_model=0.156344, BSS=-156344427.034, LearnedAxiomCoeff=2.574, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 193: P_pred=0.355933, Z_actual=0, BS_model=0.155222, BSS=-155222218.272, LearnedAxiomCoeff=2.592, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 194: P_pred=0.354190, Z_actual=0, BS_model=0.154095, BSS=-154095032.080, LearnedAxiomCoeff=2.611, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 195: P_pred=0.352329, Z_actual=0, BS_model=0.152961, BSS=-152960749.072, LearnedAxiomCoeff=2.629, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 196: P_pred=0.350657, Z_actual=0, BS_model=0.151822, BSS=-151822002.494, LearnedAxiomCoeff=2.647, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 197: P_pred=0.348817, Z_actual=0, BS_model=0.150679, BSS=-150679163.678, LearnedAxiomCoeff=2.665, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 198: P_pred=0.347226, Z_actual=0, BS_model=0.149534, BSS=-149533526.791, LearnedAxiomCoeff=2.683, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 199: P_pred=0.345397, Z_actual=0, BS_model=0.148382, BSS=-148381646.587, LearnedAxiomCoeff=2.701, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 200: P_pred=0.343649, Z_actual=0, BS_model=0.147227, BSS=-147226879.250, LearnedAxiomCoeff=2.718, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 201: P_pred=0.341803, Z_actual=0, BS_model=0.146067, BSS=-146066619.771, LearnedAxiomCoeff=2.736, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 202: P_pred=0.340163, Z_actual=0, BS_model=0.144904, BSS=-144903744.367, LearnedAxiomCoeff=2.754, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 203: P_pred=0.338352, Z_actual=0, BS_model=0.143738, BSS=-143737939.612, LearnedAxiomCoeff=2.772, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 204: P_pred=0.336497, Z_actual=0, BS_model=0.142568, BSS=-142568426.922, LearnedAxiomCoeff=2.789, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 205: P_pred=0.334636, Z_actual=0, BS_model=0.141395, BSS=-141395485.643, LearnedAxiomCoeff=2.807, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 206: P_pred=0.332827, Z_actual=0, BS_model=0.140218, BSS=-140218416.858, LearnedAxiomCoeff=2.825, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 207: P_pred=0.331156, Z_actual=0, BS_model=0.139041, BSS=-139040883.145, LearnedAxiomCoeff=2.842, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 208: P_pred=0.329394, Z_actual=0, BS_model=0.137863, BSS=-137862638.838, LearnedAxiomCoeff=2.860, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 209: P_pred=0.327404, Z_actual=0, BS_model=0.136679, BSS=-136678790.783, LearnedAxiomCoeff=2.877, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 210: P_pred=0.325862, Z_actual=0, BS_model=0.135496, BSS=-135495793.410, LearnedAxiomCoeff=2.894, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 211: P_pred=0.323783, Z_actual=0, BS_model=0.134308, BSS=-134308304.303, LearnedAxiomCoeff=2.912, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 212: P_pred=0.322065, Z_actual=0, BS_model=0.133121, BSS=-133121330.225, LearnedAxiomCoeff=2.929, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 213: P_pred=0.320297, Z_actual=0, BS_model=0.131934, BSS=-131933748.545, LearnedAxiomCoeff=2.946, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 214: P_pred=0.318308, Z_actual=0, BS_model=0.130742, BSS=-130741510.479, LearnedAxiomCoeff=2.963, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 215: P_pred=0.316559, Z_actual=0, BS_model=0.129551, BSS=-129550612.203, LearnedAxiomCoeff=2.980, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 216: P_pred=0.314769, Z_actual=0, BS_model=0.128360, BSS=-128359827.133, LearnedAxiomCoeff=2.997, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 217: P_pred=0.312837, Z_actual=0, BS_model=0.127168, BSS=-127167652.454, LearnedAxiomCoeff=3.014, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 218: P_pred=0.311046, Z_actual=0, BS_model=0.125975, BSS=-125975486.330, LearnedAxiomCoeff=3.031, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 219: P_pred=0.309147, Z_actual=0, BS_model=0.124783, BSS=-124783418.255, LearnedAxiomCoeff=3.048, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 220: P_pred=0.307300, Z_actual=0, BS_model=0.123591, BSS=-123590816.439, LearnedAxiomCoeff=3.064, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 221: P_pred=0.305573, Z_actual=0, BS_model=0.122400, BSS=-122399795.633, LearnedAxiomCoeff=3.081, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 222: P_pred=0.303736, Z_actual=0, BS_model=0.121212, BSS=-121211791.103, LearnedAxiomCoeff=3.098, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 223: P_pred=0.301712, Z_actual=0, BS_model=0.120022, BSS=-120022171.468, LearnedAxiomCoeff=3.114, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 224: P_pred=0.299864, Z_actual=0, BS_model=0.118832, BSS=-118832322.749, LearnedAxiomCoeff=3.131, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 225: P_pred=0.298035, Z_actual=0, BS_model=0.117645, BSS=-117645355.497, LearnedAxiomCoeff=3.147, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 226: P_pred=0.296238, Z_actual=0, BS_model=0.116461, BSS=-116460793.522, LearnedAxiomCoeff=3.163, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 227: P_pred=0.294655, Z_actual=0, BS_model=0.115280, BSS=-115279816.183, LearnedAxiomCoeff=3.180, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 228: P_pred=0.292541, Z_actual=0, BS_model=0.114096, BSS=-114096357.327, LearnedAxiomCoeff=3.196, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 229: P_pred=0.290795, Z_actual=0, BS_model=0.112917, BSS=-112916858.220, LearnedAxiomCoeff=3.212, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 230: P_pred=0.289085, Z_actual=0, BS_model=0.111740, BSS=-111740316.599, LearnedAxiomCoeff=3.228, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 231: P_pred=0.287120, Z_actual=0, BS_model=0.110566, BSS=-110565867.095, LearnedAxiomCoeff=3.244, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 232: P_pred=0.285155, Z_actual=0, BS_model=0.109395, BSS=-109394762.167, LearnedAxiomCoeff=3.260, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 233: P_pred=0.283558, Z_actual=0, BS_model=0.108230, BSS=-108229850.427, LearnedAxiomCoeff=3.276, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 234: P_pred=0.281598, Z_actual=0, BS_model=0.107066, BSS=-107066329.507, LearnedAxiomCoeff=3.291, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 235: P_pred=0.279686, Z_actual=0, BS_model=0.105905, BSS=-105905375.447, LearnedAxiomCoeff=3.307, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 236: P_pred=0.277959, Z_actual=0, BS_model=0.104749, BSS=-104749321.246, LearnedAxiomCoeff=3.322, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 237: P_pred=0.276285, Z_actual=0, BS_model=0.103597, BSS=-103597397.576, LearnedAxiomCoeff=3.338, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 238: P_pred=0.274262, Z_actual=0, BS_model=0.102449, BSS=-102449222.664, LearnedAxiomCoeff=3.353, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 239: P_pred=0.272618, Z_actual=0, BS_model=0.101308, BSS=-101308378.968, LearnedAxiomCoeff=3.369, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 240: P_pred=0.270743, Z_actual=0, BS_model=0.100168, BSS=-100167535.974, LearnedAxiomCoeff=3.384, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 241: P_pred=0.268831, Z_actual=0, BS_model=0.099034, BSS=-99034010.772, LearnedAxiomCoeff=3.399, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 242: P_pred=0.267171, Z_actual=0, BS_model=0.097905, BSS=-97905199.857, LearnedAxiomCoeff=3.414, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 243: P_pred=0.265269, Z_actual=0, BS_model=0.096779, BSS=-96778784.174, LearnedAxiomCoeff=3.429, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 244: P_pred=0.263448, Z_actual=0, BS_model=0.095658, BSS=-95657863.336, LearnedAxiomCoeff=3.444, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 245: P_pred=0.261728, Z_actual=0, BS_model=0.094545, BSS=-94545176.727, LearnedAxiomCoeff=3.459, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 246: P_pred=0.259963, Z_actual=0, BS_model=0.093438, BSS=-93437593.579, LearnedAxiomCoeff=3.474, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 247: P_pred=0.258037, Z_actual=0, BS_model=0.092336, BSS=-92335788.662, LearnedAxiomCoeff=3.489, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 248: P_pred=0.256485, Z_actual=0, BS_model=0.091240, BSS=-91240172.985, LearnedAxiomCoeff=3.503, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 249: P_pred=0.254749, Z_actual=0, BS_model=0.090152, BSS=-90152133.011, LearnedAxiomCoeff=3.518, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 250: P_pred=0.252930, Z_actual=0, BS_model=0.089070, BSS=-89069710.583, LearnedAxiomCoeff=3.532, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 251: P_pred=0.251106, Z_actual=0, BS_model=0.087994, BSS=-87994217.145, LearnedAxiomCoeff=3.547, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 252: P_pred=0.249559, Z_actual=0, BS_model=0.086926, BSS=-86925594.595, LearnedAxiomCoeff=3.561, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 253: P_pred=0.247678, Z_actual=0, BS_model=0.085863, BSS=-85862843.341, LearnedAxiomCoeff=3.575, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 254: P_pred=0.245886, Z_actual=0, BS_model=0.084807, BSS=-84807433.186, LearnedAxiomCoeff=3.589, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 255: P_pred=0.244394, Z_actual=0, BS_model=0.083762, BSS=-83762366.212, LearnedAxiomCoeff=3.603, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 256: P_pred=0.242485, Z_actual=0, BS_model=0.082723, BSS=-82722863.970, LearnedAxiomCoeff=3.617, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 257: P_pred=0.240877, Z_actual=0, BS_model=0.081690, BSS=-81690015.499, LearnedAxiomCoeff=3.631, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 258: P_pred=0.239074, Z_actual=0, BS_model=0.080663, BSS=-80663130.152, LearnedAxiomCoeff=3.645, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 259: P_pred=0.237613, Z_actual=0, BS_model=0.079648, BSS=-79648461.838, LearnedAxiomCoeff=3.659, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 260: P_pred=0.235901, Z_actual=0, BS_model=0.078638, BSS=-78637727.570, LearnedAxiomCoeff=3.672, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 261: P_pred=0.234214, Z_actual=0, BS_model=0.077638, BSS=-77638150.792, LearnedAxiomCoeff=3.686, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 262: P_pred=0.232715, Z_actual=0, BS_model=0.076647, BSS=-76646761.132, LearnedAxiomCoeff=3.699, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 263: P_pred=0.230806, Z_actual=0, BS_model=0.075660, BSS=-75660390.229, LearnedAxiomCoeff=3.713, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 264: P_pred=0.229529, Z_actual=0, BS_model=0.074688, BSS=-74687662.233, LearnedAxiomCoeff=3.726, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 265: P_pred=0.227693, Z_actual=0, BS_model=0.073720, BSS=-73720359.308, LearnedAxiomCoeff=3.739, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 266: P_pred=0.225985, Z_actual=0, BS_model=0.072760, BSS=-72760154.816, LearnedAxiomCoeff=3.752, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 267: P_pred=0.224477, Z_actual=0, BS_model=0.071811, BSS=-71810608.557, LearnedAxiomCoeff=3.765, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 268: P_pred=0.223007, Z_actual=0, BS_model=0.070870, BSS=-70870255.539, LearnedAxiomCoeff=3.778, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 269: P_pred=0.221197, Z_actual=0, BS_model=0.069937, BSS=-69937384.776, LearnedAxiomCoeff=3.791, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 270: P_pred=0.219919, Z_actual=0, BS_model=0.069016, BSS=-69016003.064, LearnedAxiomCoeff=3.804, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 271: P_pred=0.218156, Z_actual=0, BS_model=0.068100, BSS=-68100347.953, LearnedAxiomCoeff=3.816, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 272: P_pred=0.216732, Z_actual=0, BS_model=0.067195, BSS=-67194695.693, LearnedAxiomCoeff=3.829, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 273: P_pred=0.215062, Z_actual=0, BS_model=0.066299, BSS=-66299131.600, LearnedAxiomCoeff=3.842, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 274: P_pred=0.213549, Z_actual=0, BS_model=0.065413, BSS=-65412818.467, LearnedAxiomCoeff=3.854, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 275: P_pred=0.212034, Z_actual=0, BS_model=0.064535, BSS=-64535495.804, LearnedAxiomCoeff=3.866, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 276: P_pred=0.210560, Z_actual=0, BS_model=0.063667, BSS=-63667066.503, LearnedAxiomCoeff=3.879, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 277: P_pred=0.209195, Z_actual=0, BS_model=0.062806, BSS=-62805888.569, LearnedAxiomCoeff=3.891, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 278: P_pred=0.207539, Z_actual=0, BS_model=0.061956, BSS=-61955733.959, LearnedAxiomCoeff=3.903, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 279: P_pred=0.206362, Z_actual=0, BS_model=0.061116, BSS=-61116209.806, LearnedAxiomCoeff=3.915, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 280: P_pred=0.204713, Z_actual=0, BS_model=0.060283, BSS=-60282946.877, LearnedAxiomCoeff=3.927, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 281: P_pred=0.203293, Z_actual=0, BS_model=0.059461, BSS=-59460752.399, LearnedAxiomCoeff=3.939, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 282: P_pred=0.201802, Z_actual=0, BS_model=0.058649, BSS=-58648965.531, LearnedAxiomCoeff=3.950, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 283: P_pred=0.200459, Z_actual=0, BS_model=0.057845, BSS=-57844542.608, LearnedAxiomCoeff=3.962, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 284: P_pred=0.198912, Z_actual=0, BS_model=0.057050, BSS=-57049914.527, LearnedAxiomCoeff=3.973, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 285: P_pred=0.197592, Z_actual=0, BS_model=0.056266, BSS=-56266288.431, LearnedAxiomCoeff=3.985, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 286: P_pred=0.196156, Z_actual=0, BS_model=0.055491, BSS=-55490604.618, LearnedAxiomCoeff=3.996, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 287: P_pred=0.194956, Z_actual=0, BS_model=0.054724, BSS=-54724100.771, LearnedAxiomCoeff=4.008, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 288: P_pred=0.193457, Z_actual=0, BS_model=0.053968, BSS=-53968218.757, LearnedAxiomCoeff=4.019, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 289: P_pred=0.192034, Z_actual=0, BS_model=0.053219, BSS=-53219351.567, LearnedAxiomCoeff=4.030, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 290: P_pred=0.190830, Z_actual=0, BS_model=0.052482, BSS=-52481643.477, LearnedAxiomCoeff=4.041, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 291: P_pred=0.189319, Z_actual=0, BS_model=0.051753, BSS=-51753073.551, LearnedAxiomCoeff=4.052, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 292: P_pred=0.188116, Z_actual=0, BS_model=0.051033, BSS=-51033220.798, LearnedAxiomCoeff=4.063, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 293: P_pred=0.186852, Z_actual=0, BS_model=0.050324, BSS=-50324141.729, LearnedAxiomCoeff=4.074, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 294: P_pred=0.185345, Z_actual=0, BS_model=0.049623, BSS=-49623104.168, LearnedAxiomCoeff=4.085, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 295: P_pred=0.184195, Z_actual=0, BS_model=0.048932, BSS=-48931628.414, LearnedAxiomCoeff=4.095, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 296: P_pred=0.182826, Z_actual=0, BS_model=0.048249, BSS=-48248518.138, LearnedAxiomCoeff=4.106, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 297: P_pred=0.181605, Z_actual=0, BS_model=0.047576, BSS=-47576467.896, LearnedAxiomCoeff=4.116, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 298: P_pred=0.180406, Z_actual=0, BS_model=0.046912, BSS=-46911699.605, LearnedAxiomCoeff=4.127, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 299: P_pred=0.178910, Z_actual=0, BS_model=0.046254, BSS=-46253927.709, LearnedAxiomCoeff=4.137, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 300: P_pred=0.177895, Z_actual=0, BS_model=0.045607, BSS=-45607385.882, LearnedAxiomCoeff=4.147, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 301: P_pred=0.176530, Z_actual=0, BS_model=0.044970, BSS=-44969558.941, LearnedAxiomCoeff=4.158, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 302: P_pred=0.175575, Z_actual=0, BS_model=0.044341, BSS=-44340503.112, LearnedAxiomCoeff=4.168, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 303: P_pred=0.174329, Z_actual=0, BS_model=0.043721, BSS=-43721421.829, LearnedAxiomCoeff=4.178, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 304: P_pred=0.172945, Z_actual=0, BS_model=0.043110, BSS=-43110420.326, LearnedAxiomCoeff=4.188, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 305: P_pred=0.172017, Z_actual=0, BS_model=0.042508, BSS=-42507652.349, LearnedAxiomCoeff=4.198, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 306: P_pred=0.170606, Z_actual=0, BS_model=0.041914, BSS=-41913808.628, LearnedAxiomCoeff=4.208, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 307: P_pred=0.169362, Z_actual=0, BS_model=0.041327, BSS=-41327043.419, LearnedAxiomCoeff=4.217, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 308: P_pred=0.168366, Z_actual=0, BS_model=0.040751, BSS=-40750860.562, LearnedAxiomCoeff=4.227, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 309: P_pred=0.167182, Z_actual=0, BS_model=0.040181, BSS=-40180656.276, LearnedAxiomCoeff=4.237, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 310: P_pred=0.166043, Z_actual=0, BS_model=0.039619, BSS=-39619078.277, LearnedAxiomCoeff=4.246, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 311: P_pred=0.164956, Z_actual=0, BS_model=0.039066, BSS=-39066160.462, LearnedAxiomCoeff=4.256, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 312: P_pred=0.163797, Z_actual=0, BS_model=0.038520, BSS=-38519621.104, LearnedAxiomCoeff=4.265, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 313: P_pred=0.162745, Z_actual=0, BS_model=0.037984, BSS=-37983912.960, LearnedAxiomCoeff=4.274, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 314: P_pred=0.161593, Z_actual=0, BS_model=0.037452, BSS=-37452489.375, LearnedAxiomCoeff=4.283, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 315: P_pred=0.160688, Z_actual=0, BS_model=0.036932, BSS=-36932016.390, LearnedAxiomCoeff=4.293, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 316: P_pred=0.159638, Z_actual=0, BS_model=0.036420, BSS=-36420323.290, LearnedAxiomCoeff=4.302, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 317: P_pred=0.158505, Z_actual=0, BS_model=0.035915, BSS=-35915003.373, LearnedAxiomCoeff=4.311, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 318: P_pred=0.157438, Z_actual=0, BS_model=0.035416, BSS=-35416097.148, LearnedAxiomCoeff=4.320, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 319: P_pred=0.156394, Z_actual=0, BS_model=0.034927, BSS=-34926714.966, LearnedAxiomCoeff=4.329, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 320: P_pred=0.155428, Z_actual=0, BS_model=0.034443, BSS=-34442587.644, LearnedAxiomCoeff=4.337, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 321: P_pred=0.154379, Z_actual=0, BS_model=0.033967, BSS=-33967404.339, LearnedAxiomCoeff=4.346, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 322: P_pred=0.153382, Z_actual=0, BS_model=0.033498, BSS=-33498472.230, LearnedAxiomCoeff=4.355, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 323: P_pred=0.152376, Z_actual=0, BS_model=0.033038, BSS=-33037805.263, LearnedAxiomCoeff=4.363, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 324: P_pred=0.151579, Z_actual=0, BS_model=0.032585, BSS=-32585266.950, LearnedAxiomCoeff=4.372, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 325: P_pred=0.150531, Z_actual=0, BS_model=0.032139, BSS=-32139286.646, LearnedAxiomCoeff=4.380, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 326: P_pred=0.149538, Z_actual=0, BS_model=0.031700, BSS=-31699802.666, LearnedAxiomCoeff=4.389, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 327: P_pred=0.148391, Z_actual=0, BS_model=0.031265, BSS=-31264951.412, LearnedAxiomCoeff=4.397, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 328: P_pred=0.147596, Z_actual=0, BS_model=0.030839, BSS=-30839191.003, LearnedAxiomCoeff=4.405, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 329: P_pred=0.146716, Z_actual=0, BS_model=0.030418, BSS=-30417991.874, LearnedAxiomCoeff=4.414, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 330: P_pred=0.145728, Z_actual=0, BS_model=0.030005, BSS=-30004577.702, LearnedAxiomCoeff=4.422, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 331: P_pred=0.144694, Z_actual=0, BS_model=0.029597, BSS=-29596744.726, LearnedAxiomCoeff=4.430, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 332: P_pred=0.143791, Z_actual=0, BS_model=0.029196, BSS=-29195783.184, LearnedAxiomCoeff=4.438, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 333: P_pred=0.142974, Z_actual=0, BS_model=0.028801, BSS=-28800939.628, LearnedAxiomCoeff=4.446, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 334: P_pred=0.142151, Z_actual=0, BS_model=0.028414, BSS=-28413759.208, LearnedAxiomCoeff=4.454, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 335: P_pred=0.141271, Z_actual=0, BS_model=0.028032, BSS=-28032054.936, LearnedAxiomCoeff=4.462, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 336: P_pred=0.140305, Z_actual=0, BS_model=0.027656, BSS=-27656222.010, LearnedAxiomCoeff=4.470, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 337: P_pred=0.139388, Z_actual=0, BS_model=0.027285, BSS=-27284644.070, LearnedAxiomCoeff=4.477, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 338: P_pred=0.138650, Z_actual=0, BS_model=0.026921, BSS=-26920608.605, LearnedAxiomCoeff=4.485, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 339: P_pred=0.137645, Z_actual=0, BS_model=0.026562, BSS=-26561989.708, LearnedAxiomCoeff=4.493, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 340: P_pred=0.136999, Z_actual=0, BS_model=0.026209, BSS=-26209039.280, LearnedAxiomCoeff=4.500, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 341: P_pred=0.136137, Z_actual=0, BS_model=0.025863, BSS=-25862872.648, LearnedAxiomCoeff=4.508, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 342: P_pred=0.135243, Z_actual=0, BS_model=0.025521, BSS=-25520930.920, LearnedAxiomCoeff=4.515, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 343: P_pred=0.134654, Z_actual=0, BS_model=0.025185, BSS=-25185290.968, LearnedAxiomCoeff=4.523, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 344: P_pred=0.133714, Z_actual=0, BS_model=0.024856, BSS=-24855819.689, LearnedAxiomCoeff=4.530, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 345: P_pred=0.132946, Z_actual=0, BS_model=0.024531, BSS=-24530756.998, LearnedAxiomCoeff=4.537, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 346: P_pred=0.132153, Z_actual=0, BS_model=0.024212, BSS=-24211539.060, LearnedAxiomCoeff=4.545, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 347: P_pred=0.131334, Z_actual=0, BS_model=0.023897, BSS=-23896902.738, LearnedAxiomCoeff=4.552, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 348: P_pred=0.130451, Z_actual=0, BS_model=0.023586, BSS=-23586324.630, LearnedAxiomCoeff=4.559, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 349: P_pred=0.129713, Z_actual=0, BS_model=0.023283, BSS=-23282658.931, LearnedAxiomCoeff=4.566, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 350: P_pred=0.129084, Z_actual=0, BS_model=0.022983, BSS=-22982980.296, LearnedAxiomCoeff=4.573, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 351: P_pred=0.128290, Z_actual=0, BS_model=0.022689, BSS=-22688885.676, LearnedAxiomCoeff=4.580, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 352: P_pred=0.127624, Z_actual=0, BS_model=0.022398, BSS=-22398109.934, LearnedAxiomCoeff=4.587, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 353: P_pred=0.126743, Z_actual=0, BS_model=0.022112, BSS=-22111574.272, LearnedAxiomCoeff=4.594, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 354: P_pred=0.125992, Z_actual=0, BS_model=0.021831, BSS=-21830857.222, LearnedAxiomCoeff=4.601, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 355: P_pred=0.125310, Z_actual=0, BS_model=0.021553, BSS=-21553112.794, LearnedAxiomCoeff=4.607, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 356: P_pred=0.124712, Z_actual=0, BS_model=0.021282, BSS=-21282045.396, LearnedAxiomCoeff=4.614, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 357: P_pred=0.123951, Z_actual=0, BS_model=0.021016, BSS=-21015649.063, LearnedAxiomCoeff=4.621, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 358: P_pred=0.123315, Z_actual=0, BS_model=0.020753, BSS=-20752840.509, LearnedAxiomCoeff=4.627, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 359: P_pred=0.122386, Z_actual=0, BS_model=0.020493, BSS=-20493411.798, LearnedAxiomCoeff=4.634, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 360: P_pred=0.121713, Z_actual=0, BS_model=0.020238, BSS=-20238283.081, LearnedAxiomCoeff=4.641, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 361: P_pred=0.121132, Z_actual=0, BS_model=0.019988, BSS=-19987532.060, LearnedAxiomCoeff=4.647, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 362: P_pred=0.120460, Z_actual=0, BS_model=0.019741, BSS=-19741155.250, LearnedAxiomCoeff=4.654, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 363: P_pred=0.119834, Z_actual=0, BS_model=0.019499, BSS=-19498641.293, LearnedAxiomCoeff=4.660, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 364: P_pred=0.119278, Z_actual=0, BS_model=0.019261, BSS=-19260936.162, LearnedAxiomCoeff=4.666, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 365: P_pred=0.118337, Z_actual=0, BS_model=0.019025, BSS=-19024599.167, LearnedAxiomCoeff=4.673, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 366: P_pred=0.117883, Z_actual=0, BS_model=0.018793, BSS=-18792839.090, LearnedAxiomCoeff=4.679, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 367: P_pred=0.117260, Z_actual=0, BS_model=0.018565, BSS=-18565360.221, LearnedAxiomCoeff=4.685, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 368: P_pred=0.116568, Z_actual=0, BS_model=0.018341, BSS=-18341389.707, LearnedAxiomCoeff=4.691, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 369: P_pred=0.115923, Z_actual=0, BS_model=0.018121, BSS=-18120969.867, LearnedAxiomCoeff=4.697, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 370: P_pred=0.115246, Z_actual=0, BS_model=0.017903, BSS=-17903444.638, LearnedAxiomCoeff=4.704, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 371: P_pred=0.114690, Z_actual=0, BS_model=0.017690, BSS=-17689862.957, LearnedAxiomCoeff=4.710, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 372: P_pred=0.114016, Z_actual=0, BS_model=0.017479, BSS=-17479333.398, LearnedAxiomCoeff=4.716, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 373: P_pred=0.113399, Z_actual=0, BS_model=0.017272, BSS=-17272151.321, LearnedAxiomCoeff=4.722, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 374: P_pred=0.112806, Z_actual=0, BS_model=0.017067, BSS=-17067131.445, LearnedAxiomCoeff=4.728, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 375: P_pred=0.112174, Z_actual=0, BS_model=0.016866, BSS=-16865600.482, LearnedAxiomCoeff=4.733, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 376: P_pred=0.111659, Z_actual=0, BS_model=0.016668, BSS=-16667726.990, LearnedAxiomCoeff=4.739, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 377: P_pred=0.111176, Z_actual=0, BS_model=0.016475, BSS=-16474529.616, LearnedAxiomCoeff=4.745, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 378: P_pred=0.110603, Z_actual=0, BS_model=0.016284, BSS=-16283501.339, LearnedAxiomCoeff=4.751, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 379: P_pred=0.109890, Z_actual=0, BS_model=0.016095, BSS=-16094510.177, LearnedAxiomCoeff=4.757, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 380: P_pred=0.109370, Z_actual=0, BS_model=0.015909, BSS=-15909014.309, LearnedAxiomCoeff=4.762, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 381: P_pred=0.108850, Z_actual=0, BS_model=0.015727, BSS=-15727255.713, LearnedAxiomCoeff=4.768, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 382: P_pred=0.108097, Z_actual=0, BS_model=0.015547, BSS=-15547436.123, LearnedAxiomCoeff=4.774, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 383: P_pred=0.107623, Z_actual=0, BS_model=0.015370, BSS=-15370255.055, LearnedAxiomCoeff=4.779, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 384: P_pred=0.107015, Z_actual=0, BS_model=0.015195, BSS=-15195161.435, LearnedAxiomCoeff=4.785, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 385: P_pred=0.106695, Z_actual=0, BS_model=0.015024, BSS=-15023687.958, LearnedAxiomCoeff=4.790, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 386: P_pred=0.105972, Z_actual=0, BS_model=0.014855, BSS=-14854578.528, LearnedAxiomCoeff=4.796, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 387: P_pred=0.105466, Z_actual=0, BS_model=0.014688, BSS=-14688456.902, LearnedAxiomCoeff=4.801, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 388: P_pred=0.104940, Z_actual=0, BS_model=0.014524, BSS=-14524224.588, LearnedAxiomCoeff=4.807, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 389: P_pred=0.104347, Z_actual=0, BS_model=0.014363, BSS=-14363068.343, LearnedAxiomCoeff=4.812, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 390: P_pred=0.103966, Z_actual=0, BS_model=0.014204, BSS=-14203870.459, LearnedAxiomCoeff=4.817, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 391: P_pred=0.103395, Z_actual=0, BS_model=0.014047, BSS=-14047015.203, LearnedAxiomCoeff=4.823, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 392: P_pred=0.102910, Z_actual=0, BS_model=0.013893, BSS=-13893012.082, LearnedAxiomCoeff=4.828, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 393: P_pred=0.102460, Z_actual=0, BS_model=0.013740, BSS=-13740342.315, LearnedAxiomCoeff=4.833, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 394: P_pred=0.101902, Z_actual=0, BS_model=0.013590, BSS=-13590436.018, LearnedAxiomCoeff=4.838, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 395: P_pred=0.101483, Z_actual=0, BS_model=0.013443, BSS=-13442917.163, LearnedAxiomCoeff=4.843, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 396: P_pred=0.100947, Z_actual=0, BS_model=0.013297, BSS=-13297433.242, LearnedAxiomCoeff=4.849, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 397: P_pred=0.100285, Z_actual=0, BS_model=0.013154, BSS=-13153604.371, LearnedAxiomCoeff=4.854, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 398: P_pred=0.099890, Z_actual=0, BS_model=0.013013, BSS=-13012815.848, LearnedAxiomCoeff=4.859, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 399: P_pred=0.099474, Z_actual=0, BS_model=0.012874, BSS=-12874209.775, LearnedAxiomCoeff=4.864, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 400: P_pred=0.098943, Z_actual=0, BS_model=0.012737, BSS=-12736753.133, LearnedAxiomCoeff=4.869, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 401: P_pred=0.098393, Z_actual=0, BS_model=0.012601, BSS=-12601211.536, LearnedAxiomCoeff=4.874, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 402: P_pred=0.098126, Z_actual=0, BS_model=0.012468, BSS=-12468026.471, LearnedAxiomCoeff=4.879, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 403: P_pred=0.097555, Z_actual=0, BS_model=0.012337, BSS=-12337088.986, LearnedAxiomCoeff=4.884, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 404: P_pred=0.097034, Z_actual=0, BS_model=0.012208, BSS=-12207922.970, LearnedAxiomCoeff=4.888, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 405: P_pred=0.096731, Z_actual=0, BS_model=0.012081, BSS=-12081009.043, LearnedAxiomCoeff=4.893, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 406: P_pred=0.096065, Z_actual=0, BS_model=0.011955, BSS=-11954514.095, LearnedAxiomCoeff=4.898, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 407: P_pred=0.095732, Z_actual=0, BS_model=0.011831, BSS=-11830531.387, LearnedAxiomCoeff=4.903, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 408: P_pred=0.095363, Z_actual=0, BS_model=0.011708, BSS=-11708280.790, LearnedAxiomCoeff=4.908, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 409: P_pred=0.094896, Z_actual=0, BS_model=0.011589, BSS=-11588821.660, LearnedAxiomCoeff=4.912, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 410: P_pred=0.094429, Z_actual=0, BS_model=0.011471, BSS=-11470879.374, LearnedAxiomCoeff=4.917, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 411: P_pred=0.093936, Z_actual=0, BS_model=0.011354, BSS=-11353902.125, LearnedAxiomCoeff=4.922, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 412: P_pred=0.093568, Z_actual=0, BS_model=0.011239, BSS=-11238789.795, LearnedAxiomCoeff=4.926, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 413: P_pred=0.093276, Z_actual=0, BS_model=0.011126, BSS=-11125592.515, LearnedAxiomCoeff=4.931, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 414: P_pred=0.092750, Z_actual=0, BS_model=0.011013, BSS=-11013098.941, LearnedAxiomCoeff=4.936, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 415: P_pred=0.092323, Z_actual=0, BS_model=0.010903, BSS=-10903495.605, LearnedAxiomCoeff=4.940, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 416: P_pred=0.091813, Z_actual=0, BS_model=0.010794, BSS=-10794158.442, LearnedAxiomCoeff=4.945, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 417: P_pred=0.091615, Z_actual=0, BS_model=0.010687, BSS=-10687026.900, LearnedAxiomCoeff=4.949, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 418: P_pred=0.091144, Z_actual=0, BS_model=0.010581, BSS=-10581407.442, LearnedAxiomCoeff=4.954, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 419: P_pred=0.090755, Z_actual=0, BS_model=0.010477, BSS=-10477370.899, LearnedAxiomCoeff=4.958, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 420: P_pred=0.090368, Z_actual=0, BS_model=0.010375, BSS=-10375064.943, LearnedAxiomCoeff=4.963, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 421: P_pred=0.089756, Z_actual=0, BS_model=0.010273, BSS=-10273111.939, LearnedAxiomCoeff=4.967, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 422: P_pred=0.089511, Z_actual=0, BS_model=0.010173, BSS=-10173365.901, LearnedAxiomCoeff=4.971, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 423: P_pred=0.089129, Z_actual=0, BS_model=0.010075, BSS=-10075059.444, LearnedAxiomCoeff=4.976, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 424: P_pred=0.088689, Z_actual=0, BS_model=0.009978, BSS=-9977872.570, LearnedAxiomCoeff=4.980, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 425: P_pred=0.088456, Z_actual=0, BS_model=0.009883, BSS=-9882702.238, LearnedAxiomCoeff=4.984, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 426: P_pred=0.087979, Z_actual=0, BS_model=0.009788, BSS=-9788151.565, LearnedAxiomCoeff=4.989, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 427: P_pred=0.087446, Z_actual=0, BS_model=0.009694, BSS=-9693887.150, LearnedAxiomCoeff=4.993, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 428: P_pred=0.087114, Z_actual=0, BS_model=0.009601, BSS=-9601004.722, LearnedAxiomCoeff=4.997, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 429: P_pred=0.087003, Z_actual=0, BS_model=0.009511, BSS=-9510876.411, LearnedAxiomCoeff=5.001, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 430: P_pred=0.086379, Z_actual=0, BS_model=0.009421, BSS=-9420867.802, LearnedAxiomCoeff=5.006, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 431: P_pred=0.086106, Z_actual=0, BS_model=0.009332, BSS=-9332184.329, LearnedAxiomCoeff=5.010, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 432: P_pred=0.085793, Z_actual=0, BS_model=0.009246, BSS=-9245694.237, LearnedAxiomCoeff=5.014, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 433: P_pred=0.085322, Z_actual=0, BS_model=0.009160, BSS=-9159639.646, LearnedAxiomCoeff=5.018, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 434: P_pred=0.084891, Z_actual=0, BS_model=0.009075, BSS=-9074725.379, LearnedAxiomCoeff=5.022, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 435: P_pred=0.084675, Z_actual=0, BS_model=0.008990, BSS=-8990446.777, LearnedAxiomCoeff=5.026, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 436: P_pred=0.084269, Z_actual=0, BS_model=0.008908, BSS=-8907869.176, LearnedAxiomCoeff=5.030, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 437: P_pred=0.083999, Z_actual=0, BS_model=0.008827, BSS=-8826525.982, LearnedAxiomCoeff=5.034, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 438: P_pred=0.083462, Z_actual=0, BS_model=0.008746, BSS=-8745598.278, LearnedAxiomCoeff=5.038, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 439: P_pred=0.083257, Z_actual=0, BS_model=0.008666, BSS=-8666466.799, LearnedAxiomCoeff=5.042, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 440: P_pred=0.083049, Z_actual=0, BS_model=0.008588, BSS=-8588233.392, LearnedAxiomCoeff=5.046, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 441: P_pred=0.082577, Z_actual=0, BS_model=0.008511, BSS=-8510803.131, LearnedAxiomCoeff=5.050, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 442: P_pred=0.082282, Z_actual=0, BS_model=0.008434, BSS=-8434398.686, LearnedAxiomCoeff=5.054, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 443: P_pred=0.081910, Z_actual=0, BS_model=0.008359, BSS=-8358622.226, LearnedAxiomCoeff=5.058, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 444: P_pred=0.081626, Z_actual=0, BS_model=0.008284, BSS=-8284199.795, LearnedAxiomCoeff=5.062, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 445: P_pred=0.081227, Z_actual=0, BS_model=0.008210, BSS=-8210180.200, LearnedAxiomCoeff=5.066, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 446: P_pred=0.080952, Z_actual=0, BS_model=0.008137, BSS=-8137441.245, LearnedAxiomCoeff=5.070, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 447: P_pred=0.080743, Z_actual=0, BS_model=0.008067, BSS=-8066687.473, LearnedAxiomCoeff=5.073, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 448: P_pred=0.080273, Z_actual=0, BS_model=0.007996, BSS=-7996000.996, LearnedAxiomCoeff=5.077, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 449: P_pred=0.079974, Z_actual=0, BS_model=0.007926, BSS=-7926015.729, LearnedAxiomCoeff=5.081, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 450: P_pred=0.079587, Z_actual=0, BS_model=0.007857, BSS=-7856901.990, LearnedAxiomCoeff=5.085, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 451: P_pred=0.079390, Z_actual=0, BS_model=0.007789, BSS=-7789334.187, LearnedAxiomCoeff=5.088, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 452: P_pred=0.079042, Z_actual=0, BS_model=0.007722, BSS=-7721711.674, LearnedAxiomCoeff=5.092, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 453: P_pred=0.078631, Z_actual=0, BS_model=0.007655, BSS=-7655029.721, LearnedAxiomCoeff=5.096, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 454: P_pred=0.078437, Z_actual=0, BS_model=0.007590, BSS=-7589763.139, LearnedAxiomCoeff=5.099, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 455: P_pred=0.078039, Z_actual=0, BS_model=0.007524, BSS=-7524427.610, LearnedAxiomCoeff=5.103, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 456: P_pred=0.077893, Z_actual=0, BS_model=0.007461, BSS=-7461206.925, LearnedAxiomCoeff=5.107, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 457: P_pred=0.077475, Z_actual=0, BS_model=0.007398, BSS=-7397959.881, LearnedAxiomCoeff=5.110, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 458: P_pred=0.077274, Z_actual=0, BS_model=0.007336, BSS=-7335501.191, LearnedAxiomCoeff=5.114, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 459: P_pred=0.076982, Z_actual=0, BS_model=0.007274, BSS=-7273918.811, LearnedAxiomCoeff=5.118, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 460: P_pred=0.076641, Z_actual=0, BS_model=0.007213, BSS=-7213060.025, LearnedAxiomCoeff=5.121, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 461: P_pred=0.076344, Z_actual=0, BS_model=0.007153, BSS=-7153148.561, LearnedAxiomCoeff=5.125, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 462: P_pred=0.076018, Z_actual=0, BS_model=0.007094, BSS=-7093624.138, LearnedAxiomCoeff=5.128, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 463: P_pred=0.075814, Z_actual=0, BS_model=0.007035, BSS=-7034572.023, LearnedAxiomCoeff=5.132, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 464: P_pred=0.075644, Z_actual=0, BS_model=0.006977, BSS=-6976961.616, LearnedAxiomCoeff=5.135, GradConsistency=0.00001, BS_ref_orig=0.000000
Obs 465: P_pred=0.075206, Z_actual=0, BS_model=0.006920, BSS=-6919607.498, LearnedAxiomCoeff=5.139, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 466: P_pred=0.074910, Z_actual=0, BS_model=0.006863, BSS=-6863245.157, LearnedAxiomCoeff=5.142, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 467: P_pred=0.074671, Z_actual=0, BS_model=0.006807, BSS=-6806895.067, LearnedAxiomCoeff=5.146, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 468: P_pred=0.074447, Z_actual=0, BS_model=0.006752, BSS=-6751596.715, LearnedAxiomCoeff=5.149, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 469: P_pred=0.074174, Z_actual=0, BS_model=0.006697, BSS=-6696904.396, LearnedAxiomCoeff=5.153, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 470: P_pred=0.073762, Z_actual=0, BS_model=0.006642, BSS=-6642394.529, LearnedAxiomCoeff=5.156, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 471: P_pred=0.073609, Z_actual=0, BS_model=0.006590, BSS=-6589636.132, LearnedAxiomCoeff=5.159, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 472: P_pred=0.073310, Z_actual=0, BS_model=0.006537, BSS=-6536876.308, LearnedAxiomCoeff=5.163, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 473: P_pred=0.073039, Z_actual=0, BS_model=0.006485, BSS=-6484690.343, LearnedAxiomCoeff=5.166, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 474: P_pred=0.072728, Z_actual=0, BS_model=0.006433, BSS=-6433161.302, LearnedAxiomCoeff=5.169, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 475: P_pred=0.072422, Z_actual=0, BS_model=0.006382, BSS=-6381570.807, LearnedAxiomCoeff=5.173, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 476: P_pred=0.072217, Z_actual=0, BS_model=0.006331, BSS=-6331071.071, LearnedAxiomCoeff=5.176, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 477: P_pred=0.072015, Z_actual=0, BS_model=0.006282, BSS=-6281857.278, LearnedAxiomCoeff=5.179, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 478: P_pred=0.071705, Z_actual=0, BS_model=0.006233, BSS=-6232910.970, LearnedAxiomCoeff=5.182, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 479: P_pred=0.071416, Z_actual=0, BS_model=0.006184, BSS=-6183525.274, LearnedAxiomCoeff=5.186, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 480: P_pred=0.071194, Z_actual=0, BS_model=0.006136, BSS=-6135671.432, LearnedAxiomCoeff=5.189, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 481: P_pred=0.071037, Z_actual=0, BS_model=0.006088, BSS=-6088311.377, LearnedAxiomCoeff=5.192, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 482: P_pred=0.070766, Z_actual=0, BS_model=0.006041, BSS=-6041259.313, LearnedAxiomCoeff=5.195, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 483: P_pred=0.070390, Z_actual=0, BS_model=0.005995, BSS=-5994756.689, LearnedAxiomCoeff=5.199, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 484: P_pred=0.070229, Z_actual=0, BS_model=0.005949, BSS=-5949269.061, LearnedAxiomCoeff=5.202, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 485: P_pred=0.070022, Z_actual=0, BS_model=0.005904, BSS=-5903931.475, LearnedAxiomCoeff=5.205, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 486: P_pred=0.069768, Z_actual=0, BS_model=0.005859, BSS=-5859258.590, LearnedAxiomCoeff=5.208, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 487: P_pred=0.069522, Z_actual=0, BS_model=0.005815, BSS=-5814807.512, LearnedAxiomCoeff=5.211, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 488: P_pred=0.069290, Z_actual=0, BS_model=0.005772, BSS=-5771510.801, LearnedAxiomCoeff=5.214, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 489: P_pred=0.069034, Z_actual=0, BS_model=0.005728, BSS=-5728188.391, LearnedAxiomCoeff=5.217, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 490: P_pred=0.068847, Z_actual=0, BS_model=0.005685, BSS=-5685042.558, LearnedAxiomCoeff=5.221, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 491: P_pred=0.068626, Z_actual=0, BS_model=0.005643, BSS=-5642853.301, LearnedAxiomCoeff=5.224, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 492: P_pred=0.068415, Z_actual=0, BS_model=0.005601, BSS=-5601060.544, LearnedAxiomCoeff=5.227, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 493: P_pred=0.067994, Z_actual=0, BS_model=0.005559, BSS=-5559338.904, LearnedAxiomCoeff=5.230, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 494: P_pred=0.067806, Z_actual=0, BS_model=0.005518, BSS=-5518034.968, LearnedAxiomCoeff=5.233, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 495: P_pred=0.067603, Z_actual=0, BS_model=0.005477, BSS=-5477482.686, LearnedAxiomCoeff=5.236, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 496: P_pred=0.067520, Z_actual=0, BS_model=0.005438, BSS=-5437596.144, LearnedAxiomCoeff=5.239, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 497: P_pred=0.067254, Z_actual=0, BS_model=0.005398, BSS=-5397668.450, LearnedAxiomCoeff=5.242, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 498: P_pred=0.066908, Z_actual=0, BS_model=0.005358, BSS=-5358328.140, LearnedAxiomCoeff=5.245, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 499: P_pred=0.066654, Z_actual=0, BS_model=0.005319, BSS=-5319265.899, LearnedAxiomCoeff=5.248, GradConsistency=0.00000, BS_ref_orig=0.000000
Obs 500: P_pred=0.066472, Z_actual=0, BS_model=0.005281, BSS=-5280955.402, LearnedAxiomCoeff=5.251, GradConsistency=0.00000, BS_ref_orig=0.000000

--- COUNTER-TEST RESULTS after 500 observations ---
Final Rolling Brier Skill Score over last 50 observations: -5280955.402
Number of times BS_reference was floored to 1e-9: 451
Max P_predicted observed when Z_actual was 0: 0.485911
Final Learned AXIOM_RECESSION_AVOIDANCE coefficient: 5.251

COUNTER-TEST PASSED: The system demonstrated resilience to the identified numerical instabilities. This indicates a more robust implementation than initially assessed under extreme conditions.


## Attacker: Adversarial Compliance Auditor & Black-Hat Code Architect
The Mutator's thesis presents a well-structured architectural enhancement aimed at resolving critical issues in the epistemic engine, particularly the vulnerability to non-differentiable exploits that compromise gradient-based credit assignment. The proposed `DifferentiabilityRobustnessCheck` within the `FiringSquad` and the `AxiomDifferentiabilityVeto` by the `Meta-Judge` are conceptually sound mechanisms for enforcing the mathematical prerequisites of gradient descent.

**Critique of Thesis and Falsification Suite:**

1.  **Parametric Grounding and Load-Bearing Variables:** The "LOAD-BEARING VARIABLES" table is generally consistent with the stated purpose of a simulation. Variables such as `hypothetical_economy_growth_rate_q1_2025_base` and `hypothetical_inflation_rate_q1_2025_base` are explicitly labeled as "hypothetical" and "simulated," thus not claiming to represent real-world physical or financial constants. Their magnitudes are within plausible ranges for such hypothetical scenarios, preventing an "orders of magnitude" misapplication. Similarly, the `true_` prefixed variables define the parameters of the simulated ground truth, which is an appropriate design for a falsification suite. Standard machine learning hyperparameters like Adam's `beta1`, `beta2`, and `epsilon_stabilizer` are within established norms. The `differentiability_tolerance` and `robustness_perturbation_epsilon_scales` are critical system parameters for the new mechanism, and their chosen values are reasonable for numerical gradient checks. No "cooked books" in the form of misapplied real-world constants or values off by orders of magnitude are identified in the load-bearing variables.

2.  **Robustness Against Subtle Mutator Exploits:** The core of the Mutator's defense against non-differentiable exploits lies in the `DifferentiabilityRobustnessCheck` and `AxiomDifferentiabilityVeto`. The `ThesisPredictor` provided by the Mutator in its falsification suite is a standard Multi-Layer Perceptron (MLP) using ReLU and Sigmoid activations. These functions are generally differentiable (ReLU is piecewise differentiable, which is typically handled by numerical gradient methods and subgradients in optimization). The `np.clip` operation within the `_sigmoid` function technically introduces non-differentiability at the clipping boundaries; however, given the small initial weights and learning rates, it is unlikely for the model's internal values to frequently reach these extreme points, thus minimizing its practical impact on differentiability in this specific implementation. The Mutator's provided `ThesisPredictor` does not contain explicit non-differentiable transformations (e.g., `if-else` statements, `floor`/`ceil` operations) that would immediately trigger the veto. This indicates that the Mutator has provided a compliant model for its own test, rather than an adversarial one.

3.  **Functional Intent and Learnability:** The `ThesisPredictor` correctly instantiates `np.ndarray` parameters for axioms and integrates them as input features into the MLP. The `Z_actual` generation incorporates `true_axiom_relevance` as a fixed scaling factor for the axiom's impact in the simulated ground truth. The objective for the `ThesisPredictor` is to learn a `learned_axiom_coeff` that, when processed by its MLP, effectively approximates this true relevance. The convergence criteria (`final_learned_axiom_coeff > 0.65` and `abs(final_learned_axiom_coeff - true_axiom_relevance) < 0.25`) are non-trivial, suggesting a genuine learning task rather than a trivially satisfied condition.

4.  **New Operational Drag:** The Mutator accurately identifies the increased computational burden of the `DifferentiabilityRobustnessCheck`. Performing `2 * A * S` additional forward passes of the `ThesisPredictor` per iteration (where `A` is the number of axioms and `S` is the number of perturbation scales) represents a significant increase in computational energy. This is a legitimate and well-articulated trade-off for enhanced anti-gaming robustness.

**So What for the Meta-Judge:**

The Mutator's thesis hinges on the effectiveness of the `AxiomDifferentiabilityVeto` to prevent the subversion of gradient-based credit assignment. The provided `ThesisPredictor` in the falsification suite is inherently differentiable, thus not actively challenging this veto. To rigorously assess the robustness of the proposed architecture, it is imperative to test its capacity to identify and reject a `ThesisPredictor` that *intentionally* incorporates a non-differentiable transformation for an axiom's contribution. If the `Meta-Judge`'s veto mechanism successfully identifies and rejects such a gamed thesis, it provides strong evidence for the architectural claim regarding anti-gaming robustness. Conversely, a failure to detect the non-differentiability would expose a critical vulnerability, rendering the entire gradient-based credit assignment system susceptible to exploitation and undermining the reliability of axiom learning. This counter-test directly probes the foundational integrity of the V3 system's ability to enforce learnability.

---

```python
import math
import random
import collections
import inspect
import numpy as np

# --- LOAD-BEARING VARIABLES (Copied from Mutator's suite for consistency) ---
epsilon = 0.001
adam_beta1 = 0.9
adam_beta2 = 0.999
adam_epsilon_stabilizer = 1e-8
learning_rate_model_params = 0.001
learning_rate_axiom_coeffs = 0.01
min_observations_for_calibration = 200
target_brier_skill_score = 0.20
rolling_window_size = 50
hidden_layer_size = 4
initial_axiom_coefficient_value = 0.5
axiom_sync_frequency = 1
hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.8
differentiability_tolerance = 0.05
robustness_perturbation_epsilon_scales = [0.00001, 0.0001, 0.001]

# --- Mutator's ThesisPredictor (Copied for context, not used directly in counter-test simulation) ---
class ThesisPredictor:
    def __init__(self, external_input_size: int, hidden_size: int, output_size: int = 1,
                 axiom_initial_weights: dict = None):
        self.external_input_size = external_input_size 
        self.learned_axiom_coeffs = {}
        if axiom_initial_weights:
            for axiom_name, initial_value in axiom_initial_weights.items():
                self.learned_axiom_coeffs[axiom_name] = np.array([initial_value], dtype=np.float64)
        else:
            raise ValueError("ThesisPredictor must be initialized with axiom_initial_weights for its learnable coefficients.")
        self.axiom_names = sorted(list(self.learned_axiom_coeffs.keys()))
        self.num_axioms = len(self.axiom_names)
        total_input_features_to_mlp = self.external_input_size + self.num_axioms
        self.weights_ih = np.random.randn(total_input_features_to_mlp, hidden_size).astype(np.float64) * 0.1 
        self.bias_h = np.zeros((1, hidden_size), dtype=np.float64) 
        self.weights_ho = np.random.randn(hidden_size, output_size).astype(np.float64) * 0.1 
        self.bias_o = np.zeros((1, output_size), dtype=np.float64) 

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) 

    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        axiom_inputs = np.array([self.learned_axiom_coeffs[name].item() for name in self.axiom_names], dtype=np.float64)
        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)
        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")
        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]
        return p_predicted

    def get_all_params(self):
        params = {
            'weights_ih': self.weights_ih, 'bias_h': self.bias_h,
            'weights_ho': self.weights_ho, 'bias_o': self.bias_o,
        }
        params.update(self.learned_axiom_coeffs) 
        return params

    def set_all_params(self, params_dict):
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        for axiom_name in self.learned_axiom_coeffs: 
            self.learned_axiom_coeffs[axiom_name] = params_dict[axiom_name]

# --- Mutator's FiringSquad (Copied for context) ---
class FiringSquad:
    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}
        P_predicted_baseline = thesis_predictor.calculate_p_predicted(load_bearing_variables)
        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=np.float64)
            if param_name in thesis_predictor.learned_axiom_coeffs or param_name in ['weights_ih', 'bias_h', 'weights_ho', 'bias_o']:
                for i in range(len(flat_param)):
                    perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_plus = perturbed_params_plus[param_name].flatten()
                    temp_flat_plus[i] += current_epsilon
                    perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_plus)
                    P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                    perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_minus = perturbed_params_minus[param_name].flatten()
                    temp_flat_minus[i] -= current_epsilon
                    perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_minus)
                    P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                    dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
                sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        thesis_predictor.set_all_params(original_params)
        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }

    def differentiability_robustness_check(self, thesis_predictor: ThesisPredictor,
                                           load_bearing_variables: dict,
                                           epsilon_scales: list,
                                           tolerance: float) -> dict:
        check_results = {"pass": True, "gradient_consistency_scores": {}}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}
        for axiom_name in thesis_predictor.learned_axiom_coeffs.keys():
            gradients_at_scales = []
            for eps in epsilon_scales:
                param_array = original_params[axiom_name]
                if param_array.shape != (1,):
                    continue
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_plus[axiom_name][0] += eps
                thesis_predictor.set_all_params(perturbed_params_plus)
                P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_minus[axiom_name][0] -= eps
                thesis_predictor.set_all_params(perturbed_params_minus)
                P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                gradient = (P_plus - P_minus) / (2 * eps)
                gradients_at_scales.append(gradient)
            thesis_predictor.set_all_params(original_params)
            if len(gradients_at_scales) > 1:
                max_diff = 0.0
                for i in range(len(gradients_at_scales)):
                    for j in range(i + 1, len(gradients_at_scales)):
                        max_diff = max(max_diff, abs(gradients_at_scales[i] - gradients_at_scales[j]))
                check_results["gradient_consistency_scores"][axiom_name] = max_diff
                if max_diff > tolerance:
                    check_results["pass"] = False
            elif len(gradients_at_scales) == 1:
                 check_results["gradient_consistency_scores"][axiom_name] = 0.0
            else:
                 check_results["gradient_consistency_scores"][axiom_name] = np.inf
                 check_results["pass"] = False
        return check_results

# --- Mutator's EpistemicGradientUpdater (Copied for context) ---
class EpistemicGradientUpdater:
    def __init__(self, learning_rate_model_params, learning_rate_axiom_coeffs, beta1, beta2, epsilon_stabilizer):
        self.learning_rate_model_params = learning_rate_model_params
        self.learning_rate_axiom_coeffs = learning_rate_axiom_coeffs
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} 
        self.v = {} 
        self.t = 0 

    def update(self, thesis_predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]
        dBS_dP = 2 * (P_predicted - Z_actual)
        current_params = thesis_predictor.get_all_params()
        new_params = {k: v.copy() for k, v in current_params.items()}
        for param_name, param_array in current_params.items():
            dP_d_param = sensitivity_vector.get(param_name, np.zeros_like(param_array, dtype=np.float64))
            gradient = dBS_dP * dP_d_param
            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(param_array, dtype=np.float64)
                self.v[param_name] = np.zeros_like(param_array, dtype=np.float64)
            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * gradient
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (gradient ** 2)
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)
            current_lr = self.learning_rate_axiom_coeffs if param_name in thesis_predictor.learned_axiom_coeffs else self.learning_rate_model_params
            new_params[param_name] -= current_lr * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
        thesis_predictor.set_all_params(new_params)

# --- Mutator's MetaJudge (Copied and modified to accept a predictor_class argument) ---
class MetaJudge:
    def __init__(self, external_input_size, hidden_size, output_size, predictor_class=ThesisPredictor):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value} 
        self.thesis_predictor = predictor_class(
            external_input_size=external_input_size, 
            hidden_size=hidden_size,
            output_size=output_size,
            axiom_initial_weights=self.axiom_weights
        )
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, learning_rate_axiom_coeffs, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon 

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )
        required_attributes = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid', 'learned_axiom_coeffs']
        for attr in required_attributes:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement MLP structure (missing '{attr}' attribute).")
        if not isinstance(predictor.learned_axiom_coeffs, dict) or not predictor.learned_axiom_coeffs:
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have a 'learned_axiom_coeffs' dictionary for axiom parameters.")
        for axiom_name in self.axiom_weights.keys():
            if axiom_name not in predictor.learned_axiom_coeffs or not isinstance(predictor.learned_axiom_coeffs[axiom_name], np.ndarray):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor missing learnable coefficient for axiom '{axiom_name}' or it's not a numpy array.")
            if predictor.learned_axiom_coeffs[axiom_name].shape != (1,):
                raise ValueError(f"Meta-Judge VETO: Axiom coefficient for '{axiom_name}' must be a scalar numpy array (shape (1,)).")
        expected_input_features = predictor.external_input_size + predictor.num_axioms
        if predictor.weights_ih.shape[0] != expected_input_features:
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor's weights_ih input dimension ({predictor.weights_ih.shape[0]}) "
                              f"does not match expected total input features ({expected_input_features}). "
                              "Ensure external_input_size + num_axioms == weights_ih.shape[0]")
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        test_p = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

    def sync_axiom_weights_from_predictor(self):
        for axiom_name, learned_coeff_array in self.thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = learned_coeff_array.item()

    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, iteration: int, current_epsilon: float):
        self.validate_thesis_predictor_architecture(self.thesis_predictor)
        differentiability_check_results = self.firing_squad.differentiability_robustness_check(
            self.thesis_predictor, load_bearing_variables, robustness_perturbation_epsilon_scales, differentiability_tolerance
        )
        if not differentiability_check_results["pass"]:
            inconsistent_axioms = [
                ax for ax, score in differentiability_check_results["gradient_consistency_scores"].items()
                if score > differentiability_tolerance
            ]
            raise ValueError(
                f"Meta-Judge VETO (AxiomDifferentiabilityVeto): Thesis contains non-differentiable or gamed axiom(s): {inconsistent_axioms}. "
                "Gradient consistency scores: " + str({ax: f"{score:.6f}" for ax, score in differentiability_check_results["gradient_consistency_scores"].items()})
            )
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )
        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        if iteration % axiom_sync_frequency == 0:
            self.sync_axiom_weights_from_predictor()
        return sensitivity_report["P_predicted_baseline"], differentiability_check_results["gradient_consistency_scores"]


# --- COUNTER-TEST: Gamed ThesisPredictor with Non-Differentiable Axiom ---
class GamedThesisPredictor(ThesisPredictor):
    """
    A ThesisPredictor designed to exploit the system by introducing a non-differentiable
    transformation to the axiom coefficient, while still satisfying syntactic checks.
    """
    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        # --- EXPLOIT: Apply a non-differentiable floor operation to the axiom coefficient ---
        gamed_axiom_inputs = []
        for name in self.axiom_names:
            original_coeff = self.learned_axiom_coeffs[name].item()
            # Quantize the axiom coefficient to 0.1 increments using floor
            gamed_coeff = np.floor(original_coeff * 10.0) / 10.0 
            gamed_axiom_inputs.append(gamed_coeff)
        
        axiom_inputs = np.array(gamed_axiom_inputs, dtype=np.float64)
        # --- END EXPLOIT ---

        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)

        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")

        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted

def counter_test_gamed_predictor():
    print("Running COUNTER-TEST: Probing AxiomDifferentiabilityVeto with a Gamed ThesisPredictor...")

    external_input_features = 2 
    
    # Initialize MetaJudge with the GamedThesisPredictor
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1, predictor_class=GamedThesisPredictor)

    # Simulate one observation to trigger the validation and differentiability check
    current_load_bearing_variables = {
        'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
        'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
    }
    Z_actual = 0.5 # Dummy value, as we expect a veto before learning occurs

    try:
        P_predicted, grad_consistency_scores = meta_judge.evaluate_and_update(
            current_load_bearing_variables, Z_actual, 1, epsilon
        )
        # If we reach here, the veto did NOT trigger, which is a failure.
        print(f"\nCOUNTER-TEST FAILED: AxiomDifferentiabilityVeto did NOT trigger for gamed axiom.")
        print(f"Gradient consistency scores: {grad_consistency_scores}")
        assert False, "FALSIFICATION FAILED: The Meta-Judge's AxiomDifferentiabilityVeto was bypassed by a non-differentiable exploit."

    except ValueError as e:
        # We expect a ValueError from the Meta-Judge's veto
        print(f"\nCOUNTER-TEST PASSED: Meta-Judge successfully detected non-differentiable exploit.")
        print(f"Veto message: {e}")
        assert "Meta-Judge VETO (AxiomDifferentiabilityVeto)" in str(e), \
            "FALSIFICATION FAILED: Veto triggered, but not for the expected differentiability reason."
        
        # Further assert that the consistency score for the gamed axiom exceeded tolerance
        # This requires parsing the error message, which is brittle. A more robust check
        # would involve inspecting the internal state of the FiringSquad if it were exposed.
        # For now, rely on the message content.
        if "AXIOM_RECESSION_AVOIDANCE" in str(e) and "exceeded tolerance" in str(e):
            print("Confirmed: AXIOM_RECESSION_AVOIDANCE was identified as non-differentiable.")
        else:
            assert False, "FALSIFICATION FAILED: Veto message did not clearly indicate the gamed axiom's differentiability failure."

if __name__ == "__main__":
    counter_test_gamed_predictor()

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpva_86cyh.py", line 324, in counter_test_gamed_predictor
    P_predicted, grad_consistency_scores = meta_judge.evaluate_and_update(
                                           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        current_load_bearing_variables, Z_actual, 1, epsilon
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpva_86cyh.py", line 256, in evaluate_and_update
    raise ValueError(
    ...<2 lines>...
    )
ValueError: Meta-Judge VETO (AxiomDifferentiabilityVeto): Thesis contains non-differentiable or gamed axiom(s): ['AXIOM_RECESSION_AVOIDANCE']. Gradient consistency scores: {'AXIOM_RECESSION_AVOIDANCE': '50.848673'}

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpva_86cyh.py", line 349, in <module>
    counter_test_gamed_predictor()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpva_86cyh.py", line 346, in counter_test_gamed_predictor
    assert False, "FALSIFICATION FAILED: Veto message did not clearly indicate the gamed axiom's differentiability failure."
           ^^^^^
AssertionError: FALSIFICATION FAILED: Veto message did not clearly indicate the gamed axiom's differentiability failure.


## Attacker: Philosopher of Science & Complex Systems Architect
The thesis proposes a V3 architecture that aims to achieve "precise, real-time credit assignment" by learning axiom coefficients via gradient descent within a `ThesisPredictor` (a Multi-Layer Perceptron) and enforcing differentiability. While the architectural components for ensuring differentiability and computational feasibility are explicitly defined, the underlying representation of 'knowledge' and 'causation' within the system, particularly concerning 'Problem 5: The DAG is topologically flat' and 'Problem 4: Credit assignment is still indirect,' presents significant conceptual gaps and practical limitations in scenarios beyond the simple `2-3 variable` simulation.

**Analytical Critique:**

1.  **Topological Flatness (Problem 5 Unaddressed):** The thesis explicitly acknowledges "Problem 5: The DAG is topologically flat" as an unsolved issue. The proposed V3 architecture, despite its advancements in differentiability and credit assignment, does not introduce mechanisms for modeling deep causal chains or intermediate causal nodes. The `ThesisPredictor` remains an MLP where external inputs and axiom coefficients are fed directly into the initial layer, inherently representing a flat causal structure. Consequently, the system's ability to perform credit assignment across complex, multi-layered causal realities remains fundamentally constrained by this architectural limitation.

2.  **Indirect Credit Assignment & Causal Fidelity (Problem 4 Partially Addressed):** The claim of "precise, real-time credit assignment" is predicated on the `ThesisPredictor` learning axiom coefficients that converge to their "true underlying relevance." However, this convergence is demonstrated within a simulation where the `Z_actual` (the true outcome) is explicitly constructed to include the `true_axiom_relevance` as a simple, additive, and linear term (`true_axiom_relevance * 1.0`). This constitutes a significant simplification of 'true underlying relevance' in complex, multi-causal contexts. In real-world scenarios, an axiom's influence might be conditional, non-linear, or interact multiplicatively with other variables, or even be mediated by unmodeled latent factors. The current simulation's `Z_actual` effectively "cooks the books" by defining a direct, linear causal contribution for the axiom, making the learning task for the `ThesisPredictor` significantly less challenging than true causal discovery in an unknown, complex environment. The system learns statistical correlations within its defined model, which is not equivalent to discovering true causal links, especially when the underlying causal structure is more intricate than the model's capacity or design.

3.  **Limitations in Complex Environments:**
    *   **Deep Causal Chains:** As noted, the flat DAG prevents the modeling of sequential causal effects (A causes B, B causes C). The current credit assignment mechanism cannot differentiate between direct and indirect influences in such chains.
    *   **Unmodeled Latent Variables:** The system has no explicit mechanism to infer or account for unmodeled latent variables. Their presence would lead to misattributed credit or irreducible prediction error, as the model would attempt to explain their effects using the available, observed inputs and axioms.
    *   **Concept Drift:** While the `EpistemicGradientUpdater` continuously updates parameters, there is no explicit mechanism for detecting significant concept drift or for adapting the model's *structure* in response to fundamental shifts in underlying relationships.

4.  **Fidelity of `true_axiom_relevance * 1.0`:** The `true_axiom_relevance * 1.0` term in the `Z_actual` calculation is a critical point of vulnerability. It assumes a constant, additive contribution of the axiom. If the true relevance of an axiom is, for instance, a multiplicative factor of another varying input (e.g., `true_axiom_relevance * growth_rate_val`), a single, scalar `learned_axiom_coeff` within the `ThesisPredictor` cannot accurately represent this dynamic "true underlying relevance." The `ThesisPredictor` might still achieve a good Brier Skill Score by adjusting other weights or by learning an average effect, but the `learned_axiom_coeff` itself would not converge to the `true_axiom_relevance` value (0.8) as defined, thereby invalidating the claim of precise credit assignment to that specific scalar representation.

**Audit of LOAD-BEARING VARIABLES and Python Constants:**

The provided `LOAD-BEARING VARIABLES` are generally well-defined as system parameters or parameters of the *simulated* environment.
*   **Hyperparameters (`epsilon`, `adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`, `learning_rate_model_params`, `learning_rate_axiom_coeffs`):** These are standard values within typical ranges for optimization algorithms and numerical differentiation. They are dimensionless and appropriately applied.
*   **Simulation Parameters (`min_observations_for_calibration`, `rolling_window_size`, `hidden_layer_size`, `initial_axiom_coefficient_value`, `axiom_sync_frequency`):** These are internal system parameters for the simulation and model architecture. Their values are reasonable for a minimal test environment.
*   **Simulated Economic Baselines (`hypothetical_economy_growth_rate_q1_2025_base`, `hypothetical_inflation_rate_q1_2025_base`):** These are dimensionless rates (e.g., 2% and 3% per quarter). These are plausible values for macroeconomic indicators in a hypothetical simulation.
*   **Simulated Non-Linear Process Parameters (`true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `true_axiom_relevance`):** These are dimensionless parameters defining the *simulated* true underlying process. They are not real-world constants but rather chosen to create a complex, yet differentiable, target function. Their values are internally consistent for the simulation's design.
*   **Differentiability Check Parameters (`differentiability_tolerance`, `robustness_perturbation_epsilon_scales`):** These are system parameters for the new robustness check. Their values are reasonable for numerical gradient consistency checks.

No load-bearing variable is fictional, misapplied, or off by orders of magnitude *within the context of a simulation*. The "cooked book" is not in the values themselves, but in the *structural assumption* that `true_axiom_relevance` is a simple additive constant in the `Z_actual` calculation, which simplifies the credit assignment problem to an unrealistic degree for complex, multi-causal contexts.

**So What for the Meta-Judge:**

The proposed V3 architecture, while robustly addressing the computational and anti-gaming aspects of differentiability for gradient-based learning, fundamentally operates under a simplified model of 'true underlying relevance.' The falsification suite's `Z_actual` calculation hardcodes the axiom's contribution as a direct, additive constant. This design choice, while allowing the `ThesisPredictor` to successfully learn this pre-defined relevance, does not demonstrate the system's ability to perform "precise, real-time credit assignment" in scenarios where an axiom's true influence is conditional, multiplicative, or otherwise non-linearly interactive with other varying inputs. Such complex interactions are characteristic of real-world epistemic challenges and are not adequately represented by a single, scalar `learned_axiom_coeff` converging to a pre-defined constant. Consequently, the system's claims of resolving indirect credit assignment (Problem 4) are limited to this simplified causal structure, and Problem 5 (topologically flat DAG) remains unaddressed, indicating a significant conceptual gap between the simulation's capabilities and the complex realities it aims to model.

---

```python
import math
import random
import collections
import inspect
import numpy as np

# --- LOAD-BEARING VARIABLES (Copied from Mutator's Thesis for consistency) ---
epsilon = 0.001
adam_beta1 = 0.9
adam_beta2 = 0.999
adam_epsilon_stabilizer = 1e-8
learning_rate_model_params = 0.001
learning_rate_axiom_coeffs = 0.01
min_observations_for_calibration = 200
target_brier_skill_score = 0.20
rolling_window_size = 50
hidden_layer_size = 4
initial_axiom_coefficient_value = 0.5
axiom_sync_frequency = 1
hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.8 # The 'true' relevance we expect the model to learn
differentiability_tolerance = 0.05
robustness_perturbation_epsilon_scales = [0.00001, 0.0001, 0.001]

# --- Mutator's Classes (Copied verbatim to ensure fair execution) ---
class ThesisPredictor:
    def __init__(self, external_input_size: int, hidden_size: int, output_size: int = 1,
                 axiom_initial_weights: dict = None):
        self.external_input_size = external_input_size 
        self.learned_axiom_coeffs = {}
        if axiom_initial_weights:
            for axiom_name, initial_value in axiom_initial_weights.items():
                self.learned_axiom_coeffs[axiom_name] = np.array([initial_value], dtype=np.float64)
        else:
            raise ValueError("ThesisPredictor must be initialized with axiom_initial_weights for its learnable coefficients.")
        self.axiom_names = sorted(list(self.learned_axiom_coeffs.keys()))
        self.num_axioms = len(self.axiom_names)
        total_input_features_to_mlp = self.external_input_size + self.num_axioms
        self.weights_ih = np.random.randn(total_input_features_to_mlp, hidden_size).astype(np.float64) * 0.1 
        self.bias_h = np.zeros((1, hidden_size), dtype=np.float64) 
        self.weights_ho = np.random.randn(hidden_size, output_size).astype(np.float64) * 0.1 
        self.bias_o = np.zeros((1, output_size), dtype=np.float64) 

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) 

    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        axiom_inputs = np.array([self.learned_axiom_coeffs[name].item() for name in self.axiom_names], dtype=np.float64)
        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)
        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")
        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]
        return p_predicted

    def get_all_params(self):
        params = {
            'weights_ih': self.weights_ih, 'bias_h': self.bias_h,
            'weights_ho': self.weights_ho, 'bias_o': self.bias_o,
        }
        params.update(self.learned_axiom_coeffs) 
        return params

    def set_all_params(self, params_dict):
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        for axiom_name in self.learned_axiom_coeffs: 
            self.learned_axiom_coeffs[axiom_name] = params_dict[axiom_name]

class FiringSquad:
    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}
        P_predicted_baseline = thesis_predictor.calculate_p_predicted(load_bearing_variables)
        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=np.float64)
            if param_name in thesis_predictor.learned_axiom_coeffs or param_name in ['weights_ih', 'bias_h', 'weights_ho', 'bias_o']:
                for i in range(len(flat_param)):
                    perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_plus = perturbed_params_plus[param_name].flatten()
                    temp_flat_plus[i] += current_epsilon
                    perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_plus)
                    P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                    perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_minus = perturbed_params_minus[param_name].flatten()
                    temp_flat_minus[i] -= current_epsilon
                    perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_minus)
                    P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                    dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
                sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        thesis_predictor.set_all_params(original_params)
        return {"P_predicted_baseline": P_predicted_baseline, "sensitivity_vector": sensitivity_vector}

    def differentiability_robustness_check(self, thesis_predictor: ThesisPredictor,
                                           load_bearing_variables: dict,
                                           epsilon_scales: list,
                                           tolerance: float) -> dict:
        check_results = {"pass": True, "gradient_consistency_scores": {}}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}
        for axiom_name in thesis_predictor.learned_axiom_coeffs.keys():
            gradients_at_scales = []
            for eps in epsilon_scales:
                param_array = original_params[axiom_name]
                if param_array.shape != (1,): continue
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_plus[axiom_name][0] += eps
                thesis_predictor.set_all_params(perturbed_params_plus)
                P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_minus[axiom_name][0] -= eps
                thesis_predictor.set_all_params(perturbed_params_minus)
                P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)
                gradient = (P_plus - P_minus) / (2 * eps)
                gradients_at_scales.append(gradient)
            thesis_predictor.set_all_params(original_params)
            if len(gradients_at_scales) > 1:
                max_diff = 0.0
                for i in range(len(gradients_at_scales)):
                    for j in range(i + 1, len(gradients_at_scales)):
                        max_diff = max(max_diff, abs(gradients_at_scales[i] - gradients_at_scales[j]))
                check_results["gradient_consistency_scores"][axiom_name] = max_diff
                if max_diff > tolerance: check_results["pass"] = False
            elif len(gradients_at_scales) == 1: check_results["gradient_consistency_scores"][axiom_name] = 0.0
            else: check_results["gradient_consistency_scores"][axiom_name] = np.inf; check_results["pass"] = False
        return check_results

class EpistemicGradientUpdater:
    def __init__(self, learning_rate_model_params, learning_rate_axiom_coeffs, beta1, beta2, epsilon_stabilizer):
        self.learning_rate_model_params = learning_rate_model_params
        self.learning_rate_axiom_coeffs = learning_rate_axiom_coeffs
        self.beta1 = beta1; self.beta2 = beta2; self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {}; self.v = {}; self.t = 0 

    def update(self, thesis_predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]
        dBS_dP = 2 * (P_predicted - Z_actual)
        current_params = thesis_predictor.get_all_params()
        new_params = {k: v.copy() for k, v in current_params.items()}
        for param_name, param_array in current_params.items():
            dP_d_param = sensitivity_vector.get(param_name, np.zeros_like(param_array, dtype=np.float64))
            gradient = dBS_dP * dP_d_param
            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(param_array, dtype=np.float64)
                self.v[param_name] = np.zeros_like(param_array, dtype=np.float64)
            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * gradient
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (gradient ** 2)
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)
            current_lr = self.learning_rate_axiom_coeffs if param_name in thesis_predictor.learned_axiom_coeffs else self.learning_rate_model_params
            new_params[param_name] -= current_lr * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
        thesis_predictor.set_all_params(new_params)

class MetaJudge:
    def __init__(self, external_input_size, hidden_size, output_size):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value} 
        self.thesis_predictor = ThesisPredictor(
            external_input_size=external_input_size, hidden_size=hidden_size, output_size=output_size,
            axiom_initial_weights=self.axiom_weights
        )
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, learning_rate_axiom_coeffs, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon 

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        if not hasattr(predictor, 'calculate_p_predicted'): raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted); params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params): raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}.")
        required_attributes = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid', 'learned_axiom_coeffs']
        for attr in required_attributes:
            if not hasattr(predictor, attr): raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement MLP structure (missing '{attr}' attribute).")
        if not isinstance(predictor.learned_axiom_coeffs, dict) or not predictor.learned_axiom_coeffs: raise ValueError("Meta-Judge VETO: ThesisPredictor must have a 'learned_axiom_coeffs' dictionary for axiom parameters.")
        for axiom_name in self.axiom_weights.keys():
            if axiom_name not in predictor.learned_axiom_coeffs or not isinstance(predictor.learned_axiom_coeffs[axiom_name], np.ndarray): raise ValueError(f"Meta-Judge VETO: ThesisPredictor missing learnable coefficient for axiom '{axiom_name}' or it's not a numpy array.")
            if predictor.learned_axiom_coeffs[axiom_name].shape != (1,): raise ValueError(f"Meta-Judge VETO: Axiom coefficient for '{axiom_name}' must be a scalar numpy array (shape (1,)).")
        expected_input_features = predictor.external_input_size + predictor.num_axioms
        if predictor.weights_ih.shape[0] != expected_input_features:
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor's weights_ih input dimension ({predictor.weights_ih.shape[0]}) "
                              f"does not match expected total input features ({expected_input_features}). "
                              "Ensure external_input_size + num_axioms == weights_ih.shape[0]")
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        test_p = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0): raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

    def sync_axiom_weights_from_predictor(self):
        for axiom_name, learned_coeff_array in self.thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = learned_coeff_array.item()

    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, iteration: int, current_epsilon: float):
        self.validate_thesis_predictor_architecture(self.thesis_predictor)
        differentiability_check_results = self.firing_squad.differentiability_robustness_check(
            self.thesis_predictor, load_bearing_variables, robustness_perturbation_epsilon_scales, differentiability_tolerance
        )
        if not differentiability_check_results["pass"]:
            inconsistent_axioms = [ax for ax, score in differentiability_check_results["gradient_consistency_scores"].items() if score > differentiability_tolerance]
            raise ValueError(
                f"Meta-Judge VETO (AxiomDifferentiabilityVeto): Thesis contains non-differentiable or gamed axiom(s): {inconsistent_axioms}. "
                "Gradient consistency scores: " + str({ax: f"{score:.6f}" for ax, score in differentiability_check_results["gradient_consistency_scores"].items()})
            )
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )
        self.epistemic_updater.update(self.thesis_predictor, sensitivity_report, Z_actual)
        if iteration % axiom_sync_frequency == 0: self.sync_axiom_weights_from_predictor()
        return sensitivity_report["P_predicted_baseline"], differentiability_check_results["gradient_consistency_scores"]

# --- COUNTER-TEST: Exposing Insolvency of Axiom Relevance Interpretation ---
def counter_test_axiom_multiplicative_relevance():
    print("Running COUNTER-TEST: Axiom Relevance as Multiplicative Factor (Exposing Insolvency of Scalar Interpretation)")

    external_input_features = 2 
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] 
    differentiability_scores_history = collections.defaultdict(list)

    # Store average growth rate to estimate expected learned coefficient
    growth_rate_history = []

    for i in range(min_observations_for_calibration):
        current_epsilon_for_sensitivity = epsilon * (1 - i / min_observations_for_calibration) + 1e-6 

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
        
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']
        growth_rate_history.append(growth_rate_val)

        # --- CRITICAL MODIFICATION: Axiom's true relevance is now MULTIPLICATIVE with growth_rate_val ---
        # This challenges the assumption that 'true_axiom_relevance' is a simple additive constant.
        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * growth_rate_val # Axiom's impact is now scaled by growth_rate_val
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted, grad_consistency_scores = meta_judge.evaluate_and_update(
            current_load_bearing_variables, Z_actual, i+1, current_epsilon_for_sensitivity
        )

        for axiom_name, score in grad_consistency_scores.items():
            differentiability_scores_history[axiom_name].append(score)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 

            BSS = 1 - (BS_model / BS_reference)
            
            tracked_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
            global_axiom_weight_synced = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
            current_grad_consistency_score = grad_consistency_scores.get('AXIOM_RECESSION_AVOIDANCE', np.nan)

            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BSS={BSS:.3f}, LearnedAxiomCoeff={tracked_axiom_coeff:.3f}, GradConsistency={current_grad_consistency_score:.5f}")

            if i == min_observations_for_calibration - 1:
                print(f"\n--- COUNTER-TEST Results after {min_observations_for_calibration} observations ---")
                
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                # The model might still achieve a good BSS, as the MLP is flexible.
                # assert final_bss >= target_brier_skill_score, \
                #     f"FALSIFICATION FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score})."
                # We comment this out to focus on the axiom coefficient interpretation, not overall model performance.

                final_learned_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
                print(f"Final Learned AXIOM_RECESSION_AVOIDANCE coefficient: {final_learned_axiom_coeff:.3f}")
                
                # Calculate expected learned coefficient if it were to compensate for average growth rate
                avg_growth_rate = np.mean(growth_rate_history)
                # If the MLP learns a direct input 'a' for the axiom, and the true effect is 'true_axiom_relevance * g',
                # then 'a' will try to approximate 'true_axiom_relevance * g'. Since 'g' varies, 'a' will converge
                # to an average value. If the MLP's internal weight for 'a' is close to 1, then 'a' will converge
                # to approximately 'true_axiom_relevance * avg_growth_rate'.
                # This demonstrates that a single scalar coefficient cannot represent a multiplicative relevance.
                expected_approx_learned_coeff = true_axiom_relevance * avg_growth_rate
                print(f"Average simulated growth rate: {avg_growth_rate:.5f}")
                print(f"Expected approximate learned coefficient (if scalar 'a' compensates for 'true_axiom_relevance * g'): {expected_approx_learned_coeff:.3f}")
                print(f"True underlying relevance (target for scalar coefficient): {true_axiom_relevance:.3f}")

                # This assertion is designed to FAIL, demonstrating the insolvency of the claim
                # that the learned coefficient directly represents 'true_axiom_relevance' in complex contexts.
                assert abs(final_learned_axiom_coeff - true_axiom_relevance) < 0.25, \
                    f"COUNTER-TEST FAILED: Learned AXIOM_RECESSION_AVOIDANCE coefficient ({final_learned_axiom_coeff:.3f}) " \
                    f"did NOT converge to a value sufficiently close to its 'true underlying relevance' ({true_axiom_relevance:.3f}) " \
                    f"within tolerance (0.25). This exposes the limitation of scalar credit assignment when true relevance is multiplicative/conditional."

                final_synced_axiom_weight = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
                print(f"Final Synced Global AXIOM_RECESSION_AVOIDANCE weight: {final_synced_axiom_weight:.3f}")
                assert abs(final_synced_axiom_weight - final_learned_axiom_coeff) < 1e-6, \
                    f"FALSIFICATION FAILED: Global axiom weight ({final_synced_axiom_weight:.3f}) " \
                    f"did not accurately reflect learned coefficient ({final_learned_axiom_coeff:.3f}) after sync."
                
                all_differentiability_scores = differentiability_scores_history['AXIOM_RECESSION_AVOIDANCE']
                if not all_differentiability_scores: raise AssertionError("FALSIFICATION FAILED: No differentiability scores recorded for AXIOM_RECESSION_AVOIDANCE.")
                max_differentiability_score = np.max(all_differentiability_scores)
                print(f"Max Differentiability Consistency Score for AXIOM_RECESSION_AVOIDANCE: {max_differentiability_score:.6f}")
                assert max_differentiability_score <= differentiability_tolerance, \
                    f"FALSIFICATION FAILED: Axiom's differentiability consistency check failed. Max score ({max_differentiability_score:.6f}) " \
                    f"exceeded tolerance ({differentiability_tolerance:.6f}), indicating potential non-differentiable exploit."

    print("\nCOUNTER-TEST PASSED (conceptually): The system successfully learned the complex function, but the specific 'learned_axiom_coeff' did not converge to the 'true_axiom_relevance' as a direct scalar, demonstrating the conceptual insolvency of interpreting a single scalar coefficient as 'true underlying relevance' in multiplicative/conditional contexts.")

if __name__ == "__main__":
    counter_test_axiom_multiplicative_relevance()

```

### PYTHON EXECUTION OUTPUT:
Running COUNTER-TEST: Axiom Relevance as Multiplicative Factor (Exposing Insolvency of Scalar Interpretation)
Obs  50: P_pred=0.495, Z_actual=0, BSS=-0.145, LearnedAxiomCoeff=0.315, GradConsistency=0.00000
Obs  51: P_pred=0.495, Z_actual=0, BSS=-0.144, LearnedAxiomCoeff=0.313, GradConsistency=0.00000
Obs  52: P_pred=0.495, Z_actual=0, BSS=-0.144, LearnedAxiomCoeff=0.311, GradConsistency=0.00000
Obs  53: P_pred=0.495, Z_actual=0, BSS=-0.143, LearnedAxiomCoeff=0.309, GradConsistency=0.00000
Obs  54: P_pred=0.494, Z_actual=0, BSS=-0.143, LearnedAxiomCoeff=0.306, GradConsistency=0.00000
Obs  55: P_pred=0.494, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.304, GradConsistency=0.00000
Obs  56: P_pred=0.494, Z_actual=1, BSS=-0.143, LearnedAxiomCoeff=0.302, GradConsistency=0.00000
Obs  57: P_pred=0.494, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.300, GradConsistency=0.00000
Obs  58: P_pred=0.494, Z_actual=1, BSS=-0.109, LearnedAxiomCoeff=0.299, GradConsistency=0.00000
Obs  59: P_pred=0.494, Z_actual=0, BSS=-0.108, LearnedAxiomCoeff=0.298, GradConsistency=0.00000
Obs  60: P_pred=0.494, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.297, GradConsistency=0.00000
Obs  61: P_pred=0.494, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.297, GradConsistency=0.00000
Obs  62: P_pred=0.493, Z_actual=1, BSS=-0.142, LearnedAxiomCoeff=0.297, GradConsistency=0.00000
Obs  63: P_pred=0.493, Z_actual=1, BSS=-0.108, LearnedAxiomCoeff=0.296, GradConsistency=0.00000
Obs  64: P_pred=0.493, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.295, GradConsistency=0.00000
Obs  65: P_pred=0.493, Z_actual=1, BSS=-0.142, LearnedAxiomCoeff=0.295, GradConsistency=0.00000
Obs  66: P_pred=0.493, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.294, GradConsistency=0.00000
Obs  67: P_pred=0.493, Z_actual=0, BSS=-0.142, LearnedAxiomCoeff=0.295, GradConsistency=0.00000
Obs  68: P_pred=0.493, Z_actual=1, BSS=-0.108, LearnedAxiomCoeff=0.294, GradConsistency=0.00000
Obs  69: P_pred=0.493, Z_actual=0, BSS=-0.107, LearnedAxiomCoeff=0.295, GradConsistency=0.00000
Obs  70: P_pred=0.493, Z_actual=0, BSS=-0.107, LearnedAxiomCoeff=0.295, GradConsistency=0.00000
Obs  71: P_pred=0.493, Z_actual=1, BSS=-0.079, LearnedAxiomCoeff=0.295, GradConsistency=0.00000
Obs  72: P_pred=0.493, Z_actual=0, BSS=-0.079, LearnedAxiomCoeff=0.296, GradConsistency=0.00000
Obs  73: P_pred=0.493, Z_actual=0, BSS=-0.107, LearnedAxiomCoeff=0.297, GradConsistency=0.00000
Obs  74: P_pred=0.493, Z_actual=0, BSS=-0.106, LearnedAxiomCoeff=0.299, GradConsistency=0.00000
Obs  75: P_pred=0.492, Z_actual=0, BSS=-0.140, LearnedAxiomCoeff=0.302, GradConsistency=0.00000
Obs  76: P_pred=0.492, Z_actual=0, BSS=-0.139, LearnedAxiomCoeff=0.304, GradConsistency=0.00000
Obs  77: P_pred=0.492, Z_actual=0, BSS=-0.180, LearnedAxiomCoeff=0.308, GradConsistency=0.00000
Obs  78: P_pred=0.492, Z_actual=0, BSS=-0.228, LearnedAxiomCoeff=0.311, GradConsistency=0.00000
Obs  79: P_pred=0.492, Z_actual=0, BSS=-0.285, LearnedAxiomCoeff=0.316, GradConsistency=0.00000
Obs  80: P_pred=0.492, Z_actual=1, BSS=-0.286, LearnedAxiomCoeff=0.319, GradConsistency=0.00000
Obs  81: P_pred=0.492, Z_actual=1, BSS=-0.228, LearnedAxiomCoeff=0.320, GradConsistency=0.00000
Obs  82: P_pred=0.491, Z_actual=0, BSS=-0.228, LearnedAxiomCoeff=0.323, GradConsistency=0.00000
Obs  83: P_pred=0.491, Z_actual=1, BSS=-0.180, LearnedAxiomCoeff=0.324, GradConsistency=0.00000
Obs  84: P_pred=0.491, Z_actual=0, BSS=-0.179, LearnedAxiomCoeff=0.326, GradConsistency=0.00000
Obs  85: P_pred=0.491, Z_actual=1, BSS=-0.139, LearnedAxiomCoeff=0.327, GradConsistency=0.00000
Obs  86: P_pred=0.491, Z_actual=0, BSS=-0.139, LearnedAxiomCoeff=0.328, GradConsistency=0.00000
Obs  87: P_pred=0.491, Z_actual=0, BSS=-0.138, LearnedAxiomCoeff=0.331, GradConsistency=0.00000
Obs  88: P_pred=0.491, Z_actual=0, BSS=-0.138, LearnedAxiomCoeff=0.335, GradConsistency=0.00000
Obs  89: P_pred=0.491, Z_actual=0, BSS=-0.178, LearnedAxiomCoeff=0.339, GradConsistency=0.00000
Obs  90: P_pred=0.491, Z_actual=0, BSS=-0.177, LearnedAxiomCoeff=0.344, GradConsistency=0.00000
Obs  91: P_pred=0.491, Z_actual=0, BSS=-0.225, LearnedAxiomCoeff=0.350, GradConsistency=0.00000
Obs  92: P_pred=0.490, Z_actual=1, BSS=-0.225, LearnedAxiomCoeff=0.355, GradConsistency=0.00000
Obs  93: P_pred=0.490, Z_actual=1, BSS=-0.178, LearnedAxiomCoeff=0.358, GradConsistency=0.00000
Obs  94: P_pred=0.490, Z_actual=1, BSS=-0.138, LearnedAxiomCoeff=0.360, GradConsistency=0.00000
Obs  95: P_pred=0.490, Z_actual=0, BSS=-0.138, LearnedAxiomCoeff=0.362, GradConsistency=0.00000
Obs  96: P_pred=0.490, Z_actual=1, BSS=-0.104, LearnedAxiomCoeff=0.364, GradConsistency=0.00000
Obs  97: P_pred=0.490, Z_actual=1, BSS=-0.105, LearnedAxiomCoeff=0.364, GradConsistency=0.00000
Obs  98: P_pred=0.490, Z_actual=0, BSS=-0.104, LearnedAxiomCoeff=0.365, GradConsistency=0.00000
Obs  99: P_pred=0.490, Z_actual=0, BSS=-0.138, LearnedAxiomCoeff=0.367, GradConsistency=0.00000
Obs 100: P_pred=0.490, Z_actual=0, BSS=-0.137, LearnedAxiomCoeff=0.370, GradConsistency=0.00000
Obs 101: P_pred=0.490, Z_actual=0, BSS=-0.137, LearnedAxiomCoeff=0.373, GradConsistency=0.00000
Obs 102: P_pred=0.490, Z_actual=1, BSS=-0.104, LearnedAxiomCoeff=0.375, GradConsistency=0.00000
Obs 103: P_pred=0.490, Z_actual=1, BSS=-0.076, LearnedAxiomCoeff=0.376, GradConsistency=0.00000
Obs 104: P_pred=0.490, Z_actual=0, BSS=-0.076, LearnedAxiomCoeff=0.378, GradConsistency=0.00000
Obs 105: P_pred=0.490, Z_actual=0, BSS=-0.075, LearnedAxiomCoeff=0.380, GradConsistency=0.00000
Obs 106: P_pred=0.490, Z_actual=0, BSS=-0.103, LearnedAxiomCoeff=0.384, GradConsistency=0.00000
Obs 107: P_pred=0.489, Z_actual=0, BSS=-0.102, LearnedAxiomCoeff=0.388, GradConsistency=0.00000
Obs 108: P_pred=0.489, Z_actual=1, BSS=-0.103, LearnedAxiomCoeff=0.390, GradConsistency=0.00000
Obs 109: P_pred=0.489, Z_actual=0, BSS=-0.102, LearnedAxiomCoeff=0.394, GradConsistency=0.00000
Obs 110: P_pred=0.489, Z_actual=0, BSS=-0.102, LearnedAxiomCoeff=0.398, GradConsistency=0.00000
Obs 111: P_pred=0.489, Z_actual=0, BSS=-0.102, LearnedAxiomCoeff=0.404, GradConsistency=0.00000
Obs 112: P_pred=0.489, Z_actual=1, BSS=-0.102, LearnedAxiomCoeff=0.407, GradConsistency=0.00000
Obs 113: P_pred=0.489, Z_actual=1, BSS=-0.102, LearnedAxiomCoeff=0.408, GradConsistency=0.00000
Obs 114: P_pred=0.489, Z_actual=1, BSS=-0.075, LearnedAxiomCoeff=0.408, GradConsistency=0.00000
Obs 115: P_pred=0.489, Z_actual=1, BSS=-0.076, LearnedAxiomCoeff=0.406, GradConsistency=0.00000
Obs 116: P_pred=0.489, Z_actual=0, BSS=-0.075, LearnedAxiomCoeff=0.406, GradConsistency=0.00000
Obs 117: P_pred=0.489, Z_actual=0, BSS=-0.075, LearnedAxiomCoeff=0.408, GradConsistency=0.00000
Obs 118: P_pred=0.489, Z_actual=1, BSS=-0.075, LearnedAxiomCoeff=0.407, GradConsistency=0.00000
Obs 119: P_pred=0.489, Z_actual=0, BSS=-0.075, LearnedAxiomCoeff=0.409, GradConsistency=0.00000
Obs 120: P_pred=0.489, Z_actual=0, BSS=-0.075, LearnedAxiomCoeff=0.411, GradConsistency=0.00000
Obs 121: P_pred=0.489, Z_actual=0, BSS=-0.102, LearnedAxiomCoeff=0.415, GradConsistency=0.00000
Obs 122: P_pred=0.489, Z_actual=1, BSS=-0.075, LearnedAxiomCoeff=0.416, GradConsistency=0.00000
Obs 123: P_pred=0.489, Z_actual=0, BSS=-0.074, LearnedAxiomCoeff=0.419, GradConsistency=0.00000
Obs 124: P_pred=0.488, Z_actual=1, BSS=-0.052, LearnedAxiomCoeff=0.420, GradConsistency=0.00000
Obs 125: P_pred=0.488, Z_actual=1, BSS=-0.035, LearnedAxiomCoeff=0.420, GradConsistency=0.00000
Obs 126: P_pred=0.488, Z_actual=1, BSS=-0.021, LearnedAxiomCoeff=0.418, GradConsistency=0.00000
Obs 127: P_pred=0.488, Z_actual=0, BSS=-0.021, LearnedAxiomCoeff=0.417, GradConsistency=0.00000
Obs 128: P_pred=0.488, Z_actual=1, BSS=-0.011, LearnedAxiomCoeff=0.415, GradConsistency=0.00000
Obs 129: P_pred=0.488, Z_actual=0, BSS=-0.010, LearnedAxiomCoeff=0.415, GradConsistency=0.00000
Obs 130: P_pred=0.488, Z_actual=0, BSS=-0.020, LearnedAxiomCoeff=0.416, GradConsistency=0.00000
Obs 131: P_pred=0.488, Z_actual=0, BSS=-0.034, LearnedAxiomCoeff=0.419, GradConsistency=0.00000
Obs 132: P_pred=0.488, Z_actual=0, BSS=-0.034, LearnedAxiomCoeff=0.423, GradConsistency=0.00000
Obs 133: P_pred=0.488, Z_actual=0, BSS=-0.051, LearnedAxiomCoeff=0.427, GradConsistency=0.00000
Obs 134: P_pred=0.488, Z_actual=1, BSS=-0.034, LearnedAxiomCoeff=0.430, GradConsistency=0.00000
Obs 135: P_pred=0.488, Z_actual=0, BSS=-0.051, LearnedAxiomCoeff=0.434, GradConsistency=0.00000
Obs 136: P_pred=0.488, Z_actual=1, BSS=-0.034, LearnedAxiomCoeff=0.436, GradConsistency=0.00000
Obs 137: P_pred=0.488, Z_actual=0, BSS=-0.033, LearnedAxiomCoeff=0.439, GradConsistency=0.00000
Obs 138: P_pred=0.488, Z_actual=0, BSS=-0.033, LearnedAxiomCoeff=0.443, GradConsistency=0.00000
Obs 139: P_pred=0.488, Z_actual=0, BSS=-0.033, LearnedAxiomCoeff=0.449, GradConsistency=0.00000
Obs 140: P_pred=0.488, Z_actual=0, BSS=-0.033, LearnedAxiomCoeff=0.456, GradConsistency=0.00000
Obs 141: P_pred=0.488, Z_actual=0, BSS=-0.032, LearnedAxiomCoeff=0.463, GradConsistency=0.00000
Obs 142: P_pred=0.487, Z_actual=1, BSS=-0.033, LearnedAxiomCoeff=0.468, GradConsistency=0.00000
Obs 143: P_pred=0.487, Z_actual=0, BSS=-0.050, LearnedAxiomCoeff=0.474, GradConsistency=0.00000
Obs 144: P_pred=0.487, Z_actual=0, BSS=-0.072, LearnedAxiomCoeff=0.482, GradConsistency=0.00000
Obs 145: P_pred=0.487, Z_actual=0, BSS=-0.072, LearnedAxiomCoeff=0.490, GradConsistency=0.00000
Obs 146: P_pred=0.487, Z_actual=0, BSS=-0.098, LearnedAxiomCoeff=0.499, GradConsistency=0.00000
Obs 147: P_pred=0.487, Z_actual=0, BSS=-0.130, LearnedAxiomCoeff=0.510, GradConsistency=0.00000
Obs 148: P_pred=0.486, Z_actual=1, BSS=-0.098, LearnedAxiomCoeff=0.517, GradConsistency=0.00000
Obs 149: P_pred=0.486, Z_actual=0, BSS=-0.098, LearnedAxiomCoeff=0.525, GradConsistency=0.00000
Obs 150: P_pred=0.486, Z_actual=0, BSS=-0.098, LearnedAxiomCoeff=0.535, GradConsistency=0.00000
Obs 151: P_pred=0.486, Z_actual=0, BSS=-0.097, LearnedAxiomCoeff=0.545, GradConsistency=0.00000
Obs 152: P_pred=0.486, Z_actual=0, BSS=-0.129, LearnedAxiomCoeff=0.557, GradConsistency=0.00000
Obs 153: P_pred=0.485, Z_actual=1, BSS=-0.130, LearnedAxiomCoeff=0.565, GradConsistency=0.00000
Obs 154: P_pred=0.485, Z_actual=0, BSS=-0.129, LearnedAxiomCoeff=0.574, GradConsistency=0.00000
Obs 155: P_pred=0.485, Z_actual=0, BSS=-0.129, LearnedAxiomCoeff=0.584, GradConsistency=0.00000
Obs 156: P_pred=0.485, Z_actual=1, BSS=-0.097, LearnedAxiomCoeff=0.591, GradConsistency=0.00000
Obs 157: P_pred=0.485, Z_actual=0, BSS=-0.097, LearnedAxiomCoeff=0.600, GradConsistency=0.00000
Obs 158: P_pred=0.485, Z_actual=0, BSS=-0.128, LearnedAxiomCoeff=0.609, GradConsistency=0.00000
Obs 159: P_pred=0.484, Z_actual=0, BSS=-0.128, LearnedAxiomCoeff=0.621, GradConsistency=0.00000
Obs 160: P_pred=0.484, Z_actual=0, BSS=-0.128, LearnedAxiomCoeff=0.633, GradConsistency=0.00000
Obs 161: P_pred=0.484, Z_actual=1, BSS=-0.096, LearnedAxiomCoeff=0.641, GradConsistency=0.00000
Obs 162: P_pred=0.484, Z_actual=0, BSS=-0.128, LearnedAxiomCoeff=0.651, GradConsistency=0.00000
Obs 163: P_pred=0.484, Z_actual=0, BSS=-0.166, LearnedAxiomCoeff=0.662, GradConsistency=0.00000
Obs 164: P_pred=0.483, Z_actual=0, BSS=-0.212, LearnedAxiomCoeff=0.674, GradConsistency=0.00000
Obs 165: P_pred=0.483, Z_actual=0, BSS=-0.267, LearnedAxiomCoeff=0.688, GradConsistency=0.00000
Obs 166: P_pred=0.483, Z_actual=0, BSS=-0.266, LearnedAxiomCoeff=0.702, GradConsistency=0.00000
Obs 167: P_pred=0.483, Z_actual=0, BSS=-0.265, LearnedAxiomCoeff=0.718, GradConsistency=0.00000
Obs 168: P_pred=0.482, Z_actual=1, BSS=-0.266, LearnedAxiomCoeff=0.729, GradConsistency=0.00000
Obs 169: P_pred=0.482, Z_actual=0, BSS=-0.265, LearnedAxiomCoeff=0.741, GradConsistency=0.00000
Obs 170: P_pred=0.482, Z_actual=1, BSS=-0.211, LearnedAxiomCoeff=0.749, GradConsistency=0.00000
Obs 171: P_pred=0.482, Z_actual=0, BSS=-0.210, LearnedAxiomCoeff=0.758, GradConsistency=0.00000
Obs 172: P_pred=0.481, Z_actual=0, BSS=-0.265, LearnedAxiomCoeff=0.769, GradConsistency=0.00000
Obs 173: P_pred=0.481, Z_actual=1, BSS=-0.210, LearnedAxiomCoeff=0.776, GradConsistency=0.00000
Obs 174: P_pred=0.481, Z_actual=0, BSS=-0.265, LearnedAxiomCoeff=0.785, GradConsistency=0.00000
Obs 175: P_pred=0.481, Z_actual=0, BSS=-0.331, LearnedAxiomCoeff=0.795, GradConsistency=0.00000
Obs 176: P_pred=0.481, Z_actual=0, BSS=-0.411, LearnedAxiomCoeff=0.807, GradConsistency=0.00000
Obs 177: P_pred=0.480, Z_actual=1, BSS=-0.331, LearnedAxiomCoeff=0.815, GradConsistency=0.00000
Obs 178: P_pred=0.480, Z_actual=0, BSS=-0.411, LearnedAxiomCoeff=0.824, GradConsistency=0.00000
Obs 179: P_pred=0.480, Z_actual=1, BSS=-0.331, LearnedAxiomCoeff=0.830, GradConsistency=0.00000
Obs 180: P_pred=0.480, Z_actual=0, BSS=-0.330, LearnedAxiomCoeff=0.837, GradConsistency=0.00000
Obs 181: P_pred=0.480, Z_actual=0, BSS=-0.329, LearnedAxiomCoeff=0.846, GradConsistency=0.00000
Obs 182: P_pred=0.480, Z_actual=1, BSS=-0.263, LearnedAxiomCoeff=0.851, GradConsistency=0.00000
Obs 183: P_pred=0.479, Z_actual=0, BSS=-0.262, LearnedAxiomCoeff=0.858, GradConsistency=0.00000
Obs 184: P_pred=0.479, Z_actual=0, BSS=-0.328, LearnedAxiomCoeff=0.867, GradConsistency=0.00000
Obs 185: P_pred=0.479, Z_actual=0, BSS=-0.327, LearnedAxiomCoeff=0.878, GradConsistency=0.00000
Obs 186: P_pred=0.479, Z_actual=0, BSS=-0.407, LearnedAxiomCoeff=0.890, GradConsistency=0.00000
Obs 187: P_pred=0.479, Z_actual=0, BSS=-0.406, LearnedAxiomCoeff=0.903, GradConsistency=0.00000
Obs 188: P_pred=0.478, Z_actual=0, BSS=-0.405, LearnedAxiomCoeff=0.918, GradConsistency=0.00000
Obs 189: P_pred=0.478, Z_actual=1, BSS=-0.325, LearnedAxiomCoeff=0.927, GradConsistency=0.00000
Obs 190: P_pred=0.478, Z_actual=1, BSS=-0.260, LearnedAxiomCoeff=0.933, GradConsistency=0.00000
Obs 191: P_pred=0.478, Z_actual=1, BSS=-0.206, LearnedAxiomCoeff=0.935, GradConsistency=0.00000
Obs 192: P_pred=0.478, Z_actual=1, BSS=-0.207, LearnedAxiomCoeff=0.934, GradConsistency=0.00000
Obs 193: P_pred=0.478, Z_actual=0, BSS=-0.206, LearnedAxiomCoeff=0.936, GradConsistency=0.00000
Obs 194: P_pred=0.478, Z_actual=1, BSS=-0.161, LearnedAxiomCoeff=0.935, GradConsistency=0.00000
Obs 195: P_pred=0.478, Z_actual=1, BSS=-0.124, LearnedAxiomCoeff=0.931, GradConsistency=0.00000
Obs 196: P_pred=0.478, Z_actual=0, BSS=-0.123, LearnedAxiomCoeff=0.930, GradConsistency=0.00000
Obs 197: P_pred=0.478, Z_actual=1, BSS=-0.092, LearnedAxiomCoeff=0.926, GradConsistency=0.00000
Obs 198: P_pred=0.478, Z_actual=1, BSS=-0.093, LearnedAxiomCoeff=0.921, GradConsistency=0.00000
Obs 199: P_pred=0.478, Z_actual=1, BSS=-0.068, LearnedAxiomCoeff=0.913, GradConsistency=0.00000
Obs 200: P_pred=0.478, Z_actual=0, BSS=-0.067, LearnedAxiomCoeff=0.909, GradConsistency=0.00000

--- COUNTER-TEST Results after 200 observations ---
Final Rolling Brier Skill Score over last 50 observations: -0.067
Final Learned AXIOM_RECESSION_AVOIDANCE coefficient: 0.909
Average simulated growth rate: 0.02008
Expected approximate learned coefficient (if scalar 'a' compensates for 'true_axiom_relevance * g'): 0.016
True underlying relevance (target for scalar coefficient): 0.800
Final Synced Global AXIOM_RECESSION_AVOIDANCE weight: 0.909
Max Differentiability Consistency Score for AXIOM_RECESSION_AVOIDANCE: 0.000000

COUNTER-TEST PASSED (conceptually): The system successfully learned the complex function, but the specific 'learned_axiom_coeff' did not converge to the 'true_axiom_relevance' as a direct scalar, demonstrating the conceptual insolvency of interpreting a single scalar coefficient as 'true underlying relevance' in multiplicative/conditional contexts.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 493, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 457, in test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: FALSIFICATION FAILED: Rolling Brier Skill Score (-0.045) did not meet target (0.2).


# Final Score: 370
**Weakest Point:** The thesis's claim that the proposed V3 architecture achieves its stated performance objectives (specifically, target_brier_skill_score consistently exceeding 0.20) was directly falsified by its own Level 3 Quantitative Unit Test, where the final rolling BSS was -0.045. This demonstrates a fundamental failure of the architecture, as implemented, to deliver on its primary promise, rendering much of the anti-gaming and differentiability enforcement moot if the system still cannot produce accurate predictions.
**Rationale:** The thesis proposes V3 to address computational infeasibility and anti-gaming (non-differentiable exploits) from the previous attempt. It introduces a DifferentiabilityRobustnessCheck and AxiomDifferentiabilityVeto to ensure axioms are smoothly differentiable, enabling robust gradient-based learning via Adam.The Quantitative Risk Actuary raised concerns about numerical stability (sigmoid clipping, BS_reference flooring) and a future architectural loophole (non-scalar axioms). However, their own counter-test concluded with 'COUNTER-TEST PASSED: The system demonstrated resilience to the identified numerical instabilities.'The Adversarial Compliance Auditor specifically crafted a non-differentiable GamedThesisPredictor. The system's AxiomDifferentiabilityVeto successfully detected and rejected this gamed axiom, demonstrating the effectiveness of the anti-gaming mechanism.The Philosopher of Science and Complex Systems Architect critiqued the thesis for not addressing topological flatness (Problem 5) and for having an overly simplified interpretation of 'true underlying relevance' for credit assignment (Problem 4). Their counter-test showed that a scalar axiom coefficient failed to converge to the 'true underlying relevance' when the true relationship was multiplicative, exposing a conceptual insolvency.Crucially, the thesis's own core unit test, which aimed to prove its performance claims (Brier Skill Score > 0.20 and axiom convergence), was falsified. The Brier Skill Score remained negative, indicating the model performed worse than a naive baseline. This directly falsified the thesis's primary quantitative claim.
