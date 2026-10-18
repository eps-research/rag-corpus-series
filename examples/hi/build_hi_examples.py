#!/usr/bin/env python3
"""
EPS Research — Build all 25 SPARC/HI Example Notebooks
Run from: examples/hi/
Requires: rotation_curve_corpus_v7.json and rotation_curve_corpus_v7.1_flat.csv
          in the same directory.
Output:   25 .ipynb files ready to run in JupyterLab.

Usage:
    python3 build_hi_examples.py

Flynn, D.C. (2026) EPS Research
DOI: 10.5281/zenodo.23442703
"""

import json
import os

# ── Notebook builder helpers ──────────────────────────────────────────────────

COLAB_SETUP = "# ── Colab setup: auto-download corpus from Zenodo ─────────────\nimport os, sys\nIN_COLAB = 'google.colab' in sys.modules\nif IN_COLAB:\n    import urllib.request\n    CORPORA = {\n        'rotation_curve_corpus_v7.json': 'https://zenodo.org/records/23442703/files/rotation_curve_corpus_v7.json',\n    }\n    for filename, url in CORPORA.items():\n        if not os.path.exists(filename):\n            print(f\"Downloading {filename}...\")\n            urllib.request.urlretrieve(url, filename)\n            print(f\"  ✓ {filename}\")\n        else:\n            print(f\"  Already present: {filename}\")\n    print(\"Ready.\")\nelse:\n    print(\"Running locally — corpus files loaded from working directory.\")\n"
COLAB_SETUP_EX19 = "# ── Colab setup: auto-download corpus from Zenodo ─────────────\nimport os, sys\nIN_COLAB = 'google.colab' in sys.modules\nif IN_COLAB:\n    import urllib.request\n    CORPORA = {\n        'rotation_curve_corpus_v7.json':\n            'https://zenodo.org/records/23442703/files/rotation_curve_corpus_v7.json',\n    }\n    for filename, url in CORPORA.items():\n        if not os.path.exists(filename):\n            print(f\"Downloading {filename}...\")\n            urllib.request.urlretrieve(url, filename)\n            print(f\"  ✓ {filename}\")\n        else:\n            print(f\"  Already present: {filename}\")\n    print(\"Ready.\")\nelse:\n    print(\"Running locally — corpus files loaded from working directory.\")"

def nb(cells):
    setup = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": COLAB_SETUP
    }
    cells = [cells[0], setup] + cells[1:]
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

# -- Shared Eq. 1 helper (register G1/G1b): prepended to any cell that calls vbar_eq1() --
VBAR_EQ1_SRC = 'import numpy as np\ndef vbar_eq1(Vgas, Vdisk, Vbul, ups_disk=1.0, ups_bul=1.0):\n    """Baryonic velocity, Flynn (2027) Eq. 1; the sign is applied to Vgas^2 only.\n    Vbar^2 = |Vgas|*Vgas + ups_disk*Vdisk^2 + ups_bul*Vbul^2;  Vbar = sign(Vbar^2)*sqrt(|Vbar^2|)."""\n    Vgas, Vdisk, Vbul = (np.asarray(x, dtype=float) for x in (Vgas, Vdisk, Vbul))\n    vb2 = np.abs(Vgas)*Vgas + ups_disk*Vdisk**2 + ups_bul*Vbul**2\n    return np.sign(vb2)*np.sqrt(np.abs(vb2))\n\n'

def _with_vbar(text):
    if 'vbar_eq1(' in text and 'def vbar_eq1' not in text:
        return VBAR_EQ1_SRC + text
    return text


def code(text):
    text = _with_vbar(text)
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text
    }

CORPUS_NOTE = (
    "**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` "
    "and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. "
    "The CSV contains every kinematic parameter published by Lelli et al. (2016) "
    "including per-galaxy inclination, distance uncertainties, mass-to-light ratios, "
    "and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, "
    "Vdisk, Vbul, errV at every radial point. This is the complete published dataset "
    "in a single machine-readable file.\n\n"
    "**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n"
    "**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n"
    "**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"
)

# ── Define all 25 notebooks ───────────────────────────────────────────────────

notebooks = {}

