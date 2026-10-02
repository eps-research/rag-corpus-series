#!/usr/bin/env bash
set -euo pipefail
cd ~/lt_check
python3 - <<'PY'
import json, numpy as np
from astroquery.vizier import Vizier
Vizier.ROW_LIMIT = -1
T = Vizier.get_catalogs('J/AJ/149/180/rotdmbar')[0]

def viz_rows(name, typ):
    s = T[(T['Name'] == name) & (T['Type'] == typ)]
    R = np.array(s['R'] * s['R0.3'], float); V = np.array(s['V'] * s['V0.3'], float)
    E = np.array(s['e_V'] * s['V0.3'], float); o = np.argsort(R)
    return R[o], V[o], E[o]

v7 = {g['galaxy']: g for g in json.load(open('v71.json'))['galaxies']
      if 'LITTLE' in str(g.get('survey', '')).upper()}
dw = [g for g in json.load(open('dwarf.json'))['galaxies'] if g.get('omega_ready')]

def first_block(d):
    for i in range(1, len(d)):
        if d[i]['Rad'] < d[i-1]['Rad']: return d[:i]
    return d

# ---- Check A: VizieR 'Data' rows == v7.1 first block (all LT galaxies) ----
print("=== A: VizieR Data rows vs v7.1 first block ===")
bad = 0
for n, g in v7.items():
    R, V, _ = viz_rows(n, 'Data')
    fb = first_block(g['data'])
    r7 = np.array([p['Rad'] for p in fb]); v7v = np.array([p['Vobs'] for p in fb])
    ok = len(R) == len(r7) and np.allclose(R, r7, atol=0.006) and np.allclose(V, v7v, atol=0.006)
    if not ok:
        bad += 1; print(f"  MISMATCH {n}: viz n={len(R)} v7 n={len(r7)}")
print(f"  galaxies matching: {len(v7)-bad}/{len(v7)}")

# ---- Check B: independent omega from VizieR Data rows only ----
print("\n=== B: omega from VizieR 'Data' rows (Eq. 6, named-term form) ===")
print(f"{'galaxy':10s} {'n':>4} {'R1':>6} {'V1':>7} {'R2':>6} {'V2':>7} {'w_kms_kpc':>10} {'w_rad_gyr':>10} {'dup_R':>5}")
out = []
for g in sorted(dw, key=lambda g: g['galaxy']):
    R, V, E = viz_rows(g['galaxy'], 'Data')
    dupR = len(R) - len(np.unique(np.round(R, 2)))
    R1, V1, R2, V2 = R[0], V[0], R[-1], V[-1]
    outer_term = (V2 / R2)
    inner_term = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]
    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr
    out.append(omega_kms_kpc)
    print(f"{g['galaxy']:10s} {len(R):4d} {R1:6.3f} {V1:7.3f} {R2:6.3f} {V2:7.3f} {omega_kms_kpc:10.4f} {omega_rad_gyr:10.4f} {dupR:5d}")
out = np.array(out)
print(f"\nN={len(out)}  all positive={bool((out>0).all())}  (per-galaxy values only; no population statistic)")
PY
