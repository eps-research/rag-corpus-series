#!/usr/bin/env python3
"""Fix remaining compact omega forms in string-source notebooks."""
import json, re, os

def fix_src(src_str, path):
    changes = 0

    # Pattern 1: inline `(V2/R2 - (V1/R1)*(R1/R2)**1.5) * 1.0227` used as assignment
    # e.g.  om = (V2/R2 - (V1/R1)*(R1/R2)**1.5) * 1.0227
    #        omega = (V2/R2 - (V1/R1)*(R1/R2)**1.5) * 1.0227
    def replace_assign_with_conversion(m):
        nonlocal changes
        changes += 1
        indent = m.group(1)
        lhs = m.group(2).strip().rstrip('=').strip()
        return (f"{indent}outer_term    = (V2 / R2)\n"
                f"{indent}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
                f"{indent}omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n"
                f"{indent}omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n"
                f"{indent}{lhs} = omega_rad_gyr")

    src_str = re.sub(
        r'^([ \t]*)(om\w*\s*=)\s*\(V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5\)\s*\*\s*1\.022\d*',
        replace_assign_with_conversion, src_str, flags=re.MULTILINE)

    # Pattern 2: append form  dwarf_omegas.append(V2/R2 - (V1/R1)*(R1/R2)**1.5)
    def replace_append(m):
        nonlocal changes
        changes += 1
        indent = m.group(1)
        listname = m.group(2)
        return (f"{indent}outer_term    = (V2 / R2)\n"
                f"{indent}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
                f"{indent}omega_kms_kpc = outer_term - inner_term\n"
                f"{indent}omega_rad_gyr = omega_kms_kpc * 1.0227\n"
                f"{indent}{listname}.append(omega_rad_gyr)")

    src_str = re.sub(
        r'^([ \t]*)(\w+)\.append\(V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5\)',
        replace_append, src_str, flags=re.MULTILINE)

    # Pattern 3: return form
    def replace_return(m):
        nonlocal changes
        changes += 1
        indent = m.group(1)
        suffix = m.group(2).strip()
        conv = ' * 1.0227' if '* 1.022' in suffix else ''
        return (f"{indent}outer_term    = (V2 / R2)\n"
                f"{indent}inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n"
                f"{indent}omega_kms_kpc = outer_term - inner_term\n"
                f"{indent}omega_rad_gyr = omega_kms_kpc * 1.0227\n"
                f"{indent}return omega_rad_gyr")

    src_str = re.sub(
        r'^([ \t]*)return\s*\(?V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5\)?\s*(\*\s*1\.022\d*)?',
        replace_return, src_str, flags=re.MULTILINE)

    # Pattern 4: wrong reverse conversion V_adj = Vobs - R * omega / 1.0227
    # This means omega was already in rad/Gyr — the / 1.0227 is wrong
    def replace_wrong_div(m):
        nonlocal changes
        changes += 1
        indent = m.group(1)
        lhs = m.group(2)
        obs = m.group(3)
        r = m.group(4)
        om = m.group(5)
        return f"{indent}{lhs} = {obs} - {r} * {om}  # omega already in rad/Gyr — no unit division needed"

    src_str = re.sub(
        r'^([ \t]*)(\w+)\s*=\s*(\w+)\s*-\s*(\w+)\s*\*\s*(\w+)\s*/\s*1\.022\d*',
        replace_wrong_div, src_str, flags=re.MULTILINE)

    # Pattern 5: hs_b_02 print statements that show intermediate calc (pedagogical)
    # print(f"  ω = {V2/R2 - (V1/R1)*(R1/R2)**1.5:.3f}")
    # These are show-your-work lines — replace inline expr with omega_kms_kpc variable
    src_str = re.sub(
        r'\{V2/R2\s*-\s*\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5(:[^}]*)?\}',
        r'{omega_kms_kpc\1}',
        src_str
    )
    # Also fix the intermediate show lines
    src_str = re.sub(
        r'\{\(V1/R1\)\s*\*\s*\(R1/R2\)\*\*1\.5(:[^}]*)?\}',
        r'{inner_term\1}',
        src_str
    )

    # Pattern 6: capstone om_ex = (V2e/R2e-(V1e/R1e)*(R1e/R2e)**1.5)*1.0227
    def replace_ex(m):
        nonlocal changes
        changes += 1
        indent = m.group(1)
        lhs = m.group(2)
        s1,s2,s3,s4 = m.group(3),m.group(4),m.group(5),m.group(6)
        return (f"{indent}outer_term    = ({s2} / {s1})\n"
                f"{indent}inner_term    = ({s4} / {s3}) * (({s3} / {s1}) ** 1.5)\n"
                f"{indent}omega_kms_kpc = outer_term - inner_term\n"
                f"{indent}omega_rad_gyr = omega_kms_kpc * 1.0227\n"
                f"{indent}{lhs} = omega_rad_gyr")

    src_str = re.sub(
        r'^([ \t]*)(\w+)\s*=\s*\((\w+)/(\w+)-\((\w+)/(\w+)\)\*\(\5/\3\)\*\*1\.5\)\*1\.022\d*',
        replace_ex, src_str, flags=re.MULTILINE)

    if changes:
        print(f"  {changes} fix(es) in {os.path.basename(path)}")
    return src_str, changes


files = [
    'examples/dwarfs/dw09_dwarf_vs_sparc_comparison.ipynb',
    'examples/hi/ex09_multi_galaxy_comparison.ipynb',
    'examples/hi/ex22_distance_uncertainty.ipynb',
    'examples/highschool/hs_b_02_computing_omega.ipynb',
    'examples/highschool/hs_b_03_rmse_metric.ipynb',
    'examples/highschool/hs_b_06_omega_statistics.ipynb',
    'examples/highschool/hs_b_09_research_project.ipynb',
    'examples/highschool/hs_b_10_capstone.ipynb',
]

for path in files:
    nb = json.load(open(path))
    total = 0
    for cell in nb['cells']:
        src = cell.get('source', '')
        is_list = isinstance(src, list)
        src_str = ''.join(src) if is_list else src
        if not re.search(r'V2/R2|V1/R1|/ 1\.022', src_str):
            continue
        fixed, n = fix_src(src_str, path)
        if n:
            total += n
            cell['source'] = fixed.splitlines(keepends=True) if is_list else fixed
    if total:
        json.dump(nb, open(path,'w'), indent=1, ensure_ascii=False)
        open(path,'a').write('\n')

print("Done")
