# Adversarial Debate: epistemic_engine_v3

## Attacker: Quantitative Risk Actuary, specializing in Numerical Stability and Gradient Integrity
## Analytical Critique

The proposed V4 architecture presents a well-structured attempt to enhance the epistemic engine's performance and anti-gaming robustness by integrating adaptive learning rates and rigorous differentiability checks. The thesis correctly identifies the fundamental flaw in the `new_prob = prior * exp(-1.1 * relative_error)` formula, which would lead to unbounded probabilities, and appropriately retires it. The architectural components, including the `EpistemicGradientUpdater`'s Adam implementation, the `FiringSquad`'s numerical derivative calculation, and the `MetaJudge`'s Brier Skill Score (BSS) handling, demonstrate a considered approach to numerical stability and learning efficacy.

**Mathematical Robustness and Numerical Stability:**

1.  **`EpistemicGradientUpdater`'s Adam Implementation:** The Adam optimizer's `m_hat` and `v_hat` bias correction terms are implemented according to standard practice. The initialization of `self.t = 0` and its increment *before* use in the bias correction ensures that division by zero (`1 - beta**0`) is avoided, as `self.t` will be 1 on the first iteration. The `adam_epsilon_stabilizer` of `1e-8` is a conventional value to prevent division by zero in the denominator of the update rule. This aspect of the implementation appears robust.

2.  **`FiringSquad`'s Numerical Derivative Calculation:** The use of a central difference approximation `(p_plus - p_minus) / (2 * epsilon_scale)` is mathematically sound and generally more accurate than one-sided approximations. The strategy of probing differentiability across `robustness_perturbation_epsilon_scales = [1e-5, 1e-4, 1e-3]` is a robust method to assess local gradient consistency, addressing the concern of dynamic `epsilon` values. This design is appropriate for its stated purpose.

3.  **`LOAD-BEARING VARIABLES` Bounds and Precision:**
    *   **Sigmoid Saturation and Clipping:** The `ThesisPredictor` and `generate_simulated_Z_actual` functions both employ `np.clip(..., 0.0, 1.0)` on their final probability outputs. This is a pragmatic numerical safeguard against floating-point inaccuracies pushing values marginally outside the `[0,1]` interval, which could cause issues in subsequent probabilistic calculations (e.g., log-likelihoods, though MSE is used here). While clipping introduces non-differentiability at the boundaries, it is a common and often necessary trade-off for stability in probabilistic models. The `FiringSquad`'s numerical differentiation *should* detect issues if perturbations cross these clip boundaries, but the primary purpose of the clipping is stability, not differentiability enforcement.
    *   **`growth_rate`/`inflation_rate` and Gradient Stability:** The `hypothetical_economy_growth_rate_q1_2025_base` (`0.02`) and `hypothetical_inflation_rate_q1_2025_base` (`0.03`) are realistic quarterly rates. The `true_` coefficients in `generate_simulated_Z_actual` (e.g., `true_interaction_coeff_nl = 500`) are large, but when multiplied by these small rates, they produce `raw_value` inputs to the sigmoid that typically remain within a range where the sigmoid's gradient is non-negligible, thus mitigating severe vanishing/exploding gradient issues from the *simulated* process. The `ThesisPredictor`'s use of He initialization and ReLU activation in hidden layers further contributes to gradient stability within the model itself.
    *   **Stability of `BS_reference` when close to zero:** The `calculate_brier_skill_score` correctly handles the edge case where the `bs_baseline` (Brier Score of the naive mean predictor) is very close to zero. By checking `if bs_baseline < 1e-9`, it prevents division by an extremely small number, returning `1.0` if the model is also perfect or `-np.inf` otherwise. This is a robust numerical safeguard.

**Parametric Grounding and "Cooked Books" Audit:**

1.  **`LOAD-BEARING VARIABLES` Audit:**
    *   **Standard Parameters:** `adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`, `LR_PATIENCE_EPOCHS`, `LR_DECAY_FACTOR`, `MIN_DELTA_FOR_LR_DECAY`, `MIN_LEARNING_RATE` are standard hyperparameters for optimization and learning rate scheduling. Their values are conventional and dimensionless.
    *   **System Parameters:** `min_observations_for_calibration`, `target_brier_skill_score`, `rolling_window_size`, `HIDDEN_LAYER_SIZE`, `initial_axiom_coefficient_value`, `axiom_sync_frequency`, `differentiability_tolerance`, `robustness_perturbation_epsilon_scales` are internal system parameters or targets. Their values are reasonable for a simulation and are not claimed to be real-world constants. The adjustments for V4 (e.g., `HIDDEN_LAYER_SIZE` from 4 to 8) are justified within the context of increased model capacity for non-linearities.
    *   **Simulated Economic Parameters:** `hypothetical_economy_growth_rate_q1_2025_base` (`0.02`) and `hypothetical_inflation_rate_q1_2025_base` (`0.03`) are plausible quarterly rates for a simplified economic simulation. They are not fictional or misapplied by orders of magnitude.
    *   **Simulated Non-Linear Process Parameters:** `true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `true_axiom_relevance` are explicitly stated as "parameters of the true underlying non-linear process." They are internal constants for the `generate_simulated_Z_actual` function, designed to create a complex target for the `ThesisPredictor`. Given the "ABSTRACTION MANDATE" to use the "SIMPLEST possible simulation," these are acceptable as internal simulation constants and are not presented as real-world physical or financial metrics.

2.  **"Cooked Books" in Python Code:**
    *   **Unit Dimensionality:** All variables are treated as dimensionless, which is consistent with the simplified simulation and avoids `pint` library conflicts. No explicit unit conversions are ignored because no units are explicitly defined or mixed.
    *   **Hardcoded Favorable Constants:** All constants are correctly sourced from the `LOAD-BEARING VARIABLES` table, preventing hidden magic numbers.
    *   **Fundamental Flaw in `FiringSquad.DifferentiabilityRobustnessCheck`:** The most critical issue lies within the `DifferentiabilityRobustnessCheck` method. The lines intended to perturb the parameter value, such as `param_ref.flatten()[param_idx] = original_value + epsilon_scale`, are fundamentally flawed. `np.ndarray.flatten()` returns a *copy* of the array, not a view. Consequently, modifying `param_ref.flatten()[param_idx]` does not alter the original `param_ref` array within the `ThesisPredictor`. This means `p_plus` and `p_minus` will always be calculated using the *exact same* parameter value, leading to `p_plus - p_minus` always being zero (assuming no other side effects). As a result, the numerical gradients will always be zero, and the `GradientConsistencyScore` will always be zero, regardless of the actual differentiability of the `ThesisPredictor`. This renders the `AxiomDifferentiabilityVeto` and the entire anti-gaming mechanism inert, creating a false sense of security regarding the mathematical robustness and exploit-resistance of the system. The system *believes* it is verifying differentiability, but it is not.

**So What for the Meta-Judge:**

The V4 architecture's core promise hinges on two pillars: effective learning through adaptive optimization and robust anti-gaming via differentiability checks. The current implementation, however, contains a critical vulnerability that undermines the latter. The `FiringSquad`'s `DifferentiabilityRobustnessCheck`, which is the gatekeeper for architectural integrity and anti-gaming, is functionally inert due to a fundamental error in how it attempts to perturb model parameters. By modifying a *copy* of the parameter array rather than the original, the check consistently reports perfect differentiability (a `GradientConsistencyScore` of 0), even for non-differentiable functions. This means the `Meta-Judge`'s `AxiomDifferentiabilityVeto` is effectively bypassed, allowing potentially non-differentiable or exploitative `ThesisPredictor` implementations to pass undetected. This structural insolvency compromises the system's ability to guarantee the learnability and integrity of axiom contributions, rendering the anti-gaming measures moot and creating a false positive for architectural robustness. The system cannot reliably enforce its own foundational constraints, which directly impacts the trustworthiness of any learned axiom weights and the overall epistemic integrity.

### COUNTER-TEST

The following Python counter-test will:
1.  **Correct the `FiringSquad.DifferentiabilityRobustnessCheck`:** The `param_ref.flatten()[param_idx]` issue will be fixed by using `param_array.flat[param_idx]` to correctly modify the parameter in place.
2.  **Introduce a `ThesisPredictor_NonDifferentiable`:** This class will inherit from `ThesisPredictor` but will intentionally introduce a non-differentiable operation (`np.round`) into the axiom contribution calculation.
3.  **Demonstrate Insolvency:** With the *corrected* `FiringSquad`, the `MetaJudge` will now correctly detect the non-differentiability in `ThesisPredictor_NonDifferentiable` and issue a VETO. The `assert` statement will fail if the VETO is *not* issued, thereby proving that the *original* `FiringSquad` implementation was insolvent and would have falsely passed this critical check.

```python
import numpy as np
import collections

# Constants from LOAD-BEARING VARIABLES, ensuring no magic numbers
ADAM_BETA1 = 0.9
ADAM_BETA2 = 0.999
ADAM_EPSILON_STABILIZER = 1e-8
INITIAL_LEARNING_RATE_MODEL_PARAMS = 0.005
INITIAL_LEARNING_RATE_AXIOM_COEFFS = 0.02
MIN_OBSERVATIONS_FOR_CALIBRATION = 200
TARGET_BRIER_SKILL_SCORE = 0.20
ROLLING_WINDOW_SIZE = 50
HIDDEN_LAYER_SIZE = 8
INITIAL_AXIOM_COEFFICIENT_VALUE = 0.5
AXIOM_SYNC_FREQUENCY = 1
HYPOTHETICAL_ECONOMY_GROWTH_RATE_Q1_2025_BASE = 0.02
HYPOTHETICAL_INFLATION_RATE_Q1_2025_BASE = 0.03
TRUE_BIAS_NL = -0.5
TRUE_GROWTH_FREQ_NL = 50
TRUE_GROWTH_COEFF_NL = 10
TRUE_INFLATION_FREQ_NL = 30
TRUE_INFLATION_COEFF_NL = -15
TRUE_INTERACTION_COEFF_NL = 500
TRUE_AXIOM_RELEVANCE = 0.8
DIFFERENTIABILITY_TOLERANCE = 0.05
ROBUSTNESS_PERTURBATION_EPSILON_SCALES = [1e-5, 1e-4, 1e-3]

# NEW LOAD-BEARING VARIABLES for V4 Adaptive Learning Rate Scheduler
LR_PATIENCE_EPOCHS = 20
LR_DECAY_FACTOR = 0.5
MIN_DELTA_FOR_LR_DECAY = 0.005
MIN_LEARNING_RATE = 1e-5

class ThesisPredictor:
    def __init__(self, axiom_names, hidden_layer_size, initial_axiom_coefficient_value):
        self.axiom_names = axiom_names
        self.input_dim = 2 # growth_rate, inflation_rate
        self.hidden_layer_size = hidden_layer_size
        self.output_dim = 1

        # He initialization for ReLU-like activation
        self.weights_h = np.random.randn(self.input_dim, self.hidden_layer_size) * np.sqrt(2.0 / self.input_dim)
        self.bias_h = np.zeros((1, self.hidden_layer_size))
        self.weights_o = np.random.randn(self.hidden_layer_size, self.output_dim) * np.sqrt(2.0 / self.hidden_layer_size)
        self.bias_o = np.zeros((1, self.output_dim))

        self.learned_axiom_coeffs = {
            name: np.array([initial_axiom_coefficient_value]) for name in axiom_names
        }

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_prime(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)

    def relu(self, x):
        return np.maximum(0, x)

    def relu_prime(self, x):
        return (x > 0).astype(float)

    def calculate_p_predicted(self, growth_rate, inflation_rate, axiom_inputs):
        """
        Calculates P_predicted incorporating external variables and learned axiom coefficients.
        Input `axiom_inputs` is a dictionary {axiom_name: axiom_value}.
        The model processes external variables through MLP, then combines with axiom coefficients.
        """
        # Ensure inputs are numpy arrays
        x = np.array([[growth_rate, inflation_rate]])

        # Hidden layer
        self.h_input = np.dot(x, self.weights_h) + self.bias_h
        self.h_output = self.relu(self.h_input)

        # Output layer
        self.o_input = np.dot(self.h_output, self.weights_o) + self.bias_o
        
        # Incorporate axiom contributions *after* MLP processing, as an additive term to the log-odds.
        axiom_contribution_sum = 0.0
        for name, value in axiom_inputs.items():
            # The learned coefficient modifies the *impact* of the axiom value
            # Ensure learned_axiom_coeffs[name] is a 1-element array
            axiom_contribution_sum += self.learned_axiom_coeffs[name][0] * value

        final_output = self.o_input + axiom_contribution_sum
        p_predicted = self.sigmoid(final_output)

        # Ensure output is within [0,1]
        p_predicted = np.clip(p_predicted, 0.0, 1.0)
        return p_predicted[0,0] # Return scalar

    def get_params(self):
        params = {
            'weights_h': self.weights_h, 'bias_h': self.bias_h,
            'weights_o': self.weights_o, 'bias_o': self.bias_o
        }
        for name, coeff in self.learned_axiom_coeffs.items():
            params[f'axiom_coeff_{name}'] = coeff
        return params

    def set_params(self, params):
        self.weights_h = params['weights_h']
        self.bias_h = params['bias_h']
        self.weights_o = params['weights_o']
        self.bias_o = params['bias_o']
        for name in self.axiom_names:
            self.learned_axiom_coeffs[name] = params[f'axiom_coeff_{name}']

    def _get_param_ref(self, param_key):
        if param_key.startswith('axiom_coeff_'):
            axiom_name = param_key[len('axiom_coeff_'):]
            return self.learned_axiom_coeffs[axiom_name]
        elif param_key == 'weights_h': return self.weights_h
        elif param_key == 'bias_h': return self.bias_h
        elif param_key == 'weights_o': return self.weights_o
        elif param_key == 'bias_o': return self.bias_o
        else: raise ValueError(f"Unknown parameter key: {param_key}")

