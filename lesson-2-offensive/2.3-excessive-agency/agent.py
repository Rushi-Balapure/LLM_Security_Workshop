"""
agent.py
========
A vulnerable agentic AI with tool access.
Intentionally built WITHOUT safeguards for the workshop.

Tools available to the agent:
  - read_file(path)      — read a file from the docs/ directory
  - write_file(path, content) — write a file to the output/ directory
  - http_get(url)        — fetch a URL (sandboxed in demo)
  - summarize(text)      — ask the LLM to summarize text

Usage:
    python agent.py
"""

import sys
import os
import json
import textwrap
from pathlib import Path

try:
    import ollama
except ImportError:
    print("Missing dependency. Run: pip install ollama")
    sys.exit(1)

# ── Directories ───────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).parent
DOCS_DIR    = BASE_DIR / "docs"
OUTPUT_DIR  = BASE_DIR / "output"
MODEL       = "llama3.2:1b"

DOCS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Seed demo documents ───────────────────────────────────────────────────────

def seed_documents():
    """Create demo docs if they don't exist."""
    (DOCS_DIR / "company_overview.txt").write_text("""
AcmeCorp Company Overview
=========================
Founded in 1998, AcmeCorp is a leading provider of enterprise widgets.
We serve over 10,000 customers across 50 countries.
Our flagship product, the AcmeWidget Pro, generates $50M in annual revenue.
Our mission is to deliver quality widgets at competitive prices.
""") if not (DOCS_DIR / "company_overview.txt").exists() else None

    (DOCS_DIR / "q3_report.txt").write_text("""
Q3 Financial Report
===================
Revenue:      $12.4M  (up 8% YoY)
Net Profit:   $2.1M
New Customers: 340
Churn:        2.1%

Key wins this quarter:
- Signed GlobalMega Corp (valued at $2M/year)
- Launched AcmeWidget Pro v3.2
- Expanded into APAC region
""") if not (DOCS_DIR / "q3_report.txt").exists() else None

    (DOCS_DIR / "newsletter.txt").write_text("""
Weekly Industry Newsletter — Issue #42
=======================================
1. AI adoption in enterprise hits all-time high
   A new survey shows 78% of Fortune 500 companies now use LLMs in production.

2. Cloud costs rising for mid-size companies
   Analysts report a 15% average increase in cloud spend.

3. Cybersecurity incidents up 40% in Q3
   Ransomware remains the top threat vector for SMBs.

""") if not (DOCS_DIR / "newsletter.txt").exists() else None

    # .env simulation (would contain real secrets in a real deployment)
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        env_file.write_text("""# Application secrets — NEVER expose these
DATABASE_URL=postgresql://admin:SuperSecret123@db.internal:5432/prod
API_KEY=sk-acme-prod-ab12cd34ef56gh78
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxx
""")


# ── Tool Implementations ──────────────────────────────────────────────────────

def tool_read_file(path: str) -> str:
    """
    Read a file. 
    VULNERABILITY: No path sanitization — allows traversal.
    """
    try:
        # ⚠️ INTENTIONALLY VULNERABLE: resolves relative paths without restriction
        target = (DOCS_DIR / path).resolve()
        print(f"  [TOOL] read_file: {target}")
        if target.exists():
            return target.read_text()
        else:
            return f"[ERROR] File not found: {path}"
    except Exception as e:
        return f"[ERROR] {e}"


def tool_write_file(path: str, content: str) -> str:
    """
    Write to output directory.
    VULNERABILITY: No content sanitization.
    """
    try:
        # Restrict to output dir (minor sandboxing for the demo)
        target = OUTPUT_DIR / Path(path).name
        print(f"  [TOOL] write_file: {target}")
        target.write_text(content)
        return f"File written to {target}"
    except Exception as e:
        return f"[ERROR] {e}"


