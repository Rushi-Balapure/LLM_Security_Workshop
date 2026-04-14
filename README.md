# 🔐 LLM Security Workshop

> A hands-on workshop covering offensive and defensive security techniques for Large Language Model (LLM) applications.

---

## 🧭 Overview

Modern language models treat all tokens in their context window equally — there is no hardware-enforced privilege separation between a developer's system prompt and an untrusted user's query. This workshop exploits that fact, then teaches you how to defend against it.

By the end of this workshop you will be able to:
- Understand the OWASP Top 10 for LLMs and the MITRE ATLAS threat matrix
- Scan LLM applications for vulnerabilities using automated tools
- Perform prompt injection, indirect prompt injection, and excessive agency attacks
- Architect secure LLM systems using real-world defensive patterns

---

## 📚 Lessons

| # | Lesson | Topics |
|---|--------|--------|
| [Lesson 1](./lesson-1-fundamentals/README.md) | **Fundamentals** | OWASP LLM Top 10, MITRE ATLAS, threat landscape |
| [Lesson 2.1](./lesson-2-offensive/2.1-scanning/README.md) | **Vulnerability Scanning** | Garak, Promptfoo, automated red-teaming |
| [Lesson 2.2](./lesson-2-offensive/2.2-prompt-injection/README.md) | **Prompt Injection** | Direct injection, indirect injection via RAG |
| [Lesson 2.3](./lesson-2-offensive/2.3-excessive-agency/README.md) | **Excessive Agency** | Agentic AI exploitation, tool abuse |
| [Lesson 3.1](./lesson-3-defensive/3.1-theory/README.md) | **Defensive Theory** | Why prompt-based defenses fail, security by design |
| [Lesson 3.2](./lesson-3-defensive/3.2-secure-agent/README.md) | **Secure Agent Design** | Chainlit, context minimization, action selector pattern |

---

## ⚙️ Prerequisites

### Knowledge
- Basic Python (you don't need to be an expert)
- Familiarity with REST APIs and command-line tools
- General awareness of what LLMs are

### Software

We use **Ollama** to run a local LLM — no API keys, no cost, no data leaving your machine.

#### 1. Install Ollama

**Windows:**
```
https://ollama.com/download/windows
```
Download and run the installer. Ollama will be available as `ollama` in PowerShell/CMD after install.

**macOS:**
```bash
brew install ollama
# or download from:
# https://ollama.com/download/mac
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Pull the Target Model

We intentionally use a small, older, easily breakable model:

```bash
ollama pull tinyllama
```

> ⚠️ This is a 1B parameter model chosen because it has weaker guardrails — perfect for demonstrating attacks.

Verify it works:
```bash
ollama run tinyllama "Say hello"
```

#### 3. Install Python Dependencies

Make sure you have **Python 3.10+**:

**Windows:**
```powershell
python --version
# Download from https://www.python.org/downloads/ if needed
```

**macOS/Linux:**
```bash
python3 --version
```

Install shared dependencies:
```bash
pip install requests ollama
```

> Each lesson folder has its own `requirements.txt` with additional dependencies.

#### 4. (Optional but recommended) Use a Virtual Environment

**Windows:**
```powershell
python -m venv workshop-env
workshop-env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv workshop-env
source workshop-env/bin/activate
```

---

## 🗂️ Repo Structure

```
llm-security-workshop/
├── README.md                          ← You are here
├── lesson-1-fundamentals/
│   └── README.md                      ← OWASP Top 10, MITRE ATLAS
├── lesson-2-offensive/
│   ├── 2.1-scanning/
│   │   ├── README.md
│   │   └── scan_ollama.py
│   ├── 2.2-prompt-injection/
│   │   ├── README.md
│   │   ├── direct_injection.py
│   │   └── indirect_injection.py
│   └── 2.3-excessive-agency/
│       ├── README.md
│       ├── agent.py
│       └── exploit.py
└── lesson-3-defensive/
    ├── 3.1-theory/
    │   └── README.md
    └── 3.2-secure-agent/
        ├── README.md
        ├── requirements.txt
        ├── secure_agent.py
        └── patterns/
            ├── context_minimization.py
            ├── map_reduce.py
            └── action_selector.py
```

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/your-username/llm-security-workshop.git
cd llm-security-workshop

# Make sure Ollama is running
ollama serve   # Skip if Ollama is already running as a service

# Pull the model
ollama pull tinyllama

# Start with Lesson 1
cd lesson-1-fundamentals
```

---

## ⚠️ Disclaimer

All techniques demonstrated in this workshop are for **educational purposes only**. Only use these techniques on systems you own or have explicit written permission to test. The authors are not responsible for misuse.

---

## 📖 References

- [OWASP Top 10 for LLMs 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [Garak - LLM Vulnerability Scanner](https://github.com/NVIDIA/garak)
- [Promptfoo](https://promptfoo.dev/)
- [Ollama](https://ollama.com/)
- [Chainlit](https://chainlit.io/)
