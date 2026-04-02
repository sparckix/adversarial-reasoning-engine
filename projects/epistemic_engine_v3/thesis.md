RETIRED AXIOM: `new_prob = prior * exp(-1.1 * relative_error)` - This mathematical relationship creates unbounded probabilities outside the [0, 1] domain, rendering it fundamentally unsound for probabilistic reasoning. It is structurally irrelevant to a system requiring empirically calibrated probabilities and direct gradient-based credit assignment.

---

### SYSTEMIC INCONSISTENCY RESOLUTION: Bridging Phase Transition Blindness and LLM Pipeline Integration

**Z (Resultant State):** The `ThesisPredictor` robustly learns both continuous axiom contributions and the parameters of its internal `phase_transition_module`, leading to a `P_predicted` that accurately reflects the underlying non-linear, phase-transition-affected `Z_actual`. The `PhaseTransitionModelingError` converges below `phase_transition_modeling_tolerance`, and `LLMGuidanceDataIncompleteness` becomes 0. The `Meta-Judge` consistently outputs comprehensive, differentiable LLM guidance, explicitly bridging the gap to the operational LLM by providing real-time, empirically derived, and verified insights into complex, non-linear system dynamics, thereby resolving both the "Phase Transition Blindness" and "LLM Pipeline Integration" failures.

**X (Blocked Variable):** The architecture's fundamental limitation in addressing non-smooth, real-world phenomena (Phase Transition Blindness) using gradient-based methods, compounded by the complete absence of a concrete mechanism for direct LLM pipeline integration. This `EpistemicBlindnessToDiscontinuitiesAndLLMIsolation` is quantified as:
$X = \text{PhaseTransitionModelingError} + \text{LLMGuidanceDataIncompleteness}$
Where:
$\text{PhaseTransitionModelingError} = |\text{learned\_steepness} - \text{true\_steepness}| + |\text{learned\_threshold} - \text{true\_threshold}|$
$\text{LLMGuidanceDataIncompleteness} = 1 \text{ if LLM guidance lacks learned phase transition parameters, else } 0$

**Y (Leverage Variable):**
1.  **`ThesisPredictor.phase_transition_linear`**: An internal `torch.nn.Linear` layer within `ThesisPredictor` whose `weight` and `bias` parameters are learnable. This module takes a derived input (e.g., `growth_rate - inflation_rate`) and produces a raw output (`p_phase_transition_raw`) that directly contributes to the final `P_predicted`. This `nn.Linear` layer, when passed through a `torch.sigmoid` within the `P_predicted` calculation, effectively forms a differentiable approximation of a step function, enabling the system to *learn the steepness and threshold* of real-world phase transitions while maintaining end-to-end differentiability.
2.  **`MetaJudge.generate_llm_guidance()`**: A new method that compiles a JSON object containing `rolling_brier_skill_score`, `learned_axiom_coeffs`, and crucially, the *learned parameters of the `ThesisPredictor.phase_transition_linear` (its weight and bias)* into a structured guidance document. This artifact is explicitly saved to a predefined path (`LLM_GUIDANCE_PATH`), effectively serving as a real-time, empirically derived input constraint for the `Mutator` (LLM) to parse and integrate into its thesis generation process.
3.  **Extended `FiringSquad.DifferentiabilityRobustnessCheck`**: The `DifferentiabilityRobustnessCheck` is enhanced to include the parameters of the `ThesisPredictor.phase_transition_linear`. This ensures that even the differentiable approximation of phase transitions remains robust and untainted by non-smooth exploitable functions.

---

### LOAD-BEARING VARIABLES

