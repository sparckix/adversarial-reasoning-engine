import torch
import torch.nn as nn
import torch.optim as optim
import json
import os
import numpy as np

# --- LOAD-BEARING VARIABLES (from above table) ---
# Optimizer Parameters
adam_beta1 = 0.9
adam_beta2 = 0.999
adam_eps = 1e-8

# Learning Rates
INITIAL_LEARNING_RATE_MODEL_PARAMS = 0.005
INITIAL_LEARNING_RATE_AXIOM_COEFFS = 0.02
INITIAL_LEARNING_RATE_PHASE_TRANSITION_PARAMS = 0.01

# Calibration & Score Targets
min_observations_for_calibration = 200
target_brier_skill_score = 0.20
rolling_window_size = 50
differentiability_tolerance = 0.05
robustness_perturbation_epsilon_scales = [0.00001, 0.0001, 0.001]
phase_transition_modeling_tolerance = 0.05

# Model Architecture
HIDDEN_LAYER_SIZE = 8
initial_axiom_coefficient_value = 0.5
initial_steepness_param_value = 1.0
initial_threshold_param_value = 0.0

# System Frequencies
axiom_sync_frequency = 1

# Simulation Baselines
hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03

# True Non-Linear Simulation Parameters for Z_actual
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.8
true_phase_transition_threshold_true = -0.01
true_phase_transition_steepness_true = 200.0
true_phase_transition_effect = -0.3

# Learning Rate Scheduler Parameters
LR_PATIENCE_EPOCHS = 20
LR_DECAY_FACTOR = 0.5
MIN_DELTA_FOR_LR_DECAY = 0.005
MIN_LEARNING_RATE = 1e-5

# LLM Guidance Path
LLM_GUIDANCE_PATH = "llm_guidance.json"

# --- HELPER FUNCTIONS (adapted from V1/V2 context) ---
class AxiomStore:
    def __init__(self):
        self.axioms = {"AXIOM_RECESSION_AVOIDANCE": torch.tensor(initial_axiom_coefficient_value, requires_grad=True)}

    def get_axiom_coefficients(self):
        return {k: v.item() for k, v in self.axioms.items()}

class BrierScore:
    def __init__(self):
        self.predictions = []
        self.truths = []

    def update(self, predicted_prob, true_outcome):
        self.predictions.append(predicted_prob.item())
        self.truths.append(true_outcome.item())

    def calculate_brier_score(self):
        if not self.predictions:
            return 0.5 # Neutral score
        preds = np.array(self.predictions)
        truths = np.array(self.truths)
        return np.mean((preds - truths)**2)

    def calculate_brier_skill_score(self, baseline_score=0.25): # Baseline for 50/50 prediction
        current_bs = self.calculate_brier_score()
        return 1 - (current_bs / baseline_score)

    def get_rolling_brier_skill_score(self, window_size, baseline_score=0.25):
        if len(self.predictions) < window_size:
            return 0.0 # Not enough observations for robust rolling score
        
        preds_window = np.array(self.predictions[-window_size:])
        truths_window = np.array(self.truths[-window_size:])
        
        current_bs = np.mean((preds_window - truths_window)**2)
        return 1 - (current_bs / baseline_score)

# --- NEW V4 COMPONENTS ---
class PhaseTransitionWrapperModule(nn.Module):
    def __init__(self, initial_steepness, initial_threshold):
        super().__init__()
        # These are the parameters we learn directly
        self.steepness_param = nn.Parameter(torch.tensor(initial_steepness, dtype=torch.float32))
        self.threshold_param = nn.Parameter(torch.tensor(initial_threshold, dtype=torch.float32))

    def forward(self, trigger_input):
        # The phase transition effect is modeled as a sigmoid function
        # sigmoid(steepness * (input - threshold))
        # This is the 'raw' value that, when scaled, contributes to P_predicted
        transformed_input = self.steepness_param * (trigger_input - self.threshold_param)
        return transformed_input # This output will be passed through a sigmoid later

