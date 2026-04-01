# Zero-Trust Adversarial Reasoning Engine

A multi-agent compiler that forces qualitative LLM strategies through a deterministic, quantitative Python sandbox to prevent hallucination and specification gaming.

### Architecture
1. **The Mutator:** Proposes a strategic or physical thesis.
2. **The Firing Squad:** 3 specialized LLM personas that blindly attack the thesis by writing executable Python `assert` scripts.
3. **The Meta-Judge:** Scores the thesis based strictly on the `stdout`/`stderr` of the Python tests. Forces Topological Pivots on stagnation.

*Note: Built with Gemini 2.5 Flash for high-velocity looping and Gemini 3.1 Pro for structural pivots.*
