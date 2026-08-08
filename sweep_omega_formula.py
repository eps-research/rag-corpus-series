#!/usr/bin/env python3
"""
EPS Research — Bulk omega formula sweep
========================================
Replaces ALL compact Eq.6 forms across the entire repo.
Handles .py files and .ipynb files correctly.

Patterns replaced (all variants found in repo):
    omega  = V2/R2 - (V1/R1)*(R1/R2)**1.5
    omega = V2/R2 - (V1/R1)*(R1/R2)**1.5
    omega= V2/R2 - (V1/R1)*(R1/R2)**1.5
    omega=V2/R2 - (V1/R1)*(R1/R2)**1.5
    omega    = V2/R2 - (V1/R1)*(R1/R2)**1.5
    om = V2/R2 - (V1/R1)*(R1/R2)**1.5
    return V2/R2 - (V1/R1)*(R1/R2)**1.5
    dwarf_omegas.append(V2/R2 - (V1/R1)*(R1/R2)**1.5)
    omegas.append(V2/R2 - (V1/R1)*(R1/R2)**1.5)
    print(f"  omega = {V2/R2 - (V1/R1)*(R1/R2)**1.5:.3f}")
    # omega = V2/R2 - (V1/R1) * (R1/R2)**1.5  (comment forms in .md/.py)
"""

import json
import os
import re
import sys

REPO = os.environ.get("REPO", ".")

SKIP_FILES = {
    "CORRECTIONS.md",
    "check_omega_formula.py",
    "sweep_omega_formula.py",
    "fix_named_terms_v2.py",
    "audit_omega_remediation_v2.py",
}

SKIP_DIRS = {".git", "__pycache__", ".ipynb_checkpoints"}

# Regex: matches compact form with any variable name prefix and any whitespace
# Groups: (1) indent/prefix before the variable name, (2) lhs variable name, (3) trailing comment/suffix
COMPACT_RE = re.compile(
    r'^([ \t]*)'                          # indent
    r'(omega\s*=|omega\s{2,}=|om\s*=|'
    r'omega_kms_kpc\s*=)\s*'             # lhs
    r'V2\s*/\s*R2\s*-\s*\(V1\s*/\s*R1\)\s*\*\s*\(?R1\s*/\s*R2\)?\s*\*\*\s*1\.5'
    r'(.*?)$',                            # trailing comment
    re.MULTILINE
)

# append/return/print forms — inline, no assignment
INLINE_RE = re.compile(
    r'((?:append|return|print[^)]*)\([^)]*?)'
    r'V2\s*/\s*R2\s*-\s*\(V1\s*/\s*R1\)\s*\*\s*\(?R1\s*/\s*R2\)?\s*\*\*\s*1\.5'
    r'([^)]*\))',
    re.MULTILINE
)

# Comment forms in .py and .md
COMMENT_RE = re.compile(
    r'^([ \t]*#[ \t]*)'
    r'(?:omega\s*=\s*)?V2\s*/\s*R2\s*-\s*\(V1\s*/\s*R1\)\s*\*\s*\(?R1\s*/\s*R2\)?\s*\*\*\s*1\.5'
    r'(.*?)$',
    re.MULTILINE
)

# LaTeX Formula A in markdown: \left(\frac{V_2}{R_2} - \frac{V_1}{R_1}\right)\left(
LATEX_RE = re.compile(
    r'\\left\(\\frac\{V_2\}\{R_2\}\s*-\s*\\frac\{V_1\}\{R_1\}\\right\)'
    r'\\left\(\\frac\{R_1\}\{R_2\}\\right\)\^'
)

def named_block(indent, lhs_var, suffix):
    """Return named-term replacement lines for an assignment form."""
    i = indent
    # Determine output variable name
    lhs = lhs_var.strip().rstrip('=').strip()
    suffix = suffix.strip()
    comment = f"  # {suffix}" if suffix and not suffix.startswith('#') else (f"  {suffix}" if suffix else "")
    lines = [
        f"{i}outer_term    = (V2 / R2)",
        f"{i}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)",
        f"{i}omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]",
        f"{i}omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr",
    ]
    # Add alias if lhs is not omega_kms_kpc
    if lhs not in ('omega_kms_kpc', 'omega_rad_gyr'):
        lines.append(f"{i}{lhs} = omega_rad_gyr{comment}")
    return '\n'.join(lines)


