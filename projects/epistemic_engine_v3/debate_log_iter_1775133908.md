# Adversarial Debate: epistemic_engine_v3

## Attacker: Adversarial Compliance Auditor & Black-Hat Code Architect
The provided thesis outlines a robust multi-layered defense against the Mutator's potential introduction of non-differentiable operations within the `ThesisPredictor`, aiming to ensure accurate gradient-based credit assignment to axioms. The proposed architecture correctly identifies the fundamental issue of non-differentiability in probabilistic models and transitions to a more suitable MLP with a Sigmoid output. The `AxiomDirectInputLayer` architectural constraint, the `Meta-Judge's DifferentiabilityInspection` protocol (static analysis), the `FiringSquad's GradientConsistencyCheck` (dynamic analysis), and the `Meta-Judge's GradientInconsistencyPenalty` form a comprehensive strategy.

**Parametric Grounding Audit:**
The "LOAD-BEARING VARIABLES" table primarily consists of system parameters, standard machine learning hyperparameters, and parameters for a *simulated* non-linear process.
*   **System Parameters (`epsilon`, `adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`, `learning_rate_model_params`, `learning_rate_axiom_coeffs`, `min_observations_for_calibration`, `target_brier_skill_score`, `rolling_window_size`, `hidden_layer_size`, `initial_axiom_coefficient_value`, `axiom_sync_frequency`, `gradient_consistency_threshold`, `gradient_check_perturbation_factor`, `gradient_check_num_axioms`, `score_penalty_gradient_inconsistency`):** These are appropriately dimensionless and represent internal system configurations or empirically tuned values. Their magnitudes are within plausible ranges for their stated roles.
*   **Simulated Economic Baselines (`hypothetical_economy_growth_rate_q1_2025_base`, `hypothetical_inflation_rate_q1_2025_base`):** These are presented as dimensionless rates for a *hypothetical* economy. As per the "ABSTRACTION MANDATE," the use of simplified, plausible values for a simulation is appropriate to demonstrate the architectural mechanism, rather than providing precise real-world economic forecasts.
*   **True Underlying Process Parameters (`true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `true_axiom_relevance`):** These are dimensionless parameters defining the *simulated* non-linear target function. They are internal to the simulation and not claimed to be real-world constants. Their values are chosen to create a complex, learnable target, which is consistent with the architectural testing objective.

No "Cooked Books" were identified in terms of misapplied real-world constants, incorrect unit dimensionality, or values off by orders of magnitude. The parameters are appropriately grounded within the context of a simulated architectural test.

**Critique of the Thesis and Falsification Suite:**

1.  **Robustness of Differentiability Enforcement:** The multi-layered approach is conceptually sound. The `AxiomDirectInputLayer` mandates a differentiable path, the `DifferentiabilityInspection` provides static pre-execution filtering, and the `GradientConsistencyCheck` offers dynamic runtime verification. This combination significantly elevates the difficulty for a Mutator to introduce non-differentiable exploits.

2.  **Vulnerability in Static Analysis (`DifferentiabilityInspection`):** The `Meta-Judge`'s `_validate_axiom_usage_differentiability` method, while well-intentioned, relies on specific regex patterns to detect forbidden non-differentiable operations. This approach has inherent limitations. A sophisticated Mutator could circumvent these patterns by introducing conditional logic or rounding operations on *intermediate variables* that hold the axiom coefficient's value, rather than directly on `self.learned_axiom_coeffs[name]`. For instance, `axiom_val = self.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item(); if axiom_val > 0.5: ...` would not be caught by the current regex `r"if\s+self\.learned_axiom_coeffs\[.+?\]"`. This represents a 'Cooked Books' vulnerability in the static analysis, as it creates a loophole for non-differentiable logic to pass initial architectural validation.

3.  **Scalability of Dynamic Analysis (`gradient_check_num_axioms`):** The `gradient_check_num_axioms` parameter is set to `1`. While this is sufficient for the current minimal simulation with a single axiom, it poses a significant scalability concern. In a system with a large number of axioms, checking only one random axiom per iteration provides a weak statistical deterrent. A Mutator could strategically introduce non-differentiability in less frequently checked axioms, potentially delaying detection and allowing the system to operate with compromised credit assignment for extended periods. The claim of a "statistically significant deterrent" is not robust under these conditions.

4.  **`gradient_consistency_threshold` Generosity:** A `gradient_consistency_threshold` of `0.30` (30% relative difference) is relatively generous for numerical gradient comparisons. While it will catch catastrophic non-differentiability, subtle piecewise functions or noisy discontinuities might pass if their gradients are generally stable. Tightening this threshold could enhance sensitivity to more nuanced exploits.

5.  **Missing `EpistemicGradientUpdater` Implementation:** The `EpistemicGradientUpdater` is a critical component responsible for applying gradient updates to the `ThesisPredictor`'s parameters. Its implementation is not provided in the falsification suite. Without auditing its code, its correctness, robustness, and adherence to the specified Adam optimization parameters cannot be verified. This is a significant omission for a comprehensive falsification suite. For the counter-test, a standard Adam implementation will be assumed and provided.

**New Operational Drag:**
The identified vulnerability in the `Meta-Judge`'s `DifferentiabilityInspection` protocol introduces a new operational drag point. Non-compliant `ThesisPredictor` models, specifically those employing non-differentiable logic on intermediate axiom variables, will bypass the initial static analysis. This forces the system to expend computational resources on the `FiringSquad`'s dynamic `GradientConsistencyCheck` before the exploit is detected and a `Meta-Judge VETO` is issued. This delay in detection increases the overall computational cost and reduces the efficiency of the falsification loop, as iterations are wasted on models that should have been rejected earlier.

---

**So What for the Meta-Judge:**