# ── EX01: First rotation curve ────────────────────────────────────────────────
notebooks["ex01_first_rotation_curve.ipynb"] = nb([
md(f"""# SPARC Example 01: Your First Rotation Curve

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

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
             'EPS Research Unified HI Corpus v7.3', fontsize=11)
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

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

SPARC is unique: it provides not just Vobs but the full baryonic decomposition —
Vgas, Vdisk, and Vbul at every radial point. This is full-fidelity data directly
from Lelli et al. (2016), not derived or estimated.

We compute the baryonic velocity using sign-preserving quadrature:

    Vbar = sqrt(Upsilon*Vdisk^2 + Upsilon_b*Vbul^2 + sign(Vgas)*Vgas^2)

Note: Vgas is negative at inner radii where the gas distribution is centrally depressed; there the gas exerts a net outward pull (Lelli et al. 2016).

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

# Baryonic velocity, Eq. 1 (sign on Vgas^2 only), Upsilon=1
Vbar = vbar_eq1(Vgas, Vdisk, Vbul)

print(f"Vgas negative rows: {(Vgas < 0).sum()} (inner radii: outward pull of centrally depressed gas)")
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
             'Full-fidelity SPARC data, EPS Research Corpus v7.3', fontsize=11)
ax.legend(fontsize=9)
ax.text(0.02, 0.95,
        'Vgas < 0 at inner radii\\n= outward pull of central gas deficit\\n(sign on Vgas^2 only, Eq. 1)',
        transform=ax.transAxes, va='top', fontsize=8,
        bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', alpha=0.85))
plt.tight_layout()
plt.savefig('ex02_ddo161_baryonic.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX03: Omega correction (EPS flagship) ─────────────────────────────────────
notebooks["ex03_omega_correction_ddo161.ipynb"] = nb([
    md("# SPARC Example 03: The Omega Kinematic Correction (EPS Research)\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThis is the core EPS Research result. The omega kinematic correction is derived\nfrom boundary points only — no free parameters, no mass modeling:\n\n    V_adj = V_obs - R * omega_kms_kpc\n    outer_term    = (V2 / R2)\n    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n\nwhere (R1, V1) = innermost ring, (R2, V2) = outermost ring.\nNote: 1 km/s/kpc = 1.0227 rad/Gyr.\n\n**Published result:** omega = 4.69 rad/Gyr for DDO161\n**Reference:** Flynn & Cannaliato (2025), DOI: 10.3389/fspas.2025.1680387\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\ng = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')\nd = g['data']\n\nR     = np.array([p['Rad']   for p in d])\nVobs  = np.array([p['Vobs']  for p in d])\nerrV  = np.array([p['errV']  for p in d])\nVgas  = np.array([p['Vgas']  for p in d])\nVdisk = np.array([p['Vdisk'] for p in d])\nVbul  = np.array([p['Vbul']  for p in d])\n\n# Baryonic velocity\nVbar = vbar_eq1(Vgas, Vdisk, Vbul)\n\n# Omega from boundary points\nR1, V1 = R[0],  Vobs[0]\nR2, V2 = R[-1], Vobs[-1]\nouter_term    = (V2 / R2)\ninner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\nomega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\nomega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\nomega = omega_rad_gyr  # reporting/storage only — use omega_kms_kpc for velocity arithmetic\nV_adj  = Vobs - R * omega_kms_kpc\n\n# Keplerian baseline\nGM       = V2**2 * R2\nV_kepler = np.sqrt(GM / R)\n\n# RMSE\nrmse_omega  = np.sqrt(np.mean((V_adj  - Vbar)**2))\nrmse_kepler = np.sqrt(np.mean((V_kepler - Vbar)**2))\n\nprint(f\"Computed omega  = {omega:.3f} rad/Gyr\")\nprint(f\"Published omega = 4.69 rad/Gyr (Flynn & Cannaliato 2025)\")\nprint(f\"RMSE (omega vs Vbar):   {rmse_omega:.2f} km/s\")\nprint(f\"RMSE (Kepler vs Vbar):  {rmse_kepler:.2f} km/s\")\nprint(f\"Improvement:            {rmse_kepler - rmse_omega:.2f} km/s\")"),
    code("fig, ax = plt.subplots(figsize=(9, 5))\nax.errorbar(R, Vobs, yerr=errV, fmt='o', color='#1f77b4',\n            capsize=4, markersize=6, label=r'$V_{\\rm obs}$ (SPARC)', zorder=5)\nax.plot(R, Vbar,     's-', color='#d62728', linewidth=1.5,\n        label=r'$V_{\\rm bar}$ ($\\Upsilon=1$)')\nax.plot(R, V_adj,    '^-', color='#2ca02c', linewidth=1.8,\n        label=fr'$V_{{\\rm obs}} - R\\omega$  ($\\omega={omega:.2f}$ rad/Gyr)')\nax.plot(R, V_kepler, '--', color='#ff7f0e', linewidth=1.2,\n        label='Keplerian baseline')\nax.set_xlabel('Radius (kpc)', fontsize=12)\nax.set_ylabel('Velocity (km/s)', fontsize=12)\nax.set_title('DDO161 — Omega Kinematic Correction\\n'\n             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387', fontsize=10)\nax.legend(fontsize=9)\nax.set_xlim(0, R.max() * 1.15)\nax.set_ylim(0, Vobs.max() * 1.35)\nax.text(0.97, 0.08,\n        f'RMSE omega: {rmse_omega:.1f} km/s\\nRMSE Kepler: {rmse_kepler:.1f} km/s',\n        transform=ax.transAxes, ha='right', va='bottom', fontsize=9,\n        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))\nplt.tight_layout()\nplt.savefig('ex03_ddo161_omega.png', dpi=150, bbox_inches='tight')\nplt.show()")
])

# ── EX04: WALLABY Tier 2 ──────────────────────────────────────────────────────
notebooks["ex04_wallaby_tier2.ipynb"] = nb([
md(f"""# SPARC Example 04: WALLABY Tier 2 — Automated Pipeline with Caution Zone

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

WALLABY DR2 contributes 203 galaxies from the ASKAP automated pipeline.
Unlike SPARC/THINGS/LITTLE THINGS (Tier 1), WALLABY is Tier 2:
no per-ring uncertainties, no baryonic decomposition.

Key limitation: 30 arcsec ASKAP beam — Vrot < 50 km/s is unreliable.

Schema: since v7.3 all surveys use the `data` key. WALLABY rows hold `Rad`/`Vrot`/`e_Vrot` (published DR2 WKAPP models).
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
           and g.get('data')
           and len(g['data']) >= 3]
wg = sorted(wallaby, key=lambda x: len(x['data']), reverse=True)[0]

print(f"Galaxy:      {wg['galaxy']}")
print(f"Survey:      {wg['survey']} (Tier {wg['quality_tier']})")
print(f"Distance:    {wg['distance_mpc']} Mpc")
print(f"Inclination: {wg['inc_deg']} deg")
print(f"N rings:     {len(wg['data'])}")
print(f"\\nKey schema difference:")
print(f"  WALLABY: data -> Rad, Vrot, e_Vrot (WKAPP model)")
print(f"  SPARC:   data           -> Rad, Vobs")"""),
code("""rc  = wg['data']
R_w = np.array([p['Rad']  for p in rc])
V_w = np.array([p['Vrot'] for p in rc])
E_w = np.array([p.get('e_Vrot') or 0 for p in rc])

fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(R_w, V_w, yerr=E_w, fmt='o-', capsize=2, color='#B2182B', linewidth=1.8, markersize=5,
        label=r'$V_{\\rm rot}$ (WKAPP model, WALLABY DR2)')
ax.axhspan(0, 50, alpha=0.12, color='red',
           label=r'$V_{\\rm rot}$ < 50 km/s (beam-smearing caution zone)')
ax.axhline(50, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
ax.set_xlabel('Radius (kpc)', fontsize=12)
ax.set_ylabel(r'$V_{\\rm rot}$ (km/s)', fontsize=12)
ax.set_title(f'{wg["galaxy"]} — WALLABY DR2 Tier 2\\n'
             'EPS Research Corpus v7.3 | Automated Pipeline (no per-ring uncertainties)',
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

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

How many galaxies per survey? What quality tiers? This example
loads the flat CSV — the fastest way to get corpus-level statistics.

{CORPUS_NOTE}"""),
code("""import csv
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

rows = []
with open('rotation_curve_corpus_v7.1_flat.csv') as f:
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

plt.suptitle('EPS Research Unified HI Corpus v7.3 — Survey Coverage (N=438)',
             fontsize=11)
plt.tight_layout()
plt.savefig('ex05_survey_breakdown.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX06: Vrot distribution ───────────────────────────────────────────────────
notebooks["ex06_vrot_distribution.ipynb"] = nb([
    md("# SPARC Example 06: Peak Rotation Velocity Distribution\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nPeak rotation velocity Vrot_max traces total galaxy mass.\nThis stacked histogram spans the full dynamic range —\nfrom ~10 km/s dwarf irregulars to ~350 km/s massive spirals.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import csv\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nrows = []\nwith open('rotation_curve_corpus_v7.1_flat.csv') as f:\n    for r in csv.DictReader(f):\n        try:\n            rows.append({'survey': r['survey'],\n                         'vmax': float(r['vrot_max_kms']),\n                         'tier': int(r['quality_tier'])})\n        except (ValueError, KeyError):\n            pass\n\nSURVEYS = ['SPARC', 'THINGS', 'LITTLE_THINGS', 'WALLABY']\nCOLORS  = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']\nbins = np.arange(0, 380, 20)\n\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\n\n# Panel 1: stacked histogram\nax = axes[0]\ndata = [[r['vmax'] for r in rows if r['survey']==s] for s in SURVEYS]\nax.hist(data, bins=bins, stacked=True, color=COLORS,\n        label=[f'{s} (N={len(d)})' for s, d in zip(SURVEYS, data)],\n        edgecolor='white', linewidth=0.5)\nax.set_xlabel('Peak Rotation Velocity Vmax (km/s)', fontsize=12)\nax.set_ylabel('N galaxies', fontsize=12)\nax.set_title('Vmax Distribution by Survey\\nUnified HI Corpus v7.3', fontsize=11)\nax.legend(fontsize=9)\n\n# Panel 2: CDF by survey\nax2 = axes[1]\nfor s, color in zip(SURVEYS, COLORS):\n    v = sorted(r['vmax'] for r in rows if r['survey']==s)\n    if v:\n        ax2.plot(v, np.linspace(0, 1, len(v)), color=color, lw=2, label=s)\nax2.set_xlabel('Vmax (km/s)', fontsize=12)\nax2.set_ylabel('Cumulative fraction', fontsize=12)\nax2.set_title('Vmax CDF by Survey', fontsize=11)\nax2.legend(fontsize=9)\nax2.grid(alpha=0.3)\n\nplt.suptitle(f'HI Corpus v7.3 — Peak Velocity Distribution (N={len(rows)} galaxies)',\n             fontsize=11)\nplt.tight_layout()\nplt.savefig('ex06_vrot_distribution.png', dpi=150, bbox_inches='tight')\nplt.show()\n\nfor s in SURVEYS:\n    v = [r['vmax'] for r in rows if r['survey']==s]\n    if v:\n        print(f'{s:15s}: N={len(v):3d}  median={np.median(v):.1f}  '\n              f'mean={np.mean(v):.1f}  max={max(v):.1f} km/s')\n")
])

# ── EX07: Rmax vs Vmax parameter space ────────────────────────────────────────
notebooks["ex07_rmax_vmax_parameter_space.ipynb"] = nb([
    md("# SPARC Example 07: Rmax vs Vrot Parameter Space\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThe Rmax vs Vrot_max diagram shows the full dynamic range:\nfrom ~3 kpc dwarf irregulars to ~100 kpc massive spirals.\nColored by quality tier (Tier 1 = hand-curated, Tier 2 = automated).\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import csv\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nrows = []\nwith open('rotation_curve_corpus_v7.1_flat.csv') as f:\n    for r in csv.DictReader(f):\n        try:\n            rows.append({\n                'survey': r['survey'],\n                'r_max': float(r['r_max_kpc']),\n                'v_max': float(r['vrot_max_kms']),\n                'tier':  int(r['quality_tier']),\n            })\n        except (ValueError, KeyError):\n            pass\n\nSURVEYS = ['SPARC', 'THINGS', 'LITTLE_THINGS', 'WALLABY']\nCOLORS  = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']\nMARKERS = ['o', 's', '^', 'D']\n\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\n\n# Panel 1: Rmax vs Vmax coloured by survey\nax = axes[0]\nfor s, c, m in zip(SURVEYS, COLORS, MARKERS):\n    sub = [r for r in rows if r['survey']==s]\n    ax.scatter([r['r_max'] for r in sub], [r['v_max'] for r in sub],\n               s=15, alpha=0.5, color=c, marker=m, label=f'{s} (N={len(sub)})')\nax.set_xlabel('R_max (kpc)', fontsize=12)\nax.set_ylabel('Vmax (km/s)', fontsize=12)\nax.set_title('Parameter Space: R_max vs Vmax\\nAll surveys', fontsize=11)\nax.legend(fontsize=8)\n\n# Panel 2: Tier-1 only with log axes\nax2 = axes[1]\nt1 = [r for r in rows if r['tier']==1]\nfor s, c, m in zip(SURVEYS, COLORS, MARKERS):\n    sub = [r for r in t1 if r['survey']==s]\n    if sub:\n        ax2.scatter([r['r_max'] for r in sub], [r['v_max'] for r in sub],\n                    s=20, alpha=0.6, color=c, marker=m, label=s)\nax2.set_xscale('log'); ax2.set_yscale('log')\nax2.set_xlabel('R_max (kpc) [log]', fontsize=12)\nax2.set_ylabel('Vmax (km/s) [log]', fontsize=12)\nax2.set_title('Tier-1 Only — Log Scale', fontsize=11)\nax2.legend(fontsize=8)\nax2.grid(alpha=0.3, which='both')\n\nplt.suptitle('HI Corpus v7.3 — Rotation Curve Parameter Space', fontsize=11)\nplt.tight_layout()\nplt.savefig('ex07_rmax_vmax_parameter_space.png', dpi=150, bbox_inches='tight')\nplt.show()\nprint(f'Total galaxies: {len(rows)}  Tier-1: {len(t1)}')\nprint(f'R_max range: {min(r[\"r_max\"] for r in rows):.1f} — '\n      f'{max(r[\"r_max\"] for r in rows):.1f} kpc')\nprint(f'Vmax range:  {min(r[\"v_max\"] for r in rows):.1f} — '\n      f'{max(r[\"v_max\"] for r in rows):.1f} km/s')\n")
])

# ── EX08: Hubble type vs Vmax ─────────────────────────────────────────────────
notebooks["ex08_hubble_type_vmax.ipynb"] = nb([
    md("# SPARC Example 08: Hubble Type vs Peak Velocity\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nSPARC includes Hubble morphological type (0=S0 to 11=Irr/BCD).\nGalaxy morphology correlates with peak rotation velocity —\nearlier types (S0, Sa) rotate faster; late irregulars rotate slowly.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import csv\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom collections import defaultdict\n\nrows = []\nwith open('rotation_curve_corpus_v7.1_flat.csv') as f:\n    for r in csv.DictReader(f):\n        try:\n            if r['survey']=='SPARC' and r['hubble_type'] and r['vrot_max_kms']:\n                rows.append({\n                    'type': int(float(r['hubble_type'])),\n                    'vmax': float(r['vrot_max_kms']),\n                })\n        except (ValueError, KeyError):\n            pass\n\nTYPE_LABELS = {0:'S0',1:'Sa',2:'Sab',3:'Sb',4:'Sbc',\n               5:'Sc',6:'Scd',7:'Sd',8:'Sdm',9:'Sm',10:'Im'}\n\nby_type = defaultdict(list)\nfor r in rows:\n    by_type[r['type']].append(r['vmax'])\n\ntypes = sorted(by_type.keys())\nmedians = [np.median(by_type[t]) for t in types]\nq25 = [np.percentile(by_type[t], 25) for t in types]\nq75 = [np.percentile(by_type[t], 75) for t in types]\nlabels = [TYPE_LABELS.get(t, str(t)) for t in types]\ncounts = [len(by_type[t]) for t in types]\n\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\n\n# Panel 1: Median Vmax by Hubble type\nax = axes[0]\nx = np.arange(len(types))\nax.bar(x, medians, color='#1f77b4', alpha=0.8, edgecolor='white')\nax.errorbar(x, medians,\n            yerr=[np.array(medians)-np.array(q25),\n                  np.array(q75)-np.array(medians)],\n            fmt='none', color='black', capsize=4)\nax.set_xticks(x)\nax.set_xticklabels([f'{l}\\n(N={c})' for l,c in zip(labels,counts)], fontsize=9)\nax.set_ylabel('Median Vmax (km/s)', fontsize=12)\nax.set_title('Vmax by Hubble Type\\nSPARC sample (median ± IQR)', fontsize=11)\n\n# Panel 2: Boxplot\nax2 = axes[1]\nax2.boxplot([by_type[t] for t in types], **{('tick_labels' if tuple(int(x) for x in matplotlib.__version__.split('.')[:2]) >= (3, 9) else 'labels'): labels},\n            patch_artist=True,\n            boxprops=dict(facecolor='#aec7e8', alpha=0.7))\nax2.set_xlabel('Hubble Type', fontsize=12)\nax2.set_ylabel('Vmax (km/s)', fontsize=12)\nax2.set_title('Vmax Distribution by Hubble Type', fontsize=11)\n\nplt.suptitle('HI Corpus v7.3 — Morphology vs Kinematics (SPARC)', fontsize=11)\nplt.tight_layout()\nplt.savefig('ex08_hubble_type_vmax.png', dpi=150, bbox_inches='tight')\nplt.show()\nfor t, l, m, c in zip(types, labels, medians, counts):\n    print(f'{l:5s} (N={c:3d}): median Vmax = {m:.1f} km/s')\n")
])

# ── EX09: Multi-galaxy comparison ─────────────────────────────────────────────
notebooks["ex09_multi_galaxy_comparison.ipynb"] = nb([
    md("# SPARC Example 09: Multi-Galaxy Rotation Curve Comparison\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nCompare rotation curves across the full SPARC mass range:\n- DDO161: dwarf irregular, Vmax~67 km/s\n- NGC2403: intermediate spiral, Vmax~130 km/s  \n- UGC2885: massive spiral (one of the largest known), Vmax~300 km/s\n\nAll three loaded from a single JSON file in under 15 lines of Python.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\ntargets = ['DDO161', 'NGC2403', 'UGC2885']\ncolors  = ['#2166ac', '#4dac26', '#d6604d']\n\nfig, axes = plt.subplots(1, 3, figsize=(14, 5))\n\nfor ax, name, color in zip(axes, targets, colors):\n    try:\n        g = next(g for g in corpus['galaxies'] if g['galaxy'] == name)\n        d = g['data']\n        R    = [p['Rad']  for p in d]\n        Vobs = [p['Vobs'] for p in d]\n        ax.plot(R, Vobs, 'o-', color=color, ms=5, lw=1.5,\n                label=f'{name}')\n        ax.set_xlabel('Radius (kpc)', fontsize=11)\n        ax.set_ylabel('Vrot (km/s)', fontsize=11)\n        ax.set_title(f'{name}\\nD={g.get(\"distance_mpc\",\"?\"):.1f} Mpc  '\n                     f'Survey={g.get(\"survey\",\"?\")}', fontsize=10)\n        ax.legend(fontsize=9)\n        ax.grid(alpha=0.3)\n        # Omega annotation\n        if len(d) >= 2:\n            R1,V1 = R[0], Vobs[0]\n            R2,V2 = R[-1], Vobs[-1]\n            if R1>0 and R2>0:\n                outer_term    = (V2 / R2)\n                inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n                omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n                omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n                om = omega_rad_gyr\n                ax.annotate(f'ω={om:+.2f} rad/Gyr',\n                            xy=(0.05,0.92), xycoords='axes fraction',\n                            fontsize=9, color=color)\n    except StopIteration:\n        ax.text(0.5, 0.5, f'{name}\\nnot found',\n                ha='center', va='center', transform=ax.transAxes)\n\nplt.suptitle('HI Corpus v7.3 — Multi-Galaxy Rotation Curve Comparison\\n'\n             'Flynn & Cannaliato (2025) Eq.6 omega annotation', fontsize=11)\nplt.tight_layout()\nplt.savefig('ex09_multi_galaxy_comparison.png', dpi=150, bbox_inches='tight')\nplt.show()\nprint('Displayed:', targets)\n")
])

# ── EX10: Omega across SPARC ──────────────────────────────────────────────────
notebooks["ex10_omega_84_sparc.ipynb"] = nb([
    md("# SPARC Example 10: Omega Across the SPARC Sample\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThis example computes omega for all SPARC galaxies with sufficient data\nas an exploratory current-corpus calculation.\nIt is not a reproduction of the frozen 84-galaxy benchmark.\n\n**Reference:** Flynn, D.C. & Cannaliato, J. (2025).\nDOI: 10.3389/fspas.2025.1680387\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\nresults = []\nfor g in corpus['galaxies']:\n    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:\n        continue\n    d  = g['data']\n    R  = [p['Rad']  for p in d]\n    V  = [p['Vobs'] for p in d]\n    R1, V1 = R[0],  V[0]\n    R2, V2 = R[-1], V[-1]\n    if R1 <= 0 or R2 <= 0 or V1 <= 0 or V2 <= 0:\n        continue\n    outer_term    = (V2 / R2)\n    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n    omega = omega_rad_gyr  # Eq.6 corrected 2026-07-12: operator-precedence fix\n    results.append({'galaxy': g['galaxy'], 'omega': omega,\n                    'vmax': max(V), 'distance': g['distance_mpc']})\n\nomegas = [r['omega'] for r in results]\nprint(f\"Galaxies computed:  {len(results)}\")\nprint(f\"Mean omega:         {np.mean(omegas):.2f} rad/Gyr\")\nprint(f\"Std omega:          {np.std(omegas):.2f} rad/Gyr\")\nprint(f\"Median omega:       {np.median(omegas):.2f} rad/Gyr\")\nprint(f\"\\nPublished result (Flynn & Cannaliato 2025): 7.06 ± 3.26 rad/Gyr\")"),
    code("fig, axes = plt.subplots(1, 2, figsize=(11, 4))\n\naxes[0].hist(omegas, bins=30, color='#2166ac', alpha=0.8, edgecolor='white')\naxes[0].axvline(np.mean(omegas), color='red', linestyle='--', linewidth=1.5,\n                label=f'Mean = {np.mean(omegas):.2f} rad/Gyr')\n# Frozen-benchmark reference line intentionally omitted.\naxes[0].set_xlabel(r'$\\omega$ (rad/Gyr)', fontsize=11)\naxes[0].set_ylabel('N galaxies', fontsize=11)\naxes[0].set_title('Omega Distribution — SPARC Sample', fontsize=10)\naxes[0].legend(fontsize=8)\n\naxes[1].scatter([r['vmax'] for r in results], omegas,\n                s=20, alpha=0.6, color='#2166ac')\naxes[1].axhline(np.mean(omegas), color='red', linestyle='--', linewidth=1,\n                label=f'Mean = {np.mean(omegas):.2f}')\naxes[1].set_xlabel(r'$V_{\\rm max}$ (km/s)', fontsize=11)\naxes[1].set_ylabel(r'$\\omega$ (rad/Gyr)', fontsize=11)\naxes[1].set_title(r'$\\omega$ vs Peak Velocity', fontsize=10)\naxes[1].legend(fontsize=8)\n\nplt.suptitle('Omega Kinematic Correction — EPS Research SPARC Sample\\n'\n             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387',\n             fontsize=10)\nplt.tight_layout()\nplt.savefig('ex10_omega_sparc.png', dpi=150, bbox_inches='tight')\nplt.show()")
])

# ── EX11: THINGS vs SPARC overlap ─────────────────────────────────────────────
notebooks["ex11_things_vs_sparc.ipynb"] = nb([
md(f"""# SPARC Example 11: THINGS vs SPARC Cross-Survey Comparison

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

14 galaxies appear in both THINGS and SPARC.
THINGS provides high-resolution VLA tilted-ring fits;
SPARC provides full baryonic decomposition at Spitzer 3.6μm.
The corpus crossmatch index enables direct comparison.

{CORPUS_NOTE}"""),
code("""import csv
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7.1_flat.csv') as f:
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
             'EPS Research Corpus v7.3', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex11_things_vs_sparc.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX12: LITTLE THINGS dwarfs ────────────────────────────────────────────────
notebooks["ex12_little_things_dwarfs.ipynb"] = nb([
md(f"""# SPARC Example 12: LITTLE THINGS Dwarf Irregulars

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

LITTLE THINGS (Local Irregulars That Trace Luminosity Extremes)
provides 26 dwarf irregular galaxies with high-resolution VLA data.
These are the smallest, darkest-matter-dominated galaxies in the corpus.

{CORPUS_NOTE}"""),
code("""import csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
with open('rotation_curve_corpus_v7.1_flat.csv') as f:
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
             'EPS Research Unified HI Corpus v7.3', fontsize=11)
plt.tight_layout()
plt.savefig('ex12_little_things.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX13: Mass discrepancy ────────────────────────────────────────────────────
notebooks["ex13_mass_discrepancy.ipynb"] = nb([
md(f"""# SPARC Example 13: The Mass Discrepancy at R_max

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

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
    Vbar_sq = abs(Vgas)*Vgas + Vdisk**2 + Vbul**2
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
             'EPS Research Corpus v7.3', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex13_mass_discrepancy.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX14: Outer gap all SPARC ─────────────────────────────────────────────────
notebooks["ex14_outer_gap_distribution.ipynb"] = nb([
    md("# SPARC Example 14: Outer Gap Distribution — All SPARC Galaxies\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThe outer gap is V_adj(R2) - V_bary(R2) — the residual between the\nomega-corrected velocity and baryonic velocity at the outermost ring.\nThis notebook evaluates the outer-gap diagnostic across the SPARC sample in\nUnified HI Corpus v7.3. The sign is a boundary-consistency diagnostic only;\nit does not by itself rule out a mass component.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\nresults = []\nfor g in corpus['galaxies']:\n    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:\n        continue\n    d  = g['data']\n    R  = [p['Rad']  for p in d]\n    V  = [p['Vobs'] for p in d]\n    R1, V1 = R[0],  V[0]\n    R2, V2 = R[-1], V[-1]\n    if R1<=0 or R2<=0 or V1<=0 or V2<=0:\n        continue\n    outer_term    = (V2 / R2)\n    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n    omega = omega_rad_gyr  # Eq.6 corrected 2026-07-12: operator-precedence fix\n    V_adj = V2 - R2 * omega_kms_kpc\n    last  = d[-1]\n    Vgas  = last.get('Vgas', 0)\n    Vdisk = last.get('Vdisk', 0)\n    Vbul  = last.get('Vbul', 0)\n    Vbar_sq = abs(Vgas)*Vgas + Vdisk**2 + Vbul**2\n    if Vbar_sq <= 0:\n        continue\n    Vbar = np.sqrt(Vbar_sq)\n    gap  = V_adj - Vbar\n    results.append({'galaxy': g['galaxy'], 'gap': gap,\n                    'omega': omega, 'Vbar': Vbar})\n\ngaps = [r['gap'] for r in results]\nprint(f\"Galaxies with outer gap: {len(gaps)}\")\nprint(f\"All negative: {all(g < 0 for g in gaps)}\")\nprint(f\"Mean gap: {np.mean(gaps):.1f} km/s\")\nprint(f\"Std gap:  {np.std(gaps):.1f} km/s\")\nprint(f\"\\nPublished (Flynn 2026): mean = -51.4 ± 25.0 km/s, all 84 negative\")"),
    code("fig, ax = plt.subplots(figsize=(8, 5))\nax.hist(gaps, bins=25, color='#2166ac', alpha=0.8, edgecolor='white')\nax.axvline(0, color='red', linestyle='--', linewidth=1.5,\n           label='Gap = 0 boundary')\nax.axvline(np.mean(gaps), color='orange', linestyle='-', linewidth=1.5,\n           label=f'Mean = {np.mean(gaps):.1f} km/s')\nax.set_xlabel(r'$V_{\\rm adj}(R_2) - V_{\\rm bar}(R_2)$ (km/s)', fontsize=11)\nax.set_ylabel('N galaxies', fontsize=11)\nax.set_title('Outer Gap Distribution — SPARC\\n'\n             'All negative: V_adj < V_bar at outermost ring (Flynn 2026)',\n             fontsize=10)\nax.legend(fontsize=9)\nplt.tight_layout()\nplt.savefig('ex14_outer_gap.png', dpi=150, bbox_inches='tight')\nplt.show()")
])

# ── EX15: Log slope ───────────────────────────────────────────────────────────
notebooks["ex15_log_slope_diagnostic.ipynb"] = nb([
md(f"""# SPARC Example 15: Log-Slope Diagnostic

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

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

plt.suptitle('Log-Slope Diagnostic — DDO161\\nEPS Research Corpus v7.3', fontsize=11)
plt.tight_layout()
plt.savefig('ex15_log_slope.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX16: Enclosed mass profile ───────────────────────────────────────────────
notebooks["ex16_enclosed_mass.ipynb"] = nb([
    md("# SPARC Example 16: Enclosed Mass Profile M(<R)\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nFrom the rotation curve we can compute the enclosed mass:\n\n    M(<R) = V_obs^2 * R / G\n\nwhere G = 4.301e-3 pc Msun^-1 (km/s)^2.\nThis gives total mass (baryons + dark matter) as a function of radius.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\n# G in kpc (km/s)^2 Msun^-1\nG_kpc = 4.301e-3 * 1e-3\n\ntargets = ['DDO161', 'NGC2403', 'UGC2885']\ncolors  = ['#2166ac', '#4dac26', '#d6604d']\n\nfig, axes = plt.subplots(1, 2, figsize=(12, 5))\n\n# Panel 1: Enclosed mass profiles\nax = axes[0]\nfor name, color in zip(targets, colors):\n    try:\n        g = next(g for g in corpus['galaxies'] if g['galaxy'] == name)\n        d = g['data']\n        R    = np.array([p['Rad']  for p in d])\n        Vobs = np.array([p['Vobs'] for p in d])\n        M_enc = Vobs**2 * R / G_kpc  # solar masses\n        ax.plot(R, np.log10(M_enc), 'o-', color=color,\n                ms=5, lw=1.5, label=name)\n    except StopIteration:\n        pass\n\nax.set_xlabel('Radius (kpc)', fontsize=12)\nax.set_ylabel(r'log $M_{enc}$ ($M_\\odot$)', fontsize=12)\nax.set_title('Enclosed Mass Profiles\\nM(R) = V²R/G', fontsize=11)\nax.legend(fontsize=9)\nax.grid(alpha=0.3)\n\n# Panel 2: Normalized profiles\nax2 = axes[1]\nfor name, color in zip(targets, colors):\n    try:\n        g = next(g for g in corpus['galaxies'] if g['galaxy'] == name)\n        d = g['data']\n        R    = np.array([p['Rad']  for p in d])\n        Vobs = np.array([p['Vobs'] for p in d])\n        M_enc = Vobs**2 * R / G_kpc\n        ax2.plot(R/R[-1], M_enc/M_enc[-1], 'o-', color=color,\n                 ms=5, lw=1.5, label=name)\n    except StopIteration:\n        pass\n\nax2.set_xlabel(r'R / R$_{max}$', fontsize=12)\nax2.set_ylabel(r'M$_{enc}$ / M$_{enc,max}$', fontsize=12)\nax2.set_title('Normalized Enclosed Mass\\n(concentration comparison)', fontsize=11)\nax2.legend(fontsize=9)\nax2.grid(alpha=0.3)\n\nplt.suptitle('HI Corpus v7.3 — Enclosed Mass Profiles', fontsize=11)\nplt.tight_layout()\nplt.savefig('ex16_enclosed_mass.png', dpi=150, bbox_inches='tight')\nplt.show()\n")
])

# ── EX17: RMSE improvement over 84 galaxies ───────────────────────────────────
notebooks["ex17_rmse_improvement.ipynb"] = nb([
md(f"""# SPARC Example 17: RMSE Improvement — Reproducing Flynn (2026)

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

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
    outer_term    = (V2 / R2)
    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)
    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]
    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr
    omega = omega_rad_gyr  # reporting/storage only — use omega_kms_kpc for velocity arithmetic
    V_adj = V - R * omega_kms_kpc
    # Keplerian
    GM       = V2**2 * R2
    V_kepler = np.sqrt(GM / R)
    # Baryonic
    Vgas  = np.array([p.get('Vgas', 0)  for p in d])
    Vdisk = np.array([p.get('Vdisk', 0) for p in d])
    Vbul  = np.array([p.get('Vbul', 0)  for p in d])
    Vbar  = vbar_eq1(Vgas, Vdisk, Vbul)
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
    md("# SPARC Example 18: Omega vs Galaxy Size\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nDoes omega correlate with galaxy size (R_max)?\nThis tests whether omega is a geometric artifact of the\nboundary point selection or a genuine kinematic property.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\nresults = []\nfor g in corpus['galaxies']:\n    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:\n        continue\n    d  = g['data']\n    R  = [p['Rad']  for p in d]\n    V  = [p['Vobs'] for p in d]\n    R1, V1 = R[0],  V[0]\n    R2, V2 = R[-1], V[-1]\n    if R1<=0 or R2<=0 or V1<=0 or V2<=0:\n        continue\n    outer_term    = (V2 / R2)\n    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n    omega = omega_rad_gyr  # Eq.6 corrected 2026-07-12: operator-precedence fix\n    results.append({'galaxy': g['galaxy'], 'omega': omega,\n                    'R_max': R2, 'V_max': max(V)})\n\nR_max  = [r['R_max']  for r in results]\nomegas = [r['omega']  for r in results]\ncorr   = np.corrcoef(R_max, omegas)[0, 1]\nprint(f\"N galaxies: {len(results)}\")\nprint(f\"Pearson r (omega vs R_max): {corr:.3f}\")\nprint(f\"Interpretation: {'weak' if abs(corr)<0.3 else 'moderate' if abs(corr)<0.6 else 'strong'} correlation\")"),
    code("fig, axes = plt.subplots(1, 2, figsize=(11, 4))\n\naxes[0].scatter(R_max, omegas, s=18, alpha=0.6, color='#2166ac')\naxes[0].set_xlabel(r'$R_{\\rm max}$ (kpc)', fontsize=11)\naxes[0].set_ylabel(r'$\\omega$ (rad/Gyr)', fontsize=11)\naxes[0].set_title(f'Omega vs R_max (r={corr:.2f})', fontsize=10)\n\nV_max  = [r['V_max']  for r in results]\ncorr2  = np.corrcoef(V_max, omegas)[0, 1]\naxes[1].scatter(V_max, omegas, s=18, alpha=0.6, color='#d62728')\naxes[1].set_xlabel(r'$V_{\\rm max}$ (km/s)', fontsize=11)\naxes[1].set_ylabel(r'$\\omega$ (rad/Gyr)', fontsize=11)\naxes[1].set_title(f'Omega vs V_max (r={corr2:.2f})', fontsize=10)\n\nplt.suptitle('Omega Correlations — EPS Research SPARC Sample\\n'\n             'Testing whether omega is a geometric artifact', fontsize=10)\nplt.tight_layout()\nplt.savefig('ex18_omega_correlations.png', dpi=150, bbox_inches='tight')\nplt.show()")
])

# ── EX19: Baryonic Tully-Fisher ───────────────────────────────────────────────
notebooks["ex19_baryonic_tully_fisher.ipynb"] = nb([
    md("# Example 19: Baryonic Tully–Fisher Relation (Four Surveys)\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThe Baryonic Tully–Fisher Relation (BTFR) is a tight empirical scaling law\nrelating a galaxy's total baryonic mass to its asymptotic rotation velocity:\n\n$$M_{\\\\rm bar} \\\\propto V_{\\\\rm flat}^4$$\n\nThis notebook demonstrates BTFR retrieval across all four surveys in the\nunified corpus: **SPARC**, **THINGS**, **LITTLE THINGS**, and **WALLABY DR2**.\n\n**Mass estimation:**\n- **SPARC:** $M_{\\\\rm bar}$ computed from the rotation-curve decomposition at the\n  outermost measured ring: $M_{\\\\rm gas} = 1.33\\\\,V_{\\\\rm gas}^2 R/G$ (HI + He correction),\n  $M_{\\\\rm star} = \\\\Upsilon_{\\\\rm disk}\\\\,V_{\\\\rm disk}^2 R/G$, $M_{\\\\rm bul} = V_{\\\\rm bul}^2 R/G$.\n- **THINGS / LITTLE THINGS / WALLABY:** $V_{\\\\rm flat}$ from `vrot_max_kms`;\n  $M_{\\\\rm bar}$ estimated via the McGaugh (2012) BTFR calibration\n  ($\\\\log M_{\\\\rm bar} = 4\\\\log V_{\\\\rm flat} + \\\\log 47$) as a cross-survey consistency check.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv`\nand `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer.\nThe CSV contains every kinematic parameter published by Lelli et al. (2016)\nincluding per-galaxy inclination, distance uncertainties, mass-to-light ratios,\nand rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas,\nVdisk, Vbul, errV at every radial point.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**References:** McGaugh et al. (2000), ApJ 533, L99; McGaugh (2012), AJ 143, 40;\nLelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, json (standard library only)"),
    code("import json\nimport numpy as np\n\n# ── Load corpus ────────────────────────────────────────────────\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\ngalaxies = corpus['galaxies']\nprint(f\"Total galaxies in corpus: {len(galaxies)}\")\n\n# ── Constants ──────────────────────────────────────────────────\n# G in units: kpc (km/s)^2 Msun^-1\nG_KPC = 4.302e-6\n\n# ── SPARC: compute M_bar from rotation-curve decomposition ─────\ndef sparc_mbar(g):\n    \"\"\"\n    Estimate M_bar and V_flat from the outermost rotation-curve ring.\n    Returns (log10(M_bar/Msun), V_flat [km/s]) or (None, None).\n    \"\"\"\n    m2l = g.get('m2l_disk')\n    if not m2l or not g.get('data'):\n        return None, None\n    m2l = float(m2l)\n    ring = g['data'][-1]          # outermost ring\n    R    = ring.get('Rad')\n    Vgas = ring.get('Vgas', 0)\n    Vdisk = ring.get('Vdisk', 0)\n    Vbul  = ring.get('Vbul',  0)\n    Vobs  = ring.get('Vobs')\n    if not R or not Vobs:\n        return None, None\n    R, Vgas, Vdisk, Vbul, Vobs = (\n        float(R), float(Vgas), float(Vdisk), float(Vbul), float(Vobs))\n    Mgas  = max(Vgas,  0)**2 * R / G_KPC   # HI + He\n    Mstar = m2l  * Vdisk**2          * R / G_KPC   # stellar disk\n    Mbul  =        Vbul**2           * R / G_KPC   # bulge\n    Mbar  = Mgas + Mstar + Mbul\n    if Mbar <= 0:\n        return None, None\n    return np.log10(Mbar), Vobs\n\ndef get_vmax(g):\n    \"\"\"Return V_flat from summary field or max(Vrot) over rings.\"\"\"\n    v = g.get('vrot_max_kms') or g.get('Vobs_max_kms')\n    if v:\n        try: return float(v)\n        except: pass\n    if g.get('data'):\n        vcol = 'Vrot' if 'Vrot' in (g.get('columns') or {}) else 'Vobs'\n        vals = [float(r[vcol]) for r in g['data'] if r.get(vcol)]\n        if vals:\n            return max(vals)\n    return None\n\n# ── Collect per-survey data points ────────────────────────────\nresults = {s: [] for s in ('SPARC', 'THINGS', 'LITTLE_THINGS', 'WALLABY')}\n\nfor g in galaxies:\n    survey = g.get('survey')\n    if survey not in results:\n        continue\n    if survey == 'SPARC':\n        logM, V = sparc_mbar(g)\n        if logM is not None and V > 0:\n            results['SPARC'].append((V, logM))\n    else:\n        vmax = get_vmax(g)\n        if not vmax or vmax <= 0:\n            continue\n        # McGaugh (2012) calibration: log M_bar = 4 log V + log(47)\n        logM = 4.0 * np.log10(vmax) + np.log10(47.0)\n        results[survey].append((vmax, logM))\n\nfor survey, pts in results.items():\n    print(f\"  {survey:<15}: {len(pts):>3} galaxies\")"),
    code("import matplotlib.pyplot as plt\n\n# ── Style ──────────────────────────────────────────────────────\nCOLORS  = {'SPARC':'#1f77b4', 'THINGS':'#ff7f0e',\n           'LITTLE_THINGS':'#2ca02c', 'WALLABY':'#d62728'}\nMARKERS = {'SPARC':'o', 'THINGS':'s', 'LITTLE_THINGS':'^', 'WALLABY':'D'}\nLABELS  = {\n    'SPARC':         'SPARC — $M_{\\\\rm bar}$ from decomposition',\n    'THINGS':        'THINGS — $V^4$ proxy',\n    'LITTLE_THINGS': 'LITTLE THINGS — $V^4$ proxy',\n    'WALLABY':       'WALLABY DR2 — $V^4$ proxy',\n}\n\nfig, ax = plt.subplots(figsize=(8, 6))\n\nfor survey in ('SPARC', 'THINGS', 'LITTLE_THINGS', 'WALLABY'):\n    pts = results[survey]\n    if not pts:\n        continue\n    vs, ms = zip(*pts)\n    label = f\"{LABELS[survey]} (n={len(pts)})\"\n    ax.scatter(np.log10(vs), ms,\n               s=25, alpha=0.7, edgecolors='none',\n               color=COLORS[survey], marker=MARKERS[survey],\n               label=label)\n\n# McGaugh (2012) reference BTFR\nv_ref = np.logspace(0.8, 2.7, 200)\nax.plot(np.log10(v_ref), 4*np.log10(v_ref) + np.log10(47),\n        'k--', lw=1.2, alpha=0.55, label='McGaugh (2012) calibration')\n\nax.set_xlabel(r'$\\log_{10}\\,V_{\\rm flat}$ (km s$^{-1}$)', fontsize=13)\nax.set_ylabel(r'$\\log_{10}\\,M_{\\rm bar}$ ($M_\\odot$)',    fontsize=13)\nax.set_title(\n    'Baryonic Tully–Fisher Relation\\n'\n    'Unified HI Corpus v7.3 — SPARC · THINGS · LITTLE THINGS · WALLABY DR2',\n    fontsize=11)\nax.legend(fontsize=9, framealpha=0.9)\nax.set_xlim(0.9, 2.8)\nax.set_ylim(6.5, 12.5)\nax.grid(True, alpha=0.2)\n\nplt.tight_layout()\nplt.savefig('ex19_btfr_four_surveys.png', dpi=150, bbox_inches='tight')\nplt.show()\nprint(\"Saved: ex19_btfr_four_surveys.png\")")
])

# ── EX20: SPARC galaxy gallery ────────────────────────────────────────────────
notebooks["ex20_rotation_curve_gallery.ipynb"] = nb([
    md("# SPARC Example 20: Rotation Curve Gallery\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nA gallery of 12 SPARC rotation curves illustrating the full diversity\nof shapes found across galaxy types — from rising solid-body curves\nin dwarfs to declining Keplerian-like profiles in massive spirals.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\nsparc = [g for g in corpus['galaxies']\n         if g.get('survey')=='SPARC' and g.get('data') and len(g['data'])>=5]\nsparc_sorted = sorted(sparc, key=lambda x: max(p['Vobs'] for p in x['data']))\nn = len(sparc_sorted)\nindices = [int(i*n/12) for i in range(12)]\nselected = [sparc_sorted[i] for i in indices]\n\nfig, axes = plt.subplots(3, 4, figsize=(14, 10))\naxes = axes.flatten()\n\nfor ax, g in zip(axes, selected):\n    d = g['data']\n    R    = [p['Rad']  for p in d]\n    Vobs = [p['Vobs'] for p in d]\n    vmax = max(Vobs)\n    # color by Vmax\n    c = plt.cm.plasma(vmax / 300)\n    ax.plot(R, Vobs, 'o-', color=c, ms=3, lw=1.2)\n    ax.set_title(f\"{g['galaxy']}\\nVmax={vmax:.0f} km/s\", fontsize=8)\n    ax.set_xlabel('R (kpc)', fontsize=7)\n    ax.set_ylabel('Vrot (km/s)', fontsize=7)\n    ax.tick_params(labelsize=7)\n    ax.grid(alpha=0.3)\n\nplt.suptitle('HI Corpus v7.3 — SPARC Rotation Curve Gallery\\n'\n             '12 galaxies spanning the full Vmax range', fontsize=12)\nplt.tight_layout()\nplt.savefig('ex20_rotation_curve_gallery.png', dpi=150, bbox_inches='tight')\nplt.show()\nprint('Gallery galaxies:')\nfor g in selected:\n    vmax = max(p['Vobs'] for p in g['data'])\n    print(f\"  {g['galaxy']:<15} Vmax={vmax:.1f} km/s  N_rings={len(g['data'])}\")\n")
])

# ── EX21: SPARC query by property ─────────────────────────────────────────────
notebooks["ex21_query_by_property.ipynb"] = nb([
    md("# SPARC Example 21: Querying the Corpus by Property\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThe flat CSV enables fast filtering by any galaxy property.\nThis example demonstrates practical query patterns researchers use:\n- Find the largest galaxies\n- Find galaxies with strong gas content\n- Find galaxies with many data points (best-sampled RCs)\n- Find galaxies by Hubble type\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import csv\nimport numpy as np\n\nrows = []\nwith open('rotation_curve_corpus_v7.1_flat.csv') as f:\n    for r in csv.DictReader(f):\n        rows.append(r)\n\ndef fv(r, k):\n    try: return float(r[k])\n    except: return None\n\n# Query 1: Top 5 largest SPARC galaxies by R_max\nsparc = [r for r in rows if r['survey']=='SPARC' and fv(r,'r_max_kpc')]\nlargest = sorted(sparc, key=lambda x: fv(x,'r_max_kpc'), reverse=True)[:5]\nprint('Top 5 largest SPARC galaxies by R_max:')\nfor r in largest:\n    print(f\"  {r['galaxy']:<15} R_max={fv(r,'r_max_kpc'):.1f} kpc  \"\n          f\"Vmax={fv(r,'vrot_max_kms'):.1f} km/s\")\n\n# Query 2: Fastest rotators\nfastest = sorted(sparc, key=lambda x: fv(x,'vrot_max_kms') or 0, reverse=True)[:5]\nprint('\\nTop 5 fastest SPARC rotators:')\nfor r in fastest:\n    print(f\"  {r['galaxy']:<15} Vmax={fv(r,'vrot_max_kms'):.1f} km/s  \"\n          f\"R_max={fv(r,'r_max_kpc'):.1f} kpc\")\n\n# Query 3: Slowest rotators (dwarfs)\nslowest = sorted([r for r in sparc if fv(r,'vrot_max_kms') and fv(r,'vrot_max_kms')>0],\n                  key=lambda x: fv(x,'vrot_max_kms'))[:5]\nprint('\\nTop 5 slowest SPARC rotators (dwarfs):')\nfor r in slowest:\n    print(f\"  {r['galaxy']:<15} Vmax={fv(r,'vrot_max_kms'):.1f} km/s  \"\n          f\"R_max={fv(r,'r_max_kpc'):.1f} kpc\")\n\n# Query 4: WALLABY Tier-2 galaxies with Vmax > 200\nwallaby_fast = [r for r in rows\n                if r['survey']=='WALLABY'\n                and r['quality_tier']=='2'\n                and fv(r,'vrot_max_kms') and fv(r,'vrot_max_kms') > 200]\nprint(f'\\nWALLABY Tier-2 galaxies with Vmax > 200 km/s: {len(wallaby_fast)}')\n\n# Summary stats\nprint('\\n--- Corpus summary ---')\nfor survey in ['SPARC','THINGS','LITTLE_THINGS','WALLABY']:\n    sub = [r for r in rows if r['survey']==survey]\n    vmaxs = [fv(r,'vrot_max_kms') for r in sub if fv(r,'vrot_max_kms')]\n    print(f'{survey:15s}: N={len(sub):4d}  '\n          f'median Vmax={np.median(vmaxs):.1f} km/s' if vmaxs else f'{survey}: N={len(sub)}')\n")
])

# ── EX22: Distance uncertainty effects ────────────────────────────────────────
notebooks["ex22_distance_uncertainty.ipynb"] = nb([
    md("# SPARC Example 22: Distance Uncertainty and Its Effect on Omega\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nSPARC distance uncertainties (e_distance_mpc) are published by Lelli et al. (2016).\nSince R_kpc = R_arcsec * D_Mpc, distance uncertainty propagates into\nthe radius scale and therefore omega.\n\nThis example quantifies how much omega changes with ±1σ distance.\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\ng   = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')\nd   = g['data']\nD   = g.get('distance_mpc', 3.4)\ne_D = g.get('e_distance_mpc', D * 0.1)\n\nR    = np.array([p['Rad']  for p in d])\nVobs = np.array([p['Vobs'] for p in d])\n\ndef compute_omega(R, Vobs):\n    R1, V1 = R[0],  Vobs[0]\n    R2, V2 = R[-1], Vobs[-1]\n    if R1 <= 0 or R2 <= 0:\n        return None\n    outer_term    = (V2 / R2)\n    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n    omega_kms_kpc = outer_term - inner_term\n    omega_rad_gyr = omega_kms_kpc * 1.0227\n    return omega_rad_gyr\n\nomega_central = compute_omega(R, Vobs)\n\n# Monte Carlo distance uncertainty\nn_mc = 5000\nnp.random.seed(42)\nD_samples = np.random.normal(D, e_D, n_mc)\nomega_samples = []\nfor D_s in D_samples:\n    scale = D_s / D\n    R_s = R * scale\n    omega_s = compute_omega(R_s, Vobs)\n    if omega_s is not None:\n        omega_samples.append(omega_s)\n\nomega_samples = np.array(omega_samples)\nomega_std = np.std(omega_samples)\n\nfig, axes = plt.subplots(1, 2, figsize=(11, 5))\n\n# Panel 1: Monte Carlo omega distribution\nax = axes[0]\nax.hist(omega_samples, bins=40, color='#1f77b4', alpha=0.8, edgecolor='white')\nax.axvline(omega_central, color='red', lw=2, ls='--',\n           label=f'Central: {omega_central:.3f} rad/Gyr')\nax.axvline(omega_central - omega_std, color='orange', lw=1.5, ls=':')\nax.axvline(omega_central + omega_std, color='orange', lw=1.5, ls=':',\n           label=f'±1σ: {omega_std:.3f} rad/Gyr')\nax.set_xlabel('ω (rad/Gyr)', fontsize=12)\nax.set_ylabel('N MC samples', fontsize=12)\nax.set_title(f'DDO161 Omega — Distance Uncertainty\\n'\n             f'D = {D:.2f} ± {e_D:.2f} Mpc  (N={n_mc} MC)', fontsize=11)\nax.legend(fontsize=9)\n\n# Panel 2: Omega vs distance scaling\nax2 = axes[1]\nD_range = np.linspace(D - 3*e_D, D + 3*e_D, 100)\nomega_range = [compute_omega(R * d/D, Vobs) for d in D_range]\nax2.plot(D_range, omega_range, 'b-', lw=2)\nax2.axvline(D, color='black', lw=1, ls='--', alpha=0.5, label=f'D={D:.2f} Mpc')\nax2.axhspan(omega_central - omega_std, omega_central + omega_std,\n            alpha=0.2, color='orange', label='±1σ range')\nax2.set_xlabel('Distance (Mpc)', fontsize=12)\nax2.set_ylabel('ω (rad/Gyr)', fontsize=12)\nax2.set_title('Omega Sensitivity to Distance\\nDDO161', fontsize=11)\nax2.legend(fontsize=9)\nax2.grid(alpha=0.3)\n\nplt.suptitle('HI Corpus v7.3 — Distance Uncertainty Analysis\\n'\n             'Canonical Eq.6: ω = V₂/R₂ − (V₁/R₁)(R₁/R₂)^1.5', fontsize=11)\nplt.tight_layout()\nplt.savefig('ex22_distance_uncertainty.png', dpi=150, bbox_inches='tight')\nplt.show()\n\nprint(f'DDO161 omega:  {omega_central:+.4f} rad/Gyr')\nprint(f'Distance uncertainty: ±{e_D:.2f} Mpc ({100*e_D/D:.0f}%)')\nprint(f'Omega uncertainty:    ±{omega_std:.4f} rad/Gyr ({100*omega_std/abs(omega_central):.1f}%)')\n")
])

# ── EX23: Cross-survey schema demo ────────────────────────────────────────────
notebooks["ex23_cross_survey_schema.ipynb"] = nb([
md(f"""# SPARC Example 23: Cross-Survey Schema Navigation

**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**

The corpus combines four surveys with different schemas.
This example demonstrates the correct way to access per-ring data
regardless of survey — a common source of bugs in cross-survey code.

Key pattern:
```python
points = g.get('data') or g.get('data', [])
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
                         if g['survey']=='WALLABY' and g.get('data')),
}

print(f"{'Survey':<15} {'Galaxy':<20} {'Data key':<20} {'R field':<12} {'V field'}")
print('-' * 80)
for survey, name in examples.items():
    g = next(g for g in corpus['galaxies'] if g['galaxy']==name)
    if g.get('data'):
        key = 'data'
        r_field = list(g['data'][0].keys())[0] if g['data'] else '?'
        v_field = 'Vobs' if 'Vobs' in g['data'][0] else 'Vrot'
    elif g.get('data'):
        key = 'data'
        r_field = 'Rad'
        v_field = 'Vrot'
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
    elif g.get('data'):
        rc = g['data']
        R  = [p['Rad']  for p in rc]
        V  = [p['Vrot'] for p in rc]
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
             'EPS Research Corpus v7.3', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('ex23_cross_survey.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── EX24: SPARC RAG single-galaxy report ──────────────────────────────────────
notebooks["ex24_single_galaxy_report.ipynb"] = nb([
    md("# SPARC Example 24: Single Galaxy Full Report\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nA complete kinematic report for a single SPARC galaxy:\nall metadata, rotation curve, baryonic decomposition, omega correction,\nand RMSE diagnostics — from a single JSON load.\n\nThis is the kind of output a RAG system would generate\nin response to: \"Give me a full kinematic analysis of NGC 2403.\"\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport matplotlib.gridspec as gridspec\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\nGALAXY = 'NGC2403'  # Change to any SPARC galaxy\ng = next(g for g in corpus['galaxies'] if g['galaxy'] == GALAXY)\nd = g['data']\n\nR     = np.array([p['Rad']   for p in d])\nVobs  = np.array([p['Vobs']  for p in d])\nerrV  = np.array([p['errV']  for p in d])\nVgas  = np.array([p['Vgas']  for p in d])\nVdisk = np.array([p['Vdisk'] for p in d])\nVbul  = np.array([p['Vbul']  for p in d])\n\nVbar = vbar_eq1(Vgas, Vdisk, Vbul)\n\nR1, V1 = R[0],  Vobs[0]\nR2, V2 = R[-1], Vobs[-1]\nouter_term    = (V2 / R2)\ninner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\nomega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\nomega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\nomega = omega_rad_gyr  # reporting/storage only — use omega_kms_kpc for velocity arithmetic\nV_adj   = Vobs - R * omega_kms_kpc\nGM      = V2**2 * R2\nV_kep   = np.sqrt(GM / R)\n\nrmse_omega  = np.sqrt(np.mean((V_adj - Vbar)**2))\nrmse_kepler = np.sqrt(np.mean((V_kep  - Vbar)**2))\nouter_gap   = (V2 - R2*omega_kms_kpc) - np.sqrt(Vgas[-1]**2+Vdisk[-1]**2+Vbul[-1]**2)\n\nprint(f\"=== {GALAXY} — EPS Research Full Kinematic Report ===\")\nprint(f\"Survey:        {g['survey']} Tier {g['quality_tier']}\")\nprint(f\"Distance:      {g['distance_mpc']} ± {g.get('e_distance_mpc','?')} Mpc\")\nprint(f\"Inclination:   {g['inc_deg']} ± {g.get('e_inc_deg','?')} deg\")\nprint(f\"N rings:       {g['n_points']}\")\nprint(f\"R range:       {R.min():.2f} -- {R.max():.2f} kpc\")\nprint(f\"Vmax:          {Vobs.max():.1f} km/s\")\nprint(f\"Omega:         {omega:.3f} rad/Gyr\")\nprint(f\"RMSE omega:    {rmse_omega:.2f} km/s\")\nprint(f\"RMSE Kepler:   {rmse_kepler:.2f} km/s\")\nprint(f\"Outer gap:     {outer_gap:.2f} km/s ({'negative ✓' if outer_gap<0 else 'positive'})\")"),
    code("fig = plt.figure(figsize=(11, 7))\ngs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)\nax1 = fig.add_subplot(gs[0, :])\nax2 = fig.add_subplot(gs[1, 0])\nax3 = fig.add_subplot(gs[1, 1])\n\nax1.errorbar(R, Vobs, yerr=errV, fmt='o', color='#1f77b4', capsize=3,\n             markersize=5, label=r'$V_{\\rm obs}$', zorder=5)\nax1.plot(R, Vbar,  's-', color='#d62728', lw=1.5, label=r'$V_{\\rm bar}$')\nax1.plot(R, V_adj, '^-', color='#2ca02c', lw=1.8,\n         label=fr'$V_{{\\rm adj}}$ ($\\omega={omega:.2f}$ rad/Gyr)')\nax1.plot(R, V_kep, '--', color='#ff7f0e', lw=1.2, label='Keplerian')\nax1.set_ylabel('km/s', fontsize=11)\nax1.set_title(f'{GALAXY} — Full Kinematic Report | EPS Research Corpus v7.3', fontsize=11)\nax1.legend(fontsize=8)\n\nax2.plot(R, Vgas,  'g^-', lw=1.2, label=r'$V_{\\rm gas}$')\nax2.plot(R, Vdisk, 'bv-', lw=1.2, label=r'$V_{\\rm disk}$')\nax2.plot(R, Vbul,  'rs-', lw=1.2, label=r'$V_{\\rm bul}$')\nax2.axhline(0, color='k', lw=0.7, alpha=0.4)\nax2.set_xlabel('Radius (kpc)', fontsize=10)\nax2.set_ylabel('km/s', fontsize=10)\nax2.set_title('Baryonic Components', fontsize=10)\nax2.legend(fontsize=8)\n\nlnR = np.log(R)\nlnV = np.log(Vobs)\nslope = np.gradient(lnV, lnR)\nax3.plot(R, slope, 'o-', color='#9467bd', lw=1.5)\nax3.axhline(-0.5, color='orange', ls='--', lw=1, label='Keplerian (-0.5)')\nax3.axhline(0.0,  color='gray',   ls='--', lw=1, label='Flat (0.0)')\nax3.set_xlabel('Radius (kpc)', fontsize=10)\nax3.set_ylabel('d ln V / d ln R', fontsize=10)\nax3.set_title('Log-Slope Profile', fontsize=10)\nax3.legend(fontsize=8)\n\nplt.savefig(f'ex24_{GALAXY}_report.png', dpi=150, bbox_inches='tight')\nplt.show()")
])

# ── EX25: End-to-end omega workflow ───────────────────────────────────────────
notebooks["ex25_end_to_end_omega_workflow.ipynb"] = nb([
    md("# SPARC Example 25: End-to-End Omega Workflow\n\n**EPS Research RAG Astrophysics Corpus — Unified HI Corpus v7.3**\n\nThis capstone example runs the complete EPS Research omega workflow\non the currently eligible SPARC corpus records.\nThis is exploratory and is not a reproduction of the frozen 84-galaxy benchmark.\n\nSteps:\n1. Load corpus\n2. Filter SPARC Q=1 galaxies\n3. Compute omega for each\n4. Compute RMSE improvement\n5. Flag outer gap sign\n6. Print summary table\n\n**Reference:** Flynn, D.C. & Cannaliato, J. (2025).\nDOI: 10.3389/fspas.2025.1680387\n\n**Important note on corpus fidelity:** The `rotation_curve_corpus_v7.1_flat.csv` and `rotation_curve_corpus_v7.json` are **full-fidelity** — not a summary or veneer. The CSV contains every kinematic parameter published by Lelli et al. (2016) including per-galaxy inclination, distance uncertainties, mass-to-light ratios, and rotation curve statistics. The JSON adds full per-ring data: Vobs, Vgas, Vdisk, Vbul, errV at every radial point. This is the complete published dataset in a single machine-readable file.\n\n**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.23442703  \n**Source:** Lelli, McGaugh & Schombert (2016), AJ 152, 157  \n**Dependencies:** Python 3, numpy, matplotlib, csv (standard library only)"),
    code("import json\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nwith open('rotation_curve_corpus_v7.json') as f:\n    corpus = json.load(f)\n\nresults = []\nfor g in corpus['galaxies']:\n    if g['survey'] != 'SPARC' or not g.get('data') or len(g['data']) < 3:\n        continue\n    d  = g['data']\n    R  = np.array([p['Rad']  for p in d])\n    V  = np.array([p['Vobs'] for p in d])\n    R1, V1 = R[0],  V[0]\n    R2, V2 = R[-1], V[-1]\n    if R1<=0 or R2<=0 or V1<=0 or V2<=0:\n        continue\n    outer_term    = (V2 / R2)\n    inner_term    = (V1 / R1) * ((R1 / R2) ** 1.5)\n    omega_kms_kpc = outer_term - inner_term          # Flynn & Cannaliato 2025 Eq.6  [km/s/kpc]\n    omega_rad_gyr = omega_kms_kpc * 1.0227           # 1 km/s/kpc = 1.0227 rad/Gyr\n    omega = omega_rad_gyr  # reporting/storage only — use omega_kms_kpc for velocity arithmetic\n    V_adj = V - R * omega_kms_kpc\n    GM    = V2**2 * R2\n    V_kep = np.sqrt(GM / R)\n    Vgas  = np.array([p.get('Vgas', 0)  for p in d])\n    Vdisk = np.array([p.get('Vdisk', 0) for p in d])\n    Vbul  = np.array([p.get('Vbul', 0)  for p in d])\n    Vbar  = vbar_eq1(Vgas, Vdisk, Vbul)\n    if np.all(Vbar == 0):\n        continue\n    rmse_o = np.sqrt(np.mean((V_adj - Vbar)**2))\n    rmse_k = np.sqrt(np.mean((V_kep  - Vbar)**2))\n    gap    = (V[-1] - R[-1]*omega_kms_kpc) - np.abs(Vbar[-1])\n    results.append({\n        'galaxy':   g['galaxy'],\n        'omega':    omega,\n        'rmse_o':   rmse_o,\n        'rmse_k':   rmse_k,\n        'improved': rmse_o < rmse_k,\n        'gap':      gap,\n        'gap_neg':  gap < 0,\n    })\n\n# Summary\nomegas  = [r['omega']  for r in results]\nrmse_os = [r['rmse_o'] for r in results]\nrmse_ks = [r['rmse_k'] for r in results]\nimproved = sum(1 for r in results if r['improved'])\ngaps_neg = sum(1 for r in results if r['gap_neg'])\n\nprint(f\"{'='*60}\")\nprint(f\"EPS Research Omega Workflow — SPARC Summary\")\nprint(f\"{'='*60}\")\nprint(f\"Galaxies analyzed:     {len(results)}\")\nprint(f\"Mean omega:            {np.mean(omegas):.2f} ± {np.std(omegas):.2f} rad/Gyr\")\nprint(f\"Mean RMSE (omega):     {np.mean(rmse_os):.2f} km/s\")\nprint(f\"Mean RMSE (Keplerian): {np.mean(rmse_ks):.2f} km/s\")\nprint(f\"Improved:              {improved}/{len(results)}\")\nprint(f\"Regressions:           {len(results)-improved}/{len(results)}\")\nprint(f\"Outer gaps negative:   {gaps_neg}/{len(results)}\")\nprint(f\"\\nPublished results (Flynn & Cannaliato 2025):\")\nprint(f\"  Mean RMSE (omega):  25.45 ± 1.57 km/s\")\nprint(f\"  Improved:           53/84\")\nprint(f\"  Regressions:        0/84\")\nprint(f\"  Outer gaps neg:     84/84\")\nprint()\nprint(\"NOTE: Raw boundary-point formula gives different values than Paper 2.\")\nprint(\"Paper 2 uses Keplerian-corrected formulation with optimised Upsilon.\")\nprint(\"For Paper 2 reproduced results, see: doi.org/10.5281/zenodo.19798527\")"),
    code("fig, axes = plt.subplots(1, 3, figsize=(14, 4))\n\naxes[0].hist(omegas, bins=25, color='#2166ac', alpha=0.8, edgecolor='white')\naxes[0].axvline(np.mean(omegas), color='red', ls='--', lw=1.5,\n                label=f'Mean={np.mean(omegas):.2f}')\naxes[0].set_xlabel(r'$\\omega$ (rad/Gyr)', fontsize=11)\naxes[0].set_ylabel('N', fontsize=11)\naxes[0].set_title('Omega Distribution', fontsize=10)\naxes[0].legend(fontsize=8)\n\naxes[1].scatter(rmse_ks, rmse_os, s=18, alpha=0.6, color='#2166ac')\nlim = [0, max(rmse_ks+rmse_os)*1.05]\naxes[1].plot(lim, lim, 'k--', lw=1, alpha=0.4, label='1:1')\naxes[1].set_xlabel('RMSE Keplerian (km/s)', fontsize=11)\naxes[1].set_ylabel('RMSE Omega (km/s)', fontsize=11)\naxes[1].set_title('RMSE Comparison', fontsize=10)\naxes[1].legend(fontsize=8)\n\ngaps = [r['gap'] for r in results]\naxes[2].hist(gaps, bins=25, color='#d62728', alpha=0.8, edgecolor='white')\naxes[2].axvline(0, color='black', ls='--', lw=1.5, label='Gap=0')\naxes[2].set_xlabel('Outer gap (km/s)', fontsize=11)\naxes[2].set_ylabel('N', fontsize=11)\naxes[2].set_title('Outer Gap Distribution', fontsize=10)\naxes[2].legend(fontsize=8)\n\nplt.suptitle('End-to-End EPS Omega Workflow — SPARC Sample\\n'\n             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387',\n             fontsize=10)\nplt.tight_layout()\nplt.savefig('ex25_end_to_end.png', dpi=150, bbox_inches='tight')\nplt.show()")
])

# ── Write all notebooks ───────────────────────────────────────────────────────

written = 0
for filename, notebook in notebooks.items():
    if filename == "ex19_baryonic_tully_fisher.ipynb":
        notebook["cells"][1]["source"] = COLAB_SETUP_EX19
    with open(filename, 'w') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
        f.write('\n')
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
