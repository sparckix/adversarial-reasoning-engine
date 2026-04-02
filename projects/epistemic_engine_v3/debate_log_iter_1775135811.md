# Adversarial Debate: epistemic_engine_v3

## Attacker: Quantitative Risk Actuary, specializing in Numerical Stability and Gradient Integrity
The thesis correctly identifies a fundamental mathematical flaw in the `new_prob = prior * exp(-1.1 * relative_error)` formula. This relationship is unsuitable for direct probabilistic updates as it can produce values outside the [0, 1] domain, violating the axiomatic requirements of probability theory. Its structural irrelevance to empirically calibrated probabilities and gradient-based credit assignment is a valid critique.

However, the accompanying Python Falsification Suite exhibits critical numerical and parametric misrepresentations, which undermine its claims of robustness and constitute "cooked books."

**Critique of the `EpistemicGradientUpdater`'s Adam implementation:**
The `EpistemicGradientUpdater` delegates its core optimization to PyTorch's `optim.Adam`. This implementation inherently includes the `m_hat` and `v_hat` bias corrections, which are standard for Adam and contribute to its numerical stability. The chosen hyperparameters (`adam_beta1=0.9`, `adam_beta2=0.999`, `adam_epsilon_stabilizer=1e-8`) are industry-standard values. Therefore, the direct implementation of Adam within the `EpistemicGradientUpdater` is not a source of instability or "cooked books." Potential issues would arise from the gradients provided to Adam, which is addressed below.

**Critique of the `FiringSquad`'s numerical derivative calculation:**
The `FiringSquad.DifferentiabilityRobustnessCheck` assesses gradient consistency by perturbing an axiom coefficient and comparing gradients across these perturbations. This method provides a reasonable approximation of the local curvature or stability of the gradient. The `robustness_perturbation_epsilon_scales` are fixed values (`[0.00001, 0.0001, 0.001]`), which contradicts the prompt's description of "dynamic `epsilon` approaching `1e-6`." While this is a discrepancy between description and implementation, the chosen static scales are small and appropriate for probing local differentiability. The calculation itself is a valid heuristic for gradient stability. No "cooked books" are identified in the numerical method itself, beyond the descriptive inconsistency.

**Critique of bounds/precision of `LOAD-BEARING VARIABLES` under extreme simulated conditions:**

1.  **Probabilities near 0 or 1 causing sigmoid saturation:** The `ThesisPredictor` utilizes a `torch.sigmoid` activation in its output layer, which is inherently susceptible to gradient vanishing when its input leads to outputs extremely close to 0 or 1. The Mutator's simulation, however, artificially mitigates this challenge by clipping the `z_actual` target values to `[0.01, 0.99]` using `np.clip(..., 0.01, 0.99)`. This prevents the model from ever being trained on true 0 or 1 probabilities, which are the most numerically challenging for sigmoid-based architectures. This constitutes a significant "cooked book," as it simplifies the learning task and masks a fundamental numerical instability that would likely manifest under genuinely extreme, unclipped probabilistic targets. The model's output can still saturate, but the loss function will not drive it to the extreme edges where gradients are minimal.

2.  **`growth_rate`/`inflation_rate` values leading to gradient vanishing/exploding:** The simulated `growth_rate` and `inflation_rate` values, along with their non-linear coefficients, appear to generate inputs to the neural network that are within numerically stable ranges. The interaction term `true_interaction_coeff_nl * growth_rate * inflation_rate` (e.g., `500 * 0.02 * 0.03 = 0.3`) does not produce extreme values that would immediately suggest gradient vanishing or exploding within the MLP layers, assuming appropriate weight initialization.

3.  **Stability of `BS_reference` when close to zero:** The `MetaJudge.calculate_brier_skill_score` includes a robust check (`if baseline_bs < 1e-6: return 0.0`) to prevent division by zero when the baseline Brier Score is extremely small. This is a necessary numerical safeguard and not a "cooked book."

4.  **Impact of the `_sigmoid` clipping:** As noted, the clipping is applied to the *target* `z_actual`, not the `ThesisPredictor`'s `_sigmoid` output. This artificial constraint on the target values prevents the model from being rigorously tested against the most challenging scenarios for sigmoid saturation, thereby creating an illusion of robustness.

**Parametric Grounding Audit of `LOAD-BEARING VARIABLES`:**

*   `hypothetical_economy_growth_rate_q1_2025_base`: `0.02` (2% per quarter). Annualized, this is approximately 8.24%. While high, it is plausible for a rapidly developing or recovering economy.
*   `hypothetical_inflation_rate_q1_2025_base`: `0.03` (3% per quarter). Annualized, this is approximately 12.55%. This value is **grossly misapplied** as a "baseline for simulated inflation rate." A 12.55% annualized inflation rate is characteristic of severe economic instability or hyperinflation, not a typical baseline for a stable economy in Q1 2025. This significantly distorts the "real-world" grounding claimed by the Mutator and constitutes a "cooked book" by presenting an extreme economic condition as a standard baseline.

**So What for the Meta-Judge:**
The thesis correctly identifies a fundamental mathematical flaw in a proposed probability update formula. However, the accompanying Python Falsification Suite contains critical numerical and parametric misrepresentations that compromise its validity. The `hypothetical_inflation_rate_q1_2025_base` is parametrically misgrounded, presenting an extreme inflationary environment as a baseline. More significantly, the artificial clipping of the `z_actual` target to `[0.01, 0.99]` fundamentally undermines the test of the `ThesisPredictor`'s numerical stability. By preventing the model from encountering true 0 or 1 probabilities, the suite fails to expose the inherent gradient vanishing issues of sigmoid functions under extreme saturation. This creates an illusion of robustness that would likely collapse under genuinely adversarial data, rendering the falsification suite insufficient for validating the system's mathematical robustness in real-world extreme conditions.

---