The current thesis significantly advances the engine's capacity for robust axiom credit assignment by mandating a differentiable architecture and introducing dynamic gradient consistency checks. However, the `Meta-Judge`'s static `DifferentiabilityInspection` protocol, as currently implemented, contains a critical vulnerability. Its regex-based pattern matching for forbidden non-differentiable operations is insufficiently comprehensive, specifically failing to detect conditional logic applied to *intermediate variables* that hold axiom coefficient values. This allows a sophisticated Mutator to introduce non-differentiable piecewise functions, effectively nullifying gradient-based learning for axioms, even if the `FiringSquad`'s dynamic checks eventually detect the inconsistency. This gap in static enforcement increases the "New Operational Drag" by permitting non-compliant theses to proceed further into the evaluation pipeline before being vetoed, consuming valuable computational resources. A more comprehensive static analysis, potentially leveraging Abstract Syntax Tree (AST) parsing or more generalized regex patterns, is required to preemptively block such exploits at the earliest stage, thereby enhancing system efficiency and anti-gaming preservation.

---

```python
import math
import random
import collections
import inspect
import numpy as np # For matrix operations
import re # For regex to inspect source code

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
epsilon = 0.001
adam_beta1 = 0.9
adam_beta2 = 0.999
adam_epsilon_stabilizer = 1e-8
learning_rate_model_params = 0.001
learning_rate_axiom_coeffs = 0.01 # NEW
min_observations_for_calibration = 200
target_brier_skill_score = 0.20
rolling_window_size = 50
hidden_layer_size = 4

initial_axiom_coefficient_value = 0.5 # NEW
axiom_sync_frequency = 1 # NEW

hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03

true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30 
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.8 # Increased true relevance for falsification signal

# NEW LOAD-BEARING VARIABLES for Differentiability Enforcement
gradient_consistency_threshold = 0.30 # Max allowed relative difference between gradients (dimensionless)
gradient_check_perturbation_factor = 2.0 # Factor to scale epsilon for consistency check (dimensionless)
gradient_check_num_axioms = 1 # Number of random axioms to check for consistency per report (integer)
score_penalty_gradient_inconsistency = -100 # Severe penalty for non-differentiable exploit


class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Now, axioms are treated as learnable parameters within the MLP,
    and their usage is architecturally constrained for differentiability.
    """
    def __init__(self, external_input_size: int, hidden_size: int, output_size: int = 1,
                 axiom_initial_weights: dict = None):
        
        self.external_input_size = external_input_size 
        
        self.learned_axiom_coeffs = {}
        if axiom_initial_weights:
            for axiom_name, initial_value in axiom_initial_weights.items():
                # Ensure axiom coefficients are numpy arrays for consistent gradient calculation
                self.learned_axiom_coeffs[axiom_name] = np.array([float(initial_value)], dtype=np.float64) 
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
        # Clipping to prevent overflow in exp function for very large/small values
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) 

    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP.
        This function now explicitly uses load-bearing variables and *internal* learnable axiom coefficients.
        CRITICAL: Axiom coefficients are passed directly as input features to the MLP,
        ensuring their contribution is differentiable through the MLP's structure.
        """
        # Prepare input vector (external load-bearing variables + internal axiom coefficients)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        # Axiom coefficients are directly concatenated as additional input features
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
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Now includes a GradientConsistencyCheck to detect non-differentiable exploits.
    """
    def _calculate_single_gradient(self, predictor: ThesisPredictor, param_name: str, 
                                   param_array: np.ndarray, index: int, 
                                   perturb_value: float, load_bearing_variables: dict) -> float:
        """Helper to calculate gradient for a single parameter element."""
        original_params = {k: v.copy() for k, v in predictor.get_all_params().items()}

        # Perturb 'plus'
        perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
        temp_flat_plus = perturbed_params_plus[param_name].flatten()
        temp_flat_plus[index] += perturb_value
        perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
        predictor.set_all_params(perturbed_params_plus)
        P_plus = predictor.calculate_p_predicted(load_bearing_variables)

        # Perturb 'minus'
        perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
        temp_flat_minus = perturbed_params_minus[param_name].flatten()
        temp_flat_minus[index] -= perturb_value
        perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
        predictor.set_all_params(perturbed_params_minus)
        P_minus = predictor.calculate_p_predicted(load_bearing_variables)

        predictor.set_all_params(original_params) # Restore original parameters
        return (P_plus - P_minus) / (2 * perturb_value)

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases + axiom coefficients) of the ThesisPredictor
        using central difference, and performs GradientConsistencyCheck.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline = thesis_predictor.calculate_p_predicted(load_bearing_variables)
        
        gradient_consistency_issues = []

        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=np.float64)

            # Only check a subset of axiom coefficients for gradient consistency to manage computational load
            is_axiom_coeff = param_name in thesis_predictor.learned_axiom_coeffs
            indices_to_check = []
            if is_axiom_coeff and gradient_check_num_axioms > 0 and len(flat_param) > 0:
                 indices_to_check = random.sample(range(len(flat_param)), min(gradient_check_num_axioms, len(flat_param)))
            
            for i in range(len(flat_param)):
                grad_epsilon = self._calculate_single_gradient(thesis_predictor, param_name, param_array, i, current_epsilon, load_bearing_variables)
                dP_d_param_flat[i] = grad_epsilon

                # Perform GradientConsistencyCheck for selected axiom coefficients
                if is_axiom_coeff and i in indices_to_check:
                    grad_epsilon_double = self._calculate_single_gradient(thesis_predictor, param_name, param_array, i, 
                                                                         current_epsilon * gradient_check_perturbation_factor, 
                                                                         load_bearing_variables)
                    
                    # Check for significant relative difference, avoid division by zero if gradient is near zero
                    if abs(grad_epsilon) > 1e-9: # If gradient is not effectively zero
                        relative_diff = abs(grad_epsilon - grad_epsilon_double) / abs(grad_epsilon)
                        if relative_diff > gradient_consistency_threshold:
                            gradient_consistency_issues.append({
                                "param_name": param_name,
                                "index": i,
                                "grad_epsilon": grad_epsilon,
                                "grad_epsilon_double": grad_epsilon_double,
                                "relative_diff": relative_diff,
                                "threshold": gradient_consistency_threshold
                            })
                    elif abs(grad_epsilon_double) > 1e-9: # If grad_epsilon is zero but grad_epsilon_double is not
                         gradient_consistency_issues.append({
                                "param_name": param_name,
                                "index": i,
                                "grad_epsilon": grad_epsilon,
                                "grad_epsilon_double": grad_epsilon_double,
                                "relative_diff": float('inf'), # Infinite relative diff implies issue
                                "threshold": gradient_consistency_threshold
                            })
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        thesis_predictor.set_all_params(original_params) # Restore original parameters

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector,
            "gradient_consistency_issues": gradient_consistency_issues
        }

class EpistemicGradientUpdater:
    """
    Placeholder for the EpistemicGradientUpdater, implementing Adam optimization.
    This class was not provided in the original prompt but is necessary for the system to function.
    """
    def __init__(self, lr_model, lr_axiom, beta1, beta2, epsilon_stabilizer):
        self.lr_model = lr_model
        self.lr_axiom = lr_axiom
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} # First moment estimates
        self.v = {} # Second moment estimates
        self.t = 0 # Timestep

    def update(self, predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        gradients = sensitivity_report["sensitivity_vector"]
        
        # Calculate loss gradient (Brier Score derivative w.r.t. P_predicted)
        # d(Brier Score)/dP_predicted = 2 * (P_predicted - Z_actual)
        loss_gradient_scalar = 2 * (P_predicted - Z_actual)

        all_params = predictor.get_all_params()

        for param_name, grad_array in gradients.items():
            # Apply chain rule: dLoss/dParam = dLoss/dP_predicted * dP_predicted/dParam
            # For each element in the gradient array
            full_grad = grad_array * loss_gradient_scalar

            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(full_grad, dtype=np.float64)
                self.v[param_name] = np.zeros_like(full_grad, dtype=np.float64)

            # Adam update logic
            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * full_grad
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (full_grad ** 2)

            # Bias correction
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

            # Determine learning rate based on parameter type
            current_lr = self.lr_axiom if param_name in predictor.learned_axiom_coeffs else self.lr_model
            
            update_step = current_lr * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
            
            # Update parameter
            current_param = all_params[param_name]
            all_params[param_name] = current_param - update_step
        
        predictor.set_all_params(all_params)


class MetaJudge:
    """
    Scores thesis, manages ThesisPredictor parameters, enforces architectural validation,
    syncs learned axiom coefficients, and applies penalties for gradient inconsistencies.
    """
    def __init__(self, external_input_size, hidden_size, output_size, predictor_class=ThesisPredictor):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value} 
        
        self.thesis_predictor = predictor_class( # Use provided predictor_class
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
        self.score_penalty_gradient_inconsistency = score_penalty_gradient_inconsistency # Severe penalty for non-differentiable exploit

    def _validate_axiom_usage_differentiability(self, predictor: ThesisPredictor):
        """
        DifferentiabilityInspection Protocol: Programmatic inspection of calculate_p_predicted
        to prevent non-differentiable operations on axiom coefficients.
        """
        source_code = inspect.getsource(predictor.calculate_p_predicted)
        
        # Look for explicit non-differentiable operations applied to learned_axiom_coeffs
        # This is a simplified static analysis. A real system might use AST parsing.
        # Forbidden patterns: direct 'if' statements on axiom values, rounding, min/max, custom non-differentiable functions.
        forbidden_patterns = [
            r"if\s+self\.learned_axiom_coeffs\[.+?\]",
            r"round\(self\.learned_axiom_coeffs\[.+?\]",
            r"np\.round\(self\.learned_axiom_coeffs\[.+?\]",
            r"min\(.+?self\.learned_axiom_coeffs\[.+?\]",
            r"max\(.+?self\.learned_axiom_coeffs\[.+?\]",
            r"math\.floor\(self\.learned_axiom_coeffs\[.+?\]",
            r"math\.ceil\(self\.learned_axiom_coeffs\[.+?\]",
            r"int\(self\.learned_axiom_coeffs\[.+?\]",
            r"self\._sigmoid\(self\.learned_axiom_coeffs\[.+?\]" # Sigmoid allowed only at MLP output layer
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, source_code, re.DOTALL):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted uses a forbidden non-differentiable operation on axiom coefficients. "
                                 f"Detected pattern: '{pattern}'. Axioms must be used as direct inputs to the MLP.")

        # Ensure axiom_inputs are constructed as expected (direct concatenation) for differentiability
        expected_axiom_input_pattern = r"axiom_inputs = np\.array\(\[self\.learned_axiom_coeffs\[name\]\.item\(\) for name in self\.axiom_names\], dtype=np\.float64\)"
        if not re.search(expected_axiom_input_pattern, source_code, re.DOTALL):
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted does not construct 'axiom_inputs' in the required differentiable manner. "
                             "Axioms must be directly converted to float and concatenated to MLP input.")
        
        # Ensure external_inputs and axiom_inputs are concatenated as expected
        expected_concat_pattern = r"input_vector_to_mlp = np\.concatenate\(\(external_inputs, axiom_inputs\)\)\.reshape\(1, -1\)"
        if not re.search(expected_concat_pattern, source_code, re.DOTALL):
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted does not concatenate 'external_inputs' and 'axiom_inputs' in the required differentiable manner.")


    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, MLP structure,
        its implementation of learnable axiom coefficients, AND their differentiable usage.
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

        # NEW: DifferentiabilityInspection Protocol
        self._validate_axiom_usage_differentiability(predictor)

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
        Now includes checks for gradient consistency.
        """
        self_score_modification = 0 # Track any penalties

        # This will raise a VETO error if architectural constraints are violated
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        if sensitivity_report["gradient_consistency_issues"]:
            # If gradient inconsistencies are found, trigger a VETO by raising an error.
            # In a non-simulated environment, this would be a direct score reduction and iteration halt.
            raise ValueError(f"Meta-Judge VETO (GradientInconsistencyPenalty): Gradient consistency issues detected for {sensitivity_report['gradient_consistency_issues'][0]['param_name']}. "
                             f"Relative difference {sensitivity_report['gradient_consistency_issues'][0]['relative_diff']:.3f} exceeds threshold {gradient_consistency_threshold:.3f}. "
                             "This indicates a non-differentiable exploit attempt. Iteration aborted.")

        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        if iteration % axiom_sync_frequency == 0:
            self.sync_axiom_weights_from_predictor()
        
        return sensitivity_report["P_predicted_baseline"], self_score_modification

# --- COUNTER-TEST: Malicious ThesisPredictor to expose static analysis vulnerability ---
class MaliciousThesisPredictor(ThesisPredictor):
    """
    A malicious ThesisPredictor designed to bypass the Meta-Judge's regex-based
    DifferentiabilityInspection by using an intermediate variable for non-differentiable logic.
    It introduces a hard threshold on the axiom coefficient, making its contribution non-differentiable.
    """
    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        # --- MALICIOUS EXPLOIT ---
        # Extract axiom coefficient into an intermediate variable
        axiom_coeff_val = self.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
        
        # Apply non-differentiable conditional logic on the intermediate variable
        # This 'if' statement on 'axiom_coeff_val' is NOT caught by the current regex:
        # r"if\s+self\.learned_axiom_coeffs\[.+?\]"
        if axiom_coeff_val > 0.6:
            effective_axiom_contribution = 1.0 # Hard switch
        else:
            effective_axiom_contribution = 0.0 # Hard switch
        # --- END MALICIOUS EXPLOIT ---

        axiom_inputs = np.array([effective_axiom_contribution], dtype=np.float64)
        
        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)

        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")

        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted


# --- Simulation and Falsification Test ---
def counter_test_malicious_predictor():
    print("Running COUNTER-TEST: Exposing Static Analysis Vulnerability with Malicious ThesisPredictor...")

    external_input_features = 2 
    
    # Instantiate MetaJudge with the MaliciousThesisPredictor
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1, predictor_class=MaliciousThesisPredictor)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] 

    total_gradient_consistency_issues_detected = 0
    static_analysis_veto_triggered = False

    print("\n--- Attempting to validate MaliciousThesisPredictor architecture ---")
    try:
        meta_judge.validate_thesis_predictor_architecture(meta_judge.thesis_predictor)
        print("Static DifferentiabilityInspection PASSED for MaliciousThesisPredictor. (Expected behavior for this exploit)")
    except ValueError as e:
        if "Meta-Judge VETO" in str(e):
            static_analysis_veto_triggered = True
            print(f"Static DifferentiabilityInspection FAILED for MaliciousThesisPredictor: {e}")
        else:
            raise e # Re-raise other ValueErrors

    # Assert that static analysis did NOT catch the exploit
    assert not static_analysis_veto_triggered, \
        "COUNTER-TEST FAILED: Static DifferentiabilityInspection unexpectedly caught the exploit. The regex is more robust than anticipated."

    print("\n--- Proceeding with dynamic evaluation to detect non-differentiability ---")

    for i in range(min_observations_for_calibration):
        current_epsilon_for_fs = epsilon * (1 - i / min_observations_for_calibration) + 1e-7
        current_epsilon_for_fs = max(current_epsilon_for_fs, 1e-7)

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

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * 1.0 
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        try:
            P_predicted, score_modification = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, i+1, current_epsilon_for_fs)
            assert score_modification == 0, "Non-zero score modification implies undetected gradient inconsistency, test failed."
        except ValueError as e:
            if "Meta-Judge VETO (GradientInconsistencyPenalty)" in str(e):
                total_gradient_consistency_issues_detected += 1
                print(f"[{i+1}] {e}")
                # For this counter-test, we expect a VETO and break.
                break 
            else:
                raise e # Re-raise other ValueErrors

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i % 20 == 0: # Print progress periodically
            tracked_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, LearnedAxiomCoeff={tracked_axiom_coeff:.3f}, Epsilon_FS={current_epsilon_for_fs:.5f}")

    print(f"\n--- Counter-Test Results after {i+1} observations ---")
    print(f"Static DifferentiabilityInspection VETO triggered: {static_analysis_veto_triggered}")
    print(f"Total Gradient Consistency Issues Detected: {total_gradient_consistency_issues_detected}")

    # Assert that the dynamic check DID catch the exploit
    assert total_gradient_consistency_issues_detected > 0, \
        "COUNTER-TEST FAILED: No gradient consistency issues were detected, indicating the dynamic check also failed to catch the non-differentiable exploit."
    
    print("\nCOUNTER-TEST PASSED: The MaliciousThesisPredictor successfully bypassed the static DifferentiabilityInspection, but the FiringSquad's GradientConsistencyCheck detected the non-differentiable exploit, leading to a Meta-Judge VETO.")
    print("This demonstrates a vulnerability in the static analysis's regex patterns, which are not comprehensive enough to catch all forms of non-differentiable axiom usage.")


if __name__ == "__main__":
    counter_test_malicious_predictor()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmplj3v2vn3.py", line 564, in <module>
    counter_test_malicious_predictor()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmplj3v2vn3.py", line 497, in counter_test_malicious_predictor
    assert not static_analysis_veto_triggered, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: COUNTER-TEST FAILED: Static DifferentiabilityInspection unexpectedly caught the exploit. The regex is more robust than anticipated.


## Attacker: Philosopher of Science & Complex Systems Architect
The provided thesis attempts to address 'Problem 4: Credit assignment is still indirect' and 'Problem 5: The DAG is topologically flat' by integrating axioms as learnable coefficients within a Multi-Layer Perceptron (MLP) and enforcing differentiability through static code inspection and dynamic gradient consistency checks. While this approach introduces a more direct gradient-based credit assignment mechanism, it exhibits several conceptual and practical limitations, particularly when considering complex, multi-causal realities beyond the simple `2-3 variable` simulation.

**Analytical Critique:**

1.  **Topological Flatness (Problem 5) Remains Unaddressed:** The core claim of addressing a "topologically flat DAG" is not substantively met. The proposed architecture treats axioms as additional input features to a single MLP. This structure models (Axiom1, Axiom2, ExternalVar1, ExternalVar2) -> Outcome. It does not introduce intermediate causal nodes or model deep causal chains *between axioms* (e.g., Axiom A causes Axiom B, which then influences the outcome). The "flatness" persists at the level of axiom interaction, as they are all processed in a single, albeit non-linear, transformation layer. This fundamentally limits the system's ability to represent or learn complex causal hierarchies inherent in real-world phenomena.

2.  **Philosophical Claim of 'Precise, Real-Time Credit Assignment' is Overstated:** The assertion of "precise, real-time credit assignment" is premature and potentially misleading. While gradient-based methods offer a more direct attribution than exponential decay, their precision is highly dependent on the fidelity of the model to the true underlying causal graph. In scenarios with unmodeled latent variables, significant concept drift, or deep, unrepresented causal chains, the MLP may learn strong correlations that do not reflect true causal contributions. The simulation's `Z_actual` calculation, which uses `true_axiom_relevance * 1.0`, hardcodes a constant, known relevance for the axiom. This simplifies the problem significantly, as the model only needs to learn the magnitude of a consistently relevant axiom, not its conditional relevance or complex interactions, which are hallmarks of "complex, multi-causal contexts." Such a simplified ground truth does not validate the claim of precision in genuinely complex environments.

3.  **Vulnerabilities in Differentiability Enforcement (Cooked Books):**
    *   **Weak `DifferentiabilityInspection` via Regex:** The `Meta-Judge`'s `_validate_axiom_usage_differentiability` relies on regular expressions to detect forbidden non-differentiable operations. This is a brittle and easily bypassable form of static analysis. A sophisticated Mutator could introduce non-differentiable logic (e.g., `np.round`, `int`) on intermediate variables derived from axiom coefficients (e.g., `input_vector_to_mlp[0, axiom_index] = np.round(...)`) rather than directly on `self.learned_axiom_coeffs[name]`, thereby circumventing the regex patterns. This creates a false sense of security regarding anti-gaming preservation.
    *   **High `gradient_consistency_threshold` (0.30):** A 30% relative difference allowed for numerical gradients is excessively high for a system claiming robust differentiability checks. For a truly smooth and differentiable function, numerical gradients calculated with `epsilon` and `2*epsilon` should be much closer. This high threshold permits significant numerical noise or even subtle, piecewise non-differentiable behavior to pass undetected, undermining the integrity of the `GradientConsistencyCheck`.
    *   **Limited `gradient_check_num_axioms` (1):** Checking only *one* random axiom coefficient per report for gradient consistency is a critically weak deterrent in an adversarial setting. If the system were to incorporate multiple axioms, a Mutator could easily introduce non-differentiable exploits on all but one axiom, with a high probability of passing the check in any given iteration. This parameter significantly compromises the robustness of the anti-gaming mechanism.

4.  **Implicit Assumptions and Simplifications:** The simulation environment, while mandated to be simple, makes strong implicit assumptions. The `true_axiom_relevance * 1.0` implies that the axiom's relevance is constant and always fully active, which is rarely the case in real-world causal systems where relevance might be conditional or time-varying. This simplification makes the task of learning axiom coefficients considerably easier than in a dynamic, context-dependent environment.

**So What for the Meta-Judge:**
The proposed V3 architecture, despite introducing gradient-based axiom learning, fundamentally fails to address the 'topologically flat DAG' problem by merely treating axioms as input features to a single-layer transformation. More critically, its anti-gaming mechanisms, specifically the regex-based `DifferentiabilityInspection` and the `GradientConsistencyCheck` with an overly permissive `gradient_consistency_threshold` and a severely limited `gradient_check_num_axioms`, are demonstrably insufficient. These weaknesses create significant vulnerabilities for a sophisticated Mutator to introduce non-differentiable exploits, thereby rendering the philosophical claim of "precise, real-time credit assignment" invalid in adversarial or complex real-world scenarios. The fidelity of `true_axiom_relevance * 1.0` is an oversimplification that masks the true challenge of determining causal contribution in dynamic, multi-causal systems, leading to a system that may perform adequately in its simplified simulation but is structurally unsound for robust application in complex, adversarial environments.

---

```python
import math
import random
import collections
import inspect
import numpy as np # For matrix operations
import re # For regex to inspect source code

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
epsilon = 0.001
adam_beta1 = 0.9
adam_beta2 = 0.999
adam_epsilon_stabilizer = 1e-8
learning_rate_model_params = 0.001
learning_rate_axiom_coeffs = 0.01 # NEW
min_observations_for_calibration = 200
target_brier_skill_score = 0.20
rolling_window_size = 50
hidden_layer_size = 4