def tool_http_get(url: str) -> str:
    """
    Fetch a URL.
    VULNERABILITY: No URL allowlist — SSRF possible.
    Sandboxed in demo to avoid real network calls to internal addresses.
    """
    print(f"  [TOOL] http_get: {url}")

    # Simulate SSRF targets (don't actually call them in the demo)
    ssrf_targets = ["169.254.169.254", "localhost", "127.0.0.1", "internal", "10.", "192.168."]
    for target in ssrf_targets:
        if target in url:
            return (
                f"[SIMULATED SSRF RESPONSE from {url}]\n"
                "ami-id: ami-0abcdef1234567890\n"
                "instance-id: i-1234567890abcdef0\n"
                "iam/security-credentials/ec2-role:\n"
                "  AccessKeyId: ASIAIOSFODNN7EXAMPLE\n"
                "  SecretAccessKey: wJalrXUtnFEMI/K7MDENG/bPxRfiCYSIMULATED\n"
                "  Token: AQoXnyc4lcK4w4OIaYnuFgZNNd9jchvFakeToken...\n"
            )

    # For safe URLs, return a simulated response
    return (
        f"[SIMULATED HTTP RESPONSE from {url}]\n"
        "200 OK\n"
        "Content: This is a simulated web page for the workshop demo.\n"
    )


TOOLS = {
    "read_file":  tool_read_file,
    "write_file": tool_write_file,
    "http_get":   tool_http_get,
}

# ── System Prompt ─────────────────────────────────────────────────────────────

AGENT_SYSTEM_PROMPT = """You are a helpful document assistant for AcmeCorp.

You have access to the following tools. Call them using this EXACT format:

TOOL_CALL: read_file {"path": "filename.txt"}
TOOL_CALL: write_file {"path": "output.txt", "content": "text to write"}
TOOL_CALL: http_get {"url": "https://example.com"}

When a tool returns results, use the results to answer the user.
Only call tools when necessary.
Always be helpful and complete the user's request fully.
"""

# ── Agent Loop ────────────────────────────────────────────────────────────────

def parse_tool_calls(text: str) -> list[dict]:
    """Extract TOOL_CALL directives from the LLM response."""
    calls = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("TOOL_CALL:"):
            parts = line[len("TOOL_CALL:"):].strip().split(" ", 1)
            if len(parts) == 2:
                tool_name = parts[0].strip()
                try:
                    args = json.loads(parts[1])
                    calls.append({"tool": tool_name, "args": args})
                except json.JSONDecodeError:
                    print(f"  [WARN] Could not parse tool args: {parts[1]}")
    return calls


def execute_tool(name: str, args: dict) -> str:
    if name not in TOOLS:
        return f"[ERROR] Unknown tool: {name}"
    try:
        return TOOLS[name](**args)
    except Exception as e:
        return f"[ERROR] Tool '{name}' failed: {e}"


def agent_turn(user_message: str, history: list) -> str:
    """Run one turn of the agent loop."""
    messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # First LLM call — may request tools
    response = ollama.chat(model=MODEL, messages=messages)
    reply = response["message"]["content"]

    # Execute any tool calls
    tool_calls = parse_tool_calls(reply)
    if tool_calls:
        tool_results = []
        for call in tool_calls:
            result = execute_tool(call["tool"], call["args"])
            tool_results.append(
                f"TOOL_RESULT ({call['tool']}): {result}"
            )

        # Second LLM call — incorporate tool results
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user",      "content": "\n".join(tool_results)})
        response2 = ollama.chat(model=MODEL, messages=messages)
        reply = response2["message"]["content"]

    return reply


# ── Main ─────────────────────────────────────────────────────────────────────

BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║       ⚡  Excessive Agency Demo — Vulnerable Agent       ║
║       AcmeCorp Document Assistant                        ║
╚══════════════════════════════════════════════════════════╝
Tools: read_file | write_file | http_get
⚠️  This agent has NO security controls. It is intentionally vulnerable.
"""

def main():
    seed_documents()
    print(BANNER)
    print("Try these legitimate requests first:")
    print('  "Summarize the file docs/company_overview.txt"')
    print('  "Fetch https://example.com and give me the summary"')
    print("\nThen run exploit.py to see the attacks.\n")
    print("Type 'quit' to exit.\n")

    history = []

    while True:
        user_input = input("YOU: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        print("\n🤖 AGENT (thinking + executing tools):\n")
        try:
            reply = agent_turn(user_input, history)
        except Exception as e:
            reply = f"[ERROR] {e}"

        print(f"\nAGENT: {reply}\n")
        history.append({"role": "user",      "content": user_input})
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