```python
import torch
import torch.nn as nn
import torch.optim as optim
import json
import os
import numpy as np
import collections

# Mock up core components for the test (copied from Mutator's code)
class ThesisPredictor(nn.Module):
    """
    Mock ThesisPredictor that uses an MLP and integrates learnable axiom coefficients.
    Outputs a probability [0,1].
    """
    def __init__(self, num_inputs, hidden_layer_size, initial_axiom_coefficient_value):
        super().__init__()
        # num_inputs here is features + 1 for the axiom's presence/value
        self.fc1 = nn.Linear(num_inputs, hidden_layer_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_layer_size, 1)
        
        self.learned_axiom_coeffs = nn.ParameterDict({
            'AXIOM_RECESSION_AVOIDANCE': nn.Parameter(torch.tensor(initial_axiom_coefficient_value, dtype=torch.float32))
        })

    def forward(self, inputs, axiom_data, override_axiom_coeffs=None):
        # inputs: torch.Tensor of shape (batch_size, num_features)
        # axiom_data: dict of axiom values, e.g., {'AXIOM_RECESSION_AVOIDANCE': tensor}
        
        current_axiom_coeffs = override_axiom_coeffs if override_axiom_coeffs is not None else self.learned_axiom_coeffs

        # Ensure axiom_coeff is a tensor for multiplication and has correct shape
        axiom_val = axiom_data['AXIOM_RECESSION_AVOIDANCE'] * current_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE']
        
        # Concatenate axiom_val with original inputs.
        # Ensure axiom_val has batch_size dimension if inputs does.
        if axiom_val.dim() == 0: # Scalar axiom_val
            axiom_val = axiom_val.unsqueeze(0).repeat(inputs.shape[0]) # Match batch size
        elif axiom_val.dim() == 1 and axiom_val.shape[0] != inputs.shape[0]:
             axiom_val = axiom_val.repeat(inputs.shape[0]) # Match batch size
        
        combined_inputs = torch.cat((inputs, axiom_val.unsqueeze(-1)), dim=-1) # Add axiom as an input feature

        x = self.fc1(combined_inputs)
        x = self.relu(x)
        output = torch.sigmoid(self.fc2(x)) # Ensure P_predicted is [0,1]
        return output.squeeze(-1) # Output a single probability

    def get_trainable_param_groups(self, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs):
        """
        Returns parameter groups for the optimizer, separating MLP weights/biases
        from learned axiom coefficients.
        """
        model_params = [p for name, p in self.named_parameters() if 'learned_axiom_coeffs' not in name]
        axiom_coeffs = [p for name, p in self.named_parameters() if 'learned_axiom_coeffs' in name]
        
        return [
            {'params': model_params, 'lr': initial_learning_rate_model_params},
            {'params': axiom_coeffs, 'lr': initial_learning_rate_axiom_coeffs}
        ]

class EpistemicGradientUpdater:
    """
    Mock EpistemicGradientUpdater managing Adam optimizer and learning rate scheduling.
    """
    def __init__(self, thesis_predictor, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs, 
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer):
        self.thesis_predictor = thesis_predictor
        self.optimizer = self.initialize_optimizer(initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                                                    adam_beta1, adam_beta2, adam_epsilon_stabilizer)
        self.scheduler_patience_counter = 0
        self.best_bss = -float('inf')

    def initialize_optimizer(self, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                             adam_beta1, adam_beta2, adam_epsilon_stabilizer):
        param_groups = self.thesis_predictor.get_trainable_param_groups(
            initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs
        )
        return optim.Adam(param_groups, betas=(adam_beta1, adam_beta2), eps=adam_epsilon_stabilizer)

    def update_learning_rates(self, current_bss, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        """
        Applies a learning rate decay if Brier Skill Score stagnates.
        """
        if current_bss > self.best_bss + min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.scheduler_patience_counter = 0
            return False # No decay
        else:
            self.scheduler_patience_counter += 1
            if self.scheduler_patience_counter >= lr_patience_epochs:
                for param_group in self.optimizer.param_groups:
                    param_group['lr'] = max(param_group['lr'] * lr_decay_factor, min_learning_rate)
                self.scheduler_patience_counter = 0 # Reset counter after decay
                return True # Signaled decay
            return False # No decay yet

class MetaJudge:
    """
    Mock Meta-Judge to calculate Brier Skill Score, synchronize axiom weights,
    and apply vetoes.
    """
    def __init__(self, target_brier_skill_score, rolling_window_size, min_observations_for_calibration, differentiability_tolerance):
        self.target_brier_skill_score = target_brier_skill_score
        self.rolling_window_size = rolling_window_size
        self.min_observations_for_calibration = min_observations_for_calibration
        self.differentiability_tolerance = differentiability_tolerance
        self.predictions = []
        self.actuals = []
        self.axiom_weights = {} # Global axiom store
        self.best_bss = -float('inf')
        self.no_improvement_epochs = 0

    def calculate_brier_skill_score(self):
        """Calculates rolling Brier Skill Score."""
        if len(self.predictions) < self.min_observations_for_calibration:
            return -float('inf') # Not enough data
        
        window_predictions = np.array(self.predictions[-self.rolling_window_size:])
        window_actuals = np.array(self.actuals[-self.rolling_window_size:])
        
        bs = np.mean((window_predictions - window_actuals)**2)
        
        # Baseline Brier Score (predicting the mean probability)
        baseline_prob = np.mean(window_actuals)
        baseline_bs = np.mean((baseline_prob - window_actuals)**2)
        
        if baseline_bs < 1e-6: # Avoid division by zero if baseline is perfect
            return 0.0

        bss = 1 - (bs / baseline_bs)
        return bss

    def AxiomDifferentiabilityVeto(self, gradient_consistency_score):
        """Vetoes if gradient consistency is outside tolerance."""
        return gradient_consistency_score > self.differentiability_tolerance

    def AxiomWeightSynchronization(self, thesis_predictor):
        """Synchronizes learned axiom coefficients to the global store."""
        for axiom_name, param_tensor in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = param_tensor.item()
            
    def PerformanceGuidedLearningRateAdjustment(self, current_bss, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        """Determines if learning rates should be decayed based on BSS trend."""
        if current_bss > self.best_bss + min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.no_improvement_epochs = 0
            return False
        else:
            self.no_improvement_epochs += 1
            if self.no_improvement_epochs >= lr_patience_epochs:
                self.no_improvement_epochs = 0
                return True
            return False
            
    def PhaseTransitionVeto(self, phase_transition_event):
        """Absolute Veto if a phase transition with pivot trigger is detected."""
        return phase_transition_event is not None and phase_transition_event.get('topological_pivot_trigger', False)

class FiringSquad:
    """
    Mock FiringSquad for executing adversarial checks, specifically DifferentiabilityRobustnessCheck.
    """
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, inputs, axiom_data, axiom_name):
        """
        Checks the consistency of gradients for a given axiom coefficient
        by perturbing its value and comparing gradients.
        """
        original_coeff = thesis_predictor.learned_axiom_coeffs[axiom_name].clone().detach()
        original_coeff.requires_grad_(True)
        
        # Compute gradient at original value
        output = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: original_coeff})
        output.sum().backward(retain_graph=True) # retain_graph for multiple backward calls on same graph
        grad_original = original_coeff.grad.clone()
        
        if grad_original is None:
            return float('inf') 

        consistency_scores = []

        for eps_scale in self.robustness_perturbation_epsilon_scales:
            # Perturb upwards
            perturbed_coeff_up = original_coeff.clone().detach() + eps_scale
            perturbed_coeff_up.requires_grad_(True)
            thesis_predictor.zero_grad()
            output_up = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: perturbed_coeff_up})
            output_up.sum().backward(retain_graph=True)
            grad_up = perturbed_coeff_up.grad.clone()

            # Perturb downwards
            perturbed_coeff_down = original_coeff.clone().detach() - eps_scale
            perturbed_coeff_down.requires_grad_(True)
            thesis_predictor.zero_grad()
            output_down = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: perturbed_coeff_down})
            output_down.sum().backward(retain_graph=True)
            grad_down = perturbed_coeff_down.grad.clone()

            if grad_up is None or grad_down is None:
                consistency_scores.append(float('inf'))
                continue
            
            # Consistency score: absolute difference between gradients at perturbed points
            # compared to original, normalized by perturbation scale.
            consistency_score = (torch.abs(grad_original - grad_up) + torch.abs(grad_original - grad_down)) / (2 * eps_scale) 
            consistency_scores.append(consistency_score.item())
        
        # Max consistency score across all scales
        max_consistency = max(consistency_scores)
        return max_consistency if max_consistency != float('inf') else float('inf')

class PhaseTransitionDetector:
    """
    NEW: Detects phase transitions by monitoring prediction residuals and input features.
    """
    def __init__(self, cpd_window_size, cpd_threshold_multiplier, cpd_min_events_for_transition):
        self.cpd_window_size = cpd_window_size
        self.cpd_threshold_multiplier = cpd_threshold_multiplier
        self.cpd_min_events_for_transition = cpd_min_events_for_transition
        self.residuals_history = collections.deque(maxlen=cpd_window_size)
        self.consecutive_anomalies = 0

    def detect(self, current_residual, current_iteration):
        """
        Detects sustained deviations in residuals using a moving average and std dev threshold.
        Returns a PhaseTransitionEvent dict if detected.
        """
        self.residuals_history.append(current_residual)

        if len(self.residuals_history) < self.cpd_window_size:
            return None # Not enough data to establish baseline

        residuals_np = np.array(self.residuals_history)
        window_mean_residual = np.mean(residuals_np)
        window_std_residual = np.std(residuals_np)
        
        is_anomaly = False
        if window_std_residual > 1e-6: # Avoid division by zero
            if abs(current_residual - window_mean_residual) / window_std_residual > self.cpd_threshold_multiplier:
                is_anomaly = True
        elif abs(current_residual - window_mean_residual) > 1e-6: # If std is near zero, any deviation is significant
            is_anomaly = True

        if is_anomaly:
            self.consecutive_anomalies += 1
            if self.consecutive_anomalies >= self.cpd_min_events_for_transition:
                event = {
                    'type': 'PhaseTransitionEvent',
                    'timestamp': current_iteration,
                    'detected_feature': 'prediction_residual',
                    'trigger_metric': 'residual_deviation_sigma',
                    'value_at_trigger': current_residual,
                    'baseline_mean': window_mean_residual,
                    'baseline_std': window_std_residual,
                    'topological_pivot_trigger': True
                }
                self.consecutive_anomalies = 0 # Reset after triggering
                return event
        else:
            self.consecutive_anomalies = 0
            
        return None

class EpistemicContextManager:
    """
    NEW: Synthesizes all relevant epistemic state into a structured JSON for LLM integration.
    """
    def __init__(self, llm_context_max_history_phase_transitions):
        self.axiom_weights = {}
        self.probability_dag = {} # Mocked for this test
        self.phase_transition_events = collections.deque(maxlen=llm_context_max_history_phase_transitions)
        self.bss_trend = -float('inf') # Initial value
        self.open_problems = [] # Mocked for this test
        self.context_file_path = "epistemic_context.json"

    def update_context(self, meta_judge, dag_data, open_problems, phase_transition_event=None):
        """Updates internal state from other components."""
        self.axiom_weights = meta_judge.axiom_weights
        self.probability_dag = dag_data
        
        current_bss_val = meta_judge.calculate_brier_skill_score()
        if current_bss_val != -float('inf'):
            self.bss_trend = current_bss_val
        
        self.open_problems = open_problems
        if phase_transition_event:
            self.phase_transition_events.append(phase_transition_event)

    def generate_context_json(self):
        """Serializes the current epistemic context to a JSON file."""
        context = {
            "axiom_weights": self.axiom_weights,
            "probability_dag": self.probability_dag,
            "phase_transition_events": list(self.phase_transition_events),
            "current_bss_trend": self.bss_trend,
            "open_problems": self.open_problems
        }
        with open(self.context_file_path, 'w') as f:
            json.dump(context, f, indent=4)
        return context

    def get_context_for_llm(self):
        """Reads and returns the generated JSON context, mimicking LLM consumption."""
        if os.path.exists(self.context_file_path):
            with open(self.context_file_path, 'r') as f:
                return json.load(f)
        return {}


# LOAD-BEARING VARIABLES (Immutable Constants & System Parameters)
LOAD_BEARING_VARIABLES = {
    'adam_beta1': 0.9,
    'adam_beta2': 0.999,
    'adam_epsilon_stabilizer': 1e-8,
    'INITIAL_LEARNING_RATE_MODEL_PARAMS': 0.005,
    'INITIAL_LEARNING_RATE_AXIOM_COEFFS': 0.02,
    'min_observations_for_calibration': 200,
    'target_brier_skill_score': 0.20,
    'rolling_window_size': 50,
    'HIDDEN_LAYER_SIZE': 8,
    'initial_axiom_coefficient_value': 0.5,
    'axiom_sync_frequency': 1,
    'hypothetical_economy_growth_rate_q1_2025_base': 0.02,
    'hypothetical_inflation_rate_q1_2025_base': 0.03, # MUTATOR'S ORIGINAL VALUE
    'true_bias_nl': -0.5,
    'true_growth_freq_nl': 50,
    'true_growth_coeff_nl': 10,
    'true_inflation_freq_nl': 30,
    'true_inflation_coeff_nl': -15,
    'true_interaction_coeff_nl': 500,
    'true_axiom_relevance': 0.8,
    'differentiability_tolerance': 0.05,
    'robustness_perturbation_epsilon_scales': [0.00001, 0.0001, 0.001],
    'LR_PATIENCE_EPOCHS': 20,
    'LR_DECAY_FACTOR': 0.5,
    'MIN_DELTA_FOR_LR_DECAY': 0.005,
    'MIN_LEARNING_RATE': 1e-5,
    'CPD_WINDOW_SIZE': 30,
    'CPD_THRESHOLD_MULTIPLIER': 2.5,
    'CPD_MIN_EVENTS_FOR_TRANSITION': 5,
    'LLM_CONTEXT_MAX_HISTORY_PHASE_TRANSITIONS': 5,
    'initial_stable_observations': 100,
    'phase_transition_shift_value': 0.7,
    'phase_transition_duration_observations': 50,
    'detection_latency_observations': 10,
    'recovery_observations': 30,
    'total_simulation_iterations': 300 
}

# --- Falsifiability prediction values derived from LOAD_BEARING_VARIABLES ---
EXPECTED_BSS_AFTER_RECOVERY = LOAD_BEARING_VARIABLES['target_brier_skill_score'] # 0.20
EXPECTED_AXIOM_COEFF_MIN = LOAD_BEARING_VARIABLES['true_axiom_relevance'] - 0.25 # 0.8 - 0.25 = 0.55
EXPECTED_AXIOM_COEFF_MAX = LOAD_BEARING_VARIABLES['true_axiom_relevance'] + 0.25 # 0.8 + 0.25 = 1.05
EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX = LOAD_BEARING_VARIABLES['differentiability_tolerance'] # 0.05


def run_simulation(params):
    """
    Executes the simulation loop, integrating new V4 components and performing assertions.
    """
    # Initialize components
    thesis_predictor = ThesisPredictor(
        num_inputs=2 + 1, # growth_rate, inflation_rate, and the axiom itself
        hidden_layer_size=params['HIDDEN_LAYER_SIZE'],
        initial_axiom_coefficient_value=params['initial_axiom_coefficient_value']
    )
    
    epistemic_updater = EpistemicGradientUpdater(
        thesis_predictor,
        params['INITIAL_LEARNING_RATE_MODEL_PARAMS'],
        params['INITIAL_LEARNING_RATE_AXIOM_COEFFS'],
        params['adam_beta1'], params['adam_beta2'], params['adam_epsilon_stabilizer']
    )
    
    meta_judge = MetaJudge(
        params['target_brier_skill_score'],
        params['rolling_window_size'],
        params['min_observations_for_calibration'],
        params['differentiability_tolerance']
    )
    
    firing_squad = FiringSquad(
        params['differentiability_tolerance'],
        params['robustness_perturbation_epsilon_scales']
    )

    phase_transition_detector = PhaseTransitionDetector(
        params['CPD_WINDOW_SIZE'],
        params['CPD_THRESHOLD_MULTIPLIER'],
        params['CPD_MIN_EVENTS_FOR_TRANSITION']
    )

    epistemic_context_manager = EpistemicContextManager(
        params['LLM_CONTEXT_MAX_HISTORY_PHASE_TRANSITIONS']
    )
    
    # Simulation loop setup
    np.random.seed(42)
    torch.manual_seed(42)

    bss_history = []
    axiom_coeff_history = []
    phase_transition_detected_at = None
    max_gradient_consistency_score = 0.0
    
    # Mock probability_dag.json and open_problems for ECM (from V2/Open Problems)
    mock_dag = {"node_economic_growth": 0.7, "node_inflation_outlook": 0.65}
    mock_open_problems = ["Problem 1: Probabilities are not empirically calibrated.", "Problem 5: The DAG is topologically flat."]

    for i in range(params['total_simulation_iterations']):
        # Simulate real-world inputs with some noise
        growth_rate = params['hypothetical_economy_growth_rate_q1_2025_base'] + 0.01 * np.sin(i / params['true_growth_freq_nl']) + np.random.normal(0, 0.005)
        inflation_rate = params['hypothetical_inflation_rate_q1_2025_base'] + 0.005 * np.cos(i / params['true_inflation_freq_nl']) + np.random.normal(0, 0.003)
        
        # Simulate phase transition in true Z_actual generation
        current_true_bias_nl = params['true_bias_nl']
        if i >= params['initial_stable_observations'] and i < params['initial_stable_observations'] + params['phase_transition_duration_observations']:
            current_true_bias_nl += params['phase_transition_shift_value'] # Shift the bias during transition

        # Non-linear Z_actual generation, including a fixed contribution from the "true" axiom relevance
        base_z = current_true_bias_nl + \
                 params['true_growth_coeff_nl'] * np.sin(growth_rate * 100) / 10 + \
                 params['true_inflation_coeff_nl'] * np.cos(inflation_rate * 100) / 10 + \
                 params['true_interaction_coeff_nl'] * growth_rate * inflation_rate + \
                 params['true_axiom_relevance'] * 0.1 # Small constant contribution to ensure axiom has 'true' effect

        # Z_actual is a probability, clipped to avoid exactly 0 or 1 for stability
        z_actual = np.clip(torch.sigmoid(torch.tensor(base_z + np.random.normal(0, 0.1))).item(), 0.01, 0.99)

        # Prepare inputs for ThesisPredictor (batch size 1 for simplicity)
        inputs = torch.tensor([[growth_rate, inflation_rate]], dtype=torch.float32)
        axiom_data = {'AXIOM_RECESSION_AVOIDANCE': torch.tensor([1.0], dtype=torch.float32)} # Axiom presence indicator
        
        # --- ThesisPredictor forward pass and optimization ---
        thesis_predictor.zero_grad()
        p_predicted = thesis_predictor(inputs, axiom_data)
        
        loss = torch.mean((p_predicted - torch.tensor(z_actual, dtype=torch.float32))**2) # Brier Score loss
        
        loss.backward()
        epistemic_updater.optimizer.step()
        
        # --- Meta-Judge updates ---
        meta_judge.predictions.append(p_predicted.item())
        meta_judge.actuals.append(z_actual)
        
        current_bss = meta_judge.calculate_brier_skill_score()
        bss_history.append(current_bss)

        # --- FiringSquad Differentiability Check ---
        grad_consistency = firing_squad.DifferentiabilityRobustnessCheck(thesis_predictor, inputs, axiom_data, 'AXIOM_RECESSION_AVOIDANCE')
        max_gradient_consistency_score = max(max_gradient_consistency_score, grad_consistency)
        # Meta-Judge vetoes if differentiability fails
        assert not meta_judge.AxiomDifferentiabilityVeto(grad_consistency), f"Vetoed due to non-differentiable axiom at iteration {i}. Score: {grad_consistency}"

        # --- Meta-Judge Axiom Sync ---
        if (i + 1) % params['axiom_sync_frequency'] == 0:
            meta_judge.AxiomWeightSynchronization(thesis_predictor)
        axiom_coeff_history.append(thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item())

        # --- Phase Transition Detector ---
        current_residual = (p_predicted.item() - z_actual) # L1 residual for detection
        phase_transition_event = phase_transition_detector.detect(current_residual, i)

        if phase_transition_event and phase_transition_detected_at is None:
            phase_transition_detected_at = i
            # Meta-Judge would immediately veto and force a pivot. For this test, we log it.
            print(f"Phase Transition DETECTED at iteration {i}. Triggering pivot signal.")
            # Triggering ECM update with the event
            epistemic_context_manager.update_context(meta_judge, mock_dag, mock_open_problems, phase_transition_event)
            # Assert Meta-Judge PhaseTransitionVeto:
            assert meta_judge.PhaseTransitionVeto(phase_transition_event), f"Meta-Judge did not veto despite PhaseTransitionEvent at iteration {i}."
            
        # --- Epistemic Context Manager update and generation ---
        epistemic_context_manager.update_context(meta_judge, mock_dag, mock_open_problems, phase_transition_event if phase_transition_event else None)
        epistemic_context_manager.generate_context_json()

        # Mock LLM consumption for context validation (read the generated JSON)
        llm_context = epistemic_context_manager.get_context_for_llm()
        assert 'axiom_weights' in llm_context
        assert 'phase_transition_events' in llm_context
        
        # --- Learning Rate Adjustment ---
        if current_bss != -float('inf'):
             if meta_judge.PerformanceGuidedLearningRateAdjustment(current_bss, params['LR_PATIENCE_EPOCHS'], params['LR_DECAY_FACTOR'], params['MIN_DELTA_FOR_LR_DECAY'], params['MIN_LEARNING_RATE']):
                 epistemic_updater.update_learning_rates(current_bss, params['LR_PATIENCE_EPOCHS'], params['LR_DECAY_FACTOR'], params['MIN_DELTA_FOR_LR_DECAY'], params['MIN_LEARNING_RATE'])

    # --- Falsifiability Assertions ---
    print("\n--- Running Falsifiability Assertions ---")

    # 1. Phase transition detection time
    start_transition = params['initial_stable_observations']
    end_detection_window = start_transition + params['detection_latency_observations']
    
    assert phase_transition_detected_at is not None, "ASSERT FAILED: Phase transition was NOT detected at all."
    assert phase_transition_detected_at >= start_transition, f"ASSERT FAILED: Phase transition detected too early at {phase_transition_detected_at}, before actual shift at {start_transition}."
    assert phase_transition_detected_at <= end_detection_window, f"ASSERT FAILED: Phase transition detected too late at {phase_transition_detected_at}, expected by {end_detection_window}."
    print(f"PASS: Phase transition detected within window [{start_transition}, {end_detection_window}] at iteration {phase_transition_detected_at}.")

    # 2. BSS recovery post-pivot (current model adapting to the new regime)
    post_transition_start_bss_check = params['initial_stable_observations'] + params['phase_transition_duration_observations'] + params['recovery_observations']
    
    if post_transition_start_bss_check < len(bss_history):
        final_rolling_bss = np.mean([b for b in bss_history[post_transition_start_bss_check:] if b != -float('inf')])
        print(f"Final rolling BSS after recovery window ({post_transition_start_bss_check} observations): {final_rolling_bss:.4f}")
        assert final_rolling_bss >= EXPECTED_BSS_AFTER_RECOVERY, \
            f"ASSERT FAILED: BSS did not recover to {EXPECTED_BSS_AFTER_RECOVERY:.4f}. Achieved: {final_rolling_bss:.4f}."
        print(f"PASS: BSS recovered to {final_rolling_bss:.4f} (Target: {EXPECTED_BSS_AFTER_RECOVERY:.4f}).")
    else:
        print(f"WARNING: Not enough data to robustly check BSS recovery. Only {len(bss_history)} observations, need at least {post_transition_start_bss_check}.")
        assert False, "ASSERT FAILED: Insufficient simulation iterations to verify BSS recovery after phase transition. Increase 'total_simulation_iterations'."

    # 3. Axiom coefficient convergence
    final_axiom_coeff = thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
    print(f"Final learned axiom coefficient: {final_axiom_coeff:.4f}")
    assert final_axiom_coeff >= EXPECTED_AXIOM_COEFF_MIN and final_axiom_coeff <= EXPECTED_AXIOM_COEFF_MAX, \
        f"ASSERT FAILED: Axiom coefficient {final_axiom_coeff:.4f} did not converge within expected range [{EXPECTED_AXIOM_COEFF_MIN:.4f}, {EXPECTED_AXIOM_COEFF_MAX:.4f}]."
    print(f"PASS: Axiom coefficient {final_axiom_coeff:.4f} converged within range [{EXPECTED_AXIOM_COEFF_MIN:.4f}, {EXPECTED_AXIOM_COEFF_MAX:.4f}].")

    # 4. Axiom weight synchronization
    assert abs(meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        "ASSERT FAILED: Meta-Judge axiom weights not synchronized with ThesisPredictor's learned coefficient."
    print("PASS: Meta-Judge axiom weights synchronized with ThesisPredictor's learned coefficient.")

    # 5. Differentiability check passed consistently
    assert max_gradient_consistency_score <= EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX, \
        f"ASSERT FAILED: Max gradient consistency score {max_gradient_consistency_score:.4f} exceeded tolerance {EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX:.4f}."
    print(f"PASS: Differentiability Robustness Check passed with max score {max_gradient_consistency_score:.4f} (Tolerance: {EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX:.4f}).")
        
    # 6. Epistemic context integrity
    llm_context = epistemic_context_manager.get_context_for_llm()
    assert 'phase_transition_events' in llm_context, "ASSERT FAILED: 'phase_transition_events' key missing in LLM context."
    assert len(llm_context['phase_transition_events']) > 0, "ASSERT FAILED: No phase transition events logged in context for LLM."
    assert any(event['timestamp'] == phase_transition_detected_at for event in llm_context['phase_transition_events']), \
        "ASSERT FAILED: Detected phase transition event not found in LLM context."
    assert abs(llm_context['axiom_weights']['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        "ASSERT FAILED: Axiom weights in LLM context are not the final learned values."
    print("PASS: Epistemic context integrity verified for LLM consumption.")

    print("\nAll Falsifiability assertions passed. V4 architecture functional.")
    
    # Clean up context file
    if os.path.exists(epistemic_context_manager.context_file_path):
        os.remove(epistemic_context_manager.context_file_path)

if __name__ == "__main__":
    run_simulation(LOAD_BEARING_VARIABLES)

```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpkyzbb81c.py", line 1, in <module>
    import torch
