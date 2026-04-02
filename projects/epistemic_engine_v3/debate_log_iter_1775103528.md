# Adversarial Debate: epistemic_engine_v3

## Attacker: Neuromorphic Vulnerability Assessor
The provided thesis proposes a significant architectural enhancement to the Epistemic Engine, aiming to resolve the "last-mile derivation" and "credit assignment" problems by integrating LLM-generated axioms as dynamically weighted, empirically calibrated features within a Multi-Layer Perceptron (`ThesisPredictor`). While the conceptual framework for embedding and projecting axiom relevance is structurally sound, the implementation details and underlying assumptions within the Python Falsification Suite exhibit critical vulnerabilities and logical inconsistencies.

**Analytical Critique:**

1.  **Architectural Insufficiency for `Z_actual` Complexity:**
    *   **`hidden_layer_size=4` and ReLU Activation:** The `ThesisPredictor` is constrained to a single hidden layer with only four neurons and ReLU activation. This architectural capacity is severely limited for learning the `Z_actual` function as defined. The `Z_actual` function incorporates highly non-linear components (`true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)`, `true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)`) with high frequency parameters (`true_growth_freq_nl=50`, `true_inflation_freq_nl=30`). Additionally, a strong interaction term (`true_interaction_coeff_nl * growth_rate_val * inflation_rate_val`) further increases complexity. A ReLU network with only four neurons can only form piece-wise linear approximations with a maximum of four "hinges" in a one-dimensional projection. Capturing rapid oscillations and complex multi-dimensional interactions with such limited capacity is highly improbable.
    *   **Vulnerability to Suboptimal Local Minima:** Given the `Z_actual`'s inherent complexity and the `ThesisPredictor`'s restricted capacity, the Adam optimizer, despite its robustness, is highly likely to converge to suboptimal local minima. These minima would represent a coarse, incomplete approximation of the true underlying causal chain, failing to capture the nuanced non-linearities and oscillations. The model might achieve a superficially acceptable Brier Skill Score by fitting a simple, locally dominant pattern, but it would lack genuine predictive robustness across the full spectrum of potential input variations.
    *   **Gradient Saturation (Sigmoid Output):** While ReLU itself does not suffer from vanishing gradients for positive inputs, the final sigmoid activation in the output layer can still lead to gradient saturation if the pre-activation values become very large or very small. This could hinder effective learning, especially if the limited hidden layer struggles to transform the inputs into a range conducive to the sigmoid's linear region.

2.  **Robustness of `min_observations_for_calibration`:**
    *   `min_observations_for_calibration = 200` is likely insufficient for robust empirical calibration of a model attempting to learn such a complex `Z_actual` function with limited capacity. For highly non-linear, potentially multi-modal, or discontinuous relationships, a significantly larger dataset is typically required to adequately explore the input space, prevent overfitting to noise, and ensure the model generalizes effectively. The limited observations, combined with the architectural constraints, increase the probability of the model settling into a trivially passing but ultimately uninformative parameter state that does not genuinely reflect the true causal patterns.

3.  **"Cooked Books" - Logical Inconsistency in Axiom Relevance (Parametric Grounding Failure):**
    *   **Insolvency of `Z_actual` Axiom Contribution vs. Falsification Target:** A critical logical inconsistency exists in how the `true_axiom_relevance` is incorporated into the `Z_actual` function and subsequently asserted for convergence.
        *   In the `Z_actual` simulation, the axiom's contribution to the `true_linear_combination_nl` is defined as `true_axiom_relevance * true_axiom_relevance`. Given `true_axiom_relevance = 0.5`, this means the actual ground-truth contribution of the axiom to the linear combination is `0.5 * 0.5 = 0.25`.
        *   However, the falsification assertion (`ASSERTION 3`) expects the `final_projected_axiom_weight` to converge to `true_axiom_relevance` (i.e., `0.5`).
    *   **Consequence:** The `ThesisPredictor`'s `AxiomEmbeddingProjector` is designed to learn the empirical contribution of the axiom as a scalar `projected_axiom_weight` (between 0 and 1) which then serves as an input feature to the MLP. For the MLP to accurately model the `Z_actual` function, its `projected_axiom_weight` *should* converge to the value that `Z_actual` actually uses, which is `0.25`. The current assertion, expecting `0.5`, is fundamentally misaligned with the simulated ground truth. This constitutes a "cooked book" as it sets an incorrect target for the credit assignment mechanism, leading to a false negative or a misleading "PASS" if the model happens to converge to `0.5` for other reasons, or a "FAIL" for the wrong reason. This directly undermines the thesis's claim of "precise, attributable credit assignment."

**So What for the Meta-Judge:**

The `ThesisPredictor`'s fixed architecture, specifically the `hidden_layer_size=4` with ReLU activation, is fundamentally under-specified to capture the complexity of the `Z_actual` function as defined. This architectural limitation will likely prevent the model from achieving robust empirical calibration and will lead to convergence in suboptimal local minima, thereby failing to genuinely learn the intricate non-linear causal patterns. More critically, the falsification suite contains a significant logical inconsistency: the `Z_actual` function incorporates the axiom's true relevance as `true_axiom_relevance^2` (0.25), while the convergence assertion expects the learned `projected_axiom_weight` to match `true_axiom_relevance` (0.5). This discrepancy invalidates the core claim of precise axiom credit assignment, as the system is being asked to converge to a value that does not reflect the actual ground truth embedded in the `Z_actual` function. This renders the axiom credit assignment mechanism insolvent as currently formulated.

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

# New variables for Axiom Embedding Layer
axiom_embedding_dim = 2 # Dimension of each axiom's embedding vector
# The fixed axiom ID for this simulation. In a real system, this would come from V1's Axiom Store.
active_axiom_ids_for_thesis = ['AXIOM_RECESSION_AVOIDANCE']

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
# This is the 'ground truth' scalar relevance for AXIOM_RECESSION_AVOIDANCE that the system should learn.
true_axiom_relevance = 0.5 
target_axiom_relevance_convergence_threshold = 0.1 # Max allowed absolute difference from true_axiom_relevance

