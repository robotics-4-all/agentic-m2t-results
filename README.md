# zpaper_results

This folder contains the inputs and execution outputs of two end-to-end runs of the **agentic model-to-text (M2T) methodology**, used as examples in the accompanying paper.

## What is this methodology?

The agentic M2T pipeline takes a **textX grammar** (a DSL definition) and a set of **valid model samples** written in that DSL, then autonomously:

1. Generates Jinja2 templates that transform DSL models into executable Python code.
2. Iteratively refines those templates by validating the rendered outputs against the grammar and fixing errors.
3. Generates a per-sample test suite (pytest) that verifies the rendered code behaves correctly.
4. Packages each rendered sample into a self-contained Docker artifact (Dockerfile + entrypoint + tarball).

---

## Folder structure

```
.
├── calculator/
│   ├── input/                         # Calculator DSL inputs
│   │   ├── calculator.tx              # textX grammar for the calculator language
│   │   ├── requirements.txt
│   │   └── samples/
│   │       ├── valid/                 # 4 valid .calc models used as input
│   │       └── invalid/              # Invalid models (not processed)
│   └── results/                       # Calculator run output (2026-03-27)
│       ├── summary.json               # Run metadata and per-sample test statistics
│       ├── templates/                 # Generated Jinja2 templates (main + macros)
│       └── rendered_outputs/
│           ├── example{1-4}/          # Per-sample rendered artifacts
│           │   ├── output.py          # Python code rendered from the model
│           │   ├── test_example{N}.py # pytest test suite
│           │   ├── Dockerfile
│           └── └── entrypoint.sh
│           
│
└── smart_home/
    ├── input/                         # Smart Home DSL inputs
    │   ├── smartHome.tx               # textX grammar for the smart home language
    │   ├── requirements.txt
    │   └── samples/valid/             # 8 valid .smarthome models used as input
    └── results/                       # Smart Home run output (2026-04-01)
        ├── summary.json               # Run metadata and per-sample test statistics
        ├── templates/                 # Generated Jinja2 templates (main + macros + helpers)
        └── rendered_outputs/
            ├── model_{1-8}_*/         # Per-sample rendered artifacts
            │   ├── output.py          # Python simulation code rendered from the model
            │   ├── test_model_{N}_*.py # pytest test suite
            │   ├── Dockerfile
            │   ├── entrypoint.sh
            └── └── requirements.txt
            
```

---

## The two examples

### 1. Calculator

A simple arithmetic DSL that supports variable assignment, arithmetic expressions with operator precedence, parenthesized sub-expressions, and unary operators. The pipeline processed 4 valid model samples and generated 34 test functions across them, with 2 template refinement rounds and 0 validation errors in the final output.

### 2. Smart Home

A domain-specific language for describing IoT smart home simulations, covering MQTT/AMQP/Redis message brokers, sensor and actuator entities, value generators (Gaussian, sinusoidal, sawtooth, linear), noise wrappers, authentication schemes, and automation rules with compound conditions. The pipeline processed 8 valid model samples and generated 72 test functions across them, with 6 template refinement rounds and 0 validation errors in the final output.

---

## Key files per run

| File | Description |
|---|---|
| `summary.json` | Timestamp, grammar name, refinement count, validation errors, and per-sample test breakdown |
| `templates/main.jinja2` | Primary Jinja2 template that drives code generation |
| `templates/macros.jinja2` | Reusable rendering macros extracted by the agent |
| `templates/helpers.jinja2` | Additional helper macros (smart home run only) |
| `rendered_outputs/<sample>/output.py` | Final Python code produced from the DSL model |
| `rendered_outputs/<sample>/test_*.py` | pytest suite validating the rendered output |
| `rendered_outputs/<sample>/Dockerfile` | Container definition for isolated execution |
| `rendered_outputs/<sample>.tar.gz` | Self-contained archive of the full sample artifact |