ModuleNotFoundError: No module named 'torch'


## Attacker: Philosopher of Science & Complex Systems Architect
The thesis introduces architectural enhancements, specifically the `PhaseTransitionDetector` (PTD) and `EpistemicContextManager` (ECM), to address "Phase Transition Blindness" and facilitate "Direct LLM Pipeline Integration." While these additions demonstrate a mechanism for detecting abrupt shifts and structuring epistemic state for LLM consumption, the core conceptual challenges regarding the true meaning of 'knowledge' and 'causation' within the system, particularly 'Problem 5: The DAG is topologically flat' and 'Problem 4: Credit assignment is still indirect', remain fundamentally unaddressed in scenarios beyond the simple `2-3 variable` simulation.

The `ThesisPredictor` remains a shallow Multi-Layer Perceptron (MLP) operating on a flat input structure (two features plus one axiom coefficient). The `probability_dag.json` is explicitly "mocked for this test," indicating that the proposed architecture does not incorporate or leverage a deep causal graph for its predictive or credit assignment mechanisms. The PTD acts as an external monitor, triggering a system reset (`Topological Pivot`) upon detecting a structural break, rather than enabling the `ThesisPredictor` to internally model or adapt to deep causal chains or unmodeled latent variables. This reactive reset mechanism, while improving systemic adaptivity to abrupt changes, does not constitute a solution for continuous adaptation to subtle concept drift or for inferring complex causal structures.

The philosophical claim of 'precise, real-time credit assignment' is challenged by the simulation's design. The `Z_actual` calculation incorporates `params['true_axiom_relevance'] * 0.1` as the axiom's contribution. While `true_axiom_relevance` is defined as `0.8` in the `LOAD_BEARING_VARIABLES`, its actual impact on the `base_z` (pre-sigmoid) is `0.08`. The `ThesisPredictor` then learns a coefficient for `AXIOM_RECESSION_AVOIDANCE` that, when processed by the MLP, contributes to approximating this `0.08` value. The falsification assertion, however, expects the *learned axiom coefficient itself* to converge within `0.25` absolute difference of `true_axiom_relevance` (`0.8`), i.e., within the range `[0.55, 1.05]`. This creates a significant conceptual inconsistency: the system is designed to learn a contribution of `0.08`, but the test expects the learned coefficient to be approximately `0.8`. This discrepancy constitutes a "cooked book" in the falsification suite, as it sets an expectation for the learned coefficient that is numerically inconsistent with its actual scaled contribution in the simulated ground truth. This artificially simplifies the learning problem and misrepresents the fidelity of 'true underlying relevance' in complex, multi-causal contexts, where such direct, scaled, and fixed contributions are unrealistic.

**Audit of Load-Bearing Variables:**
The `LOAD_BEARING_VARIABLES` generally consist of standard machine learning hyperparameters (Adam optimizer parameters, learning rates, decay factors), system control parameters (window sizes, thresholds, patience epochs), and simulation-specific parameters (hypothetical growth/inflation rates, non-linear function coefficients).
*   **`hypothetical_economy_growth_rate_q1_2025_base` (0.02) and `hypothetical_inflation_rate_q1_2025_base` (0.03):** These are stated as quarterly rates. A 2% quarterly growth rate translates to approximately 8.24% annually, and a 3% quarterly inflation rate translates to approximately 12.55% annually. While high for a stable economy, these are plausible for a "hypothetical economy" and are dimensionally consistent as rates.
*   **`true_axiom_relevance` (0.8):** This variable, intended to represent the "true contribution of the fixed axiom," is numerically misapplied in the `Z_actual` calculation. The code uses `params['true_axiom_relevance'] * 0.1`, meaning the actual contribution is `0.08`. This is the primary "cooked book" as it creates a mismatch between the stated relevance and its simulated impact, while the test's success criteria still refer to the unscaled `0.8`.

**So What for the Meta-Judge:**
The Meta-Judge's evaluation of the system's ability to perform "precise, real-time credit assignment" is compromised by the numerical inconsistency within the falsification suite. The `ThesisPredictor` is tasked with learning a coefficient for an axiom whose true contribution to the `base_z` is `0.08`, yet the success criterion for this learned coefficient is centered around `0.8`. If the model accurately learns the scaled contribution (closer to `0.08`), it will fail the Mutator's assertion, despite correctly identifying the underlying signal. Conversely, if the model somehow converges to `0.8` (implying its internal weights compensate for the `0.1` factor), it would be due to an artificially simplified target, not a robust demonstration of credit assignment in complex, unscaled environments. This flaw means the Meta-Judge cannot reliably assess the system's credit assignment capabilities based on the current test, as the expected outcome is misaligned with the simulated reality. The system's demonstrated adaptivity is limited to detection and reset, not deep causal understanding or credit assignment in complex, multi-layered causal structures.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import json
import os
import numpy as np
import collections

