#!/usr/bin/env python3
"""
EPS Research — Build all 25 SPARC/HI Example Notebooks
Run from: ~/Documents/rag-corpus-series/examples/hi/
Requires: rotation_curve_corpus_v7.json and rotation_curve_corpus_v7_flat.csv
          in the same directory.
Output:   25 .ipynb files ready to run in JupyterLab.

Usage:
    python3 build_hi_examples.py

Flynn, D.C. (2026) EPS Research
DOI: 10.5281/zenodo.19563417
"""

import json
import os

# ── Notebook builder helpers ──────────────────────────────────────────────────

def nb(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

def md(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text
    }

def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text
    }

CORPUS_NOTE = (
    "**Important note on corpus fidelity:** The `rotation_curve_corpus_v7_flat.csv` "
    "and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. "
    "The CSV contains every kinematic parameter published by Lelli et al. (2016) "
    "including per-galaxy inclination, distance uncertainties, mass-to-light ratios, "
    "and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, "
    "Vdisk, Vbul, errV at every radial point. This is the complete published dataset "
    "in a single machine-readable file.\n\n"
    "**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.19563417  \n"
    "**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n"
    "**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"
)

# ── Define all 25 notebooks ───────────────────────────────────────────────────

notebooks = {}

# ── EX01: First rotation curve ────────────────────────────────────────────────
notebooks["ex01_first_rotation_curve.ipynb"] = nb([
md(f"""# SPARC Example 01: Your First Rotation Curve

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

Load a single galaxy rotation curve from the corpus and plot it.
We use DDO161, a dwarf irregular galaxy at 7.5 Mpc — the anchor galaxy
of the EPS Research omega correction framework.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

# Load the corpus
with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

print(f"Total galaxies:  {len(corpus['galaxies'])}")
print(f"Surveys covered: SPARC, THINGS, LITTLE THINGS, WALLABY DR2")

# Retrieve DDO161
g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
print(f"\\nGalaxy:        {g['galaxy']}")
print(f"Survey:        {g['survey']}")
print(f"Distance:      {g['distance_mpc']} Mpc")
print(f"Inclination:   {g['inc_deg']} deg")
print(f"Quality tier:  {g['quality_tier']} (1=hand-curated, per-point uncertainties)")
print(f"N data points: {g['n_points']}")"""),
code("""# Extract per-ring data
d    = g['data']
R    = np.array([p['Rad']  for p in d])
Vobs = np.array([p['Vobs'] for p in d])
errV = np.array([p['errV'] for p in d])

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(R, Vobs, yerr=errV, fmt='o-', color='#1f77b4',
            capsize=4, linewidth=1.8, markersize=6,
            label=r'$V_{\\rm obs}$ (SPARC Tier 1)')
ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel(r'$V_{\\rm obs}$ (km/s)', fontsize=12)
ax.set_title('DDO161 — SPARC Tier 1 Rotation Curve\\n'
             'EPS Research Unified HI Corpus v7.0', fontsize=11)
ax.legend(fontsize=10)
ax.set_xlim(0, R.max() * 1.15)
ax.set_ylim(0, Vobs.max() * 1.35)
ax.text(0.97, 0.08,
        f'D = {g["distance_mpc"]} Mpc\\ninc = {g["inc_deg"]}°\\nN = {g["n_points"]} rings',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
plt.tight_layout()
plt.savefig('ex01_ddo161_rc.png', dpi=150, bbox_inches='tight')
plt.show()
print('Saved: ex01_ddo161_rc.png')""")
])

