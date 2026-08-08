#!/usr/bin/env python3
"""
Fix dimensional error: V_adj = Vobs - R * omega where omega was set to omega_rad_gyr.
V_adj requires omega in km/s/kpc. omega_rad_gyr is for reporting only.

Pattern fixed:
    omega = omega_rad_gyr        ← alias used in V_adj calc
    V_adj = Vobs - R * omega     ← WRONG: rad/Gyr * kpc ≠ km/s

Becomes:
    V_adj = Vobs - R * omega_kms_kpc   ← CORRECT
    omega = omega_rad_gyr               ← kept for reporting
"""
import re, json, os

REPO = os.environ.get('REPO', '.')

# In .py files: find `omega = omega_rad_gyr` followed soon by `V_adj = ... R * omega`
# Strategy: replace the alias line and fix the V_adj line

PY_ALIAS_RE = re.compile(
    r'^([ \t]*)omega\s*=\s*omega_rad_gyr\b(.*)\n',
    re.MULTILINE
)

VADJ_OMEGA_RE = re.compile(
    r'\bR\s*\*\s*omega\b(?!_)'  # R * omega but not R * omega_kms_kpc or omega_rad_gyr
)

def fix_py(content, path):
    changes = 0
    lines = content.splitlines(keepends=True)
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Fix V_adj lines that use bare `omega` after R *
        if VADJ_OMEGA_RE.search(line) and ('V_adj' in line or 'Vadj' in line or 'V_omega' in line):
            fixed = VADJ_OMEGA_RE.sub('R * omega_kms_kpc', line)
            if fixed != line:
                new_lines.append(fixed)
                changes += 1
                print(f'  fixed V_adj line: {line.strip()[:80]}')
                i += 1
                continue
        # Fix `omega = omega_rad_gyr` alias — add comment clarifying it's for reporting
        m = PY_ALIAS_RE.match(line)
        if m:
            indent = m.group(1)
            suffix = m.group(2).strip()
            new_line = f"{indent}omega = omega_rad_gyr  # reporting/storage only — use omega_kms_kpc for velocity arithmetic\n"
            new_lines.append(new_line)
            if new_line != line:
                changes += 1
            i += 1
            continue
        new_lines.append(line)
        i += 1
    return ''.join(new_lines), changes


def fix_notebook_src(src_str, path):
    changes = 0
    lines = src_str.splitlines(keepends=True)
    new_lines = []
    for line in lines:
        if VADJ_OMEGA_RE.search(line) and ('V_adj' in line or 'Vadj' in line or 'V_omega' in line):
            fixed = VADJ_OMEGA_RE.sub('R * omega_kms_kpc', line)
            if fixed != line:
                new_lines.append(fixed)
                changes += 1
                print(f'  fixed V_adj: {line.strip()[:80]}')
                continue
        # Fix alias comment
        if re.search(r'omega\s*=\s*omega_rad_gyr', line):
            fixed = re.sub(
                r'(omega\s*=\s*omega_rad_gyr)(.*)',
                r'\1  # reporting/storage only — use omega_kms_kpc for velocity arithmetic',
                line)
            new_lines.append(fixed)
            if fixed != line: changes += 1
            continue
        new_lines.append(line)
    return ''.join(new_lines), changes


def fix_notebook(path):
    nb = json.load(open(path))
    total = 0
    for cell in nb['cells']:
        src = cell.get('source', '')
        is_list = isinstance(src, list)
        src_str = ''.join(src) if is_list else src
        if 'R * omega' not in src_str and 'R*omega' not in src_str:
            continue
        fixed, n = fix_notebook_src(src_str, path)
        if n:
            total += n
            cell['source'] = fixed.splitlines(keepends=True) if is_list else fixed
    if total:
        json.dump(nb, open(path, 'w'), indent=1, ensure_ascii=False)
        open(path, 'a').write('\n')
    return total


SKIP = {'check_omega_formula.py', 'fix_units_sweep.py', 'audit_omega_remediation_v2.py'}

print("Units sweep: V_adj must use omega_kms_kpc not omega_rad_gyr")
print("=" * 60)

total_files = 0
total_changes = 0

for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.ipynb_checkpoints'}]
    for fname in files:
        if fname in SKIP: continue
        path = os.path.join(root, fname)
        rel = os.path.relpath(path, REPO)
        ext = os.path.splitext(fname)[1].lower()
        if ext == '.py':
            content = open(path).read()
            if 'R * omega' not in content and 'R*omega' not in content: continue
            fixed, n = fix_py(content, rel)
            if n:
                open(path, 'w').write(fixed)
                print(f'  {n} fix(es): {rel}')
                total_files += 1
                total_changes += n
        elif ext == '.ipynb':
            try: n = fix_notebook(path)
            except: continue
            if n:
                print(f'  {n} fix(es): {rel}')
                total_files += 1
                total_changes += n

print(f"\nDone. {total_changes} fix(es) in {total_files} file(s).")
print("Verify: grep -rn 'R \\* omega[^_]' examples/ | grep -v '__pycache__'")
