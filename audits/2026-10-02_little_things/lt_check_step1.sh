#!/usr/bin/env bash
set -euo pipefail
cd ~/lt_check

# --- Download the exact Zenodo files the curation tool pulls ---
[ -f v71.json ]   || curl -sSL -o v71.json   "https://zenodo.org/records/21768240/files/rotation_curve_corpus_v7.json?download=1"
[ -f dwarf.json ] || curl -sSL -o dwarf.json "https://zenodo.org/records/20320362/files/dwarf_irregular_corpus_v1.json?download=1"
sha256sum v71.json dwarf.json
python3 -c "import astroquery" 2>/dev/null || python3 -m pip install --quiet --user astroquery

python3 - <<'PY'
import json, collections
# ---------- STEP 1: does Zenodo v7.1 contain an appended second curve? ----------
G = json.load(open('v71.json'))['galaxies']
lt = [g for g in G if 'LITTLE' in str(g.get('survey','')).upper()]
def split(d):
    for i in range(1, len(d)):
        if d[i]['Rad'] < d[i-1]['Rad']:
            return d[:i], d[i:]
    return d, []
ndp = lambda v: len(repr(float(v)).split('.')[-1].rstrip('0'))
tot_rows = sum(len(g['data']) for g in lt); app = 0; hit = []
for g in lt:
    vk = 'Vobs' if 'Vobs' in g['data'][0] else 'Vrot'
    a, b = split(g['data'])
    if b:
        app += len(b)
        hit.append((g['galaxy'], len(a), len(b),
                    max(ndp(p[vk]) for p in a), min(ndp(p[vk]) for p in b)))
print("\n=== STEP 1: Zenodo v7.1 LITTLE THINGS ===")
print(f"LT galaxies: {len(lt)}   LT rows: {tot_rows}   galaxies with appended block: {len(hit)}   appended rows: {app}")
print("galaxy, n_first_block, n_second_block, max_decimals_first, min_decimals_second")
for h in hit: print("  ", h)
print("no appended block:", [g['galaxy'] for g in lt if not split(g['data'])[1]])

# Dwarf corpus = v7 rows? (multiset check)
D = {g['galaxy']: g for g in json.load(open('dwarf.json'))['galaxies'] if g.get('omega_ready')}
V = {g['galaxy']: g for g in lt}
eq = sum(collections.Counter((p['Rad'], p.get('Vrot', p.get('Vobs'))) for p in D[n]['data']) ==
         collections.Counter((p['Rad'], p.get('Vobs', p.get('Vrot'))) for p in V[n]['data']) for n in D)
print(f"dwarf omega-ready galaxies whose rows equal the v7.1 rows exactly: {eq}/{len(D)}")

# ---------- STEP 2: what is the second curve? Compare against Oh et al. 2015 ----------
from astroquery.vizier import Vizier
Vizier.ROW_LIMIT = -1
cats = Vizier.get_catalogs('J/AJ/149/180')
print("\n=== STEP 2: VizieR J/AJ/149/180 ===")
for key in cats.keys():
    t = cats[key]
    print(f"\n--- table {key}: {len(t)} rows ---")
    print("columns:", t.colnames)
    namecol = next((c for c in t.colnames if c.lower() in ('name','galaxy','id')), t.colnames[0])
    sel = [r for r in t if str(r[namecol]).replace(' ','').upper() in ('DDO154','DDO_154')]
    print(f"DDO 154 rows: {len(sel)}")
    for r in sel[:6]:  print("   ", list(r))
    if len(sel) > 6:
        print("    ...")
        for r in sel[-4:]: print("   ", list(r))
    for c in t.colnames:
        vals = set(str(x) for x in t[c])
        if 1 < len(vals) <= 6: print(f"  low-cardinality column '{c}': {sorted(vals)}")

g = V['DDO_154']; a, b = split(g['data']); R03, V03 = g['R0.3_kpc'], g['V0.3_kms']
print(f"\nv7.1 DDO_154 scaled for comparison (R0.3={R03}, V0.3={V03}):")
print("  first block  (R/R0.3, V/V0.3):", [(round(p['Rad']/R03,4), round(p['Vobs']/V03,4)) for p in a[:4]])
print("  second block (R/R0.3, V/V0.3):", [(round(p['Rad']/R03,4), round(p['Vobs']/V03,4)) for p in b[:4]])
PY
