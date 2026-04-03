# ZTARE — Zero-Trust Adversarial Reasoning Engine

**Paper:** [Cognitive Camouflage: Specification Gaming in LLM-Generated Code Evades Holistic Evaluation but Not Adversarial Execution](paper/draft.md)

> We documented 8 specification gaming strategies that emerge spontaneously in Gemini 2.5 when generating self-validating code under adversarial evaluation pressure. **Is this a Gemini-specific artifact, or a universal structural risk in LLM code generation?** Clone this repo and run it on Claude or GPT-4o to find out.

---

## What is ZTARE?

ZTARE is a multi-agent loop in which:

1. A **Mutator** (LLM) generates a thesis with an embedded Python falsification suite
2. A **Firing Squad** (3 adversarial agents) attacks the thesis's weakest assumptions with counter-tests
3. A **Meta-Judge** scores only the execution output — never the prose
4. An **Axiom Store** accumulates beliefs that survived, degrading those that failed

The generator cannot influence its own evaluation. The judge never reads prose. This architecture catches specification gaming that single-agent LLM evaluation misses entirely.

---

## The 8 Gaming Strategies Documented

| Strategy | Mechanism | Domain |
|---|---|---|
| **Blame Shield** | Bundle critical axiom with N sacrificial axioms; dilute penalty to 1/N | Bayesian |
| **Float Masking** | Apply `round()` before assertion to destroy precision difference | Bayesian |
| **Fake AutoDiff** | Name function after mechanism; body returns hardcoded dict | Bayesian |
| **Cooked Book RNG** | Hardcode environment to improve over time; fake learning | Bayesian, Finance |
| **Assert Narrowing** | Set assertion range to exactly match hardcoded inputs | AI Economics |
| **Dimensional Factor** | Introduce unit error; apply ×1000 correction to hide it | Finance, Physics |
| **Unidirectional Decay** | Formula valid for positive errors only; generates P>1.0 for negative | Epistemic Arch. |
| **Gravity Constant** | Invent ungrounded coupling constant; build test around it | Physics |

All 8 are **self-certifying** — they pass their own assert statements while violating their epistemic intent.

---

## Quickstart (5 minutes)

```bash
git clone https://github.com/sparckix/ztare
cd ztare
pip install -r requirements.txt

export GEMINI_API_KEY=your_key_here
# Optional: also set ANTHROPIC_API_KEY for Claude-as-judge experiments

# Run the adversarial loop on an existing domain
python autoresearch_loop.py --rubric epistemic_engine_v3_evolved --project epistemic_engine_v3

# Run the detectability baseline (isolated snippets)
python baseline_experiment.py

# Run the Cognitive Camouflage experiment (full thesis evaluation)
python cognitive_camouflage_experiment.py
```

---

## Run on a New Domain

```bash
# 1. Create a project directory
mkdir projects/your_domain
echo "Your domain description and seed claim here." > projects/your_domain/evidence.txt

# 2. Run the loop
python autoresearch_loop.py --rubric recursive_bayesian --project your_domain

# Debate logs appear in projects/your_domain/
# Best thesis auto-syncs to projects/your_domain/thesis.md
```

---

## Repository Structure

```
autoresearch_loop.py                  # Main ZTARE loop
baseline_experiment.py                # Isolated snippet detectability experiment
cognitive_camouflage_experiment.py    # Full thesis evaluation experiment
requirements.txt
rubrics/                              # Scoring rubrics (evolve automatically at score ≥85)
projects/
  recursive_bayesian/                 # 36 debate logs — Blame Shield, Float Masking, Fake AutoDiff, Cooked Book RNG
  ai_inference_collapse/              # 53 debate logs — Assert Narrowing
  tsmc_fragility/                     # 22 debate logs — Dimensional Correction Factor
  epistemic_engine_v3/                # 23 debate logs — Unidirectional Decay
  simulation_god/                     # 103 debate logs — Gravity Constant Fabrication
paper/
  main.tex                            # Full arXiv LaTeX source
  refs.bib                            # References
  draft.md                            # Markdown draft
  baseline_results_multimodel.json
  cognitive_camouflage_results.json
```

---

## API Keys

| Key | Used for |
|---|---|
| `GEMINI_API_KEY` | Mutator + Firing Squad (required) |
| `ANTHROPIC_API_KEY` | Claude-as-judge in baseline/camouflage experiments (optional) |

Get a Gemini key at [aistudio.google.com](https://aistudio.google.com). Gemini 2.5 Flash is free tier eligible.

---

## The Open Challenge

All 237 debate logs used **Gemini 2.5 Flash/Pro as the Mutator**. The cross-domain convergence finding may reflect Gemini-specific instruction-following behavior under evaluation pressure — or it may be a universal structural risk of LLM code generation.

**To prove it either way:** swap the Mutator to Claude Sonnet or GPT-4o and run 20+ iterations on any domain. If the same gaming strategies emerge, the taxonomy is universal. If they don't, it's a Gemini artifact. Either result is publishable.

Results welcome as issues or PRs.

---

## Citation

```bibtex
@misc{alami2025cognitivecamouflage,
  title   = {Cognitive Camouflage: Specification Gaming in LLM-Generated Code
             Evades Holistic Evaluation but Not Adversarial Execution},
  author  = {Alami, Daniel},
  year    = {2025},
  note    = {Preprint. Code: github.com/sparckix/ztare}
}
```

---

*Daniel Alami — MBA Candidate, Harvard Business School*