class ThesisPredictor(nn.Module):
    def __init__(self, axiom_store: AxiomStore):
        super().__init__()
        self.axiom_store = axiom_store
        
        # Core MLP for non-linear interactions
        self.mlp = nn.Sequential(
            nn.Linear(2 + 1, HIDDEN_LAYER_SIZE), # 2 external inputs (growth, inflation) + 1 axiom
            nn.ReLU(),
            nn.Linear(HIDDEN_LAYER_SIZE, 1)
        )
        
        # Directly learn steepness and threshold for phase transitions
        self.phase_transition_module = PhaseTransitionWrapperModule(
            initial_steepness_param_value,
            initial_threshold_param_value
        )
        
        # Axiom coefficients are now parameters of the ThesisPredictor (for training purposes)
        # These will be synchronized with AxiomStore by Meta-Judge
        self.axiom_coeffs = nn.ParameterDict({
            k: nn.Parameter(v.clone().detach().requires_grad_(True)) for k, v in axiom_store.axioms.items()
        })
        
    def forward(self, growth_rate, inflation_rate):
        # Prepare inputs for MLP
        axiom_input = self.axiom_coeffs["AXIOM_RECESSION_AVOIDANCE"].unsqueeze(0)
        
        # Combine base features and axiom for MLP
        mlp_input = torch.cat([growth_rate.unsqueeze(0), inflation_rate.unsqueeze(0), axiom_input], dim=0).unsqueeze(0)
        
        raw_mlp_output = self.mlp(mlp_input)
        
        # Calculate phase transition trigger input
        phase_transition_trigger_input = growth_rate - inflation_rate
        
        # Get raw phase transition output from the dedicated module
        p_phase_transition_raw = self.phase_transition_module(phase_transition_trigger_input)
        
        # Combine MLP output with phase transition effect and pass through sigmoid for final probability
        # The true_phase_transition_effect is part of the true Z_actual. The model learns to incorporate
        # its own learned phase transition behavior into the probability.
        # For simplicity in this test, let's assume raw_mlp_output is already in a logit-like space.
        # The phase transition module's output directly modifies this logit.
        # We model the actual effect by scaling the learned phase transition raw output.
        
        # The final P_predicted is a sigmoid of the sum of MLP output and the scaled phase transition effect
        # The *magnitude* of the phase transition effect is currently fixed in the simulation, 
        # but the *threshold* and *steepness* are learned.
        # Here, we directly add the phase transition raw output to the logit
        
        # The model's P_predicted should incorporate the learned phase transition behavior.
        # The simulation defines a 'true_phase_transition_effect' (-0.3) that occurs *after* the sigmoid logic.
        # To reflect this, the model's output should be sensitive to the *learned* phase transition.
        
        # Let's adjust this: the raw_mlp_output represents general prediction.
        # The phase transition module's output `p_phase_transition_raw` acts as a logit modifier.
        
        # Example: P_predicted = sigmoid( MLP_output_logit + phase_transition_factor * sigmoid(p_phase_transition_raw) )
        # This structure allows the phase transition to *modify* the overall prediction.
        # A simpler way, consistent with the original idea of adding to P_predicted directly (pre-sigmoid):
        # P_predicted_logit = raw_mlp_output + some_factor * sigmoid(p_phase_transition_raw)
        
        # To align with the original problem statement (P_predicted as output), 
        # let's assume the combined output is directly passed to sigmoid.
        # The phase_transition_module directly outputs the "logit-like" input for the sigmoid step.
        # So we combine raw_mlp_output with this.
        
        # Let's make the model's structure clearer: it predicts a logit, then applies sigmoid.
        # The phase transition effect is modeled as adding to this logit.
        # A fixed scaling factor for the *learned* phase transition magnitude might be needed if it's not learned.
        # For simplicity, let's assume the MLP output and the phase transition output are both logit contributions.
        combined_logit = raw_mlp_output.squeeze(0) + p_phase_transition_raw
        
        P_predicted = torch.sigmoid(combined_logit)
        return P_predicted.squeeze() # Ensure scalar output

    def get_trainable_param_groups(self):
        # Group parameters for different learning rates
        param_groups = [
            {'params': self.mlp.parameters(), 'lr': INITIAL_LEARNING_RATE_MODEL_PARAMS},
            {'params': self.axiom_coeffs.parameters(), 'lr': INITIAL_LEARNING_RATE_AXIOM_COEFFS},
            {'params': self.phase_transition_module.parameters(), 'lr': INITIAL_LEARNING_RATE_PHASE_TRANSITION_PARAMS}
        ]
        return param_groups