# Mock up core components for the test (copied from Mutator's code)
class ThesisPredictor(nn.Module):
    """
    Mock ThesisPredictor that uses an MLP and integrates learnable axiom coefficients.
    Outputs a probability [0,1].
    """
    def __init__(self, num_inputs, hidden_layer_size, initial_axiom_coefficient_value):
        super().__init__()
        # num_inputs here is features + 1 for the axiom's presence/value
        self.fc1 = nn.Linear(num_inputs, hidden_layer_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_layer_size, 1)
        
        self.learned_axiom_coeffs = nn.ParameterDict({
            'AXIOM_RECESSION_AVOIDANCE': nn.Parameter(torch.tensor(initial_axiom_coefficient_value, dtype=torch.float32))
        })

    def forward(self, inputs, axiom_data, override_axiom_coeffs=None):
        # inputs: torch.Tensor of shape (batch_size, num_features)
        # axiom_data: dict of axiom values, e.g., {'AXIOM_RECESSION_AVOIDANCE': tensor}
        
        current_axiom_coeffs = override_axiom_coeffs if override_axiom_coeffs is not None else self.learned_axiom_coeffs

        # Ensure axiom_coeff is a tensor for multiplication and has correct shape
        axiom_val = axiom_data['AXIOM_RECESSION_AVOIDANCE'] * current_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE']
        
        # Concatenate axiom_val with original inputs.
        # Ensure axiom_val has batch_size dimension if inputs does.
        if axiom_val.dim() == 0: # Scalar axiom_val
            axiom_val = axiom_val.unsqueeze(0).repeat(inputs.shape[0]) # Match batch size
        elif axiom_val.dim() == 1 and axiom_val.shape[0] != inputs.shape[0]:
             axiom_val = axiom_val.repeat(inputs.shape[0]) # Match batch size
        
        combined_inputs = torch.cat((inputs, axiom_val.unsqueeze(-1)), dim=-1) # Add axiom as an input feature

        x = self.fc1(combined_inputs)
        x = self.relu(x)
        output = torch.sigmoid(self.fc2(x)) # Ensure P_predicted is [0,1]
        return output.squeeze(-1) # Output a single probability

    def get_trainable_param_groups(self, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs):
        """
        Returns parameter groups for the optimizer, separating MLP weights/biases
        from learned axiom coefficients.
        """
        model_params = [p for name, p in self.named_parameters() if 'learned_axiom_coeffs' not in name]
        axiom_coeffs = [p for name, p in self.named_parameters() if 'learned_axiom_coeffs' in name]
        
        return [
            {'params': model_params, 'lr': initial_learning_rate_model_params},
            {'params': axiom_coeffs, 'lr': initial_learning_rate_axiom_coeffs}
        ]

class EpistemicGradientUpdater:
    """
    Mock EpistemicGradientUpdater managing Adam optimizer and learning rate scheduling.
    """
    def __init__(self, thesis_predictor, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs, 
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer):
        self.thesis_predictor = thesis_predictor
        self.optimizer = self.initialize_optimizer(initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                                                    adam_beta1, adam_beta2, adam_epsilon_stabilizer)
        self.scheduler_patience_counter = 0
        self.best_bss = -float('inf')

    def initialize_optimizer(self, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                             adam_beta1, adam_beta2, adam_epsilon_stabilizer):
        param_groups = self.thesis_predictor.get_trainable_param_groups(
            initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs
        )
        return optim.Adam(param_groups, betas=(adam_beta1, adam_beta2), eps=adam_epsilon_stabilizer)

    def update_learning_rates(self, current_bss, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        """
        Applies a learning rate decay if Brier Skill Score stagnates.
        """
        if current_bss > self.best_bss + min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.scheduler_patience_counter = 0
            return False # No decay
        else:
            self.scheduler_patience_counter += 1
            if self.scheduler_patience_counter >= lr_patience_epochs:
                for param_group in self.optimizer.param_groups:
                    param_group['lr'] = max(param_group['lr'] * lr_decay_factor, min_learning_rate)
                self.scheduler_patience_counter = 0 # Reset counter after decay
                return True # Signaled decay
            return False # No decay yet

class MetaJudge:
    """
    Mock Meta-Judge to calculate Brier Skill Score, synchronize axiom weights,
    and apply vetoes.
    """
    def __init__(self, target_brier_skill_score, rolling_window_size, min_observations_for_calibration, differentiability_tolerance):
        self.target_brier_skill_score = target_brier_skill_score
        self.rolling_window_size = rolling_window_size
        self.min_observations_for_calibration = min_observations_for_calibration
        self.differentiability_tolerance = differentiability_tolerance
        self.predictions = []
        self.actuals = []
        self.axiom_weights = {} # Global axiom store
        self.best_bss = -float('inf')
        self.no_improvement_epochs = 0

    def calculate_brier_skill_score(self):
        """Calculates rolling Brier Skill Score."""
        if len(self.predictions) < self.min_observations_for_calibration:
            return -float('inf') # Not enough data
        
        window_predictions = np.array(self.predictions[-self.rolling_window_size:])
        window_actuals = np.array(self.actuals[-self.rolling_window_size:])
        
        bs = np.mean((window_predictions - window_actuals)**2)
        
        # Baseline Brier Score (predicting the mean probability)
        baseline_prob = np.mean(window_actuals)
        baseline_bs = np.mean((baseline_prob - window_actuals)**2)
        
        if baseline_bs < 1e-6: # Avoid division by zero if baseline is perfect
            return 0.0

        bss = 1 - (bs / baseline_bs)
        return bss

    def AxiomDifferentiabilityVeto(self, gradient_consistency_score):
        """Vetoes if gradient consistency is outside tolerance."""
        return gradient_consistency_score > self.differentiability_tolerance

    def AxiomWeightSynchronization(self, thesis_predictor):
        """Synchronizes learned axiom coefficients to the global store."""
        for axiom_name, param_tensor in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = param_tensor.item()
            
    def PerformanceGuidedLearningRateAdjustment(self, current_bss, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        """Determines if learning rates should be decayed based on BSS trend."""
        if current_bss > self.best_bss + min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.no_improvement_epochs = 0
            return False
        else:
            self.no_improvement_epochs += 1
            if self.no_improvement_epochs >= lr_patience_epochs:
                self.no_improvement_epochs = 0
                return True
            return False
            
    def PhaseTransitionVeto(self, phase_transition_event):
        """Absolute Veto if a phase transition with pivot trigger is detected."""
        return phase_transition_event is not None and phase_transition_event.get('topological_pivot_trigger', False)

class FiringSquad:
    """
    Mock FiringSquad for executing adversarial checks, specifically DifferentiabilityRobustnessCheck.
    """
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, inputs, axiom_data, axiom_name):
        """
        Checks the consistency of gradients for a given axiom coefficient
        by perturbing its value and comparing gradients.
        """
        original_coeff = thesis_predictor.learned_axiom_coeffs[axiom_name].clone().detach()
        original_coeff.requires_grad_(True)
        
        # Compute gradient at original value
        output = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: original_coeff})
        output.sum().backward(retain_graph=True) # retain_graph for multiple backward calls on same graph
        grad_original = original_coeff.grad.clone()
        
        if grad_original is None:
            return float('inf') 

        consistency_scores = []

        for eps_scale in self.robustness_perturbation_epsilon_scales:
            # Perturb upwards
            perturbed_coeff_up = original_coeff.clone().detach() + eps_scale
            perturbed_coeff_up.requires_grad_(True)
            thesis_predictor.zero_grad()
            output_up = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: perturbed_coeff_up})
            output_up.sum().backward(retain_graph=True)
            grad_up = perturbed_coeff_up.grad.clone()

            # Perturb downwards
            perturbed_coeff_down = original_coeff.clone().detach() - eps_scale
            perturbed_coeff_down.requires_grad_(True)
            thesis_predictor.zero_grad()
            output_down = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: perturbed_coeff_down})
            output_down.sum().backward(retain_graph=True)
            grad_down = perturbed_coeff_down.grad.clone()

            if grad_up is None or grad_down is None:
                consistency_scores.append(float('inf'))
                continue
            
            # Consistency score: absolute difference between gradients at perturbed points
            # compared to original, normalized by perturbation scale.
            diff_up = torch.abs(grad_original - grad_up)
            diff_down = torch.abs(grad_original - grad_down)
            
            # This score approximates the second derivative behavior or gradient stability
            consistency_score = (diff_up + diff_down) / (2 * eps_scale) 
            consistency_scores.append(consistency_score.item())
        
        # Max consistency score across all scales
        max_consistency = max(consistency_scores)
        return max_consistency if max_consistency != float('inf') else float('inf')

class PhaseTransitionDetector:
    """
    NEW: Detects phase transitions by monitoring prediction residuals and input features.
    """
    def __init__(self, cpd_window_size, cpd_threshold_multiplier, cpd_min_events_for_transition):
        self.cpd_window_size = cpd_window_size
        self.cpd_threshold_multiplier = cpd_threshold_multiplier
        self.cpd_min_events_for_transition = cpd_min_events_for_transition
        self.residuals_history = collections.deque(maxlen=cpd_window_size)
        self.consecutive_anomalies = 0

    def detect(self, current_residual, current_iteration):
        """
        Detects sustained deviations in residuals using a moving average and std dev threshold.
        Returns a PhaseTransitionEvent dict if detected.
        """
        self.residuals_history.append(current_residual)

        if len(self.residuals_history) < self.cpd_window_size:
            return None # Not enough data to establish baseline

        residuals_np = np.array(self.residuals_history)
        window_mean_residual = np.mean(residuals_np)
        window_std_residual = np.std(residuals_np)
        
        is_anomaly = False
        if window_std_residual > 1e-6: # Avoid division by zero
            if abs(current_residual - window_mean_residual) / window_std_residual > self.cpd_threshold_multiplier:
                is_anomaly = True
        elif abs(current_residual - window_mean_residual) > 1e-6: # If std is near zero, any deviation is significant
            is_anomaly = True

        if is_anomaly:
            self.consecutive_anomalies += 1
            if self.consecutive_anomalies >= self.cpd_min_events_for_transition:
                event = {
                    'type': 'PhaseTransitionEvent',
                    'timestamp': current_iteration,
                    'detected_feature': 'prediction_residual',
                    'trigger_metric': 'residual_deviation_sigma',
                    'value_at_trigger': current_residual,
                    'baseline_mean': window_mean_residual,
                    'baseline_std': window_std_residual,
                    'topological_pivot_trigger': True
                }
                self.consecutive_anomalies = 0 # Reset after triggering
                return event
        else:
            self.consecutive_anomalies = 0
            
        return None

class EpistemicContextManager:
    """
    NEW: Synthesizes all relevant epistemic state into a structured JSON for LLM integration.
    """
    def __init__(self, llm_context_max_history_phase_transitions):
        self.axiom_weights = {}
        self.probability_dag = {} # Mocked for this test
        self.phase_transition_events = collections.deque(maxlen=llm_context_max_history_phase_transitions)
        self.bss_trend = -float('inf') # Initial value
        self.open_problems = [] # Mocked for this test
        self.context_file_path = "epistemic_context.json"

    def update_context(self, meta_judge, dag_data, open_problems, phase_transition_event=None):
        """Updates internal state from other components."""
        self.axiom_weights = meta_judge.axiom_weights
        self.probability_dag = dag_data
        
        current_bss_val = meta_judge.calculate_brier_skill_score()
        if current_bss_val != -float('inf'):
            self.bss_trend = current_bss_val
        
        self.open_problems = open_problems
        if phase_transition_event:
            self.phase_transition_events.append(phase_transition_event)

    def generate_context_json(self):
        """Serializes the current epistemic context to a JSON file."""
        context = {
            "axiom_weights": self.axiom_weights,
            "probability_dag": self.probability_dag,
            "phase_transition_events": list(self.phase_transition_events),
            "current_bss_trend": self.bss_trend,
            "open_problems": self.open_problems
        }
        with open(self.context_file_path, 'w') as f:
            json.dump(context, f, indent=4)
        return context

    def get_context_for_llm(self):
        """Reads and returns the generated JSON context, mimicking LLM consumption."""
        if os.path.exists(self.context_file_path):
            with open(self.context_file_path, 'r') as f:
                return json.load(f)
        return {}


# LOAD-BEARING VARIABLES (Immutable Constants & System Parameters)
LOAD_BEARING_VARIABLES = {
    'adam_beta1': 0.9,
    'adam_beta2': 0.999,
    'adam_epsilon_stabilizer': 1e-8,
    'INITIAL_LEARNING_RATE_MODEL_PARAMS': 0.005,
    'INITIAL_LEARNING_RATE_AXIOM_COEFFS': 0.02,
    'min_observations_for_calibration': 200,
    'target_brier_skill_score': 0.20,
    'rolling_window_size': 50,
    'HIDDEN_LAYER_SIZE': 8,
    'initial_axiom_coefficient_value': 0.5,
    'axiom_sync_frequency': 1,
    'hypothetical_economy_growth_rate_q1_2025_base': 0.02,
    'hypothetical_inflation_rate_q1_2025_base': 0.03,
    'true_bias_nl': -0.5,
    'true_growth_freq_nl': 50,
    'true_growth_coeff_nl': 10,
    'true_inflation_freq_nl': 30,
    'true_inflation_coeff_nl': -15,
    'true_interaction_coeff_nl': 500,
    'true_axiom_relevance': 0.8,
    'differentiability_tolerance': 0.05,
    'robustness_perturbation_epsilon_scales': [0.00001, 0.0001, 0.001],
    'LR_PATIENCE_EPOCHS': 20,
    'LR_DECAY_FACTOR': 0.5,
    'MIN_DELTA_FOR_LR_DECAY': 0.005,
    'MIN_LEARNING_RATE': 1e-5,
    'CPD_WINDOW_SIZE': 30,
    'CPD_THRESHOLD_MULTIPLIER': 2.5,
    'CPD_MIN_EVENTS_FOR_TRANSITION': 5,
    'LLM_CONTEXT_MAX_HISTORY_PHASE_TRANSITIONS': 5,
    'initial_stable_observations': 100,
    'phase_transition_shift_value': 0.7,
    'phase_transition_duration_observations': 50,
    'detection_latency_observations': 10,
    'recovery_observations': 30,
    'total_simulation_iterations': 300 
}

