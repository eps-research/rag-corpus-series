#!/usr/bin/env python3
"""
EPS Research — Named-term Eq.6 formula replacement v2
======================================================
Operates on parsed notebook JSON — safe for Jupyter .ipynb files.
No raw string replacement; modifies cell source lists directly.

CANONICAL FORM (Sol 5.6 requirement):
    outer_term    = (V2 / R2)
    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term
    omega_rad_gyr = omega_kms_kpc * 1.0227  # 1 km/s/kpc = 1.0227 rad/Gyr
"""

import json
import os
import re

REPO = os.environ.get("REPO", os.path.expanduser(
    "~/Documents/Astrophysics/rag-corpus-series"))

FILES = [
    f"{REPO}/QuickStart.ipynb",
    f"{REPO}/examples/highz/hz_nb3_eps_omega_bridge.ipynb",
    f"{REPO}/examples/hi/ex03_omega_correction_ddo161.ipynb",
]

# Named-term block — used in executable cells (indented versions built per-call)
def named_term_block(indent=""):
    return [
        f"{indent}outer_term    = (V2 / R2)\n",
        f"{indent}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n",
        f"{indent}omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n",
        f"{indent}omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n",
    ]

def named_term_comment_block(indent="# "):
    return [
        f"{indent}Flynn & Cannaliato (2025) Eq.6 — named-term form (Sol 5.6 hardened):\n",
        f"{indent}  outer_term    = (V2 / R2)\n",
        f"{indent}  inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n",
        f"{indent}  omega_kms_kpc = outer_term - inner_term        [km/s/kpc]\n",
        f"{indent}  omega_rad_gyr = omega_kms_kpc * 1.0227         [rad/Gyr]  (1 km/s/kpc = 1.0227 rad/Gyr)\n",
    ]

# Patterns to find and replace within individual source lines
LINE_REPLACEMENTS = [
    # Compact executable forms → named-term
    (
        re.compile(r'^(\s*)omega\s*=\s*V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5(.*)$'),
        lambda m: named_term_block(m.group(1)) + ([f"{m.group(1)}omega = omega_rad_gyr  # canonical output in rad/Gyr\n"] if m.group(2).strip() else []),
        "compact omega = V2/R2 - (V1/R1)*..."
    ),
    (
        re.compile(r'^(\s*)om\s*=\s*V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5(.*)$'),
        lambda m: named_term_block(m.group(1)) + [f"{m.group(1)}om = omega_rad_gyr  # canonical output in rad/Gyr\n"],
        "compact om = V2/R2 - (V1/R1)*..."
    ),
    # Comment forms
    (
        re.compile(r'^(\s*#\s*)omega\s*=\s*V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5(.*)$'),
        lambda m: [
            f"{m.group(1)}outer_term    = (V2 / R2)\n",
            f"{m.group(1)}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n",
            f"{m.group(1)}omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6\n",
            f"{m.group(1)}omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n",
        ],
        "comment # omega = V2/R2 - (V1/R1)*..."
    ),
    # Wrong units claim
    (
        re.compile(r'^(.*)already in consistent units(.*)$'),
        lambda m: [f"{m.group(1)}multiply by 1.0227 to convert km/s/kpc -> rad/Gyr{m.group(2)}\n"],
        "wrong: already in consistent units"
    ),
    (
        re.compile(r'^(.*)1 rad/Gyr = 1\.022\d* km/s/kpc(.*)$'),
        lambda m: [f"{m.group(1)}1 km/s/kpc = 1.0227 rad/Gyr  (multiply raw Eq.6 output by 1.0227 to convert){m.group(2)}\n"],
        "wrong units direction: 1 rad/Gyr = 1.022 km/s/kpc"
    ),
    # Markdown/comment inline formula (not LaTeX)
    (
        re.compile(r'^(\s*)omega\s*=\s*V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\^.*\[rad/Gyr\](.*)$'),
        lambda m: [
            f"{m.group(1)}outer_term    = (V2 / R2)\n",
            f"{m.group(1)}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n",
            f"{m.group(1)}omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n",
            f"{m.group(1)}omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n",
        ],
        "markdown omega = V2/R2... [rad/Gyr]"
    ),
]