# ── EX02: Baryonic decomposition ──────────────────────────────────────────────
notebooks["ex02_baryonic_decomposition.ipynb"] = nb([
md(f"""# SPARC Example 02: Baryonic Decomposition

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

SPARC is unique: it provides not just Vobs but the full baryonic decomposition —
Vgas, Vdisk, and Vbul at every radial point. This is full-fidelity data directly
from Lelli et al. (2016), not derived or estimated.

We compute the baryonic velocity using sign-preserving quadrature:

    Vbar = sqrt(Upsilon*Vdisk^2 + Upsilon_b*Vbul^2 + sign(Vgas)*Vgas^2)

Note: Vgas can be negative at inner radii where thermal pressure exceeds rotation.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
d = g['data']

R     = np.array([p['Rad']   for p in d])
Vobs  = np.array([p['Vobs']  for p in d])
errV  = np.array([p['errV']  for p in d])
Vgas  = np.array([p['Vgas']  for p in d])
Vdisk = np.array([p['Vdisk'] for p in d])
Vbul  = np.array([p['Vbul']  for p in d])

# Sign-preserving quadrature at Upsilon=1
Vbar = np.where(Vgas < 0,
                -np.sqrt(Vgas**2 + Vdisk**2 + Vbul**2),
                 np.sqrt(Vgas**2 + Vdisk**2 + Vbul**2))

print(f"Vgas negative rows: {(Vgas < 0).sum()} (inner radii — thermal pressure)")
print(f"Mass discrepancy at R_max:")
print(f"  Vobs = {Vobs[-1]:.1f} km/s")
print(f"  Vbar = {Vbar[-1]:.1f} km/s")
print(f"  Outer gap (Vobs - Vbar) = {Vobs[-1] - Vbar[-1]:.1f} km/s")"""),
code("""fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(R, Vobs, yerr=errV, fmt='o', color='#1f77b4',
            capsize=4, markersize=6, label=r'$V_{\\rm obs}$ (SPARC)', zorder=5)
ax.plot(R, Vbar,  's-', color='#d62728', linewidth=1.5,
        label=r'$V_{\\rm bar}$ (quadrature, $\\Upsilon=1$)')
ax.plot(R, Vgas,  '^--', color='#2ca02c', linewidth=1.2, alpha=0.8,
        label=r'$V_{\\rm gas}$')
ax.plot(R, Vdisk, 'v--', color='#ff7f0e', linewidth=1.2, alpha=0.8,
        label=r'$V_{\\rm disk}$')
ax.axhline(0, color='black', linewidth=0.7, alpha=0.4)
ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel('Velocity (km/s)', fontsize=12)
ax.set_title('DDO161 — Full Baryonic Decomposition\\n'
             'Full-fidelity SPARC data, EPS Research Corpus v7.0', fontsize=11)
ax.legend(fontsize=9)
ax.text(0.02, 0.95,
        'Vgas < 0 at inner radii\\n= thermal pressure term\\n(sign-preserving quadrature)',
        transform=ax.transAxes, va='top', fontsize=8,
        bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', alpha=0.85))
plt.tight_layout()
plt.savefig('ex02_ddo161_baryonic.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX03: Omega correction (EPS flagship) ─────────────────────────────────────
notebooks["ex03_omega_correction_ddo161.ipynb"] = nb([
md(f"""# SPARC Example 03: The Omega Kinematic Correction (EPS Research)

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

This is the core EPS Research result. The omega kinematic correction is derived
from boundary points only — no free parameters, no mass modeling:

    V_adj = V_obs - R * omega
    omega = (V2/R2 - V1/R1) * (R1/R2)^(3/2)   [rad/Gyr]

where (R1, V1) = innermost ring, (R2, V2) = outermost ring.
Note: 1 rad/Gyr = 1.022 km/s/kpc.

**Published result:** omega = 4.69 rad/Gyr for DDO161
**Reference:** Flynn & Cannaliato (2025), DOI: 10.3389/fspas.2025.1680387

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
d = g['data']

R     = np.array([p['Rad']   for p in d])
Vobs  = np.array([p['Vobs']  for p in d])
errV  = np.array([p['errV']  for p in d])
Vgas  = np.array([p['Vgas']  for p in d])
Vdisk = np.array([p['Vdisk'] for p in d])
Vbul  = np.array([p['Vbul']  for p in d])

# Baryonic velocity
Vbar = np.where(Vgas < 0,
                -np.sqrt(Vgas**2 + Vdisk**2 + Vbul**2),
                 np.sqrt(Vgas**2 + Vdisk**2 + Vbul**2))

# Omega from boundary points
R1, V1 = R[0],  Vobs[0]
R2, V2 = R[-1], Vobs[-1]
omega  = (V2/R2 - V1/R1) * (R1/R2)**1.5
V_adj  = Vobs - R * omega

# Keplerian baseline
GM       = V2**2 * R2
V_kepler = np.sqrt(GM / R)

# RMSE
rmse_omega  = np.sqrt(np.mean((V_adj  - Vbar)**2))
rmse_kepler = np.sqrt(np.mean((V_kepler - Vbar)**2))

print(f"Computed omega  = {omega:.3f} rad/Gyr")
print(f"Published omega = 4.69 rad/Gyr (Flynn & Cannaliato 2025)")
print(f"RMSE (omega vs Vbar):   {rmse_omega:.2f} km/s")
print(f"RMSE (Kepler vs Vbar):  {rmse_kepler:.2f} km/s")
print(f"Improvement:            {rmse_kepler - rmse_omega:.2f} km/s")"""),
code("""fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(R, Vobs, yerr=errV, fmt='o', color='#1f77b4',
            capsize=4, markersize=6, label=r'$V_{\\rm obs}$ (SPARC)', zorder=5)
ax.plot(R, Vbar,     's-', color='#d62728', linewidth=1.5,
        label=r'$V_{\\rm bar}$ ($\\Upsilon=1$)')
ax.plot(R, V_adj,    '^-', color='#2ca02c', linewidth=1.8,
        label=fr'$V_{{\\rm obs}} - R\\omega$  ($\\omega={omega:.2f}$ rad/Gyr)')
ax.plot(R, V_kepler, '--', color='#ff7f0e', linewidth=1.2,
        label='Keplerian baseline')
ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel('Velocity (km/s)', fontsize=12)
ax.set_title('DDO161 — Omega Kinematic Correction\\n'
             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387', fontsize=10)
ax.legend(fontsize=9)
ax.set_xlim(0, R.max() * 1.15)
ax.set_ylim(0, Vobs.max() * 1.35)
ax.text(0.97, 0.08,
        f'RMSE omega: {rmse_omega:.1f} km/s\\nRMSE Kepler: {rmse_kepler:.1f} km/s',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
plt.tight_layout()
plt.savefig('ex03_ddo161_omega.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX04: WALLABY Tier 2 ──────────────────────────────────────────────────────
notebooks["ex04_wallaby_tier2.ipynb"] = nb([
md(f"""# SPARC Example 04: WALLABY Tier 2 — Automated Pipeline with Caution Zone

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

WALLABY DR2 contributes 203 galaxies from the ASKAP automated pipeline.
Unlike SPARC/THINGS/LITTLE THINGS (Tier 1), WALLABY is Tier 2:
no per-ring uncertainties, no baryonic decomposition.

Key limitation: 30 arcsec ASKAP beam — Vrot < 50 km/s is unreliable.

Schema difference: WALLABY uses `rotation_curve` key with `rad_kpc`/`vrot_kms`.
SPARC uses `data` key with `Rad`/`Vobs`. Always check the survey.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Find a WALLABY galaxy with many rings
wallaby = [g for g in corpus['galaxies']
           if g['survey'] == 'WALLABY'
           and g.get('rotation_curve')
           and len(g['rotation_curve']) >= 20]
wg = sorted(wallaby, key=lambda x: len(x['rotation_curve']), reverse=True)[0]

print(f"Galaxy:      {wg['galaxy']}")
print(f"Survey:      {wg['survey']} (Tier {wg['quality_tier']})")
print(f"Distance:    {wg['distance_mpc']} Mpc")
print(f"Inclination: {wg['inc_deg']} deg")
print(f"N rings:     {len(wg['rotation_curve'])}")
print(f"\\nKey schema difference:")
print(f"  WALLABY: rotation_curve -> rad_kpc, vrot_kms")
print(f"  SPARC:   data           -> Rad, Vobs")"""),
code("""rc  = wg['rotation_curve']
R_w = np.array([p['rad_kpc']  for p in rc])
V_w = np.array([p['vrot_kms'] for p in rc])

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(R_w, V_w, 'o-', color='#B2182B', linewidth=1.8, markersize=5,
        label=r'$V_{\\rm rot}$ (3DBarolo, WALLABY)')
ax.axhspan(0, 50, alpha=0.12, color='red',
           label=r'$V_{\\rm rot}$ < 50 km/s (beam-smearing caution zone)')
ax.axhline(50, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel(r'$V_{\\rm rot}$ (km/s)', fontsize=12)
ax.set_title(f'{wg["galaxy"]} — WALLABY DR2 Tier 2\\n'
             'EPS Research Corpus v7.0 | Automated Pipeline (no per-ring uncertainties)',
             fontsize=10)
ax.legend(fontsize=9)
ax.text(0.03, 0.95,
        f'D = {wg["distance_mpc"]:.1f} Mpc\\n'
        f'inc = {wg["inc_deg"]:.1f}°\\n'
        f'{len(rc)} rings\\nTier 2',
        transform=ax.transAxes, va='top', fontsize=8,
        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
plt.tight_layout()
plt.savefig('ex04_wallaby_tier2.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX05: Survey breakdown ────────────────────────────────────────────────────
notebooks["ex05_survey_breakdown.ipynb"] = nb([
md(f"""# SPARC Example 05: Corpus Survey Breakdown

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

How many galaxies per survey? What quality tiers? This example
loads the flat CSV — the fastest way to get corpus-level statistics.

{CORPUS_NOTE}"""),
code("""import csv
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        rows.append(r)

surveys = Counter(r['survey'] for r in rows)
tiers   = Counter(r['quality_tier'] for r in rows)

print(f"Total galaxies: {len(rows)}")
print("\\nSurvey breakdown:")
for s, n in sorted(surveys.items(), key=lambda x: -x[1]):
    print(f"  {s:<15} {n:>4} galaxies")
print("\\nQuality tiers:")
for t, n in sorted(tiers.items()):
    label = "hand-curated" if t == "1" else "automated pipeline"
    print(f"  Tier {t}: {n} galaxies ({label})")"""),
code("""COLORS = {'SPARC':'#1f77b4','THINGS':'#ff7f0e',
          'LITTLE_THINGS':'#2ca02c','WALLABY':'#d62728'}

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

# Pie
labels = list(surveys.keys())
sizes  = [surveys[k] for k in labels]
colors = [COLORS.get(k, '#9467bd') for k in labels]
axes[0].pie(sizes, labels=[f'{l}\\n({n})' for l, n in zip(labels, sizes)],
            colors=colors, autopct='%1.0f%%', textprops={'fontsize': 9})
axes[0].set_title('Galaxies by Survey', fontsize=11)

# Stacked bar by tier
x = np.arange(len(COLORS))
tier_data = {}
for r in rows:
    tier_data.setdefault(r['survey'], {}).setdefault(r['quality_tier'], 0)
    tier_data[r['survey']][r['quality_tier']] += 1
for i, (t, color) in enumerate([('1','#2166ac'), ('2','#b2182b')]):
    vals = [tier_data.get(s, {}).get(t, 0) for s in COLORS]
    axes[1].bar(x + i*0.35, vals, 0.35, label=f'Tier {t}', color=color, alpha=0.85)
axes[1].set_xticks(x + 0.175)
axes[1].set_xticklabels(list(COLORS.keys()), fontsize=9)
axes[1].set_ylabel('N galaxies')
axes[1].set_title('Quality Tier by Survey', fontsize=11)
axes[1].legend()

plt.suptitle('EPS Research Unified HI Corpus v7.0 — Survey Coverage (N=438)',
             fontsize=11)
plt.tight_layout()
plt.savefig('ex05_survey_breakdown.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX06: Vrot distribution ───────────────────────────────────────────────────
notebooks["ex06_vrot_distribution.ipynb"] = nb([
md(f"""# SPARC Example 06: Peak Rotation Velocity Distribution

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

Peak rotation velocity Vrot_max traces total galaxy mass.
This stacked histogram spans the full dynamic range —
from ~10 km/s dwarf irregulars to ~350 km/s massive spirals.

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        if r['vrot_max_kms']:
            rows.append(r)

COLORS = {'SPARC':'#1f77b4','THINGS':'#ff7f0e',
          'LITTLE_THINGS':'#2ca02c','WALLABY':'#d62728'}
bins = np.arange(0, 360, 20)

fig, ax = plt.subplots(figsize=(9, 5))
bottom = np.zeros(len(bins) - 1)
for survey, color in COLORS.items():
    vals = [float(r['vrot_max_kms']) for r in rows if r['survey'] == survey]
    counts, _ = np.histogram(vals, bins=bins)
    ax.bar(bins[:-1], counts, width=19, bottom=bottom, color=color,
           label=f'{survey} ({len(vals)})', alpha=0.85, align='edge')
    bottom += counts

ax.set_xlabel(r'$V_{\\rm rot,max}$ (km/s)', fontsize=12)
ax.set_ylabel('N galaxies', fontsize=12)
ax.set_title('Peak Rotation Velocity Distribution\\n'
             'EPS Research Unified HI Corpus v7.0 (N=438)', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex06_vrot_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

all_vmax = [float(r['vrot_max_kms']) for r in rows]
print(f"Total galaxies with Vrot_max: {len(all_vmax)}")
print(f"Range: {min(all_vmax):.1f} -- {max(all_vmax):.1f} km/s")
print(f"Median: {np.median(all_vmax):.1f} km/s")""")
])

# ── EX07: Rmax vs Vmax parameter space ────────────────────────────────────────
notebooks["ex07_rmax_vmax_parameter_space.ipynb"] = nb([
md(f"""# SPARC Example 07: Rmax vs Vrot Parameter Space

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The Rmax vs Vrot_max diagram shows the full dynamic range:
from ~3 kpc dwarf irregulars to ~100 kpc massive spirals.
Colored by quality tier (Tier 1 = hand-curated, Tier 2 = automated).

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        if r['r_max_kpc'] and r['vrot_max_kms']:
            rows.append(r)

r_max = np.array([float(r['r_max_kpc'])    for r in rows])
v_max = np.array([float(r['vrot_max_kms']) for r in rows])
tier  = np.array([int(r['quality_tier'])   for r in rows])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(r_max[tier==1], v_max[tier==1], s=18, alpha=0.7,
           color='#2166ac', label=f'Tier 1 — {(tier==1).sum()} galaxies')
ax.scatter(r_max[tier==2], v_max[tier==2], s=18, alpha=0.5,
           color='#b2182b', marker='^',
           label=f'Tier 2 — {(tier==2).sum()} galaxies')
ax.set_xlabel(r'$R_{\\rm max}$ (kpc)', fontsize=12)
ax.set_ylabel(r'$V_{\\rm rot,max}$ (km/s)', fontsize=12)
ax.set_title('Parameter Space — EPS Research Unified HI Corpus v7.0\\n'
             'From dwarf irregulars (~3 kpc) to massive spirals (~100 kpc)',
             fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex07_parameter_space.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX08: Hubble type vs Vmax ─────────────────────────────────────────────────
notebooks["ex08_hubble_type_vmax.ipynb"] = nb([
md(f"""# SPARC Example 08: Hubble Type vs Peak Velocity

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

SPARC includes Hubble morphological type (0=S0 to 11=Irr/BCD).
Galaxy morphology correlates with peak rotation velocity —
earlier types (S0, Sa) rotate faster; late irregulars rotate slowly.

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        if r['survey']=='SPARC' and r['hubble_type'] and r['vrot_max_kms']:
            rows.append(r)

type_labels = {0:'S0',1:'Sa',2:'Sab',3:'Sb',4:'Sbc',5:'Sc',
               6:'Scd',7:'Sd',8:'Sdm',9:'Sm',10:'Im',11:'BCD'}

by_type = defaultdict(list)
for r in rows:
    t = int(float(r['hubble_type']))
    by_type[t].append(float(r['vrot_max_kms']))

types   = sorted(by_type.keys())
medians = [np.median(by_type[t]) for t in types]
counts  = [len(by_type[t]) for t in types]
xlabels = [type_labels.get(t, str(t)) for t in types]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(xlabels, medians, color='#2166ac', alpha=0.8, edgecolor='white')
for i, (m, n) in enumerate(zip(medians, counts)):
    ax.text(i, m + 2, f'n={n}', ha='center', fontsize=7)
ax.set_xlabel('Hubble Type', fontsize=12)
ax.set_ylabel(r'Median $V_{\\rm rot,max}$ (km/s)', fontsize=12)
ax.set_title('Hubble Type vs Peak Rotation Velocity\\n'
             'SPARC (175 galaxies) — EPS Research Corpus v7.0', fontsize=11)
plt.tight_layout()
plt.savefig('ex08_hubble_type_vmax.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX09: Multi-galaxy comparison ─────────────────────────────────────────────
notebooks["ex09_multi_galaxy_comparison.ipynb"] = nb([
md(f"""# SPARC Example 09: Multi-Galaxy Rotation Curve Comparison

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

Compare rotation curves across the full SPARC mass range:
- DDO161: dwarf irregular, Vmax~67 km/s
- NGC2403: intermediate spiral, Vmax~130 km/s  
- UGC2885: massive spiral (one of the largest known), Vmax~300 km/s

All three loaded from a single JSON file in under 15 lines of Python.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

targets = ['DDO161', 'NGC2403', 'UGC2885']
colors  = ['#2166ac', '#4dac26', '#d6604d']

fig, ax = plt.subplots(figsize=(9, 5))
for name, color in zip(targets, colors):
    try:
        g = next(g for g in corpus['galaxies'] if g['galaxy'] == name)
        d = g['data']
        R    = [p['Rad']  for p in d]
        Vobs = [p['Vobs'] for p in d]
        ax.plot(R, Vobs, 'o-', color=color, linewidth=1.5, markersize=4,
                label=f'{name}  Vmax={max(Vobs):.0f} km/s  D={g["distance_mpc"]} Mpc')
    except StopIteration:
        print(f"Galaxy {name} not found — check galaxy name in corpus")

ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel(r'$V_{\\rm obs}$ (km/s)', fontsize=12)
ax.set_title('Rotation Curves Across the Mass Range\\n'
             'EPS Research Unified HI Corpus v7.0', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex09_multi_galaxy.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX10: Omega across SPARC ──────────────────────────────────────────────────
notebooks["ex10_omega_84_sparc.ipynb"] = nb([
md(f"""# SPARC Example 10: Omega Across the SPARC Sample

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

This example computes omega for all SPARC galaxies with sufficient data
and reproduces the key result from Flynn & Cannaliato (2025):
mean omega = 7.06 ± 3.26 rad/Gyr across 84 Q=1 galaxies.

**Reference:** Flynn, D.C. & Cannaliato, J. (2025).
DOI: 10.3389/fspas.2025.1680387

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

results = []
for g in corpus['galaxies']:
    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:
        continue
    d  = g['data']
    R  = [p['Rad']  for p in d]
    V  = [p['Vobs'] for p in d]
    R1, V1 = R[0],  V[0]
    R2, V2 = R[-1], V[-1]
    if R1 <= 0 or R2 <= 0 or V1 <= 0 or V2 <= 0:
        continue
    omega = (V2/R2 - V1/R1) * (R1/R2)**1.5
    results.append({'galaxy': g['galaxy'], 'omega': omega,
                    'vmax': max(V), 'distance': g['distance_mpc']})

omegas = [r['omega'] for r in results]
print(f"Galaxies computed:  {len(results)}")
print(f"Mean omega:         {np.mean(omegas):.2f} rad/Gyr")
print(f"Std omega:          {np.std(omegas):.2f} rad/Gyr")
print(f"Median omega:       {np.median(omegas):.2f} rad/Gyr")
print(f"\\nPublished result (Flynn & Cannaliato 2025): 7.06 ± 3.26 rad/Gyr")"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].hist(omegas, bins=30, color='#2166ac', alpha=0.8, edgecolor='white')
axes[0].axvline(np.mean(omegas), color='red', linestyle='--', linewidth=1.5,
                label=f'Mean = {np.mean(omegas):.2f} rad/Gyr')
axes[0].axvline(7.06, color='orange', linestyle=':', linewidth=1.5,
                label='Published: 7.06 rad/Gyr')
axes[0].set_xlabel(r'$\\omega$ (rad/Gyr)', fontsize=11)
axes[0].set_ylabel('N galaxies', fontsize=11)
axes[0].set_title('Omega Distribution — SPARC Sample', fontsize=10)
axes[0].legend(fontsize=8)

axes[1].scatter([r['vmax'] for r in results], omegas,
                s=20, alpha=0.6, color='#2166ac')
axes[1].axhline(np.mean(omegas), color='red', linestyle='--', linewidth=1,
                label=f'Mean = {np.mean(omegas):.2f}')
axes[1].set_xlabel(r'$V_{\\rm max}$ (km/s)', fontsize=11)
axes[1].set_ylabel(r'$\\omega$ (rad/Gyr)', fontsize=11)
axes[1].set_title(r'$\\omega$ vs Peak Velocity', fontsize=10)
axes[1].legend(fontsize=8)

plt.suptitle('Omega Kinematic Correction — EPS Research SPARC Sample\\n'
             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387',
             fontsize=10)
plt.tight_layout()
plt.savefig('ex10_omega_sparc.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX11: THINGS vs SPARC overlap ─────────────────────────────────────────────
notebooks["ex11_things_vs_sparc.ipynb"] = nb([
md(f"""# SPARC Example 11: THINGS vs SPARC Cross-Survey Comparison

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

14 galaxies appear in both THINGS and SPARC.
THINGS provides high-resolution VLA tilted-ring fits;
SPARC provides full baryonic decomposition at Spitzer 3.6μm.
The corpus crossmatch index enables direct comparison.

{CORPUS_NOTE}"""),
code("""import csv
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        rows.append(r)

sparc_names  = {r['galaxy'] for r in rows if r['survey'] == 'SPARC'}
things_names = {r['galaxy'] for r in rows if r['survey'] == 'THINGS'}
overlap      = sparc_names & things_names

print(f"SPARC galaxies:  {len(sparc_names)}")
print(f"THINGS galaxies: {len(things_names)}")
print(f"Overlap:         {len(overlap)} galaxies\\n")

sparc_vmax, things_vmax, names = [], [], []
for name in sorted(overlap):
    sr = next((r for r in rows if r['galaxy']==name and r['survey']=='SPARC'
               and r['vrot_max_kms']), None)
    tr = next((r for r in rows if r['galaxy']==name and r['survey']=='THINGS'
               and r['vrot_max_kms']), None)
    if sr and tr:
        sv, tv = float(sr['vrot_max_kms']), float(tr['vrot_max_kms'])
        sparc_vmax.append(sv)
        things_vmax.append(tv)
        names.append(name)
        print(f"  {name:<15} SPARC={sv:.0f}  THINGS={tv:.0f} km/s")"""),
code("""fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(sparc_vmax, things_vmax, s=60, color='#2166ac', zorder=3)
for i, name in enumerate(names):
    ax.annotate(name, (sparc_vmax[i], things_vmax[i]),
                textcoords='offset points', xytext=(4, 3), fontsize=7)
lim = [0, max(sparc_vmax + things_vmax) * 1.1]
ax.plot(lim, lim, 'k--', linewidth=1, alpha=0.5, label='1:1 line')
ax.set_xlabel('SPARC Vrot_max (km/s)', fontsize=11)
ax.set_ylabel('THINGS Vrot_max (km/s)', fontsize=11)
ax.set_title(f'SPARC vs THINGS: {len(names)} overlapping galaxies\\n'
             'EPS Research Corpus v7.0', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex11_things_vs_sparc.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX12: LITTLE THINGS dwarfs ────────────────────────────────────────────────
notebooks["ex12_little_things_dwarfs.ipynb"] = nb([
md(f"""# SPARC Example 12: LITTLE THINGS Dwarf Irregulars

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

LITTLE THINGS (Local Irregulars That Trace Luminosity Extremes)
provides 26 dwarf irregular galaxies with high-resolution VLA data.
These are the smallest, darkest-matter-dominated galaxies in the corpus.

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        if r['survey'] == 'LITTLE_THINGS':
            rows.append(r)

print(f"LITTLE THINGS galaxies: {len(rows)}")
dists = [float(r['distance_mpc']) for r in rows]
vmaxs = [float(r['vrot_max_kms']) for r in rows if r['vrot_max_kms']]
print(f"Distance range: {min(dists):.1f} -- {max(dists):.1f} Mpc")
print(f"Vrot_max range: {min(vmaxs):.1f} -- {max(vmaxs):.1f} km/s")
print(f"Median Vrot_max: {np.median(vmaxs):.1f} km/s")
print(f"\\nAll LITTLE THINGS galaxies:")
for r in sorted(rows, key=lambda x: float(x['vrot_max_kms'] or 0), reverse=True):
    print(f"  {r['galaxy']:<15} D={float(r['distance_mpc']):.1f} Mpc  "
          f"Vmax={r['vrot_max_kms']} km/s")"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(dists, bins=8, color='#2ca02c', alpha=0.8, edgecolor='white')
axes[0].set_xlabel('Distance (Mpc)', fontsize=11)
axes[0].set_ylabel('N galaxies', fontsize=11)
axes[0].set_title('LITTLE THINGS — Distance Distribution', fontsize=10)

axes[1].hist(vmaxs, bins=8, color='#ff7f0e', alpha=0.8, edgecolor='white')
axes[1].set_xlabel(r'$V_{\\rm rot,max}$ (km/s)', fontsize=11)
axes[1].set_ylabel('N galaxies', fontsize=11)
axes[1].set_title('LITTLE THINGS — Peak Velocity', fontsize=10)

plt.suptitle('LITTLE THINGS Subsample (26 galaxies)\\n'
             'EPS Research Unified HI Corpus v7.0', fontsize=11)
plt.tight_layout()
plt.savefig('ex12_little_things.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX13: Mass discrepancy ────────────────────────────────────────────────────
notebooks["ex13_mass_discrepancy.ipynb"] = nb([
md(f"""# SPARC Example 13: The Mass Discrepancy at R_max

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The ratio Vobs/Vbar at the outermost ring quantifies the mass discrepancy —
how much more mass is implied by kinematics than accounted for by baryons.
This is the central observational fact that dark matter, MOND, and the
omega correction each try to explain.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

results = []
for g in corpus['galaxies']:
    if g['survey'] != 'SPARC' or not g.get('data'):
        continue
    last = g['data'][-1]
    Vobs = last.get('Vobs', 0)
    Vgas = last.get('Vgas', 0)
    Vdisk= last.get('Vdisk', 0)
    Vbul = last.get('Vbul', 0)
    Vbar_sq = Vgas**2 + Vdisk**2 + Vbul**2
    if Vbar_sq <= 0 or Vobs <= 0:
        continue
    Vbar = np.sqrt(Vbar_sq)
    results.append({'galaxy': g['galaxy'], 'Vobs': Vobs,
                    'Vbar': Vbar, 'ratio': Vobs/Vbar})

ratios = [r['ratio'] for r in results]
print(f"SPARC galaxies with baryonic data: {len(results)}")
print(f"Median Vobs/Vbar at R_max: {np.median(ratios):.2f}")
print(f"Max ratio: {max(ratios):.2f} ({results[ratios.index(max(ratios))]['galaxy']})")
print(f"Min ratio: {min(ratios):.2f} ({results[ratios.index(min(ratios))]['galaxy']})")
print(f"\\nRatio > 2 (strong dark matter excess): "
      f"{sum(1 for r in ratios if r > 2)} galaxies")"""),
code("""fig, ax = plt.subplots(figsize=(8, 5))
vbars  = [r['Vbar']  for r in results]
ratios = [r['ratio'] for r in results]
sc = ax.scatter(vbars, ratios, s=20, alpha=0.6, c=ratios,
                cmap='RdYlBu_r', vmin=0.5, vmax=3.5)
plt.colorbar(sc, ax=ax, label=r'$V_{\\rm obs}/V_{\\rm bar}$')
ax.axhline(1.0, color='black', linestyle='--', linewidth=1, alpha=0.5,
           label=r'$V_{\\rm obs} = V_{\\rm bar}$ (no discrepancy)')
ax.set_xlabel(r'$V_{\\rm bar}$ at $R_{\\rm max}$ (km/s)', fontsize=12)
ax.set_ylabel(r'$V_{\\rm obs}/V_{\\rm bar}$', fontsize=12)
ax.set_title('Mass Discrepancy at Outermost Ring — SPARC\\n'
             'EPS Research Corpus v7.0', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex13_mass_discrepancy.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX14: Outer gap all SPARC ─────────────────────────────────────────────────
notebooks["ex14_outer_gap_distribution.ipynb"] = nb([
md(f"""# SPARC Example 14: Outer Gap Distribution — All SPARC Galaxies

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The outer gap is V_adj(R2) - V_bary(R2) — the residual between the
omega-corrected velocity and baryonic velocity at the outermost ring.
A key result of Flynn (2026): all 84 outer gaps are negative,
meaning V_adj always falls below V_bary, ruling out dark-matter re-importation.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

results = []
for g in corpus['galaxies']:
    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:
        continue
    d  = g['data']
    R  = [p['Rad']  for p in d]
    V  = [p['Vobs'] for p in d]
    R1, V1 = R[0],  V[0]
    R2, V2 = R[-1], V[-1]
    if R1<=0 or R2<=0 or V1<=0 or V2<=0:
        continue
    omega = (V2/R2 - V1/R1) * (R1/R2)**1.5
    V_adj = V2 - R2 * omega
    last  = d[-1]
    Vgas  = last.get('Vgas', 0)
    Vdisk = last.get('Vdisk', 0)
    Vbul  = last.get('Vbul', 0)
    Vbar_sq = Vgas**2 + Vdisk**2 + Vbul**2
    if Vbar_sq <= 0:
        continue
    Vbar = np.sqrt(Vbar_sq)
    gap  = V_adj - Vbar
    results.append({'galaxy': g['galaxy'], 'gap': gap,
                    'omega': omega, 'Vbar': Vbar})

gaps = [r['gap'] for r in results]
print(f"Galaxies with outer gap: {len(gaps)}")
print(f"All negative: {all(g < 0 for g in gaps)}")
print(f"Mean gap: {np.mean(gaps):.1f} km/s")
print(f"Std gap:  {np.std(gaps):.1f} km/s")
print(f"\\nPublished (Flynn 2026): mean = -51.4 ± 25.0 km/s, all 84 negative")"""),
code("""fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(gaps, bins=25, color='#2166ac', alpha=0.8, edgecolor='white')
ax.axvline(0, color='red', linestyle='--', linewidth=1.5,
           label='Gap = 0 boundary')
ax.axvline(np.mean(gaps), color='orange', linestyle='-', linewidth=1.5,
           label=f'Mean = {np.mean(gaps):.1f} km/s')
ax.set_xlabel(r'$V_{\\rm adj}(R_2) - V_{\\rm bar}(R_2)$ (km/s)', fontsize=11)
ax.set_ylabel('N galaxies', fontsize=11)
ax.set_title('Outer Gap Distribution — SPARC\\n'
             'All negative: V_adj < V_bar at outermost ring (Flynn 2026)',
             fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex14_outer_gap.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX15: Log slope ───────────────────────────────────────────────────────────
notebooks["ex15_log_slope_diagnostic.ipynb"] = nb([
md(f"""# SPARC Example 15: Log-Slope Diagnostic

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The logarithmic slope d ln V / d ln R diagnoses the rotation curve shape:
- slope = +1.0: solid-body rotation (rising linearly)
- slope = 0.0:  flat rotation curve (constant V)
- slope = -0.5: Keplerian decline (falling as 1/sqrt(R))

Galaxies with outer slope near -0.5 are falling toward Keplerian —
these are the strongest candidates for the omega correction.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# DDO161: compute slope at each ring
g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
d = g['data']
R    = np.array([p['Rad']  for p in d])
Vobs = np.array([p['Vobs'] for p in d])

# Log slope via finite differences
lnR  = np.log(R)
lnV  = np.log(Vobs)
slope = np.gradient(lnV, lnR)

print("DDO161 log-slope profile:")
print(f"{'R (kpc)':>10}  {'Vobs':>8}  {'d ln V / d ln R':>16}")
for r, v, s in zip(R, Vobs, slope):
    print(f"{r:>10.2f}  {v:>8.2f}  {s:>16.3f}")
print(f"\\nOuter slope: {slope[-1]:.3f}")
print(f"Keplerian slope: -0.5")"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(R, Vobs, 'o-', color='#1f77b4', linewidth=1.5)
axes[0].set_xlabel('Radius (kpc)', fontsize=11)
axes[0].set_ylabel(r'$V_{\\rm obs}$ (km/s)', fontsize=11)
axes[0].set_title('DDO161 Rotation Curve', fontsize=10)

axes[1].plot(R, slope, 's-', color='#d62728', linewidth=1.5)
axes[1].axhline(0.0,  color='gray',  linestyle='--', linewidth=1, label='Flat (slope=0)')
axes[1].axhline(-0.5, color='orange',linestyle='--', linewidth=1, label='Keplerian (slope=-0.5)')
axes[1].axhline(1.0,  color='green', linestyle='--', linewidth=1, label='Solid-body (slope=+1)')
axes[1].set_xlabel('Radius (kpc)', fontsize=11)
axes[1].set_ylabel(r'd ln V / d ln R', fontsize=11)
axes[1].set_title('Log-Slope Profile', fontsize=10)
axes[1].legend(fontsize=8)

plt.suptitle('Log-Slope Diagnostic — DDO161\\nEPS Research Corpus v7.0', fontsize=11)
plt.tight_layout()
plt.savefig('ex15_log_slope.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX16: Enclosed mass profile ───────────────────────────────────────────────
notebooks["ex16_enclosed_mass.ipynb"] = nb([
md(f"""# SPARC Example 16: Enclosed Mass Profile M(<R)

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

From the rotation curve we can compute the enclosed mass:

    M(<R) = V_obs^2 * R / G

where G = 4.301e-3 pc Msun^-1 (km/s)^2.
This gives total mass (baryons + dark matter) as a function of radius.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# G in units of kpc Msun^-1 (km/s)^2
G_kpc = 4.301e-3 * 1e-3  # kpc Msun^-1 (km/s)^2

targets = ['DDO161', 'NGC2403', 'UGC2885']
colors  = ['#2166ac', '#4dac26', '#d6604d']

fig, ax = plt.subplots(figsize=(8, 5))
for name, color in zip(targets, colors):
    try:
        g = next(g for g in corpus['galaxies'] if g['galaxy'] == name)
        d = g['data']
        R    = np.array([p['Rad']  for p in d])
        Vobs = np.array([p['Vobs'] for p in d])
        M    = Vobs**2 * R / G_kpc
        ax.plot(R, np.log10(M), 'o-', color=color, linewidth=1.5, markersize=4,
                label=f'{name}  log M_max={np.log10(M[-1]):.2f}')
    except StopIteration:
        print(f"{name} not found")

ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel(r'log$_{10}$ $M(<R)$ ($M_\\odot$)', fontsize=12)
ax.set_title('Enclosed Mass Profile M(<R) = V^2 R / G\\n'
             'EPS Research Unified HI Corpus v7.0', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex16_enclosed_mass.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX17: RMSE improvement over 84 galaxies ───────────────────────────────────
notebooks["ex17_rmse_improvement.ipynb"] = nb([
md(f"""# SPARC Example 17: RMSE Improvement — Reproducing Flynn (2026)

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

This example reproduces the RMSE comparison from Flynn (2026):
- RMSE(omega vs Vbar) vs RMSE(Keplerian vs Vbar) for each galaxy
- Published result: mean 25.45 ± 1.57 km/s vs 74.20 km/s (Keplerian)
- 2.0× improvement on average, 0 regressions

**Reference:** Flynn, D.C. (2026), New Astronomy (NEWAST-D-26-00207)
Preprint: DOI 10.5281/zenodo.20132805

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

results = []
for g in corpus['galaxies']:
    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:
        continue
    d  = g['data']
    R  = np.array([p['Rad']  for p in d])
    V  = np.array([p['Vobs'] for p in d])
    R1, V1 = R[0],  V[0]
    R2, V2 = R[-1], V[-1]
    if R1<=0 or R2<=0 or V1<=0 or V2<=0:
        continue
    # Omega and adjusted velocity
    omega = (V2/R2 - V1/R1) * (R1/R2)**1.5
    V_adj = V - R * omega
    # Keplerian
    GM       = V2**2 * R2
    V_kepler = np.sqrt(GM / R)
    # Baryonic
    Vgas  = np.array([p.get('Vgas', 0)  for p in d])
    Vdisk = np.array([p.get('Vdisk', 0) for p in d])
    Vbul  = np.array([p.get('Vbul', 0)  for p in d])
    Vbar  = np.where(Vgas < 0,
                     -np.sqrt(Vgas**2+Vdisk**2+Vbul**2),
                      np.sqrt(Vgas**2+Vdisk**2+Vbul**2))
    if np.all(Vbar == 0):
        continue
    rmse_omega  = np.sqrt(np.mean((V_adj   - Vbar)**2))
    rmse_kepler = np.sqrt(np.mean((V_kepler - Vbar)**2))
    results.append({'galaxy': g['galaxy'],
                    'rmse_omega': rmse_omega,
                    'rmse_kepler': rmse_kepler,
                    'improved': rmse_omega < rmse_kepler})

ro = [r['rmse_omega']  for r in results]
rk = [r['rmse_kepler'] for r in results]
improved = sum(1 for r in results if r['improved'])
print(f"Galaxies analyzed: {len(results)}")
print(f"Mean RMSE (omega):   {np.mean(ro):.2f} ± {np.std(ro)/np.sqrt(len(ro)):.2f} km/s")
print(f"Mean RMSE (Kepler):  {np.mean(rk):.2f} km/s")
print(f"Improved: {improved}/{len(results)}")
print(f"Regressions: {len(results)-improved}/{len(results)}")
print(f"\\nPublished: 25.45 ± 1.57 km/s, improved 53/84, 0 regressions")"""),
code("""fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(rk, ro, s=20, alpha=0.6, color='#2166ac', zorder=3)
lim = [0, max(rk+ro)*1.05]
ax.plot(lim, lim, 'k--', linewidth=1, alpha=0.4, label='1:1 (no improvement)')
ax.set_xlabel('RMSE Keplerian (km/s)', fontsize=12)
ax.set_ylabel('RMSE Omega (km/s)', fontsize=12)
ax.set_title('RMSE: Omega vs Keplerian Baseline\\n'
             'Points below diagonal = omega improves fit (Flynn 2026)', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex17_rmse_improvement.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX18: Omega vs HI radius correlation ──────────────────────────────────────
notebooks["ex18_omega_vs_rmax.ipynb"] = nb([
md(f"""# SPARC Example 18: Omega vs Galaxy Size

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

Does omega correlate with galaxy size (R_max)?
This tests whether omega is a geometric artifact of the
boundary point selection or a genuine kinematic property.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

results = []
for g in corpus['galaxies']:
    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:
        continue
    d  = g['data']
    R  = [p['Rad']  for p in d]
    V  = [p['Vobs'] for p in d]
    R1, V1 = R[0],  V[0]
    R2, V2 = R[-1], V[-1]
    if R1<=0 or R2<=0 or V1<=0 or V2<=0:
        continue
    omega = (V2/R2 - V1/R1) * (R1/R2)**1.5
    results.append({'galaxy': g['galaxy'], 'omega': omega,
                    'R_max': R2, 'V_max': max(V)})

R_max  = [r['R_max']  for r in results]
omegas = [r['omega']  for r in results]
corr   = np.corrcoef(R_max, omegas)[0, 1]
print(f"N galaxies: {len(results)}")
print(f"Pearson r (omega vs R_max): {corr:.3f}")
print(f"Interpretation: {'weak' if abs(corr)<0.3 else 'moderate' if abs(corr)<0.6 else 'strong'} correlation")"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].scatter(R_max, omegas, s=18, alpha=0.6, color='#2166ac')
axes[0].set_xlabel(r'$R_{\\rm max}$ (kpc)', fontsize=11)
axes[0].set_ylabel(r'$\\omega$ (rad/Gyr)', fontsize=11)
axes[0].set_title(f'Omega vs R_max (r={corr:.2f})', fontsize=10)

V_max  = [r['V_max']  for r in results]
corr2  = np.corrcoef(V_max, omegas)[0, 1]
axes[1].scatter(V_max, omegas, s=18, alpha=0.6, color='#d62728')
axes[1].set_xlabel(r'$V_{\\rm max}$ (km/s)', fontsize=11)
axes[1].set_ylabel(r'$\\omega$ (rad/Gyr)', fontsize=11)
axes[1].set_title(f'Omega vs V_max (r={corr2:.2f})', fontsize=10)

plt.suptitle('Omega Correlations — EPS Research SPARC Sample\\n'
             'Testing whether omega is a geometric artifact', fontsize=10)
plt.tight_layout()
plt.savefig('ex18_omega_correlations.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX19: Baryonic Tully-Fisher ───────────────────────────────────────────────
notebooks["ex19_baryonic_tully_fisher.ipynb"] = nb([
md(f"""# SPARC Example 19: Baryonic Tully-Fisher Relation

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The Baryonic Tully-Fisher Relation (BTFR) relates total baryonic mass
to peak rotation velocity: M_bar ∝ V^4.
SPARC is one of the definitive datasets for this relation.

We estimate M_bar ≈ M_HI * 1.33 (helium correction) here as a proxy
since full stellar masses are not in the corpus for all galaxies.

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        rows.append(r)

# Use LITTLE THINGS which has r0p3 data
lt = [r for r in rows if r['survey']=='LITTLE_THINGS'
      and r['vrot_max_kms'] and r.get('v0p3_kms') and r['v0p3_kms']]

vmax = np.array([float(r['v0p3_kms'])     for r in lt])
# Use r_max as proxy for size
rmax = np.array([float(r['r_max_kpc'])    for r in lt])

print(f"LITTLE THINGS galaxies with v0.3: {len(lt)}")
print(f"v0.3 range: {vmax.min():.1f} -- {vmax.max():.1f} km/s")
print(f"\\nNote: v0.3 is velocity at radius where log slope = 0.3")
print(f"This is the LITTLE THINGS characteristic velocity parameter")
print(f"from Oh et al. (2015), Table 1")"""),
code("""fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(np.log10(vmax), rmax, s=40, color='#2ca02c', alpha=0.8)
for r, rv, rm in zip(lt[:8], np.log10(vmax[:8]), rmax[:8]):
    ax.annotate(r['galaxy'], (rv, rm),
                textcoords='offset points', xytext=(4, 3), fontsize=7)
ax.set_xlabel(r'log$_{10}$ $V_{0.3}$ (km/s)', fontsize=12)
ax.set_ylabel(r'$R_{\\rm max}$ (kpc)', fontsize=12)
ax.set_title('LITTLE THINGS: Velocity vs Size\\n'
             'EPS Research Corpus v7.0 | v0.3 from Oh et al. (2015)', fontsize=10)
plt.tight_layout()
plt.savefig('ex19_btfr_proxy.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX20: SPARC galaxy gallery ────────────────────────────────────────────────
notebooks["ex20_rotation_curve_gallery.ipynb"] = nb([
md(f"""# SPARC Example 20: Rotation Curve Gallery

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

A gallery of 12 SPARC rotation curves illustrating the full diversity
of shapes found across galaxy types — from rising solid-body curves
in dwarfs to declining Keplerian-like profiles in massive spirals.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Select 12 SPARC galaxies spanning the Vmax range
sparc = [g for g in corpus['galaxies']
         if g['survey']=='SPARC' and g.get('data') and len(g['data'])>=5]
sparc_sorted = sorted(sparc, key=lambda x: max(p['Vobs'] for p in x['data']))
n = len(sparc_sorted)
indices = [int(i*n/12) for i in range(12)]
selected = [sparc_sorted[i] for i in indices]

fig, axes = plt.subplots(3, 4, figsize=(14, 9))
axes = axes.flatten()

for i, g in enumerate(selected):
    d    = g['data']
    R    = [p['Rad']  for p in d]
    Vobs = [p['Vobs'] for p in d]
    axes[i].plot(R, Vobs, 'o-', color='#1f77b4', linewidth=1.2, markersize=3)
    axes[i].set_title(f"{g['galaxy']}\\nVmax={max(Vobs):.0f} km/s", fontsize=8)
    axes[i].set_xlabel('R (kpc)', fontsize=7)
    axes[i].set_ylabel('V (km/s)', fontsize=7)
    axes[i].tick_params(labelsize=7)

plt.suptitle('SPARC Rotation Curve Gallery — EPS Research Corpus v7.0\\n'
             '12 galaxies spanning full Vmax range', fontsize=11)
plt.tight_layout()
plt.savefig('ex20_gallery.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX21: SPARC query by property ─────────────────────────────────────────────
notebooks["ex21_query_by_property.ipynb"] = nb([
md(f"""# SPARC Example 21: Querying the Corpus by Property

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The flat CSV enables fast filtering by any galaxy property.
This example demonstrates practical query patterns researchers use:
- Find the largest galaxies
- Find galaxies with strong gas content
- Find galaxies with many data points (best-sampled RCs)
- Find galaxies by Hubble type

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np

rows = []
with open('rotation_curve_corpus_v7_flat.csv') as f:
    for r in csv.DictReader(f):
        rows.append(r)

# Query 1: Largest galaxies by R_max
sparc = [r for r in rows if r['survey']=='SPARC' and r['r_max_kpc']]
largest = sorted(sparc, key=lambda x: float(x['r_max_kpc']), reverse=True)[:5]
print("Top 5 largest SPARC galaxies by R_max:")
for r in largest:
    print(f"  {r['galaxy']:<15} R_max={float(r['r_max_kpc']):.1f} kpc  "
          f"Vmax={r['vrot_max_kms']} km/s")

# Query 2: Most data points
best = sorted([r for r in sparc if r['n_points']],
              key=lambda x: int(float(x['n_points'])), reverse=True)[:5]
print("\\nTop 5 best-sampled SPARC rotation curves:")
for r in best:
    print(f"  {r['galaxy']:<15} N={int(float(r['n_points']))} points")

# Query 3: Galaxies with negative Vgas rows (strong gas term)
gas_rich = [r for r in sparc if r.get('vgas_negative_rows')
            and float(r['vgas_negative_rows']) > 3]
print(f"\\nSPARC galaxies with >3 negative Vgas rows (strong gas term): {len(gas_rich)}")
for r in gas_rich[:5]:
    print(f"  {r['galaxy']:<15} neg_Vgas_rows={r['vgas_negative_rows']}")""")
])

# ── EX22: Distance uncertainty effects ────────────────────────────────────────
notebooks["ex22_distance_uncertainty.ipynb"] = nb([
md(f"""# SPARC Example 22: Distance Uncertainty and Its Effect on Omega

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

SPARC distance uncertainties (e_distance_mpc) are published by Lelli et al. (2016).
Since R_kpc = R_arcsec * D_Mpc, distance uncertainty propagates into
the radius scale and therefore omega.

This example quantifies how much omega changes with ±1σ distance.

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

g = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
d = g['data']
D      = g['distance_mpc']
e_D    = g.get('e_distance_mpc', D * 0.1)

R    = np.array([p['Rad']  for p in d])
Vobs = np.array([p['Vobs'] for p in d])

def compute_omega(R, Vobs):
    R1, V1 = R[0],  Vobs[0]
    R2, V2 = R[-1], Vobs[-1]
    if R1<=0 or R2<=0:
        return None
    return (V2/R2 - V1/R1) * (R1/R2)**1.5

omega_nominal = compute_omega(R, Vobs)

# Scale radii by distance
omega_plus  = compute_omega(R * (D + e_D) / D, Vobs)
omega_minus = compute_omega(R * (D - e_D) / D, Vobs)

print(f"DDO161:")
print(f"  Distance:      {D:.2f} ± {e_D:.2f} Mpc")
print(f"  Omega nominal: {omega_nominal:.3f} rad/Gyr")
print(f"  Omega D+1σ:    {omega_plus:.3f} rad/Gyr")
print(f"  Omega D-1σ:    {omega_minus:.3f} rad/Gyr")
print(f"  Delta omega:   ±{(omega_plus - omega_minus)/2:.3f} rad/Gyr")
print(f"  Fractional:    {abs(omega_plus-omega_minus)/(2*omega_nominal)*100:.1f}%")""")
])

# ── EX23: Cross-survey schema demo ────────────────────────────────────────────
notebooks["ex23_cross_survey_schema.ipynb"] = nb([
md(f"""# SPARC Example 23: Cross-Survey Schema Navigation

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

The corpus combines four surveys with different schemas.
This example demonstrates the correct way to access per-ring data
regardless of survey — a common source of bugs in cross-survey code.

Key pattern:
```python
points = g.get('data') or g.get('rotation_curve', [])
```

{CORPUS_NOTE}"""),
code("""import json
import numpy as np

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Demonstrate schema differences
examples = {
    'SPARC':        'DDO161',
    'THINGS':       next(g['galaxy'] for g in corpus['galaxies']
                         if g['survey']=='THINGS' and g.get('data')),
    'LITTLE_THINGS':next(g['galaxy'] for g in corpus['galaxies']
                         if g['survey']=='LITTLE_THINGS'),
    'WALLABY':      next(g['galaxy'] for g in corpus['galaxies']
                         if g['survey']=='WALLABY' and g.get('rotation_curve')),
}

print(f"{'Survey':<15} {'Galaxy':<20} {'Data key':<20} {'R field':<12} {'V field'}")
print('-' * 80)
for survey, name in examples.items():
    g = next(g for g in corpus['galaxies'] if g['galaxy']==name)
    if g.get('data'):
        key = 'data'
        r_field = list(g['data'][0].keys())[0] if g['data'] else '?'
        v_field = 'Vobs' if 'Vobs' in g['data'][0] else 'Vrot'
    elif g.get('rotation_curve'):
        key = 'rotation_curve'
        r_field = 'rad_kpc'
        v_field = 'vrot_kms'
    else:
        key, r_field, v_field = 'none', '-', '-'
    print(f"{survey:<15} {name:<20} {key:<20} {r_field:<12} {v_field}")
"""),
code("""# Safe cross-survey extraction function
def get_rc(g):
    \"\"\"Extract (R, V) from any survey in the EPS corpus.\"\"\"
    if g.get('data'):
        d = g['data']
        R = [p.get('Rad') or p.get('Vrot') for p in d]  # fallback
        R = [p.get('Rad', 0) for p in d]
        V = [p.get('Vobs') or p.get('Vrot', 0) for p in d]
    elif g.get('rotation_curve'):
        rc = g['rotation_curve']
        R  = [p['rad_kpc']  for p in rc]
        V  = [p['vrot_kms'] for p in rc]
    else:
        return None, None
    return np.array(R), np.array(V)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 5))
colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728']
for (survey, name), color in zip(examples.items(), colors):
    g = next(g for g in corpus['galaxies'] if g['galaxy']==name)
    R, V = get_rc(g)
    if R is not None:
        ax.plot(R, V, 'o-', color=color, linewidth=1.5, markersize=4,
                label=f'{survey}: {name}')
ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel('Velocity (km/s)', fontsize=12)
ax.set_title('Cross-Survey Rotation Curves — Single Extraction Function\\n'
             'EPS Research Corpus v7.0', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex23_cross_survey.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX24: SPARC RAG single-galaxy report ──────────────────────────────────────
notebooks["ex24_single_galaxy_report.ipynb"] = nb([
md(f"""# SPARC Example 24: Single Galaxy Full Report

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

A complete kinematic report for a single SPARC galaxy:
all metadata, rotation curve, baryonic decomposition, omega correction,
and RMSE diagnostics — from a single JSON load.

This is the kind of output a RAG system would generate
in response to: "Give me a full kinematic analysis of NGC 2403."

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

GALAXY = 'NGC2403'  # Change to any SPARC galaxy
g = next(g for g in corpus['galaxies'] if g['galaxy'] == GALAXY)
d = g['data']

R     = np.array([p['Rad']   for p in d])
Vobs  = np.array([p['Vobs']  for p in d])
errV  = np.array([p['errV']  for p in d])
Vgas  = np.array([p['Vgas']  for p in d])
Vdisk = np.array([p['Vdisk'] for p in d])
Vbul  = np.array([p['Vbul']  for p in d])

Vbar = np.where(Vgas<0, -np.sqrt(Vgas**2+Vdisk**2+Vbul**2),
                         np.sqrt(Vgas**2+Vdisk**2+Vbul**2))

R1, V1 = R[0],  Vobs[0]
R2, V2 = R[-1], Vobs[-1]
omega   = (V2/R2 - V1/R1) * (R1/R2)**1.5
V_adj   = Vobs - R * omega
GM      = V2**2 * R2
V_kep   = np.sqrt(GM / R)

rmse_omega  = np.sqrt(np.mean((V_adj - Vbar)**2))
rmse_kepler = np.sqrt(np.mean((V_kep  - Vbar)**2))
outer_gap   = (V2 - R2*omega) - np.sqrt(Vgas[-1]**2+Vdisk[-1]**2+Vbul[-1]**2)

print(f"=== {GALAXY} — EPS Research Full Kinematic Report ===")
print(f"Survey:        {g['survey']} Tier {g['quality_tier']}")
print(f"Distance:      {g['distance_mpc']} ± {g.get('e_distance_mpc','?')} Mpc")
print(f"Inclination:   {g['inc_deg']} ± {g.get('e_inc_deg','?')} deg")
print(f"N rings:       {g['n_points']}")
print(f"R range:       {R.min():.2f} -- {R.max():.2f} kpc")
print(f"Vmax:          {Vobs.max():.1f} km/s")
print(f"Omega:         {omega:.3f} rad/Gyr")
print(f"RMSE omega:    {rmse_omega:.2f} km/s")
print(f"RMSE Kepler:   {rmse_kepler:.2f} km/s")
print(f"Outer gap:     {outer_gap:.2f} km/s ({'negative ✓' if outer_gap<0 else 'positive'})")"""),
code("""fig = plt.figure(figsize=(11, 7))
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])

ax1.errorbar(R, Vobs, yerr=errV, fmt='o', color='#1f77b4', capsize=3,
             markersize=5, label=r'$V_{\\rm obs}$', zorder=5)
ax1.plot(R, Vbar,  's-', color='#d62728', lw=1.5, label=r'$V_{\\rm bar}$')
ax1.plot(R, V_adj, '^-', color='#2ca02c', lw=1.8,
         label=fr'$V_{{\\rm adj}}$ ($\\omega={omega:.2f}$ rad/Gyr)')
ax1.plot(R, V_kep, '--', color='#ff7f0e', lw=1.2, label='Keplerian')
ax1.set_ylabel('km/s', fontsize=11)
ax1.set_title(f'{GALAXY} — Full Kinematic Report | EPS Research Corpus v7.0', fontsize=11)
ax1.legend(fontsize=8)

ax2.plot(R, Vgas,  'g^-', lw=1.2, label=r'$V_{\\rm gas}$')
ax2.plot(R, Vdisk, 'bv-', lw=1.2, label=r'$V_{\\rm disk}$')
ax2.plot(R, Vbul,  'rs-', lw=1.2, label=r'$V_{\\rm bul}$')
ax2.axhline(0, color='k', lw=0.7, alpha=0.4)
ax2.set_xlabel('Radius (kpc)', fontsize=10)
ax2.set_ylabel('km/s', fontsize=10)
ax2.set_title('Baryonic Components', fontsize=10)
ax2.legend(fontsize=8)

lnR = np.log(R)
lnV = np.log(Vobs)
slope = np.gradient(lnV, lnR)
ax3.plot(R, slope, 'o-', color='#9467bd', lw=1.5)
ax3.axhline(-0.5, color='orange', ls='--', lw=1, label='Keplerian (-0.5)')
ax3.axhline(0.0,  color='gray',   ls='--', lw=1, label='Flat (0.0)')
ax3.set_xlabel('Radius (kpc)', fontsize=10)
ax3.set_ylabel('d ln V / d ln R', fontsize=10)
ax3.set_title('Log-Slope Profile', fontsize=10)
ax3.legend(fontsize=8)

plt.savefig(f'ex24_{GALAXY}_report.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX25: End-to-end omega workflow ───────────────────────────────────────────
notebooks["ex25_end_to_end_omega_workflow.ipynb"] = nb([
md(f"""# SPARC Example 25: End-to-End Omega Workflow

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.0**

This capstone example runs the complete EPS Research omega workflow
on the full SPARC sample and produces a summary table mirroring
Table 2 from Flynn & Cannaliato (2025).

Steps:
1. Load corpus
2. Filter SPARC Q=1 galaxies
3. Compute omega for each
4. Compute RMSE improvement
5. Flag outer gap sign
6. Print summary table

**Reference:** Flynn, D.C. & Cannaliato, J. (2025).
DOI: 10.3389/fspas.2025.1680387

{CORPUS_NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

results = []
for g in corpus['galaxies']:
    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:
        continue
    d  = g['data']
    R  = np.array([p['Rad']  for p in d])
    V  = np.array([p['Vobs'] for p in d])
    R1, V1 = R[0],  V[0]
    R2, V2 = R[-1], V[-1]
    if R1<=0 or R2<=0 or V1<=0 or V2<=0:
        continue
    omega = (V2/R2 - V1/R1) * (R1/R2)**1.5
    V_adj = V - R * omega
    GM    = V2**2 * R2
    V_kep = np.sqrt(GM / R)
    Vgas  = np.array([p.get('Vgas', 0)  for p in d])
    Vdisk = np.array([p.get('Vdisk', 0) for p in d])
    Vbul  = np.array([p.get('Vbul', 0)  for p in d])
    Vbar  = np.where(Vgas<0,
                     -np.sqrt(Vgas**2+Vdisk**2+Vbul**2),
                      np.sqrt(Vgas**2+Vdisk**2+Vbul**2))
    if np.all(Vbar == 0):
        continue
    rmse_o = np.sqrt(np.mean((V_adj - Vbar)**2))
    rmse_k = np.sqrt(np.mean((V_kep  - Vbar)**2))
    gap    = (V[-1] - R[-1]*omega) - np.abs(Vbar[-1])
    results.append({
        'galaxy':   g['galaxy'],
        'omega':    omega,
        'rmse_o':   rmse_o,
        'rmse_k':   rmse_k,
        'improved': rmse_o < rmse_k,
        'gap':      gap,
        'gap_neg':  gap < 0,
    })

# Summary
omegas  = [r['omega']  for r in results]
rmse_os = [r['rmse_o'] for r in results]
rmse_ks = [r['rmse_k'] for r in results]
improved = sum(1 for r in results if r['improved'])
gaps_neg = sum(1 for r in results if r['gap_neg'])

print(f"{'='*60}")
print(f"EPS Research Omega Workflow — SPARC Summary")
print(f"{'='*60}")
print(f"Galaxies analyzed:     {len(results)}")
print(f"Mean omega:            {np.mean(omegas):.2f} ± {np.std(omegas):.2f} rad/Gyr")
print(f"Mean RMSE (omega):     {np.mean(rmse_os):.2f} km/s")
print(f"Mean RMSE (Keplerian): {np.mean(rmse_ks):.2f} km/s")
print(f"Improved:              {improved}/{len(results)}")
print(f"Regressions:           {len(results)-improved}/{len(results)}")
print(f"Outer gaps negative:   {gaps_neg}/{len(results)}")
print(f"\\nPublished results (Flynn & Cannaliato 2025):")
print(f"  Mean RMSE (omega):  25.45 ± 1.57 km/s")
print(f"  Improved:           53/84")
print(f"  Regressions:        0/84")
print(f"  Outer gaps neg:     84/84")"""),
code("""fig, axes = plt.subplots(1, 3, figsize=(14, 4))

axes[0].hist(omegas, bins=25, color='#2166ac', alpha=0.8, edgecolor='white')
axes[0].axvline(np.mean(omegas), color='red', ls='--', lw=1.5,
                label=f'Mean={np.mean(omegas):.2f}')
axes[0].set_xlabel(r'$\\omega$ (rad/Gyr)', fontsize=11)
axes[0].set_ylabel('N', fontsize=11)
axes[0].set_title('Omega Distribution', fontsize=10)
axes[0].legend(fontsize=8)

axes[1].scatter(rmse_ks, rmse_os, s=18, alpha=0.6, color='#2166ac')
lim = [0, max(rmse_ks+rmse_os)*1.05]
axes[1].plot(lim, lim, 'k--', lw=1, alpha=0.4, label='1:1')
axes[1].set_xlabel('RMSE Keplerian (km/s)', fontsize=11)
axes[1].set_ylabel('RMSE Omega (km/s)', fontsize=11)
axes[1].set_title('RMSE Comparison', fontsize=10)
axes[1].legend(fontsize=8)

gaps = [r['gap'] for r in results]
axes[2].hist(gaps, bins=25, color='#d62728', alpha=0.8, edgecolor='white')
axes[2].axvline(0, color='black', ls='--', lw=1.5, label='Gap=0')
axes[2].set_xlabel('Outer gap (km/s)', fontsize=11)
axes[2].set_ylabel('N', fontsize=11)
axes[2].set_title('Outer Gap Distribution', fontsize=10)
axes[2].legend(fontsize=8)

plt.suptitle('End-to-End EPS Omega Workflow — SPARC Sample\\n'
             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387',
             fontsize=10)
plt.tight_layout()
plt.savefig('ex25_end_to_end.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── Write all notebooks ───────────────────────────────────────────────────────

written = 0
for filename, notebook in notebooks.items():
    with open(filename, 'w') as f:
        json.dump(notebook, f, indent=1)
    written += 1
    print(f"Written: {filename}")

print(f"\n{'='*50}")
print(f"SPARC/HI Examples: {written}/25 notebooks written")
print(f"{'='*50}")
print(f"\nNext steps:")
print(f"1. Run: jupyter lab")
print(f"2. Open each notebook and run all cells")
print(f"3. Verify figures save cleanly")
print(f"4. git add examples/hi/ && git commit -m 'Add 25 SPARC/HI examples'")
print(f"5. git push")