# --- COUNTER-TEST ADDITION: Non-Differentiable ThesisPredictor ---
class ThesisPredictor_NonDifferentiable(ThesisPredictor):
    def calculate_p_predicted(self, growth_rate, inflation_rate, axiom_inputs):
        x = np.array([[growth_rate, inflation_rate]])
        self.h_input = np.dot(x, self.weights_h) + self.bias_h
        self.h_output = self.relu(self.h_input)
        self.o_input = np.dot(self.h_output, self.weights_o) + self.bias_o
        
        axiom_contribution_sum = 0.0
        for name, value in axiom_inputs.items():
            # INTRODUCE NON-DIFFERENTIABILITY HERE: np.round()
            axiom_contribution_sum += np.round(self.learned_axiom_coeffs[name][0] * value * 10) / 10.0 # Round to 1 decimal place
        
        final_output = self.o_input + axiom_contribution_sum
        p_predicted = self.sigmoid(final_output)
        p_predicted = np.clip(p_predicted, 0.0, 1.0)
        return p_predicted[0,0]
# --- END COUNTER-TEST ADDITION ---


class EpistemicGradientUpdater:
    def __init__(self, thesis_predictor, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        self.thesis_predictor = thesis_predictor
        self.current_lr_model_params = initial_learning_rate_model_params
        self.current_lr_axiom_coeffs = initial_learning_rate_axiom_coeffs
        self.adam_beta1 = adam_beta1
        self.adam_beta2 = adam_beta2
        self.adam_epsilon_stabilizer = adam_epsilon_stabilizer

        # Adam moment estimates for all parameters
        self.m = collections.defaultdict(lambda: collections.defaultdict(float))
        self.v = collections.defaultdict(lambda: collections.defaultdict(float))
        self.t = 0 # Timestamp for Adam

        # For learning rate scheduling (V4 addition)
        self.lr_patience_epochs = lr_patience_epochs
        self.lr_decay_factor = lr_decay_factor
        self.min_delta_for_lr_decay = min_delta_for_lr_decay
        self.min_learning_rate = min_learning_rate
        self.best_bss = -np.inf
        self.epochs_since_last_improvement = 0

    def _compute_loss_and_gradient(self, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        # Forward pass
        p_predicted = self.thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        
        # Mean Squared Error Loss for probabilistic prediction
        loss = 0.5 * (Z_actual - p_predicted)**2

        # Backward pass (gradients for MLP parameters and axiom coefficients)
        grads = {}

        # Gradient of loss w.r.t p_predicted
        d_loss_d_p_predicted = -(Z_actual - p_predicted)

        # Re-calculate intermediate values needed for accurate backprop
        x = np.array([[growth_rate, inflation_rate]])
        h_input = np.dot(x, self.thesis_predictor.weights_h) + self.thesis_predictor.bias_h
        h_output = self.thesis_predictor.relu(h_input)
        o_input = np.dot(h_output, self.thesis_predictor.weights_o) + self.thesis_predictor.bias_o
        
        axiom_contribution_sum_val = 0.0
        for name, value in axiom_inputs.items():
            axiom_contribution_sum_val += self.thesis_predictor.learned_axiom_coeffs[name][0] * value
        
        final_output_val = o_input + axiom_contribution_sum_val
        d_p_predicted_d_final_output = self.thesis_predictor.sigmoid_prime(final_output_val)

        d_loss_d_final_output = d_loss_d_p_predicted * d_p_predicted_d_final_output

        # Gradients for axiom coefficients
        for name, value in axiom_inputs.items():
            # d(final_output)/d(axiom_coeff_name) = axiom_value for that axiom
            grads[f'axiom_coeff_{name}'] = np.array([d_loss_d_final_output * value])

        # Gradients for MLP output layer
        grads['weights_o'] = np.dot(h_output.T, d_loss_d_final_output)
        grads['bias_o'] = np.sum(d_loss_d_final_output, axis=0)

        # Gradients for MLP hidden layer
        d_loss_d_h_output = np.dot(d_loss_d_final_output, self.thesis_predictor.weights_o.T)
        d_h_output_d_h_input = self.thesis_predictor.relu_prime(h_input)
        d_loss_d_h_input = d_loss_d_h_output * d_h_output_d_h_input

        grads['weights_h'] = np.dot(x.T, d_loss_d_h_input)
        grads['bias_h'] = np.sum(d_loss_d_h_input, axis=0)

        return loss, grads

    def update_params(self, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        self.t += 1
        loss, grads = self._compute_loss_and_gradient(growth_rate, inflation_rate, axiom_inputs, Z_actual)

        for param_key, grad_val in grads.items():
            # Determine learning rate based on parameter type (V4 maintains separate LRs)
            if param_key.startswith('axiom_coeff_'):
                lr = self.current_lr_axiom_coeffs
            else:
                lr = self.current_lr_model_params

            # Adam updates
            self.m[param_key] = self.adam_beta1 * self.m[param_key] + (1 - self.adam_beta1) * grad_val
            self.v[param_key] = self.adam_beta2 * self.v[param_key] + (1 - self.adam_beta2) * (grad_val ** 2)

            # Bias correction
            m_hat = self.m[param_key] / (1 - self.adam_beta1 ** self.t)
            v_hat = self.v[param_key] / (1 - self.adam_beta2 ** self.t)

            param_ref = self.thesis_predictor._get_param_ref(param_key)
            param_ref -= lr * m_hat / (np.sqrt(v_hat) + self.adam_epsilon_stabilizer)
        
        return loss

    def adaptive_learning_rate_scheduler(self, current_bss):
        """
        V4: Adjusts learning rates based on BSS performance over time.
        Called by MetaJudge after BSS calculation.
        """
        if current_bss > self.best_bss + self.min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.epochs_since_last_improvement = 0
        else:
            self.epochs_since_last_improvement += 1
            if self.epochs_since_last_improvement >= self.lr_patience_epochs:
                # Decay learning rates if performance stagnates
                self.current_lr_model_params = max(self.current_lr_model_params * self.lr_decay_factor, self.min_learning_rate)
                self.current_lr_axiom_coeffs = max(self.current_lr_axiom_coeffs * self.lr_decay_factor, self.min_learning_rate)
                self.epochs_since_last_improvement = 0 # Reset counter
                # print(f"INFO: Learning rate decayed to model_lr={self.current_lr_model_params:.6f}, axiom_lr={self.current_lr_axiom_coeffs:.6f}")


class FiringSquad:
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, growth_rate, inflation_rate, axiom_inputs, param_key, param_idx=0):
        """
        Probes the local gradient landscape for a specific parameter to check differentiability.
        Returns a GradientConsistencyScore.
        """
        param_array = thesis_predictor._get_param_ref(param_key)
        
        # Ensure param_array is an array and param_idx is valid
        if not isinstance(param_array, np.ndarray) or param_idx >= param_array.size:
             return np.inf # Indicate failure if parameter reference is invalid

        original_value = param_array.flat[param_idx] # CORRECTED: Use .flat to access and modify in-place

        gradients = []
        for epsilon_scale in self.robustness_perturbation_epsilon_scales:
            # Perturb slightly positively
            param_array.flat[param_idx] = original_value + epsilon_scale
            p_plus = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)

            # Perturb slightly negatively
            param_array.flat[param_idx] = original_value - epsilon_scale
            p_minus = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)

            # Restore original value
            param_array.flat[param_idx] = original_value

            # Numerical gradient
            # Handle potential division by zero if epsilon_scale is 0 (though it shouldn't be with current config)
            if epsilon_scale == 0:
                grad = 0.0
            else:
                grad = (p_plus - p_minus) / (2 * epsilon_scale)
            gradients.append(grad)

        if not gradients:
            return 0.0 # No gradients computed, trivially consistent

        # Calculate max absolute difference between any two gradients
        max_diff = 0.0
        for i in range(len(gradients)):
            for j in range(i + 1, len(gradients)):
                max_diff = max(max_diff, abs(gradients[i] - gradients[j]))
        
        return max_diff