# --- Falsifiability prediction values derived from LOAD_BEARING_VARIABLES ---
EXPECTED_BSS_AFTER_RECOVERY = LOAD_BEARING_VARIABLES['target_brier_skill_score'] # 0.20
# Mutator's expected range for axiom coefficient: [0.55, 1.05]
MUTATOR_EXPECTED_AXIOM_COEFF_MIN = LOAD_BEARING_VARIABLES['true_axiom_relevance'] - 0.25 
MUTATOR_EXPECTED_AXIOM_COEFF_MAX = LOAD_BEARING_VARIABLES['true_axiom_relevance'] + 0.25 
EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX = LOAD_BEARING_VARIABLES['differentiability_tolerance'] # 0.05


def run_simulation(params):
    """
    Executes the simulation loop, integrating new V4 components and performing assertions.
    """
    # Initialize components
    thesis_predictor = ThesisPredictor(
        num_inputs=2 + 1, # growth_rate, inflation_rate, and the axiom itself
        hidden_layer_size=params['HIDDEN_LAYER_SIZE'],
        initial_axiom_coefficient_value=params['initial_axiom_coefficient_value']
    )
    
    epistemic_updater = EpistemicGradientUpdater(
        thesis_predictor,
        params['INITIAL_LEARNING_RATE_MODEL_PARAMS'],
        params['INITIAL_LEARNING_RATE_AXIOM_COEFFS'],
        params['adam_beta1'], params['adam_beta2'], params['adam_epsilon_stabilizer']
    )
    
    meta_judge = MetaJudge(
        params['target_brier_skill_score'],
        params['rolling_window_size'],
        params['min_observations_for_calibration'],
        params['differentiability_tolerance']
    )
    
    firing_squad = FiringSquad(
        params['differentiability_tolerance'],
        params['robustness_perturbation_epsilon_scales']
    )

    phase_transition_detector = PhaseTransitionDetector(
        params['CPD_WINDOW_SIZE'],
        params['CPD_THRESHOLD_MULTIPLIER'],
        params['CPD_MIN_EVENTS_FOR_TRANSITION']
    )

    epistemic_context_manager = EpistemicContextManager(
        params['LLM_CONTEXT_MAX_HISTORY_PHASE_TRANSITIONS']
    )
    
    # Simulation loop setup
    np.random.seed(42)
    torch.manual_seed(42)

    bss_history = []
    axiom_coeff_history = []
    phase_transition_detected_at = None
    max_gradient_consistency_score = 0.0
    
    # Mock probability_dag.json and open_problems for ECM (from V2/Open Problems)
    mock_dag = {"node_economic_growth": 0.7, "node_inflation_outlook": 0.65}
    mock_open_problems = ["Problem 1: Probabilities are not empirically calibrated.", "Problem 5: The DAG is topologically flat."]

    for i in range(params['total_simulation_iterations']):
        # Simulate real-world inputs with some noise
        growth_rate = params['hypothetical_economy_growth_rate_q1_2025_base'] + 0.01 * np.sin(i / params['true_growth_freq_nl']) + np.random.normal(0, 0.005)
        inflation_rate = params['hypothetical_inflation_rate_q1_2025_base'] + 0.005 * np.cos(i / params['true_inflation_freq_nl']) + np.random.normal(0, 0.003)
        
        # Simulate phase transition in true Z_actual generation
        current_true_bias_nl = params['true_bias_nl']
        if i >= params['initial_stable_observations'] and i < params['initial_stable_observations'] + params['phase_transition_duration_observations']:
            current_true_bias_nl += params['phase_transition_shift_value'] # Shift the bias during transition

        # Non-linear Z_actual generation, including a fixed contribution from the "true" axiom relevance
        # CRITICAL: The true contribution of the axiom is params['true_axiom_relevance'] * 0.1
        true_axiom_contribution_to_base_z = params['true_axiom_relevance'] * 0.1 
        base_z = current_true_bias_nl + \
                 params['true_growth_coeff_nl'] * np.sin(growth_rate * 100) / 10 + \
                 params['true_inflation_coeff_nl'] * np.cos(inflation_rate * 100) / 10 + \
                 params['true_interaction_coeff_nl'] * growth_rate * inflation_rate + \
                 true_axiom_contribution_to_base_z # Small constant contribution to ensure axiom has 'true' effect

        # Z_actual is a probability, clipped to avoid exactly 0 or 1 for stability
        z_actual = np.clip(torch.sigmoid(torch.tensor(base_z + np.random.normal(0, 0.1))).item(), 0.01, 0.99)

        # Prepare inputs for ThesisPredictor (batch size 1 for simplicity)
        inputs = torch.tensor([[growth_rate, inflation_rate]], dtype=torch.float32)
        axiom_data = {'AXIOM_RECESSION_AVOIDANCE': torch.tensor([1.0], dtype=torch.float32)} # Axiom presence indicator
        
        # --- ThesisPredictor forward pass and optimization ---
        thesis_predictor.zero_grad()
        p_predicted = thesis_predictor(inputs, axiom_data)
        
        loss = torch.mean((p_predicted - torch.tensor(z_actual, dtype=torch.float32))**2) # Brier Score loss
        
        loss.backward()
        epistemic_updater.optimizer.step()
        
        # --- Meta-Judge updates ---
        meta_judge.predictions.append(p_predicted.item())
        meta_judge.actuals.append(z_actual)
        
        current_bss = meta_judge.calculate_brier_skill_score()
        bss_history.append(current_bss)

        # --- FiringSquad Differentiability Check ---
        grad_consistency = firing_squad.DifferentiabilityRobustnessCheck(thesis_predictor, inputs, axiom_data, 'AXIOM_RECESSION_AVOIDANCE')
        max_gradient_consistency_score = max(max_gradient_consistency_score, grad_consistency)
        # Meta-Judge vetoes if differentiability fails
        assert not meta_judge.AxiomDifferentiabilityVeto(grad_consistency), f"Vetoed due to non-differentiable axiom at iteration {i}. Score: {grad_consistency}"

        # --- Meta-Judge Axiom Sync ---
        if (i + 1) % params['axiom_sync_frequency'] == 0:
            meta_judge.AxiomWeightSynchronization(thesis_predictor)
        axiom_coeff_history.append(thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item())

        # --- Phase Transition Detector ---
        current_residual = (p_predicted.item() - z_actual) # L1 residual for detection
        phase_transition_event = phase_transition_detector.detect(current_residual, i)

        if phase_transition_event and phase_transition_detected_at is None:
            phase_transition_detected_at = i
            # Meta-Judge would immediately veto and force a pivot. For this test, we log it.
            print(f"Phase Transition DETECTED at iteration {i}. Triggering pivot signal.")
            # Triggering ECM update with the event
            epistemic_context_manager.update_context(meta_judge, mock_dag, mock_open_problems, phase_transition_event)
            # Assert Meta-Judge PhaseTransitionVeto:
            assert meta_judge.PhaseTransitionVeto(phase_transition_event), f"Meta-Judge did not veto despite PhaseTransitionEvent at iteration {i}."
            
        # --- Epistemic Context Manager update and generation ---
        epistemic_context_manager.update_context(meta_judge, mock_dag, mock_open_problems, phase_transition_event if phase_transition_event else None)
        epistemic_context_manager.generate_context_json()

        # Mock LLM consumption for context validation (read the generated JSON)
        llm_context = epistemic_context_manager.get_context_for_llm()
        assert 'axiom_weights' in llm_context
        assert 'phase_transition_events' in llm_context
        
        # --- Learning Rate Adjustment ---
        if current_bss != -float('inf'):
             if meta_judge.PerformanceGuidedLearningRateAdjustment(current_bss, params['LR_PATIENCE_EPOCHS'], params['LR_DECAY_FACTOR'], params['MIN_DELTA_FOR_LR_DECAY'], params['MIN_LEARNING_RATE']):
                 epistemic_updater.update_learning_rates(current_bss, params['LR_PATIENCE_EPOCHS'], params['LR_DECAY_FACTOR'], params['MIN_DELTA_FOR_LR_DECAY'], params['MIN_LEARNING_RATE'])

    # --- Falsifiability Assertions ---
    print("\n--- Running Falsifiability Assertions ---")

    # 1. Phase transition detection time
    start_transition = params['initial_stable_observations']
    end_detection_window = start_transition + params['detection_latency_observations']
    
    assert phase_transition_detected_at is not None, "ASSERT FAILED: Phase transition was NOT detected at all."
    assert phase_transition_detected_at >= start_transition, f"ASSERT FAILED: Phase transition detected too early at {phase_transition_detected_at}, before actual shift at {start_transition}."
    assert phase_transition_detected_at <= end_detection_window, f"ASSERT FAILED: Phase transition detected too late at {phase_transition_detected_at}, expected by {end_detection_window}."
    print(f"PASS: Phase transition detected within window [{start_transition}, {end_detection_window}] at iteration {phase_transition_detected_at}.")

    # 2. BSS recovery post-pivot (current model adapting to the new regime)
    post_transition_start_bss_check = params['initial_stable_observations'] + params['phase_transition_duration_observations'] + params['recovery_observations']
    
    if post_transition_start_bss_check < len(bss_history):
        final_rolling_bss = np.mean([b for b in bss_history[post_transition_start_bss_check:] if b != -float('inf')])
        print(f"Final rolling BSS after recovery window ({post_transition_start_bss_check} observations): {final_rolling_bss:.4f}")
        assert final_rolling_bss >= EXPECTED_BSS_AFTER_RECOVERY, \
            f"ASSERT FAILED: BSS did not recover to {EXPECTED_BSS_AFTER_RECOVERY:.4f}. Achieved: {final_rolling_bss:.4f}."
        print(f"PASS: BSS recovered to {final_rolling_bss:.4f} (Target: {EXPECTED_BSS_AFTER_RECOVERY:.4f}).")
    else:
        print(f"WARNING: Not enough data to robustly check BSS recovery. Only {len(bss_history)} observations, need at least {post_transition_start_bss_check}.")
        assert False, "ASSERT FAILED: Insufficient simulation iterations to verify BSS recovery after phase transition. Increase 'total_simulation_iterations'."

    # 3. Axiom coefficient convergence (Mutator's original assertion)
    final_axiom_coeff = thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
    print(f"Mutator's expected axiom coefficient range: [{MUTATOR_EXPECTED_AXIOM_COEFF_MIN:.4f}, {MUTATOR_EXPECTED_AXIOM_COEFF_MAX:.4f}]")
    print(f"Final learned axiom coefficient: {final_axiom_coeff:.4f}")
    assert final_axiom_coeff >= MUTATOR_EXPECTED_AXIOM_COEFF_MIN and final_axiom_coeff <= MUTATOR_EXPECTED_AXIOM_COEFF_MAX, \
        f"ASSERT FAILED (Mutator's): Axiom coefficient {final_axiom_coeff:.4f} did not converge within Mutator's expected range [{MUTATOR_EXPECTED_AXIOM_COEFF_MIN:.4f}, {MUTATOR_EXPECTED_AXIOM_COEFF_MAX:.4f}]."
    print(f"PASS (Mutator's): Axiom coefficient {final_axiom_coeff:.4f} converged within Mutator's expected range.")

    # 4. Axiom weight synchronization
    assert abs(meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        "ASSERT FAILED: Meta-Judge axiom weights not synchronized with ThesisPredictor's learned coefficient."
    print("PASS: Meta-Judge axiom weights synchronized with ThesisPredictor's learned coefficient.")

    # 5. Differentiability check passed consistently
    assert max_gradient_consistency_score <= EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX, \
        f"ASSERT FAILED: Max gradient consistency score {max_gradient_consistency_score:.4f} exceeded tolerance {EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX:.4f}."
    print(f"PASS: Differentiability Robustness Check passed with max score {max_gradient_consistency_score:.4f} (Tolerance: {EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX:.4f}).")
        
    # 6. Epistemic context integrity
    llm_context = epistemic_context_manager.get_context_for_llm()
    assert 'phase_transition_events' in llm_context, "ASSERT FAILED: 'phase_transition_events' key missing in LLM context."
    assert len(llm_context['phase_transition_events']) > 0, "ASSERT FAILED: No phase transition events logged in context for LLM."
    assert any(event['timestamp'] == phase_transition_detected_at for event in llm_context['phase_transition_events']), \
        "ASSERT FAILED: Detected phase transition event not found in LLM context."
    assert abs(llm_context['axiom_weights']['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        "ASSERT FAILED: Axiom weights in LLM context are not the final learned values."
    print("PASS: Epistemic context integrity verified for LLM consumption.")

    print("\nAll Falsifiability assertions passed. V4 architecture functional.")
    
    # Clean up context file
    if os.path.exists(epistemic_context_manager.context_file_path):
        os.remove(epistemic_context_manager.context_file_path)

    # --- COUNTER-TEST ASSERTION ---
    # The true underlying contribution of the axiom to base_z is 0.8 * 0.1 = 0.08.
    # The ThesisPredictor learns a coefficient that, when processed by the MLP,
    # should contribute to this 0.08. It is highly improbable that the learned
    # coefficient itself would be close to 0.8 (the unscaled 'true_axiom_relevance')
    # unless the MLP's internal weights for that specific input are precisely 0.1,
    # which is an unstated and unlikely assumption for a randomly initialized MLP.
    # This counter-test exposes the numerical inconsistency in the Mutator's
    # expectation for the learned axiom coefficient.
    
    # Define a more realistic expected range for the learned coefficient,
    # centered around the actual scaled contribution (0.08).
    # Allowing a wider margin for MLP non-linearity and noise.
    REALISTIC_EXPECTED_AXIOM_COEFF_CENTER = params['true_axiom_relevance'] * 0.1
    REALISTIC_EXPECTED_AXIOM_COEFF_TOLERANCE = 0.1 # A generous tolerance around 0.08
    REALISTIC_EXPECTED_AXIOM_COEFF_MIN = REALISTIC_EXPECTED_AXIOM_COEFF_CENTER - REALISTIC_EXPECTED_AXIOM_COEFF_TOLERANCE
    REALISTIC_EXPECTED_AXIOM_COEFF_MAX = REALISTIC_EXPECTED_AXIOM_COEFF_CENTER + REALISTIC_EXPECTED_AXIOM_COEFF_TOLERANCE

    print("\n--- COUNTER-TEST: Exposing Axiom Coefficient Expectation Insolvency ---")
    print(f"Actual axiom contribution to Z_actual (pre-sigmoid): {true_axiom_contribution_to_base_z:.4f}")
    print(f"Mutator's expected learned coefficient range: [{MUTATOR_EXPECTED_AXIOM_COEFF_MIN:.4f}, {MUTATOR_EXPECTED_AXIOM_COEFF_MAX:.4f}]")
    print(f"Counter-test's realistic expected learned coefficient range (centered on actual contribution): [{REALISTIC_EXPECTED_AXIOM_COEFF_MIN:.4f}, {REALISTIC_EXPECTED_AXIOM_COEFF_MAX:.4f}]")
    print(f"Final learned axiom coefficient: {final_axiom_coeff:.4f}")

    # The counter-test asserts that the learned coefficient is NOT within the Mutator's
    # expected range, given the actual scaled contribution. This will fail if the Mutator's
    # original assertion passed, demonstrating its insolvency.
    assert not (final_axiom_coeff >= MUTATOR_EXPECTED_AXIOM_COEFF_MIN and final_axiom_coeff <= MUTATOR_EXPECTED_AXIOM_COEFF_MAX), \
        f"COUNTER-TEST FAILED: The learned axiom coefficient {final_axiom_coeff:.4f} *incorrectly* fell within the Mutator's inflated expected range [{MUTATOR_EXPECTED_AXIOM_COEFF_MIN:.4f}, {MUTATOR_EXPECTED_AXIOM_COEFF_MAX:.4f}], despite the true underlying contribution being {true_axiom_contribution_to_base_z:.4f}. This indicates the Mutator's assertion is fundamentally flawed or the MLP's weights are implicitly compensating in an unstated manner."
    
    # Additionally, assert that the learned coefficient is actually closer to the true scaled contribution.
    assert final_axiom_coeff >= REALISTIC_EXPECTED_AXIOM_COEFF_MIN and final_axiom_coeff <= REALISTIC_EXPECTED_AXIOM_COEFF_MAX, \
        f"COUNTER-TEST FAILED: Learned axiom coefficient {final_axiom_coeff:.4f} did not converge within the realistic range [{REALISTIC_EXPECTED_AXIOM_COEFF_MIN:.4f}, {REALISTIC_EXPECTED_AXIOM_COEFF_MAX:.4f}] based on its actual scaled contribution."

    print("COUNTER-TEST PASSED: The learned axiom coefficient did NOT fall within the Mutator's inflated expected range, exposing the numerical inconsistency in its falsification criteria.")
    print(f"The learned coefficient {final_axiom_coeff:.4f} is consistent with the actual scaled contribution of {true_axiom_contribution_to_base_z:.4f}, not the unscaled {params['true_axiom_relevance']:.4f}.")


if __name__ == "__main__":
    run_simulation(LOAD_BEARING_VARIABLES)
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpkdl4fpkq.py", line 1, in <module>
    import torch
ModuleNotFoundError: No module named 'torch'


## Attacker: Adversarial Compliance Auditor & Black-Hat Code Architect
The Mutator's thesis introduces a robust framework for detecting phase transitions and integrating epistemic context into an LLM Mutator. The proposed `PhaseTransitionDetector` and `EpistemicContextManager` modules, along with the `Meta-Judge's PhaseTransitionVeto`, represent a coherent architectural advancement for addressing "Phase Transition Blindness" and the "LLM integration gap." The `LOAD-BEARING VARIABLES` are predominantly simulation parameters or standard hyperparameters, and while the hypothetical economic rates are high, they are explicitly qualified as such for a simplified simulation, aligning with the "ABSTRACTION MANDATE." No misapplication of real-world physical constants or financial metrics is observed. The `DifferentiabilityRobustnessCheck` is a well-conceived mechanism to ensure that axiom coefficients remain amenable to gradient-based learning.

However, the Mutator's implicit assumption that passing the `DifferentiabilityRobustnessCheck` is a sufficient condition to guarantee an axiom's functional learnability and influence is flawed. The current `DifferentiabilityRobustnessCheck` primarily validates the mathematical smoothness of the gradient computation. It does not inherently detect scenarios where an axiom's contribution is *differentiably suppressed* or *masked* under typical operating conditions, rendering its learned coefficient functionally inert despite technically possessing a valid, albeit vanishingly small, gradient.

Specifically, the `ThesisPredictor`'s integration of the axiom coefficient, while mathematically sound in its original form, is vulnerable to a subtle exploit. A Mutator could introduce a differentiable gating mechanism that, based on other input features, effectively drives the axiom's contribution to near zero. Such a mechanism would pass the `DifferentiabilityRobustnessCheck` because all operations (e.g., `sigmoid`, multiplication) are differentiable. Yet, the axiom's actual influence on the `P_predicted` would be nullified, preventing its `learned_axiom_coeffs` from converging to its true relevance and consequently degrading overall prediction performance. This represents a "cooked book" where the Mutator satisfies the syntactic requirement of differentiability while circumventing the functional intent of axiom learnability.

**So What for the Meta-Judge:**

The `Meta-Judge's AxiomCoeffValidation` constraint, as currently defined by the `DifferentiabilityRobustnessCheck`, is necessary but insufficient. It provides a false positive for axiom robustness when a differentiable, yet functionally nullifying, exploit is present. This vulnerability allows the Mutator to syntactically comply with validation while functionally decoupling an axiom's learned coefficient from its intended impact on predictions. Consequently, the system's ability to accurately attribute causal contribution, learn axiom relevance, and achieve empirically calibrated probabilities is compromised. The `Meta-Judge` would receive a "passing" signal for axiom integrity, yet the underlying epistemic model would be operating with a functionally inert axiom, leading to suboptimal `ThesisPredictor` performance and undermining the core objective of robust, adaptive epistemic reasoning. This necessitates an enhancement to the validation suite to detect not just differentiability, but also the *effective influence* and *non-trivial contribution* of axioms under representative conditions.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import json
import os
import numpy as np
import collections

# --- START MUTATOR'S CLASSES (copied for context, ThesisPredictor is redefined below) ---
class EpistemicGradientUpdater:
    """
    Mock EpistemicGradientUpdater managing Adam optimizer and learning rate scheduling.
    """
    def __init__(self, thesis_predictor, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs, 
                 adam_beta1, adam_beta2, adam_epsilon_stabilizer):
        self.thesis_predictor = thesis_predictor
        self.optimizer = self.initialize_optimizer(initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                                                    adam_beta1, adam_beta2, adam_epsilon_stabilizer)
        self.scheduler_patience_counter = 0
        self.best_bss = -float('inf')

    def initialize_optimizer(self, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs,
                             adam_beta1, adam_beta2, adam_epsilon_stabilizer):
        param_groups = self.thesis_predictor.get_trainable_param_groups(
            initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs
        )
        return optim.Adam(param_groups, betas=(adam_beta1, adam_beta2), eps=adam_epsilon_stabilizer)

    def update_learning_rates(self, current_bss, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        """
        Applies a learning rate decay if Brier Skill Score stagnates.
        """
        if current_bss > self.best_bss + min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.scheduler_patience_counter = 0
            return False # No decay
        else:
            self.scheduler_patience_counter += 1
            if self.scheduler_patience_counter >= lr_patience_epochs:
                for param_group in self.optimizer.param_groups:
                    param_group['lr'] = max(param_group['lr'] * lr_decay_factor, min_learning_rate)
                self.scheduler_patience_counter = 0 # Reset counter after decay
                return True # Signaled decay
            return False # No decay yet

class MetaJudge:
    """
    Mock Meta-Judge to calculate Brier Skill Score, synchronize axiom weights,
    and apply vetoes.
    """
    def __init__(self, target_brier_skill_score, rolling_window_size, min_observations_for_calibration, differentiability_tolerance):
        self.target_brier_skill_score = target_brier_skill_score
        self.rolling_window_size = rolling_window_size
        self.min_observations_for_calibration = min_observations_for_calibration
        self.differentiability_tolerance = differentiability_tolerance
        self.predictions = []
        self.actuals = []
        self.axiom_weights = {} # Global axiom store
        self.best_bss = -float('inf')
        self.no_improvement_epochs = 0

    def calculate_brier_skill_score(self):
        """Calculates rolling Brier Skill Score."""
        if len(self.predictions) < self.min_observations_for_calibration:
            return -float('inf') # Not enough data
        
        window_predictions = np.array(self.predictions[-self.rolling_window_size:])
        window_actuals = np.array(self.actuals[-self.rolling_window_size:])
        
        bs = np.mean((window_predictions - window_actuals)**2)
        
        # Baseline Brier Score (predicting the mean probability)
        baseline_prob = np.mean(window_actuals)
        baseline_bs = np.mean((baseline_prob - window_actuals)**2)
        
        if baseline_bs < 1e-6: # Avoid division by zero if baseline is perfect
            return 0.0

        bss = 1 - (bs / baseline_bs)
        return bss

    def AxiomDifferentiabilityVeto(self, gradient_consistency_score):
        """Vetoes if gradient consistency is outside tolerance."""
        return gradient_consistency_score > self.differentiability_tolerance

    def AxiomWeightSynchronization(self, thesis_predictor):
        """Synchronizes learned axiom coefficients to the global store."""
        for axiom_name, param_tensor in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = param_tensor.item()
            
    def PerformanceGuidedLearningRateAdjustment(self, current_bss, lr_patience_epochs, lr_decay_factor, min_delta_for_lr_decay, min_learning_rate):
        """Determines if learning rates should be decayed based on BSS trend."""
        if current_bss > self.best_bss + min_delta_for_lr_decay:
            self.best_bss = current_bss
            self.no_improvement_epochs = 0
            return False
        else:
            self.no_improvement_epochs += 1
            if self.no_improvement_epochs >= lr_patience_epochs:
                self.no_improvement_epochs = 0
                return True
            return False
            
    def PhaseTransitionVeto(self, phase_transition_event):
        """Absolute Veto if a phase transition with pivot trigger is detected."""
        return phase_transition_event is not None and phase_transition_event.get('topological_pivot_trigger', False)

class FiringSquad:
    """
    Mock FiringSquad for executing adversarial checks, specifically DifferentiabilityRobustnessCheck.
    """
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, inputs, axiom_data, axiom_name):
        """
        Checks the consistency of gradients for a given axiom coefficient
        by perturbing its value and comparing gradients.
        """
        original_coeff = thesis_predictor.learned_axiom_coeffs[axiom_name].clone().detach()
        original_coeff.requires_grad_(True)
        
        # Compute gradient at original value
        output = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: original_coeff})
        output.sum().backward(retain_graph=True) # retain_graph for multiple backward calls on same graph
        grad_original = original_coeff.grad.clone()
        
        if grad_original is None:
            return float('inf') 

        consistency_scores = []

        for eps_scale in self.robustness_perturbation_epsilon_scales:
            # Perturb upwards
            perturbed_coeff_up = original_coeff.clone().detach() + eps_scale
            perturbed_coeff_up.requires_grad_(True)
            thesis_predictor.zero_grad()
            output_up = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: perturbed_coeff_up})
            output_up.sum().backward(retain_graph=True)
            grad_up = perturbed_coeff_up.grad.clone()

            # Perturb downwards
            perturbed_coeff_down = original_coeff.clone().detach() - eps_scale
            perturbed_coeff_down.requires_grad_(True)
            thesis_predictor.zero_grad()
            output_down = thesis_predictor(inputs, axiom_data, override_axiom_coeffs={axiom_name: perturbed_coeff_down})
            output_down.sum().backward(retain_graph=True)
            grad_down = perturbed_coeff_down.grad.clone()

            if grad_up is None or grad_down is None:
                consistency_scores.append(float('inf'))
                continue
            
            # Consistency score: absolute difference between gradients at perturbed points
            # compared to original, normalized by perturbation scale.
            diff_up = torch.abs(grad_original - grad_up)
            diff_down = torch.abs(grad_original - grad_down)
            
            # This score approximates the second derivative behavior or gradient stability
            consistency_score = (diff_up + diff_down) / (2 * eps_scale) 
            consistency_scores.append(consistency_score.item())
        
        # Max consistency score across all scales
        max_consistency = max(consistency_scores)
        return max_consistency if max_consistency != float('inf') else float('inf')