# --- ADVERSARIAL CHECKS ---
class FiringSquad:
    def DifferentiabilityRobustnessCheck(self, model: ThesisPredictor, growth_rate, inflation_rate):
        initial_params = {n: p.clone().detach() for n, p in model.named_parameters()}
        gradient_consistency_scores = {}

        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue

            # Calculate reference gradient
            model.zero_grad()
            P_predicted_ref = model(growth_rate, inflation_rate)
            P_predicted_ref.backward() # Assuming scalar output. If tensor, use .sum().backward()
            ref_grad = param.grad.clone() if param.grad is not None else torch.zeros_like(param)
            
            perturbation_gradients = []
            for epsilon in robustness_perturbation_epsilon_scales:
                # Perturb parameter
                param_perturbed = param.clone().detach().requires_grad_(True)
                model_perturbed = ThesisPredictor(model.axiom_store) # Create a fresh model instance
                
                # Manually copy all parameters, ensuring the perturbed one is set
                for n_m, p_m in model_perturbed.named_parameters():
                    if n_m == name:
                        p_m.data = initial_params[name].data + epsilon # Apply perturbation
                    else:
                        p_m.data = initial_params[n_m].data # Copy original

                model_perturbed.zero_grad()
                P_predicted_perturbed = model_perturbed(growth_rate, inflation_rate)
                P_predicted_perturbed.backward()
                
                # For perturbation gradient, we consider the difference in output / epsilon
                # A more robust check involves finite difference approximation of the gradient itself
                # This check ensures that the analytic gradient is consistent with small perturbations
                # (dy/dx ~ (f(x+eps) - f(x-eps))/(2*eps) or (f(x+eps) - f(x))/eps)
                # For now, let's just check if the analytic grad changes drastically.
                
                # More robust check: use finite differences to approximate gradient
                # (f(x+eps) - f(x-eps)) / (2*eps)
                param_plus = param.clone().detach().requires_grad_(True)
                model_plus = ThesisPredictor(model.axiom_store)
                for n_m, p_m in model_plus.named_parameters():
                    if n_m == name: p_m.data = initial_params[name].data + epsilon
                    else: p_m.data = initial_params[n_m].data
                P_plus = model_plus(growth_rate, inflation_rate)

                param_minus = param.clone().detach().requires_grad_(True)
                model_minus = ThesisPredictor(model.axiom_store)
                for n_m, p_m in model_minus.named_parameters():
                    if n_m == name: p_m.data = initial_params[name].data - epsilon
                    else: p_m.data = initial_params[n_m].data
                P_minus = model_minus(growth_rate, inflation_rate)

                # Approximate gradient
                finite_diff_grad = (P_plus - P_minus) / (2 * epsilon)
                perturbation_gradients.append(finite_diff_grad)

            # Compare reference grad with perturbation approximations
            if ref_grad.nelement() == 1: # Scalar gradient
                max_diff = 0
                for fd_grad in perturbation_gradients:
                    max_diff = max(max_diff, abs(ref_grad.item() - fd_grad.item()))
                gradient_consistency_scores[name] = max_diff
            else: # Tensor gradient (e.g., for MLP weights)
                # For complex parameters, comparing absolute difference is harder.
                # Here, we'll simplify to mean absolute difference for conceptual test.
                # A full check would be cosine similarity or other metric for vectors.
                max_mean_diff = 0
                for fd_grad in perturbation_gradients:
                    # To compare, we need to ensure fd_grad is also a tensor.
                    # This finite difference method computes the gradient of output w.r.t the *perturbed parameter*
                    # A better way for vector params would be to take the actual gradients produced by backward for perturbed models
                    # and compare their consistency.
                    # For this test, let's ensure the scalar values of gradient for single parameters (like axiom coeffs, steepness/threshold)
                    # are consistent. For MLP weights/biases, we'll keep it simple for demonstration.
                    pass # Skip complex gradients for now, focus on single-parameter gradients for the prompt's scope

        # Reset model parameters
        for name, param in model.named_parameters():
            param.data = initial_params[name].data
        
        # For this test, we care most about steepness_param, threshold_param and axiom_coeffs
        critical_param_scores = {}
        for name, score in gradient_consistency_scores.items():
            if "steepness_param" in name or "threshold_param" in name or "axiom_coeffs" in name:
                critical_param_scores[name] = score

        max_critical_score = max(critical_param_scores.values()) if critical_param_scores else 0.0
        
        if max_critical_score > differentiability_tolerance:
            print(f"DifferentiabilityRobustnessCheck FAILED: Max critical score {max_critical_score} > tolerance {differentiability_tolerance}")
            print(f"Critical parameter scores: {critical_param_scores}")
            return False, max_critical_score
        return True, max_critical_score

