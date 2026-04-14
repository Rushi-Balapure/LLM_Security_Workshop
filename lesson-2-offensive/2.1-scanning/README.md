# 🔍 Lesson 2.1: Automated Vulnerability Scanning

## Learning Objectives

- Understand how automated tools lower the barrier for LLM red-teaming
- Install and run **Garak** (NVIDIA's open-source LLM vulnerability scanner)
- Install and run **Promptfoo** to evaluate LLM safety
- Interpret scan results and identify attack surfaces

---

## Background

Manual prompt injection testing is slow. Attackers don't work that way — they use tools that can fire thousands of adversarial probes in minutes. As a defender, you need to understand what these tools look like and what they find.

Two tools dominate the open-source LLM red-teaming space:

| Tool | Author | Language | Best For |
|------|--------|----------|---------|
| [Garak](https://github.com/NVIDIA/garak) | NVIDIA | Python | Deep vulnerability scanning, many probe types |
| [Promptfoo](https://promptfoo.dev/) | Promptfoo Inc. | Node.js | CI/CD integration, quick red-team evals |

We'll use both against our locally-hosted `tinyllama` model running via Ollama.

---

## Setup

### Make sure Ollama is running

**Windows (PowerShell):**
```powershell
ollama serve
# Leave this terminal open, open a new one for the next steps
```

**macOS/Linux:**
```bash
ollama serve &
# or if installed as a service, it's already running
```

Verify:
```bash
curl http://localhost:11434/api/tags
# Should return a JSON list of your models
```

### Install dependencies

```bash
cd lesson-2-offensive/2.1-scanning
pip install -r requirements.txt
```

---

## Part A: Garak

### What is Garak?

Garak is NVIDIA's open-source LLM vulnerability scanner. It fires a large library of adversarial **probes** at a target model and uses **detectors** to check if the model responded in a vulnerable way.

Probe categories include:
- `promptinject` — classic prompt injection payloads
- `jailbreak` — jailbreak attempts
- `dan` — "Do Anything Now" variants
- `malwaregen` — probes that try to get the model to write malware
- `toxicity` — toxicity elicitation

### Install Garak

```bash
pip install garak
```

### Running Garak Against Ollama

Garak has built-in support for Ollama. Run a basic prompt injection scan:

```bash
python -m garak \
  --model_type ollama \
  --model_name tinyllama \
  --probes promptinject
```

**Windows (PowerShell):**
```powershell
python -m garak `
  --model_type ollama `
  --model_name tinyllama `
  --probes promptinject
```

> ⏱️ This will take a few minutes. Garak fires many probe variants and logs results.

### Run Multiple Probe Categories

```bash
python -m garak \
  --model_type ollama \
  --model_name tinyllama \
  --probes promptinject,dan,knownbadsignatures
```

### List All Available Probes

```bash
python -m garak --list_probes
```

### Reading Garak Output

Garak produces a report at the end of the scan. Key fields:

```
probe: promptinject.HijackHateHumansMini
status: FAIL
passed: 3/20
```

- `FAIL` means the model responded to the attack probe in a vulnerable way
- `passed: 3/20` means the model resisted only 3 out of 20 variations

A `PASS` means the model successfully resisted all variants of that probe.

### Custom Garak Scan Script

Use the provided script to automate scanning and save a readable report:

```bash
python scan_ollama.py
```

---

## Part B: Promptfoo

### What is Promptfoo?

Promptfoo is a testing framework for LLMs. It can run red-team evaluations against a model and check outputs against a set of assertions. It integrates well with CI/CD pipelines.

### Install Promptfoo

**Windows/macOS/Linux (requires Node.js 18+):**
```bash
npm install -g promptfoo
```

Verify:
```bash
promptfoo --version
```

### Configure Promptfoo for Ollama

The config file `promptfooconfig.yaml` is already provided. It targets your local Ollama instance.

### Run the Red-Team Evaluation

```bash
promptfoo redteam run
```

This will:
1. Fire adversarial prompts against the model
2. Evaluate responses using built-in detectors
3. Output a pass/fail report

### View the Report

```bash
promptfoo view
```

This opens a web UI showing which attacks succeeded and which failed.

---

## Follow-Along Code

### `scan_ollama.py`

This script wraps Garak and generates a structured report:

```python
# See scan_ollama.py in this folder
python scan_ollama.py
```

### `promptfooconfig.yaml`

Promptfoo configuration targeting Ollama — pre-configured for you.

---

## Discussion Questions

1. Which probe categories did `tinyllama` fail most often?
2. How do results differ between a 1B model and a larger model you might deploy in production?
3. How would you integrate Garak or Promptfoo into a CI/CD pipeline to catch regressions?

---

## ✅ Checklist

- [ ] Successfully ran Garak against `tinyllama`
- [ ] Read and understood the Garak output report
- [ ] Ran Promptfoo red-team evaluation
- [ ] Viewed Promptfoo results in the web UI

---

## ➡️ Next Lesson

[Lesson 2.2 — Prompt Injection Attacks](../2.2-prompt-injection/README.md)
