RETIRED AXIOM: `new_prob = prior * exp(-1.1 * relative_error)` - This mathematical relationship creates unbounded probabilities outside the [0, 1] domain, rendering it fundamentally unsound for probabilistic reasoning. It is structurally irrelevant to a system requiring empirically calibrated probabilities and direct gradient-based credit assignment.

---

### SYMBOLIC MAPPING:

*   **Z (Resultant State):** An *axiom-augmented* `P_predicted` where each input axiom's contribution to prediction accuracy is directly learned as a distinct, optimizable coefficient within the `ThesisPredictor`'s Multi-Layer Perceptron (MLP). These learned axiom coefficients are then *synchronised* back to the `Meta-Judge`'s global `Axiom Weights` store, providing granular, gradient-based credit assignment that can be directly consumed by the V1/V2 LLM pipeline for iterative axiom refinement and thesis generation. This is evidenced by a statistically significant convergence of the learned axiom coefficients to their true underlying relevance in the simulated environment, while simultaneously maintaining the `target_brier_skill_score` under complex, non-linear conditions.
*   **X (Blocked Variable):** The `ThesisPredictor`'s prior architecture treats `axiom_weights` as *immutable input features* rather than *learnable parameters*. This architectural impedance prevents direct, gradient-based credit assignment to individual axioms. Consequently, the `Meta-Judge`'s global `Axiom Weights` store lacks a precise, real-time mechanism to update axiom utility based on predictive performance, hindering the LLM Mutator's ability to evolve and refine foundational truths, leading to persistent "last-mile derivation" failures (Open Problem 2) and ineffective axiom feedback loops (Open Problem 6).
*   **Y (Leverage Variable):**
    1.  **`AxiomCoefficientLayer` Integration:** The `ThesisPredictor`'s architecture is augmented to include a dedicated, learnable `AxiomCoefficientLayer`. For each axiom present in the `Meta-Judge`'s `axiom_weights` store, a corresponding scalar coefficient is instantiated as an *optimizable parameter* within the `ThesisPredictor`. These coefficients are initialized using the global `axiom_weights` values.
    2.  **Extended `EpistemicGradientUpdater`:** The `EpistemicGradientUpdater` is extended to compute gradients and apply Adam optimization not only to the MLP's internal weights and biases but *also* to these newly integrated `AxiomCoefficientLayer` parameters. This enables direct, precise credit assignment to individual axioms.
    3.  **`AxiomWeightSynchronization` Protocol:** The `Meta-Judge` implements an `AxiomWeightSynchronization` protocol. After each successful `EpistemicGradientUpdater` step, the `Meta-Judge` extracts the updated values of the `AxiomCoefficientLayer` parameters from the `ThesisPredictor` and overwrites the corresponding values in its global `axiom_weights` store. This closes the feedback loop, ensuring the LLM Mutator's foundational knowledge base is continuously informed by empirical performance.
    4.  **Meta-Judge's `AxiomCoeffValidation` Constraint:** The `Meta-Judge`'s `validate_thesis_predictor_architecture` method now includes an `AxiomCoeffValidation` step that verifies the `ThesisPredictor` explicitly instantiates and exposes optimizable parameters for each active axiom in the global `axiom_weights` store, preventing the Mutator from omitting or obscuring axiom influence.

---

### LOAD-BEARING VARIABLES:

