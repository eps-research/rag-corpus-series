#!/usr/bin/env python3
"""
EPS Research — Omega Formula Enforcement
=========================================
Rejects any commit containing the compact or erroneous Eq.6 form.
Enforces named-term form only.

CANONICAL (only acceptable form):
    outer_term = V2 / R2
    inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term
    omega_rad_gyr = omega_kms_kpc * 1.0227  # 1 km/s/kpc = 1.0227 rad/Gyr

BANNED patterns:
    Formula A (original bug):  (V2/R2 - V1/R1) * (R1/R2)**1.5
    Compact form (also banned): V2/R2 - (V1/R1) * (R1/R2)**1.5
    Wrong conversion direction: / 1.0227  (dividing instead of multiplying)

Usage:
    python3 check_omega_formula.py [files...]   # check specific files
    python3 check_omega_formula.py              # check all staged files (pre-commit mode)

Install as pre-commit hook:
    cp check_omega_formula.py .git/hooks/
    cat > .git/hooks/pre-commit << 'EOF'
    #!/bin/bash
    python3 "$(git rev-parse --show-toplevel)/.git/hooks/check_omega_formula.py"
    EOF
    chmod +x .git/hooks/pre-commit
"""

import re
import subprocess
import sys
import os

# ── Banned patterns ────────────────────────────────────────────────────────────

BANNED = [
    (
        # Formula A — the original parenthesization bug
        re.compile(r'\(\s*V2\s*/\s*R2\s*-\s*V1\s*/\s*R1\s*\)\s*\*\s*\(?\s*R1\s*/\s*R2\s*\)?\s*\*\*\s*1\.5'),
        "FORMULA A (parenthesization bug): (V2/R2 - V1/R1) * (R1/R2)**1.5  ← WRONG"
    ),
    (
        # Compact form — mathematically correct but banned by Sol 5.6 requirement
        re.compile(r'V\w*\s*/\s*R\w*\s*-\s*\(\s*V\w*\s*/\s*R\w*\s*\)\s*\*\s*\(?\s*R\w*\s*/\s*R\w*\s*\)?\s*\*\*\s*1\.5'),
        "COMPACT FORM (banned): V2/R2 - (V1/R1) * (R1/R2)**1.5  ← use named-term form"
    ),
    (
        # Wrong unit conversion direction
        re.compile(r'omega[_a-z]*\s*/=?\s*1\.022\d*\b'),
        "WRONG CONVERSION: dividing by 1.0227 reverses units  ← multiply: omega_rad_gyr = omega_kms_kpc * 1.0227"
    ),
]

# ── File extensions to check ───────────────────────────────────────────────────

CHECK_EXTENSIONS = {'.py', '.ipynb', '.md', '.txt', '.tex', '.rst'}

SKIP_PATHS = {
    'CORRECTIONS.md',       # correction notice intentionally shows old formula
    'flynn2026_sign_reversal',  # manuscript may quote old formula for correction purposes
    'audit_omega',          # audit scripts test for the banned pattern
    'check_omega_formula',  # this script itself
    'fix_named_terms',      # remediation script
}


def should_skip(filepath):
    name = os.path.basename(filepath)
    for skip in SKIP_PATHS:
        if skip in filepath:
            return True
    return False


def check_file(filepath):
    """Returns list of (line_number, pattern_description, line_content) violations."""
    violations = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                for pattern, description in BANNED:
                    if pattern.search(line):
                        violations.append((lineno, description, line.rstrip()))
    except (IOError, OSError) as e:
        print(f"  WARNING: could not read {filepath}: {e}")
    return violations


def get_staged_files():
    """Get list of staged files from git."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        mode = "explicit"
    else:
        files = get_staged_files()
        mode = "pre-commit"

    if not files:
        print("check_omega_formula: no files to check.")
        sys.exit(0)

    print(f"check_omega_formula: checking {len(files)} file(s) [{mode} mode]")

    total_violations = 0
    flagged_files = 0

    for filepath in files:
        # Skip non-text or explicitly excluded files
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in CHECK_EXTENSIONS:
            continue
        if should_skip(filepath):
            continue
        if not os.path.exists(filepath):
            continue

        violations = check_file(filepath)
        if violations:
            flagged_files += 1
            total_violations += len(violations)
            print(f"\n  ❌ {filepath}")
            for lineno, desc, line in violations:
                print(f"     Line {lineno}: {desc}")
                print(f"     >>> {line[:120]}")

    if total_violations:
        print(f"""
{'='*60}
COMMIT BLOCKED — {total_violations} banned omega formula pattern(s) in {flagged_files} file(s)

Required form (Flynn & Cannaliato 2025 Eq.6):

    outer_term    = V2 / R2
    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term
    omega_rad_gyr = omega_kms_kpc * 1.0227  # 1 km/s/kpc = 1.0227 rad/Gyr

Fix the formula, then re-stage and commit.
See CORRECTIONS.md for full context.
{'='*60}
""")
        sys.exit(1)
    else:
        print("  ✓ No banned omega formula patterns found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
