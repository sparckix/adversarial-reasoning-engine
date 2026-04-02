# Adversarial Debate: epistemic_engine_v3

## Attacker: Algorithmic Solvency Auditor
The thesis presents a conceptually robust framework for enhancing numerical stability in axiom credit assignment, particularly under low-entropy `Z_actual` conditions. The introduction of a `CompositeEpistemicLoss` with dynamic weighting via a `LossFunctionSelectionProtocol` and persistent L2 regularization is a sound architectural response to the identified fragility of the Brier Skill Score. The `LOAD-BEARING VARIABLES` are appropriately defined for a simulated environment, with hypothetical economic rates and non-linear function parameters establishing a complex ground truth. The chosen values for Adam optimizer parameters, learning rates, and regularization strengths are within standard operational ranges for machine learning systems. The `low_variance_z_actual_threshold` and `convergence_tolerance` are reasonable system parameters for detecting and responding to specific numerical states.

However, a critical insolvency exists within the Python Falsification Suite's implementation of the `generate_z_actual` function, specifically in its simulation of `low_variance_active` conditions. The function's logic, which alternates between `np.random.uniform(0.05, 0.15)` and `np.random.uniform(0.85, 0.95)` based on iteration modulo, does not produce a low-variance `Z_actual` distribution over the `rolling_window_size`. Instead, it generates a distinctly bimodal distribution, which will inherently exhibit a *high* variance, significantly exceeding the `low_variance_z_actual_threshold` of `0.005`.

This misrepresentation of the "low variance" condition has the following systemic implications:
1.  **Protocol Activation Failure:** The `MetaJudge`'s `LossFunctionSelectionProtocol`, which is designed to dynamically adjust loss weights when `current_z_variance < low_variance_z_actual_threshold`, will not be triggered under the intended stress conditions. The simulated "low variance" period will consistently register as "STABLE" due to its high actual variance, preventing the protocol from switching to `BinaryCrossEntropyLoss` dominance and increased L2 regularization.
2.  **Invalidated Falsifiability:** Consequently, Falsifiability Prediction 2, which asserts that `BinaryCrossEntropyLoss` will be dominant during the low-variance interval, cannot be accurately tested. The Mutator's suite would either fail this assertion because the protocol never activated, or it would pass under a misinterpretation of the underlying data distribution. The empirical validation of the protocol's adaptive capability under true numerical fragility is therefore absent.
3.  **Unverified Robustness:** The core claim of the thesis—that the system achieves robust convergence under extreme low-entropy conditions—remains unverified by the provided code. The Mutator has failed to construct a test environment that accurately reflects the specific numerical fragility it purports to address.

The `calculate_brier_skill_score` function's handling of `bs_baseline == 0` by returning `0.0` is a pragmatic measure to prevent division by zero. While it avoids a runtime error, it represents a simplification of a mathematically undefined scenario rather than a comprehensive resolution of the metric's inherent fragility. This is a minor point compared to the fundamental flaw in `Z_actual` generation.

**So What for the Meta-Judge:**

The Mutator's proposed `LossFunctionSelectionProtocol` is intended to provide numerical stability when `Z_actual` exhibits low variance, a critical edge case for Brier Skill Score-based credit assignment. However, the Python Falsification Suite's `generate_z_actual` function, when configured to simulate these low-variance conditions, produces a high-variance bimodal distribution. This miscalibration means the `LossFunctionSelectionProtocol` is unlikely to be triggered as designed, rendering the Mutator's self-validation of its robustness under true low-entropy `Z_actual` conditions inconclusive. The system's resilience to the specific numerical fragility it aims to mitigate is therefore not empirically demonstrated by the provided evidence, indicating a significant gap in the verification of its core anti-fragility mechanism.

