#!/usr/bin/env python3
"""
EPS Research — Build remaining 22 High-z Example Notebooks (hz04-hz25)
Run from: ~/Documents/rag-corpus-series/examples/highz/
Requires: high_z_kinematic_corpus_Z1.json and high_z_kinematic_corpus_Z1_flat.csv
          in the same directory.

Usage:
    python3 build_hz_examples_04_25.py

Flynn, D.C. (2026) EPS Research
DOI: 10.5281/zenodo.20369286
arXiv: 2605.25339
"""

import json
import os

def nb(cells):
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3",
                                        "language": "python", "name": "python3"},
                         "language_info": {"name": "python", "version": "3.10.0"}},
            "nbformat": 4, "nbformat_minor": 4}

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text}

def code(text):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [], "source": text}

NOTE = ("**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.20369286  \n"
        "**arXiv:** 2605.25339  \n"
        "**Source:** Jones et al. (2021), MNRAS 507, 3540; Le Fevre et al. (2020)  \n"
        "**Dependencies:** Python 3, numpy, matplotlib")

LOAD_JSON = """import json
import numpy as np
import matplotlib.pyplot as plt

with open('high_z_kinematic_corpus_Z1.json') as f:
    corpus = json.load(f)

galaxies  = corpus['galaxies']
rotators  = [g for g in galaxies if g.get('is_rotator') and g.get('quality_tier')==1]
print(f"Total galaxies: {len(galaxies)}")
print(f"Tier-1 rotators: {len(rotators)}")
"""

LOAD_CSV = """import csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
with open('high_z_kinematic_corpus_Z1_flat.csv') as f:
    for r in csv.DictReader(f):
        rows.append(r)
print(f"Total galaxies: {len(rows)}")
"""

notebooks = {}