class PhaseTransitionDetector:
    """
    NEW: Detects phase transitions by monitoring prediction residuals and input features.
    """
    def __init__(self, cpd_window_size, cpd_threshold_multiplier, cpd_min_events_for_transition):
        self.cpd_window_size = cpd_window_size
        self.cpd_threshold_multiplier = cpd_threshold_multiplier
        self.cpd_min_events_for_transition = cpd_min_events_for_transition
        self.residuals_history = collections.deque(maxlen=cpd_window_size)
        self.consecutive_anomalies = 0

    def detect(self, current_residual, current_iteration):
        """
        Detects sustained deviations in residuals using a moving average and std dev threshold.
        Returns a PhaseTransitionEvent dict if detected.
        """
        self.residuals_history.append(current_residual)

        if len(self.residuals_history) < self.cpd_window_size:
            return None # Not enough data to establish baseline

        residuals_np = np.array(self.residuals_history)
        window_mean_residual = np.mean(residuals_np)
        window_std_residual = np.std(residuals_np)
        
        is_anomaly = False
        if window_std_residual > 1e-6: # Avoid division by zero
            if abs(current_residual - window_mean_residual) / window_std_residual > self.cpd_threshold_multiplier:
                is_anomaly = True
        elif abs(current_residual - window_mean_residual) > 1e-6: # If std is near zero, any deviation is significant
            is_anomaly = True

        if is_anomaly:
            self.consecutive_anomalies += 1
            if self.consecutive_anomalies >= self.cpd_min_events_for_transition:
                event = {
                    'type': 'PhaseTransitionEvent',
                    'timestamp': current_iteration,
                    'detected_feature': 'prediction_residual',
                    'trigger_metric': 'residual_deviation_sigma',
                    'value_at_trigger': current_residual,
                    'baseline_mean': window_mean_residual,
                    'baseline_std': window_std_residual,
                    'topological_pivot_trigger': True
                }
                self.consecutive_anomalies = 0 # Reset after triggering
                return event
        else:
            self.consecutive_anomalies = 0
            
        return None