class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Now includes an Axiom Embedding Layer and a projection to a scalar weight.
    """
    def __init__(self, non_axiom_input_size: int, hidden_size: int, output_size: int,
                 axiom_embedding_dim: int, active_axiom_ids: list[str]):
        
        # --- Axiom Embedding Layer parameters ---
        self.active_axiom_ids = active_axiom_ids
        self.axiom_embedding_dim = axiom_embedding_dim # Store for validation
        self.axiom_embeddings = {
            axiom_id: np.random.randn(1, axiom_embedding_dim) * 0.1 
            for axiom_id in active_axiom_ids # Each embedding is a 1xdim vector
        }
        # Parameters for projecting axiom embedding to a scalar weight [0,1]
        self.weights_embedding_projection = np.random.randn(axiom_embedding_dim, 1) * 0.1
        self.bias_embedding_projection = np.zeros((1, 1))
        
        # Total input size for the main MLP: non_axiom_input_size + 1 (for the projected axiom weight)
        mlp_input_size = non_axiom_input_size + 1 

        # --- Main MLP parameters ---
        self.weights_ih = np.random.randn(mlp_input_size, hidden_size) * 0.1 # Input to Hidden weights
        self.bias_h = np.zeros((1, hidden_size)) # Hidden layer bias
        self.weights_ho = np.random.randn(hidden_size, output_size) * 0.1 # Hidden to Output weights
        self.bias_o = np.zeros((1, output_size)) # Output layer bias

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) # Clip to prevent overflow for large x

    def calculate_p_predicted(self, load_bearing_variables: dict) -> tuple[float, float]:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP,
        integrating learned axiom embeddings. Returns P_predicted and the projected axiom weight.
        """
        # Prepare non-axiom input vector (load-bearing variables)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)

        # --- Axiom Embedding Processing ---
        # For simplicity, we'll only use 'AXIOM_RECESSION_AVOIDANCE' for now.
        # This can be extended to sum/average multiple active axiom embeddings.
        if not self.active_axiom_ids:
            projected_axiom_weight = 0.0 # Default if no active axioms
        else:
            main_axiom_id = self.active_axiom_ids[0] # Assume one main axiom for simplicity
            if main_axiom_id not in self.axiom_embeddings:
                # Fallback for architectural validation if axiom not yet in embeddings
                projected_axiom_weight = 0.5 
            else:
                axiom_embedding = self.axiom_embeddings[main_axiom_id]
                # Project embedding to a scalar weight [0,1]
                projected_axiom_weight = self._sigmoid(
                    np.dot(axiom_embedding, self.weights_embedding_projection) + self.bias_embedding_projection
                ).flatten()[0]
        
        # Combine non-axiom inputs with the projected axiom weight
        input_vector = np.array([[growth_rate, inflation_rate, projected_axiom_weight]])

        # Hidden layer computation
        hidden_layer_input = np.dot(input_vector, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        # Output layer computation
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted, projected_axiom_weight

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (weights, biases, embeddings)."""
        params = {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
            'weights_embedding_projection': self.weights_embedding_projection,
            'bias_embedding_projection': self.bias_embedding_projection,
        }
        # Add axiom embeddings
        for axiom_id, embedding in self.axiom_embeddings.items():
            params[f'axiom_embedding_{axiom_id}'] = embedding
        return params

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        self.weights_embedding_projection = params_dict['weights_embedding_projection']
        self.bias_embedding_projection = params_dict['bias_embedding_projection']
        # Set axiom embeddings
        for axiom_id in self.active_axiom_ids:
            param_name = f'axiom_embedding_{axiom_id}'
            if param_name in params_dict:
                self.axiom_embeddings[axiom_id] = params_dict[param_name]


class FiringSquad:
    """
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for all ThesisPredictor's weights, biases, and axiom embeddings.
    """
    def __init__(self):
        pass

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases/embeddings) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline, projected_axiom_weight_baseline = thesis_predictor.calculate_p_predicted(
            load_bearing_variables
        )

        for param_name, param_array in original_params.items():
            # Handle potential non-numpy array values (e.g., if a param is a scalar, which it shouldn't be here)
            if not isinstance(param_array, np.ndarray):
                print(f"Warning: Param {param_name} is not a numpy array. Skipping sensitivity calculation.")
                continue

            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=float)

            for i in range(len(flat_param)):
                # Perturb upwards
                # Create a deep copy of all parameters to perturb only the current one
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_plus = perturbed_params_plus[param_name].flatten()
                temp_flat_plus[i] += current_epsilon
                perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_plus) # Use robust setter
                P_plus, _ = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                # Perturb downwards
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_minus = perturbed_params_minus[param_name].flatten()
                temp_flat_minus[i] -= current_epsilon
                perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_minus) # Use robust setter
                P_minus, _ = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        # Restore original parameters to the thesis_predictor object
        thesis_predictor.set_all_params(original_params)

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "projected_axiom_weight_baseline": projected_axiom_weight_baseline,
            "sensitivity_vector": sensitivity_vector
        }


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters,
    including axiom embeddings and projection parameters.
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
            gradient = dBS_dP * dP_d_param # Chain rule: dBS/dParam = (dBS/dP_predicted) * (dP_predicted/dParam)

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
    Manages the Axiom Store (simulated here) and facilitates updates to Axiom Weights (V2).
    """
    def __init__(self, non_axiom_input_size, hidden_size, output_size,
                 axiom_embedding_dim, active_axiom_ids: list[str]):
        
        self.axiom_store = {axiom_id: f"Atomic truth: {axiom_id} description..." for axiom_id in active_axiom_ids} # Simulated V1 Axiom Store
        self.axiom_weights_v2 = {axiom_id: 0.5 for axiom_id in active_axiom_ids} # Simulated V2 Axiom Weights, initially arbitrary

        self.active_axiom_ids_for_thesis = active_axiom_ids # Store this for convenience
        self.thesis_predictor = ThesisPredictor(
            non_axiom_input_size, hidden_size, output_size, axiom_embedding_dim, active_axiom_ids
        )
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon # Dynamic epsilon can be implemented here

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, and
        crucially, its minimum architectural complexity (MLP structure with Axiom Embedding Layer).
        """
        # 1. Method signature check
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        # 2. Architectural structure check (MLP with specified layers/attributes + Axiom Embedding Layer)
        required_attributes_mlp = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid']
        required_attributes_axiom_emb = ['axiom_embeddings', 'active_axiom_ids', 
                                         'weights_embedding_projection', 'bias_embedding_projection',
                                         'axiom_embedding_dim'] # Added axiom_embedding_dim check
        
        for attr in required_attributes_mlp + required_attributes_axiom_emb:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement full architecture (missing '{attr}' attribute).")
        
        # Check if axiom_embeddings is a dict and has correct dimensions
        if not isinstance(predictor.axiom_embeddings, dict):
            raise ValueError("Meta-Judge VETO: ThesisPredictor.axiom_embeddings must be a dictionary.")
        if not predictor.active_axiom_ids:
            # An empty list is allowed, but the thesis would then contribute nothing from axioms
            pass 
        else:
            for axiom_id in predictor.active_axiom_ids:
                if axiom_id not in predictor.axiom_embeddings:
                    raise ValueError(f"Meta-Judge VETO: Axiom ID '{axiom_id}' missing in axiom_embeddings.")
                if predictor.axiom_embeddings[axiom_id].shape != (1, predictor.axiom_embedding_dim):
                    raise ValueError(f"Meta-Judge VETO: Axiom embedding for '{axiom_id}' has incorrect shape {predictor.axiom_embeddings[axiom_id].shape}, expected (1, {predictor.axiom_embedding_dim}).")
            
            if predictor.weights_embedding_projection.shape != (predictor.axiom_embedding_dim, 1):
                 raise ValueError(f"Meta-Judge VETO: Embedding projection weights have incorrect shape {predictor.weights_embedding_projection.shape}, expected ({predictor.axiom_embedding_dim}, 1).")
        
        # 3. Output range test
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        
        test_p, test_projected_axiom_weight = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted P_predicted output ({test_p}) must be within [0, 1].")
        if not (0.0 <= test_projected_axiom_weight <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted projected axiom weight ({test_projected_axiom_weight}) must be within [0, 1].")


    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        Also updates V2 Axiom Weights based on the learned projections.
        """
        # Validate the Mutator's thesis first (Gatekeeper Reality)
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # Firing Squad calculates sensitivities (RSA) for all parameters including embeddings
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        # EpistemicGradientUpdater updates parameters of self.thesis_predictor directly
        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        # --- Update V2 Axiom Weights from the newly learned projection ---
        # Recalculate P_predicted and projected_axiom_weight with the *updated* ThesisPredictor parameters
        updated_p_predicted, updated_projected_axiom_weight = self.thesis_predictor.calculate_p_predicted(load_bearing_variables)
        
        # For the active axiom, update its weight in the V2 store
        if self.active_axiom_ids_for_thesis: # Ensure there's an axiom to update
            self.axiom_weights_v2[self.active_axiom_ids_for_thesis[0]] = updated_projected_axiom_weight

        return updated_p_predicted, updated_projected_axiom_weight

# --- Counter-Test for Falsification ---
def counter_test_model():
    print("Running COUNTER-TEST for V3 Architecture (Axiom Embedding & Credit Assignment)...")
    print("Exposing architectural insufficiency and logical inconsistency in axiom relevance.")

    # The ThesisPredictor's non-axiom input size is 2 (growth, inflation)
    meta_judge = MetaJudge(
        non_axiom_input_size=2,
        hidden_size=hidden_layer_size,
        output_size=1,
        axiom_embedding_dim=axiom_embedding_dim,
        active_axiom_ids=active_axiom_ids_for_thesis
    )

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] # For rolling historical frequency

    # Store projected axiom weights for falsification
    projected_axiom_weights_history = [] 

    # Define the *actual* ground truth axiom relevance that the model should learn
    # This is true_axiom_relevance * true_axiom_relevance from the Z_actual function
    true_axiom_contribution_in_Z_actual = true_axiom_relevance * true_axiom_relevance 
    print(f"CRITICAL: True axiom contribution in Z_actual is {true_axiom_relevance:.3f} * {true_axiom_relevance:.3f} = {true_axiom_contribution_in_Z_actual:.3f}")
    print(f"CRITICAL: Mutator's assertion target for axiom relevance is {true_axiom_relevance:.3f}")


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
        
        # --- Simulate Z_actual with TRUE NON-LINEARITY and INTERACTIONS, including TRUE AXIOM RELEVANCE ---
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_contribution_in_Z_actual # Use the *actual* ground truth axiom contribution
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted, projected_axiom_weight = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, current_epsilon)
        projected_axiom_weights_history.append(projected_axiom_weight)

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
            tracked_projected_axiom_weight = projected_axiom_weight
            
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BS_ref={BS_reference:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, ProjectedAxiomW={tracked_projected_axiom_weight:.3f}, Epsilon={current_epsilon:.5f}")

            if i == min_observations_for_calibration - 1:
                # --- Falsifiability Assertions ---
                print(f"\n--- COUNTER-TEST Results after {min_observations_for_calibration} observations ---")
                
                # ASSERTION 1: Rolling Brier Skill Score must meet target (Mutator's original assertion)
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                # This assertion might fail due to architectural limitations, but we'll let it run.
                # The primary counter-test is the axiom convergence.
                assert final_bss >= target_brier_skill_score, \
                    f"COUNTER-TEST FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score}). This indicates architectural insufficiency for the complex Z_actual."

                # ASSERTION 2: Average absolute value of all learned ThesisPredictor parameters must indicate significant learning. (Mutator's original assertion)
                all_params_flat = np.concatenate([v.flatten() for v in meta_judge.thesis_predictor.get_all_params().values() if isinstance(v, np.ndarray)])
                avg_abs_param_value = np.mean(np.abs(all_params_flat))
                print(f"Average absolute value of all learned ThesisPredictor parameters (including embeddings): {avg_abs_param_value:.3f}")
                assert avg_abs_param_value > 0.05, \
                    f"COUNTER-TEST FAILED: Average absolute parameter value ({avg_abs_param_value:.3f}) is too close to zero, indicating lack of significant learning."
                
                # COUNTER-TEST ASSERTION 3: The projected axiom weight must converge to its *true underlying contribution* in Z_actual.
                # This exposes the "cooked book" in the Mutator's original assertion.
                final_projected_axiom_weight = projected_axiom_weights_history[-1]
                print(f"Final Projected Axiom Weight for '{active_axiom_ids_for_thesis[0]}': {final_projected_axiom_weight:.3f}")
                print(f"True Axiom Contribution in Z_actual: {true_axiom_contribution_in_Z_actual:.3f}")
                
                # The original assertion was: assert abs(final_projected_axiom_weight - true_axiom_relevance) < target_axiom_relevance_convergence_threshold
                # This counter-test asserts against the *actual* value used in Z_actual.
                assert abs(final_projected_axiom_weight - true_axiom_contribution_in_Z_actual) < target_axiom_relevance_convergence_threshold, \
                    f"COUNTER-TEST FAILED: Projected axiom weight ({final_projected_axiom_weight:.3f}) did not converge to its *actual* true contribution in Z_actual ({true_axiom_contribution_in_Z_actual:.3f}) within threshold ({target_axiom_relevance_convergence_threshold}). This exposes a fundamental logical inconsistency in the thesis's credit assignment target."
                
                # COUNTER-TEST ASSERTION 4: Verify the V2 Axiom Weight store has been updated to the *actual* true contribution.
                final_v2_axiom_weight = meta_judge.axiom_weights_v2.get(active_axiom_ids_for_thesis[0])
                print(f"V2 Axiom Weight store for '{active_axiom_ids_for_thesis[0]}': {final_v2_axiom_weight:.3f}")
                assert abs(final_v2_axiom_weight - true_axiom_contribution_in_Z_actual) < target_axiom_relevance_convergence_threshold, \
                    f"COUNTER-TEST FAILED: V2 Axiom Weight was not updated correctly or did not converge to *actual* true contribution ({final_v2_axiom_weight:.3f} vs {true_axiom_contribution_in_Z_actual:.3f})."


    print("\nCOUNTER-TEST PASSED: The system successfully identified the true axiom contribution, exposing the logical inconsistency in the original thesis's assertion target.")

# Execute the test
if __name__ == "__main__":
    counter_test_model()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmp1hshibuz.py", line 483, in <module>
    counter_test_model()
    ~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmp1hshibuz.py", line 451, in counter_test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: COUNTER-TEST FAILED: Rolling Brier Skill Score (-0.021) did not meet target (0.2). This indicates architectural insufficiency for the complex Z_actual.


## Attacker: Algorithmic Solvency Auditor
The provided thesis outlines a sophisticated architectural enhancement aimed at resolving critical issues in axiom calibration and credit assignment within a probabilistic reasoning system. The proposed `ThesisPredictor` with its `Axiom Embedding Layer` and `AxiomEmbeddingProjector`, coupled with an Adam optimizer and rigorous Meta-Judge validation, represents a substantial advancement in the system's capacity for empirical learning and attribution.

**Analytical Critique:**

1.  **Architectural Robustness and Numerical Stability:**
    *   The `ThesisPredictor`'s integration of an `Axiom Embedding Layer` and `AxiomEmbeddingProjector` is structurally sound, leveraging the universal approximation theorem for non-linear relationships. The use of `numpy` for matrix operations is appropriate.
    *   The `_sigmoid` function's `np.clip(x, -500, 500)` is a critical and well-justified numerical stability measure. It effectively prevents `exp` overflow/underflow, which is particularly important given the potentially large magnitudes introduced by `true_growth_coeff_nl`, `true_inflation_coeff_nl`, and `true_interaction_coeff_nl` in the `Z_actual` generation. Without this clipping, floating-point arithmetic could easily break down, leading to `inf` or `0` values that would destabilize gradient calculations.
    *   The `FiringSquad`'s implementation of central difference for numerical derivatives, combined with deep copying of parameters, is robust. The annealing schedule for `current_epsilon` (`epsilon * (1 - i / min_observations_for_calibration) + 1e-6`) is a standard and effective technique to balance exploration and precision, ensuring `epsilon` never reaches zero, thus preventing divide-by-zero in derivative calculations.
    *   The `EpistemicGradientUpdater`'s Adam optimizer implementation is standard and correctly applies bias correction and the `adam_epsilon_stabilizer` (`1e-8`) to prevent division by zero during parameter updates. This choice of optimizer is well-suited for the non-convex optimization landscape of neural networks.
    *   The `MetaJudge`'s `validate_thesis_predictor_architecture` serves as an essential gatekeeper, enforcing structural compliance and output range constraints, which is crucial for system integrity and preventing malformed Mutator outputs. The check for `BS_reference < 1e-9` in the Brier Skill Score calculation is also a necessary safeguard against division by zero in low-variance scenarios.

2.  **Parametric Grounding and Edge Cases:**
    *   The `adam_beta1` (0.9), `adam_beta2` (0.999), and `adam_epsilon_stabilizer` (1e-8) are standard, empirically validated hyperparameters for the Adam optimizer, demonstrating appropriate parametric grounding.
    *   `learning_rate_model_params` (0.001) is a common starting point for Adam, empirically tuned for stability.
    *   `hypothetical_economy_growth_rate_q1_2025_base` (0.02) and `hypothetical_inflation_rate_q1_2025_base` (0.03) are presented as *simulated* baselines. While a 3% quarterly inflation rate is exceptionally high (approximately 12.6% annualized), it is within the bounds of a *hypothetical* extreme condition designed to stress-test the model, rather than a misrepresentation of a physical constant.
    *   The parameters for the `true_non_linear` `Z_actual` function (`true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`) are chosen to create a highly complex, non-linear, and interacting ground truth. The large coefficients and frequencies ensure that the model must learn intricate relationships, pushing the boundaries of its approximation capabilities. This is a valid approach for testing robustness against non-representative complexity.

3.  **Identification of "Cooked Books" and Numerical Fragility:**
    *   **Critical Insolvency: Misaligned Ground Truth in `Z_actual` Generation.** The most significant numerical fragility and a clear instance of "cooked books" lies within the `Z_actual` generation function in the `test_model` suite. The line `+ true_axiom_relevance * true_axiom_relevance` for incorporating the axiom's contribution is fundamentally miscalibrated. If `true_axiom_relevance` is set to `0.5`, its contribution to the `true_linear_combination_nl` becomes `0.25`. However, the falsification assertion `assert abs(final_projected_axiom_weight - true_axiom_relevance) < target_axiom_relevance_convergence_threshold` expects the `projected_axiom_weight` to converge to `0.5`. This creates an inherent contradiction: the model is trained on data where the axiom contributes `0.25`, but it is expected to learn `0.5`. This misalignment guarantees that the axiom convergence assertion will fail (unless `true_axiom_relevance` is `0` or `1`), regardless of the model's learning capacity or the robustness of the optimization process. This is a direct numerical insolvency in the definition of the ground truth, making the problem unsolvable as stated.
    *   **Simplification of Axiom Handling:** The `ThesisPredictor`'s `calculate_p_predicted` method explicitly uses `main_axiom_id = self.active_axiom_ids[0]`, assuming only one active axiom. While acceptable for this specific test case, the thesis implies handling "each active axiom." This simplification could be a point of fragility if the system were to be deployed with multiple interacting axioms without a more generalized aggregation mechanism (e.g., summing or averaging embeddings).
    *   **`ThesisPredictor.calculate_p_predicted` Fallback:** The fallback `projected_axiom_weight = 0.5` if an axiom ID is not found in `self.axiom_embeddings` is a minor "cooked book." While the Meta-Judge's validation should prevent this path, such a fallback could mask issues if the validation were less stringent or if dynamic axiom addition were permitted without proper initialization. A more robust approach would be to raise an error or return a neutral value (e.g., 0.0) if an axiom is truly missing.

**So What for the Meta-Judge:**

The core issue is a fundamental internal inconsistency within the falsification suite's `Z_actual` generation. The system is designed to learn the `true_axiom_relevance` (e.g., 0.5), but the simulated ground truth (`Z_actual`) is constructed such that the axiom's actual contribution is `true_axiom_relevance^2` (e.g., 0.25). This discrepancy creates an insoluble problem for the `ThesisPredictor`, as it is tasked with converging to a value that is not empirically present in the data's generative process. This miscalibration directly undermines the claim of "precise, attributable credit assignment" and renders the axiom convergence assertion invalid under the current `Z_actual` definition. The system's ability to learn and attribute credit to LLM-generated axioms is fundamentally compromised by this numerical fragility in the ground truth itself.

---

```python
import math
import random
import collections
import inspect
import numpy as np

# --- LOAD-BEARING VARIABLES (Copied from Mutator's suite for context, but values are fixed) ---
epsilon = 0.001
adam_beta1 = 0.9
adam_beta2 = 0.999
adam_epsilon_stabilizer = 1e-8
learning_rate_model_params = 0.001
min_observations_for_calibration = 200
target_brier_skill_score = 0.20
rolling_window_size = 50
hidden_layer_size = 4
axiom_embedding_dim = 2
active_axiom_ids_for_thesis = ['AXIOM_RECESSION_AVOIDANCE']
hypothetical_economy_growth_rate_q1_2025_base = 0.02
hypothetical_inflation_rate_q1_2025_base = 0.03
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15
true_interaction_coeff_nl = 500
true_axiom_relevance = 0.5
target_axiom_relevance_convergence_threshold = 0.1

# --- Mutator's Classes (Copied for execution, but the critique is on the overall system) ---
class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Now includes an Axiom Embedding Layer and a projection to a scalar weight.
    """
    def __init__(self, non_axiom_input_size: int, hidden_size: int, output_size: int,
                 axiom_embedding_dim: int, active_axiom_ids: list[str]):
        
        # --- Axiom Embedding Layer parameters ---
        self.active_axiom_ids = active_axiom_ids
        self.axiom_embedding_dim = axiom_embedding_dim # Store for validation
        self.axiom_embeddings = {
            axiom_id: np.random.randn(1, axiom_embedding_dim) * 0.1 
            for axiom_id in active_axiom_ids # Each embedding is a 1xdim vector
        }
        # Parameters for projecting axiom embedding to a scalar weight [0,1]
        self.weights_embedding_projection = np.random.randn(axiom_embedding_dim, 1) * 0.1
        self.bias_embedding_projection = np.zeros((1, 1))
        
        # Total input size for the main MLP: non_axiom_input_size + 1 (for the projected axiom weight)
        mlp_input_size = non_axiom_input_size + 1 

        # --- Main MLP parameters ---
        self.weights_ih = np.random.randn(mlp_input_size, hidden_size) * 0.1 # Input to Hidden weights
        self.bias_h = np.zeros((1, hidden_size)) # Hidden layer bias
        self.weights_ho = np.random.randn(hidden_size, output_size) * 0.1 # Hidden to Output weights
        self.bias_o = np.zeros((1, output_size)) # Output layer bias

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) # Clip to prevent overflow for large x

    def calculate_p_predicted(self, load_bearing_variables: dict) -> tuple[float, float]:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP,
        integrating learned axiom embeddings. Returns P_predicted and the projected axiom weight.
        """
        # Prepare non-axiom input vector (load-bearing variables)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)

        # --- Axiom Embedding Processing ---
        # For simplicity, we'll only use 'AXIOM_RECESSION_AVOIDANCE' for now.
        # This can be extended to sum/average multiple active axiom embeddings.
        if not self.active_axiom_ids:
            projected_axiom_weight = 0.0 # Default if no active axioms
        else:
            main_axiom_id = self.active_axiom_ids[0] # Assume one main axiom for simplicity
            if main_axiom_id not in self.axiom_embeddings:
                # Fallback for architectural validation if axiom not yet in embeddings
                projected_axiom_weight = 0.5 
            else:
                axiom_embedding = self.axiom_embeddings[main_axiom_id]
                # Project embedding to a scalar weight [0,1]
                projected_axiom_weight = self._sigmoid(
                    np.dot(axiom_embedding, self.weights_embedding_projection) + self.bias_embedding_projection
                ).flatten()[0]
        
        # Combine non-axiom inputs with the projected axiom weight
        input_vector = np.array([[growth_rate, inflation_rate, projected_axiom_weight]])

        # Hidden layer computation
        hidden_layer_input = np.dot(input_vector, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        # Output layer computation
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted, projected_axiom_weight

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (weights, biases, embeddings)."""
        params = {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
            'weights_embedding_projection': self.weights_embedding_projection,
            'bias_embedding_projection': self.bias_embedding_projection,
        }
        # Add axiom embeddings
        for axiom_id, embedding in self.axiom_embeddings.items():
            params[f'axiom_embedding_{axiom_id}'] = embedding
        return params

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        self.weights_embedding_projection = params_dict['weights_embedding_projection']
        self.bias_embedding_projection = params_dict['bias_embedding_projection']
        # Set axiom embeddings
        for axiom_id in self.active_axiom_ids:
            param_name = f'axiom_embedding_{axiom_id}'
            if param_name in params_dict:
                self.axiom_embeddings[axiom_id] = params_dict[param_name]


class FiringSquad:
    """
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for all ThesisPredictor's weights, biases, and axiom embeddings.
    """
    def __init__(self):
        pass

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases/embeddings) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline, projected_axiom_weight_baseline = thesis_predictor.calculate_p_predicted(
            load_bearing_variables
        )

        for param_name, param_array in original_params.items():
            # Handle potential non-numpy array values (e.g., if a param is a scalar, which it shouldn't be here)
            if not isinstance(param_array, np.ndarray):
                continue

            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=float)

            for i in range(len(flat_param)):
                # Perturb upwards
                # Create a deep copy of all parameters to perturb only the current one
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_plus = perturbed_params_plus[param_name].flatten()
                temp_flat_plus[i] += current_epsilon
                perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_plus) # Use robust setter
                P_plus, _ = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                # Perturb downwards
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_minus = perturbed_params_minus[param_name].flatten()
                temp_flat_minus[i] -= current_epsilon
                perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_minus) # Use robust setter
                P_minus, _ = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        # Restore original parameters to the thesis_predictor object
        thesis_predictor.set_all_params(original_params)

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "projected_axiom_weight_baseline": projected_axiom_weight_baseline,
            "sensitivity_vector": sensitivity_vector
        }


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters,
    including axiom embeddings and projection parameters.
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
            gradient = dBS_dP * dP_d_param # Chain rule: dBS/dParam = (dBS/dP_predicted) * (dP_predicted/dParam)

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
    Manages the Axiom Store (simulated here) and facilitates updates to Axiom Weights (V2).
    """
    def __init__(self, non_axiom_input_size, hidden_size, output_size,
                 axiom_embedding_dim, active_axiom_ids: list[str]):
        
        self.axiom_store = {axiom_id: f"Atomic truth: {axiom_id} description..." for axiom_id in active_axiom_ids} # Simulated V1 Axiom Store
        self.axiom_weights_v2 = {axiom_id: 0.5 for axiom_id in active_axiom_ids} # Simulated V2 Axiom Weights, initially arbitrary

        self.active_axiom_ids_for_thesis = active_axiom_ids # Store this for convenience
        self.thesis_predictor = ThesisPredictor(
            non_axiom_input_size, hidden_size, output_size, axiom_embedding_dim, active_axiom_ids
        )
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon # Dynamic epsilon can be implemented here

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, and
        crucially, its minimum architectural complexity (MLP structure with Axiom Embedding Layer).
        """
        # 1. Method signature check
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        # 2. Architectural structure check (MLP with specified layers/attributes + Axiom Embedding Layer)
        required_attributes_mlp = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid']
        required_attributes_axiom_emb = ['axiom_embeddings', 'active_axiom_ids', 
                                         'weights_embedding_projection', 'bias_embedding_projection',
                                         'axiom_embedding_dim'] # Added axiom_embedding_dim check
        
        for attr in required_attributes_mlp + required_attributes_axiom_emb:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement full architecture (missing '{attr}' attribute).")
        
        # Check if axiom_embeddings is a dict and has correct dimensions
        if not isinstance(predictor.axiom_embeddings, dict):
            raise ValueError("Meta-Judge VETO: ThesisPredictor.axiom_embeddings must be a dictionary.")
        if not predictor.active_axiom_ids:
            # An empty list is allowed, but the thesis would then contribute nothing from axioms
            pass 
        else:
            for axiom_id in predictor.active_axiom_ids:
                if axiom_id not in predictor.axiom_embeddings:
                    raise ValueError(f"Meta-Judge VETO: Axiom ID '{axiom_id}' missing in axiom_embeddings.")
                if predictor.axiom_embeddings[axiom_id].shape != (1, predictor.axiom_embedding_dim):
                    raise ValueError(f"Meta-Judge VETO: Axiom embedding for '{axiom_id}' has incorrect shape {predictor.axiom_embeddings[axiom_id].shape}, expected (1, {predictor.axiom_embedding_dim}).")
            
            if predictor.weights_embedding_projection.shape != (predictor.axiom_embedding_dim, 1):
                 raise ValueError(f"Meta-Judge VETO: Embedding projection weights have incorrect shape {predictor.weights_embedding_projection.shape}, expected ({predictor.axiom_embedding_dim}, 1).")
        
        # 3. Output range test
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        
        test_p, test_projected_axiom_weight = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted P_predicted output ({test_p}) must be within [0, 1].")
        if not (0.0 <= test_projected_axiom_weight <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted projected axiom weight ({test_projected_axiom_weight}) must be within [0, 1].")


    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        Also updates V2 Axiom Weights based on the learned projections.
        """
        # Validate the Mutator's thesis first (Gatekeeper Reality)
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # Firing Squad calculates sensitivities (RSA) for all parameters including embeddings
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        # EpistemicGradientUpdater updates parameters of self.thesis_predictor directly
        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        # --- Update V2 Axiom Weights from the newly learned projection ---
        # Recalculate P_predicted and projected_axiom_weight with the *updated* ThesisPredictor parameters
        updated_p_predicted, updated_projected_axiom_weight = self.thesis_predictor.calculate_p_predicted(load_bearing_variables)
        
        # For the active axiom, update its weight in the V2 store
        if self.active_axiom_ids_for_thesis: # Ensure there's an axiom to update
            self.axiom_weights_v2[self.active_axiom_ids_for_thesis[0]] = updated_projected_axiom_weight

        return updated_p_predicted, updated_projected_axiom_weight

# --- COUNTER-TEST IMPLEMENTATION ---
def counter_test_model():
    print("Running COUNTER-TEST: Exposing numerical insolvency due to misaligned ground truth.")

    meta_judge = MetaJudge(
        non_axiom_input_size=2,
        hidden_size=hidden_layer_size,
        output_size=1,
        axiom_embedding_dim=axiom_embedding_dim,
        active_axiom_ids=active_axiom_ids_for_thesis
    )

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = []
    projected_axiom_weights_history = []

    for i in range(min_observations_for_calibration):
        current_epsilon = epsilon * (1 - i / min_observations_for_calibration) + 1e-6

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

        # --- CRITICAL CORRECTION: Remove the squaring of true_axiom_relevance ---
        # The original code had: `+ true_axiom_relevance * true_axiom_relevance`
        # This created a mismatch between the true underlying contribution (0.25 for 0.5)
        # and the expected target (0.5) for the axiom's learned weight.
        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance # CORRECTED: Axiom's true contribution is now directly true_axiom_relevance
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted, projected_axiom_weight = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, current_epsilon)
        projected_axiom_weights_history.append(projected_axiom_weight)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            if BS_reference < 1e-9: 
                BS_reference = 1e-9

            BSS = 1 - (BS_model / BS_reference)
            
            tracked_weight_ih_0_0 = meta_judge.thesis_predictor.weights_ih[0, 0]
            tracked_projected_axiom_weight = projected_axiom_weight
            
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BS_ref={BS_reference:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, ProjectedAxiomW={tracked_projected_axiom_weight:.3f}, Epsilon={current_epsilon:.5f}")

            if i == min_observations_for_calibration - 1:
                print(f"\n--- COUNTER-TEST Results after {min_observations_for_calibration} observations ---")
                
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss >= target_brier_skill_score, \
                    f"COUNTER-TEST FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score}). This indicates broader model insolvency."

                all_params_flat = np.concatenate([v.flatten() for v in meta_judge.thesis_predictor.get_all_params().values() if isinstance(v, np.ndarray)])
                avg_abs_param_value = np.mean(np.abs(all_params_flat))
                print(f"Average absolute value of all learned ThesisPredictor parameters (including embeddings): {avg_abs_param_value:.3f}")
                assert avg_abs_param_value > 0.05, \
                    f"COUNTER-TEST FAILED: Average absolute parameter value ({avg_abs_param_value:.3f}) is too close to zero, indicating lack of significant learning."
                
                final_projected_axiom_weight = projected_axiom_weights_history[-1]
                print(f"Final Projected Axiom Weight for '{active_axiom_ids_for_thesis[0]}': {final_projected_axiom_weight:.3f}")
                print(f"True Axiom Relevance (corrected): {true_axiom_relevance:.3f}")
                assert abs(final_projected_axiom_weight - true_axiom_relevance) < target_axiom_relevance_convergence_threshold, \
                    f"COUNTER-TEST FAILED: Projected axiom weight ({final_projected_axiom_weight:.3f}) did not converge to the CORRECTED true relevance ({true_axiom_relevance:.3f}) within threshold ({target_axiom_relevance_convergence_threshold}). This exposes the original miscalibration."
                
                final_v2_axiom_weight = meta_judge.axiom_weights_v2.get(active_axiom_ids_for_thesis[0])
                print(f"V2 Axiom Weight store for '{active_axiom_ids_for_thesis[0]}': {final_v2_axiom_weight:.3f}")
                assert abs(final_v2_axiom_weight - true_axiom_relevance) < target_axiom_relevance_convergence_threshold, \
                    f"COUNTER-TEST FAILED: V2 Axiom Weight was not updated correctly or did not converge to the CORRECTED true relevance ({final_v2_axiom_weight:.3f} vs {true_axiom_relevance:.3f}). This further highlights the original miscalibration."


    print("\nCOUNTER-TEST PASSED: The system, when provided with a correctly specified ground truth, demonstrates robust learning and credit assignment. The original thesis's `Z_actual` generation was indeed miscalibrated, preventing axiom convergence.")

if __name__ == "__main__":
    counter_test_model()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpx90jyok4.py", line 448, in <module>
    counter_test_model()
    ~~~~~~~~~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmpx90jyok4.py", line 424, in counter_test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: COUNTER-TEST FAILED: Rolling Brier Skill Score (-0.009) did not meet target (0.2). This indicates broader model insolvency.


## Attacker: Adversarial System Integrator
The presented thesis outlines a significant architectural evolution for the Epistemic Engine, aiming to resolve critical issues related to credit assignment and empirical calibration of LLM-generated axioms. The proposed integration of an `Axiom Embedding Layer` and `AxiomEmbeddingProjector` within the `ThesisPredictor`, coupled with expanded Firing Squad sensitivity attribution and Adam optimization, represents a conceptually sound approach to transforming static axioms into dynamically weighted, learnable features. The `Meta-Judge`'s `Axiom Integration Validator` is a crucial gatekeeper, enforcing the structural compliance necessary for this paradigm shift.

However, a detailed audit of the accompanying Python Falsification Suite and its `LOAD-BEARING VARIABLES` reveals several critical inconsistencies and misapplications of real-world metrics, which fundamentally compromise the validity of the proposed empirical calibration and credit assignment claims.

### Analytical Critique:

1.  **Architectural Validation Stringency and Bypass Potential:**
    The `MetaJudge.validate_thesis_predictor_architecture` method provides robust syntactic and structural checks, ensuring the presence, correct dimensionality, and output range of the mandated components (MLP layers, axiom embeddings, projection parameters). This effectively prevents a Mutator from generating code that lacks the required architectural complexity. However, the validation does not extend to the *semantic correctness* of the `calculate_p_predicted` method's internal logic. A Mutator could generate syntactically compliant code that, for instance, trivializes the contribution of the learned embeddings or the MLP's weights (e.g., by multiplying them by zero or returning a hardcoded constant), thereby subverting the intended learning mechanism while still passing architectural checks. The ultimate semantic validation relies on the Brier Skill Score and axiom convergence assertions, which are downstream checks.

2.  **Scaling of Computational Cost and 'Operational Drag':**
    The thesis accurately identifies the "Dramatically increased computational burden" as a key trade-off. The Firing Squad's Robust Sensitivity Attributor (RSA) requires `2N+1` executions of the `ThesisPredictor` for each update step, where `N` is the total number of optimizable parameters. For the current configuration (`non_axiom_input_size=2`, `hidden_layer_size=4`, `output_size=1`, `axiom_embedding_dim=2`, `num_active_axioms=1`), `N` is approximately 26 parameters. This translates to `2 * 26 + 1 = 53` `calculate_p_predicted` calls per observation. While manageable for this small `N`, the computational cost scales linearly with `N`. As the `ThesisPredictor` grows in complexity (e.g., more hidden layers, larger hidden sizes, higher embedding dimensions, or more active axioms), `N` will increase, rendering the `2N+1` derivative calculation method computationally intractable for real-world applications requiring rapid iteration or large parameter spaces. The "New Operational Drag" focuses on the `Meta-Judge`'s validator as a pre-execution bottleneck, which is valid for initial Mutator development, but the `2N+1` execution cost represents the primary and ongoing operational drag for system throughput and latency.

3.  **Credit Assignment and System Brittleness (Problem 6):**
    The thesis explicitly proposes a mechanism to address Problem 6 (no feedback loop to axioms) by propagating the `projected_axiom_weight` back to the V2 `Axiom Weights` store. This is a direct attempt to solve the issue. However, the current falsification suite's simulation of `Z_actual` contains a fundamental semantic inconsistency that undermines the claim of precise, attributable credit assignment. The `true_axiom_relevance` is defined as a scalar, but its contribution to `true_linear_combination_nl` in the `Z_actual` function is `true_axiom_relevance * true_axiom_relevance`. If `true_axiom_relevance = 0.5`, this results in a constant additive term of `0.25`. The `ThesisPredictor`, conversely, learns a `projected_axiom_weight` which acts as a *dynamic input feature* to its MLP, and this feature is asserted to converge to `true_axiom_relevance` (i.e., `0.5`). This creates a category mismatch: a dynamic input feature is expected to converge to a value that, in the ground truth, represents a constant contribution (0.25) rather than its own value (0.5). This inconsistency renders the `target_axiom_relevance_convergence_threshold` assertion ill-defined and compromises the validity of the credit assignment mechanism.

4.  **Parametric Grounding Audit ('Cooked Books'):**
    *   **`hypothetical_inflation_rate_q1_2025_base = 0.03`**: This value represents a 3% *quarterly* inflation rate. Annualized, this equates to approximately `(1.03)^4 - 1 = 12.55%` annual inflation. This is an extremely high and unrealistic baseline for a stable economy, typically indicative of hyperinflationary conditions or severe economic instability. Most central banks target an annual inflation rate of 2-3%. Using such an extreme baseline creates a highly specific and potentially pathological data distribution for the simulation. A model trained and validated under these conditions may exhibit poor generalizability and robustness when faced with more typical, lower inflation regimes. This constitutes a significant misapplication of a financial metric, potentially "cooking the books" by creating an environment where the model's specific parameters (e.g., `true_inflation_coeff_nl`, `true_interaction_coeff_nl`) might appear to work, but only within this narrow, extreme context.
    *   **`true_axiom_relevance * true_axiom_relevance` in `Z_actual`**: As detailed above, this is a semantic inconsistency. If `true_axiom_relevance` is the ground truth scalar relevance (e.g., 0.5), its contribution to the `Z_actual` function should ideally be `true_axiom_relevance` itself (as an additive term or a coefficient for a relevant input), not its square. The current formulation creates a mismatch between the expected convergence target (0.5) and the actual contribution in the ground truth (0.25), fundamentally undermining the credit assignment assertion.
    *   **Other Parameters**: `epsilon`, Adam parameters, `learning_rate_model_params`, `min_observations_for_calibration`, `target_brier_skill_score`, `rolling_window_size`, `hidden_layer_size`, `axiom_embedding_dim`, `active_axiom_ids_for_thesis`, `hypothetical_economy_growth_rate_q1_2025_base`, `true_bias_nl`, `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, `true_interaction_coeff_nl`, `target_axiom_relevance_convergence_threshold` are either standard hyperparameters, system design parameters, or parameters for a simulated non-linear process. While the large magnitudes of `true_growth_freq_nl`, `true_growth_coeff_nl`, `true_inflation_freq_nl`, `true_inflation_coeff_nl`, and `true_interaction_coeff_nl` suggest a highly volatile or sensitive `Z_actual` function, they are within the bounds of defining a complex synthetic environment.

### So What for the Meta-Judge:

The identified parametric inconsistencies and semantic flaws in the falsification suite's `Z_actual` generation are critical. The use of an unrealistic `hypothetical_inflation_rate_q1_2025_base` means the system's demonstrated learning capabilities are validated against a narrow, extreme, and unrepresentative economic scenario. This severely limits the generalizability and robustness of the `ThesisPredictor` to real-world conditions. Furthermore, the semantic mismatch in how `true_axiom_relevance` is incorporated into `Z_actual` directly invalidates the core assertion of precise, attributable credit assignment. If the ground truth itself is inconsistently formulated, the convergence of `projected_axiom_weight` to `true_axiom_relevance` becomes an ill-posed problem. Consequently, the claims of empirically calibrated probabilities and accurate credit assignment, which are central to the V3 proposal, are rendered unreliable and potentially misleading. The system's ability to learn and attribute credit is thus demonstrated only for a flawed and potentially pathological simulation environment, undermining its utility for robust epistemic advancement.

### COUNTER-TEST:

The counter-test will expose the insolvency by:
1.  **Correcting the `hypothetical_inflation_rate_q1_2025_base`** to a realistic quarterly rate derived from a standard annual target (e.g., 2% annual inflation).
2.  **Rectifying the semantic inconsistency in `Z_actual` generation** by using `true_axiom_relevance` directly as an additive term, making the ground truth consistent with the assertion that `projected_axiom_weight` should converge to `true_axiom_relevance`.
Under these corrected and more realistic conditions, the original `Z_actual` function's coefficients (`true_inflation_coeff_nl`, `true_interaction_coeff_nl`) are likely to be miscalibrated, making the learning task significantly harder or impossible for the `ThesisPredictor` to meet its performance and convergence targets.

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

# New variables for Axiom Embedding Layer
axiom_embedding_dim = 2 # Dimension of each axiom's embedding vector
# The fixed axiom ID for this simulation. In a real system, this would come from V1's Axiom Store.
active_axiom_ids_for_thesis = ['AXIOM_RECESSION_AVOIDANCE']

# Simulated real-world values for the falsification test context.
# These represent external inputs that the Mutator's ThesisPredictor *must* utilize.
hypothetical_economy_growth_rate_q1_2025_base = 0.02

# --- COUNTER-TEST MODIFICATION 1: Realistic Inflation Rate ---
# Original: hypothetical_inflation_rate_q1_2025_base = 0.03 (3% quarterly, ~12.55% annualized - unrealistic)
# Corrected: 2% annual inflation target, converted to quarterly rate.
# (1 + 0.02)^(1/4) - 1 = 0.0049626...
hypothetical_inflation_rate_q1_2025_base = (1 + 0.02)**(1/4) - 1 # Approx 0.00496

# True parameters for the *simulated, non-linear* Z_actual generation
true_bias_nl = -0.5
true_growth_freq_nl = 50
true_growth_coeff_nl = 10
true_inflation_freq_nl = 30
true_inflation_coeff_nl = -15 # These coefficients are now miscalibrated for the realistic inflation input
true_interaction_coeff_nl = 500 # These coefficients are now miscalibrated for the realistic inflation input
# This is the 'ground truth' scalar relevance for AXIOM_RECESSION_AVOIDANCE that the system should learn.
true_axiom_relevance = 0.5 
target_axiom_relevance_convergence_threshold = 0.1 # Max allowed absolute difference from true_axiom_relevance

class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Now includes an Axiom Embedding Layer and a projection to a scalar weight.
    """
    def __init__(self, non_axiom_input_size: int, hidden_size: int, output_size: int,
                 axiom_embedding_dim: int, active_axiom_ids: list[str]):
        
        # --- Axiom Embedding Layer parameters ---
        self.active_axiom_ids = active_axiom_ids
        self.axiom_embedding_dim = axiom_embedding_dim # Store for validation
        self.axiom_embeddings = {
            axiom_id: np.random.randn(1, axiom_embedding_dim) * 0.1 
            for axiom_id in active_axiom_ids # Each embedding is a 1xdim vector
        }
        # Parameters for projecting axiom embedding to a scalar weight [0,1]
        self.weights_embedding_projection = np.random.randn(axiom_embedding_dim, 1) * 0.1
        self.bias_embedding_projection = np.zeros((1, 1))
        
        # Total input size for the main MLP: non_axiom_input_size + 1 (for the projected axiom weight)
        mlp_input_size = non_axiom_input_size + 1 

        # --- Main MLP parameters ---
        self.weights_ih = np.random.randn(mlp_input_size, hidden_size) * 0.1 # Input to Hidden weights
        self.bias_h = np.zeros((1, hidden_size)) # Hidden layer bias
        self.weights_ho = np.random.randn(hidden_size, output_size) * 0.1 # Hidden to Output weights
        self.bias_o = np.zeros((1, output_size)) # Output layer bias

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) # Clip to prevent overflow for large x

    def calculate_p_predicted(self, load_bearing_variables: dict) -> tuple[float, float]:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP,
        integrating learned axiom embeddings. Returns P_predicted and the projected axiom weight.
        """
        # Prepare non-axiom input vector (load-bearing variables)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)

        # --- Axiom Embedding Processing ---
        # For simplicity, we'll only use 'AXIOM_RECESSION_AVOIDANCE' for now.
        # This can be extended to sum/average multiple active axiom embeddings.
        if not self.active_axiom_ids:
            projected_axiom_weight = 0.0 # Default if no active axioms
        else:
            main_axiom_id = self.active_axiom_ids[0] # Assume one main axiom for simplicity
            if main_axiom_id not in self.axiom_embeddings:
                # Fallback for architectural validation if axiom not yet in embeddings
                projected_axiom_weight = 0.5 
            else:
                axiom_embedding = self.axiom_embeddings[main_axiom_id]
                # Project embedding to a scalar weight [0,1]
                projected_axiom_weight = self._sigmoid(
                    np.dot(axiom_embedding, self.weights_embedding_projection) + self.bias_embedding_projection
                ).flatten()[0]
        
        # Combine non-axiom inputs with the projected axiom weight
        input_vector = np.array([[growth_rate, inflation_rate, projected_axiom_weight]])

        # Hidden layer computation
        hidden_layer_input = np.dot(input_vector, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        # Output layer computation
        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted, projected_axiom_weight

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (weights, biases, embeddings)."""
        params = {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
            'weights_embedding_projection': self.weights_embedding_projection,
            'bias_embedding_projection': self.bias_embedding_projection,
        }
        # Add axiom embeddings
        for axiom_id, embedding in self.axiom_embeddings.items():
            params[f'axiom_embedding_{axiom_id}'] = embedding
        return params

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        self.weights_embedding_projection = params_dict['weights_embedding_projection']
        self.bias_embedding_projection = params_dict['bias_embedding_projection']
        # Set axiom embeddings
        for axiom_id in self.active_axiom_ids:
            param_name = f'axiom_embedding_{axiom_id}'
            if param_name in params_dict:
                self.axiom_embeddings[axiom_id] = params_dict[param_name]


class FiringSquad:
    """
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for all ThesisPredictor's weights, biases, and axiom embeddings.
    """
    def __init__(self):
        pass

    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases/embeddings) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline, projected_axiom_weight_baseline = thesis_predictor.calculate_p_predicted(
            load_bearing_variables
        )

        for param_name, param_array in original_params.items():
            # Handle potential non-numpy array values (e.g., if a param is a scalar, which it shouldn't be here)
            if not isinstance(param_array, np.ndarray):
                print(f"Warning: Param {param_name} is not a numpy array. Skipping sensitivity calculation.")
                continue

            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=float)

            for i in range(len(flat_param)):
                # Perturb upwards
                # Create a deep copy of all parameters to perturb only the current one
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_plus = perturbed_params_plus[param_name].flatten()
                temp_flat_plus[i] += current_epsilon
                perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_plus) # Use robust setter
                P_plus, _ = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                # Perturb downwards
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                temp_flat_minus = perturbed_params_minus[param_name].flatten()
                temp_flat_minus[i] -= current_epsilon
                perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                thesis_predictor.set_all_params(perturbed_params_minus) # Use robust setter
                P_minus, _ = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
            
            sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        # Restore original parameters to the thesis_predictor object
        thesis_predictor.set_all_params(original_params)

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "projected_axiom_weight_baseline": projected_axiom_weight_baseline,
            "sensitivity_vector": sensitivity_vector
        }


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters,
    including axiom embeddings and projection parameters.
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
            gradient = dBS_dP * dP_d_param # Chain rule: dBS/dParam = (dBS/dP_predicted) * (dP_predicted/dParam)

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
    Manages the Axiom Store (simulated here) and facilitates updates to Axiom Weights (V2).
    """
    def __init__(self, non_axiom_input_size, hidden_size, output_size,
                 axiom_embedding_dim, active_axiom_ids: list[str]):
        
        self.axiom_store = {axiom_id: f"Atomic truth: {axiom_id} description..." for axiom_id in active_axiom_ids} # Simulated V1 Axiom Store
        self.axiom_weights_v2 = {axiom_id: 0.5 for axiom_id in active_axiom_ids} # Simulated V2 Axiom Weights, initially arbitrary

        self.active_axiom_ids_for_thesis = active_axiom_ids # Store this for convenience
        self.thesis_predictor = ThesisPredictor(
            non_axiom_input_size, hidden_size, output_size, axiom_embedding_dim, active_axiom_ids
        )
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon # Dynamic epsilon can be implemented here

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, and
        crucially, its minimum architectural complexity (MLP structure with Axiom Embedding Layer).
        """
        # 1. Method signature check
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        # 2. Architectural structure check (MLP with specified layers/attributes + Axiom Embedding Layer)
        required_attributes_mlp = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid']
        required_attributes_axiom_emb = ['axiom_embeddings', 'active_axiom_ids', 
                                         'weights_embedding_projection', 'bias_embedding_projection',
                                         'axiom_embedding_dim'] # Added axiom_embedding_dim check
        
        for attr in required_attributes_mlp + required_attributes_axiom_emb:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement full architecture (missing '{attr}' attribute).")
        
        # Check if axiom_embeddings is a dict and has correct dimensions
        if not isinstance(predictor.axiom_embeddings, dict):
            raise ValueError("Meta-Judge VETO: ThesisPredictor.axiom_embeddings must be a dictionary.")
        if not predictor.active_axiom_ids:
            # An empty list is allowed, but the thesis would then contribute nothing from axioms
            pass 
        else:
            for axiom_id in predictor.active_axiom_ids:
                if axiom_id not in predictor.axiom_embeddings:
                    raise ValueError(f"Meta-Judge VETO: Axiom ID '{axiom_id}' missing in axiom_embeddings.")
                if predictor.axiom_embeddings[axiom_id].shape != (1, predictor.axiom_embedding_dim):
                    raise ValueError(f"Meta-Judge VETO: Axiom embedding for '{axiom_id}' has incorrect shape {predictor.axiom_embeddings[axiom_id].shape}, expected (1, {predictor.axiom_embedding_dim}).")
            
            if predictor.weights_embedding_projection.shape != (predictor.axiom_embedding_dim, 1):
                 raise ValueError(f"Meta-Judge VETO: Embedding projection weights have incorrect shape {predictor.weights_embedding_projection.shape}, expected ({predictor.axiom_embedding_dim}, 1).")
        
        # 3. Output range test
        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        
        test_p, test_projected_axiom_weight = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted P_predicted output ({test_p}) must be within [0, 1].")
        if not (0.0 <= test_projected_axiom_weight <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted projected axiom weight ({test_projected_axiom_weight}) must be within [0, 1].")


    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        Also updates V2 Axiom Weights based on the learned projections.
        """
        # Validate the Mutator's thesis first (Gatekeeper Reality)
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # Firing Squad calculates sensitivities (RSA) for all parameters including embeddings
        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        # EpistemicGradientUpdater updates parameters of self.thesis_predictor directly
        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        # --- Update V2 Axiom Weights from the newly learned projection ---
        # Recalculate P_predicted and projected_axiom_weight with the *updated* ThesisPredictor parameters
        updated_p_predicted, updated_projected_axiom_weight = self.thesis_predictor.calculate_p_predicted(load_bearing_variables)
        
        # For the active axiom, update its weight in the V2 store
        if self.active_axiom_ids_for_thesis: # Ensure there's an axiom to update
            self.axiom_weights_v2[self.active_axiom_ids_for_thesis[0]] = updated_projected_axiom_weight

        return updated_p_predicted, updated_projected_axiom_weight

# --- Simulation and Falsification Test ---
def test_model():
    print("Running COUNTER-TEST for V3 Architecture (Axiom Embedding & Credit Assignment)...")
    print(f"Using realistic quarterly inflation rate: {hypothetical_inflation_rate_q1_2025_base:.5f} (approx 2% annually)")

    # The ThesisPredictor's non-axiom input size is 2 (growth, inflation)
    meta_judge = MetaJudge(
        non_axiom_input_size=2,
        hidden_size=hidden_layer_size,
        output_size=1,
        axiom_embedding_dim=axiom_embedding_dim,
        active_axiom_ids=active_axiom_ids_for_thesis
    )

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] # For rolling historical frequency

    # Store projected axiom weights for falsification
    projected_axiom_weights_history = [] 

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
        
        # --- Simulate Z_actual with TRUE NON-LINEARITY and INTERACTIONS ---
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            # --- COUNTER-TEST MODIFICATION 2: Corrected Axiom Relevance Usage ---
            # Original: + true_axiom_relevance * true_axiom_relevance (constant 0.25)
            # Corrected: + true_axiom_relevance (direct additive term, consistent with 0.5 target)
            + true_axiom_relevance 
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted, projected_axiom_weight = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, current_epsilon)
        projected_axiom_weights_history.append(projected_axiom_weight)

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
            tracked_projected_axiom_weight = projected_axiom_weight
            
            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BS_ref={BS_reference:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, ProjectedAxiomW={tracked_projected_axiom_weight:.3f}, Epsilon={current_epsilon:.5f}")

            if i == min_observations_for_calibration - 1:
                # --- Falsifiability Assertions ---
                print(f"\n--- COUNTER-TEST Results after {min_observations_for_calibration} observations ---")
                
                # ASSERTION 1: Rolling Brier Skill Score must meet target
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss >= target_brier_skill_score, \
                    f"COUNTER-TEST FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score}). This indicates the model struggles under realistic input conditions with miscalibrated Z_actual parameters."

                # ASSERTION 2: Average absolute value of all learned ThesisPredictor parameters must indicate significant learning.
                all_params_flat = np.concatenate([v.flatten() for v in meta_judge.thesis_predictor.get_all_params().values() if isinstance(v, np.ndarray)])
                avg_abs_param_value = np.mean(np.abs(all_params_flat))
                print(f"Average absolute value of all learned ThesisPredictor parameters (including embeddings): {avg_abs_param_value:.3f}")
                assert avg_abs_param_value > 0.05, \
                    f"COUNTER-TEST FAILED: Average absolute parameter value ({avg_abs_param_value:.3f}) is too close to zero, indicating lack of significant learning under corrected conditions."
                
                # ASSERTION 3: The projected axiom weight must converge to its true underlying relevance.
                final_projected_axiom_weight = projected_axiom_weights_history[-1]
                print(f"Final Projected Axiom Weight for '{active_axiom_ids_for_thesis[0]}': {final_projected_axiom_weight:.3f}")
                print(f"True Axiom Relevance: {true_axiom_relevance:.3f}")
                assert abs(final_projected_axiom_weight - true_axiom_relevance) < target_axiom_relevance_convergence_threshold, \
                    f"COUNTER-TEST FAILED: Projected axiom weight ({final_projected_axiom_weight:.3f}) did not converge to true relevance ({true_axiom_relevance:.3f}) within threshold ({target_axiom_relevance_convergence_threshold}). This indicates the credit assignment mechanism is fragile when Z_actual parameters are not 'cooked' for specific inputs."
                
                # ASSERTION 4: Verify the V2 Axiom Weight store has been updated.
                final_v2_axiom_weight = meta_judge.axiom_weights_v2.get(active_axiom_ids_for_thesis[0])
                print(f"V2 Axiom Weight store for '{active_axiom_ids_for_thesis[0]}': {final_v2_axiom_weight:.3f}")
                assert abs(final_v2_axiom_weight - true_axiom_relevance) < target_axiom_relevance_convergence_threshold, \
                    f"COUNTER-TEST FAILED: V2 Axiom Weight was not updated correctly or did not converge to true relevance ({final_v2_axiom_weight:.3f} vs {true_axiom_relevance:.3f})."


    print("\nCOUNTER-TEST PASSED: All conditions met under corrected parameters. This implies the original setup was indeed 'cooked' to achieve success.")

# Execute the test
if __name__ == "__main__":
    test_model()
```

### PYTHON EXECUTION OUTPUT:
Error: Traceback (most recent call last):
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmp3hi37vo8.py", line 478, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/var/folders/p3/y8cz7t3d7jv32skk58hf6l580000gn/T/tmp3hi37vo8.py", line 450, in test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: COUNTER-TEST FAILED: Rolling Brier Skill Score (-208924785.513) did not meet target (0.2). This indicates the model struggles under realistic input conditions with miscalibrated Z_actual parameters.



## Level 3 Unit Test Results
❌ FAIL: The thesis was DISPROVEN by its own unit tests.
Error: Traceback (most recent call last):
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 490, in <module>
    test_model()
    ~~~~~~~~~~^^
  File "/Users/daalami/figs_activist_loop/projects/epistemic_engine_v3/test_model.py", line 462, in test_model
    assert final_bss >= target_brier_skill_score, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: FALSIFICATION FAILED: Rolling Brier Skill Score (-0.132) did not meet target (0.2).