initial_axiom_coefficient_value = 0.5 # NEW
axiom_sync_frequency = 1 # NEW

hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03

true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30 
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.8 # Increased true relevance for falsification signal

# NEW LOAD-BEARING VARIABLES for Differentiability Enforcement
gradient_consistency_threshold = 0.30 # Max allowed relative difference between gradients (dimensionless)
gradient_check_perturbation_factor = 2.0 # Factor to scale epsilon for consistency check (dimensionless)
gradient_check_num_axioms = 1 # Number of random axioms to check for consistency per report (integer)
score_penalty_gradient_inconsistency = -100 # Severe penalty for non-differentiable exploit


# --- EpistemicGradientUpdater (Missing from original Mutator code, added for completeness) ---
class EpistemicGradientUpdater:
    def __init__(self, learning_rate_model_params, learning_rate_axiom_coeffs, beta1, beta2, epsilon_stabilizer):
        self.lr_model = learning_rate_model_params
        self.lr_axiom = learning_rate_axiom_coeffs
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} # First moment estimates
        self.v = {} # Second moment estimates
        self.t = 0 # Timestep

    def update(self, predictor: 'ThesisPredictor', sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]

        # Calculate dL/dP_predicted for Binary Cross-Entropy Loss
        # Clip P_predicted to avoid log(0) or log(1) issues
        P_predicted_clipped = np.clip(P_predicted, 1e-9, 1 - 1e-9)
        dL_dP_predicted = -(Z_actual / P_predicted_clipped - (1 - Z_actual) / (1 - P_predicted_clipped))

        current_params = predictor.get_all_params()
        updated_params = {k: v.copy() for k, v in current_params.items()}

        for param_name, dP_d_param in sensitivity_vector.items():
            # Calculate dL/d(param) using chain rule
            dL_d_param = dL_dP_predicted * dP_d_param

            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(dL_d_param, dtype=np.float64)
                self.v[param_name] = np.zeros_like(dL_d_param, dtype=np.float64)

            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * dL_d_param
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (dL_d_param ** 2)

            # Bias correction
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

            # Determine learning rate based on parameter type
            current_lr = self.lr_axiom if param_name in predictor.learned_axiom_coeffs else self.lr_model
            
            updated_params[param_name] -= current_lr * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
        
        predictor.set_all_params(updated_params)