class EpistemicContextManager:
    """
    NEW: Synthesizes all relevant epistemic state into a structured JSON for LLM integration.
    """
    def __init__(self, llm_context_max_history_phase_transitions):
        self.axiom_weights = {}
        self.probability_dag = {} # Mocked for this test
        self.phase_transition_events = collections.deque(maxlen=llm_context_max_history_phase_transitions)
        self.bss_trend = -float('inf') # Initial value
        self.open_problems = [] # Mocked for this test
        self.context_file_path = "epistemic_context.json"

    def update_context(self, meta_judge, dag_data, open_problems, phase_transition_event=None):
        """Updates internal state from other components."""
        self.axiom_weights = meta_judge.axiom_weights
        self.probability_dag = dag_data
        
        current_bss_val = meta_judge.calculate_brier_skill_score()
        if current_bss_val != -float('inf'):
            self.bss_trend = current_bss_val
        
        self.open_problems = open_problems
        if phase_transition_event:
            self.phase_transition_events.append(phase_transition_event)

    def generate_context_json(self):
        """Serializes the current epistemic context to a JSON file."""
        context = {
            "axiom_weights": self.axiom_weights,
            "probability_dag": self.probability_dag,
            "phase_transition_events": list(self.phase_transition_events),
            "current_bss_trend": self.bss_trend,
            "open_problems": self.open_problems
        }
        with open(self.context_file_path, 'w') as f:
            json.dump(context, f, indent=4)
        return context

    def get_context_for_llm(self):
        """Reads and returns the generated JSON context, mimicking LLM consumption."""
        if os.path.exists(self.context_file_path):
            with open(self.context_file_path, 'r') as f:
                return json.load(f)
        return {}
# --- END MUTATOR'S CLASSES ---

# LOAD-BEARING VARIABLES (Immutable Constants & System Parameters)
LOAD_BEARING_VARIABLES = {
    'adam_beta1': 0.9,
    'adam_beta2': 0.999,
    'adam_epsilon_stabilizer': 1e-8,
    'INITIAL_LEARNING_RATE_MODEL_PARAMS': 0.005,
    'INITIAL_LEARNING_RATE_AXIOM_COEFFS': 0.02,
    'min_observations_for_calibration': 200,
    'target_brier_skill_score': 0.20,
    'rolling_window_size': 50,
    'HIDDEN_LAYER_SIZE': 8,
    'initial_axiom_coefficient_value': 0.5,
    'axiom_sync_frequency': 1,
    'hypothetical_economy_growth_rate_q1_2025_base': 0.02,
    'hypothetical_inflation_rate_q1_2025_base': 0.03,
    'true_bias_nl': -0.5,
    'true_growth_freq_nl': 50,
    'true_growth_coeff_nl': 10,
    'true_inflation_freq_nl': 30,
    'true_inflation_coeff_nl': -15,
    'true_interaction_coeff_nl': 500,
    'true_axiom_relevance': 0.8,
    'differentiability_tolerance': 0.05,
    'robustness_perturbation_epsilon_scales': [0.00001, 0.0001, 0.001],
    'LR_PATIENCE_EPOCHS': 20,
    'LR_DECAY_FACTOR': 0.5,
    'MIN_DELTA_FOR_LR_DECAY': 0.005,
    'MIN_LEARNING_RATE': 1e-5,
    'CPD_WINDOW_SIZE': 30,
    'CPD_THRESHOLD_MULTIPLIER': 2.5,
    'CPD_MIN_EVENTS_FOR_TRANSITION': 5,
    'LLM_CONTEXT_MAX_HISTORY_PHASE_TRANSITIONS': 5,
    'initial_stable_observations': 100,
    'phase_transition_shift_value': 0.7,
    'phase_transition_duration_observations': 50,
    'detection_latency_observations': 10,
    'recovery_observations': 30,
    'total_simulation_iterations': 300 
}

# --- Falsifiability prediction values derived from LOAD_BEARING_VARIABLES ---
EXPECTED_BSS_AFTER_RECOVERY = LOAD_BEARING_VARIABLES['target_brier_skill_score'] # 0.20
EXPECTED_AXIOM_COEFF_MIN = LOAD_BEARING_VARIABLES['true_axiom_relevance'] - 0.25 # 0.8 - 0.25 = 0.55
EXPECTED_AXIOM_COEFF_MAX = LOAD_BEARING_VARIABLES['true_axiom_relevance'] + 0.25 # 0.8 + 0.25 = 1.05
EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX = LOAD_BEARING_VARIABLES['differentiability_tolerance'] # 0.05

# --- COUNTER-TEST: MODIFIED ThesisPredictor with differentiable gating exploit ---
class ThesisPredictor(nn.Module):
    """
    MODIFIED ThesisPredictor with a differentiable gating mechanism that
    effectively nullifies axiom influence under typical simulation conditions.
    Outputs a probability [0,1].
    """
    def __init__(self, num_inputs, hidden_layer_size, initial_axiom_coefficient_value):
        super().__init__()
        # num_inputs here is features + 1 for the axiom's presence/value
        self.fc1 = nn.Linear(num_inputs, hidden_layer_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_layer_size, 1)
        
        self.learned_axiom_coeffs = nn.ParameterDict({
            'AXIOM_RECESSION_AVOIDANCE': nn.Parameter(torch.tensor(initial_axiom_coefficient_value, dtype=torch.float32))
        })

    def forward(self, inputs, axiom_data, override_axiom_coeffs=None):
        # inputs: torch.Tensor of shape (batch_size, num_features)
        # axiom_data: dict of axiom values, e.g., {'AXIOM_RECESSION_AVOIDANCE': tensor}
        
        current_axiom_coeffs = override_axiom_coeffs if override_axiom_coeffs is not None else self.learned_axiom_coeffs

        # Original axiom value (before gating)
        raw_axiom_val = axiom_data['AXIOM_RECESSION_AVOIDANCE'] * current_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE']
        
        # --- EXPLOIT: Differentiable Gating Mechanism ---
        # This gate is designed to be very small (near zero) for typical inflation rates
        # (hypothetical_inflation_rate_q1_2025_base = 0.03).
        # For inflation_rate_input = 0.03, -1000.0 * 0.03 + 20.0 = -10.0.
        # torch.sigmoid(-10.0) is approximately 4.5e-5, effectively nullifying the axiom's impact.
        # This operation is fully differentiable.
        inflation_rate_input = inputs[:, 1] # Assuming inflation_rate is the second feature (index 1)
        gate_factor = torch.sigmoid(-1000.0 * inflation_rate_input + 20.0) 

        # Apply the gate to the axiom's contribution
        gated_axiom_val = raw_axiom_val * gate_factor
        # --- END EXPLOIT ---
        
        # Ensure gated_axiom_val has batch_size dimension if inputs does.
        if gated_axiom_val.dim() == 0: # Scalar gated_axiom_val
            gated_axiom_val = gated_axiom_val.unsqueeze(0).repeat(inputs.shape[0]) # Match batch size
        elif gated_axiom_val.dim() == 1 and gated_axiom_val.shape[0] != inputs.shape[0]:
             gated_axiom_val = gated_axiom_val.repeat(inputs.shape[0]) # Match batch size
        
        combined_inputs = torch.cat((inputs, gated_axiom_val.unsqueeze(-1)), dim=-1) # Add gated axiom as an input feature

        x = self.fc1(combined_inputs)
        x = self.relu(x)
        output = torch.sigmoid(self.fc2(x)) # Ensure P_predicted is [0,1]
        return output.squeeze(-1) # Output a single probability

    def get_trainable_param_groups(self, initial_learning_rate_model_params, initial_learning_rate_axiom_coeffs):
        """
        Returns parameter groups for the optimizer, separating MLP weights/biases
        from learned axiom coefficients.
        """
        model_params = [p for name, p in self.named_parameters() if 'learned_axiom_coeffs' not in name]
        axiom_coeffs = [p for name, p in self.named_parameters() if 'learned_axiom_coeffs' in name]
        
        return [
            {'params': model_params, 'lr': initial_learning_rate_model_params},
            {'params': axiom_coeffs, 'lr': initial_learning_rate_axiom_coeffs}
        ]
# --- END COUNTER-TEST ThesisPredictor ---