class MetaJudge:
    def __init__(self, axiom_store: AxiomStore):
        self.brier_history = BrierScore()
        self.axiom_store = axiom_store
        self.max_gradient_inconsistency_score = 0.0 # Track max score from FiringSquad

    def evaluate_thesis(self, model: ThesisPredictor, growth_rate, inflation_rate, Z_actual):
        with torch.no_grad():
            P_predicted = model(growth_rate, inflation_rate)
        
        self.brier_history.update(P_predicted, Z_actual)

        # Sync learned axiom coefficients from model back to axiom store
        if len(self.brier_history.predictions) % axiom_sync_frequency == 0:
            for k, v in model.axiom_coeffs.items():
                self.axiom_store.axioms[k] = v.clone().detach().requires_grad_(True)
        
        # Check differentiability
        differentiability_passed, consistency_score = FiringSquad().DifferentiabilityRobustnessCheck(
            model, growth_rate, inflation_rate
        )
        self.max_gradient_inconsistency_score = max(self.max_gradient_inconsistency_score, consistency_score)
        
        if not differentiability_passed:
            raise ValueError("AxiomDifferentiabilityVeto: Thesis rejected due to non-smooth gradients.")

        return P_predicted

    def generate_llm_guidance(self, model: ThesisPredictor):
        llm_guidance_data = {
            "rolling_brier_skill_score": self.brier_history.get_rolling_brier_skill_score(rolling_window_size),
            "learned_axiom_coeffs": {k: v.item() for k, v in model.axiom_coeffs.items()},
            "learned_phase_transition_params": {
                "steepness": model.phase_transition_module.steepness_param.item(),
                "threshold": model.phase_transition_module.threshold_param.item()
            },
            "max_gradient_inconsistency_score": self.max_gradient_inconsistency_score
        }
        with open(LLM_GUIDANCE_PATH, 'w') as f:
            json.dump(llm_guidance_data, f, indent=4)
        print(f"LLM guidance generated at {LLM_GUIDANCE_PATH}")
        return llm_guidance_data

# --- SIMULATION ENVIRONMENT ---
def simulate_z_actual(growth_rate, inflation_rate, axiom_relevance_input):
    """
    Simulates a non-linear Z_actual with phase transition and noise.
    """
    growth_rate_val = growth_rate.item()
    inflation_rate_val = inflation_rate.item()
    axiom_relevance_val = axiom_relevance_input.item() if isinstance(axiom_relevance_input, torch.Tensor) else axiom_relevance_input

    # Base non-linear effects
    base_effect = (
        true_bias_nl
        + true_growth_coeff_nl * np.sin(true_growth_freq_nl * growth_rate_val)
        + true_inflation_coeff_nl * np.cos(true_inflation_freq_nl * inflation_rate_val)
        + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
    )

    # Phase transition effect
    trigger_input = growth_rate_val - inflation_rate_val
    if trigger_input < true_phase_transition_threshold_true:
        # A smooth step function (sigmoid) for the true phase transition
        # We model the true transition as sigmoid(steepness * (trigger - threshold))
        # The 'effect' then scales this.
        phase_transition_logit = true_phase_transition_steepness_true * (trigger_input - true_phase_transition_threshold_true)
        phase_transition_influence = torch.sigmoid(torch.tensor(phase_transition_logit, dtype=torch.float32)).item()
        phase_transition_term = true_phase_transition_effect * phase_transition_influence
    else:
        phase_transition_term = 0.0 # No strong effect above threshold, or a different functional form
        
    # For a sigmoid-like effect over the *entire range* based on true parameters, it would be:
    # phase_transition_logit = true_phase_transition_steepness_true * (trigger_input - true_phase_transition_threshold_true)
    # phase_transition_factor = torch.sigmoid(torch.tensor(phase_transition_logit, dtype=torch.float32)).item()
    # phase_transition_term = true_phase_transition_effect * phase_transition_factor

    # Let's use the explicit sigmoid for the simulation to match how the model learns it
    phase_transition_logit = true_phase_transition_steepness_true * (trigger_input - true_phase_transition_threshold_true)
    phase_transition_factor = torch.sigmoid(torch.tensor(phase_transition_logit, dtype=torch.float32)).item()
    
    # Let's adjust this. If true_phase_transition_effect is a drop, it's usually 0 to effect.
    # The sigmoid output is [0,1]. If threshold is met, it should transition.
    # A simple smooth step:
    phase_transition_contribution = true_phase_transition_effect * phase_transition_factor # This means it scales from 0 to -0.3

    # Axiom contribution (fixed in simulation)
    axiom_contribution = true_axiom_relevance * axiom_relevance_val # If axiom_relevance_input is already 0/1 for binary, otherwise it's a coefficient

    # Combine all terms and apply final sigmoid to get a probability in [0,1]
    # The true Z_actual needs to be a probability.
    # Summing all contributions and passing through sigmoid to get the *true* probability
    true_logit = base_effect + phase_transition_contribution + axiom_contribution
    true_prob = torch.sigmoid(torch.tensor(true_logit, dtype=torch.float32))

    # Add some noise for realism
    noise = torch.randn(1) * 0.05
    noisy_prob = torch.clamp(true_prob + noise, 0.01, 0.99) # Clamp to keep it within reasonable prob range

    return noisy_prob.squeeze()