# LaTeX patterns to fix in markdown cells
LATEX_REPLACEMENTS = [
    # Formula A in LaTeX: \left(\frac{V_2}{R_2} - \frac{V_1}{R_1}\right)\left(... — WRONG grouping
    (
        re.compile(r'\\left\(\\frac\{V_2\}\{R_2\}\s*-\s*\\frac\{V_1\}\{R_1\}\\right\)\\left\(\\frac\{R_1\}\{R_2\}\\right\)\^'),
        r'\\frac{V_2}{R_2} - \\frac{V_1}{R_1}\\left(\\frac{R_1}{R_2}\\right)^',
        "LaTeX Formula A grouping error"
    ),
]


def fix_source_lines(lines, filepath_hint=""):
    """Process a cell's source line list, returning fixed lines and count of changes."""
    new_lines = []
    changes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # Strip trailing newline for matching, preserve it
        stripped = line.rstrip('\n')
        matched = False
        for pattern, replacement, desc in LINE_REPLACEMENTS:
            m = pattern.match(stripped)
            if m:
                result = replacement(m)
                new_lines.extend(result)
                changes += 1
                print(f"    fixed: {desc}")
                matched = True
                break
        if not matched:
            new_lines.append(line)
        i += 1
    return new_lines, changes


def fix_latex_in_source(source_str):
    """Fix LaTeX formula errors in markdown source strings."""
    changes = 0
    for pattern, replacement, desc in LATEX_REPLACEMENTS:
        new_str, n = pattern.subn(replacement, source_str)
        if n:
            source_str = new_str
            changes += n
            print(f"    fixed LaTeX: {desc}")
    return source_str, changes


def process_notebook(filepath):
    print(f"\n=== {os.path.basename(filepath)} ===")

    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    total_changes = 0

    for cell_idx, cell in enumerate(nb['cells']):
        cell_type = cell.get('cell_type', '')
        source = cell.get('source', [])

        # Normalise: source can be list or string
        if isinstance(source, str):
            source = source.splitlines(keepends=True)

        if cell_type == 'code':
            new_source, n = fix_source_lines(source, filepath)
            if n:
                cell['source'] = new_source
                total_changes += n

        elif cell_type == 'markdown':
            # Join, fix LaTeX, re-split
            joined = ''.join(source)
            fixed, n = fix_latex_in_source(joined)
            if n:
                cell['source'] = fixed.splitlines(keepends=True)
                total_changes += n

    if total_changes == 0:
        print("  No changes needed.")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write('\n')

    print(f"  Written ({total_changes} change(s))")
    return True


def verify(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON INVALID: {filepath}: {e}")
        return

    issues = []
    for cell in nb['cells']:
        src = ''.join(cell.get('source', []))
        if re.search(r'V2/R2\s*-\s*\(V1/R1\)', src):
            issues.append("compact form still present")
        if re.search(r'\(V2/R2\s*-\s*V1/R1\)', src):
            issues.append("Formula A still present")
        if re.search(r'omega\w*\s*/\s*1\.022', src):
            issues.append("wrong unit division still present")
        if 'already in consistent units' in src:
            issues.append("'already in consistent units' still present")

    if issues:
        print(f"  ❌ {os.path.basename(filepath)}: {'; '.join(issues)}")
    else:
        print(f"  ✓  {os.path.basename(filepath)}: JSON valid, no banned patterns")


if __name__ == '__main__':
    print("Named-term Eq.6 replacement v2 (JSON-safe)")
    print("Sol 5.6: outer_term / inner_term / * 1.0227")
    print("=" * 60)

    changed = 0
    for f in FILES:
        if not os.path.exists(f):
            print(f"\nMISSING: {f}")
            continue
        if process_notebook(f):
            changed += 1

    print("\n--- Verification ---")
    for f in FILES:
        if os.path.exists(f):
            verify(f)

    print(f"\nDone. {changed}/{len(FILES)} files modified.")
    print("Next: git diff to review, then commit.")