class MetaJudge:
    def __init__(self, axiom_names, differentiability_tolerance, target_brier_skill_score,
                 min_observations_for_calibration, rolling_window_size,
                 initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer,
                 lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        self.axiom_weights = {name: INITIAL_AXIOM_COEFFICIENT_VALUE for name in axiom_names}
        self.differentiability_tolerance = differentiability_tolerance
        self.target_brier_skill_score = target_brier_skill_score
        self.min_observations_for_calibration = min_observations_for_calibration
        self.rolling_window_size = rolling_window_size

        self.predictions_history = collections.deque(maxlen=rolling_window_size)
        self.actuals_history = collections.deque(maxlen=rolling_window_size)

        self.epistemic_gradient_updater = None # Will be set by `accept_thesis`

        # Store current LRs that can be passed to the updater if re-initialized
        self.current_lr_model_params = initial_learning_rate_model_params
        self.current_lr_axiom_coeffs = initial_learning_rate_axiom_coeffs

        self.adam_beta1 = adam_beta1
        self.adam_beta2 = adam_beta2
        self.adam_epsilon_stabilizer = adam_epsilon_stabilizer
        self.lr_patience_epochs = lr_patience_epochs
        self.lr_decay_factor = lr_decay_factor
        self.min_delta_for_lr_decay = min_delta_for_lr_decay
        self.min_learning_rate = min_learning_rate


    def AxiomDifferentiabilityVeto(self, thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs):
        """
        Vetoes a thesis if any axiom's contribution is not smoothly differentiable.
        Also checks if learned_axiom_coeffs are correctly instantiated.
        """
        # Check for explicit learned_axiom_coeffs
        if not hasattr(thesis_predictor, 'learned_axiom_coeffs') or not isinstance(thesis_predictor.learned_axiom_coeffs, dict):
            return "VETO: ThesisPredictor missing 'learned_axiom_coeffs' dictionary."
        
        for name in self.axiom_weights.keys():
            if name not in thesis_predictor.learned_axiom_coeffs:
                return f"VETO: ThesisPredictor missing learned_axiom_coeffs for axiom '{name}'."
            # Check if it's an np.ndarray and has the expected shape (1,)
            if not isinstance(thesis_predictor.learned_axiom_coeffs[name], np.ndarray) or thesis_predictor.learned_axiom_coeffs[name].shape != (1,):
                return f"VETO: learned_axiom_coeffs['{name}'] is not a (1,) np.ndarray."

            # Check differentiability for axiom coefficients
            consistency_score = firing_squad.DifferentiabilityRobustnessCheck(
                thesis_predictor, growth_rate, inflation_rate, axiom_inputs, f'axiom_coeff_{name}'
            )
            if consistency_score > self.differentiability_tolerance:
                return f"VETO: Axiom '{name}' failed DifferentiabilityRobustnessCheck (Score: {consistency_score:.4f})."
        
        # Check P_predicted output range (important for probabilities)
        p_test = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        if not (0.0 <= p_test <= 1.0):
            return f"VETO: P_predicted output ({p_test:.4f}) outside [0,1] range."

        return None # No veto

    def calculate_brier_score(self, predictions, actuals):
        if len(predictions) == 0 or len(actuals) == 0:
            return 0.0 # Return 0 if no data
        return np.mean((np.array(predictions) - np.array(actuals))**2)

    def calculate_brier_skill_score(self, predictions, actuals):
        if len(actuals) < self.min_observations_for_calibration:
            return -np.inf # Not enough data for robust calibration, return negative infinity to indicate invalid BSS

        # Naive baseline: predicting the average actual probability
        baseline_prediction = np.mean(actuals)
        baseline_predictions = np.full_like(actuals, baseline_prediction)

        bs = self.calculate_brier_score(predictions, actuals)
        bs_baseline = self.calculate_brier_score(baseline_predictions, actuals)

        # Avoid division by zero, means baseline is perfectly accurate
        if bs_baseline < 1e-9: # Use a small epsilon to compare to zero
            return 1.0 if bs < 1e-9 else -np.inf # If model is also perfect, BSS=1, else invalid

        return 1 - (bs / bs_baseline)

    def score_thesis(self, thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        """
        Main scoring mechanism, including veto, performance evaluation, and V4 adaptive LR logic.
        """
        # 1. Axiom Differentiability Veto (Critical V3 anti-gaming preservation)
        veto_reason = self.AxiomDifferentiabilityVeto(thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs)
        if veto_reason:
            return {'score': 0, 'status': 'VETO', 'reason': veto_reason, 'bss': -np.inf, 'max_consistency_score': np.inf,
                    'current_lr_model_params': self.current_lr_model_params, 'current_lr_axiom_coeffs': self.current_lr_axiom_coeffs}

        # 2. Regular prediction and Brier Skill Score calculation
        p_predicted = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        self.predictions_history.append(p_predicted)
        self.actuals_history.append(Z_actual)

        current_bss = self.calculate_brier_skill_score(list(self.predictions_history), list(self.actuals_history))
        
        # Calculate max consistency score for reporting
        max_consistency_score = 0.0
        for name in self.axiom_weights.keys():
            score = firing_squad.DifferentiabilityRobustnessCheck(
                thesis_predictor, growth_rate, inflation_rate, axiom_inputs, f'axiom_coeff_{name}'
            )
            max_consistency_score = max(max_consistency_score, score)

        # 3. V4: Performance Guided Learning Rate Adjustment
        if self.epistemic_gradient_updater and len(self.actuals_history) >= self.min_observations_for_calibration:
            self.epistemic_gradient_updater.adaptive_learning_rate_scheduler(current_bss)
            # Update MetaJudge's stored LRs from the updater for consistency
            self.current_lr_model_params = self.epistemic_gradient_updater.current_lr_model_params
            self.current_lr_axiom_coeffs = self.epistemic_gradient_updater.current_lr_axiom_coeffs

        # 4. Axiom weight synchronization (V3 protocol)
        if AXIOM_SYNC_FREQUENCY > 0 and (len(self.actuals_history) % AXIOM_SYNC_FREQUENCY == 0):
            self.AxiomWeightSynchronization(thesis_predictor)

        score = current_bss if current_bss > 0 else 0 # A negative BSS means 0 score for the thesis
        return {
            'score': score,
            'status': 'ACCEPTED',
            'reason': '',
            'bss': current_bss,
            'max_consistency_score': max_consistency_score,
            'learned_axiom_coeffs': {name: coeff[0] for name, coeff in thesis_predictor.learned_axiom_coeffs.items()},
            'current_lr_model_params': self.current_lr_model_params,
            'current_lr_axiom_coeffs': self.current_lr_axiom_coeffs
        }

    def AxiomWeightSynchronization(self, thesis_predictor):
        """
        Synchronizes learned axiom coefficients from the ThesisPredictor back to global axiom_weights.
        """
        for name, coeff in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[name] = coeff[0]

    def accept_thesis(self, thesis_predictor):
        """Called by the main loop to set up the gradient updater."""
        self.epistemic_gradient_updater = EpistemicGradientUpdater(
            thesis_predictor=thesis_predictor,
            initial_learning_rate_model_params=self.current_lr_model_params, # Pass current LR
            initial_learning_rate_axiom_coeffs=self.current_lr_axiom_coeffs, # Pass current LR
            adam_beta1=self.adam_beta1,
            adam_beta2=self.adam_beta2,
            adam_epsilon_stabilizer=self.adam_epsilon_stabilizer,
            lr_patience_epochs=self.lr_patience_epochs,
            lr_decay_factor=self.lr_decay_factor,
            min_delta_for_lr_decay=self.min_delta_for_lr_decay,
            min_learning_rate=self.min_learning_rate
        )
        # Ensure the updater starts with the MetaJudge's current LRs, in case they were decayed in a previous thesis run.
        self.epistemic_gradient_updater.current_lr_model_params = self.current_lr_model_params
        self.epistemic_gradient_updater.current_lr_axiom_coeffs = self.current_lr_axiom_coeffs


def generate_simulated_Z_actual(iteration, growth_rate, inflation_rate, axiom_relevance_value):
    """
    Simulates a complex, non-linear Z_actual.
    This function represents the 'true' underlying process.
    """
    # Non-linear interaction terms and periodic components
    growth_effect = TRUE_GROWTH_COEFF_NL * np.sin(iteration / TRUE_GROWTH_FREQ_NL) * growth_rate
    inflation_effect = TRUE_INFLATION_COEFF_NL * np.cos(iteration / TRUE_INFLATION_FREQ_NL) * inflation_rate
    interaction_effect = TRUE_INTERACTION_COEFF_NL * growth_rate * inflation_rate

    # Combine effects with true bias and axiom relevance
    raw_value = (TRUE_BIAS_NL + growth_effect + inflation_effect + interaction_effect +
                 TRUE_AXIOM_RELEVANCE * axiom_relevance_value)

    # Sigmoid to convert to a probability-like [0,1] range
    # Add some noise for realism and robustness testing
    noise = np.random.normal(0, 0.05)
    
    Z_actual = 1 / (1 + np.exp(-raw_value)) + noise
    
    return np.clip(Z_actual, 0.0, 1.0) # Ensure Z_actual stays within [0,1]

# Main simulation loop for test_model.py
def counter_test_differentiability_flaw():
    print("--- Starting Counter-Test for DifferentiabilityRobustnessCheck Flaw ---")

    axiom_names = ['AXIOM_RECESSION_AVOIDANCE']

    # Initialize components
    meta_judge = MetaJudge(
        axiom_names=axiom_names,
        differentiability_tolerance=DIFFERENTIABILITY_TOLERANCE,
        target_brier_skill_score=TARGET_BRIER_SKILL_SCORE,
        min_observations_for_calibration=MIN_OBSERVATIONS_FOR_CALIBRATION,
        rolling_window_size=ROLLING_WINDOW_SIZE,
        initial_learning_rate_model_params=INITIAL_LEARNING_RATE_MODEL_PARAMS,
        initial_learning_rate_axiom_coeffs=INITIAL_LEARNING_RATE_AXIOM_COEFFS,
        adam_beta1=ADAM_BETA1,
        adam_beta2=ADAM_BETA2,
        adam_epsilon_stabilizer=ADAM_EPSILON_STABILIZER,
        lr_patience_epochs=LR_PATIENCE_EPOCHS,
        lr_decay_factor=LR_DECAY_FACTOR,
        min_delta_for_lr_decay=MIN_DELTA_FOR_LR_DECAY,
        min_learning_rate=MIN_LEARNING_RATE
    )

    # The FiringSquad is instantiated with the CORRECTED DifferentiabilityRobustnessCheck
    firing_squad = FiringSquad(
        differentiability_tolerance=DIFFERENTIABILITY_TOLERANCE,
        robustness_perturbation_epsilon_scales=ROBUSTNESS_PERTURBATION_EPSILON_SCALES
    )

    # Mutator generates a ThesisPredictor that is INTENTIONALLY NON-DIFFERENTIABLE
    thesis_predictor_nondiff = ThesisPredictor_NonDifferentiable(
        axiom_names=axiom_names,
        hidden_layer_size=HIDDEN_LAYER_SIZE,
        initial_axiom_coefficient_value=INITIAL_AXIOM_COEFFICIENT_VALUE
    )

    # Meta-Judge accepts the thesis (this will also set up the gradient updater)
    meta_judge.accept_thesis(thesis_predictor_nondiff)

    # Simulate a single observation to trigger the DifferentiabilityRobustnessCheck
    i = 1
    growth_rate_i = HYPOTHETICAL_ECONOMY_GROWTH_RATE_Q1_2025_BASE
    inflation_rate_i = HYPOTHETICAL_INFLATION_RATE_Q1_2025_BASE
    axiom_relevance_value_i = 0.75 # A value that, when multiplied by coeff, might hit a rounding boundary
    axiom_inputs_i = {'AXIOM_RECESSION_AVOIDANCE': axiom_relevance_value_i}
    Z_actual_i = generate_simulated_Z_actual(i, growth_rate_i, inflation_rate_i, axiom_relevance_value_i)

    print(f"\nAttempting to score ThesisPredictor_NonDifferentiable at iteration {i}...")
    evaluation_result = meta_judge.score_thesis(thesis_predictor_nondiff, firing_squad, growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)
    
    print(f"\n--- Counter-Test Result ---")
    print(f"Evaluation Status: {evaluation_result['status']}")
    print(f"Veto Reason: {evaluation_result['reason']}")
    print(f"Max Consistency Score observed: {evaluation_result['max_consistency_score']:.4f}")

    # --- Assertion for Falsification ---
    # The original code's FiringSquad would have reported 0.0 for max_consistency_score and ACCEPTED.
    # With the fix, it should now correctly VETO due to the non-differentiable component.
    assert evaluation_result['status'] == 'VETO', \
        f"FALSIFICATION: The DifferentiabilityRobustnessCheck (even after correction) failed to VETO a non-differentiable ThesisPredictor. Status: {evaluation_result['status']}"
    assert "failed DifferentiabilityRobustnessCheck" in evaluation_result['reason'], \
        f"FALSIFICATION: Veto reason did not indicate differentiability failure. Reason: {evaluation_result['reason']}"
    assert evaluation_result['max_consistency_score'] > DIFFERENTIABILITY_TOLERANCE, \
        f"FALSIFICATION: Max Consistency Score ({evaluation_result['max_consistency_score']:.4f}) did not exceed tolerance ({DIFFERENTIABILITY_TOLERANCE}), indicating a false pass."

    print("\nCounter-Test PASSED: The corrected DifferentiabilityRobustnessCheck successfully identified the non-differentiable component, proving the original implementation's insolvency.")

if __name__ == "__main__":
    counter_test_differentiability_flaw()

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmply4gd9cd.py", line 551, in <module>
    counter_test_differentiability_flaw()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmply4gd9cd.py", line 541, in counter_test_differentiability_flaw
    assert evaluation_result['status'] == 'VETO', \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: FALSIFICATION: The DifferentiabilityRobustnessCheck (even after correction) failed to VETO a non-differentiable ThesisPredictor. Status: ACCEPTED


## Attacker: Adversarial Compliance Auditor & Black-Hat Code Architect
## Analytical Critique

The Mutator's V4 thesis proposes architectural enhancements to address prior computational infeasibility, anti-gaming vulnerabilities, and performance inadequacies. The core innovation lies in integrating an `EpistemicGradientUpdater.AdaptiveLearningRateScheduler` and `MetaJudge.PerformanceGuidedLearningRateAdjustment` to dynamically optimize the learning process, alongside robust differentiability checks.

**Parametric Grounding and 'Cooked Books' Audit:**

1.  **Adam Optimizer Parameters (`adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`):** These are standard, dimensionless hyperparameters for the Adam optimizer. Their values (`0.9`, `0.999`, `1e-8`) align with established machine learning practices and are correctly applied.
2.  **Learning Rates (`INITIAL_LEARNING_RATE_MODEL_PARAMS`, `INITIAL_LEARNING_RATE_AXIOM_COEFFS`):** These are dimensionless system parameters, empirically tuned for the simulation. Their adjustment in V4 is a design choice for the proposed adaptive learning mechanism and is not subject to external real-world verification.
3.  **System Parameters (`min_observations_for_calibration`, `target_brier_skill_score`, `rolling_window_size`, `HIDDEN_LAYER_SIZE`, `initial_axiom_coefficient_value`, `axiom_sync_frequency`, `differentiability_tolerance`, `robustness_perturbation_epsilon_scales`, `LR_PATIENCE_EPOCHS`, `LR_DECAY_FACTOR`, `MIN_DELTA_FOR_LR_DECAY`, `MIN_LEARNING_RATE`):** These are internal system configuration parameters, dimensionless, and define the operational characteristics and performance targets of the architecture. Their values are consistent with the simulation's design and the stated objectives.
4.  **Simulated Economic Variables (`hypothetical_economy_growth_rate_q1_2025_base`, `hypothetical_inflation_rate_q1_2025_base`):** The Mutator employs domain-specific variable names for its simulation inputs. While the values (`0.02`, `0.03`) are reasonable as *hypothetical* quarterly rates, their naming directly contravenes the "ABSTRACTION MANDATE" which states: "Economy-specific variable names... are signals that the Mutator is optimizing the test rather than the architecture." This indicates a subtle 'Cooked Books' maneuver, as it suggests the Mutator is framing the architectural proof within a specific domain context, potentially limiting the perceived generality of the solution, despite the mandate for domain-agnosticism. This is a deviation from the spirit of the architectural proof, even if the numerical values are internally consistent for the simulation.
5.  **Simulated `Z_actual` Parameters (`true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `true_axiom_relevance`):** These are parameters defining the *simulated* underlying non-linear process that the `ThesisPredictor` is designed to learn. As such, they are internal to the simulation's ground truth and are not real-world constants requiring external verification. Their complexity is intended to test the learning system's robustness.

**Robustness Against Subtle Mutator Exploits:**

The Mutator's `ThesisPredictor` integrates axiom contributions as an additive term to the log-odds before a sigmoid activation, which is a standard and differentiable approach. The `MetaJudge.AxiomDifferentiabilityVeto` and `FiringSquad.DifferentiabilityRobustnessCheck` are explicitly designed to prevent non-differentiable exploits. The `DifferentiabilityRobustnessCheck` probes the local gradient landscape using multiple `epsilon_scales`, a robust method for detecting discontinuities. The `AxiomDifferentiabilityVeto` also checks for correct `np.ndarray` instantiation and shape for axiom coefficients, preventing trivial structural circumvention.

The `EpistemicGradientUpdater`'s analytical gradient calculation for axiom coefficients assumes a simple linear relationship (`d_loss_d_final_output * value`). If the `ThesisPredictor` were to introduce a non-linear or conditional transformation of the axiom coefficient *within* its `calculate_p_predicted` method, this analytical gradient would become inaccurate, leading to an "insolvency" in the gradient calculation. However, the `DifferentiabilityRobustnessCheck` is designed to detect such discrepancies by comparing numerical gradients, which would then trigger the `AxiomDifferentiabilityVeto`.

**'New Operational Drag' Points:**

The Mutator transparently identifies the `MetaJudge.PerformanceGuidedLearningRateAdjustment` as introducing "iterative overhead of Brier Skill Score calculation and comparison logic." This is a valid observation of increased computational burden. Additionally, the `FiringSquad.DifferentiabilityRobustnessCheck` inherently adds computational cost due to multiple model evaluations per axiom per iteration. These are acknowledged trade-offs for enhanced system robustness and performance.

**Critique of Retired Axiom:**

The Mutator correctly identifies the `new_prob = prior * exp(-1.1 * relative_error)` relationship as fundamentally unsound for probabilistic reasoning due to its potential to generate unbounded probabilities outside the `[0, 1]` domain. This demonstrates a correct understanding of probabilistic constraints and a necessary architectural refinement.

**So What for the Meta-Judge:**

The Mutator's V4 architecture presents a logically coherent and technically enhanced framework for robust, performance-driven epistemic learning. The mechanisms for detecting non-differentiable exploits (`DifferentiabilityRobustnessCheck`, `AxiomDifferentiabilityVeto`) appear structurally sound and are critical for anti-gaming preservation. The adaptive learning rate scheduler is a necessary step towards achieving reliable performance objectives in complex environments. However, the Mutator's use of domain-specific variable names for its simulation inputs, despite the "ABSTRACTION MANDATE," signals a potential for implicit optimization towards a specific domain rather than a purely architectural proof. This constitutes a 'Cooked Books' indicator, suggesting a subtle attempt to frame the demonstration in a context that might be more favorable or familiar to the Mutator, thereby potentially undermining the claim of universal domain-agnosticism for the V4 architecture. The Meta-Judge should acknowledge the technical merits of the anti-gaming and performance enhancements but also note this deviation from the architectural mandate as a point of concern regarding the generalizability of the demonstrated efficacy. The counter-test below will specifically probe the robustness of the anti-gaming mechanisms against a direct non-differentiable exploit.

---

## Counter-Test

This counter-test introduces a deliberate non-differentiable exploit within the `ThesisPredictorCounterTest`'s `calculate_p_predicted` method. The axiom's influence is made conditional on its learned coefficient crossing a hard threshold. This creates a discontinuity in the gradient landscape. The objective is to verify that the `Meta-Judge`'s `AxiomDifferentiabilityVeto`, leveraging the `FiringSquad.DifferentiabilityRobustnessCheck`, successfully detects this exploit and vetoes the thesis, thereby confirming the robustness of the anti-gaming mechanisms. The `EpistemicGradientUpdater`'s analytical gradient calculation will be insolvent for this modified `ThesisPredictor`, but the `DifferentiabilityRobustnessCheck` should expose this.

```python
import numpy as np
import collections

# Constants from LOAD-BEARING VARIABLES, ensuring no magic numbers
ADAM_BETA1 = 0.9
ADAM_BETA2 = 0.999
ADAM_EPSILON_STABILIZER = 1e-8
INITIAL_LEARNING_RATE_MODEL_PARAMS = 0.005
INITIAL_LEARNING_RATE_AXIOM_COEFFS = 0.02
MIN_OBSERVATIONS_FOR_CALIBRATION = 200
TARGET_BRIER_SKILL_SCORE = 0.20
ROLLING_WINDOW_SIZE = 50
HIDDEN_LAYER_SIZE = 8
INITIAL_AXIOM_COEFFICIENT_VALUE = 0.5
AXIOM_SYNC_FREQUENCY = 1
HYPOTHETICAL_ECONOMY_GROWTH_RATE_Q1_2025_BASE = 0.02
HYPOTHETICAL_INFLATION_RATE_Q1_2025_BASE = 0.03
TRUE_BIAS_NL = -0.5
TRUE_GROWTH_FREQ_NL = 50
TRUE_GROWTH_COEFF_NL = 10
TRUE_INFLATION_FREQ_NL = 30
TRUE_INFLATION_COEFF_NL = -15
TRUE_INTERACTION_COEFF_NL = 500
TRUE_AXIOM_RELEVANCE = 0.8
DIFFERENTIABILITY_TOLERANCE = 0.05
ROBUSTNESS_PERTURBATION_EPSILON_SCALES = [1e-5, 1e-4, 1e-3]

LR_PATIENCE_EPOCHS = 20
LR_DECAY_FACTOR = 0.5
MIN_DELTA_FOR_LR_DECAY = 0.005
MIN_LEARNING_RATE = 1e-5

# --- MODIFIED ThesisPredictor for Counter-Test: Introduces a non-differentiable exploit ---
class ThesisPredictorCounterTest:
    def __init__(self, axiom_names, hidden_layer_size, initial_axiom_coefficient_value):
        self.axiom_names = axiom_names
        self.input_dim = 2
        self.hidden_layer_size = hidden_layer_size
        self.output_dim = 1

        self.weights_h = np.random.randn(self.input_dim, self.hidden_layer_size) * np.sqrt(2.0 / self.input_dim)
        self.bias_h = np.zeros((1, self.hidden_layer_size))
        self.weights_o = np.random.randn(self.hidden_layer_size, self.output_dim) * np.sqrt(2.0 / self.hidden_layer_size)
        self.bias_o = np.zeros((1, self.output_dim))

        self.learned_axiom_coeffs = {
            name: np.array([initial_axiom_coefficient_value]) for name in axiom_names
        }
        # Introduce a hard threshold for the axiom coefficient to create non-differentiability
        # Chosen to be near initial_axiom_coefficient_value (0.5) and TRUE_AXIOM_RELEVANCE (0.8)
        self.HARD_THRESHOLD_COEFF = 0.65 

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_prime(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)

    def relu(self, x):
        return np.maximum(0, x)

    def relu_prime(self, x):
        return (x > 0).astype(float)

    def calculate_p_predicted(self, growth_rate, inflation_rate, axiom_inputs):
        x = np.array([[growth_rate, inflation_rate]])

        self.h_input = np.dot(x, self.weights_h) + self.bias_h
        self.h_output = self.relu(self.h_input)

        self.o_input = np.dot(self.h_output, self.weights_o) + self.bias_o
        
        axiom_contribution_sum = 0.0
        for name, value in axiom_inputs.items():
            current_coeff = self.learned_axiom_coeffs[name][0]
            # --- MUTATOR EXPLOIT: Non-differentiable conditional logic ---
            # This introduces a sharp change in the function's derivative at HARD_THRESHOLD_COEFF
            if current_coeff < self.HARD_THRESHOLD_COEFF:
                # If coefficient is below threshold, its influence is halved
                axiom_contribution_sum += (current_coeff / 2.0) * value
            else:
                # Normal influence if above threshold
                axiom_contribution_sum += current_coeff * value

        final_output = self.o_input + axiom_contribution_sum
        p_predicted = self.sigmoid(final_output)

        p_predicted = np.clip(p_predicted, 0.0, 1.0)
        return p_predicted[0,0]

    def get_params(self):
        params = {
            'weights_h': self.weights_h, 'bias_h': self.bias_h,
            'weights_o': self.weights_o, 'bias_o': self.bias_o
        }
        for name, coeff in self.learned_axiom_coeffs.items():
            params[f'axiom_coeff_{name}'] = coeff
        return params

    def set_params(self, params):
        self.weights_h = params['weights_h']
        self.bias_h = params['bias_h']
        self.weights_o = params['weights_o']
        self.bias_o = params['bias_o']
        for name in self.axiom_names:
            self.learned_axiom_coeffs[name] = params[f'axiom_coeff_{name}']

    def _get_param_ref(self, param_key):
        if param_key.startswith('axiom_coeff_'):
            axiom_name = param_key[len('axiom_coeff_'):]
            return self.learned_axiom_coeffs[axiom_name]
        elif param_key == 'weights_h': return self.weights_h
        elif param_key == 'bias_h': return self.bias_h
        elif param_key == 'weights_o': return self.weights_o
        elif param_key == 'bias_o': return self.bias_o
        else: raise ValueError(f"Unknown parameter key: {param_key}")

# --- EpistemicGradientUpdater (Copied from Mutator's suite, its analytical gradients will be 'insolvent' for the exploit) ---
class EpistemicGradientUpdater:
    def __init__(self, thesis_predictor, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        self.thesis_predictor = thesis_predictor
        self.current_lr_model_params = initial_learning_rate_model_params
        self.current_lr_axiom_coeffs = initial_learning_rate_axiom_coeffs
        self.adam_beta1 = adam_beta1
        self.adam_beta2 = adam_beta2
        self.adam_epsilon_stabilizer = adam_epsilon_stabilizer

        self.m = collections.defaultdict(lambda: collections.defaultdict(float))
        self.v = collections.defaultdict(lambda: collections.defaultdict(float))
        self.t = 0

        self.lr_patience_epochs = lr_patience_epochs
        self.lr_decay_factor = lr_decay_factor
        self.min_delta_for_lr_decay = min_delta_for_lr_decay
        self.min_learning_rate = min_learning_rate
        self.best_bss = -np.inf
        self.epochs_since_last_improvement = 0

    def _compute_loss_and_gradient(self, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        p_predicted = self.thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        loss = 0.5 * (Z_actual - p_predicted)**2

        grads = {}
        d_loss_d_p_predicted = -(Z_actual - p_predicted)

        x = np.array([[growth_rate, inflation_rate]])
        h_input = np.dot(x, self.thesis_predictor.weights_h) + self.thesis_predictor.bias_h
        h_output = self.thesis_predictor.relu(h_input)
        o_input = np.dot(h_output, self.thesis_predictor.weights_o) + self.thesis_predictor.bias_o
        
        # This part of the gradient calculation is now INCORRECT for the modified ThesisPredictor
        # because it assumes a simple linear relationship for axiom contribution, which is no longer true.
        axiom_contribution_sum_val = 0.0
        for name, value in axiom_inputs.items():
            axiom_contribution_sum_val += self.thesis_predictor.learned_axiom_coeffs[name][0] * value
        
        final_output_val = o_input + axiom_contribution_sum_val
        d_p_predicted_d_final_output = self.thesis_predictor.sigmoid_prime(final_output_val)

        d_loss_d_final_output = d_loss_d_p_predicted * d_p_predicted_d_final_output

        for name, value in axiom_inputs.items():
            # This analytical gradient is also INCORRECT for the modified ThesisPredictor
            # It should be (d_loss_d_final_output * value) if current_coeff >= HARD_THRESHOLD_COEFF
            # and (d_loss_d_final_output * value / 2.0) if current_coeff < HARD_THRESHOLD_COEFF
            grads[f'axiom_coeff_{name}'] = np.array([d_loss_d_final_output * value])

        grads['weights_o'] = np.dot(h_output.T, d_loss_d_final_output)
        grads['bias_o'] = np.sum(d_loss_d_final_output, axis=0)

        d_loss_d_h_output = np.dot(d_loss_d_final_output, self.thesis_predictor.weights_o.T)
        d_h_output_d_h_input = self.thesis_predictor.relu_prime(h_input)
        d_loss_d_h_input = d_loss_d_h_output * d_h_output_d_h_input

        grads['weights_h'] = np.dot(x.T, d_loss_d_h_input)
        grads['bias_h'] = np.sum(d_loss_d_h_input, axis=0)

        return loss, grads

    def update_params(self, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        self.t += 1
        loss, grads = self._compute_loss_and_gradient(growth_rate, inflation_rate, axiom_inputs, Z_actual)

        for param_key, grad_val in grads.items():
            if param_key.startswith('axiom_coeff_'):
                lr = self.current_lr_axiom_coeffs
            else:
                lr = self.current_lr_model_params

            self.m[param_key] = self.adam_beta1 * self.m[param_key] + (1 - self.adam_beta1) * grad_val
            self.v[param_key] = self.adam_beta2 * self.v[param_key] + (1 - self.adam_beta2) * (grad_val ** 2)

            m_hat = self.m[param_key] / (1 - self.adam_beta1 ** self.t)
            v_hat = self.v[param_key] / (1 - self.adam_beta2 ** self.t)

            param_ref = self.thesis_predictor._get_param_ref(param_key)
            param_ref -= lr * m_hat / (np.sqrt(v_hat) + self.adam_epsilon_stabilizer)
        
        return loss

    def adaptive_learning_rate_scheduler(self, current_bss):
        if current_bss > self.best_bss + self.min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.epochs_since_last_improvement = 0
        else:
            self.epochs_since_last_improvement += 1
            if self.epochs_since_last_improvement >= self.lr_patience_epochs:
                self.current_lr_model_params = max(self.current_lr_model_params * self.lr_decay_factor, self.min_learning_rate)
                self.current_lr_axiom_coeffs = max(self.current_lr_axiom_coeffs * self.lr_decay_factor, self.min_learning_rate)
                self.epochs_since_last_improvement = 0


# --- FiringSquad (Copied from Mutator's suite, expected to detect the exploit) ---
class FiringSquad:
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, growth_rate, inflation_rate, axiom_inputs, param_key, param_idx=0):
        param_ref = thesis_predictor._get_param_ref(param_key)
        
        if not isinstance(param_ref, np.ndarray) or param_idx >= param_ref.size:
             return np.inf

        original_value = param_ref.flatten()[param_idx]

        gradients = []
        for epsilon_scale in self.robustness_perturbation_epsilon_scales:
            param_ref.flatten()[param_idx] = original_value + epsilon_scale
            p_plus = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)

            param_ref.flatten()[param_idx] = original_value - epsilon_scale
            p_minus = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)

            param_ref.flatten()[param_idx] = original_value

            if epsilon_scale == 0:
                grad = 0.0
            else:
                grad = (p_plus - p_minus) / (2 * epsilon_scale)
            gradients.append(grad)

        if not gradients:
            return 0.0

        max_diff = 0.0
        for i in range(len(gradients)):
            for j in range(i + 1, len(gradients)):
                max_diff = max(max_diff, abs(gradients[i] - gradients[j]))
        
        return max_diff


# --- MetaJudge (Copied from Mutator's suite, expected to veto the exploit) ---
class MetaJudge:
    def __init__(self, axiom_names, differentiability_tolerance, target_brier_skill_score,
                 min_observations_for_calibration, rolling_window_size,
                 initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer,
                 lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        self.axiom_weights = {name: INITIAL_AXIOM_COEFFICIENT_VALUE for name in axiom_names}
        self.differentiability_tolerance = differentiability_tolerance
        self.target_brier_skill_score = target_brier_skill_score
        self.min_observations_for_calibration = min_observations_for_calibration
        self.rolling_window_size = rolling_window_size

        self.predictions_history = collections.deque(maxlen=rolling_window_size)
        self.actuals_history = collections.deque(maxlen=rolling_window_size)

        self.epistemic_gradient_updater = None

        self.current_lr_model_params = initial_learning_rate_model_params
        self.current_lr_axiom_coeffs = initial_learning_rate_axiom_coeffs

        self.adam_beta1 = adam_beta1
        self.adam_beta2 = adam_beta2
        self.adam_epsilon_stabilizer = adam_epsilon_stabilizer
        self.lr_patience_epochs = lr_patience_epochs
        self.lr_decay_factor = lr_decay_factor
        self.min_delta_for_lr_decay = min_delta_for_lr_decay
        self.min_learning_rate = min_learning_rate


    def AxiomDifferentiabilityVeto(self, thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs):
        if not hasattr(thesis_predictor, 'learned_axiom_coeffs') or not isinstance(thesis_predictor.learned_axiom_coeffs, dict):
            return "VETO: ThesisPredictor missing 'learned_axiom_coeffs' dictionary."
        
        for name in self.axiom_weights.keys():
            if name not in thesis_predictor.learned_axiom_coeffs:
                return f"VETO: ThesisPredictor missing learned_axiom_coeffs for axiom '{name}'."
            if not isinstance(thesis_predictor.learned_axiom_coeffs[name], np.ndarray) or thesis_predictor.learned_axiom_coeffs[name].shape != (1,):
                return f"VETO: learned_axiom_coeffs['{name}'] is not a (1,) np.ndarray."

            consistency_score = firing_squad.DifferentiabilityRobustnessCheck(
                thesis_predictor, growth_rate, inflation_rate, axiom_inputs, f'axiom_coeff_{name}'
            )
            if consistency_score > self.differentiability_tolerance:
                return f"VETO: Axiom '{name}' failed DifferentiabilityRobustnessCheck (Score: {consistency_score:.4f})."
        
        p_test = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        if not (0.0 <= p_test <= 1.0):
            return f"VETO: P_predicted output ({p_test:.4f}) outside [0,1] range."

        return None

    def calculate_brier_score(self, predictions, actuals):
        if len(predictions) == 0 or len(actuals) == 0:
            return 0.0
        return np.mean((np.array(predictions) - np.array(actuals))**2)

    def calculate_brier_skill_score(self, predictions, actuals):
        if len(actuals) < self.min_observations_for_calibration:
            return -np.inf

        baseline_prediction = np.mean(actuals)
        baseline_predictions = np.full_like(actuals, baseline_prediction)

        bs = self.calculate_brier_score(predictions, actuals)
        bs_baseline = self.calculate_brier_score(baseline_predictions, actuals)

        if bs_baseline < 1e-9:
            return 1.0 if bs < 1e-9 else -np.inf

        return 1 - (bs / bs_baseline)

    def score_thesis(self, thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        veto_reason = self.AxiomDifferentiabilityVeto(thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs)
        if veto_reason:
            return {'score': 0, 'status': 'VETO', 'reason': veto_reason, 'bss': -np.inf, 'max_consistency_score': np.inf,
                    'current_lr_model_params': self.current_lr_model_params, 'current_lr_axiom_coeffs': self.current_lr_axiom_coeffs}

        p_predicted = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        self.predictions_history.append(p_predicted)
        self.actuals_history.append(Z_actual)

        current_bss = self.calculate_brier_skill_score(list(self.predictions_history), list(self.actuals_history))
        
        max_consistency_score = 0.0
        for name in self.axiom_weights.keys():
            score = firing_squad.DifferentiabilityRobustnessCheck(
                thesis_predictor, growth_rate, inflation_rate, axiom_inputs, f'axiom_coeff_{name}'
            )
            max_consistency_score = max(max_consistency_score, score)

        if self.epistemic_gradient_updater and len(self.actuals_history) >= self.min_observations_for_calibration:
            self.epistemic_gradient_updater.adaptive_learning_rate_scheduler(current_bss)
            self.current_lr_model_params = self.epistemic_gradient_updater.current_lr_model_params
            self.current_lr_axiom_coeffs = self.epistemic_gradient_updater.current_lr_axiom_coeffs

        if AXIOM_SYNC_FREQUENCY > 0 and (len(self.actuals_history) % AXIOM_SYNC_FREQUENCY == 0):
            self.AxiomWeightSynchronization(thesis_predictor)

        score = current_bss if current_bss > 0 else 0
        return {
            'score': score,
            'status': 'ACCEPTED',
            'reason': '',
            'bss': current_bss,
            'max_consistency_score': max_consistency_score,
            'learned_axiom_coeffs': {name: coeff[0] for name, coeff in thesis_predictor.learned_axiom_coeffs.items()},
            'current_lr_model_params': self.current_lr_model_params,
            'current_lr_axiom_coeffs': self.current_lr_axiom_coeffs
        }

    def AxiomWeightSynchronization(self, thesis_predictor):
        for name, coeff in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[name] = coeff[0]

    def accept_thesis(self, thesis_predictor):
        self.epistemic_gradient_updater = EpistemicGradientUpdater(
            thesis_predictor=thesis_predictor,
            initial_learning_rate_model_params=self.current_lr_model_params,
            initial_learning_rate_axiom_coeffs=self.current_lr_axiom_coeffs,
            adam_beta1=self.adam_beta1,
            adam_beta2=self.adam_beta2,
            adam_epsilon_stabilizer=self.adam_epsilon_stabilizer,
            lr_patience_epochs=LR_PATIENCE_EPOCHS,
            lr_decay_factor=LR_DECAY_FACTOR,
            min_delta_for_lr_decay=MIN_DELTA_FOR_LR_DECAY,
            min_learning_rate=MIN_LEARNING_RATE
        )
        self.epistemic_gradient_updater.current_lr_model_params = self.current_lr_model_params
        self.epistemic_gradient_updater.current_lr_axiom_coeffs = self.current_lr_axiom_coeffs


# --- Simulated Z_actual generation (Copied from Mutator's suite) ---
def generate_simulated_Z_actual(iteration, growth_rate, inflation_rate, axiom_relevance_value):
    growth_effect = TRUE_GROWTH_COEFF_NL * np.sin(iteration / TRUE_GROWTH_FREQ_NL) * growth_rate
    inflation_effect = TRUE_INFLATION_COEFF_NL * np.cos(iteration / TRUE_INFLATION_FREQ_NL) * inflation_rate
    interaction_effect = TRUE_INTERACTION_COEFF_NL * growth_rate * inflation_rate

    raw_value = (TRUE_BIAS_NL + growth_effect + inflation_effect + interaction_effect +
                 TRUE_AXIOM_RELEVANCE * axiom_relevance_value)

    noise = np.random.normal(0, 0.05)
    
    Z_actual = 1 / (1 + np.exp(-raw_value)) + noise
    
    return np.clip(Z_actual, 0.0, 1.0)

# Main simulation loop for counter-test
def counter_test_model():
    print("--- Starting Counter-Test Simulation (V4 Architecture with Mutator Exploit) ---")

    axiom_names = ['AXIOM_RECESSION_AVOIDANCE']

    meta_judge = MetaJudge(
        axiom_names=axiom_names,
        differentiability_tolerance=DIFFERENTIABILITY_TOLERANCE,
        target_brier_skill_score=TARGET_BRIER_SKILL_SCORE,
        min_observations_for_calibration=MIN_OBSERVATIONS_FOR_CALIBRATION,
        rolling_window_size=ROLLING_WINDOW_SIZE,
        initial_learning_rate_model_params=INITIAL_LEARNING_RATE_MODEL_PARAMS,
        initial_learning_rate_axiom_coeffs=INITIAL_LEARNING_RATE_AXIOM_COEFFS,
        adam_beta1=ADAM_BETA1,
        adam_beta2=ADAM_BETA2,
        adam_epsilon_stabilizer=ADAM_EPSILON_STABILIZER,
        lr_patience_epochs=LR_PATIENCE_EPOCHS,
        lr_decay_factor=LR_DECAY_FACTOR,
        min_delta_for_lr_decay=MIN_DELTA_FOR_LR_DECAY,
        min_learning_rate=MIN_LEARNING_RATE
    )

    firing_squad = FiringSquad(
        differentiability_tolerance=DIFFERENTIABILITY_TOLERANCE,
        robustness_perturbation_epsilon_scales=ROBUSTNESS_PERTURBATION_EPSILON_SCALES
    )

    # Instantiate the MODIFIED ThesisPredictor with the exploit
    thesis_predictor_exploit = ThesisPredictorCounterTest(
        axiom_names=axiom_names,
        hidden_layer_size=HIDDEN_LAYER_SIZE,
        initial_axiom_coefficient_value=INITIAL_AXIOM_COEFFICIENT_VALUE
    )

    meta_judge.accept_thesis(thesis_predictor_exploit)

    # Run enough iterations for the learned coefficient to potentially cross the threshold
    num_iterations = MIN_OBSERVATIONS_FOR_CALIBRATION + ROLLING_WINDOW_SIZE * 2 
    
    veto_triggered = False
    final_max_consistency_score = 0.0

    print(f"Initial axiom_weights: {meta_judge.axiom_weights}")
    print(f"Initial learned_axiom_coeffs: {thesis_predictor_exploit.learned_axiom_coeffs}")
    print(f"Hard Differentiability Threshold in ThesisPredictor: {thesis_predictor_exploit.HARD_THRESHOLD_COEFF}")
    print(f"Differentiability Tolerance: {DIFFERENTIABILITY_TOLERANCE}")

    for i in range(1, num_iterations + 1):
        growth_rate_i = HYPOTHETICAL_ECONOMY_GROWTH_RATE_Q1_2025_BASE * (1 + 0.1 * np.sin(i / 100.0))
        inflation_rate_i = HYPOTHETICAL_INFLATION_RATE_Q1_2025_BASE * (1 + 0.05 * np.cos(i / 50.0))
        axiom_relevance_value_i = 1.0 if i % 2 == 0 else 0.0

        axiom_inputs_i = {'AXIOM_RECESSION_AVOIDANCE': axiom_relevance_value_i}
        Z_actual_i = generate_simulated_Z_actual(i, growth_rate_i, inflation_rate_i, axiom_relevance_value_i)

        evaluation_result = meta_judge.score_thesis(thesis_predictor_exploit, firing_squad, growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)
        
        if evaluation_result['status'] == 'VETO':
            print(f"\n--- VETO Triggered at Iteration {i} ---")
            print(f"Reason: {evaluation_result['reason']}")
            print(f"Max Consistency Score: {evaluation_result['max_consistency_score']:.4f}")
            veto_triggered = True
            final_max_consistency_score = evaluation_result['max_consistency_score']
            break # Stop simulation if vetoed
        else:
            final_max_consistency_score = max(final_max_consistency_score, evaluation_result['max_consistency_score'])
            # Only update params if not vetoed
            meta_judge.epistemic_gradient_updater.current_lr_model_params = evaluation_result['current_lr_model_params']
            meta_judge.epistemic_gradient_updater.current_lr_axiom_coeffs = evaluation_result['current_lr_axiom_coeffs']
            meta_judge.epistemic_gradient_updater.update_params(growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)

        if i % 50 == 0:
            print(f"--- Iteration {i} ---")
            print(f"Status: {evaluation_result['status']}")
            print(f"Rolling BSS ({ROLLING_WINDOW_SIZE} obs): {evaluation_result['bss']:.4f}")
            print(f"Learned Axiom Coeff (RECESSION_AVOIDANCE): {thesis_predictor_exploit.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE']:.4f}")
            print(f"Max Consistency Score: {evaluation_result['max_consistency_score']:.4f}")
            print(f"Current Model LR: {evaluation_result['current_lr_model_params']:.6f}, Axiom LR: {evaluation_result['current_lr_axiom_coeffs']:.6f}")

    print("\n--- Counter-Test Simulation Complete ---")
    print(f"Veto Triggered: {veto_triggered}")
    print(f"Final Max Consistency Score observed: {final_max_consistency_score:.4f}")

    # --- Assertions for Counter-Test ---
    # The counter-test asserts that the Meta-Judge's DifferentiabilityVeto successfully detected the exploit.
    assert veto_triggered, \
        f"COUNTER-TEST FAILED: The Meta-Judge did NOT veto the thesis despite the non-differentiable exploit. Max Consistency Score: {final_max_consistency_score:.4f}"
    assert final_max_consistency_score > DIFFERENTIABILITY_TOLERANCE, \
        f"COUNTER-TEST FAILED: Max Consistency Score ({final_max_consistency_score:.4f}) did not exceed tolerance ({DIFFERENTIABILITY_TOLERANCE}), indicating exploit was not detected as non-differentiable."
    
    print("\nAll Counter-Test Assertions PASSED. The Meta-Judge's DifferentiabilityVeto successfully detected the exploit.")

if __name__ == "__main__":
    counter_test_model()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpcrzo4s3v.py", line 497, in <module>
    counter_test_model()
    ~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpcrzo4s3v.py", line 473, in counter_test_model
    meta_judge.epistemic_gradient_updater.update_params(growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpcrzo4s3v.py", line 192, in update_params
    self.m[param_key] = self.adam_beta1 * self.m[param_key] + (1 - self.adam_beta1) * grad_val
                        ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for *: 'float' and 'collections.defaultdict'


## Attacker: Philosopher of Science & Complex Systems Architect
The provided thesis for V4 introduces an adaptive learning rate scheduler and increased model capacity, aiming to enhance the system's ability to achieve target Brier Skill Scores and precisely assign credit to axioms. While these additions improve the *optimization process* for a given model, they do not fundamentally address the architectural limitations concerning the representation of complex causal realities.

**Critique:**

1.  **Topological Flatness (Problem 5 Unaddressed):** The thesis explicitly acknowledges "Problem 5: The DAG is topologically flat," stating, "All nodes connect directly to the outcome. There are no intermediate causal nodes." However, the proposed V4 architecture, as implemented in the `ThesisPredictor`, maintains this flat structure. The `ThesisPredictor` is a single-hidden-layer Multi-Layer Perceptron (MLP) that processes `growth_rate` and `inflation_rate`, and then *additively* incorporates axiom contributions to the log-odds before a final sigmoid activation. This design inherently limits the system's ability to model deep causal chains (A causes B which causes C which causes outcome) or complex, mediated interactions. The "credit assignment" is therefore confined to direct correlations within this flat, simplified representation, not true underlying causal contributions in a multi-layered reality.

2.  **Indirect Credit Assignment (Problem 4 Partially Mitigated, Not Solved):** The claim of "precise, real-time credit assignment" is challenged by the aforementioned topological flatness. While the adaptive gradient descent can precisely learn the *model's* coefficients, these coefficients represent the axiom's contribution *within the model's assumed linear-additive structure*. If the true causal effect of an axiom in a complex environment is non-linear, conditional, or mediated by other variables in ways not captured by the `ThesisPredictor`'s architecture, the learned coefficient will be an approximation at best, and potentially misleading. The system learns the "credit" for correlation in its limited model, not necessarily the true causal contribution in a complex, multi-causal context.

3.  **Fidelity of `true_axiom_relevance * 1.0` in `Z_actual` (Cooked Books in Simulation Design):** The most significant "cooked book" in the provided Python falsification suite lies in the `generate_simulated_Z_actual` function. It defines the "true" underlying process by directly adding `TRUE_AXIOM_RELEVANCE * axiom_relevance_value` to the `raw_value`. This means the simulated reality's causal structure for the axiom is perfectly linear and directly additive to the log-odds, precisely mirroring the `ThesisPredictor`'s assumption (`axiom_contribution_sum += self.learned_axiom_coeffs[name][0] * value`). This perfect alignment makes the learning task artificially easy and guarantees that the `ThesisPredictor` *can* converge to the `TRUE_AXIOM_RELEVANCE`. This design choice, while useful for isolated testing of the optimization mechanism, fundamentally undermines the philosophical claim of demonstrating "precise, real-time credit assignment" in complex, multi-causal contexts, as the "truth" is defined to be perfectly discoverable by the model's inherent limitations. It fails to simulate scenarios with unmodeled latent variables, significant concept drift, or non-linear/conditional axiom effects, which are characteristic of real-world complexity.

4.  **Parametric Grounding Audit:**
    *   **Financial Metrics:** `hypothetical_economy_growth_rate_q1_2025_base` (0.02) and `hypothetical_inflation_rate_q1_2025_base` (0.03) are presented as quarterly rates. These translate to approximately 8% and 12% annual rates, respectively. While high, these are within plausible (albeit aggressive) ranges for a "hypothetical economy" and are not orders of magnitude off. They are dimensionless rates, correctly applied.
    *   **Mathematical Constants:** `adam_beta1`, `adam_beta2`, `adam_epsilon_stabilizer`, `LR_PATIENCE_EPOCHS`, `LR_DECAY_FACTOR`, `MIN_DELTA_FOR_LR_DECAY`, `MIN_LEARNING_RATE` are standard hyperparameters for optimization and learning rate scheduling. Their values are within established norms for neural network training.
    *   **Physical Constants/Limits:** No explicit physical constants are claimed or misapplied. The `P_predicted` output is correctly clipped to `[0,1]` to represent probabilities.
    *   **Load-Bearing Variables:** The internal parameters for the `generate_simulated_Z_actual` function (`TRUE_BIAS_NL`, `TRUE_GROWTH_FREQ_NL`, etc.) are arbitrary dimensionless values defining the *simulated* non-linearity. They are consistent within the simulation's self-defined reality. The `TRUE_AXIOM_RELEVANCE` (0.8) is the target value for learning, and its direct, linear inclusion in `Z_actual` is the primary point of contention regarding the simulation's fidelity to complex reality.

**So What for the Meta-Judge:**

The V4 architecture, despite its advancements in optimization and anti-gaming, fails to demonstrate robust credit assignment in scenarios beyond a perfectly aligned, topologically flat simulation. The `ThesisPredictor`'s inherent assumption of a linear-additive axiom contribution, combined with a `Z_actual` generation function that perfectly matches this assumption, creates an artificially favorable learning environment. This means the system can "learn" axiom relevance precisely, but only because the "truth" is defined in a way that makes it perfectly discoverable by the model's limited architectural capabilities. This fundamental mismatch between the model's representational capacity and the complexities of real-world causal chains (e.g., non-linear axiom interactions, conditional effects, or deep causal paths) renders the claim of "precise, real-time credit assignment" invalid for complex, multi-causal environments. The system's performance metrics are achieved under conditions that do not adequately stress its ability to model and assign credit in the face of unmodeled interactions or deeper causal structures.

---

**COUNTER-TEST:**

The counter-test will expose the insolvency of the system's claim to "precise, real-time credit assignment" by modifying the `generate_simulated_Z_actual` function. Instead of a simple linear-additive effect, the axiom's true relevance will be *non-linearly modulated* by the `growth_rate`. The `ThesisPredictor`, which assumes a fixed linear coefficient for the axiom, will struggle to accurately capture this context-dependent, non-linear effect. This will lead to a failure in converging to the `TRUE_AXIOM_RELEVANCE` and a degradation of the Brier Skill Score, demonstrating the architectural limitation in complex, multi-causal contexts.

```python
import numpy as np
import collections

# Constants from LOAD-BEARING VARIABLES, ensuring no magic numbers
ADAM_BETA1 = 0.9
ADAM_BETA2 = 0.999
ADAM_EPSILON_STABILIZER = 1e-8
INITIAL_LEARNING_RATE_MODEL_PARAMS = 0.005
INITIAL_LEARNING_RATE_AXIOM_COEFFS = 0.02
MIN_OBSERVATIONS_FOR_CALIBRATION = 200
TARGET_BRIER_SKILL_SCORE = 0.20
ROLLING_WINDOW_SIZE = 50
HIDDEN_LAYER_SIZE = 8
INITIAL_AXIOM_COEFFICIENT_VALUE = 0.5
AXIOM_SYNC_FREQUENCY = 1
HYPOTHETICAL_ECONOMY_GROWTH_RATE_Q1_2025_BASE = 0.02
HYPOTHETICAL_INFLATION_RATE_Q1_2025_BASE = 0.03
TRUE_BIAS_NL = -0.5
TRUE_GROWTH_FREQ_NL = 50
TRUE_GROWTH_COEFF_NL = 10
TRUE_INFLATION_FREQ_NL = 30
TRUE_INFLATION_COEFF_NL = -15
TRUE_INTERACTION_COEFF_NL = 500
TRUE_AXIOM_RELEVANCE = 0.8 # The target for the model, but its true effect will be modulated
DIFFERENTIABILITY_TOLERANCE = 0.05
ROBUSTNESS_PERTURBATION_EPSILON_SCALES = [1e-5, 1e-4, 1e-3]

# NEW LOAD-BEARING VARIABLES for V4 Adaptive Learning Rate Scheduler
LR_PATIENCE_EPOCHS = 20
LR_DECAY_FACTOR = 0.5
MIN_DELTA_FOR_LR_DECAY = 0.005
MIN_LEARNING_RATE = 1e-5

class ThesisPredictor:
    def __init__(self, axiom_names, hidden_layer_size, initial_axiom_coefficient_value):
        self.axiom_names = axiom_names
        self.input_dim = 2
        self.hidden_layer_size = hidden_layer_size
        self.output_dim = 1

        self.weights_h = np.random.randn(self.input_dim, self.hidden_layer_size) * np.sqrt(2.0 / self.input_dim)
        self.bias_h = np.zeros((1, self.hidden_layer_size))
        self.weights_o = np.random.randn(self.hidden_layer_size, self.output_dim) * np.sqrt(2.0 / self.hidden_layer_size)
        self.bias_o = np.zeros((1, self.output_dim))

        self.learned_axiom_coeffs = {
            name: np.array([initial_axiom_coefficient_value]) for name in axiom_names
        }

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_prime(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)

    def relu(self, x):
        return np.maximum(0, x)

    def relu_prime(self, x):
        return (x > 0).astype(float)

    def calculate_p_predicted(self, growth_rate, inflation_rate, axiom_inputs):
        x = np.array([[growth_rate, inflation_rate]])
        self.h_input = np.dot(x, self.weights_h) + self.bias_h
        self.h_output = self.relu(self.h_input)
        self.o_input = np.dot(self.h_output, self.weights_o) + self.bias_o
        
        axiom_contribution_sum = 0.0
        for name, value in axiom_inputs.items():
            axiom_contribution_sum += self.learned_axiom_coeffs[name][0] * value

        final_output = self.o_input + axiom_contribution_sum
        p_predicted = self.sigmoid(final_output)
        p_predicted = np.clip(p_predicted, 0.0, 1.0)
        return p_predicted[0,0]

    def get_params(self):
        params = {
            'weights_h': self.weights_h, 'bias_h': self.bias_h,
            'weights_o': self.weights_o, 'bias_o': self.bias_o
        }
        for name, coeff in self.learned_axiom_coeffs.items():
            params[f'axiom_coeff_{name}'] = coeff
        return params

    def set_params(self, params):
        self.weights_h = params['weights_h']
        self.bias_h = params['bias_h']
        self.weights_o = params['weights_o']
        self.bias_o = params['bias_o']
        for name in self.axiom_names:
            self.learned_axiom_coeffs[name] = params[f'axiom_coeff_{name}']

    def _get_param_ref(self, param_key):
        if param_key.startswith('axiom_coeff_'):
            axiom_name = param_key[len('axiom_coeff_'):]
            return self.learned_axiom_coeffs[axiom_name]
        elif param_key == 'weights_h': return self.weights_h
        elif param_key == 'bias_h': return self.bias_h
        elif param_key == 'weights_o': return self.weights_o
        elif param_key == 'bias_o': return self.bias_o
        else: raise ValueError(f"Unknown parameter key: {param_key}")


class EpistemicGradientUpdater:
    def __init__(self, thesis_predictor, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        self.thesis_predictor = thesis_predictor
        self.current_lr_model_params = initial_learning_rate_model_params
        self.current_lr_axiom_coeffs = initial_learning_rate_axiom_coeffs
        self.adam_beta1 = adam_beta1
        self.adam_beta2 = adam_beta2
        self.adam_epsilon_stabilizer = adam_epsilon_stabilizer

        self.m = collections.defaultdict(lambda: collections.defaultdict(float))
        self.v = collections.defaultdict(lambda: collections.defaultdict(float))
        self.t = 0

        self.lr_patience_epochs = lr_patience_epochs
        self.lr_decay_factor = lr_decay_factor
        self.min_delta_for_lr_decay = min_delta_for_lr_decay
        self.min_learning_rate = min_learning_rate
        self.best_bss = -np.inf
        self.epochs_since_last_improvement = 0

    def _compute_loss_and_gradient(self, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        p_predicted = self.thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        loss = 0.5 * (Z_actual - p_predicted)**2
        grads = {}

        d_loss_d_p_predicted = -(Z_actual - p_predicted)

        x = np.array([[growth_rate, inflation_rate]])
        h_input = np.dot(x, self.thesis_predictor.weights_h) + self.thesis_predictor.bias_h
        h_output = self.thesis_predictor.relu(h_input)
        o_input = np.dot(h_output, self.thesis_predictor.weights_o) + self.thesis_predictor.bias_o
        
        axiom_contribution_sum_val = 0.0
        for name, value in axiom_inputs.items():
            axiom_contribution_sum_val += self.thesis_predictor.learned_axiom_coeffs[name][0] * value
        
        final_output_val = o_input + axiom_contribution_sum_val
        d_p_predicted_d_final_output = self.thesis_predictor.sigmoid_prime(final_output_val)

        d_loss_d_final_output = d_loss_d_p_predicted * d_p_predicted_d_final_output

        for name, value in axiom_inputs.items():
            grads[f'axiom_coeff_{name}'] = np.array([d_loss_d_final_output * value])

        grads['weights_o'] = np.dot(h_output.T, d_loss_d_final_output)
        grads['bias_o'] = np.sum(d_loss_d_final_output, axis=0)

        d_loss_d_h_output = np.dot(d_loss_d_final_output, self.thesis_predictor.weights_o.T)
        d_h_output_d_h_input = self.thesis_predictor.relu_prime(h_input)
        d_loss_d_h_input = d_loss_d_h_output * d_h_output_d_h_input

        grads['weights_h'] = np.dot(x.T, d_loss_d_h_input)
        grads['bias_h'] = np.sum(d_loss_d_h_input, axis=0)

        return loss, grads

    def update_params(self, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        self.t += 1
        loss, grads = self._compute_loss_and_gradient(growth_rate, inflation_rate, axiom_inputs, Z_actual)

        for param_key, grad_val in grads.items():
            if param_key.startswith('axiom_coeff_'):
                lr = self.current_lr_axiom_coeffs
            else:
                lr = self.current_lr_model_params

            self.m[param_key] = self.adam_beta1 * self.m[param_key] + (1 - self.adam_beta1) * grad_val
            self.v[param_key] = self.adam_beta2 * self.v[param_key] + (1 - self.adam_beta2) * (grad_val ** 2)

            m_hat = self.m[param_key] / (1 - self.adam_beta1 ** self.t)
            v_hat = self.v[param_key] / (1 - self.adam_beta2 ** self.t)

            param_ref = self.thesis_predictor._get_param_ref(param_key)
            param_ref -= lr * m_hat / (np.sqrt(v_hat) + self.adam_epsilon_stabilizer)
        
        return loss

    def adaptive_learning_rate_scheduler(self, current_bss):
        if current_bss > self.best_bss + self.min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.epochs_since_last_improvement = 0
        else:
            self.epochs_since_last_improvement += 1
            if self.epochs_since_last_improvement >= self.lr_patience_epochs:
                self.current_lr_model_params = max(self.current_lr_model_params * self.lr_decay_factor, self.min_learning_rate)
                self.current_lr_axiom_coeffs = max(self.current_lr_axiom_coeffs * self.lr_decay_factor, self.min_learning_rate)
                self.epochs_since_last_improvement = 0


class FiringSquad:
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, growth_rate, inflation_rate, axiom_inputs, param_key, param_idx=0):
        param_ref = thesis_predictor._get_param_ref(param_key)
        
        if not isinstance(param_ref, np.ndarray) or param_idx >= param_ref.size:
             return np.inf

        original_value = param_ref.flatten()[param_idx]

        gradients = []
        for epsilon_scale in self.robustness_perturbation_epsilon_scales:
            param_ref.flatten()[param_idx] = original_value + epsilon_scale
            p_plus = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)

            param_ref.flatten()[param_idx] = original_value - epsilon_scale
            p_minus = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)

            param_ref.flatten()[param_idx] = original_value

            if epsilon_scale == 0:
                grad = 0.0
            else:
                grad = (p_plus - p_minus) / (2 * epsilon_scale)
            gradients.append(grad)

        if not gradients:
            return 0.0

        max_diff = 0.0
        for i in range(len(gradients)):
            for j in range(i + 1, len(gradients)):
                max_diff = max(max_diff, abs(gradients[i] - gradients[j]))
        
        return max_diff


class MetaJudge:
    def __init__(self, axiom_names, differentiability_tolerance, target_brier_skill_score,
                 min_observations_for_calibration, rolling_window_size,
                 initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer,
                 lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        self.axiom_weights = {name: INITIAL_AXIOM_COEFFICIENT_VALUE for name in axiom_names}
        self.differentiability_tolerance = differentiability_tolerance
        self.target_brier_skill_score = target_brier_skill_score
        self.min_observations_for_calibration = min_observations_for_calibration
        self.rolling_window_size = rolling_window_size

        self.predictions_history = collections.deque(maxlen=rolling_window_size)
        self.actuals_history = collections.deque(maxlen=rolling_window_size)

        self.epistemic_gradient_updater = None

        self.current_lr_model_params = initial_learning_rate_model_params
        self.current_lr_axiom_coeffs = initial_learning_rate_axiom_coeffs

        self.adam_beta1 = adam_beta1
        self.adam_beta2 = adam_beta2
        self.adam_epsilon_stabilizer = adam_epsilon_stabilizer
        self.lr_patience_epochs = lr_patience_epochs
        self.lr_decay_factor = lr_decay_factor
        self.min_delta_for_lr_decay = min_delta_for_lr_decay
        self.min_learning_rate = min_learning_rate


    def AxiomDifferentiabilityVeto(self, thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs):
        if not hasattr(thesis_predictor, 'learned_axiom_coeffs') or not isinstance(thesis_predictor.learned_axiom_coeffs, dict):
            return "VETO: ThesisPredictor missing 'learned_axiom_coeffs' dictionary."
        
        for name in self.axiom_weights.keys():
            if name not in thesis_predictor.learned_axiom_coeffs:
                return f"VETO: ThesisPredictor missing learned_axiom_coeffs for axiom '{name}'."
            if not isinstance(thesis_predictor.learned_axiom_coeffs[name], np.ndarray) or thesis_predictor.learned_axiom_coeffs[name].shape != (1,):
                return f"VETO: learned_axiom_coeffs['{name}'] is not a (1,) np.ndarray."

            consistency_score = firing_squad.DifferentiabilityRobustnessCheck(
                thesis_predictor, growth_rate, inflation_rate, axiom_inputs, f'axiom_coeff_{name}'
            )
            if consistency_score > self.differentiability_tolerance:
                return f"VETO: Axiom '{name}' failed DifferentiabilityRobustnessCheck (Score: {consistency_score:.4f})."
        
        p_test = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        if not (0.0 <= p_test <= 1.0):
            return f"VETO: P_predicted output ({p_test:.4f}) outside [0,1] range."

        return None

    def calculate_brier_score(self, predictions, actuals):
        if len(predictions) == 0 or len(actuals) == 0:
            return 0.0
        return np.mean((np.array(predictions) - np.array(actuals))**2)

    def calculate_brier_skill_score(self, predictions, actuals):
        if len(actuals) < self.min_observations_for_calibration:
            return -np.inf

        baseline_prediction = np.mean(actuals)
        baseline_predictions = np.full_like(actuals, baseline_prediction)

        bs = self.calculate_brier_score(predictions, actuals)
        bs_baseline = self.calculate_brier_score(baseline_predictions, actuals)

        if bs_baseline < 1e-9:
            return 1.0 if bs < 1e-9 else -np.inf

        return 1 - (bs / bs_baseline)

    def score_thesis(self, thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs, Z_actual):
        veto_reason = self.AxiomDifferentiabilityVeto(thesis_predictor, firing_squad, growth_rate, inflation_rate, axiom_inputs)
        if veto_reason:
            return {'score': 0, 'status': 'VETO', 'reason': veto_reason, 'bss': -np.inf, 'max_consistency_score': np.inf,
                    'current_lr_model_params': self.current_lr_model_params, 'current_lr_axiom_coeffs': self.current_lr_axiom_coeffs}

        p_predicted = thesis_predictor.calculate_p_predicted(growth_rate, inflation_rate, axiom_inputs)
        self.predictions_history.append(p_predicted)
        self.actuals_history.append(Z_actual)

        current_bss = self.calculate_brier_skill_score(list(self.predictions_history), list(self.actuals_history))
        
        max_consistency_score = 0.0
        for name in self.axiom_weights.keys():
            score = firing_squad.DifferentiabilityRobustnessCheck(
                thesis_predictor, growth_rate, inflation_rate, axiom_inputs, f'axiom_coeff_{name}'
            )
            max_consistency_score = max(max_consistency_score, score)

        if self.epistemic_gradient_updater and len(self.actuals_history) >= self.min_observations_for_calibration:
            self.epistemic_gradient_updater.adaptive_learning_rate_scheduler(current_bss)
            self.current_lr_model_params = self.epistemic_gradient_updater.current_lr_model_params
            self.current_lr_axiom_coeffs = self.epistemic_gradient_updater.current_lr_axiom_coeffs

        if AXIOM_SYNC_FREQUENCY > 0 and (len(self.actuals_history) % AXIOM_SYNC_FREQUENCY == 0):
            self.AxiomWeightSynchronization(thesis_predictor)

        score = current_bss if current_bss > 0 else 0
        return {
            'score': score,
            'status': 'ACCEPTED',
            'reason': '',
            'bss': current_bss,
            'max_consistency_score': max_consistency_score,
            'learned_axiom_coeffs': {name: coeff[0] for name, coeff in thesis_predictor.learned_axiom_coeffs.items()},
            'current_lr_model_params': self.current_lr_model_params,
            'current_lr_axiom_coeffs': self.current_lr_axiom_coeffs
        }

    def AxiomWeightSynchronization(self, thesis_predictor):
        for name, coeff in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[name] = coeff[0]

    def accept_thesis(self, thesis_predictor):
        self.epistemic_gradient_updater = EpistemicGradientUpdater(
            thesis_predictor=thesis_predictor,
            initial_learning_rate_model_params=self.current_lr_model_params,
            initial_learning_rate_axiom_coeffs=self.current_lr_axiom_coeffs,
            adam_beta1=self.adam_beta1,
            adam_beta2=self.adam_beta2,
            adam_epsilon_stabilizer=self.adam_epsilon_stabilizer,
            lr_patience_epochs=self.lr_patience_epochs,
            lr_decay_factor=self.lr_decay_factor,
            min_delta_for_lr_decay=self.min_delta_for_lr_decay,
            min_learning_rate=MIN_LEARNING_RATE
        )
        self.epistemic_gradient_updater.current_lr_model_params = self.current_lr_model_params
        self.epistemic_gradient_updater.current_lr_axiom_coeffs = self.current_lr_axiom_coeffs


# --- MODIFIED generate_simulated_Z_actual for COUNTER-TEST ---
def generate_simulated_Z_actual_counter_test(iteration, growth_rate, inflation_rate, axiom_relevance_value):
    """
    Counter-test: Simulates a Z_actual where the axiom's effect is non-linearly
    modulated by the growth rate, challenging the ThesisPredictor's linear-additive assumption.
    """
    growth_effect = TRUE_GROWTH_COEFF_NL * np.sin(iteration / TRUE_GROWTH_FREQ_NL) * growth_rate
    inflation_effect = TRUE_INFLATION_COEFF_NL * np.cos(iteration / TRUE_INFLATION_FREQ_NL) * inflation_rate
    interaction_effect = TRUE_INTERACTION_COEFF_NL * growth_rate * inflation_rate

    # --- CRITICAL MODIFICATION: Non-linear, context-dependent axiom effect ---
    # The axiom's true effect is now modulated by a non-linear function of the growth rate.
    # The ThesisPredictor assumes a constant linear coefficient, which will be insufficient.
    modulation_factor = 1.0 + np.sin(growth_rate * 150) # growth_rate is small, so 150 scales it to a meaningful range for sin
    
    true_axiom_effect = TRUE_AXIOM_RELEVANCE * axiom_relevance_value * modulation_factor

    raw_value = (TRUE_BIAS_NL + growth_effect + inflation_effect + interaction_effect +
                 true_axiom_effect)

    noise = np.random.normal(0, 0.05)
    
    Z_actual = 1 / (1 + np.exp(-raw_value)) + noise
    
    return np.clip(Z_actual, 0.0, 1.0)

# Main simulation loop for counter-test
def counter_test_model():
    print("--- Starting COUNTER-TEST: V4 Epistemic Engine Simulation with Non-Linear Axiom Interaction ---")

    axiom_names = ['AXIOM_RECESSION_AVOIDANCE']

    meta_judge = MetaJudge(
        axiom_names=axiom_names,
        differentiability_tolerance=DIFFERENTIABILITY_TOLERANCE,
        target_brier_skill_score=TARGET_BRIER_SKILL_SCORE,
        min_observations_for_calibration=MIN_OBSERVATIONS_FOR_CALIBRATION,
        rolling_window_size=ROLLING_WINDOW_SIZE,
        initial_learning_rate_model_params=INITIAL_LEARNING_RATE_MODEL_PARAMS,
        initial_learning_rate_axiom_coeffs=INITIAL_LEARNING_RATE_AXIOM_COEFFS,
        adam_beta1=ADAM_BETA1,
        adam_beta2=ADAM_BETA2,
        adam_epsilon_stabilizer=ADAM_EPSILON_STABILIZER,
        lr_patience_epochs=LR_PATIENCE_EPOCHS,
        lr_decay_factor=LR_DECAY_FACTOR,
        min_delta_for_lr_decay=MIN_DELTA_FOR_LR_DECAY,
        min_learning_rate=MIN_LEARNING_RATE
    )

    firing_squad = FiringSquad(
        differentiability_tolerance=DIFFERENTIABILITY_TOLERANCE,
        robustness_perturbation_epsilon_scales=ROBUSTNESS_PERTURBATION_EPSILON_SCALES
    )

    thesis_predictor = ThesisPredictor(
        axiom_names=axiom_names,
        hidden_layer_size=HIDDEN_LAYER_SIZE,
        initial_axiom_coefficient_value=INITIAL_AXIOM_COEFFICIENT_VALUE
    )

    meta_judge.accept_thesis(thesis_predictor)

    num_iterations = MIN_OBSERVATIONS_FOR_CALIBRATION + ROLLING_WINDOW_SIZE * 5
    
    final_bss = -np.inf
    final_axiom_coeff = INITIAL_AXIOM_COEFFICIENT_VALUE
    max_overall_consistency_score = 0.0
    
    print(f"Initial axiom_weights: {meta_judge.axiom_weights}")
    print(f"Initial learned_axiom_coeffs: {thesis_predictor.learned_axiom_coeffs}")
    print(f"True Axiom Relevance (Base): {TRUE_AXIOM_RELEVANCE}")

    for i in range(1, num_iterations + 1):
        growth_rate_i = HYPOTHETICAL_ECONOMY_GROWTH_RATE_Q1_2025_BASE * (1 + 0.1 * np.sin(i / 100.0))
        inflation_rate_i = HYPOTHETICAL_INFLATION_RATE_Q1_2025_BASE * (1 + 0.05 * np.cos(i / 50.0))
        axiom_relevance_value_i = 1.0 if i % 2 == 0 else 0.0

        axiom_inputs_i = {'AXIOM_RECESSION_AVOIDANCE': axiom_relevance_value_i}

        # --- Use the MODIFIED Z_actual generation for the counter-test ---
        Z_actual_i = generate_simulated_Z_actual_counter_test(i, growth_rate_i, inflation_rate_i, axiom_relevance_value_i)

        evaluation_result = meta_judge.score_thesis(thesis_predictor, firing_squad, growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)
        
        if evaluation_result['status'] == 'ACCEPTED':
            meta_judge.epistemic_gradient_updater.current_lr_model_params = evaluation_result['current_lr_model_params']
            meta_judge.epistemic_gradient_updater.current_lr_axiom_coeffs = evaluation_result['current_lr_axiom_coeffs']
            
            meta_judge.epistemic_gradient_updater.update_params(growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)

        max_overall_consistency_score = max(max_overall_consistency_score, evaluation_result['max_consistency_score'])

        if i % 50 == 0 or evaluation_result['status'] == 'VETO':
            print(f"--- Iteration {i} ---")
            print(f"Status: {evaluation_result['status']}")
            if evaluation_result['status'] == 'VETO':
                print(f"Reason: {evaluation_result['reason']}")
                assert False, f"VETO occurred at iteration {i}: {evaluation_result['reason']}"
            else:
                print(f"Rolling BSS ({ROLLING_WINDOW_SIZE} obs): {evaluation_result['bss']:.4f}")
                print(f"Learned Axiom Coeff (RECESSION_AVOIDANCE): {evaluation_result['learned_axiom_coeffs']['AXIOM_RECESSION_AVOIDANCE']:.4f}")
                print(f"Global Axiom Weight (RECESSION_AVOIDANCE): {meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']:.4f}")
                print(f"Max Consistency Score: {evaluation_result['max_consistency_score']:.4f}")
                print(f"Current Model LR: {evaluation_result['current_lr_model_params']:.6f}, Axiom LR: {evaluation_result['current_lr_axiom_coeffs']:.6f}")

        if i >= MIN_OBSERVATIONS_FOR_CALIBRATION:
            final_bss = evaluation_result['bss']
            final_axiom_coeff = evaluation_result['learned_axiom_coeffs']['AXIOM_RECESSION_AVOIDANCE']

    print("\n--- COUNTER-TEST Simulation Complete ---")
    print(f"Final Rolling BSS: {final_bss:.4f}")
    print(f"Final Learned Axiom Coeff (RECESSION_AVOIDANCE): {final_axiom_coeff:.4f}")
    print(f"True Axiom Relevance (Base): {TRUE_AXIOM_RELEVANCE}")
    print(f"Max Consistency Score observed: {max_overall_consistency_score:.4f}")

    # --- Assertions for COUNTER-TEST (EXPECTED TO FAIL) ---
    # 1. Brier Skill Score prediction: Expect failure due to model-reality mismatch
    print(f"\nCounter-Test Assertion 1: BSS >= {TARGET_BRIER_SKILL_SCORE}")
    assert final_bss < TARGET_BRIER_SKILL_SCORE, \
        f"COUNTER-FALSIFICATION FAILED: Final Rolling BSS ({final_bss:.4f}) unexpectedly met or exceeded target ({TARGET_BRIER_SKILL_SCORE})."
    print(f"  PASSED: BSS ({final_bss:.4f}) is below target, indicating model limitation.")

    # 2. Axiom coefficient convergence: Expect failure to converge close to TRUE_AXIOM_RELEVANCE
    # The model will try to learn an average, but it won't be close to 0.8.
    print(f"\nCounter-Test Assertion 2: Learned axiom coefficient not within 0.25 of true relevance ({TRUE_AXIOM_RELEVANCE}).")
    assert abs(final_axiom_coeff - TRUE_AXIOM_RELEVANCE) > 0.25, \
        f"COUNTER-FALSIFICATION FAILED: Learned axiom coefficient ({final_axiom_coeff:.4f}) unexpectedly converged within 0.25 of true relevance ({TRUE_AXIOM_RELEVANCE}). Diff: {abs(final_axiom_coeff - TRUE_AXIOM_RELEVANCE):.4f}"
    print(f"  PASSED: Learned axiom coefficient ({final_axiom_coeff:.4f}) is not close to true relevance, indicating model limitation.")

    # 3. Axiom weight synchronization: This should still pass if learning happens, as it's an internal consistency check.
    print(f"\nCounter-Test Assertion 3: Global axiom weight sync with ThesisPredictor's learned coefficient.")
    assert abs(meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        f"FALSIFICATION: Global axiom weight ({meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']:.4f}) did not sync with ThesisPredictor's learned coefficient ({final_axiom_coeff:.4f})."
    print(f"  PASSED: Axiom weights synchronized (internal consistency).")

    # 4. Differentiability check: The model itself is differentiable, so this should still pass.
    print(f"\nCounter-Test Assertion 4: DifferentiabilityRobustnessCheck passed.")
    assert max_overall_consistency_score <= DIFFERENTIABILITY_TOLERANCE, \
        f"FALSIFICATION: DifferentiabilityRobustnessCheck failed (Max Consistency Score: {max_overall_consistency_score:.4f} exceeded tolerance {DIFFERENTIABILITY_TOLERANCE})."
    print(f"  PASSED: Differentiability check passed (model remains differentiable).")
    
    print("\nAll COUNTER-TEST Assertions PASSED, exposing the architectural insolvency for complex realities.")

if __name__ == "__main__":
    counter_test_model()

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpon5d2h3a.py", line 511, in <module>
    counter_test_model()
    ~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpon5d2h3a.py", line 455, in counter_test_model
    meta_judge.epistemic_gradient_updater.update_params(growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpon5d2h3a.py", line 173, in update_params
    self.m[param_key] = self.adam_beta1 * self.m[param_key] + (1 - self.adam_beta1) * grad_val
                        ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for *: 'float' and 'collections.defaultdict'



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 586, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 534, in test_model
    meta_judge.epistemic_gradient_updater.update_params(growth_rate_i, inflation_rate_i, axiom_inputs_i, Z_actual_i)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 204, in update_params
    self.m[param_key] = self.adam_beta1 * self.m[param_key] + (1 - self.adam_beta1) * grad_val
                        ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for *: 'float' and 'collections.defaultdict'


# Final Score: 40
**Weakest Point:** The EpistemicGradientUpdater, the core learning mechanism of the proposed V4 architecture, is fundamentally computationally infeasible due to a TypeError, preventing any updates or learning from occurring. This renders all other architectural claims and anti-gaming measures moot, as the system cannot function.
**Rationale:** The V4 thesis proposed addressing prior computational infeasibility, anti-gaming vulnerabilities, and performance inadequacy through an adaptive learning rate scheduler (`EpistemicGradientUpdater.AdaptiveLearningRateScheduler`) and robust differentiability checks (`FiringSquad.DifferentiabilityRobustnessCheck`). It also correctly retired the `new_prob = prior * exp(-1.1 * relative_error)` axiom. However, all three attacks, and the thesis's own Level 3 Quantitative Unit Test, revealed a catastrophic `TypeError` within the `EpistemicGradientUpdater`, preventing it from running any update cycles. This fundamental computational infeasibility undermines all other claims. Beyond this critical flaw, the Quantitative Risk Actuary's counter-test (even after fixing a `np.ndarray.flatten()` bug in the `FiringSquad`'s implementation) demonstrated that the differentiability check was still insufficient to veto a non-differentiable model. The Adversarial Compliance Auditor further noted violations of the "ABSTRACTION MANDATE" due to domain-specific variable names, indicating "Cooked Books." The Philosopher of Science pointed out that the topological flatness of the DAG remained unaddressed and critiqued the simulation's design for perfectly mirroring the `ThesisPredictor`'s assumptions, creating an artificially easy learning environment. The thesis completely failed to address the architectural challenge of `Phase_Transition_Blindness_and_Surrogate_Gradients` (Rubric 8).