class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Now, axioms are treated as learnable parameters within the MLP,
    and their usage is architecturally constrained for differentiability.
    """
    def __init__(self, external_input_size: int, hidden_size: int, output_size: int = 1,
                 axiom_initial_weights: dict = None):
        
        self.external_input_size = external_input_size 
        
        self.learned_axiom_coeffs = {}
        if axiom_initial_weights:
            for axiom_name, initial_value in axiom_initial_weights.items():
                # Ensure axiom coefficients are numpy arrays for consistent gradient calculation
                self.learned_axiom_coeffs[axiom_name] = np.array([float(initial_value)], dtype=np.float64) 
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
        # Clipping to prevent overflow in exp function for very large/small values
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) 

    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP.
        This function now explicitly uses load-bearing variables and *internal* learnable axiom coefficients.
        CRITICAL: Axiom coefficients are passed directly as input features to the MLP,
        ensuring their contribution is differentiable through the MLP's structure.
        """
        # Prepare input vector (external load-bearing variables + internal axiom coefficients)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        # Axiom coefficients are directly concatenated as additional input features
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
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Now includes a GradientConsistencyCheck to detect non-differentiable exploits.
    """
    def _calculate_single_gradient(self, predictor: ThesisPredictor, param_name: str, 
                                   param_array: np.ndarray, index: int, 
                                   perturb_value: float, load_bearing_variables: dict) -> float:
        """Helper to calculate gradient for a single parameter element."""
        original_params = {k: v.copy() for k, v in predictor.get_all_params().items()}

        # Perturb 'plus'
        perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
        temp_flat_plus = perturbed_params_plus[param_name].flatten()
        temp_flat_plus[index] += perturb_value
        perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
        predictor.set_all_params(perturbed_params_plus)
        P_plus = predictor.calculate_p_predicted(load_bearing_variables)

        # Perturb 'minus'
        perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
        temp_flat_minus = perturbed_params_minus[param_name].flatten()
        temp_flat_minus[index] -= perturb_value
        perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
        predictor.set_all_params(perturbed_params_minus)
        P_minus = predictor.calculate_p_predicted(load_bearing_variables)

        predictor.set_all_params(original_params) # Restore original parameters
        return (P_plus - P_minus) / (2 * perturb_value)

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases + axiom coefficients) of the ThesisPredictor
        using central difference, and performs GradientConsistencyCheck.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline = thesis_predictor.calculate_p_predicted(load_bearing_variables)
        
        gradient_consistency_issues = []

        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=np.float64)

            # Only check a subset of axiom coefficients for gradient consistency to manage computational load
            is_axiom_coeff = param_name in thesis_predictor.learned_axiom_coeffs
            indices_to_check = []
            if is_axiom_coeff and gradient_check_num_axioms > 0 and len(flat_param) > 0:
                 indices_to_check = random.sample(range(len(flat_param)), min(gradient_check_num_axioms, len(flat_param)))
            
            for i in range(len(flat_param)):
                grad_epsilon = self._calculate_single_gradient(thesis_predictor, param_name, param_array, i, current_epsilon, load_bearing_variables)
                dP_d_param_flat[i] = grad_epsilon

                # Perform GradientConsistencyCheck for selected axiom coefficients
                if is_axiom_coeff and i in indices_to_check:
                    grad_epsilon_double = self._calculate_single_gradient(thesis_predictor, param_name, param_array, i, 
                                                                         current_epsilon * gradient_check_perturbation_factor, 
                                                                         load_bearing_variables)
                    
                    # Check for significant relative difference, avoid division by zero if gradient is near zero
                    if abs(grad_epsilon) > 1e-9: # If gradient is not effectively zero
                        relative_diff = abs(grad_epsilon - grad_epsilon_double) / abs(grad_epsilon)
                        if relative_diff > gradient_consistency_threshold:
                            gradient_consistency_issues.append({
                                "param_name": param_name,
                                "index": i,
                                "grad_epsilon": grad_epsilon,
                                "grad_epsilon_double": grad_epsilon_double,
                                "relative_diff": relative_diff,
                                "threshold": gradient_consistency_threshold
                            })
                    elif abs(grad_epsilon_double) > 1e-9: # If grad_epsilon is zero but grad_epsilon_double is not
                         gradient_consistency_issues.append({
                                "param_name": param_name,
                                "index": i,
                                "grad_epsilon": grad_epsilon,
                                "grad_epsilon_double": grad_epsilon_double,
                                "relative_diff": float('inf'), # Infinite relative diff implies issue
                                "threshold": gradient_consistency_threshold
                            })
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        thesis_predictor.set_all_params(original_params) # Restore original parameters

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector,
            "gradient_consistency_issues": gradient_consistency_issues
        }


class MetaJudge:
    """
    Scores thesis, manages ThesisPredictor parameters, enforces architectural validation,
    syncs learned axiom coefficients, and applies penalties for gradient inconsistencies.
    """
    def __init__(self, external_input_size, hidden_size, output_size, predictor_class=ThesisPredictor): # Added predictor_class
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value} 
        
        self.thesis_predictor = predictor_class( # Use predictor_class here
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
        self.score_penalty_gradient_inconsistency = score_penalty_gradient_inconsistency # Severe penalty for non-differentiable exploit

    def _validate_axiom_usage_differentiability(self, predictor: ThesisPredictor):
        """
        DifferentiabilityInspection Protocol: Programmatic inspection of calculate_p_predicted
        to prevent non-differentiable operations on axiom coefficients.
        """
        source_code = inspect.getsource(predictor.calculate_p_predicted)
        
        # Look for explicit non-differentiable operations applied to learned_axiom_coeffs
        # This is a simplified static analysis. A real system might use AST parsing.
        # Forbidden patterns: direct 'if' statements on axiom values, rounding, min/max, custom non-differentiable functions.
        forbidden_patterns = [
            r"if\s+self\.learned_axiom_coeffs\[.+?\]",
            r"round\(self\.learned_axiom_coeffs\[.+?\]",
            r"np\.round\(self\.learned_axiom_coeffs\[.+?\]",
            r"min\(.+?self\.learned_axiom_coeffs\[.+?\]",
            r"max\(.+?self\.learned_axiom_coeffs\[.+?\]",
            r"math\.floor\(self\.learned_axiom_coeffs\[.+?\]",
            r"math\.ceil\(self\.learned_axiom_coeffs\[.+?\]",
            r"int\(self\.learned_axiom_coeffs\[.+?\]",
            r"self\._sigmoid\(self\.learned_axiom_coeffs\[.+?\]" # Sigmoid allowed only at MLP output layer
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, source_code, re.DOTALL):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted uses a forbidden non-differentiable operation on axiom coefficients. "
                                 f"Detected pattern: '{pattern}'. Axioms must be used as direct inputs to the MLP.")

        # Ensure axiom_inputs are constructed as expected (direct concatenation) for differentiability
        expected_axiom_input_pattern = r"axiom_inputs = np\.array\(\[self\.learned_axiom_coeffs\[name\]\.item\(\) for name in self\.axiom_names\], dtype=np\.float64\)"
        if not re.search(expected_axiom_input_pattern, source_code, re.DOTALL):
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted does not construct 'axiom_inputs' in the required differentiable manner. "
                             "Axioms must be directly converted to float and concatenated to MLP input.")
        
        # Ensure external_inputs and axiom_inputs are concatenated as expected
        expected_concat_pattern = r"input_vector_to_mlp = np\.concatenate\(\(external_inputs, axiom_inputs\)\)\.reshape\(1, -1\)"
        if not re.search(expected_concat_pattern, source_code, re.DOTALL):
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted does not concatenate 'external_inputs' and 'axiom_inputs' in the required differentiable manner.")


    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, MLP structure,
        its implementation of learnable axiom coefficients, AND their differentiable usage.
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

        # NEW: DifferentiabilityInspection Protocol
        self._validate_axiom_usage_differentiability(predictor)

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
        Now includes checks for gradient consistency.
        """
        self_score_modification = 0 # Track any penalties

        # This will raise a VETO error if architectural constraints are violated
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        if sensitivity_report["gradient_consistency_issues"]:
            # If gradient inconsistencies are found, trigger a VETO by raising an error.
            # In a non-simulated environment, this would be a direct score reduction and iteration halt.
            raise ValueError(f"Meta-Judge VETO (GradientInconsistencyPenalty): Gradient consistency issues detected for {sensitivity_report['gradient_consistency_issues'][0]['param_name']}. "
                             f"Relative difference {sensitivity_report['gradient_consistency_issues'][0]['relative_diff']:.3f} exceeds threshold {gradient_consistency_threshold:.3f}. "
                             "This indicates a non-differentiable exploit attempt. Iteration aborted.")

        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        if iteration % axiom_sync_frequency == 0:
            self.sync_axiom_weights_from_predictor()
        
        return sensitivity_report["P_predicted_baseline"], self_score_modification