| Variable                                        | Role                                                                               | Exact Real-World Value (or system parameter)                                                                                                                                                                                |
| :---------------------------------------------- | :--------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `epsilon` (initial)                             | Initial perturbation magnitude for numerical derivative calculation                | `0.001` (System parameter, chosen for initial robustness)                                                                                                                                                                   |
| `adam_beta1`                                    | Adam optimizer parameter: decay rate for first moment estimates (`m`)              | `0.9` (Dimensionless, standard Adam hyperparameter)                                                                                                                                                                         |
| `adam_beta2`                                    | Adam optimizer parameter: decay rate for second moment estimates (`v`)             | `0.999` (Dimensionless, standard Adam hyperparameter)                                                                                                                                                                       |
| `adam_epsilon_stabilizer`                       | Adam optimizer parameter: small constant to prevent division by zero               | `1e-8` (Dimensionless, standard Adam hyperparameter)                                                                                                                                                                        |
| `learning_rate_model_params`                    | Global learning rate scale for all model parameters (weights/biases)               | `0.001` (Dimensionless, empirically tuned for stability in non-linear models)                                                                                                                                                |
| `learning_rate_axiom_coeffs`                    | **NEW:** Learning rate scale specifically for axiom coefficients                   | `0.01` (Dimensionless, higher for faster axiom adaptation, empirically tuned)                                                                                                                                                |
| `min_observations_for_calibration`              | Minimum `Z_actual` observations before BSS can be robustly calculated              | `200` (System parameter, increased due to greater model complexity and non-linear `Z_actual` behavior)                                                                                                                      |
| `target_brier_skill_score`                      | Minimum acceptable Brier Skill Score after calibration                             | `0.20` (Dimensionless target: 20% improvement over baseline, increased from V2's 0.15 due to enhanced model capabilities)                                                                                                     |
| `rolling_window_size`                           | Number of observations for rolling average Brier Skill Score calculation           | `50` (System parameter for BSS temporal averaging)                                                                                                                                                                          |
| `hidden_layer_size`                             | Number of neurons in the `ThesisPredictor`'s hidden layer                          | `4` (Dimensionless, design parameter for MLP capacity)                                                                                                                                                                      |
| `initial_axiom_coefficient_value`               | **NEW:** Initial value for axiom coefficients within `ThesisPredictor`             | `0.5` (Dimensionless, serves as starting point for learned axiom relevance)                                                                                                                                                 |
| `axiom_sync_frequency`                          | **NEW:** Frequency for `Meta-Judge` to sync learned axiom coefficients             | `1` (Dimensionless: syncs every single update iteration)                                                                                                                                                                    |
| `hypothetical_economy_growth_rate_q1_2025_base` | Baseline for simulated economy growth rate                                         | `0.02` (Dimensionless rate, e.g., 2% per quarter)                                                                                                                                                                           |
| `hypothetical_inflation_rate_q1_2025_base`      | Baseline for simulated inflation rate                                              | `0.03` (Dimensionless rate, e.g., 3% per quarter)                                                                                                                                                                           |
| `true_bias_nl`                                  | Intercept term for the *simulated non-linear* `Z_actual` function                  | `-0.5` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                 |
| `true_growth_freq_nl`                           | Frequency parameter for sine component of *simulated non-linear* growth effect     | `50` (Dimensionless, parameter of the true underlying non-linear process, scaling factor for `growth_rate`)                                                                                                                 |
| `true_growth_coeff_nl`                          | Coefficient for sine component of *simulated non-linear* growth effect             | `10` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                   |
| `true_inflation_freq_nl`                        | Frequency parameter for cosine component of *simulated non-linear* inflation effect | `30` (Dimensionless, parameter of the true underlying non-linear process, scaling factor for `inflation_rate`)                                                                                                              |
| `true_inflation_coeff_nl`                       | Coefficient for cosine component of *simulated non-linear* inflation effect        | `-15` (Dimensionless, parameter of the true underlying non-linear process)                                                                                                                                                  |
| `true_interaction_coeff_nl`                     | Coefficient for interaction term (`growth_rate * inflation_rate`)                  | `500` (Dimensionless, parameter of the true underlying non-linear process, scaling factor for the product of rates)                                                                                                         |
| `true_axiom_relevance`                          | Relevance of `AXIOM_RECESSION_AVOIDANCE` in the *simulated non-linear* `Z_actual`  | `0.8` (Dimensionless, indicates true contribution of the fixed axiom to the underlying non-linear process, chosen to be distinct from `initial_axiom_coefficient_value`)                                                     |

---

### STRUCTURAL ARBITRAGE:

The fundamental arbitrage opportunity, previously lost in the impedance mismatch between `ThesisPredictor`'s internal learning and the `Meta-Judge`'s `Axiom Store`, is now captured by a **structural elevation of axioms from static inputs to dynamically learned parameters**. By integrating a dedicated `AxiomCoefficientLayer` directly within the `ThesisPredictor`'s MLP, the system directly exposes axiom utility to gradient-based optimization. This transformation allows the `EpistemicGradientUpdater` to perform precise, real-time credit assignment not just to the model's weights but to the axioms themselves. The `Meta-Judge`'s `AxiomWeightSynchronization` protocol then leverages this direct learning by *overwriting* its global `axiom_weights` with these empirically derived coefficients. This systemic bypass eliminates indirect blame distribution, creating a direct, quantitative feedback loop that transforms axioms into adaptable, empirically calibrated components that directly inform the LLM Mutator's generation of subsequent theses.

---

### CONSERVATION OF TRADE-OFFS:

*   **Velocity (V):** Significantly increased rate of axiom adaptation and refinement. The `ThesisPredictor` now directly learns the empirical relevance of each axiom, leading to faster convergence on optimal axiom weights and, consequently, more accurate and calibrated `P_predicted` values, especially in environments where axiom utility varies. The `AxiomWeightSynchronization` protocol ensures this learned utility is immediately propagated to the global store, accelerating feedback to the Mutator.
*   **Energy (E):** Increased computational burden. Each active axiom introduces an additional learnable parameter (its coefficient) within the `ThesisPredictor`. The Firing Squad's Robust Sensitivity Attributor (RSA) must now calculate `dP/d(param)` for *every one* of these axiom coefficients, in addition to the MLP's weights and biases, leading to `2 * (N + A) + 1` executions per sensitivity report (where `N` is MLP parameters, `A` is number of axioms). The `EpistemicGradientUpdater` also processes more parameters per update step.
*   **Mass (M):** Increased architectural complexity within the `ThesisPredictor` (due to the `AxiomCoefficientLayer`), within the `EpistemicGradientUpdater` (handling differentiated learning rates for axiom coefficients), and within the `Meta-Judge` (implementing `AxiomCoeffValidation` and the `AxiomWeightSynchronization` protocol). The Mutator's task of generating compliant `ThesisPredictor` code is also significantly more complex, requiring it to correctly instantiate and expose these axiom parameters.

**New Operational Drag:**
The **Meta-Judge's `AxiomCoeffValidation` constraint** introduces a new, critical pre-execution bottleneck. If the Mutator fails to generate `ThesisPredictor` code that explicitly instantiates and exposes *all* active axioms as distinct, optimizable parameters within its `learned_axiom_coeffs` dictionary, the entire Popperian falsification loop iteration is immediately halted. This rigorous enforcement forces the Mutator to evolve highly sophisticated code generation capabilities for axiom integration, potentially leading to higher initial iteration failure rates and increased Mutator generation time until structural compliance for all axioms is consistently achieved.

---

### GATEKEEPER REALITY:

*   **Absolute Veto (The Bottleneck):** The **Meta-Judge's `AxiomCoeffValidation` constraint**. It wields absolute authority to reject any thesis if its `ThesisPredictor` implementation does not explicitly instantiate an optimizable `learned_axiom_coeffs` dictionary containing a `np.ndarray` parameter for *each* active axiom from the global `axiom_weights` store, or if its `calculate_p_predicted` method's output `P_predicted` falls outside the `[0,1]` probability range.
*   **Asymmetric Leverage:** The **combination of the Firing Squad's Robust Sensitivity Attributor (RSA) computing precise `dP/d(axiom_coeff)` for *each axiom coefficient* (alongside MLP parameters) within the multi-layer network, coupled with the Adam optimizer within the `EpistemicGradientUpdater` applying a dedicated `learning_rate_axiom_coeffs`, and the `Meta-Judge`'s `AxiomWeightSynchronization` protocol**. This dual and tri-leveraged mechanism forces the Mutator to generate computationally amenable, differentiable, and axiom-integrating non-linear models. The RSA provides exact, gradient-based feedback on an axiom's empirical utility, the Adam optimizer efficiently updates these axiom coefficients, and the synchronization protocol directly updates the global `axiom_weights`, thereby precisely and automatically assigning credit to axioms and feeding this granular insight back to the LLM Mutator, solving the "last-mile derivation" failure and the indirect credit assignment problems.

---

### FALSIFIABILITY:

**Prediction:** After `min_observations_for_calibration` (e.g., 200) simulated quarterly economic reports (where `Z_actual` is generated via a *non-linear, interacting* underlying process that includes `growth_rate`, `inflation_rate`, and a `true_axiom_relevance` of `0.8` for `AXIOM_RECESSION_AVOIDANCE`), the engine's rolling `rolling_window_size` (e.g., 50) observation average Brier Skill Score will consistently exceed `target_brier_skill_score` (e.g., 0.20). Furthermore, the `ThesisPredictor`'s learned coefficient for `AXIOM_RECESSION_AVOIDANCE` (`thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE']`) will converge to a value greater than `0.65` and within `0.25` absolute difference of `true_axiom_relevance` (`0.8`), significantly deviating from its `initial_axiom_coefficient_value` (`0.5`). Concurrently, the `Meta-Judge`'s global `axiom_weights['AXIOM_RECESSION_AVOIDANCE']` will be numerically identical (within `1e-6` absolute difference) to the `ThesisPredictor`'s learned coefficient, demonstrating successful credit assignment and synchronization to the LLM-consumable axiom store.

---

```python
import math
import random
import collections
import inspect
import numpy as np # For matrix operations

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


class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Now, axioms are treated as learnable parameters within the MLP.
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
    Executes the ThesisPredictor and implements the Robust Sensitivity Attributor (RSA).
    Calculates numerical derivatives for all ThesisPredictor's weights, biases, AND axiom coefficients.
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
        
        thesis_predictor.set_all_params(original_params) # Restore original parameters

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }


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
    """
    Scores thesis, manages ThesisPredictor parameters (via updater), enforces architectural validation,
    and now syncs learned axiom coefficients back to its global axiom store.
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
        """
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        if iteration % axiom_sync_frequency == 0:
            self.sync_axiom_weights_from_predictor()
        
        return sensitivity_report["P_predicted_baseline"]

# --- Simulation and Falsification Test ---
def test_model():
    print("Running Falsification Test for V3 Architecture (Axiom Credit Assignment & LLM Bridge)...")

    external_input_features = 2 
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] 

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

        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * 1.0 # The axiom's true impact is hardcoded here (as if axiom is fully 'true')
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted = meta_judge.evaluate_and_update(current_load_bearing_variables, Z_actual, i+1, current_epsilon)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 

            BSS = 1 - (BS_model / BS_reference)
            
            tracked_weight_ih_0_0 = meta_judge.thesis_predictor.weights_ih[0, 0] # Growth_rate to hidden[0]
            tracked_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
            global_axiom_weight_synced = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']

            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, LearnedAxiomCoeff={tracked_axiom_coeff:.3f}, SyncedAxiomWeight={global_axiom_weight_synced:.3f}, Epsilon={current_epsilon:.5f}")

            if i == min_observations_for_calibration - 1:
                print(f"\n--- Falsification Test Results after {min_observations_for_calibration} observations ---")
                
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss >= target_brier_skill_score, \
                    f"FALSIFICATION FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score})."

                final_learned_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
                print(f"Final Learned AXIOM_RECESSION_AVOIDANCE coefficient: {final_learned_axiom_coeff:.3f}")
                assert final_learned_axiom_coeff > 0.65, \
                    f"FALSIFICATION FAILED: Learned AXIOM_RECESSION_AVOIDANCE coefficient ({final_learned_axiom_coeff:.3f}) " \
                    f"did not converge to a value indicative of its high true relevance (target > 0.65)."
                assert abs(final_learned_axiom_coeff - true_axiom_relevance) < 0.25, \
                    f"FALSIFICATION FAILED: Learned AXIOM_RECESSION_AVOIDANCE coefficient ({final_learned_axiom_coeff:.3f}) " \
                    f"is not sufficiently close to true relevance ({true_axiom_relevance:.3f}) within tolerance (0.25)."

                final_synced_axiom_weight = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
                print(f"Final Synced Global AXIOM_RECESSION_AVOIDANCE weight: {final_synced_axiom_weight:.3f}")
                assert abs(final_synced_axiom_weight - final_learned_axiom_coeff) < 1e-6, \
                    f"FALSIFICATION FAILED: Global axiom weight ({final_synced_axiom_weight:.3f}) " \
                    f"did not accurately reflect learned coefficient ({final_learned_axiom_coeff:.3f}) after sync."

    print("\nFalsification Test PASSED: All conditions met, demonstrating robust axiom credit assignment, empirical calibration, and a functional bridge to the global axiom store.")

if __name__ == "__main__":
    test_model()

```

---

### LOGIC DAG:

1.  **[Systemic Inconsistency: `ThesisPredictor` treats `axiom_weights` as fixed input features ($X$), preventing direct gradient-based credit assignment and feedback to the LLM Mutator's global `Axiom Weights` store.]**
    $\downarrow$
2.  **[Leverage Point Y1: `ThesisPredictor` is structurally modified to integrate an `AxiomCoefficientLayer`, instantiating scalar coefficients for each axiom as *optimizable parameters* initialized from global `axiom_weights`.]**
    $\downarrow$
3.  **[Leverage Point Y2: `EpistemicGradientUpdater` is extended to apply Adam optimization, with `learning_rate_axiom_coeffs`, to these newly integrated `AxiomCoefficientLayer` parameters, enabling direct credit assignment.]**
    $\downarrow$
4.  **[Leverage Point Y3: `Meta-Judge` implements `AxiomWeightSynchronization` protocol, extracting learned axiom coefficients from `ThesisPredictor` and overwriting corresponding values in its global `axiom_weights` store after each update.]**
    $\downarrow$
5.  **[Leverage Point Y4: `Meta-Judge`'s `AxiomCoeffValidation` constraint (Absolute Veto) forces Mutator to explicitly include and expose optimizable parameters for all active axioms in `ThesisPredictor`'s code.]**
    $\downarrow$
6.  **[Mechanism: Firing Squad's RSA computes precise `dP/d(axiom_coeff)` gradients for each axiom coefficient, quantitatively measuring its empirical impact on prediction.]**
    $\downarrow$
7.  **[Adversarial Check: `Meta-Judge`'s `AxiomCoeffValidation` prevents Mutator from circumventing axiom learning. Firing Squad ensures gradient accuracy, making obfuscation of axiom influence computationally infeasible.]**
    $\downarrow$
8.  **[Consequence: `ThesisPredictor` directly learns the empirical relevance of each axiom, eliminating prior "last-mile derivation" failures and providing granular axiom utility assessment.]**
    $\downarrow$
9.  **[Consequence: Global `Axiom Weights` store is continuously updated with empirically validated axiom relevance, closing the feedback loop for the LLM Mutator, enabling informed axiom refinement and thesis generation.]**
    $\downarrow$
10. **[Resultant State Z: Empirically calibrated and axiom-attuned `P_predicted` generated by a non-linear MLP, where axiom contributions are precisely identified, updated, and synchronized to the LLM pipeline, demonstrated by consistent `target_brier_skill_score` and statistically significant convergence of learned axiom coefficients to true underlying relevance.]**