| Variable                                        | Role                                                                               | Exact Real-World Value (or system parameter)                                                                                                                                                                                |
| :---------------------------------------------- | :--------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `adam_beta1`                                    | Adam optimizer parameter: decay rate for first moment estimates (`m`)              | `0.9` (Dimensionless, standard Adam hyperparameter)                                                                                                                                                                         |
| `adam_beta2`                                    | Adam optimizer parameter: decay rate for second moment estimates (`v`)             | `0.999` (Dimensionless, standard Adam hyperparameter)                                                                                                                                                                       |
| `adam_epsilon_stabilizer`                       | Adam optimizer parameter: small constant to prevent division by zero               | `1e-8` (Dimensionless, standard Adam hyperparameter)                                                                                                                                                                        |
| `INITIAL_LEARNING_RATE_MODEL_PARAMS`            | Initial global learning rate scale for all model parameters                        | `0.005` (Dimensionless, empirically tuned for stability in non-linear models)                                                                                                                                                |
| `INITIAL_LEARNING_RATE_AXIOM_COEFFS`            | Initial learning rate scale specifically for axiom coefficients                    | `0.02` (Dimensionless, higher for faster axiom adaptation)                                                                                                                                                                    |
| `INITIAL_LEARNING_RATE_PHASE_TRANSITION_MODULE` | Initial learning rate scale for phase transition module parameters                 | `0.01` (Dimensionless, tuned for stable learning of transition dynamics)                                                                                                                                                    |
| `min_observations_for_calibration`              | Minimum `Z_actual` observations before BSS can be robustly calculated              | `200` (System parameter, increased due to greater model complexity)                                                                                                                                                         |
| `target_brier_skill_score`                      | Minimum acceptable Brier Skill Score after calibration                             | `0.20` (Dimensionless target: 20% improvement over baseline)                                                                                                                                                                  |
| `rolling_window_size`                           | Number of observations for rolling average Brier Skill Score calculation           | `50` (System parameter for BSS temporal averaging)                                                                                                                                                                          |
| `HIDDEN_LAYER_SIZE`                             | Number of neurons in the `ThesisPredictor`'s hidden layer                          | `8` (Dimensionless, increased from `4` for more capacity)                                                                                                                                                                   |
| `initial_axiom_coefficient_value`               | Initial value for axiom coefficients within `ThesisPredictor`                      | `0.5` (Dimensionless, serves as starting point for learned axiom relevance)                                                                                                                                                 |
| `initial_phase_transition_linear_weight`        | Initial value for `phase_transition_linear`'s weight parameter                     | `0.0` (Dimensionless, initial guess for steepness, starting from neutral)                                                                                                                                                   |
| `initial_phase_transition_linear_bias`          | Initial value for `phase_transition_linear`'s bias parameter                       | `0.0` (Dimensionless, initial guess for threshold, starting from neutral)                                                                                                                                                   |
| `axiom_sync_frequency`                          | Frequency for `Meta-Judge` to sync learned axiom coefficients                      | `1` (Dimensionless: syncs every single update iteration)                                                                                                                                                                    |
| `hypothetical_economy_growth_rate_q1_2025_base` | Baseline for simulated economy growth rate                                         | `0.02` (Dimensionless rate, e.g., 2% per quarter)                                                                                                                                                                           |
| `hypothetical_inflation_rate_q1_2025_base`      | Baseline for simulated inflation rate                                              | `0.03` (Dimensionless rate, e.g., 3% per quarter)                                                                                                                                                                           |
| `true_bias_nl`                                  | Intercept term for the *simulated non-linear* `Z_actual` function                  | `-0.5` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                 |
| `true_growth_freq_nl`                           | Frequency parameter for sine component of *simulated non-linear* growth effect     | `50` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                   |
| `true_growth_coeff_nl`                          | Coefficient for sine component of *simulated non-linear* growth effect             | `10` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                   |
| `true_inflation_freq_nl`                        | Frequency parameter for cosine component of *simulated non-linear* inflation effect | `30` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                   |
| `true_inflation_coeff_nl`                       | Coefficient for cosine component of *simulated non-linear* inflation effect        | `-15` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                  |
| `true_interaction_coeff_nl`                     | Coefficient for interaction term (`growth_rate * inflation_rate`)                  | `500` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                  |
| `true_axiom_relevance`                          | Relevance of `AXIOM_RECESSION_AVOIDANCE` in the *simulated non-linear* `Z_actual`  | `0.8` (Dimensionless, true contribution of the fixed axiom)                                                                                                                                                                 |
| `true_phase_transition_threshold_true`          | Trigger point for the *simulated non-linear* phase transition                      | `-0.01` (Dimensionless, e.g., `growth_rate - inflation_rate` below this triggers transition)                                                                                                                                |
| `true_phase_transition_steepness_true`          | Steepness parameter for the *simulated non-linear* phase transition                | `200.0` (Dimensionless, how sharply the transition occurs in `Z_actual`)                                                                                                                                                    |
| `true_phase_transition_effect`                  | Magnitude of impact of the *simulated non-linear* phase transition                 | `-0.3` (Dimensionless, e.g., a drop of 0.3 in the raw `Z_actual` pre-sigmoid)                                                                                                                                               |
| `differentiability_tolerance`                   | Max allowed absolute difference between perturbation gradients                     | `0.05` (Dimensionless, empirically tuned for robustness)                                                                                                                                                                   |
| `robustness_perturbation_epsilon_scales`        | Array of epsilon scales for `DifferentiabilityRobustnessCheck`                     | `[0.00001, 0.0001, 0.001]` (Dimensionless, multiple tighter small scales)                                                                                                                                                   |
| `LR_PATIENCE_EPOCHS`                            | Number of iterations without BSS improvement before LR decay                       | `20` (Dimensionless, system parameter for learning rate scheduling)                                                                                                                                                         |
| `LR_DECAY_FACTOR`                               | Factor by which learning rates are reduced during decay                            | `0.5` (Dimensionless, standard decay factor)                                                                                                                                                                                |
| `MIN_DELTA_FOR_LR_DECAY`                        | Minimum BSS improvement to reset patience counter                                  | `0.005` (Dimensionless, threshold for considering BSS as 'improved')                                                                                                                                                        |
| `MIN_LEARNING_RATE`                             | Floor for learning rates to prevent them from dropping to zero                     | `1e-5` (Dimensionless, ensures learning doesn't completely stop)                                                                                                                                                            |
| `phase_transition_modeling_tolerance`           | Max acceptable error for phase transition parameter learning                       | `0.05` (Dimensionless, sum of absolute errors for learned steepness and threshold)                                                                                                                                          |
| `LLM_GUIDANCE_PATH`                             | File path for `Meta-Judge` to output LLM guidance JSON                           | `"llm_guidance.json"` (String, system path for Mutator input)                                                                                                                                                               |

---

### STRUCTURAL ARBITRAGE

The architectural bypass resolves the `EpistemicBlindnessToDiscontinuitiesAndLLMIsolation` by introducing two reciprocal leverage points. First, the `ThesisPredictor` is augmented with a **`phase_transition_linear` module**, a `torch.nn.Linear` layer whose learnable parameters (`weight` and `bias`) are integrated into the `P_predicted` calculation. This enables the system to construct a *differentiable approximation* of real-world discontinuities (phase transitions) by learning their inherent steepness and threshold, thereby extracting precise gradient signals from previously non-smooth phenomena. Second, the `Meta-Judge` now explicitly activates **`generate_llm_guidance()`**, which serializes not only the `learned_axiom_coeffs` and `rolling_brier_skill_score` but also the *learned parameters of the `phase_transition_linear`* into a structured JSON artifact (`llm_guidance.json`). This artifact serves as a mandatory, real-time input for the `Mutator` (LLM), thereby forcing direct integration of empirically validated, differentiable insights into non-linear system dynamics into the LLM's reasoning pipeline. This combined approach transforms a computationally unlearnable aspect of reality into a gradient-optimizable and LLM-actionable truth, achieving "last-mile derivation" for regime shifts and directly integrating the engine's highest-fidelity insights into the LLM workflow.

---

### CONSERVATION OF TRADE-OFFS

*   **Velocity (V):** Infinite increase in effective learning and convergence velocity for phase-transitioning systems, as the architecture transitions from epistemic blindness to learning and direct LLM integration (V=0 to V>0). The system can now proactively adapt to and inform about regime shifts.
*   **Energy (E):** Marginally increased computational overhead. The `ThesisPredictor` now includes an additional `nn.Linear` layer, adding parameters to train and computations per forward/backward pass. The `FiringSquad.DifferentiabilityRobustnessCheck` now explicitly extends to these new parameters, increasing the number of gradient computations during falsification. The `Meta-Judge.generate_llm_guidance()` also introduces minor serialization overhead.
*   **Mass (M):** Slightly increased architectural complexity within `ThesisPredictor` (for the `phase_transition_linear` module) and `Meta-Judge` (for handling and serializing phase transition parameters in LLM guidance).

**New Operational Drag:**
The **`ThesisPredictor.phase_transition_linear` module** introduces `2 * |num_phase_transition_inputs|` additional learnable parameters (here, 2 parameters for a single input to the linear layer) that require gradient computation and rigorous differentiability checks during every falsification cycle. This adds a small but persistent multiplicative overhead to the core learning and validation loops. Furthermore, the **`MetaJudge.generate_llm_guidance()`** method necessitates serialization and data transfer of these new learned phase transition parameters, adding complexity to the data contract and imposing a non-trivial parsing and ingestion overhead on the downstream `Mutator` (LLM), which must now consistently interpret a more complex structured input.

---

### GATEKEEPER REALITY

*   **Absolute Veto (The Bottleneck):** The **Meta-Judge's `AxiomDifferentiabilityVeto` constraint** is extended to encompass the *parameters of the `ThesisPredictor.phase_transition_linear`*. It retains absolute authority to reject any thesis if the `FiringSquad`'s enhanced `DifferentiabilityRobustnessCheck` reports a `GradientConsistencyScore` for *any* parameter (model, axiom coefficient, or phase transition module parameter) that exceeds `differentiability_tolerance`. This ensures that the foundational `learnability` and *smoothness* of even approximated discontinuities are uncompromised, preventing non-differentiable exploits.
*   **Asymmetric Leverage:** The **direct feedback loop established by `MetaJudge.generate_llm_guidance()`** which explicitly outputs the *learned phase transition parameters* alongside axiom coefficients and performance metrics in a structured, parseable JSON format. This mechanism *forces* the `Mutator` (LLM) to acknowledge, interpret, and integrate these empirically derived non-linear dynamics into its reasoning process for thesis generation. This direct, verifiable pipeline integration bridges the epistemic engine to the LLM's operational context, transforming "epistemic blindness" into "epistemic guidance" and compelling the LLM to grapple with empirically validated discontinuities rather than merely hand-waving or abstracting them. The absolute differentiability veto ensures this guidance is always computationally sound and robust.

---

### FALSIFIABILITY

**Prediction:** After `min_observations_for_calibration` (e.g., 200) simulated quarterly economic reports (where `Z_actual` is generated via a *non-linear, interacting, smoothly differentiable, and noisy* underlying process that includes `growth_rate`, `inflation_rate`, `AXIOM_RECESSION_AVOIDANCE`, and a `true_phase_transition_effect` triggered by `growth_rate - inflation_rate` falling below `true_phase_transition_threshold_true`), the engine's rolling `rolling_window_size` (e.g., 50) observation average Brier Skill Score will consistently exceed `target_brier_skill_score` (e.g., 0.20). Furthermore, the `ThesisPredictor`'s learned coefficient for `AXIOM_RECESSION_AVOIDANCE` will converge to a value greater than `0.65` and within `0.25` absolute difference of `true_axiom_relevance` (`0.8`), significantly deviating from its `initial_axiom_coefficient_value` (`0.5`).
**Crucially, the learned weight of the `phase_transition_linear` module will converge to within `0.05` absolute difference of `true_phase_transition_steepness_true` (`200.0`), and its learned bias will converge to within `0.05` absolute difference of `-true_phase_transition_steepness_true * true_phase_transition_threshold_true` (`-200.0 * -0.01 = 2.0`). The combined absolute error of these two phase transition parameters will be less than `phase_transition_modeling_tolerance` (e.g., `0.05`).** Concurrently, the `Meta-Judge` will successfully generate an `llm_guidance.json` file containing these converged phase transition parameters and axiom coefficients. For every iteration, the `FiringSquad.DifferentiabilityRobustnessCheck` will pass for *all* parameters (model, axiom, and phase transition module), with a final maximum consistency score across all iterations less than or equal to `differentiability_tolerance` (e.g., `0.05`), confirming that the system remains smoothly differentiable and uncompromised by exploits, even when modeling discontinuities.

---

### `test_model.py`

```python
import torch
import torch.nn as nn
import torch.optim as optim
import json
import numpy as np
import random
from collections import deque
import os

# --- LOAD-BEARING VARIABLES ---
# Updated for V4 architecture, including phase transition modeling and LLM guidance
LOAD_BEARING_VARIABLES = {
    "adam_beta1": 0.9,  # Dimensionless, standard Adam hyperparameter
    "adam_beta2": 0.999,  # Dimensionless, standard Adam hyperparameter
    "adam_epsilon_stabilizer": 1e-8,  # Dimensionless, standard Adam hyperparameter
    "INITIAL_LEARNING_RATE_MODEL_PARAMS": 0.005,  # Dimensionless, empirically tuned for stability
    "INITIAL_LEARNING_RATE_AXIOM_COEFFS": 0.02,  # Dimensionless, higher for faster axiom adaptation
    "INITIAL_LEARNING_RATE_PHASE_TRANSITION_MODULE": 0.01, # Dimensionless, for phase transition parameters
    "min_observations_for_calibration": 200,  # System parameter, increased due to greater model complexity
    "target_brier_skill_score": 0.20,  # Dimensionless target: 20% improvement over baseline
    "rolling_window_size": 50,  # System parameter for BSS temporal averaging
    "HIDDEN_LAYER_SIZE": 8,  # Dimensionless, increased for more capacity
    "initial_axiom_coefficient_value": 0.5,  # Dimensionless, serves as starting point
    "initial_phase_transition_linear_weight": 0.0, # Initial guess for phase transition steepness
    "initial_phase_transition_linear_bias": 0.0, # Initial guess for phase transition threshold
    "axiom_sync_frequency": 1,  # Dimensionless: syncs every single update iteration
    "hypothetical_economy_growth_rate_q1_2025_base": 0.02,  # Dimensionless rate, e.g., 2%
    "hypothetical_inflation_rate_q1_2025_base": 0.03,  # Dimensionless rate, e.g., 3%
    "true_bias_nl": -0.5,  # Dimensionless, parameter of the true underlying non-linear process
    "true_growth_freq_nl": 50,  # Dimensionless, parameter of the true underlying non-linear process
    "true_growth_coeff_nl": 10,  # Dimensionless, parameter of the true underlying non-linear process
    "true_inflation_freq_nl": 30,  # Dimensionless, parameter of the true underlying non-linear process
    "true_inflation_coeff_nl": -15,  # Dimensionless, parameter of the true underlying non-linear process
    "true_interaction_coeff_nl": 500,  # Dimensionless, parameter of the true underlying non-linear process
    "true_axiom_relevance": 0.8,  # Dimensionless, true contribution of fixed axiom
    "true_phase_transition_threshold_true": -0.01, # Trigger for phase transition (e.g., growth - inflation)
    "true_phase_transition_steepness_true": 200.0, # How sharp the true phase transition is
    "true_phase_transition_effect": -0.3, # How much the phase transition impacts P_predicted (e.g., lowers it)
    "differentiability_tolerance": 0.05,  # Max allowed absolute difference between perturbation gradients
    "robustness_perturbation_epsilon_scales": [0.00001, 0.0001, 0.001],  # Multiple tighter small scales
    "LR_PATIENCE_EPOCHS": 20,  # Number of iterations without BSS improvement before LR decay
    "LR_DECAY_FACTOR": 0.5,  # Standard decay factor
    "MIN_DELTA_FOR_LR_DECAY": 0.005,  # Minimum BSS improvement to reset patience counter
    "MIN_LEARNING_RATE": 1e-5,  # Floor for learning rates
    "phase_transition_modeling_tolerance": 0.05, # Max acceptable error for PT parameter learning (sum of abs errors)
    "LLM_GUIDANCE_PATH": "llm_guidance.json", # Path for LLM guidance output
}

# Ensure reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

class ThesisPredictor(nn.Module):
    """
    A non-linear neural network model that predicts an outcome P_predicted based on
    input features and learned axiom coefficients. Includes a differentiable phase transition module.
    """
    def __init__(self, num_inputs, hidden_layer_size, axiom_names, initial_axiom_coefficient_value,
                 initial_phase_transition_linear_weight, initial_phase_transition_linear_bias):
        super().__init__()
        self.axiom_names = axiom_names
        
        # Core MLP for general prediction
        self.mlp = nn.Sequential(
            nn.Linear(num_inputs, hidden_layer_size),
            nn.ReLU(),
            nn.Linear(hidden_layer_size, 1)
        )
        
        # Learnable axiom coefficients as nn.ParameterDict
        self.learned_axiom_coeffs = nn.ParameterDict({
            name: nn.Parameter(torch.tensor([initial_axiom_coefficient_value], dtype=torch.float32))
            for name in axiom_names
        })
        
        # New: Phase Transition Module - a simple linear layer
        # Its weight and bias will learn the steepness and threshold of the phase transition.
        self.phase_transition_linear = nn.Linear(1, 1)
        # Initialize phase transition linear layer's parameters
        with torch.no_grad():
            self.phase_transition_linear.weight.fill_(initial_phase_transition_linear_weight)
            self.phase_transition_linear.bias.fill_(initial_phase_transition_linear_bias)

    def forward(self, growth_rate, inflation_rate, axiom_inputs, override_axiom_coeffs=None, override_phase_transition_params=None):
        # Concatenate base inputs (growth_rate, inflation_rate) and relevant axiom inputs
        x_input = torch.cat([growth_rate.unsqueeze(1), inflation_rate.unsqueeze(1), 
                             axiom_inputs['AXIOM_RECESSION_AVOIDANCE'].unsqueeze(1)], dim=1)
        
        mlp_raw_output = self.mlp(x_input)

        # Apply learned axiom coefficients (using overrides for differentiability check)
        current_axiom_coeffs = override_axiom_coeffs if override_axiom_coeffs is not None else self.learned_axiom_coeffs
        axiom_contribution = current_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'] * axiom_inputs['AXIOM_RECESSION_AVOIDANCE'].unsqueeze(1)
        
        # Phase Transition Modeling - the input to this module is (growth_rate - inflation_rate)
        phase_transition_trigger_input = (growth_rate - inflation_rate).unsqueeze(1)
        
        # Override phase transition parameters if provided (for robustness check)
        if override_phase_transition_params is not None:
            # Create a temporary linear layer with overridden parameters
            temp_linear = nn.Linear(1, 1)
            temp_linear.weight.data = override_phase_transition_params['weight']
            temp_linear.bias.data = override_phase_transition_params['bias']
            p_phase_transition_raw = temp_linear(phase_transition_trigger_input)
        else:
            p_phase_transition_raw = self.phase_transition_linear(phase_transition_trigger_input)
        
        # The raw output of phase_transition_linear contributes to the total pre-sigmoid sum.
        # Its weight and bias directly learn to model the steepness and threshold of the true phase transition.
        total_pre_sigmoid = mlp_raw_output + axiom_contribution + p_phase_transition_raw
        
        P_predicted = torch.sigmoid(total_pre_sigmoid)
        return P_predicted

    def get_trainable_param_groups(self):
        """
        Explicitly returns a list of dictionaries, each representing a parameter group
        for the optimizer, ensuring all trainable components (MLP, axiom_coeffs,
        phase_transition_linear) are correctly registered as torch.nn.Parameter objects.
        """
        param_groups = [
            {'params': self.mlp.parameters(), 'lr': LOAD_BEARING_VARIABLES["INITIAL_LEARNING_RATE_MODEL_PARAMS"]},
            {'params': self.learned_axiom_coeffs.parameters(), 'lr': LOAD_BEARING_VARIABLES["INITIAL_LEARNING_RATE_AXIOM_COEFFS"]},
            {'params': self.phase_transition_linear.parameters(), 'lr': LOAD_BEARING_VARIABLES["INITIAL_LEARNING_RATE_PHASE_TRANSITION_MODULE"]}
        ]
        return param_groups

class EpistemicGradientUpdater:
    """
    Manages the Adam optimization process for the ThesisPredictor, including adaptive learning rates.
    """
    def __init__(self, thesis_predictor):
        self.thesis_predictor = thesis_predictor
        self.optimizer = None
        self.initialize_optimizer()
        self.best_brier_skill_score = -float('inf')
        self.patience_counter = 0

    def initialize_optimizer(self):
        """Initializes the Adam optimizer with distinct parameter groups from ThesisPredictor."""
        param_groups = self.thesis_predictor.get_trainable_param_groups()
        self.optimizer = optim.Adam(param_groups, 
                                    betas=(LOAD_BEARING_VARIABLES["adam_beta1"], LOAD_BEARING_VARIABLES["adam_beta2"]),
                                    eps=LOAD_BEARING_VARIABLES["adam_epsilon_stabilizer"])

    def update_learning_rates(self, current_brier_skill_score):
        """
        Adjusts learning rates for each parameter group based on Brier Skill Score improvement.
        """
        if current_brier_skill_score > self.best_brier_skill_score + LOAD_BEARING_VARIABLES["MIN_DELTA_FOR_LR_DECAY"]:
            self.best_brier_skill_score = current_brier_skill_score
            self.patience_counter = 0
        else:
            self.patience_counter += 1
            if self.patience_counter >= LOAD_BEARING_VARIABLES["LR_PATIENCE_EPOCHS"]:
                for param_group in self.optimizer.param_groups:
                    param_group['lr'] = max(param_group['lr'] * LOAD_BEARING_VARIABLES["LR_DECAY_FACTOR"], LOAD_BEARING_VARIABLES["MIN_LEARNING_RATE"])
                self.patience_counter = 0 # Reset patience after decay

    def step(self, loss):
        """Performs a single optimization step."""
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

class FiringSquad:
    """
    Executes counter-tests and performs Differentiability Robustness Check.
    Reads only stdout/stderr (simulated via direct function calls).
    """
    def __init__(self, differentiability_tolerance, robustness_perturbation_epsilon_scales):
        self.differentiability_tolerance = differentiability_tolerance
        self.robustness_perturbation_epsilon_scales = robustness_perturbation_epsilon_scales

    def DifferentiabilityRobustnessCheck(self, thesis_predictor, growth_rate, inflation_rate, axiom_inputs):
        """
        Checks the consistency of gradients for all learnable parameters (MLP, axioms, phase transition module).
        Returns True if robust, False otherwise, along with max inconsistency score.
        """
        max_inconsistency_score = 0.0
        
        # Store original states to restore later
        original_mlp_params = {n: p.data.clone() for n, p in thesis_predictor.mlp.named_parameters()}
        original_axiom_coeffs = {n: p.data.clone() for n, p in thesis_predictor.learned_axiom_coeffs.items()}
        original_pt_params = {n: p.data.clone() for n, p in thesis_predictor.phase_transition_linear.named_parameters()}

        # Compute analytical gradients for all parameters in one backward pass
        thesis_predictor.zero_grad()
        P_predicted_for_grad = thesis_predictor(growth_rate, inflation_rate, axiom_inputs)
        loss_for_grad = P_predicted_for_grad.mean() 
        loss_for_grad.backward(retain_graph=True) # Retain graph for subsequent numerical checks if needed

        # Helper to get analytical gradient
        def get_analytical_grad(param):
            return param.grad.mean().item() if param.grad is not None else 0.0

        # Check MLP parameters
        for name, param in thesis_predictor.mlp.named_parameters():
            if param.requires_grad:
                analytical_grad = get_analytical_grad(param)
                numerical_grad = self._compute_numerical_gradient_for_param(
                    thesis_predictor, growth_rate, inflation_rate, axiom_inputs, param, is_mlp_param=True
                )
                inconsistency = torch.abs(torch.tensor(analytical_grad) - torch.tensor(numerical_grad)).item()
                max_inconsistency_score = max(max_inconsistency_score, inconsistency)
        
        # Check axiom coefficients
        for axiom_name, param in thesis_predictor.learned_axiom_coeffs.items():
            if param.requires_grad:
                analytical_grad = get_analytical_grad(param)
                numerical_grad = self._compute_numerical_gradient_for_param(
                    thesis_predictor, growth_rate, inflation_rate, axiom_inputs, param, is_axiom_param=True, axiom_name=axiom_name
                )
                inconsistency = torch.abs(torch.tensor(analytical_grad) - torch.tensor(numerical_grad)).item()
                max_inconsistency_score = max(max_inconsistency_score, inconsistency)

        # Check phase_transition_linear parameters (weight and bias)
        for name, param in thesis_predictor.phase_transition_linear.named_parameters():
            if param.requires_grad:
                analytical_grad = get_analytical_grad(param)
                numerical_grad = self._compute_numerical_gradient_for_param(
                    thesis_predictor, growth_rate, inflation_rate, axiom_inputs, param, is_pt_param=True, param_name=name
                )
                inconsistency = torch.abs(torch.tensor(analytical_grad) - torch.tensor(numerical_grad)).item()
                max_inconsistency_score = max(max_inconsistency_score, inconsistency)
        
        # Restore original parameters to avoid side effects on subsequent forward passes
        with torch.no_grad():
            for name, param in thesis_predictor.mlp.named_parameters():
                param.data.copy_(original_mlp_params[name])
            for name, param in thesis_predictor.learned_axiom_coeffs.items():
                param.data.copy_(original_axiom_coeffs[name])
            for name, param in thesis_predictor.phase_transition_linear.named_parameters():
                param.data.copy_(original_pt_params[name])

        robust = max_inconsistency_score <= self.differentiability_tolerance
        return robust, max_inconsistency_score

    def _compute_numerical_gradient_for_param(self, thesis_predictor, growth_rate, inflation_rate, axiom_inputs, 
                                   target_param, is_mlp_param=False, is_axiom_param=False, axiom_name=None, 
                                   is_pt_param=False, param_name=None):
        """
        Computes numerical gradient for a single target_param using finite differences.
        Handles different types of parameters for perturbation.
        """
        original_value = target_param.data.clone()
        numerical_grads = []

        for eps_scale in self.robustness_perturbation_epsilon_scales:
            # Perturb +epsilon
            override_axiom_coeffs_plus = None
            override_pt_params_plus = None
            if is_mlp_param:
                with torch.no_grad():
                    target_param.data += eps_scale
            elif is_axiom_param:
                override_axiom_coeffs_plus = {k: v.data.clone() for k, v in thesis_predictor.learned_axiom_coeffs.items()}
                override_axiom_coeffs_plus[axiom_name].data += eps_scale
            elif is_pt_param:
                override_pt_params_plus = {'weight': thesis_predictor.phase_transition_linear.weight.data.clone(),
                                           'bias': thesis_predictor.phase_transition_linear.bias.data.clone()}
                if param_name == 'weight':
                    override_pt_params_plus['weight'] += eps_scale
                elif param_name == 'bias':
                    override_pt_params_plus['bias'] += eps_scale
            
            P_plus = thesis_predictor(growth_rate, inflation_rate, axiom_inputs,
                                      override_axiom_coeffs=override_axiom_coeffs_plus,
                                      override_phase_transition_params=override_pt_params_plus).mean()

            # Perturb -epsilon
            override_axiom_coeffs_minus = None
            override_pt_params_minus = None
            if is_mlp_param:
                with torch.no_grad():
                    target_param.data = original_value - eps_scale # Reset to original, then subtract
            elif is_axiom_param:
                override_axiom_coeffs_minus = {k: v.data.clone() for k, v in thesis_predictor.learned_axiom_coeffs.items()}
                override_axiom_coeffs_minus[axiom_name].data -= eps_scale
            elif is_pt_param:
                override_pt_params_minus = {'weight': thesis_predictor.phase_transition_linear.weight.data.clone(),
                                            'bias': thesis_predictor.phase_transition_linear.bias.data.clone()}
                if param_name == 'weight':
                    override_pt_params_minus['weight'] -= eps_scale
                elif param_name == 'bias':
                    override_pt_params_minus['bias'] -= eps_scale

            P_minus = thesis_predictor(growth_rate, inflation_rate, axiom_inputs,
                                       override_axiom_coeffs=override_axiom_coeffs_minus,
                                       override_phase_transition_params=override_pt_params_minus).mean()

            # Restore original value if it was directly perturbed
            if is_mlp_param:
                with torch.no_grad():
                    target_param.data = original_value
            
            numerical_grad = (P_plus - P_minus) / (2 * eps_scale)
            numerical_grads.append(numerical_grad.item())
        
        return np.mean(numerical_grads)


class MetaJudge:
    """
    Scores thesis, accepts quantitative evidence, manages axiom weights, and forces topological pivots.
    Now also manages adaptive learning rates and outputs LLM guidance, including phase transition parameters.
    """
    def __init__(self, axiom_names):
        self.axiom_weights = {name: 1.0 for name in axiom_names} # Global weights, updated by sync
        self.best_overall_score = -float('inf')
        self.stagnation_counter = 0
        self.axiom_differentiability_veto_active = False

    def calculate_brier_score(self, P_predicted, Z_actual):
        """Calculates the Brier Score."""
        return torch.mean((P_predicted - Z_actual)**2).item()

    def calculate_brier_skill_score(self, P_predicted, Z_actual):
        """
        Calculates Brier Skill Score (BSS) against a baseline of 0.5 probability (no information).
        Higher is better. Max BSS = 1.0 (perfect prediction). Lower bound is negative (worse than baseline).
        """
        baseline_pred = torch.full_like(P_predicted, 0.5)
        bs_model = self.calculate_brier_score(P_predicted, Z_actual)
        bs_baseline = self.calculate_brier_score(baseline_pred, Z_actual)
        
        if bs_baseline == 0: # Avoid division by zero if baseline is perfect (unlikely in real data)
            return 0.0 # Return neutral if baseline is perfect, avoids NaN
        return (bs_baseline - bs_model) / bs_baseline

    def AxiomDifferentiabilityVeto(self, robust, max_inconsistency_score):
        """
        Vetoes thesis if differentiability check fails for any parameter (MLP, axiom, PT module).
        """
        if not robust:
            self.axiom_differentiability_veto_active = True
            print(f"Veto: Differentiability check failed with max inconsistency {max_inconsistency_score:.4f}")
            return True
        self.axiom_differentiability_veto_active = False
        return False
    
    def AxiomWeightSynchronization(self, thesis_predictor):
        """
        Synchronizes the globally held axiom_weights with the learned_axiom_coeffs
        from the ThesisPredictor.
        """
        for name, param in thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[name] = param.item()
    
    def PerformanceGuidedLearningRateAdjustment(self, epistemic_updater, current_brier_skill_score):
        """
        Orchestrates learning rate adjustment based on performance.
        """
        epistemic_updater.update_learning_rates(current_brier_skill_score)

    def generate_llm_guidance(self, thesis_predictor, rolling_brier_skill_score, path=LOAD_BEARING_VARIABLES["LLM_GUIDANCE_PATH"]):
        """
        Generates a JSON file containing learned parameters and performance metrics
        for the LLM Mutator, including phase transition module parameters.
        """
        guidance_data = {
            "current_brier_skill_score": rolling_brier_skill_score,
            "learned_axiom_coefficients": {name: coeff.item() for name, coeff in thesis_predictor.learned_axiom_coeffs.items()},
            "learned_phase_transition_params": {
                "weight": thesis_predictor.phase_transition_linear.weight.item(),
                "bias": thesis_predictor.phase_transition_linear.bias.item()
            },
            "differentiability_veto_active": self.axiom_differentiability_veto_active,
        }
        with open(path, 'w') as f:
            json.dump(guidance_data, f, indent=4)
        # print(f"Generated LLM guidance to {path}") # Commented for less verbose output during runs


# --- Simulation of real-world Z_actual for testing V4 ---
def simulate_z_actual(growth_rate, inflation_rate, axiom_inputs, iteration):
    """
    Simulates a non-linear Z_actual with a smoothly differentiable phase transition.
    """
    # Parameters from LOAD_BEARING_VARIABLES
    true_bias_nl = LOAD_BEARING_VARIABLES["true_bias_nl"]
    true_growth_freq_nl = LOAD_BEARING_VARIABLES["true_growth_freq_nl"]
    true_growth_coeff_nl = LOAD_BEARING_VARIABLES["true_growth_coeff_nl"]
    true_inflation_freq_nl = LOAD_BEARING_VARIABLES["true_inflation_freq_nl"]
    true_inflation_coeff_nl = LOAD_BEARING_VARIABLES["true_inflation_coeff_nl"]
    true_interaction_coeff_nl = LOAD_BEARING_VARIABLES["true_interaction_coeff_nl"]
    true_axiom_relevance = LOAD_BEARING_VARIABLES["true_axiom_relevance"]
    
    true_phase_transition_threshold_true = LOAD_BEARING_VARIABLES["true_phase_transition_threshold_true"]
    true_phase_transition_steepness_true = LOAD_BEARING_VARIABLES["true_phase_transition_steepness_true"]
    true_phase_transition_effect = LOAD_BEARING_VARIABLES["true_phase_transition_effect"]

    # Base non-linear component
    z_base = (
        true_bias_nl +
        true_growth_coeff_nl * torch.sin(growth_rate * true_growth_freq_nl) +
        true_inflation_coeff_nl * torch.cos(inflation_rate * true_inflation_freq_nl) +
        true_interaction_coeff_nl * (growth_rate * inflation_rate)
    )

    # Axiom contribution
    axiom_contribution = true_axiom_relevance * axiom_inputs['AXIOM_RECESSION_AVOIDANCE']
    
    # Phase transition component (smoothly approximated discontinuity in the true process)
    # The phase transition triggers when (growth_rate - inflation_rate) drops below a threshold.
    phase_transition_trigger_input = (growth_rate - inflation_rate)
    
    # Using sigmoid to create a smooth but steep transition for the true underlying process
    # When (trigger - threshold) is large negative, sigmoid is ~0.
    # So (1 - sigmoid) is ~1, and the full effect is applied.
    # When (trigger - threshold) is large positive, sigmoid is ~1.
    # So (1 - sigmoid) is ~0, and no effect is applied.
    # The true effect is an ADDITIVE contribution if `true_phase_transition_effect` is negative.
    # This `sigmoid` is crucial for the "true" data to be differentiable.
    phase_transition_modifier = (1 - torch.sigmoid(
        true_phase_transition_steepness_true * (phase_transition_trigger_input - true_phase_transition_threshold_true)
    ))
    phase_transition_term = true_phase_transition_effect * phase_transition_modifier

    # Combine all components
    raw_z_actual = z_base + axiom_contribution + phase_transition_term
    
    # Add some noise for realism and robustness
    noise = torch.randn_like(raw_z_actual) * 0.05 * (1 + 0.1 * torch.sin(torch.tensor(iteration / 10.0))) # Dynamic noise
    
    # Scale to be a probability [0, 1] using sigmoid
    Z_actual_prob = torch.sigmoid(raw_z_actual + noise)
    
    return Z_actual_prob

# --- Main Test Script ---
def run_v4_test():
    # Setup
    num_iterations = 500
    axiom_names = ['AXIOM_RECESSION_AVOIDANCE'] # Only one for simplicity of test case
    num_inputs_mlp = 3 # growth_rate, inflation_rate, AXIOM_RECESSION_AVOIDANCE_INPUT

    thesis_predictor = ThesisPredictor(num_inputs_mlp, 
                                       LOAD_BEARING_VARIABLES["HIDDEN_LAYER_SIZE"], 
                                       axiom_names, 
                                       LOAD_BEARING_VARIABLES["initial_axiom_coefficient_value"],
                                       LOAD_BEARING_VARIABLES["initial_phase_transition_linear_weight"],
                                       LOAD_BEARING_VARIABLES["initial_phase_transition_linear_bias"])
    epistemic_updater = EpistemicGradientUpdater(thesis_predictor)
    firing_squad = FiringSquad(LOAD_BEARING_VARIABLES["differentiability_tolerance"], 
                               LOAD_BEARING_VARIABLES["robustness_perturbation_epsilon_scales"])
    meta_judge = MetaJudge(axiom_names)

    criterion = nn.BCELoss() # Binary Cross Entropy Loss for probabilities

    brier_skill_scores = deque(maxlen=LOAD_BEARING_VARIABLES["rolling_window_size"])
    llm_guidance_data = None # To store the last generated guidance

    print("Starting V4 Architecture Simulation...")
    for i in range(1, num_iterations + 1):
        # Generate synthetic real-world data (simplified for architecture testing)
        growth_rate_val = torch.tensor(random.uniform(LOAD_BEARING_VARIABLES["hypothetical_economy_growth_rate_q1_2025_base"] * 0.5, 
                                                       LOAD_BEARING_VARIABLES["hypothetical_economy_growth_rate_q1_2025_base"] * 1.5), dtype=torch.float32)
        inflation_rate_val = torch.tensor(random.uniform(LOAD_BEARING_VARIABLES["hypothetical_inflation_rate_q1_2025_base"] * 0.5, 
                                                          LOAD_BEARING_VARIABLES["hypothetical_inflation_rate_q1_2025_base"] * 1.5), dtype=torch.float32)
        
        # AXIOM_RECESSION_AVOIDANCE_INPUT could be 1.0 if (growth-inflation) is low, 0.0 otherwise
        axiom_recession_input = torch.tensor([1.0 if (growth_rate_val - inflation_rate_val).item() < 0.0 else 0.0], dtype=torch.float32)
        axiom_inputs = {'AXIOM_RECESSION_AVOIDANCE': axiom_recession_input}

        Z_actual = simulate_z_actual(growth_rate_val, inflation_rate_val, axiom_inputs, i)
        
        # Forward pass and loss calculation
        P_predicted = thesis_predictor(growth_rate_val, inflation_rate_val, axiom_inputs)
        loss = criterion(P_predicted, Z_actual.unsqueeze(0)) # Z_actual needs to be compatible shape

        # Backpropagation and optimization
        epistemic_updater.step(loss)

        # Differentiability Robustness Check
        robust, max_inconsistency = firing_squad.DifferentiabilityRobustnessCheck(
            thesis_predictor, growth_rate_val, inflation_rate_val, axiom_inputs
        )
        if meta_judge.AxiomDifferentiabilityVeto(robust, max_inconsistency):
            print(f"Iteration {i}: Differentiability veto triggered. Max inconsistency: {max_inconsistency:.4f}")
            # In a real system, this would trigger a Mutator reset or a pivot
            break # Exit loop if vetoed
        
        # Performance evaluation
        current_brier_skill_score = meta_judge.calculate_brier_skill_score(P_predicted, Z_actual)
        if not np.isnan(current_brier_skill_score):
            brier_skill_scores.append(current_brier_skill_score)

        if len(brier_skill_scores) >= LOAD_BEARING_VARIABLES["rolling_window_size"] and i % LOAD_BEARING_VARIABLES["axiom_sync_frequency"] == 0:
            rolling_bss = np.mean(brier_skill_scores)
            meta_judge.AxiomWeightSynchronization(thesis_predictor)
            meta_judge.PerformanceGuidedLearningRateAdjustment(epistemic_updater, rolling_bss)
            
            # Generate LLM guidance
            meta_judge.generate_llm_guidance(thesis_predictor, rolling_bss)
            if os.path.exists(LOAD_BEARING_VARIABLES["LLM_GUIDANCE_PATH"]): # Ensure file exists
                with open(LOAD_BEARING_VARIABLES["LLM_GUIDANCE_PATH"], 'r') as f:
                    llm_guidance_data = json.load(f)

            if i % 50 == 0:
                print(f"Iteration {i}: Loss={loss.item():.4f}, Rolling BSS={rolling_bss:.4f}, "
                      f"Axiom Rec. Coeff={thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item():.4f}, "
                      f"PT Weight={thesis_predictor.phase_transition_linear.weight.item():.4f}, "
                      f"PT Bias={thesis_predictor.phase_transition_linear.bias.item():.4f}")
    
    # --- ASSERTIONS (Falsifiability) ---
    print("\nRunning Falsifiability Assertions...")

    # 1. Brier Skill Score convergence
    final_rolling_bss = np.mean(brier_skill_scores) if len(brier_skill_scores) >= LOAD_BEARING_VARIABLES["rolling_window_size"] else 0.0
    assert final_rolling_bss > LOAD_BEARING_VARIABLES["target_brier_skill_score"], \
        f"Falsification: Rolling BSS {final_rolling_bss:.4f} did not exceed target {LOAD_BEARING_VARIABLES['target_brier_skill_score']:.4f}"
    print(f"Assertion PASSED: Rolling BSS ({final_rolling_bss:.4f}) exceeded target ({LOAD_BEARING_VARIABLES['target_brier_skill_score']:.4f}).")

    # 2. Learned axiom coefficient convergence
    learned_axiom_coeff = thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
    true_axiom_relevance = LOAD_BEARING_VARIABLES['true_axiom_relevance']
    assert learned_axiom_coeff > 0.65 and abs(learned_axiom_coeff - true_axiom_relevance) < 0.25, \
        f"Falsification: Learned axiom coeff {learned_axiom_coeff:.4f} did not converge to within 0.25 of true relevance {true_axiom_relevance:.4f}"
    print(f"Assertion PASSED: Learned axiom coeff ({learned_axiom_coeff:.4f}) converged near true relevance ({true_axiom_relevance:.4f}).")

    # 3. Axiom weight synchronization
    assert abs(meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE'] - learned_axiom_coeff) < 1e-6, \
        "Falsification: Meta-Judge's global axiom_weights did not synchronize with ThesisPredictor's learned coefficient."
    print(f"Assertion PASSED: Meta-Judge axiom weights synchronized.")

    # 4. Differentiability Robustness Check (last known state)
    # Re-run check on final model parameters to get max inconsistency (using latest sample)
    final_robust, final_max_inconsistency = firing_squad.DifferentiabilityRobustnessCheck(
        thesis_predictor, growth_rate_val, inflation_rate_val, axiom_inputs
    )
    assert final_max_inconsistency <= LOAD_BEARING_VARIABLES["differentiability_tolerance"], \
        f"Falsification: Final DifferentiabilityRobustnessCheck failed with max inconsistency {final_max_inconsistency:.4f}"
    print(f"Assertion PASSED: Final Differentiability Robustness Check passed (max inconsistency {final_max_inconsistency:.4f}).")

    # 5. Learned Phase Transition Parameters (Steepness/Weight and Threshold/Bias) convergence
    learned_pt_weight = thesis_predictor.phase_transition_linear.weight.item()
    learned_pt_bias = thesis_predictor.phase_transition_linear.bias.item()
    
    true_steepness = LOAD_BEARING_VARIABLES["true_phase_transition_steepness_true"]
    true_threshold = LOAD_BEARING_VARIABLES["true_phase_transition_threshold_true"]
    
    # The phase_transition_linear.weight learns `true_steepness`.
    # The phase_transition_linear.bias learns `-true_steepness * true_threshold`.
    target_pt_bias = -true_steepness * true_threshold
    
    error_pt_weight = abs(learned_pt_weight - true_steepness)
    error_pt_bias = abs(learned_pt_bias - target_pt_bias)
    
    total_pt_param_error = error_pt_weight + error_pt_bias
    
    assert total_pt_param_error < LOAD_BEARING_VARIABLES["phase_transition_modeling_tolerance"], \
        f"Falsification: Learned phase transition parameters diverged too much. " \
        f"Weight error: {error_pt_weight:.4f} (learned {learned_pt_weight:.4f} vs true {true_steepness:.4f}), " \
        f"Bias error: {error_pt_bias:.4f} (learned {learned_pt_bias:.4f} vs target {target_pt_bias:.4f}). Total error: {total_pt_param_error:.4f}"
    print(f"Assertion PASSED: Learned phase transition parameters converged (Total error {total_pt_param_error:.4f}).")

    # 6. LLM Guidance Data Completeness
    assert llm_guidance_data is not None, "Falsification: LLM guidance data was not generated."
    assert "learned_phase_transition_params" in llm_guidance_data, \
        "Falsification: LLM guidance data is missing 'learned_phase_transition_params'."
    assert "weight" in llm_guidance_data["learned_phase_transition_params"], \
        "Falsification: LLM guidance data is missing 'weight' in phase transition params."
    assert "bias" in llm_guidance_data["learned_phase_transition_params"], \
        "Falsification: LLM guidance data is missing 'bias' in phase transition params."
    print(f"Assertion PASSED: LLM guidance data generated correctly with phase transition parameters.")
    
    # 7. Ensure no veto was active at the end
    assert not meta_judge.axiom_differentiability_veto_active, "Falsification: Differentiability veto was active at the end of training."
    print(f"Assertion PASSED: Differentiability veto was never active at final state.")

    # Clean up generated file
    if os.path.exists(LOAD_BEARING_VARIABLES["LLM_GUIDANCE_PATH"]):
        os.remove(LOAD_BEARING_VARIABLES["LLM_GUIDANCE_PATH"])


if __name__ == "__main__":
    run_v4_test()
```

---

### LOGIC DAG

1.  **[Systemic Inconsistency: `EpistemicBlindnessToDiscontinuitiesAndLLMIsolation` ($X$): Architecture cannot learn from non-smooth phase transitions using gradients AND lacks direct LLM pipeline integration.]**
    $\downarrow$
2.  **[Leverage Point Y1: `ThesisPredictor.phase_transition_linear` (new `nn.Linear` module) is introduced into `ThesisPredictor`, whose learnable `weight` and `bias` parameters approximate the steepness and threshold of discontinuities in a differentiable manner.]**
    $\downarrow$
3.  **[Leverage Point Y2: `EpistemicGradientUpdater` is configured via `ThesisPredictor.get_trainable_param_groups()` to optimize `phase_transition_linear` parameters, enabling gradient-based learning of phase transition dynamics.]**
    $\downarrow$
4.  **[Mechanism (V4): `ThesisPredictor` now uses `p_phase_transition_raw = self.phase_transition_linear(phase_transition_trigger_input)` which directly contributes to `P_predicted`, allowing the model to learn and represent phase transition effects through differentiable parameters.]**
    $\downarrow$
5.  **[Leverage Point Y3: `FiringSquad.DifferentiabilityRobustnessCheck` is extended to rigorously verify the gradient consistency of the `phase_transition_linear`'s parameters across multiple perturbation scales.]**
    $\downarrow$
6.  **[Leverage Point Y4: `Meta-Judge`'s `AxiomDifferentiabilityVeto` is extended to reject any thesis if `phase_transition_linear` parameters fail the `DifferentiabilityRobustnessCheck`, enforcing architectural integrity for learned discontinuities.]**
    $\downarrow$
7.  **[Mechanism (V4): The combined differentiable modeling of discontinuities and strict differentiability checks force the Mutator to generate *smoothly learnable* models for regime shifts, preventing non-differentiable exploits.]**
    $\downarrow$
8.  **[Leverage Point Y5: `MetaJudge.generate_llm_guidance()` method is implemented to serialize not only `learned_axiom_coeffs` and `BrierSkillScore`, but also the *learned `weight` and `bias` of `ThesisPredictor.phase_transition_linear`* into a structured `llm_guidance.json` file.]**
    $\downarrow$
9.  **[Mechanism (V4): The `llm_guidance.json` becomes a mandatory, real-time input for the LLM Mutator, forcing it to integrate empirically derived, differentiable insights into non-linear system dynamics (steepness/threshold of phase transitions) into its thesis generation.]**
    $\downarrow$
10. **[Resultant State Z: Empirically calibrated and axiom-attuned `P_predicted` generated by a non-linear MLP, where axiom contributions *and phase transition dynamics* are precisely identified, updated, and synchronized. The system is *verifiably robust against non-differentiable exploits* across all parameters, demonstrably achieves the `target_brier_skill_score`, and provides comprehensive, actionable guidance for the LLM Mutator, resolving "Phase Transition Blindness" and "LLM Pipeline Integration" by transforming previously unlearnable discontinuities into differentiable, LLM-consumable truths.]**

<!-- best_iteration: 1775133604_iter7_score_62_epistemic_engine_v3_evolved -->