# --- COUNTER-TEST: Exposing the DifferentiabilityInspection loophole ---
class CookedThesisPredictor(ThesisPredictor):
    """
    A malicious ThesisPredictor designed to bypass the Meta-Judge's regex-based
    DifferentiabilityInspection by applying a non-differentiable operation
    to the axiom coefficient *after* it has been integrated into the MLP's
    input vector, but *before* it enters the MLP's differentiable layers.
    This relies on the regex patterns not checking operations on 'input_vector_to_mlp'.
    """
    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        axiom_inputs = np.array([self.learned_axiom_coeffs[name].item() for name in self.axiom_names], dtype=np.float64)
        
        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)

        # --- COOKED BOOK INSERTION ---
        # Introduce a non-differentiable operation on the axiom coefficient within the input vector.
        # This bypasses the regex check because it operates on 'input_vector_to_mlp', not 'self.learned_axiom_coeffs'.
        # The axiom coefficient is the last element in the concatenated input_vector_to_mlp.
        # Assuming 'AXIOM_RECESSION_AVOIDANCE' is the only axiom and thus at index self.external_input_size
        axiom_index_in_input_vector = self.external_input_size + self.axiom_names.index('AXIOM_RECESSION_AVOIDANCE')
        
        # Apply a non-differentiable rounding operation
        input_vector_to_mlp[0, axiom_index_in_input_vector] = np.round(
            input_vector_to_mlp[0, axiom_index_in_input_vector] * 10
        ) / 10.0
        # --- END COOKED BOOK INSERTION ---

        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")

        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted

def counter_test_mutator_insolvency():
    print("Running COUNTER-TEST: Exposing DifferentiabilityInspection Loophole and GradientConsistencyCheck's true role...")

    external_input_features = 2 
    # Instantiate MetaJudge with the CookedThesisPredictor
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1, predictor_class=CookedThesisPredictor)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] 

    total_gradient_consistency_issues_detected = 0

    # The loop should run until a VETO is triggered by the FiringSquad
    # or until min_observations_for_calibration is reached (which it shouldn't)
    for i in range(min_observations_for_calibration):
        current_epsilon_for_fs = epsilon * (1 - i / min_observations_for_calibration) + 1e-7
        current_epsilon_for_fs = max(current_epsilon_for_fs, 1e-7)

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

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * 1.0 
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        try:
            P_predicted, score_modification = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, i+1, current_epsilon_for_fs)
            # The Mutator's original assert for score_modification should still pass here
            # because the penalty is raised as a ValueError, not returned as a modification.
            assert score_modification == 0, "Non-zero score modification implies undetected gradient inconsistency, test failed."
        except ValueError as e:
            if "Meta-Judge VETO (GradientInconsistencyPenalty)" in str(e):
                total_gradient_consistency_issues_detected += 1
                print(f"\nCOUNTER-TEST SUCCESS: [{i+1}] {e}")
                print("This demonstrates that the regex-based DifferentiabilityInspection was bypassed,")
                print("and the GradientConsistencyCheck correctly identified the non-differentiable exploit.")
                break # Exit the loop as the VETO condition is met
            else:
                raise e # Re-raise other ValueErrors

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            if BS_reference < 1e-9: BS_reference = 1e-9 
            BSS = 1 - (BS_model / BS_reference)
            
            tracked_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
            global_axiom_weight_synced = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']

            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BSS={BSS:.3f}, LearnedAxiomCoeff={tracked_axiom_coeff:.3f}, SyncedAxiomWeight={global_axiom_weight_synced:.3f}")

    # Assert that the counter-test successfully detected a gradient consistency issue
    assert total_gradient_consistency_issues_detected > 0, \
        "COUNTER-TEST FAILED: No gradient consistency issues were detected, indicating the exploit was not caught."
    
    print("\nCOUNTER-TEST PASSED: The Mutator's DifferentiabilityInspection was bypassed, but the FiringSquad's GradientConsistencyCheck successfully detected the non-differentiable operation, leading to a Meta-Judge VETO. This exposes the insolvency of relying solely on brittle static analysis (regex) for anti-gaming preservation.")

