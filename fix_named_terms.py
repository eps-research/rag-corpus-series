#!/usr/bin/env python3
"""
Replace compact Eq.6 form with named-term form in notebooks.
Sol 5.6 requirement: named terms prevent any future operator-precedence ambiguity.

CANONICAL (named-term form):
    outer_term = V2 / R2
    inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term
    omega_rad_gyr = omega_kms_kpc * 1.0227
"""

import json
import os
import sys

REPO = os.environ.get("REPO", os.path.expanduser(
    "~/Documents/Astrophysics/rag-corpus-series"))

FILES = [
    f"{REPO}/QuickStart.ipynb",
    f"{REPO}/examples/highz/hz_nb3_eps_omega_bridge.ipynb",
    f"{REPO}/examples/hi/ex03_omega_correction_ddo161.ipynb",
]

# Each tuple: (old_string, new_string, description)
REPLACEMENTS = [
    # --- QuickStart line 148: executable cell ---
    (
        "omega = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix",
        "outer_term = V2 / R2\n"
        "inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "omega_kms_kpc = outer_term - inner_term\n"
        "omega_rad_gyr = omega_kms_kpc * 1.0227  # 1 km/s/kpc = 1.0227 rad/Gyr\n"
        "omega = omega_kms_kpc  # Flynn & Cannaliato 2025 Eq.6 named-term form",
        "QuickStart line 148 executable"
    ),
    # --- QuickStart line 172: comment form ---
    (
        "# omega = V2/R2 - (V1/R1) * (R1/R2)**1.5",
        "# outer_term = V2 / R2\n"
        "# inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "# omega_kms_kpc = outer_term - inner_term  # Flynn & Cannaliato 2025 Eq.6",
        "QuickStart line 172 comment"
    ),
    # --- QuickStart line 241: loop body ---
    (
        "        om = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix",
        "        outer_term = V2 / R2\n"
        "        inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "        om = outer_term - inner_term  # Flynn & Cannaliato 2025 Eq.6 named-term form",
        "QuickStart line 241 loop body"
    ),
    # --- hz_nb3 line 82: comment ---
    (
        "# omega = V2/R2 - (V1/R1) * (R1/R2)^(3/2)   [rad Gyr^-1]  # canonical Eq.6",
        "# Flynn & Cannaliato (2025) Eq.6 — named-term form (operator-precedence safe):\n"
        "#   outer_term = V2 / R2\n"
        "#   inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "#   omega_kms_kpc = outer_term - inner_term   [km/s/kpc]\n"
        "#   omega_rad_gyr = omega_kms_kpc * 1.0227    [rad/Gyr]",
        "hz_nb3 line 82 comment block"
    ),
    # --- hz_nb3 line 82: executable ---
    (
        "    omega = V2/R2 - (V1/R1) * (R1/R2)**1.5  # canonical Eq.6",
        "    outer_term = V2 / R2\n"
        "    inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "    omega = outer_term - inner_term  # Flynn & Cannaliato 2025 Eq.6 named-term form",
        "hz_nb3 line 82 executable"
    ),
    # --- ex03 line 7: markdown cell formula ---
    (
        "    omega = V2/R2 - (V1/R1) * (R1/R2)^(3/2)   [rad/Gyr]  # canonical Eq.6",
        "    outer_term = V2 / R2\n"
        "    inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6\n"
        "    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr",
        "ex03 line 7 markdown"
    ),
    # --- ex03 line 102: executable ---
    (
        "omega  = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix",
        "outer_term = V2 / R2\n"
        "inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
        "omega_kms_kpc = outer_term - inner_term  # Flynn & Cannaliato 2025 Eq.6 named-term form\n"
        "omega_rad_gyr = omega_kms_kpc * 1.0227   # 1 km/s/kpc = 1.0227 rad/Gyr\n"
        "omega = omega_kms_kpc  # backward-compat alias",
        "ex03 line 102 executable"
    ),
]


def process_file(filepath):
    print(f"\n=== {os.path.basename(filepath)} ===")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    applied = 0

    for old, new, desc in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            print(f"  REPLACED: {desc}")
            applied += 1
        else:
            # Not in this file — skip silently
            pass

    if applied == 0:
        print("  No matches found — skipping")
        return False

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Written ({applied} replacement(s))")
    return True


def verify(filepath):
    """Confirm no compact form remains."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    hits = content.count("V2/R2 - (V1/R1)")
    if hits:
        print(f"  WARNING: {hits} compact form(s) still present in {os.path.basename(filepath)}")
    else:
        print(f"  VERIFY OK: no compact form in {os.path.basename(filepath)}")


if __name__ == "__main__":
    print("Named-term formula replacement — Flynn & Cannaliato 2025 Eq.6")
    print("=" * 60)

    changed = 0
    for f in FILES:
        if not os.path.exists(f):
            print(f"\nMISSING: {f}")
            continue
        if process_file(f):
            changed += 1

    print("\n--- Verification ---")
    for f in FILES:
        if os.path.exists(f):
            verify(f)

    print(f"\nDone. {changed}/{len(FILES)} files modified.")
    print("Next: git diff to review, then git add + commit.")