# --- MAIN TRAINING LOOP (Simplified to demonstrate falsifiability) ---
def run_simulation():
    axiom_store = AxiomStore()
    model = ThesisPredictor(axiom_store)
    meta_judge = MetaJudge(axiom_store)

    # Separate optimizers for different learning rates
    optimizer = optim.Adam(model.get_trainable_param_groups(), eps=adam_eps, betas=(adam_beta1, adam_beta2))
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='max', # We want to maximize Brier Skill Score
        factor=LR_DECAY_FACTOR,
        patience=LR_PATIENCE_EPOCHS,
        min_delta=MIN_DELTA_FOR_LR_DECAY,
        min_lr=MIN_LEARNING_RATE,
        verbose=True
    )

    brier_scores = []
    max_brier_skill_score_achieved = -float('inf')
    
    # Storage for learned parameters to check convergence
    learned_steepness_history = []
    learned_threshold_history = []
    learned_axiom_coeffs_history = []
    gradient_consistency_scores_history = []

    print("Starting V4 Epistemic Engine Simulation...")

    for i in range(min_observations_for_calibration + rolling_window_size): # Enough iterations for calibration and rolling window
        # Simulate real-world inputs (dynamic, for demonstration)
        growth_rate = torch.tensor(hypothetical_economy_growth_rate_q1_2025_base + 0.01 * np.sin(i / 10.0), dtype=torch.float32)
        inflation_rate = torch.tensor(hypothetical_inflation_rate_q1_2025_base - 0.005 * np.cos(i / 15.0), dtype=torch.float32)
        
        # Simulate the true Z_actual based on actual inputs and fixed true axiom relevance
        # For simplicity, let axiom_relevance_input be a constant for simulation's Z_actual generation
        Z_actual = simulate_z_actual(growth_rate, inflation_rate, torch.tensor(true_axiom_relevance, dtype=torch.float32))

        # --- MODEL TRAINING ---
        model.train()
        optimizer.zero_grad()
        P_predicted = model(growth_rate, inflation_rate)
        
        # Loss: Binary Cross-Entropy Loss for probabilities
        loss = nn.functional.binary_cross_entropy(P_predicted, Z_actual)
        loss.backward()
        optimizer.step()

        # --- META-JUDGE EVALUATION ---
        model.eval()
        _ = meta_judge.evaluate_thesis(model, growth_rate, inflation_rate, Z_actual)
        
        current_bss = meta_judge.brier_history.get_rolling_brier_skill_score(rolling_window_size)
        if current_bss > max_brier_skill_score_achieved:
            max_brier_skill_score_achieved = current_bss
        brier_scores.append(current_bss)

        # Learning rate scheduler step
        if i >= min_observations_for_calibration:
            scheduler.step(current_bss)
        
        # Record learned parameters
        learned_steepness_history.append(model.phase_transition_module.steepness_param.item())
        learned_threshold_history.append(model.phase_transition_module.threshold_param.item())
        learned_axiom_coeffs_history.append(model.axiom_coeffs["AXIOM_RECESSION_AVOIDANCE"].item())
        gradient_consistency_scores_history.append(meta_judge.max_gradient_inconsistency_score)


        if (i + 1) % 50 == 0:
            print(f"Iteration {i+1}: Loss = {loss.item():.4f}, Rolling BSS = {current_bss:.4f}")
            print(f"  Learned Steepness: {model.phase_transition_module.steepness_param.item():.4f}, "
                  f"Threshold: {model.phase_transition_module.threshold_param.item():.4f}, "
                  f"Axiom Coeff: {model.axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item():.4f}")
            print(f"  Max Grad Inconsistency: {meta_judge.max_gradient_inconsistency_score:.4f}")

    # Generate final LLM guidance
    final_llm_guidance = meta_judge.generate_llm_guidance(model)
    print("\n--- Simulation Complete ---")

    # --- FALSIFIABILITY ASSERTIONS ---
    final_rolling_bss = meta_judge.brier_history.get_rolling_brier_skill_score(rolling_window_size)
    final_learned_axiom_coeff = model.axiom_coeffs["AXIOM_RECESSION_AVOIDANCE"].item()
    final_learned_steepness = model.phase_transition_module.steepness_param.item()
    final_learned_threshold = model.phase_transition_module.threshold_param.item()
    final_max_gradient_inconsistency = meta_judge.max_gradient_inconsistency_score

    print(f"\nFinal Rolling BSS: {final_rolling_bss:.4f}")
    print(f"Final Learned Axiom Coeff: {final_learned_axiom_coeff:.4f} (True: {true_axiom_relevance})")
    print(f"Final Learned Steepness: {final_learned_steepness:.4f} (True: {true_phase_transition_steepness_true})")
    print(f"Final Learned Threshold: {final_learned_threshold:.4f} (True: {true_phase_transition_threshold_true})")
    print(f"Final Max Gradient Inconsistency: {final_max_gradient_inconsistency:.4f}")

    # Assertion 1: Brier Skill Score
    assert final_rolling_bss > target_brier_skill_score, \
        f"FALSIFICATION: Rolling BSS {final_rolling_bss:.4f} did not exceed target {target_brier_skill_score:.4f}."

    # Assertion 2: Axiom Coefficient Convergence
    assert abs(final_learned_axiom_coeff - true_axiom_relevance) < 0.25, \
        f"FALSIFICATION: Axiom coefficient {final_learned_axiom_coeff:.4f} did not converge close enough to true relevance {true_axiom_relevance}."
    assert final_learned_axiom_coeff > 0.65, \
        f"FALSIFICATION: Axiom coefficient {final_learned_axiom_coeff:.4f} did not meet minimum threshold 0.65."

    # Assertion 3: Steepness Parameter Convergence
    assert abs(final_learned_steepness - true_phase_transition_steepness_true) < 0.05, \
        f"FALSIFICATION: Learned steepness {final_learned_steepness:.4f} did not converge within 0.05 of true steepness {true_phase_transition_steepness_true}."

    # Assertion 4: Threshold Parameter Convergence
    assert abs(final_learned_threshold - true_phase_transition_threshold_true) < 0.05, \
        f"FALSIFICATION: Learned threshold {final_learned_threshold:.4f} did not converge within 0.05 of true threshold {true_phase_transition_threshold_true}."

    # Assertion 5: Combined Phase Transition Modeling Error
    phase_transition_modeling_error = abs(final_learned_steepness - true_phase_transition_steepness_true) + \
                                      abs(final_learned_threshold - true_phase_transition_threshold_true)
    assert phase_transition_modeling_error < phase_transition_modeling_tolerance, \
        f"FALSIFICATION: Combined phase transition modeling error {phase_transition_modeling_error:.4f} exceeded tolerance {phase_transition_modeling_tolerance}."

    # Assertion 6: Differentiability Robustness
    assert final_max_gradient_inconsistency <= differentiability_tolerance, \
        f"FALSIFICATION: Max gradient inconsistency {final_max_gradient_inconsistency:.4f} exceeded tolerance {differentiability_tolerance}."

    # Assertion 7: LLM Guidance File Existence and content
    assert os.path.exists(LLM_GUIDANCE_PATH), \
        f"FALSIFICATION: LLM guidance file not found at {LLM_GUIDANCE_PATH}."
    with open(LLM_GUIDANCE_PATH, 'r') as f:
        guidance_content = json.load(f)
    assert "learned_phase_transition_params" in guidance_content, \
        "FALSIFICATION: LLM guidance missing 'learned_phase_transition_params'."
    assert "steepness" in guidance_content["learned_phase_transition_params"], \
        "FALSIFICATION: LLM guidance missing 'steepness' in phase transition params."
    assert "threshold" in guidance_content["learned_phase_transition_params"], \
        "FALSIFICATION: LLM guidance missing 'threshold' in phase transition params."
    assert abs(guidance_content["learned_phase_transition_params"]["steepness"] - final_learned_steepness) < 1e-6, \
        "FALSIFICATION: LLM guidance steepness parameter mismatch."
    assert abs(guidance_content["learned_phase_transition_params"]["threshold"] - final_learned_threshold) < 1e-6, \
        "FALSIFICATION: LLM guidance threshold parameter mismatch."

    print("\nALL FALSIFIABILITY CHECKS PASSED.")

if __name__ == "__main__":
    run_simulation()