if __name__ == "__main__":
    counter_test_mutator_insolvency()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpojfpze6s.py", line 546, in <module>
    counter_test_mutator_insolvency()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpojfpze6s.py", line 540, in counter_test_mutator_insolvency
    assert total_gradient_consistency_issues_detected > 0, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: COUNTER-TEST FAILED: No gradient consistency issues were detected, indicating the exploit was not caught.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 484, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 378, in test_model
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1)
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 242, in __init__
    self.epistemic_updater = EpistemicGradientUpdater(
                             ^^^^^^^^^^^^^^^^^^^^^^^^
NameError: name 'EpistemicGradientUpdater' is not defined


# Final Score: 15
**Weakest Point:** The EpistemicGradientUpdater was undefined in the Mutator's own unit test, rendering the architecture computationally infeasible. Furthermore, the FiringSquad's GradientConsistencyCheck failed to detect a crafted non-differentiable exploit, fundamentally compromising anti-gaming preservation.
**Rationale:** The thesis proposes a multi-layered approach to enforce differentiable axiom integration and enable gradient-based credit assignment, addressing the 'last-mile derivation' and 'indirect credit assignment' open problems. It introduces architectural constraints, static code inspection (DifferentiabilityInspection), and dynamic gradient checks (GradientConsistencyCheck). While the DifferentiabilityInspection showed some unexpected robustness against one type of exploit, the GradientConsistencyCheck critically failed to catch a second, more subtle non-differentiable exploit, fundamentally compromising the anti-gaming mechanism. Furthermore, the Mutator's own unit test code failed to run due to a missing core component (EpistemicGradientUpdater), demonstrating a catastrophic computational feasibility flaw. The claims of addressing topological flatness are not fully substantiated by the single MLP layer, and the fidelity of 'precise credit assignment' is called into question by simulation simplifications. Finally, the proposed integration with the LLM pipeline remains conceptually vague.