```python
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import math

# --- LOAD-BEARING VARIABLES (from above table) ---
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
low_variance_z_actual_threshold = 0.005
base_l2_axiom_regularization_strength = 0.001
high_l2_axiom_regularization_strength = 0.01
convergence_tolerance = 0.10
low_variance_simulation_interval = 10 # iterations
calibration_check_iterations = 50 # iterations after min_observations_for_calibration

# --- HELPER FUNCTIONS (Copied from Mutator's suite for context) ---
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def calculate_brier_score(P_predicted, Z_actual):
    return np.mean((P_predicted - Z_actual)**2)

def calculate_brier_skill_score(P_predicted_history, Z_actual_history):
    if len(P_predicted_history) < rolling_window_size:
        return -1.0 # Not enough data
    
    recent_P_predicted = P_predicted_history[-rolling_window_size:]
    recent_Z_actual = Z_actual_history[-rolling_window_size:]

    if len(recent_Z_actual) == 0:
        return -1.0

    bs = np.mean((recent_P_predicted - recent_Z_actual)**2)
    
    if len(recent_Z_actual) > 0:
        naive_baseline_prediction = np.mean(recent_Z_actual)
        bs_baseline = np.mean((naive_baseline_prediction - recent_Z_actual)**2)
    else:
        bs_baseline = 1.0

    if bs_baseline == 0:
        return 0.0
    
    return 1 - (bs / bs_baseline)

# Mutator's original generate_z_actual (for comparison)
def mutator_generate_z_actual(growth_rate, inflation_rate, axiom_value, current_iteration, low_variance_active=False):
    z = true_bias_nl + \
        true_growth_coeff_nl * math.sin(growth_rate * true_growth_freq_nl) + \
        true_inflation_coeff_nl * math.cos(inflation_rate * true_inflation_freq_nl) + \
        true_interaction_coeff_nl * growth_rate * inflation_rate + \
        true_axiom_relevance * axiom_value
    
    z_prob = sigmoid(z)

    if low_variance_active:
        # This logic creates a bimodal distribution, resulting in HIGH variance
        if current_iteration % 3 == 0:
            return np.random.uniform(0.05, 0.15)
        else:
            return np.random.uniform(0.85, 0.95)
    else:
        noise = np.random.normal(0, 0.1) 
        return np.clip(z_prob + noise, 0.01, 0.99)

# --- CORRECTED generate_z_actual for true low variance ---
def corrected_generate_z_actual(growth_rate, inflation_rate, axiom_value, current_iteration, low_variance_active=False):
    if low_variance_active:
        # Truly force Z_actual into a low variance state, e.g., always near 0.9 with minimal noise
        return np.random.uniform(0.89, 0.91) # Very tight range, variance will be low
    else:
        # Use the original non-linear generation for normal periods
        z = true_bias_nl + \
            true_growth_coeff_nl * math.sin(growth_rate * true_growth_freq_nl) + \
            true_inflation_coeff_nl * math.cos(inflation_rate * true_inflation_freq_nl) + \
            true_interaction_coeff_nl * growth_rate * inflation_rate + \
            true_axiom_relevance * axiom_value
        z_prob = sigmoid(z)
        noise = np.random.normal(0, 0.1) 
        return np.clip(z_prob + noise, 0.01, 0.99)

# --- ARCHITECTURAL COMPONENTS (Copied from Mutator's suite) ---
class ThesisPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, initial_axiom_coeffs):
        super(ThesisPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
        self.learned_axiom_coeffs = nn.ParameterDict()
        for axiom_name, initial_value in initial_axiom_coeffs.items():
            self.learned_axiom_coeffs[axiom_name] = nn.Parameter(torch.tensor(float(initial_value), dtype=torch.float32))

    def calculate_p_predicted(self, input_features, axiom_input_values):
        processed_features = []
        for feat in input_features:
            processed_features.append(feat)
        for axiom_name, axiom_val in axiom_input_values.items():
            processed_features.append(axiom_val * self.learned_axiom_coeffs[axiom_name])
        x = torch.tensor(processed_features, dtype=torch.float32).unsqueeze(0)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        P_predicted = self.sigmoid(x).item()
        if not (0.0 <= P_predicted <= 1.0):
            raise ValueError(f"P_predicted out of bounds: {P_predicted}")
        return P_predicted

class EpistemicGradientUpdater:
    def __init__(self, thesis_predictor):
        self.thesis_predictor = thesis_predictor
        self.optimizer = optim.Adam([
            {'params': self.thesis_predictor.fc1.parameters(), 'lr': learning_rate_model_params},
            {'params': self.thesis_predictor.fc2.parameters(), 'lr': learning_rate_model_params},
            {'params': self.thesis_predictor.learned_axiom_coeffs.parameters(), 'lr': learning_rate_axiom_coeffs}
        ], betas=(adam_beta1, adam_beta2), eps=adam_epsilon_stabilizer)
        self.bce_loss_fn = nn.BCELoss()
        self.w_bce = 0.5
        self.w_brier = 0.5
        self.axiom_l2_regularization_strength = base_l2_axiom_regularization_strength

    def update_loss_weights(self, w_bce, w_brier, axiom_l2_strength):
        self.w_bce = w_bce
        self.w_brier = w_brier
        self.axiom_l2_regularization_strength = axiom_l2_strength

    def compute_composite_loss(self, p_predicted, z_actual):
        p_predicted_t = torch.tensor(p_predicted, dtype=torch.float32).unsqueeze(0)
        z_actual_t = torch.tensor(z_actual, dtype=torch.float32).unsqueeze(0)
        bce_loss = self.bce_loss_fn(p_predicted_t, z_actual_t)
        brier_loss = torch.mean((p_predicted_t - z_actual_t)**2)
        l2_axiom_loss = 0.0
        for param in self.thesis_predictor.learned_axiom_coeffs.parameters():
            l2_axiom_loss += torch.norm(param, p=2)
        total_loss = (self.w_bce * bce_loss) + \
                     (self.w_brier * brier_loss) + \
                     (self.axiom_l2_regularization_strength * l2_axiom_loss)
        return total_loss

    def update_parameters(self, p_predicted, z_actual):
        self.optimizer.zero_grad()
        loss = self.compute_composite_loss(p_predicted, z_actual)
        loss.backward()
        self.optimizer.step()
        return loss.item()

class MetaJudge:
    def __init__(self, axiom_store):
        self.axiom_weights = {k: v for k, v in axiom_store.items()}
        self.p_predicted_history = deque(maxlen=rolling_window_size)
        self.z_actual_history = deque(maxlen=rolling_window_size)
        self.loss_selection_log = []

    def validate_thesis_predictor_architecture(self, thesis_predictor):
        if not isinstance(thesis_predictor.learned_axiom_coeffs, nn.ParameterDict):
            raise ValueError("ThesisPredictor must have a 'learned_axiom_coeffs' ParameterDict.")
        for axiom_name in self.axiom_weights:
            if axiom_name not in thesis_predictor.learned_axiom_coeffs:
                raise ValueError(f"Axiom '{axiom_name}' not exposed as a learnable parameter in ThesisPredictor.")
            if not isinstance(thesis_predictor.learned_axiom_coeffs[axiom_name], nn.Parameter):
                 raise ValueError(f"Axiom '{axiom_name}' in learned_axiom_coeffs must be a nn.Parameter.")
        
    def validate_epistemic_updater_configuration(self, updater):
        if not hasattr(updater, 'compute_composite_loss') or not callable(updater.compute_composite_loss):
            raise ValueError("EpistemicGradientUpdater must implement 'compute_composite_loss'.")
        if not all(hasattr(updater, attr) for attr in ['w_bce', 'w_brier', 'axiom_l2_regularization_strength']):
            raise ValueError("EpistemicGradientUpdater missing dynamic loss weight attributes.")
        
    def axiom_weight_synchronization(self, thesis_predictor):
        for axiom_name, param in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = param.item()

    def loss_function_selection_protocol(self, updater, current_iteration):
        if len(self.z_actual_history) < rolling_window_size:
            current_z_variance = 1.0
        else:
            current_z_variance = np.var(list(self.z_actual_history))

        selected_w_bce = 0.5
        selected_w_brier = 0.5
        selected_l2_strength = base_l2_axiom_regularization_strength

        if current_z_variance < low_variance_z_actual_threshold:
            selected_w_bce = 1.0
            selected_w_brier = 0.0
            selected_l2_strength = high_l2_axiom_regularization_strength
            self.loss_selection_log.append(f"Iter {current_iteration}: UNSTABLE (variance={current_z_variance:.6f}) - BCE dominant, L2 high")
        else:
            self.loss_selection_log.append(f"Iter {current_iteration}: STABLE (variance={current_z_variance:.6f}) - Hybrid loss, L2 base")
        
        updater.update_loss_weights(selected_w_bce, selected_w_brier, selected_l2_strength)

# --- SIMULATION FUNCTION (Modified to accept a Z_actual generator) ---
def run_simulation_with_generator(z_actual_generator_func, enable_dynamic_loss_protocol=True):
    initial_axiom_coeffs = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value}
    
    thesis_predictor = ThesisPredictor(
        input_size=2 + len(initial_axiom_coeffs),
        hidden_size=hidden_layer_size,
        initial_axiom_coeffs=initial_axiom_coeffs
    )
    epistemic_updater = EpistemicGradientUpdater(thesis_predictor)
    meta_judge = MetaJudge(initial_axiom_coeffs)

    meta_judge.validate_thesis_predictor_architecture(thesis_predictor)
    meta_judge.validate_epistemic_updater_configuration(epistemic_updater)

    axiom_coeff_history = []
    brier_skill_score_history = []
    
    total_iterations = min_observations_for_calibration + calibration_check_iterations
    
    for i in range(1, total_iterations + 1):
        growth_rate = np.random.uniform(hypothetical_economy_growth_rate_q1_2025_base * 0.5, hypothetical_economy_growth_rate_q1_2025_base * 1.5)
        inflation_rate = np.random.uniform(hypothetical_inflation_rate_q1_2025_base * 0.5, hypothetical_inflation_rate_q1_2025_base * 1.5)
        current_axiom_input_value = 1.0
        
        is_low_variance_period = (i > min_observations_for_calibration / 2) and \
                                 (i <= min_observations_for_calibration / 2 + low_variance_simulation_interval)

        z_actual = z_actual_generator_func(growth_rate, inflation_rate, current_axiom_input_value, i, 
                                           low_variance_active=is_low_variance_period)
        
        input_features = [growth_rate, inflation_rate]
        axiom_input_values = {'AXIOM_RECESSION_AVOIDANCE': current_axiom_input_value}
        p_predicted = thesis_predictor.calculate_p_predicted(input_features, axiom_input_values)

        meta_judge.p_predicted_history.append(p_predicted)
        meta_judge.z_actual_history.append(z_actual)
        
        if enable_dynamic_loss_protocol:
            meta_judge.loss_function_selection_protocol(epistemic_updater, i)
        else:
            epistemic_updater.update_loss_weights(w_bce=0.0, w_brier=1.0, axiom_l2_strength=base_l2_axiom_regularization_strength)
            meta_judge.loss_selection_log.append(f"Iter {i}: PROTOCOL DISABLED - Forced Brier")

        loss_value = epistemic_updater.update_parameters(p_predicted, z_actual)
        
        if i % axiom_sync_frequency == 0:
            meta_judge.axiom_weight_synchronization(thesis_predictor)

        axiom_coeff_history.append(thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item())

        if i >= rolling_window_size:
            bss = calculate_brier_skill_score(list(meta_judge.p_predicted_history), list(meta_judge.z_actual_history))
            brier_skill_score_history.append(bss)
        else:
            brier_skill_score_history.append(-1.0)

    final_axiom_coeff = thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
    final_global_axiom_weight = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
    
    if len(brier_skill_score_history) > calibration_check_iterations:
        avg_bss_check = np.mean([x for x in brier_skill_score_history[min_observations_for_calibration - rolling_window_size:] if x != -1.0])
    else:
        avg_bss_check = -1.0

    return {
        "final_axiom_coeff": final_axiom_coeff,
        "final_global_axiom_weight": final_global_axiom_weight,
        "avg_bss_check": avg_bss_check,
        "axiom_coeff_history": axiom_coeff_history,
        "loss_selection_log": meta_judge.loss_selection_log,
        "z_actual_history": list(meta_judge.z_actual_history) # Return full history for variance check
    }

# --- COUNTER-TEST IMPLEMENTATION ---
print("--- Running COUNTER-TEST ---")

# Part 1: Expose the Mutator's `generate_z_actual` flaw
print("\n--- Verifying Mutator's 'low_variance_active' simulation ---")
# Simulate a period where Mutator's low_variance_active would be true
mutator_z_actual_samples = []
# We need enough samples to fill the rolling window and observe variance
for i in range(rolling_window_size * 2): # Simulate enough iterations to get a stable variance estimate
    mutator_z_actual_samples.append(mutator_generate_z_actual(0.02, 0.03, 1.0, i, low_variance_active=True))

# Calculate variance over a window that would be used by the MetaJudge
mutator_simulated_variance = np.var(mutator_z_actual_samples[-rolling_window_size:])
print(f"Mutator's 'low_variance_active' Z_actual variance over {rolling_window_size} samples: {mutator_simulated_variance:.6f}")
print(f"Configured low_variance_z_actual_threshold: {low_variance_z_actual_threshold:.6f}")

assert mutator_simulated_variance > low_variance_z_actual_threshold, \
    f"COUNTER-TEST FAILED: Mutator's 'low_variance_active' Z_actual variance ({mutator_simulated_variance:.6f}) " \
    f"is NOT greater than the threshold ({low_variance_z_actual_threshold:.6f}). " \
    f"The Mutator's simulation of low variance is flawed; it produces high variance."

print("COUNTER-TEST PASSED Part 1: Mutator's 'low_variance_active' indeed produces high variance, confirming the flaw.")

# Part 2: Demonstrate intended behavior with a corrected `generate_z_actual`
print("\n--- Running simulation with CORRECTED 'low_variance_active' Z_actual generation ---")

results_corrected_dynamic = run_simulation_with_generator(corrected_generate_z_actual, enable_dynamic_loss_protocol=True)

# Verify that the corrected low-variance period actually has low variance
# The low variance period starts at min_observations_for_calibration // 2 and lasts for low_variance_simulation_interval
low_variance_start_idx = min_observations_for_calibration // 2
low_variance_end_idx = low_variance_start_idx + low_variance_simulation_interval
# Ensure we have enough history for the rolling window to be meaningful
corrected_low_variance_samples = results_corrected_dynamic["z_actual_history"][max(0, low_variance_start_idx - rolling_window_size + 1) : low_variance_end_idx + 1]
corrected_simulated_variance = np.var(corrected_low_variance_samples[-rolling_window_size:]) # Variance over the last rolling window in the low-variance period

print(f"Corrected 'low_variance_active' Z_actual variance during critical interval: {corrected_simulated_variance:.6f}")
assert corrected_simulated_variance < low_variance_z_actual_threshold, \
    f"COUNTER-TEST FAILED: Corrected 'low_variance_active' Z_actual variance ({corrected_simulated_variance:.6f}) " \
    f"is NOT below the threshold ({low_variance_z_actual_threshold:.6f}). " \
    f"The corrected simulation failed to produce true low variance."

print("COUNTER-TEST PASSED Part 2a: Corrected 'low_variance_active' successfully produces low variance.")

# Now, verify Prediction 2 (Loss Function Adaptability) with the corrected low variance
low_variance_log_entries_corrected = [entry for entry in results_corrected_dynamic["loss_selection_log"] 
                                      if f"Iter " in entry and int(entry.split(' ')[1].split(':')[0]) > low_variance_start_idx and \
                                         int(entry.split(' ')[1].split(':')[0]) <= low_variance_end_idx]

bce_dominant_count_corrected = sum(1 for entry in low_variance_log_entries_corrected if "BCE dominant" in entry)

print(f"Log entries during corrected low variance period: {len(low_variance_log_entries_corrected)}")
print(f"BCE dominant entries during corrected low variance period: {bce_dominant_count_corrected}")

assert len(low_variance_log_entries_corrected) > 0, "No log entries for corrected low variance period."
assert (bce_dominant_count_corrected / len(low_variance_log_entries_corrected)) > 0.8, \
    f"COUNTER-TEST FAILED Part 2b: BCE was NOT dominant (>80%) during corrected low variance period. " \
    f"Only {bce_dominant_count_corrected / len(low_variance_log_entries_corrected):.2f} dominant. " \
    f"The LossFunctionSelectionProtocol did not activate as expected under true low variance."

print("COUNTER-TEST PASSED Part 2b: LossFunctionSelectionProtocol correctly switched to BCE dominance under true low variance.")

# Verify Prediction 1 (Axiom Convergence) with the corrected low variance
assert abs(results_corrected_dynamic["final_axiom_coeff"] - true_axiom_relevance) <= convergence_tolerance, \
    f"COUNTER-TEST FAILED Part 2c: Axiom coefficient ({results_corrected_dynamic['final_axiom_coeff']:.4f}) did not converge " \
    f"within tolerance {convergence_tolerance} to {true_axiom_relevance} with corrected dynamic loss."

print("COUNTER-TEST PASSED Part 2c: Axiom coefficient converged under true low variance with dynamic loss.")

print("\nALL COUNTER-TESTS PASSED: The Mutator's simulation of low variance was flawed, but the underlying protocol functions correctly when exposed to actual low-variance conditions.")
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmprz8ck6vs.py", line 2, in <module>
    import torch
ModuleNotFoundError: No module named 'torch'


