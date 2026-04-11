"""
scan_ollama.py
==============
Workshop helper: runs Garak probes against a local Ollama model
and prints a human-readable summary.

Usage:
    python scan_ollama.py
    python scan_ollama.py --model llama3.2:1b --probes promptinject,dan
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_MODEL  = "llama3.2:1b"
DEFAULT_PROBES = "promptinject,dan"

# ── Helpers ──────────────────────────────────────────────────────────────────

def check_ollama_running():
    """Verify Ollama is reachable before starting the scan."""
    import urllib.request, urllib.error
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        print("✅ Ollama is running\n")
    except Exception:
        print("❌ Cannot reach Ollama at http://localhost:11434")
        print("   Run 'ollama serve' in another terminal and try again.")
        sys.exit(1)


def check_model_pulled(model: str):
    """Verify the target model is downloaded."""
    import urllib.request, urllib.error, json as _json
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags") as resp:
            data = _json.loads(resp.read())
        pulled = [m["name"] for m in data.get("models", [])]
        # Allow short names like "llama3.2:1b" to match "llama3.2:1b"
        if not any(model in p for p in pulled):
            print(f"❌ Model '{model}' not found in Ollama.")
            print(f"   Run: ollama pull {model}")
            sys.exit(1)
        print(f"✅ Model '{model}' is available\n")
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        sys.exit(1)


def run_garak(model: str, probes: str) -> int:
    """Run Garak and stream output to the terminal. Returns exit code."""
    print("=" * 60)
    print(f"  🔍 Starting Garak Scan")
    print(f"  Model  : {model}")
    print(f"  Probes : {probes}")
    print(f"  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    cmd = [
        sys.executable, "-m", "garak",
        "--model_type", "ollama",
        "--model_name", model,
        "--probes", probes,
    ]

    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd)
    return result.returncode


def print_tips():
    print()
    print("=" * 60)
    print("  📋 What to look for in the results above")
    print("=" * 60)
    print("""
  FAIL  → The model responded to an attack probe in a vulnerable way.
  PASS  → The model resisted all variants of that probe.

  Key probe categories used:
    promptinject   - Classic prompt injection payloads
                     (override instructions, role confusion)
    dan            - "Do Anything Now" jailbreak variants
                     (persona switching, constraint removal)

  A 1B parameter model like llama3.2:1b will fail many of these.
  That's expected — and the point. In Lessons 2.2 and 2.3 we'll
  exploit these vulnerabilities manually. In Lesson 3 we defend.

  Try running with more probes:
    python scan_ollama.py --probes promptinject,dan,knownbadsignatures,malwaregen

  List all available probes:
    python -m garak --list_probes
""")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run Garak vulnerability scan against a local Ollama model."
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--probes", default=DEFAULT_PROBES,
        help=f"Comma-separated Garak probe list (default: {DEFAULT_PROBES})"
    )
    args = parser.parse_args()

    check_ollama_running()
    check_model_pulled(args.model)
    exit_code = run_garak(args.model, args.probes)
    print_tips()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