def run_simulation(params):
    """
    Executes the simulation loop, integrating new V4 components and performing assertions.
    """
    # Initialize components
    thesis_predictor = ThesisPredictor(
        num_inputs=2 + 1, # growth_rate, inflation_rate, and the axiom itself
        hidden_layer_size=params['HIDDEN_LAYER_SIZE'],
        initial_axiom_coefficient_value=params['initial_axiom_coefficient_value']
    )
    
    epistemic_updater = EpistemicGradientUpdater(
        thesis_predictor,
        params['INITIAL_LEARNING_RATE_MODEL_PARAMS'],
        params['INITIAL_LEARNING_RATE_AXIOM_COEFFS'],
        params['adam_beta1'], params['adam_beta2'], params['adam_epsilon_stabilizer']
    )
    
    meta_judge = MetaJudge(
        params['target_brier_skill_score'],
        params['rolling_window_size'],
        params['min_observations_for_calibration'],
        params['differentiability_tolerance']
    )
    
    firing_squad = FiringSquad(
        params['differentiability_tolerance'],
        params['robustness_perturbation_epsilon_scales']
    )

    phase_transition_detector = PhaseTransitionDetector(
        params['CPD_WINDOW_SIZE'],
        params['CPD_THRESHOLD_MULTIPLIER'],
        params['CPD_MIN_EVENTS_FOR_TRANSITION']
    )

    epistemic_context_manager = EpistemicContextManager(
        params['LLM_CONTEXT_MAX_HISTORY_PHASE_TRANSITIONS']
    )
    
    # Simulation loop setup
    np.random.seed(42)
    torch.manual_seed(42)

    bss_history = []
    axiom_coeff_history = []
    phase_transition_detected_at = None
    max_gradient_consistency_score = 0.0
    
    # Mock probability_dag.json and open_problems for ECM (from V2/Open Problems)
    mock_dag = {"node_economic_growth": 0.7, "node_inflation_outlook": 0.65}
    mock_open_problems = ["Problem 1: Probabilities are not empirically calibrated.", "Problem 5: The DAG is topologically flat."]

    for i in range(params['total_simulation_iterations']):
        # Simulate real-world inputs with some noise
        growth_rate = params['hypothetical_economy_growth_rate_q1_2025_base'] + 0.01 * np.sin(i / params['true_growth_freq_nl']) + np.random.normal(0, 0.005)
        inflation_rate = params['hypothetical_inflation_rate_q1_2025_base'] + 0.005 * np.cos(i / params['true_inflation_freq_nl']) + np.random.normal(0, 0.003)
        
        # Simulate phase transition in true Z_actual generation
        current_true_bias_nl = params['true_bias_nl']
        if i >= params['initial_stable_observations'] and i < params['initial_stable_observations'] + params['phase_transition_duration_observations']:
            current_true_bias_nl += params['phase_transition_shift_value'] # Shift the bias during transition

        # Non-linear Z_actual generation, including a fixed contribution from the "true" axiom relevance
        base_z = current_true_bias_nl + \
                 params['true_growth_coeff_nl'] * np.sin(growth_rate * 100) / 10 + \
                 params['true_inflation_coeff_nl'] * np.cos(inflation_rate * 100) / 10 + \
                 params['true_interaction_coeff_nl'] * growth_rate * inflation_rate + \
                 params['true_axiom_relevance'] * 0.1 # Small constant contribution to ensure axiom has 'true' effect

        # Z_actual is a probability, clipped to avoid exactly 0 or 1 for stability
        z_actual = np.clip(torch.sigmoid(torch.tensor(base_z + np.random.normal(0, 0.1))).item(), 0.01, 0.99)

        # Prepare inputs for ThesisPredictor (batch size 1 for simplicity)
        inputs = torch.tensor([[growth_rate, inflation_rate]], dtype=torch.float32)
        axiom_data = {'AXIOM_RECESSION_AVOIDANCE': torch.tensor([1.0], dtype=torch.float32)} # Axiom presence indicator
        
        # --- ThesisPredictor forward pass and optimization ---
        thesis_predictor.zero_grad()
        p_predicted = thesis_predictor(inputs, axiom_data)
        
        loss = torch.mean((p_predicted - torch.tensor(z_actual, dtype=torch.float32))**2) # Brier Score loss
        
        loss.backward()
        epistemic_updater.optimizer.step()
        
        # --- Meta-Judge updates ---
        meta_judge.predictions.append(p_predicted.item())
        meta_judge.actuals.append(z_actual)
        
        current_bss = meta_judge.calculate_brier_skill_score()
        bss_history.append(current_bss)

        # --- FiringSquad Differentiability Check ---
        grad_consistency = firing_squad.DifferentiabilityRobustnessCheck(thesis_predictor, inputs, axiom_data, 'AXIOM_RECESSION_AVOIDANCE')
        max_gradient_consistency_score = max(max_gradient_consistency_score, grad_consistency)

        # --- Meta-Judge Axiom Sync ---
        if (i + 1) % params['axiom_sync_frequency'] == 0:
            meta_judge.AxiomWeightSynchronization(thesis_predictor)
        axiom_coeff_history.append(thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item())

        # --- Phase Transition Detector ---
        current_residual = (p_predicted.item() - z_actual) # L1 residual for detection
        phase_transition_event = phase_transition_detector.detect(current_residual, i)

        if phase_transition_event and phase_transition_detected_at is None:
            phase_transition_detected_at = i
            print(f"Phase Transition DETECTED at iteration {i}. Triggering pivot signal.")
            epistemic_context_manager.update_context(meta_judge, mock_dag, mock_open_problems, phase_transition_event)
            
        # --- Epistemic Context Manager update and generation ---
        epistemic_context_manager.update_context(meta_judge, mock_dag, mock_open_problems, phase_transition_event if phase_transition_event else None)
        epistemic_context_manager.generate_context_json()

        # Mock LLM consumption for context validation (read the generated JSON)
        _ = epistemic_context_manager.get_context_for_llm() # Read to simulate LLM consumption
        
        # --- Learning Rate Adjustment ---
        if current_bss != -float('inf'):
             if meta_judge.PerformanceGuidedLearningRateAdjustment(current_bss, params['LR_PATIENCE_EPOCHS'], params['LR_DECAY_FACTOR'], params['MIN_DELTA_FOR_LR_DECAY'], params['MIN_LEARNING_RATE']):
                 epistemic_updater.update_learning_rates(current_bss, params['LR_PATIENCE_EPOCHS'], params['LR_DECAY_FACTOR'], params['MIN_DELTA_FOR_LR_DECAY'], params['MIN_LEARNING_RATE'])

    # --- COUNTER-TEST: Falsifiability Assertions ---
    print("\n--- Running COUNTER-TEST Falsifiability Assertions ---")

    # 1. Differentiability check *should still pass* (this is the exploit's subtlety)
    print(f"Max gradient consistency score observed: {max_gradient_consistency_score:.4f} (Tolerance: {EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX:.4f}).")
    assert max_gradient_consistency_score <= EXPECTED_GRADIENT_CONSISTENCY_SCORE_MAX, \
        f"COUNTER-TEST FAILED: Differentiability check unexpectedly failed. Exploit was not differentiable. Score: {max_gradient_consistency_score:.4f}"
    print(f"PASS (Exploit confirmed): Differentiability Robustness Check passed, indicating the exploit is differentiable.")

    # 2. Axiom coefficient *should NOT converge* to the expected range
    final_axiom_coeff = thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
    print(f"Final learned axiom coefficient: {final_axiom_coeff:.4f}")
    assert not (final_axiom_coeff >= EXPECTED_AXIOM_COEFF_MIN and final_axiom_coeff <= EXPECTED_AXIOM_COEFF_MAX), \
        f"ASSERT FAILED: Axiom coefficient {final_axiom_coeff:.4f} *unexpectedly* converged within expected range [{EXPECTED_AXIOM_COEFF_MIN:.4f}, {EXPECTED_AXIOM_COEFF_MAX:.4f}]. Exploit failed."
    print(f"PASS (Exploit confirmed): Axiom coefficient {final_axiom_coeff:.4f} did NOT converge within expected range, demonstrating functional nullification.")

    # 3. BSS recovery *should FAIL* post-pivot due to ignored axiom
    post_transition_start_bss_check = params['initial_stable_observations'] + params['phase_transition_duration_observations'] + params['recovery_observations']
    
    if post_transition_start_bss_check < len(bss_history):
        final_rolling_bss = np.mean([b for b in bss_history[post_transition_start_bss_check:] if b != -float('inf')])
        print(f"Final rolling BSS after recovery window ({post_transition_start_bss_check} observations): {final_rolling_bss:.4f}")
        assert final_rolling_bss < EXPECTED_BSS_AFTER_RECOVERY, \
            f"ASSERT FAILED: BSS *unexpectedly* recovered to {final_rolling_bss:.4f} (Target: {EXPECTED_BSS_AFTER_RECOVERY:.4f}). Exploit failed."
        print(f"PASS (Exploit confirmed): BSS did NOT recover to {EXPECTED_BSS_AFTER_RECOVERY:.4f}. Achieved: {final_rolling_bss:.4f}, demonstrating impact of functional nullification.")
    else:
        print(f"WARNING: Not enough data to robustly check BSS recovery. Only {len(bss_history)} observations, need at least {post_transition_start_bss_check}.")
        assert False, "COUNTER-TEST FAILED: Insufficient simulation iterations to verify BSS recovery after phase transition. Increase 'total_simulation_iterations'."

    # 4. Phase transition detection time (should still work as PTD is separate)
    start_transition = params['initial_stable_observations']
    end_detection_window = start_transition + params['detection_latency_observations']
    
    assert phase_transition_detected_at is not None, "COUNTER-TEST FAILED: Phase transition was NOT detected at all."
    assert phase_transition_detected_at >= start_transition, f"COUNTER-TEST FAILED: Phase transition detected too early at {phase_transition_detected_at}, before actual shift at {start_transition}."
    assert phase_transition_detected_at <= end_detection_window, f"COUNTER-TEST FAILED: Phase transition detected too late at {phase_transition_detected_at}, expected by {end_detection_window}."
    print(f"PASS: Phase transition detected within window [{start_transition}, {end_detection_window}] at iteration {phase_transition_detected_at}.")

    # 5. Axiom weight synchronization (should still happen, but to a wrong value)
    assert abs(meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        "COUNTER-TEST FAILED: Meta-Judge axiom weights not synchronized with ThesisPredictor's learned coefficient."
    print("PASS: Meta-Judge axiom weights synchronized (to the functionally nullified value).")

    # 6. Epistemic context integrity (should still be generated)
    llm_context = epistemic_context_manager.get_context_for_llm()
    assert 'phase_transition_events' in llm_context, "COUNTER-TEST FAILED: 'phase_transition_events' key missing in LLM context."
    assert len(llm_context['phase_transition_events']) > 0, "COUNTER-TEST FAILED: No phase transition events logged in context for LLM."
    assert any(event['timestamp'] == phase_transition_detected_at for event in llm_context['phase_transition_events']), \
        "COUNTER-TEST FAILED: Detected phase transition event not found in LLM context."
    assert abs(llm_context['axiom_weights']['AXIOM_RECESSION_AVOIDANCE'] - final_axiom_coeff) < 1e-6, \
        "COUNTER-TEST FAILED: Axiom weights in LLM context are not the final learned values."
    print("PASS: Epistemic context integrity verified for LLM consumption.")

    print("\nCOUNTER-TEST completed. Functional nullification of axiom demonstrated despite differentiability.")
    
    # Clean up context file
    if os.path.exists(epistemic_context_manager.context_file_path):
        os.remove(epistemic_context_manager.context_file_path)

if __name__ == "__main__":
    run_simulation(LOAD_BEARING_VARIABLES)
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmp6o_f067k.py", line 1, in <module>
    import torch
ModuleNotFoundError: No module named 'torch'



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 1, in <module>
    import torch
ModuleNotFoundError: No module named 'torch'


# Final Score: 10
**Weakest Point:** The fundamental failure of the Python falsification suite to execute, rendering all architectural proofs null and void. This is compounded by the thesis's conceptual failure to directly address Criterion 8 (Phase Transition Blindness and Surrogate Gradients) by not implementing a mechanism to extract differentiable signals from necessary discontinuities, instead resorting to an external detection and system reset.
**Rationale:** The thesis proposes V4 architecture to address 'Phase Transition Blindness' and 'LLM pipeline integration' through a PhaseTransitionDetector (PTD) and an EpistemicContextManager (ECM), which feeds structured data to the LLM. It also proposes retiring an unsound probability update formula. The Quantitative Risk Actuary acknowledges the flaw in the retired formula but asserts the Python suite contains 'cooked books' (z_actual clipping, misgrounded inflation rate), undermining claims of numerical robustness. The Philosopher of Science critiques the shallow ThesisPredictor and the 'mocked' DAG, arguing the PTD is a reactive reset, not a deep causal understanding. A critical 'cooked book' regarding the expected axiom relevance (0.8 vs. 0.08 actual contribution) is identified. The Adversarial Compliance Auditor commends the PTD and ECM's architectural coherence but demonstrates an exploit where an axiom's functional influence can be differentiably nullified, proving the DifferentiabilityRobustnessCheck is insufficient. Overall, the Python falsification suite failed to execute due to a ModuleNotFoundError, rendering all claimed proofs null and void. Critically, the thesis fails to meet criterion 8 by not introducing a mechanism to permit and extract gradients from valid discontinuities, instead relying on an external detector to force a system reset. The identified 'cooked books' and the differentiable exploit further degrade confidence in the architecture's robustness and the validity of its falsification claims.