def fix_py_content(content, filepath):
    changes = 0

    # Assignment forms
    def replace_compact(m):
        nonlocal changes
        changes += 1
        return named_block(m.group(1), m.group(2), m.group(3))
    content = COMPACT_RE.sub(replace_compact, content)

    # Comment forms → named-term comment block
    def replace_comment(m):
        nonlocal changes
        changes += 1
        i = m.group(1)
        return (f"{i}outer_term    = (V2 / R2)\n"
                f"{i}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
                f"{i}omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n"
                f"{i}omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr")
    content = COMMENT_RE.sub(replace_comment, content)

    # Inline append/return/print — warn, don't auto-fix (too risky)
    inline_hits = INLINE_RE.findall(content)
    if inline_hits:
        print(f"  ⚠️  {len(inline_hits)} inline form(s) need manual fix in {filepath}")

    return content, changes


def fix_md_content(content):
    changes = 0

    # Code blocks in markdown
    def replace_compact(m):
        nonlocal changes
        changes += 1
        return named_block(m.group(1), m.group(2), m.group(3))
    content = COMPACT_RE.sub(replace_compact, content)

    def replace_comment(m):
        nonlocal changes
        changes += 1
        i = m.group(1)
        return (f"{i}outer_term    = (V2 / R2)\n"
                f"{i}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
                f"{i}omega_kms_kpc = outer_term - inner_term\n"
                f"{i}omega_rad_gyr = omega_kms_kpc * 1.0227")
    content = COMMENT_RE.sub(replace_comment, content)

    # Fix LaTeX Formula A grouping
    def replace_latex(m):
        nonlocal changes
        changes += 1
        return r'\frac{V_2}{R_2} - \frac{V_1}{R_1}\left(\frac{R_1}{R_2}\right)^'
    content = LATEX_RE.sub(replace_latex, content)

    return content, changes


def fix_notebook(filepath):
    """Fix .ipynb — parse JSON, fix cell sources, write back."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON error: {e}")
        return 0

    total = 0
    for cell in nb['cells']:
        src = cell.get('source', '')
        is_list = isinstance(src, list)
        src_str = ''.join(src) if is_list else src

        if not (re.search(r'V2/R2.*V1/R1', src_str) or
                re.search(r'V1/R1.*V2/R2', src_str)):
            continue

        if cell['cell_type'] == 'code':
            fixed, n = fix_py_content(src_str, filepath)
        else:
            fixed, n = fix_md_content(src_str)

        if n:
            total += n
            # Preserve original format (string vs list)
            if is_list:
                cell['source'] = fixed.splitlines(keepends=True)
            else:
                cell['source'] = fixed

    if total:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write('\n')

    return total


def should_skip(path):
    name = os.path.basename(path)
    if name in SKIP_FILES:
        return True
    for part in path.split(os.sep):
        if part in SKIP_DIRS:
            return True
    return False


def walk_repo():
    results = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in ('.py', '.ipynb', '.md'):
                full = os.path.join(root, fname)
                if not should_skip(full):
                    results.append((ext, full))
    return results


def main():
    print("EPS Research — Bulk omega formula sweep")
    print("Sol 5.6: outer_term / inner_term / * 1.0227")
    print("=" * 60)

    files = walk_repo()
    print(f"Scanning {len(files)} files...\n")

    total_files = 0
    total_changes = 0

    for ext, filepath in sorted(files):
        rel = os.path.relpath(filepath, REPO)

        if ext == '.ipynb':
            n = fix_notebook(filepath)
        else:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            if ext == '.md':
                fixed, n = fix_md_content(content)
            else:
                fixed, n = fix_py_content(content, rel)
            if n:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed)

        if n:
            print(f"  {n:2d} fix(es)  {rel}")
            total_files += 1
            total_changes += n

    print(f"\nDone. {total_changes} replacement(s) in {total_files} file(s).")
    print("Run check_omega_formula.py to verify, then commit.")


if __name__ == '__main__':
    main()