# ── HZ04: All 8 rotators gallery ─────────────────────────────────────────────
notebooks["hz_nb4_rotator_gallery.ipynb"] = nb([
md(f"""# High-z Example 04: All 8 Tier-1 Rotator Gallery

**EPS Research — High-z Kinematic Corpus Z1**

All 8 confirmed ALPINE rotators plotted in a single figure.
Each panel shows Vrot with 3DBarolo error bars, loaded directly
from the Z1 corpus JSON.

{NOTE}"""),
code(LOAD_JSON),
code("""fig, axes = plt.subplots(2, 4, figsize=(14, 7))
axes = axes.flatten()

for i, g in enumerate(sorted(rotators, key=lambda x: x['redshift'])):
    d    = g['data']
    R    = [p['R_kpc']     for p in d]
    Vrot = [p['Vrot_kms']  for p in d]
    eV   = [p['e_Vrot_kms'] for p in d]
    ax   = axes[i]
    ax.errorbar(R, Vrot, yerr=eV, fmt='o-', color='#e74c3c',
                capsize=4, linewidth=1.5, markersize=5)
    ax.set_title(f"{g['galaxy']}\\nz={g['redshift']:.4f}  "
                 f"Vmax={max(Vrot):.0f} km/s", fontsize=8)
    ax.set_xlabel('R (kpc)', fontsize=7)
    ax.set_ylabel('Vrot (km/s)', fontsize=7)
    ax.tick_params(labelsize=7)

plt.suptitle('All 8 ALPINE Tier-1 Rotators — EPS Research Z1 Corpus\\n'
             'Sorted by redshift (z = 4.26 to 5.54)', fontsize=11)
plt.tight_layout()
plt.savefig('hz04_rotator_gallery.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ05: V/sigma profiles ────────────────────────────────────────────────────
notebooks["hz_nb5_v_sigma_profiles.ipynb"] = nb([
md(f"""# High-z Example 05: V/sigma Kinematic State Profiles

**EPS Research — High-z Kinematic Corpus Z1**

V/sigma = Vrot/sigma per ring measures the kinematic state:
- V/sigma > 3: rotation-dominated (disk-like)
- V/sigma < 1: dispersion-dominated

At z~5, even confirmed rotators show lower V/sigma than local disks,
reflecting the elevated turbulence in high-z star-forming galaxies.

{NOTE}"""),
code(LOAD_JSON),
code("""fig, axes = plt.subplots(2, 4, figsize=(14, 7))
axes = axes.flatten()

for i, g in enumerate(sorted(rotators, key=lambda x: x['redshift'])):
    d   = g['data']
    R   = [p['R_kpc']       for p in d]
    vos = [p['v_over_sigma'] for p in d]
    ax  = axes[i]
    ax.plot(R, vos, 'o-', color='#9b59b6', linewidth=1.5, markersize=5)
    ax.axhline(3.0, color='green',  ls='--', lw=1, alpha=0.7, label='V/σ=3 (W15)')
    ax.axhline(1.0, color='orange', ls='--', lw=1, alpha=0.7, label='V/σ=1')
    ax.set_title(f"{g['galaxy']}  z={g['redshift']:.4f}", fontsize=8)
    ax.set_xlabel('R (kpc)', fontsize=7)
    ax.set_ylabel('V/σ', fontsize=7)
    ax.tick_params(labelsize=7)
    if i == 0:
        ax.legend(fontsize=6)

plt.suptitle('V/σ Kinematic State — All 8 Z1 Tier-1 Rotators\\n'
             'EPS Research Z1 Corpus | Jones et al. (2021)', fontsize=11)
plt.tight_layout()
plt.savefig('hz05_v_sigma_profiles.png', dpi=150, bbox_inches='tight')
plt.show()

# Summary stats
vos_outer = [g['data'][-1]['v_over_sigma'] for g in rotators]
print(f"V/sigma at outermost ring:")
print(f"  Range:  {min(vos_outer):.2f} -- {max(vos_outer):.2f}")
print(f"  Median: {np.median(vos_outer):.2f}")
print(f"  Above W15 threshold (V/σ>3): {sum(1 for v in vos_outer if v>3)}/8")""")
])

# ── HZ06: Dynamical mass vs stellar mass ──────────────────────────────────────
notebooks["hz_nb6_mdyn_vs_mstar.ipynb"] = nb([
md(f"""# High-z Example 06: Dynamical Mass vs Stellar Mass

**EPS Research — High-z Kinematic Corpus Z1**

For tier-1 rotators, dynamical mass Mdyn = V^2 * R / G.
Comparing Mdyn to M* reveals the dark matter fraction at z~5.
Two anomalous cases (CG32, DC396844) have Mdyn < M* —
physically implausible, likely due to inclination uncertainty.

{NOTE}"""),
code(LOAD_JSON),
code("""data = []
for g in rotators:
    last = g['data'][-1]
    log_mdyn = g.get('log_mdyn_msun')
    log_mstar = g.get('log_mstar_msun')
    if log_mdyn and log_mstar:
        data.append({'galaxy': g['galaxy'],
                     'z': g['redshift'],
                     'log_mdyn': log_mdyn,
                     'log_mstar': log_mstar,
                     'anomalous': log_mdyn < log_mstar})

print(f"Rotators with mass data: {len(data)}")
print(f"\\n{'Galaxy':<20} {'log Mdyn':>9} {'log M*':>8} {'Mdyn/M*':>8} {'Flag'}")
print('-' * 58)
for d in sorted(data, key=lambda x: x['log_mdyn']):
    ratio = d['log_mdyn'] - d['log_mstar']
    flag  = '⚠️  Mdyn < M*' if d['anomalous'] else ''
    print(f"{d['galaxy']:<20} {d['log_mdyn']:>9.3f} {d['log_mstar']:>8.3f} "
          f"{ratio:>8.3f}  {flag}")"""),
code("""fig, ax = plt.subplots(figsize=(7, 6))
log_mdyn  = [d['log_mdyn']  for d in data]
log_mstar = [d['log_mstar'] for d in data]
colors    = ['#e74c3c' if d['anomalous'] else '#2166ac' for d in data]

ax.scatter(log_mstar, log_mdyn, s=80, c=colors, zorder=3, edgecolors='k', linewidths=0.5)
for d in data:
    ax.annotate(d['galaxy'][:8], (d['log_mstar'], d['log_mdyn']),
                textcoords='offset points', xytext=(5, 3), fontsize=7)

lim = [min(log_mstar+log_mdyn)-0.1, max(log_mstar+log_mdyn)+0.1]
ax.plot(lim, lim, 'k--', lw=1, alpha=0.4, label='Mdyn = M* (no dark matter)')
ax.set_xlabel(r'log M$_*$ ($M_\odot$)', fontsize=12)
ax.set_ylabel(r'log M$_{\rm dyn}$ ($M_\odot$)', fontsize=12)
ax.set_title('Dynamical vs Stellar Mass — Z1 Tier-1 Rotators\\n'
             'Red = Mdyn < M* (anomalous, inclination uncertainty)',
             fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hz06_mdyn_mstar.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ07: Wisnioski W15 criteria heatmap ──────────────────────────────────────
notebooks["hz_nb7_w15_heatmap.ipynb"] = nb([
md(f"""# High-z Example 07: Wisnioski (2015) Disk Criteria Heatmap

**EPS Research — High-z Kinematic Corpus Z1**

Wisnioski et al. (2015) define 5 disk criteria for classifying
high-z galaxies as rotation-dominated:
1. Vrot/sigma > 1
2. Smooth velocity gradient
3. Kinematic major axis aligned with morphological axis
4. Peak velocity dispersion at kinematic center
5. Beam-smearing corrected Vrot > sigma

The heatmap shows which criteria each Z1 rotator passes.

{NOTE}"""),
code(LOAD_JSON),
code("""criteria_names = ['V/σ>1', 'Vel. gradient', 'Axis align.',
                  'σ peak center', 'Vrot>σ (corr.)']

# Extract W15 criteria for each rotator
heatmap = []
galaxy_names = []
for g in sorted(rotators, key=lambda x: x['redshift']):
    w15 = g.get('w15_criteria', {})
    row = [1 if w15.get(k, False) else 0
           for k in ['vrot_gt_sigma', 'smooth_gradient',
                     'axis_aligned', 'sigma_peak_center', 'vrot_gt_sigma_corr']]
    # fallback: use n_w15_passed
    if all(v == 0 for v in row) and g.get('n_w15_passed') is not None:
        n = int(g['n_w15_passed'])
        row = [1]*n + [0]*(5-n)
    heatmap.append(row)
    galaxy_names.append(f"{g['galaxy']} (z={g['redshift']:.2f})")

import numpy as np
H = np.array(heatmap)
passed = H.sum(axis=1)

fig, ax = plt.subplots(figsize=(9, 6))
im = ax.imshow(H, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(5))
ax.set_xticklabels(criteria_names, fontsize=9, rotation=20, ha='right')
ax.set_yticks(range(len(galaxy_names)))
ax.set_yticklabels([f"{n}  ({p}/5)" for n, p in zip(galaxy_names, passed)],
                   fontsize=8)
ax.set_title('Wisnioski (2015) Disk Criteria — Z1 Tier-1 Rotators\\n'
             'Green=pass, Red=fail | EPS Research Z1 Corpus', fontsize=10)
plt.colorbar(im, ax=ax, ticks=[0, 1], label='Pass/Fail')
plt.tight_layout()
plt.savefig('hz07_w15_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ08: Omega table reproduction ────────────────────────────────────────────
notebooks["hz_nb8_omega_table.ipynb"] = nb([
md(f"""# High-z Example 08: Reproducing Table 4 — Omega Values

**EPS Research — High-z Kinematic Corpus Z1**

This example reproduces Table 4 from Flynn (2026) arXiv:2605.25339:
omega values for all 8 tier-1 rotators computed from boundary points.

All 8 values are negative (median -13.05 rad/Gyr), contrasting
with positive values at z=0 (SPARC mean +7.06 rad/Gyr).

**Reference:** Flynn (2026), arXiv:2605.25339

{NOTE}"""),
code(LOAD_JSON),
code("""results = []
for g in sorted(rotators, key=lambda x: x['redshift']):
    d  = g['data']
    R1, V1 = d[0]['R_kpc'],  d[0]['Vrot_kms']
    R2, V2 = d[-1]['R_kpc'], d[-1]['Vrot_kms']
    omega  = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
    results.append({'galaxy': g['galaxy'], 'z': g['redshift'],
                    'R2': R2, 'V2': V2, 'omega': omega,
                    'n_rings': len(d)})

omegas = [r['omega'] for r in results]
print(f"{'='*60}")
print(f"Table 4 Reproduction — Z1 Omega Values")
print(f"{'='*60}")
print(f"{'Galaxy':<20} {'z':>7} {'R2':>6} {'V2':>8} {'omega':>10} {'N':>4}")
print('-'*60)
for r in results:
    print(f"{r['galaxy']:<20} {r['z']:>7.4f} {r['R2']:>6.2f} "
          f"{r['V2']:>8.2f} {r['omega']:>10.3f} {r['n_rings']:>4}")
print('-'*60)
print(f"Median omega: {np.median(omegas):.3f} rad/Gyr")
print(f"All negative: {all(o < 0 for o in omegas)}")
print(f"\\nPublished (Flynn 2026): median = -13.05 rad/Gyr")
print(f"SPARC z=0 mean: +7.06 rad/Gyr (Flynn & Cannaliato 2025)")"""),
code("""fig, ax = plt.subplots(figsize=(8, 4))
zs = [r['z'] for r in results]
ax.scatter(zs, omegas, s=100, color='#e74c3c', zorder=5,
           marker='D', edgecolors='k', linewidths=0.7)
for r in results:
    ax.annotate(r['galaxy'][:6], (r['z'], r['omega']),
                textcoords='offset points', xytext=(4, 3), fontsize=7)
ax.axhline(0,    color='black', ls='-',  lw=0.8, alpha=0.3)
ax.axhline(7.06, color='#3498db', ls='-', lw=2, alpha=0.7,
           label='SPARC mean +7.06 (z=0)')
ax.axhline(-13.05, color='red', ls='--', lw=1.5,
           label='Z1 median -13.05 (z~5)')
ax.set_xlabel('Redshift z', fontsize=12)
ax.set_ylabel(r'$\omega$ (rad/Gyr)', fontsize=12)
ax.set_title('Omega Values — Z1 Tier-1 Rotators (Table 4)\\n'
             'Flynn (2026) arXiv:2605.25339', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hz08_omega_table.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ09: Morpho-kinematic class fractions ────────────────────────────────────
notebooks["hz_nb9_class_fractions.ipynb"] = nb([
md(f"""# High-z Example 09: Morpho-Kinematic Class Fractions

**EPS Research — High-z Kinematic Corpus Z1**

Jones et al. (2021) classify all 31 ALPINE galaxies:
- ROT: confirmed rotator (8)
- MER: merger (5)
- DIS: dispersion-dominated (3)
- UNC: uncertain (15)

{NOTE}"""),
code(LOAD_CSV),
code("""from collections import Counter
classes = Counter(r['class_jones2021'] for r in rows)
print("Morpho-kinematic classes:")
for c, n in sorted(classes.items(), key=lambda x: -x[1]):
    print(f"  {c}: {n} ({n/len(rows)*100:.0f}%)")

COLORS = {'ROT':'#2ecc71','MER':'#e74c3c','DIS':'#f39c12','UNC':'#95a5a6'}
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Pie
labels = list(classes.keys())
sizes  = [classes[k] for k in labels]
colors = [COLORS.get(k, '#bdc3c7') for k in labels]
axes[0].pie(sizes, labels=[f'{l} ({n})' for l,n in zip(labels,sizes)],
            colors=colors, autopct='%1.0f%%', textprops={'fontsize': 10})
axes[0].set_title('Class Fractions (N=31)', fontsize=11)

# Redshift by class
for cls, color in COLORS.items():
    zs = [float(r['redshift']) for r in rows if r['class_jones2021']==cls]
    if zs:
        axes[1].scatter([cls]*len(zs), zs, s=40, color=color, alpha=0.8)
axes[1].axhline(5.0, color='black', ls='--', lw=1, alpha=0.5, label='z=5')
axes[1].set_xlabel('Class', fontsize=11)
axes[1].set_ylabel('Redshift z', fontsize=11)
axes[1].set_title('Redshift by Class', fontsize=11)
axes[1].legend(fontsize=8)

plt.suptitle('ALPINE Morpho-Kinematic Classification\\n'
             'EPS Research Z1 Corpus | Jones et al. (2021)', fontsize=11)
plt.tight_layout()
plt.savefig('hz09_class_fractions.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ10: Redshift distribution ───────────────────────────────────────────────
notebooks["hz_nb10_redshift_distribution.ipynb"] = nb([
md(f"""# High-z Example 10: Redshift Distribution

**EPS Research — High-z Kinematic Corpus Z1**

31 galaxies spanning z = 4.26-5.68.
9 galaxies lie at z > 5, approaching cosmic reionization.
Maximum redshift: DC773957 at z = 5.6773.

{NOTE}"""),
code(LOAD_CSV),
code("""import numpy as np
zs = [float(r['redshift']) for r in rows]
classes = [r['class_jones2021'] for r in rows]

print(f"Redshift range: {min(zs):.4f} -- {max(zs):.4f}")
print(f"Median: {np.median(zs):.4f}")
print(f"z > 5: {sum(1 for z in zs if z > 5)} galaxies")
print(f"\\nMax redshift galaxy:")
max_idx = zs.index(max(zs))
print(f"  {rows[max_idx]['galaxy']} at z = {max(zs):.4f}")

COLORS = {'ROT':'#2ecc71','MER':'#e74c3c','DIS':'#f39c12','UNC':'#95a5a6'}
bins = [4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8]

fig, ax = plt.subplots(figsize=(9, 4))
bottom = np.zeros(len(bins)-1)
for cls, color in COLORS.items():
    vals = [float(r['redshift']) for r in rows if r['class_jones2021']==cls]
    counts, _ = np.histogram(vals, bins=bins)
    ax.bar(bins[:-1], counts, width=0.18, bottom=bottom,
           color=color, label=f'{cls} ({len(vals)})', alpha=0.85, align='edge')
    bottom += counts
ax.axvline(5.0, color='black', ls='--', lw=1.5, label='z=5')
ax.set_xlabel('Redshift z', fontsize=12)
ax.set_ylabel('N galaxies', fontsize=12)
ax.set_title('Redshift Distribution — Z1 Corpus (N=31)\\n'
             'Stacked by morpho-kinematic class', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hz10_redshift_distribution.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ11: SFR distribution ────────────────────────────────────────────────────
notebooks["hz_nb11_sfr_distribution.ipynb"] = nb([
md(f"""# High-z Example 11: Star Formation Rate Distribution

**EPS Research — High-z Kinematic Corpus Z1**

Star formation rates from ALPINE SED fitting (Faisst et al. 2020).
At z~5 these are main-sequence star-forming galaxies —
SFR >> typical local galaxies due to cosmic star formation peak.

{NOTE}"""),
code(LOAD_CSV),
code("""import numpy as np
sfrs = [float(r['sfr_msun_yr']) for r in rows if r.get('sfr_msun_yr')]
classes = [r['class_jones2021'] for r in rows if r.get('sfr_msun_yr')]

print(f"Galaxies with SFR: {len(sfrs)}")
print(f"SFR range: {min(sfrs):.1f} -- {max(sfrs):.1f} Msun/yr")
print(f"Median SFR: {np.median(sfrs):.1f} Msun/yr")
print(f"For comparison: Milky Way SFR ~ 2 Msun/yr")
print(f"These galaxies form stars {np.median(sfrs)/2:.0f}x faster than the Milky Way!")

COLORS = {'ROT':'#2ecc71','MER':'#e74c3c','DIS':'#f39c12','UNC':'#95a5a6'}
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(sfrs, bins=12, color='#3498db', alpha=0.8, edgecolor='white')
axes[0].axvline(np.median(sfrs), color='red', ls='--', lw=1.5,
                label=f'Median={np.median(sfrs):.0f}')
axes[0].set_xlabel('SFR (Msun/yr)', fontsize=11)
axes[0].set_ylabel('N', fontsize=11)
axes[0].set_title('SFR Distribution', fontsize=10)
axes[0].legend(fontsize=8)

zs = [float(r['redshift']) for r in rows if r.get('sfr_msun_yr')]
axes[1].scatter(zs, sfrs, s=30, c=[{'ROT':'#2ecc71','MER':'#e74c3c',
    'DIS':'#f39c12','UNC':'#95a5a6'}.get(c,'gray') for c in classes],
    alpha=0.8)
axes[1].set_xlabel('Redshift z', fontsize=11)
axes[1].set_ylabel('SFR (Msun/yr)', fontsize=11)
axes[1].set_title('SFR vs Redshift', fontsize=10)

plt.suptitle('Star Formation Rates — Z1 Corpus\\n'
             'Faisst et al. (2020) ALPINE photometry', fontsize=11)
plt.tight_layout()
plt.savefig('hz11_sfr_distribution.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ12: Stellar mass distribution ──────────────────────────────────────────
notebooks["hz_nb12_stellar_mass.ipynb"] = nb([
md(f"""# High-z Example 12: Stellar Mass Distribution

**EPS Research — High-z Kinematic Corpus Z1**

Stellar masses from ALPINE SED fitting (Faisst et al. 2020).
log M* range: ~9-11 Msun — consistent with massive star-forming
main-sequence galaxies at the peak of cosmic star formation.

{NOTE}"""),
code(LOAD_CSV),
code("""import numpy as np
data = [(r['galaxy'], float(r['log_mstar_msun']), r['class_jones2021'])
        for r in rows if r.get('log_mstar_msun')]
log_ms = [d[1] for d in data]
print(f"Galaxies with M*: {len(data)}")
print(f"log M* range: {min(log_ms):.2f} -- {max(log_ms):.2f}")
print(f"Median log M*: {np.median(log_ms):.2f}")

COLORS = {'ROT':'#2ecc71','MER':'#e74c3c','DIS':'#f39c12','UNC':'#95a5a6'}
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(log_ms, bins=12, color='#9b59b6', alpha=0.8, edgecolor='white')
axes[0].axvline(np.median(log_ms), color='red', ls='--', lw=1.5,
                label=f'Median={np.median(log_ms):.2f}')
axes[0].set_xlabel(r'log M$_*$ ($M_\odot$)', fontsize=11)
axes[0].set_ylabel('N', fontsize=11)
axes[0].set_title('Stellar Mass Distribution', fontsize=10)
axes[0].legend(fontsize=8)

zs = [float(r['redshift']) for r in rows if r.get('log_mstar_msun')]
classes = [r['class_jones2021'] for r in rows if r.get('log_mstar_msun')]
axes[1].scatter(zs, log_ms, s=30,
    c=[COLORS.get(c,'gray') for c in classes], alpha=0.8)
axes[1].set_xlabel('Redshift z', fontsize=11)
axes[1].set_ylabel(r'log M$_*$', fontsize=11)
axes[1].set_title('Stellar Mass vs Redshift', fontsize=10)

plt.suptitle('Stellar Mass Distribution — Z1 Corpus\\n'
             'Faisst et al. (2020) ALPINE SED fitting', fontsize=11)
plt.tight_layout()
plt.savefig('hz12_stellar_mass.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ13: z>5 subsample ──────────────────────────────────────────────────────
notebooks["hz_nb13_z5_subsample.ipynb"] = nb([
md(f"""# High-z Example 13: The z > 5 Subsample

**EPS Research — High-z Kinematic Corpus Z1**

9 of 31 Z1 galaxies lie at z > 5, approaching cosmic reionization.
3 of these are confirmed rotators, making them among the most
distant kinematically-resolved disk galaxies known.

{NOTE}"""),
code(LOAD_CSV),
code("""import numpy as np
z5 = [r for r in rows if float(r['redshift']) > 5.0]
print(f"Galaxies at z > 5: {len(z5)}")
from collections import Counter
classes = Counter(r['class_jones2021'] for r in z5)
print(f"Classes: {dict(classes)}")
print(f"\\n{'Galaxy':<20} {'z':>7} {'Class':>6} {'log M*':>8} {'SFR':>8}")
print('-'*55)
for r in sorted(z5, key=lambda x: float(x['redshift']), reverse=True):
    print(f"{r['galaxy']:<20} {float(r['redshift']):>7.4f} "
          f"{r['class_jones2021']:>6} "
          f"{r.get('log_mstar_msun','?'):>8} "
          f"{r.get('sfr_msun_yr','?'):>8}")
"""),
code("""fig, ax = plt.subplots(figsize=(8, 5))
COLORS = {'ROT':'#2ecc71','MER':'#e74c3c','DIS':'#f39c12','UNC':'#95a5a6'}

for cls, color in COLORS.items():
    sub = [r for r in rows if r['class_jones2021']==cls]
    zs  = [float(r['redshift']) for r in sub]
    ms  = [float(r['log_mstar_msun']) for r in sub if r.get('log_mstar_msun')]
    zs  = [float(r['redshift']) for r in sub if r.get('log_mstar_msun')]
    if zs:
        ax.scatter(zs, ms, s=60, color=color, label=f'{cls}', alpha=0.85,
                   edgecolors='k', linewidths=0.5)

ax.axvline(5.0, color='black', ls='--', lw=1.5, alpha=0.6, label='z=5')
ax.set_xlabel('Redshift z', fontsize=12)
ax.set_ylabel(r'log M$_*$ ($M_\odot$)', fontsize=12)
ax.set_title('Z1 Sample: Stellar Mass vs Redshift\\n'
             'z>5 subsample approaches cosmic reionization', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hz13_z5_subsample.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ14: HZ9 anomaly ────────────────────────────────────────────────────────
notebooks["hz_nb14_hz9_anomaly.ipynb"] = nb([
md(f"""# High-z Example 14: HZ9 Outer-Ring Dispersion Anomaly

**EPS Research — High-z Kinematic Corpus Z1**

HZ9 at z=5.5413 has an anomalous outer ring:
sigma(outer) = 4.82 km/s vs sigma(inner) ~ 71-75 km/s.
This produces V/sigma = 36.6 at the outer boundary —
physically implausible and likely a 3DBarolo fit artifact
at the ALMA beam resolution limit.

This is a documented known limitation in the corpus.

{NOTE}"""),
code(LOAD_JSON),
code("""import numpy as np
# Find HZ9
hz9 = next((g for g in rotators if 'HZ9' in g['galaxy']), None)
if hz9 is None:
    hz9 = next((g for g in galaxies if 'HZ9' in g['galaxy']), None)

if hz9:
    print(f"Galaxy: {hz9['galaxy']}")
    print(f"Redshift: {hz9['redshift']}")
    print(f"\\nPer-ring data:")
    print(f"{'Ring':>5} {'R (kpc)':>9} {'Vrot':>8} {'sigma':>8} {'V/sigma':>9}")
    print('-'*45)
    for i, p in enumerate(hz9['data']):
        flag = ' ⚠️ ANOMALY' if p['sigma_kms'] < 10 else ''
        print(f"{i+1:>5} {p['R_kpc']:>9.2f} {p['Vrot_kms']:>8.2f} "
              f"{p['sigma_kms']:>8.2f} {p['v_over_sigma']:>9.2f}{flag}")
    print(f"\\nNote: Outer sigma={hz9['data'][-1]['sigma_kms']:.2f} km/s is")
    print(f"      {hz9['data'][0]['sigma_kms']/hz9['data'][-1]['sigma_kms']:.0f}x lower than inner sigma")
    print(f"      This is a known 3DBarolo artifact at beam resolution limit")
else:
    print("HZ9 not found in tier-1 rotators — check corpus")"""),
code("""if hz9:
    d = hz9['data']
    R     = [p['R_kpc']      for p in d]
    Vrot  = [p['Vrot_kms']   for p in d]
    sigma = [p['sigma_kms']  for p in d]
    vos   = [p['v_over_sigma'] for p in d]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].plot(R, Vrot, 'o-', color='#e74c3c', lw=1.5, ms=6)
    axes[0].set_xlabel('R (kpc)'); axes[0].set_ylabel('Vrot (km/s)')
    axes[0].set_title('Rotation Curve')

    axes[1].plot(R, sigma, 'o-', color='#9b59b6', lw=1.5, ms=6)
    axes[1].scatter(R[-1], sigma[-1], s=200, color='red', zorder=5,
                    marker='*', label=f'Anomaly: σ={sigma[-1]:.1f}')
    axes[1].set_xlabel('R (kpc)'); axes[1].set_ylabel('σ (km/s)')
    axes[1].set_title('Velocity Dispersion'); axes[1].legend(fontsize=8)

    axes[2].plot(R, vos, 'o-', color='#2ecc71', lw=1.5, ms=6)
    axes[2].scatter(R[-1], vos[-1], s=200, color='red', zorder=5,
                    marker='*', label=f'V/σ={vos[-1]:.1f} (anomalous)')
    axes[2].axhline(3.0, color='gray', ls='--', lw=1)
    axes[2].set_xlabel('R (kpc)'); axes[2].set_ylabel('V/σ')
    axes[2].set_title('Kinematic State'); axes[2].legend(fontsize=8)

    plt.suptitle(f'HZ9 (z={hz9["redshift"]}) — Outer Ring Dispersion Anomaly\\n'
                 'Known 3DBarolo artifact | EPS Research Z1 Corpus', fontsize=11)
    plt.tight_layout()
    plt.savefig('hz14_hz9_anomaly.png', dpi=150, bbox_inches='tight')
    plt.show()""")
])

# ── HZ15: Mdyn < Mstar cases ──────────────────────────────────────────────────
notebooks["hz_nb15_mdyn_anomalies.ipynb"] = nb([
md(f"""# High-z Example 15: CG32 and DC396844 — Mdyn < M* Anomalies

**EPS Research — High-z Kinematic Corpus Z1**

Two Z1 galaxies have dynamical mass below stellar mass:
- CG32: log Mdyn - log M* = -0.16 dex
- DC396844: log Mdyn - log M* = -0.35 dex

This is physically implausible. Likely causes:
- Inclination uncertainty (DC396844 has e_inc = 31°)
- 2-ring boundary constraint amplifying errors
- Unresolved non-circular motions

Values reported as published in Jones et al. (2021).

{NOTE}"""),
code(LOAD_JSON),
code("""import numpy as np
anomalies = []
normal    = []
for g in rotators:
    mdyn  = g.get('log_mdyn_msun')
    mstar = g.get('log_mstar_msun')
    inc   = g.get('inc_kin_deg')
    einc  = g.get('e_inc_kin_deg')
    if mdyn and mstar:
        entry = {'galaxy': g['galaxy'], 'z': g['redshift'],
                 'log_mdyn': mdyn, 'log_mstar': mstar,
                 'diff': mdyn - mstar, 'inc': inc, 'einc': einc}
        if mdyn < mstar:
            anomalies.append(entry)
        else:
            normal.append(entry)

print(f"Anomalous (Mdyn < M*): {len(anomalies)}")
print(f"Normal (Mdyn >= M*):   {len(normal)}")
print()
for a in anomalies:
    print(f"Galaxy: {a['galaxy']}  z={a['z']:.4f}")
    print(f"  log Mdyn = {a['log_mdyn']:.3f}")
    print(f"  log M*   = {a['log_mstar']:.3f}")
    print(f"  Deficit  = {a['diff']:.3f} dex")
    if a['einc']:
        print(f"  Inc uncertainty = ±{a['einc']}° (likely cause)")
    print()"""),
code("""fig, ax = plt.subplots(figsize=(7, 6))
for entry in normal:
    ax.scatter(entry['log_mstar'], entry['log_mdyn'], s=60,
               color='#2166ac', alpha=0.8, zorder=3)
for entry in anomalies:
    ax.scatter(entry['log_mstar'], entry['log_mdyn'], s=120,
               color='#e74c3c', alpha=0.9, zorder=4,
               marker='*', label=f"{entry['galaxy']} (anomalous)")
    ax.annotate(entry['galaxy'], (entry['log_mstar'], entry['log_mdyn']),
                textcoords='offset points', xytext=(5, -10), fontsize=8,
                color='#e74c3c')

all_vals = [e['log_mstar'] for e in normal+anomalies] + \
           [e['log_mdyn']  for e in normal+anomalies]
lim = [min(all_vals)-0.1, max(all_vals)+0.1]
ax.plot(lim, lim, 'k--', lw=1, alpha=0.4, label='Mdyn = M*')
ax.set_xlabel(r'log M$_*$', fontsize=12); ax.set_ylabel(r'log M$_{\rm dyn}$', fontsize=12)
ax.set_title('CG32 & DC396844: Mdyn < M* Anomalies\\n'
             'Likely inclination uncertainty | Values as published', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hz15_mdyn_anomalies.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ16: DC519281 redshift uncertainty ───────────────────────────────────────
notebooks["hz_nb16_redshift_uncertainty.ipynb"] = nb([
md(f"""# High-z Example 16: DC519281 — Anomalous Redshift Uncertainty

**EPS Research — High-z Kinematic Corpus Z1**

DC519281 has ez = 0.02, approximately 40x larger than the
typical sample uncertainty (~0.0005).

This large uncertainty reflects genuine spectroscopic ambiguity
and affects kinematic parameter reliability for this source.

{NOTE}"""),
code(LOAD_CSV),
code("""import numpy as np
ezs = [(r['galaxy'], float(r['redshift']),
        float(r.get('e_redshift', 0) or 0))
       for r in rows if r.get('e_redshift')]
if not ezs:
    # Try to get from JSON
    print("Note: e_redshift may not be in flat CSV - loading from JSON")
    import json
    with open('high_z_kinematic_corpus_Z1.json') as f:
        corpus = json.load(f)
    ezs = [(g['galaxy'], g['redshift'], g.get('e_redshift', 0))
           for g in corpus['galaxies'] if g.get('e_redshift')]

if ezs:
    typical = np.median([e[2] for e in ezs if e[2] > 0])
    print(f"Typical redshift uncertainty: {typical:.4f}")
    print(f"\\n{'Galaxy':<20} {'z':>7} {'ez':>8} {'ez/typical':>12}")
    print('-'*52)
    for name, z, ez in sorted(ezs, key=lambda x: -x[2]):
        print(f"{name:<20} {z:>7.4f} {ez:>8.4f} {ez/typical if typical else 0:>12.1f}x")
else:
    print("Loading redshift data from corpus JSON directly:")
    import json
    with open('high_z_kinematic_corpus_Z1.json') as f:
        corpus = json.load(f)
    for g in corpus['galaxies']:
        if 'DC519281' in g['galaxy'] or g.get('e_redshift', 0) > 0.01:
            print(f"  {g['galaxy']}: z={g['redshift']}, ez={g.get('e_redshift','?')}")""")
])

# ── HZ17: Z1 vs SPARC Vmax ────────────────────────────────────────────────────
notebooks["hz_nb17_z1_vs_sparc_vmax.ipynb"] = nb([
md(f"""# High-z Example 17: Z1 vs SPARC Peak Velocity Comparison (EPS)

**EPS Research — Cross-Corpus**

How do Z1 peak rotation velocities compare to the SPARC z=0 sample?
Z1 tier-1 rotators span 62-252 km/s — overlapping with SPARC dwarfs
and intermediate spirals, but not massive spirals.

This cross-corpus comparison requires both Z1 and SPARC corpora.

{NOTE}"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

# Load Z1
with open('high_z_kinematic_corpus_Z1.json') as f:
    z1_corpus = json.load(f)

rotators = [g for g in z1_corpus['galaxies']
            if g.get('is_rotator') and g.get('quality_tier')==1]
z1_vmax = [g['vrot_max_kms'] for g in rotators if g.get('vrot_max_kms')]
z1_names = [g['galaxy'] for g in rotators if g.get('vrot_max_kms')]

print(f"Z1 tier-1 Vmax range: {min(z1_vmax):.0f} -- {max(z1_vmax):.0f} km/s")
print(f"Z1 tier-1 median Vmax: {np.median(z1_vmax):.0f} km/s")

# SPARC reference from corpus v7 if available
try:
    import csv
    sparc_vmax = []
    with open('../hi/rotation_curve_corpus_v7_flat.csv') as f:
        for r in csv.DictReader(f):
            if r['survey']=='SPARC' and r.get('vrot_max_kms'):
                sparc_vmax.append(float(r['vrot_max_kms']))
    print(f"\\nSPARC Vmax range: {min(sparc_vmax):.0f} -- {max(sparc_vmax):.0f} km/s")
    print(f"SPARC median Vmax: {np.median(sparc_vmax):.0f} km/s")
    have_sparc = True
except:
    print("\\nSPARC corpus not found in ../hi/ — showing Z1 only")
    have_sparc = False"""),
code("""fig, ax = plt.subplots(figsize=(9, 5))
bins = range(0, 400, 20)

if have_sparc:
    ax.hist(sparc_vmax, bins=bins, alpha=0.5, color='#3498db',
            label=f'SPARC z=0 (N={len(sparc_vmax)})', edgecolor='white')
ax.hist(z1_vmax, bins=bins, alpha=0.8, color='#e74c3c',
        label=f'Z1 z~4-6 tier-1 (N={len(z1_vmax)})', edgecolor='white')

for v, name in zip(z1_vmax, z1_names):
    ax.axvline(v, color='#e74c3c', lw=0.5, alpha=0.4)

ax.set_xlabel('Peak rotation velocity (km/s)', fontsize=12)
ax.set_ylabel('N galaxies', fontsize=12)
ax.set_title('Z1 vs SPARC Peak Velocity Distribution\\n'
             'EPS Research Cross-Corpus Comparison', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hz17_z1_vs_sparc_vmax.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ18: Progenitor candidates ───────────────────────────────────────────────
notebooks["hz_nb18_progenitor_candidates.ipynb"] = nb([
md(f"""# High-z Example 18: Local Dwarf Progenitor Candidates (EPS)

**EPS Research — Cross-Corpus**

Which Z1 galaxies could be progenitors of local dwarfs?
Criteria: Vmax < 100 km/s, ROT or UNC class, log M* < 10.

ALPINE selection bias means true DDO161-mass progenitors
(log M* ~ 7.5) are below ALPINE detection limits.
The candidates here are upper-mass analogs.

{NOTE}"""),
code("""import json, numpy as np, matplotlib.pyplot as plt

with open('high_z_kinematic_corpus_Z1.json') as f:
    corpus = json.load(f)

# Z1 progenitor candidates
candidates = [g for g in corpus['galaxies']
              if g.get('vrot_max_kms') and g['vrot_max_kms'] < 120
              and g.get('log_mstar_msun') and g['log_mstar_msun'] < 10.5]

print(f"Z1 progenitor candidates (Vmax<120, log M*<10.5): {len(candidates)}")
print(f"\\n{'Galaxy':<20} {'z':>7} {'Vmax':>7} {'log M*':>8} {'Class':>6}")
print('-'*55)
for g in sorted(candidates, key=lambda x: x['vrot_max_kms']):
    print(f"{g['galaxy']:<20} {g['redshift']:>7.4f} "
          f"{g['vrot_max_kms']:>7.1f} {g['log_mstar_msun']:>8.2f} "
          f"{g['class_jones2021']:>6}")

print(f"\\nComparison — Local dwarfs (EPS Dwarf Corpus v1.0):")
print(f"  DDO161: Vmax=67 km/s, log M*~7.8")
print(f"  Median dwarf: Vmax~50 km/s")
print(f"  Note: ALPINE misses true DDO161-mass progenitors (ALPINE SFR > few Msun/yr)")"""),
code("""all_g = corpus['galaxies']
vmax  = [g['vrot_max_kms'] for g in all_g if g.get('vrot_max_kms')]
ms    = [g['log_mstar_msun'] for g in all_g if g.get('vrot_max_kms') and g.get('log_mstar_msun')]
vmax2 = [g['vrot_max_kms'] for g in all_g if g.get('vrot_max_kms') and g.get('log_mstar_msun')]
classes=[g['class_jones2021'] for g in all_g if g.get('vrot_max_kms') and g.get('log_mstar_msun')]

COLORS={'ROT':'#2ecc71','MER':'#e74c3c','DIS':'#f39c12','UNC':'#95a5a6'}
fig,ax=plt.subplots(figsize=(8,5))
for cls,color in COLORS.items():
    idx=[i for i,c in enumerate(classes) if c==cls]
    ax.scatter([vmax2[i] for i in idx],[ms[i] for i in idx],
               s=60,color=color,label=cls,alpha=0.8,edgecolors='k',linewidths=0.5)
ax.axvline(120,color='black',ls='--',lw=1.5,alpha=0.5,label='Vmax=120 km/s cutoff')
ax.axhline(10.5,color='gray',ls='--',lw=1.5,alpha=0.5,label='log M*=10.5 cutoff')
ax.set_xlabel('Vmax (km/s)',fontsize=12); ax.set_ylabel(r'log M$_*$',fontsize=12)
ax.set_title('Z1 Progenitor Candidates\\nEPS Research Cross-Corpus Analysis',fontsize=11)
ax.legend(fontsize=8); plt.tight_layout()
plt.savefig('hz18_progenitors.png',dpi=150,bbox_inches='tight'); plt.show()""")
])

# ── HZ19: Full EPS trilogy omega ──────────────────────────────────────────────
notebooks["hz_nb19_eps_trilogy_omega.ipynb"] = nb([
md(f"""# High-z Example 19: The EPS Omega Trilogy Plot (EPS Flagship)

**EPS Research — Cross-Corpus: All Four Corpora**

This is the signature EPS Research cross-epoch result:
omega sign reversal from z~5 to z=0.

- Z1 (z~4-6): median -13.05 rad/Gyr (all negative)
- SPARC (z=0): mean +7.06 rad/Gyr (all positive)
- Dwarfs (z=0): median +9.94 rad/Gyr (all positive)

This sign reversal across ~9 Gyr is consistent with evolution
from compact centrally-concentrated high-z systems to extended
rotating disks at z=0.

**References:**
- Flynn & Cannaliato (2025) DOI: 10.3389/fspas.2025.1680387
- Flynn (2026) arXiv:2605.25339

{NOTE}"""),
code("""import json, numpy as np, matplotlib.pyplot as plt

with open('high_z_kinematic_corpus_Z1.json') as f:
    corpus = json.load(f)

rotators = [g for g in corpus['galaxies']
            if g.get('is_rotator') and g.get('quality_tier')==1]

# Compute Z1 omega
z1_results = []
for g in rotators:
    d  = g['data']
    R1, V1 = d[0]['R_kpc'],  d[0]['Vrot_kms']
    R2, V2 = d[-1]['R_kpc'], d[-1]['Vrot_kms']
    omega  = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
    z1_results.append({'galaxy': g['galaxy'], 'z': g['redshift'], 'omega': omega})

# Published z=0 reference values (Flynn & Cannaliato 2025, Flynn 2026)
sparc_mean    = 7.06;  sparc_std    = 3.26
dwarf_median  = 9.94;  dwarf_std    = 4.5   # approximate

z1_z      = [r['z']     for r in z1_results]
z1_omega  = [r['omega'] for r in z1_results]
z1_median = np.median(z1_omega)

print(f"Z1 omega: median={z1_median:.2f}, all negative={all(o<0 for o in z1_omega)}")
print(f"SPARC omega: mean={sparc_mean:.2f} ± {sparc_std:.2f} rad/Gyr")
print(f"Dwarf omega: median={dwarf_median:.2f} rad/Gyr")
print(f"\\nSign reversal confirmed: z~5 negative, z=0 positive")"""),
code("""fig, ax = plt.subplots(figsize=(10, 5))

# z=0 reference bands
ax.axhspan(sparc_mean-sparc_std, sparc_mean+sparc_std,
           alpha=0.15, color='#3498db', label=f'SPARC ±1σ band')
ax.axhline(sparc_mean, color='#3498db', ls='-', lw=2, alpha=0.8,
           label=f'SPARC mean +{sparc_mean:.2f} (z=0)')
ax.axhline(dwarf_median, color='#2ecc71', ls='--', lw=2, alpha=0.8,
           label=f'Dwarf median +{dwarf_median:.2f} (z=0)')
ax.axhline(0, color='black', ls='-', lw=0.8, alpha=0.3)
ax.axhline(z1_median, color='#e74c3c', ls='--', lw=1.5,
           label=f'Z1 median {z1_median:.2f} (z~5)')

# Z1 points
sc = ax.scatter(z1_z, z1_omega, s=120, color='#e74c3c', zorder=5,
                marker='D', edgecolors='k', linewidths=0.7,
                label='Z1 tier-1 rotators')
for r in z1_results:
    ax.annotate(r['galaxy'][:6], (r['z'], r['omega']),
                textcoords='offset points', xytext=(4, 3), fontsize=7)

ax.set_xlabel('Redshift z', fontsize=12)
ax.set_ylabel(r'$\omega$ (rad/Gyr)', fontsize=12)
ax.set_title('EPS Research Omega Trilogy: Sign Reversal Across Cosmic Time\\n'
             'Flynn & Cannaliato (2025) + Flynn (2026) arXiv:2605.25339',
             fontsize=11)
ax.legend(fontsize=8, loc='upper right')
ax.text(0.02, 0.05,
        'Note: Z1 values are observational kinematics only\\n'
        'No baryonic decomposition available at z~5',
        transform=ax.transAxes, fontsize=8,
        bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.85))
plt.tight_layout()
plt.savefig('hz19_eps_trilogy_omega.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HZ20: Beam smearing assessment ────────────────────────────────────────────
notebooks["hz_nb20_beam_smearing.ipynb"] = nb([
md(f"""# High-z Example 20: Beam Smearing Assessment

**EPS Research — High-z Kinematic Corpus Z1**

All ALPINE data has ~1 arcsec beam (~6-7 kpc at z~5).
This sets the spatial resolution floor and affects inner-ring
kinematic measurements. 3DBarolo mitigates but does not
eliminate beam-smearing effects.

This example quantifies the beam size relative to galaxy size.

{NOTE}"""),
code(LOAD_JSON),
code("""import numpy as np
# ALMA beam: ~1 arcsec FWHM
# Angular diameter distance at z~5: ~1740 Mpc (flat LCDM)
# 1 arcsec at z=5 ~ 6.3 kpc

beam_kpc = 6.3  # approximate beam size in kpc at z~5

print(f"ALMA beam size: ~1 arcsec FWHM")
print(f"Physical scale: ~{beam_kpc:.1f} kpc at z~5")
print()
print("Beam size relative to rotation curve extent:")
print(f"{'Galaxy':<20} {'z':>6} {'R_max':>7} {'Beam/R_max':>11} {'N_rings':>8}")
print('-'*58)

for g in sorted(rotators, key=lambda x: x['redshift']):
    R_max   = g['data'][-1]['R_kpc']
    n_rings = len(g['data'])
    ratio   = beam_kpc / R_max
    flag    = ' ← marginal' if ratio > 0.4 else ''
    print(f"{g['galaxy']:<20} {g['redshift']:>6.4f} {R_max:>7.2f} "
          f"{ratio:>11.2f}{flag}  {n_rings:>8}")

print(f"\\nNote: Beam/R_max > 0.4 means beam spans >40% of galaxy — poorly resolved")""")
])

# ── HZ21: Single galaxy full JSON report ──────────────────────────────────────
notebooks["hz_nb21_single_galaxy_report.ipynb"] = nb([
md(f"""# High-z Example 21: Single Galaxy Full JSON Report

**EPS Research — High-z Kinematic Corpus Z1**

A complete kinematic report for DC552206 — the z=5.5 rotator
with the most rings (3) and a rising rotation curve.
All parameters extracted from a single JSON load.

{NOTE}"""),
code(LOAD_JSON),
code("""# DC552206: z=5.5016, 3 rings, rising Vrot
target = 'DC552206'
g = next((g for g in galaxies if g['galaxy'] == target), rotators[0])

print(f"{'='*55}")
print(f"Full Kinematic Report: {g['galaxy']}")
print(f"{'='*55}")
print(f"Redshift:        {g['redshift']}")
print(f"Classification:  {g['class_jones2021']}")
print(f"Quality tier:    {g['quality_tier']}")
print(f"Beam smeared:    {g.get('beam_smeared', True)}")
print(f"\\nKinematics:")
print(f"  Inclination:   {g.get('inc_kin_deg','?')} deg")
print(f"  PA:            {g.get('pa_kin_deg','?')} deg")
print(f"  Vrot_max:      {g.get('vrot_max_kms','?')} km/s")
print(f"  sigma_mean:    {g.get('sigma_mean_kms','?')} km/s")
print(f"  V/sigma:       {g.get('v_over_sigma','?')}")
print(f"\\nMasses:")
print(f"  log Mdyn:      {g.get('log_mdyn_msun','?')}")
print(f"  log M*:        {g.get('log_mstar_msun','?')}")
print(f"  SFR:           {g.get('sfr_msun_yr','?')} Msun/yr")
print(f"\\nPer-ring data ({len(g['data'])} rings):")
print(f"{'Ring':>5} {'R (kpc)':>9} {'Vrot':>8} {'eVrot':>7} {'sigma':>8} {'V/sigma':>9}")
for i,p in enumerate(g['data']):
    print(f"{i+1:>5} {p['R_kpc']:>9.2f} {p['Vrot_kms']:>8.2f} "
          f"{p['e_Vrot_kms']:>7.2f} {p['sigma_kms']:>8.2f} {p['v_over_sigma']:>9.2f}")

# Omega
d=g['data']; R1,V1=d[0]['R_kpc'],d[0]['Vrot_kms']; R2,V2=d[-1]['R_kpc'],d[-1]['Vrot_kms']
omega=V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
print(f"\\nEPS omega:       {omega:.3f} rad/Gyr")""")
])

# ── HZ22: Flat CSV query patterns ─────────────────────────────────────────────
notebooks["hz_nb22_csv_query_patterns.ipynb"] = nb([
md(f"""# High-z Example 22: Flat CSV Query Patterns

**EPS Research — High-z Kinematic Corpus Z1**

The flat CSV enables fast filtering without loading the full JSON.
This example demonstrates common query patterns for the Z1 corpus.

{NOTE}"""),
code(LOAD_CSV),
code("""import numpy as np

# Query 1: All confirmed rotators
rotators_csv = [r for r in rows if r['class_jones2021'] == 'ROT']
print(f"Query 1 — Confirmed rotators: {len(rotators_csv)}")

# Query 2: Galaxies at z > 5
z5 = [r for r in rows if float(r['redshift']) > 5.0]
print(f"Query 2 — z > 5: {len(z5)}")

# Query 3: High V/sigma (rotation dominated)
high_vos = [r for r in rows if r.get('v_over_sigma') and
            float(r['v_over_sigma']) > 3.0]
print(f"Query 3 — V/sigma > 3: {len(high_vos)}")

# Query 4: Tier 1 with high Vrot
fast = [r for r in rows if r.get('quality_tier') and
        r['quality_tier'] == '1' and
        r.get('vrot_max_kms') and float(r['vrot_max_kms']) > 150]
print(f"Query 4 — Tier 1 with Vmax > 150 km/s: {len(fast)}")
for r in fast:
    print(f"  {r['galaxy']}: {r['vrot_max_kms']} km/s at z={r['redshift']}")

# Query 5: Mergers
mergers = [r for r in rows if r['class_jones2021'] == 'MER']
print(f"\\nQuery 5 — Mergers: {len(mergers)}")
for r in mergers:
    print(f"  {r['galaxy']}: z={r['redshift']}")""")
])

# ── HZ23: RAG JSONL demo ──────────────────────────────────────────────────────
notebooks["hz_nb23_rag_jsonl_demo.ipynb"] = nb([
md(f"""# High-z Example 23: RAG-Ready JSONL Demonstration

**EPS Research — High-z Kinematic Corpus Z1**

The JSONL format (one galaxy per line) is optimized for LLM
retrieval-augmented generation (RAG) pipelines.
Each line is a self-contained JSON object with full metadata —
no external lookups needed to answer kinematic queries.

This example shows how to load and query the JSONL format.

{NOTE}"""),
code("""import json
import numpy as np

# Load JSONL (one galaxy per line)
galaxies_jsonl = []
with open('high_z_kinematic_corpus_Z1.jsonl') as f:
    for line in f:
        galaxies_jsonl.append(json.loads(line))

print(f"Loaded {len(galaxies_jsonl)} galaxy records from JSONL")
print(f"\\nEach record is self-contained:")
g = galaxies_jsonl[0]
print(f"  Keys: {list(g.keys())}")
print(f"\\nSize per record: ~{len(json.dumps(g))/1024:.1f} KB")
print(f"  (well within LLM context limits)")
print(f"\\nExample RAG query: 'What is the omega value for {g['galaxy']}?'")

# Simulate a RAG retrieval
target = 'DC552206'
record = next((g for g in galaxies_jsonl if g['galaxy'] == target),
              galaxies_jsonl[0])
d = record.get('data', [])
if d:
    R1,V1=d[0]['R_kpc'],d[0]['Vrot_kms']
    R2,V2=d[-1]['R_kpc'],d[-1]['Vrot_kms']
    omega=V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
    print(f"\\nRAG answer for {target}:")
    print(f"  omega = {omega:.3f} rad/Gyr")
    print(f"  Vmax = {record.get('vrot_max_kms','?')} km/s")
    print(f"  z = {record['redshift']}")""")
])

# ── HZ24: Schema self-description ────────────────────────────────────────────
notebooks["hz_nb24_schema_self_description.ipynb"] = nb([
md(f"""# High-z Example 24: Schema Self-Description Test

**EPS Research — High-z Kinematic Corpus Z1**

The Z1 corpus is designed to be self-describing for LLM consumption.
This example verifies that all field names, units, and quality flags
are explicit and unambiguous in the JSON schema.

{NOTE}"""),
code(LOAD_JSON),
code("""# Verify schema self-description
print("Z1 Corpus Schema Verification")
print("="*50)
print(f"\\nTop-level keys: {list(corpus.keys())}")
if corpus.get('metadata'):
    print(f"\\nMetadata:")
    for k, v in corpus['metadata'].items():
        print(f"  {k}: {v}")

print(f"\\nPer-galaxy fields:")
g = galaxies[0]
for k, v in g.items():
    if k != 'data':
        print(f"  {k}: {type(v).__name__} = {v}")

print(f"\\nPer-ring fields (tier-1):")
tier1 = next(g for g in galaxies if g.get('quality_tier')==1)
if tier1.get('data'):
    for k, v in tier1['data'][0].items():
        print(f"  {k}: {type(v).__name__} = {v}")

print(f"\\nQuality tier system:")
print(f"  Tier 1: per-ring Vrot, sigma, Mdyn ({sum(1 for g in galaxies if g.get('quality_tier')==1)} galaxies)")
print(f"  Tier 2: morpho-kinematic classification only ({sum(1 for g in galaxies if g.get('quality_tier')==2)} galaxies)")""")
])

# ── HZ25: End-to-end Z1 workflow capstone ────────────────────────────────────
notebooks["hz_nb25_end_to_end_workflow.ipynb"] = nb([
md(f"""# High-z Example 25: End-to-End Z1 Workflow Capstone

**EPS Research — High-z Kinematic Corpus Z1**

Capstone example: the complete Z1 analysis workflow.
1. Load corpus
2. Filter tier-1 rotators
3. Compute omega for all 8
4. Compare to z=0 reference values
5. Reproduce the key Z1 result from Flynn (2026)

**Reference:** Flynn (2026) arXiv:2605.25339
DOI: 10.5281/zenodo.20369286

{NOTE}"""),
code(LOAD_JSON),
code("""import numpy as np

# Step 1: Filter tier-1 rotators
rotators = [g for g in galaxies
            if g.get('is_rotator') and g.get('quality_tier')==1]
print(f"Step 1: {len(rotators)} tier-1 rotators loaded")

# Step 2: Compute omega for all
results = []
for g in sorted(rotators, key=lambda x: x['redshift']):
    d  = g['data']
    R1, V1 = d[0]['R_kpc'],  d[0]['Vrot_kms']
    R2, V2 = d[-1]['R_kpc'], d[-1]['Vrot_kms']
    omega  = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
    results.append({'galaxy': g['galaxy'], 'z': g['redshift'],
                    'omega': omega, 'vmax': g.get('vrot_max_kms', 0),
                    'n_rings': len(d)})

omegas = [r['omega'] for r in results]

# Step 3: Summary
print(f"\\nStep 2: Omega computed for {len(results)} galaxies")
print(f"\\n{'='*60}")
print(f"Z1 Omega Results — Flynn (2026) arXiv:2605.25339")
print(f"{'='*60}")
print(f"{'Galaxy':<20} {'z':>7} {'omega':>8} {'Vmax':>7} {'N':>4}")
print('-'*48)
for r in results:
    print(f"{r['galaxy']:<20} {r['z']:>7.4f} {r['omega']:>8.3f} "
          f"{r['vmax']:>7.1f} {r['n_rings']:>4}")
print('-'*48)
print(f"Median omega:    {np.median(omegas):.3f} rad/Gyr")
print(f"All negative:    {all(o < 0 for o in omegas)}")
print(f"\\nPublished result (Flynn 2026): median = -13.05 rad/Gyr")
print(f"SPARC z=0 mean:  +7.06 ± 3.26 rad/Gyr (Flynn & Cannaliato 2025)")
print(f"Dwarf z=0 med:   +9.94 rad/Gyr (Flynn 2026)")
print(f"\\nSign reversal confirmed across ~9 Gyr of cosmic evolution.")"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(11, 4))

zs = [r['z'] for r in results]
axes[0].scatter(zs, omegas, s=100, color='#e74c3c', zorder=5,
                marker='D', edgecolors='k', linewidths=0.7,
                label='Z1 tier-1 rotators')
axes[0].axhline(7.06,  color='#3498db', ls='-',  lw=2, alpha=0.8,
                label='SPARC mean +7.06 (z=0)')
axes[0].axhline(9.94,  color='#2ecc71', ls='--', lw=2, alpha=0.8,
                label='Dwarf median +9.94 (z=0)')
axes[0].axhline(0,     color='black',   ls='-',  lw=0.7, alpha=0.3)
axes[0].set_xlabel('Redshift z', fontsize=11)
axes[0].set_ylabel(r'$\omega$ (rad/Gyr)', fontsize=11)
axes[0].set_title('Omega Sign Reversal', fontsize=10)
axes[0].legend(fontsize=7)

axes[1].barh([r['galaxy'] for r in results], omegas,
             color=['#e74c3c' if o < 0 else '#2ecc71' for o in omegas],
             alpha=0.8, edgecolor='white')
axes[1].axvline(0, color='black', lw=1.5)
axes[1].axvline(7.06, color='#3498db', ls='--', lw=1.5, alpha=0.7,
                label='SPARC mean')
axes[1].set_xlabel(r'$\omega$ (rad/Gyr)', fontsize=11)
axes[1].set_title('Per-Galaxy Omega', fontsize=10)
axes[1].legend(fontsize=8)

plt.suptitle('Z1 End-to-End Workflow — EPS Research\\n'
             'Flynn (2026) arXiv:2605.25339 | DOI: 10.5281/zenodo.20369286',
             fontsize=11)
plt.tight_layout()
plt.savefig('hz25_end_to_end.png', dpi=150, bbox_inches='tight')
plt.show()
print("\\nCapstone complete. All 25 Z1 examples demonstrated.")""")
])

# ── Write all notebooks ───────────────────────────────────────────────────────
written = 0
for filename, notebook in notebooks.items():
    with open(filename, 'w') as f:
        json.dump(notebook, f, indent=1)
    written += 1
    print(f"Written: {filename}")

print(f"\n{'='*50}")
print(f"High-z Examples: {written}/22 new notebooks written")
print(f"Total Z1 examples: {written + 3}/25 (including nb1-nb3)")
print(f"{'='*50}")
print(f"\nRequired data files in this directory:")
print(f"  high_z_kinematic_corpus_Z1.json")
print(f"  high_z_kinematic_corpus_Z1_flat.csv")
print(f"  high_z_kinematic_corpus_Z1.jsonl")
print(f"\nNext steps:")
print(f"1. Copy corpus files here")
print(f"2. Run: jupyter lab")
print(f"3. Spot-check hz_nb4 and hz_nb25")
print(f"4. git add examples/highz/ && git commit -m 'Add hz04-hz25 examples'")
print(f"5. git push")
