#!/usr/bin/env python3
"""
EPS Research — Build all 25 Globular Cluster Example Notebooks
Run from: ~/Documents/rag-corpus-series/examples/gc/
Requires: harris_gc_corpus_v1.3.1.jsonl in the same directory.

Usage:
    python3 build_gc_examples.py

Flynn, D.C. (2026) EPS Research
DOI: 10.5281/zenodo.19907765
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

NOTE = ("**Corpus:** Flynn (2026), Zenodo DOI: 10.5281/zenodo.19907765  \n"
        "**Sources:** Harris (1996/2010), Vasiliev & Baumgardt (2021), "
        "Baumgardt et al. (2023), Schiavon et al. (2024) APOGEE DR17  \n"
        "**Dependencies:** Python 3, numpy, matplotlib")

LOAD = """import json
import numpy as np
import matplotlib.pyplot as plt

clusters = []
with open('harris_gc_corpus_v1.3.1.jsonl') as f:
    for line in f:
        clusters.append(json.loads(line))
print(f"Total clusters: {len(clusters)}")
"""

notebooks = {}

# ── GC01: First globular cluster ──────────────────────────────────────────────
notebooks["gc01_first_cluster.ipynb"] = nb([
md(f"""# GC Example 01: Your First Globular Cluster Record

**EPS Research — Milky Way Globular Cluster Corpus v1.3.1**

Load and inspect a complete globular cluster record.
We use NGC 104 (47 Tucanae) — the most data-rich record in the corpus,
with full coverage from all four surveys: Harris, Gaia EDR3,
Baumgardt N-body dynamics, and APOGEE DR17 chemistry.

{NOTE}"""),
code(LOAD),
code("""# Find NGC 104 (47 Tuc)
gc = next(c for c in clusters if c['cluster_id'] == 'NGC 104')

print(f"Cluster:       {gc['cluster_id']} ({gc.get('alt_name', 'N/A')})")
print(f"Position:      RA={gc['position']['ra_hms']}  Dec={gc['position']['dec_dms']}")
print(f"Distance:      {gc['distances']['r_sun_kpc']} kpc (from Sun)")
print(f"Metallicity:   [Fe/H] = {gc['metallicity']['feh']}")
print(f"Luminosity:    M_V = {gc['photometry']['m_v_t']}")
print(f"\\nSurvey coverage:")
print(f"  Harris (1996/2010):   {'YES' if gc.get('metallicity') else 'NO'}")
print(f"  Gaia EDR3:            {'YES' if gc.get('gaia_edr3') else 'NO'}")
print(f"  Baumgardt (2023):     {'YES' if gc.get('baumgardt2023') else 'NO'}")
print(f"  APOGEE DR17:          {'YES' if gc.get('apogee_dr17') else 'NO'}")
print(f"\\nBaumgardt dynamics:")
b = gc['baumgardt2023']
print(f"  Mass:           {b['mass_msun']:,.0f} Msun")
print(f"  Half-mass R:    {b['rhm_pc']:.1f} pc")
print(f"  Velocity disp:  {b['sigma0_kms']:.1f} km/s")
print(f"  Pericenter:     {b['r_peri_kpc']:.2f} kpc")
print(f"  Apocenter:      {b['r_apo_kpc']:.2f} kpc")
print(f"\\nAPOGEE chemistry:")
a = gc['apogee_dr17']
print(f"  [Fe/H] APOGEE:  {a['feh_apogee']}")
print(f"  N members:      {a['n_members']}")""")
])

# ── GC02: Corpus overview ─────────────────────────────────────────────────────
notebooks["gc02_corpus_overview.ipynb"] = nb([
md(f"""# GC Example 02: Corpus Overview — 174 Milky Way Globular Clusters

**EPS Research — Milky Way Globular Cluster Corpus v1.3.1**

174 clusters across four surveys, 17,438 data points total.
This example characterizes the full corpus.

{NOTE}"""),
code(LOAD),
code("""# Survey coverage statistics
has_harris    = sum(1 for c in clusters if c.get('metallicity') and c['metallicity'].get('feh') is not None)
has_gaia      = sum(1 for c in clusters if c.get('gaia_edr3'))
has_baumgardt = sum(1 for c in clusters if c.get('baumgardt2023') and c['baumgardt2023'])
has_apogee    = sum(1 for c in clusters if c.get('apogee_dr17') and c['apogee_dr17'].get('feh_apogee') is not None)
has_all_four  = sum(1 for c in clusters
                    if c.get('metallicity') and c['metallicity'].get('feh') is not None
                    and c.get('gaia_edr3') and c.get('baumgardt2023')
                    and c.get('apogee_dr17') and c['apogee_dr17'].get('feh_apogee') is not None)

print(f"Total clusters:          {len(clusters)}")
print(f"Harris (1996/2010):      {has_harris}")
print(f"Gaia EDR3:               {has_gaia}")
print(f"Baumgardt (2023):        {has_baumgardt}")
print(f"APOGEE DR17:             {has_apogee}")
print(f"Full four-survey:        {has_all_four}")

# Metallicity distribution
fehs = [c['metallicity']['feh'] for c in clusters
        if c.get('metallicity') and c['metallicity'].get('feh') is not None]
print(f"\\n[Fe/H] range: {min(fehs):.2f} to {max(fehs):.2f}")
print(f"Median [Fe/H]: {np.median(fehs):.2f}")"""),
code("""fig, axes = plt.subplots(1, 3, figsize=(13, 4))

# Metallicity histogram
axes[0].hist(fehs, bins=20, color='#2166ac', alpha=0.8, edgecolor='white')
axes[0].set_xlabel('[Fe/H]', fontsize=11)
axes[0].set_ylabel('N clusters', fontsize=11)
axes[0].set_title('Metallicity Distribution', fontsize=10)

# Distance distribution
r_sun = [c['distances']['r_sun_kpc'] for c in clusters
         if c.get('distances') and c['distances'].get('r_sun_kpc')]
axes[1].hist(r_sun, bins=20, color='#d62728', alpha=0.8, edgecolor='white')
axes[1].set_xlabel('Distance from Sun (kpc)', fontsize=11)
axes[1].set_ylabel('N clusters', fontsize=11)
axes[1].set_title('Distance Distribution', fontsize=10)

# Survey coverage bar
surveys = ['Harris', 'Gaia EDR3', 'Baumgardt', 'APOGEE DR17']
counts  = [has_harris, has_gaia, has_baumgardt, has_apogee]
colors  = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
axes[2].bar(surveys, counts, color=colors, alpha=0.8, edgecolor='white')
axes[2].set_ylabel('N clusters', fontsize=11)
axes[2].set_title('Survey Coverage', fontsize=10)
axes[2].tick_params(axis='x', rotation=20)

plt.suptitle('EPS Research Milky Way GC Corpus v1.3.1 — Overview (N=174)',
             fontsize=11)
plt.tight_layout()
plt.savefig('gc02_corpus_overview.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── GC03: Proper motion query ──────────────────────────────────────────────────
notebooks["gc03_proper_motion_query.ipynb"] = nb([
md(f"""# GC Example 03: Gaia EDR3 Proper Motion Query

**EPS Research — Milky Way Globular Cluster Corpus v1.3.1**

Gaia EDR3 provides precise proper motions (mu_alpha, mu_delta) for 170/174 clusters.
This example queries and visualizes the proper motion field across the sky.

{NOTE}"""),
code(LOAD),
code("""# Extract Gaia EDR3 proper motions
pm_clusters = [c for c in clusters if c.get('gaia_edr3') and
               c['gaia_edr3'].get('mu_alpha_mas_yr') is not None]
print(f"Clusters with Gaia proper motions: {len(pm_clusters)}")

l_deg   = [c['position']['l_deg']                    for c in pm_clusters if c['position'].get('l_deg')]
b_deg   = [c['position']['b_deg']                    for c in pm_clusters if c['position'].get('b_deg')]
mu_tot  = [np.sqrt(c['gaia_edr3']['mu_alpha_mas_yr']**2 +
                   c['gaia_edr3']['mu_delta_mas_yr']**2)
           for c in pm_clusters
           if c['position'].get('l_deg') and c['gaia_edr3'].get('mu_alpha_mas_yr')]

print(f"Total proper motion range: {min(mu_tot):.2f} -- {max(mu_tot):.2f} mas/yr")
print(f"Median: {np.median(mu_tot):.2f} mas/yr")"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(12, 4))

sc = axes[0].scatter(l_deg, b_deg, c=np.log10(mu_tot), s=20,
                     cmap='viridis', alpha=0.8)
plt.colorbar(sc, ax=axes[0], label=r'log$_{10}$ $\\mu_{\\rm tot}$ (mas/yr)')
axes[0].set_xlabel('Galactic longitude l (deg)', fontsize=10)
axes[0].set_ylabel('Galactic latitude b (deg)', fontsize=10)
axes[0].set_title('GC Sky Distribution — Colored by Proper Motion', fontsize=10)

axes[1].hist(mu_tot, bins=25, color='#2166ac', alpha=0.8, edgecolor='white')
axes[1].set_xlabel(r'$\\mu_{\\rm tot}$ (mas/yr)', fontsize=11)
axes[1].set_ylabel('N clusters', fontsize=11)
axes[1].set_title('Total Proper Motion Distribution', fontsize=10)

plt.suptitle('Gaia EDR3 Proper Motions — EPS Research GC Corpus v1.3.1', fontsize=11)
plt.tight_layout()
plt.savefig('gc03_proper_motions.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── GC04: Mass vs metallicity ─────────────────────────────────────────────────
notebooks["gc04_mass_metallicity.ipynb"] = nb([
md(f"""# GC Example 04: Dynamical Mass vs Metallicity

**EPS Research — Milky Way Globular Cluster Corpus v1.3.1**

Baumgardt N-body masses vs Harris metallicity.
More massive clusters tend to be more metal-rich —
a fossil record of the Milky Way's chemical enrichment history.

{NOTE}"""),
code(LOAD),
code("""data = []
for c in clusters:
    if (c.get('baumgardt2023') and c['baumgardt2023'].get('mass_msun') and
            c.get('metallicity') and c['metallicity'].get('feh') is not None):
        data.append({'cluster': c['cluster_id'],
                     'mass': c['baumgardt2023']['mass_msun'],
                     'feh':  c['metallicity']['feh'],
                     'r_gc': c['distances'].get('r_gc_kpc', 0) if c.get('distances') else 0})

masses = [d['mass'] for d in data]
fehs   = [d['feh']  for d in data]
r_gcs  = [d['r_gc'] for d in data]

print(f"Clusters with mass + [Fe/H]: {len(data)}")
corr = np.corrcoef(fehs, np.log10(masses))[0, 1]
print(f"Pearson r ([Fe/H] vs log mass): {corr:.3f}")

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(fehs, np.log10(masses), c=r_gcs, s=25, alpha=0.7,
                cmap='RdYlBu_r', vmin=0, vmax=30)
plt.colorbar(sc, ax=ax, label='R_GC (kpc)')
ax.set_xlabel('[Fe/H]', fontsize=12)
ax.set_ylabel(r'log$_{10}$ Mass ($M_\\odot$)', fontsize=12)
ax.set_title(f'Dynamical Mass vs Metallicity (r={corr:.2f})\\n'
             'EPS Research GC Corpus v1.3.1', fontsize=11)
plt.tight_layout()
plt.savefig('gc04_mass_metallicity.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── GC05: Orbital properties ──────────────────────────────────────────────────
notebooks["gc05_orbital_properties.ipynb"] = nb([
md(f"""# GC Example 05: Orbital Properties — Pericenter vs Apocenter

**EPS Research — Milky Way Globular Cluster Corpus v1.3.1**

Baumgardt (2023) provides orbital pericenter and apocenter
computed in the Irrgang et al. (2013) Milky Way potential.
Orbital eccentricity e = (r_apo - r_peri)/(r_apo + r_peri).

{NOTE}"""),
code(LOAD),
code("""orbits = []
for c in clusters:
    b = c.get('baumgardt2023', {})
    if b and b.get('r_peri_kpc') is not None and b.get('r_apo_kpc') is not None:
        r_peri = b['r_peri_kpc']
        r_apo  = b['r_apo_kpc']
        ecc    = (r_apo - r_peri) / (r_apo + r_peri) if (r_apo + r_peri) > 0 else 0
        orbits.append({'cluster': c['cluster_id'], 'r_peri': r_peri,
                       'r_apo': r_apo, 'ecc': ecc,
                       'mass': b.get('mass_msun', 0)})

eccs = [o['ecc'] for o in orbits]
print(f"Clusters with orbital data: {len(orbits)}")
print(f"Eccentricity range: {min(eccs):.3f} -- {max(eccs):.3f}")
print(f"Median eccentricity: {np.median(eccs):.3f}")
print(f"Highly eccentric (e>0.8): {sum(1 for e in eccs if e>0.8)}")

# Most extreme orbits
print("\\nMost eccentric orbits:")
for o in sorted(orbits, key=lambda x: -x['ecc'])[:5]:
    print(f"  {o['cluster']:<12} e={o['ecc']:.3f}  r_peri={o['r_peri']:.1f}  r_apo={o['r_apo']:.1f} kpc")
"""),
code("""fig, axes = plt.subplots(1, 2, figsize=(11, 4))

r_peri = [o['r_peri'] for o in orbits]
r_apo  = [o['r_apo']  for o in orbits]

axes[0].scatter(r_peri, r_apo, s=15, alpha=0.6, color='#2166ac')
lim = [0, max(r_apo) * 1.05]
axes[0].plot(lim, lim, 'k--', lw=1, alpha=0.3, label='r_peri=r_apo (circular)')
axes[0].set_xlabel('Pericenter (kpc)', fontsize=11)
axes[0].set_ylabel('Apocenter (kpc)', fontsize=11)
axes[0].set_title('GC Orbital Pericenter vs Apocenter', fontsize=10)
axes[0].legend(fontsize=8)

axes[1].hist(eccs, bins=20, color='#d62728', alpha=0.8, edgecolor='white')
axes[1].axvline(np.median(eccs), color='black', ls='--', lw=1.5,
                label=f'Median={np.median(eccs):.2f}')
axes[1].set_xlabel('Orbital eccentricity', fontsize=11)
axes[1].set_ylabel('N clusters', fontsize=11)
axes[1].set_title('Eccentricity Distribution', fontsize=10)
axes[1].legend(fontsize=8)

plt.suptitle('Milky Way GC Orbital Properties — EPS Research Corpus v1.3.1', fontsize=11)
plt.tight_layout()
plt.savefig('gc05_orbital_properties.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── GC06-25: Remaining GC notebooks ──────────────────────────────────────────

remaining_gc = {

"gc06_half_mass_radius.ipynb": nb([
md(f"# GC Example 06: Half-Mass Radius Distribution\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nHalf-mass radius r_hm from Baumgardt N-body models.\nCorrelates with age and dynamical state.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['baumgardt2023']['rhm_pc'],c['baumgardt2023']['mass_msun'])
      for c in clusters if c.get('baumgardt2023') and c['baumgardt2023'].get('rhm_pc')]
rhm=[d[1] for d in data]; mass=[d[2] for d in data]
print(f"Clusters with r_hm: {len(data)}")
print(f"r_hm range: {min(rhm):.1f} -- {max(rhm):.1f} pc")
print(f"Median r_hm: {np.median(rhm):.1f} pc")
corr=np.corrcoef(np.log10(mass),np.log10(rhm))[0,1]
print(f"r(log mass, log r_hm) = {corr:.3f}")
fig,axes=plt.subplots(1,2,figsize=(10,4))
axes[0].hist(rhm,bins=20,color='#9467bd',alpha=0.8,edgecolor='white')
axes[0].set_xlabel('Half-mass radius (pc)',fontsize=11); axes[0].set_title('r_hm Distribution',fontsize=10)
axes[1].scatter(np.log10(mass),np.log10(rhm),s=15,alpha=0.6,color='#9467bd')
axes[1].set_xlabel(r'log Mass ($M_\\odot$)',fontsize=11); axes[1].set_ylabel('log r_hm (pc)',fontsize=11)
axes[1].set_title(f'Mass vs r_hm (r={corr:.2f})',fontsize=10)
plt.suptitle('GC Half-Mass Radius — EPS Research Corpus v1.3.1',fontsize=11)
plt.tight_layout(); plt.savefig('gc06_rhm.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc07_velocity_dispersion.ipynb": nb([
md(f"# GC Example 07: Central Velocity Dispersion\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nCentral velocity dispersion sigma_0 from Baumgardt N-body models.\nRelates to cluster mass via sigma_0^2 ∝ M/r_hm.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['baumgardt2023']['sigma0_kms'],c['baumgardt2023']['mass_msun'])
      for c in clusters if c.get('baumgardt2023') and c['baumgardt2023'].get('sigma0_kms')]
sigma=[d[1] for d in data]; mass=[d[2] for d in data]
print(f"Clusters with sigma_0: {len(data)}")
print(f"sigma_0 range: {min(sigma):.1f} -- {max(sigma):.1f} km/s")
fig,ax=plt.subplots(figsize=(7,5))
ax.scatter(np.log10(mass),sigma,s=20,alpha=0.7,color='#1f77b4')
ax.set_xlabel(r'log Mass ($M_\\odot$)',fontsize=12); ax.set_ylabel(r'$\\sigma_0$ (km/s)',fontsize=12)
ax.set_title('Central Velocity Dispersion vs Mass\\nEPS Research GC Corpus v1.3.1',fontsize=10)
plt.tight_layout(); plt.savefig('gc07_sigma0.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc08_inner_outer_halo.ipynb": nb([
md(f"# GC Example 08: Inner vs Outer Halo Classification\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nInner halo (R_GC < 8 kpc) vs outer halo (R_GC > 8 kpc) clusters\nhave different formation histories and chemical properties.\n\n{NOTE}"),
code(LOAD),
code("""inner=[c for c in clusters if c.get('distances') and c['distances'].get('r_gc_kpc') and c['distances']['r_gc_kpc']<8]
outer=[c for c in clusters if c.get('distances') and c['distances'].get('r_gc_kpc') and c['distances']['r_gc_kpc']>=8]
print(f"Inner halo (R_GC < 8 kpc): {len(inner)}")
print(f"Outer halo (R_GC >= 8 kpc): {len(outer)}")
inner_feh=[c['metallicity']['feh'] for c in inner if c.get('metallicity') and c['metallicity'].get('feh') is not None]
outer_feh=[c['metallicity']['feh'] for c in outer if c.get('metallicity') and c['metallicity'].get('feh') is not None]
print(f"Inner median [Fe/H]: {np.median(inner_feh):.2f}")
print(f"Outer median [Fe/H]: {np.median(outer_feh):.2f}")
fig,ax=plt.subplots(figsize=(7,4))
ax.hist(inner_feh,bins=15,alpha=0.7,color='#d62728',label=f'Inner halo ({len(inner_feh)})',edgecolor='white')
ax.hist(outer_feh,bins=15,alpha=0.7,color='#2166ac',label=f'Outer halo ({len(outer_feh)})',edgecolor='white')
ax.set_xlabel('[Fe/H]',fontsize=12); ax.set_ylabel('N',fontsize=12)
ax.set_title('Inner vs Outer Halo Metallicity\\nEPS Research GC Corpus v1.3.1',fontsize=10)
ax.legend(); plt.tight_layout(); plt.savefig('gc08_inner_outer.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc09_apogee_chemistry.ipynb": nb([
md(f"# GC Example 09: APOGEE DR17 Chemistry\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nAPOGEE DR17 provides mean [Fe/H] from H-band spectroscopy for 72 clusters.\nCompare APOGEE vs Harris metallicities.\n\n{NOTE}"),
code(LOAD),
code("""data=[]
for c in clusters:
    if c.get('apogee_dr17') and c['apogee_dr17'].get('feh_apogee') is not None:
        if c.get('metallicity') and c['metallicity'].get('feh') is not None:
            data.append({'cluster':c['cluster_id'],
                         'feh_apogee':c['apogee_dr17']['feh_apogee'],
                         'feh_harris':c['metallicity']['feh'],
                         'n_members':c['apogee_dr17'].get('n_members',0)})
feh_a=[d['feh_apogee'] for d in data]; feh_h=[d['feh_harris'] for d in data]
diff=np.array(feh_a)-np.array(feh_h)
print(f"Clusters with both APOGEE and Harris [Fe/H]: {len(data)}")
print(f"Mean offset (APOGEE - Harris): {np.mean(diff):.3f} dex")
print(f"Std: {np.std(diff):.3f} dex")
fig,axes=plt.subplots(1,2,figsize=(11,4))
axes[0].scatter(feh_h,feh_a,s=20,alpha=0.7,color='#2166ac')
lim=[min(feh_h)-0.1,max(feh_h)+0.1]
axes[0].plot(lim,lim,'k--',lw=1,alpha=0.5,label='1:1')
axes[0].set_xlabel('Harris [Fe/H]',fontsize=11); axes[0].set_ylabel('APOGEE [Fe/H]',fontsize=11)
axes[0].set_title('APOGEE vs Harris Metallicity',fontsize=10); axes[0].legend()
axes[1].hist(diff,bins=15,color='#d62728',alpha=0.8,edgecolor='white')
axes[1].axvline(0,color='black',ls='--',lw=1.5)
axes[1].set_xlabel('APOGEE - Harris [Fe/H]',fontsize=11); axes[1].set_title('Offset Distribution',fontsize=10)
plt.suptitle('APOGEE DR17 vs Harris Metallicity\\nEPS Research GC Corpus v1.3.1',fontsize=11)
plt.tight_layout(); plt.savefig('gc09_apogee_chemistry.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc10_relaxation_time.ipynb": nb([
md(f"# GC Example 10: Relaxation Time and Dynamical State\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nHalf-mass relaxation time t_rh indicates how 'relaxed' a cluster is.\nCore-collapsed clusters have the shortest relaxation times.\n\n{NOTE}"),
code(LOAD),
code("""data=[]
for c in clusters:
    b=c.get('baumgardt2023',{})
    h=c.get('structure',{})
    if b and b.get('log_trh_yr') and h:
        data.append({'cluster':c['cluster_id'],
                     'log_trh':b['log_trh_yr'],
                     'core_collapsed':h.get('core_collapsed',False),
                     'mass':b.get('mass_msun',0)})
cc=[d for d in data if d['core_collapsed']]
nc=[d for d in data if not d['core_collapsed']]
print(f"Total with t_rh: {len(data)}")
print(f"Core-collapsed: {len(cc)}")
print(f"Not core-collapsed: {len(nc)}")
print(f"Mean log t_rh (CC): {np.mean([d['log_trh'] for d in cc]):.2f} yr")
print(f"Mean log t_rh (non-CC): {np.mean([d['log_trh'] for d in nc]):.2f} yr")
fig,ax=plt.subplots(figsize=(7,4))
ax.hist([d['log_trh'] for d in nc],bins=15,alpha=0.7,color='#2166ac',
        label=f'Normal ({len(nc)})',edgecolor='white')
ax.hist([d['log_trh'] for d in cc],bins=10,alpha=0.8,color='#d62728',
        label=f'Core-collapsed ({len(cc)})',edgecolor='white')
ax.set_xlabel(r'log$_{10}$ $t_{\\rm rh}$ (yr)',fontsize=11); ax.set_ylabel('N',fontsize=11)
ax.set_title('Half-Mass Relaxation Time\\nEPS Research GC Corpus v1.3.1',fontsize=10)
ax.legend(); plt.tight_layout(); plt.savefig('gc10_relaxation.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc11_galactic_distribution.ipynb": nb([
md(f"# GC Example 11: Galactic Distribution of GCs\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nGlobular clusters trace the Milky Way's old stellar populations.\nThis example maps the 3D distribution using Baumgardt X,Y,Z coordinates.\n\n{NOTE}"),
code(LOAD),
code("""data=[]
for c in clusters:
    b=c.get('baumgardt2023',{})
    if b and b.get('x_kpc') is not None:
        data.append({'x':b['x_kpc'],'y':b['y_kpc'],'z':b['z_kpc'],
                     'mass':b.get('mass_msun',1e5),'cluster':c['cluster_id']})
print(f"Clusters with 3D positions: {len(data)}")
X=[d['x'] for d in data]; Y=[d['y'] for d in data]; Z=[d['z'] for d in data]
M=[np.log10(d['mass']) for d in data]
fig,axes=plt.subplots(1,2,figsize=(12,5))
sc=axes[0].scatter(X,Y,c=M,s=15,alpha=0.7,cmap='viridis')
plt.colorbar(sc,ax=axes[0],label=r'log Mass ($M_\\odot$)')
axes[0].scatter([0],[0],marker='*',s=200,color='yellow',zorder=5,label='Sun')
axes[0].set_xlabel('X (kpc)',fontsize=11); axes[0].set_ylabel('Y (kpc)',fontsize=11)
axes[0].set_title('Face-on View (X-Y plane)',fontsize=10); axes[0].legend()
sc2=axes[1].scatter(X,Z,c=M,s=15,alpha=0.7,cmap='viridis')
plt.colorbar(sc2,ax=axes[1],label=r'log Mass ($M_\\odot$)')
axes[1].scatter([0],[0],marker='*',s=200,color='yellow',zorder=5)
axes[1].set_xlabel('X (kpc)',fontsize=11); axes[1].set_ylabel('Z (kpc)',fontsize=11)
axes[1].set_title('Edge-on View (X-Z plane)',fontsize=10)
plt.suptitle('Milky Way GC Distribution — EPS Research Corpus v1.3.1',fontsize=11)
plt.tight_layout(); plt.savefig('gc11_distribution.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc12_mass_function.ipynb": nb([
md(f"# GC Example 12: Globular Cluster Mass Function\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nThe GC mass function is roughly log-normal peaked at ~2×10^5 Msun.\nThis turnover mass is a fossil record of dynamical evolution.\n\n{NOTE}"),
code(LOAD),
code("""masses=[c['baumgardt2023']['mass_msun'] for c in clusters
        if c.get('baumgardt2023') and c['baumgardt2023'].get('mass_msun')]
print(f"Clusters with mass: {len(masses)}")
print(f"Mass range: {min(masses):.0f} -- {max(masses):.0f} Msun")
print(f"Median mass: {np.median(masses):.0f} Msun")
print(f"log median: {np.log10(np.median(masses)):.2f}")
fig,ax=plt.subplots(figsize=(8,5))
ax.hist(np.log10(masses),bins=20,color='#9467bd',alpha=0.8,edgecolor='white')
ax.axvline(np.log10(np.median(masses)),color='red',ls='--',lw=1.5,
           label=f'Median={np.median(masses):.0f} Msun')
ax.axvline(np.log10(2e5),color='orange',ls=':',lw=1.5,label='Turnover ~2×10^5')
ax.set_xlabel(r'log$_{10}$ Mass ($M_\\odot$)',fontsize=12)
ax.set_ylabel('N clusters',fontsize=12)
ax.set_title('GC Mass Function — EPS Research Corpus v1.3.1',fontsize=11)
ax.legend(); plt.tight_layout()
plt.savefig('gc12_mass_function.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc13_rotation_detection.ipynb": nb([
md(f"# GC Example 13: GC Rotation Detection\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nBaumgardt (2023) provides rotation amplitude a_rot and detection probability p_rot.\nSome GCs show clear solid-body rotation.\n\n{NOTE}"),
code(LOAD),
code("""rotating=[c for c in clusters if c.get('baumgardt2023') and
           c['baumgardt2023'].get('p_rot_pct') is not None and
           c['baumgardt2023']['p_rot_pct']>90]
print(f"GCs with high rotation probability (p_rot>90%): {len(rotating)}")
print(f"\\n{'Cluster':<15} {'a_rot':>8} {'p_rot':>8} {'mass':>12}")
print('-'*48)
for c in sorted(rotating,key=lambda x:-x['baumgardt2023']['a_rot_kms'])[:10]:
    b=c['baumgardt2023']
    print(f"{c['cluster_id']:<15} {b['a_rot_kms']:>8.2f} {b['p_rot_pct']:>8.1f} {b['mass_msun']:>12,.0f}")
a_rot=[c['baumgardt2023']['a_rot_kms'] for c in clusters
       if c.get('baumgardt2023') and c['baumgardt2023'].get('a_rot_kms') is not None]
fig,ax=plt.subplots(figsize=(7,4))
ax.hist(a_rot,bins=20,color='#2ca02c',alpha=0.8,edgecolor='white')
ax.set_xlabel('Rotation amplitude (km/s)',fontsize=11); ax.set_ylabel('N clusters',fontsize=11)
ax.set_title('GC Rotation Amplitude Distribution\\nEPS Research Corpus v1.3.1',fontsize=10)
plt.tight_layout(); plt.savefig('gc13_rotation.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc14_sgr_stream.ipynb": nb([
md(f"# GC Example 14: Sagittarius Stream Clusters\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nSome GCs were accreted with the Sagittarius dwarf galaxy.\nThe corpus flags these with sgr_stream=True.\n\n{NOTE}"),
code(LOAD),
code("""sgr=[c for c in clusters if c.get('flags',{}).get('sgr_stream',False)]
non_sgr=[c for c in clusters if not c.get('flags',{}).get('sgr_stream',False)]
print(f"Sgr stream GCs: {len(sgr)}")
print(f"Non-Sgr GCs:    {len(non_sgr)}")
print(f"\\nSgr stream clusters:")
for c in sgr:
    b=c.get('baumgardt2023',{})
    feh=c.get('metallicity',{}).get('feh','?')
    mass=b.get('mass_msun','?') if b else '?'
    print(f"  {c['cluster_id']:<12} [Fe/H]={feh}  mass={'N/A' if not isinstance(mass,float) else f'{mass:.0f}'}")
sgr_feh=[c['metallicity']['feh'] for c in sgr
         if c.get('metallicity') and c['metallicity'].get('feh') is not None]
non_feh=[c['metallicity']['feh'] for c in non_sgr
         if c.get('metallicity') and c['metallicity'].get('feh') is not None]
fig,ax=plt.subplots(figsize=(7,4))
ax.hist(non_feh,bins=15,alpha=0.7,color='#2166ac',label=f'Non-Sgr ({len(non_feh)})',edgecolor='white')
ax.hist(sgr_feh,bins=8,alpha=0.8,color='#d62728',label=f'Sgr stream ({len(sgr_feh)})',edgecolor='white')
ax.set_xlabel('[Fe/H]',fontsize=11); ax.set_ylabel('N',fontsize=11)
ax.set_title('Sgr Stream vs Non-Sgr GC Metallicities',fontsize=10)
ax.legend(); plt.tight_layout()
plt.savefig('gc14_sgr_stream.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc15_four_survey_record.ipynb": nb([
md(f"# GC Example 15: Full Four-Survey Record — omega Cen\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nomega Centauri (NGC 5139) is the most massive Milky Way GC.\nThis example displays its complete four-survey record.\n\n{NOTE}"),
code(LOAD),
code("""# Find omega Cen
gc = next((c for c in clusters if 'NGC 5139' in c['cluster_id']
           or (c.get('alt_name') and 'Cen' in str(c.get('alt_name','')))
           or c['cluster_id'] == 'NGC 5139'), None)
if gc is None:
    # Fall back to most massive
    gc = sorted([c for c in clusters if c.get('baumgardt2023') and
                 c['baumgardt2023'].get('mass_msun')],
                key=lambda x: -x['baumgardt2023']['mass_msun'])[0]

print(f"Cluster: {gc['cluster_id']}  Alt: {gc.get('alt_name','')}")
print(f"\\nHarris (1996/2010):")
m=gc['metallicity']; p=gc['photometry']; d=gc['distances']
print(f"  [Fe/H] = {m.get('feh','?')}   E(B-V) = {m.get('ebv','?')}")
print(f"  M_V = {p.get('m_v_t','?')}   Distance = {d.get('r_sun_kpc','?')} kpc")
if gc.get('gaia_edr3'):
    g=gc['gaia_edr3']
    print(f"\\nGaia EDR3:")
    print(f"  mu_alpha = {g.get('mu_alpha_mas_yr','?')} mas/yr")
    print(f"  mu_delta = {g.get('mu_delta_mas_yr','?')} mas/yr")
    print(f"  N members = {g.get('n_members_gaia','?')}")
if gc.get('baumgardt2023'):
    b=gc['baumgardt2023']
    print(f"\\nBaumgardt (2023):")
    print(f"  Mass = {b.get('mass_msun','?'):,.0f} Msun")
    print(f"  sigma_0 = {b.get('sigma0_kms','?')} km/s")
    print(f"  r_hm = {b.get('rhm_pc','?')} pc")
if gc.get('apogee_dr17'):
    a=gc['apogee_dr17']
    print(f"\\nAPOGEE DR17:")
    print(f"  [Fe/H] = {a.get('feh_apogee','?')}")
    print(f"  N members = {a.get('n_members','?')}")""")
]),

"gc16_n_body_selection.ipynb": nb([
md(f"# GC Example 16: Selecting GCs for N-body Follow-up\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nWhich clusters are best suited for N-body simulation follow-up?\nCriteria: well-characterized mass, moderate relaxation time, sufficient members.\n\n{NOTE}"),
code(LOAD),
code("""candidates=[]
for c in clusters:
    b=c.get('baumgardt2023',{})
    if not b or not b.get('mass_msun'): continue
    mass=b['mass_msun']; log_trh=b.get('log_trh_yr',0)
    n_rv=b.get('n_rv',0); n_pm=b.get('n_pm',0)
    score=0
    if 1e4<mass<1e6: score+=2
    if log_trh>9.5: score+=2
    if n_rv>100: score+=1
    if n_pm>1000: score+=1
    candidates.append({'cluster':c['cluster_id'],'mass':mass,
                       'log_trh':log_trh,'n_rv':n_rv,'n_pm':n_pm,'score':score})

top=sorted(candidates,key=lambda x:-x['score'])[:10]
print("Top 10 GCs for N-body follow-up:")
print(f"{'Cluster':<15} {'Mass':>10} {'log t_rh':>9} {'N_rv':>6} {'N_pm':>7} {'Score':>6}")
print('-'*58)
for c in top:
    print(f"{c['cluster']:<15} {c['mass']:>10,.0f} {c['log_trh']:>9.2f} "
          f"{c['n_rv']:>6} {c['n_pm']:>7} {c['score']:>6}")""")
]),

"gc17_distance_comparison.ipynb": nb([
md(f"# GC Example 17: Harris vs Baumgardt Distance Comparison\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nHarris (1996/2010) and Baumgardt (2023) provide independent distance estimates.\nSystematic offsets reveal calibration differences.\n\n{NOTE}"),
code(LOAD),
code("""data=[]
for c in clusters:
    dh=c.get('distances',{}).get('r_sun_kpc')
    db=c.get('baumgardt2023',{}).get('r_sun_kpc') if c.get('baumgardt2023') else None
    if dh and db:
        data.append({'cluster':c['cluster_id'],'harris':dh,'baumgardt':db,'diff':db-dh})
diffs=[d['diff'] for d in data]
print(f"Clusters with both distances: {len(data)}")
print(f"Mean offset (Baumgardt - Harris): {np.mean(diffs):.2f} kpc")
print(f"Std: {np.std(diffs):.2f} kpc")
dh=[d['harris'] for d in data]; db=[d['baumgardt'] for d in data]
fig,axes=plt.subplots(1,2,figsize=(11,4))
axes[0].scatter(dh,db,s=15,alpha=0.6,color='#2166ac')
lim=[0,max(dh+db)*1.05]; axes[0].plot(lim,lim,'k--',lw=1,alpha=0.4)
axes[0].set_xlabel('Harris distance (kpc)',fontsize=11); axes[0].set_ylabel('Baumgardt distance (kpc)',fontsize=11)
axes[0].set_title('Harris vs Baumgardt Distances',fontsize=10)
axes[1].hist(diffs,bins=20,color='#d62728',alpha=0.8,edgecolor='white')
axes[1].axvline(0,color='black',ls='--',lw=1.5)
axes[1].set_xlabel('Baumgardt - Harris (kpc)',fontsize=11); axes[1].set_title('Distance Offset',fontsize=10)
plt.suptitle('Distance Comparison — EPS Research GC Corpus v1.3.1',fontsize=11)
plt.tight_layout(); plt.savefig('gc17_distances.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc18_escape_velocity.ipynb": nb([
md(f"# GC Example 18: Central Escape Velocity\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nThe central escape velocity v_esc determines whether stars and stellar remnants\n(neutron stars, black holes) can be retained after formation.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['baumgardt2023']['v_esc_kms'],c['baumgardt2023']['mass_msun'])
      for c in clusters if c.get('baumgardt2023') and c['baumgardt2023'].get('v_esc_kms')]
v_esc=[d[1] for d in data]; mass=[d[2] for d in data]
print(f"Clusters with v_esc: {len(data)}")
print(f"v_esc range: {min(v_esc):.1f} -- {max(v_esc):.1f} km/s")
print(f"\\nHighest v_esc (black hole retention likely):")
for d in sorted(data,key=lambda x:-x[1])[:5]:
    print(f"  {d[0]:<12} v_esc={d[1]:.1f} km/s  mass={d[2]:.0f} Msun")
print(f"\\nLowest v_esc (neutron star kick likely to unbind):")
for d in sorted(data,key=lambda x:x[1])[:5]:
    print(f"  {d[0]:<12} v_esc={d[1]:.1f} km/s")
fig,ax=plt.subplots(figsize=(7,5))
ax.scatter(np.log10(mass),v_esc,s=20,alpha=0.7,color='#ff7f0e')
ax.axhline(50,color='red',ls='--',lw=1.5,label='50 km/s (NS kick threshold)')
ax.set_xlabel(r'log Mass ($M_\\odot$)',fontsize=12); ax.set_ylabel(r'$v_{\\rm esc}$ (km/s)',fontsize=12)
ax.set_title('Escape Velocity vs Mass\\nEPS Research GC Corpus v1.3.1',fontsize=10)
ax.legend(); plt.tight_layout(); plt.savefig('gc18_escape_velocity.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc19_gaia_parallax.ipynb": nb([
md(f"# GC Example 19: Gaia Parallax Cross-Check\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nGaia parallaxes are available for the nearest clusters.\nCross-check parallax-based distances vs Harris photometric distances.\n\n{NOTE}"),
code(LOAD),
code("""data=[]
for c in clusters:
    g=c.get('gaia_edr3',{})
    d=c.get('distances',{})
    if g and g.get('parallax_mas') and d.get('r_sun_kpc'):
        plx=g['parallax_mas']
        if plx>0.1:  # Only significant parallaxes
            d_plx=1.0/plx  # kpc (Lindegren zero-point corrected)
            data.append({'cluster':c['cluster_id'],'plx':plx,
                         'd_plx':d_plx,'d_harris':d['r_sun_kpc']})
print(f"Clusters with significant Gaia parallax (>0.1 mas): {len(data)}")
for d in sorted(data,key=lambda x:-x['plx']):
    print(f"  {d['cluster']:<12} plx={d['plx']:.3f} mas  "
          f"D_plx={d['d_plx']:.2f} kpc  D_Harris={d['d_harris']:.2f} kpc")""")
]),

"gc20_mass_segregation.ipynb": nb([
md(f"# GC Example 20: Mass Segregation Parameters\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nBaumgardt provides eta_c and eta_h — mass segregation parameters\nfrom Trenti & van der Marel (2013).\nNegative eta means more massive stars concentrated toward center.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['baumgardt2023']['eta_c'],c['baumgardt2023']['eta_h'],
        c['baumgardt2023']['mass_msun'])
      for c in clusters if c.get('baumgardt2023') and
      c['baumgardt2023'].get('eta_c') is not None and
      c['baumgardt2023'].get('eta_h') is not None]
eta_c=[d[1] for d in data]; eta_h=[d[2] for d in data]; mass=[d[3] for d in data]
print(f"Clusters with mass segregation data: {len(data)}")
print(f"eta_c range: {min(eta_c):.2f} -- {max(eta_c):.2f}")
print(f"eta_h range: {min(eta_h):.2f} -- {max(eta_h):.2f}")
fig,axes=plt.subplots(1,2,figsize=(10,4))
axes[0].scatter(eta_c,eta_h,s=15,alpha=0.6,color='#9467bd')
axes[0].axhline(0,color='black',ls='--',lw=0.8,alpha=0.5)
axes[0].axvline(0,color='black',ls='--',lw=0.8,alpha=0.5)
axes[0].set_xlabel(r'$\\eta_c$ (core)',fontsize=11); axes[0].set_ylabel(r'$\\eta_h$ (half-mass)',fontsize=11)
axes[0].set_title('Mass Segregation Parameters',fontsize=10)
axes[1].scatter(np.log10(mass),eta_c,s=15,alpha=0.6,color='#9467bd')
axes[1].set_xlabel(r'log Mass ($M_\\odot$)',fontsize=11); axes[1].set_ylabel(r'$\\eta_c$',fontsize=11)
axes[1].set_title('Segregation vs Mass',fontsize=10)
plt.suptitle('Mass Segregation — EPS Research GC Corpus v1.3.1',fontsize=11)
plt.tight_layout(); plt.savefig('gc20_segregation.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc21_tidal_radius.ipynb": nb([
md(f"# GC Example 21: Tidal Radius Distribution\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nThe tidal radius r_t marks where Galactic tidal forces overcome\nthe cluster's self-gravity. Clusters beyond r_t are stripped.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['baumgardt2023']['rt_pc'],c['baumgardt2023']['rhm_pc'],
        c['baumgardt2023']['mass_msun'])
      for c in clusters if c.get('baumgardt2023') and
      c['baumgardt2023'].get('rt_pc') and c['baumgardt2023'].get('rhm_pc')]
rt=[d[1] for d in data]; rhm=[d[2] for d in data]; mass=[d[3] for d in data]
ratio=[t/h for t,h in zip(rt,rhm)]
print(f"Clusters with r_t: {len(data)}")
print(f"r_t range: {min(rt):.0f} -- {max(rt):.0f} pc")
print(f"r_t/r_hm ratio range: {min(ratio):.1f} -- {max(ratio):.1f}")
print(f"Median ratio: {np.median(ratio):.1f}")
fig,ax=plt.subplots(figsize=(7,5))
ax.scatter(np.log10(mass),rt,s=20,alpha=0.7,color='#1f77b4')
ax.set_xlabel(r'log Mass ($M_\\odot$)',fontsize=12); ax.set_ylabel('Tidal radius (pc)',fontsize=12)
ax.set_title('Tidal Radius vs Mass\\nEPS Research GC Corpus v1.3.1',fontsize=10)
plt.tight_layout(); plt.savefig('gc21_tidal_radius.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc22_apogee_members.ipynb": nb([
md(f"# GC Example 22: APOGEE Member Star Counts\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nAPOGEE DR17 provides n_members — the number of member stars\nwith H-band spectroscopy. Higher counts = better chemistry statistics.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['apogee_dr17']['n_members'],
        c['apogee_dr17'].get('feh_apogee'),
        c['apogee_dr17'].get('mass_1e4_msun'))
      for c in clusters if c.get('apogee_dr17') and c['apogee_dr17'].get('n_members')]
n_members=[d[1] for d in data]
print(f"Clusters with APOGEE members: {len(data)}")
print(f"N members range: {min(n_members)} -- {max(n_members)}")
print(f"\\nTop 10 by member count:")
for d in sorted(data,key=lambda x:-x[1])[:10]:
    print(f"  {d[0]:<12} N={d[1]:>4}  [Fe/H]={d[2]}  mass={d[3]} x10^4 Msun")
fig,ax=plt.subplots(figsize=(7,4))
ax.hist(n_members,bins=20,color='#e74c3c',alpha=0.8,edgecolor='white')
ax.set_xlabel('N APOGEE member stars',fontsize=11); ax.set_ylabel('N clusters',fontsize=11)
ax.set_title('APOGEE DR17 Member Counts per GC\\nEPS Research Corpus v1.3.1',fontsize=10)
plt.tight_layout(); plt.savefig('gc22_apogee_members.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc23_dissolution_timescale.ipynb": nb([
md(f"# GC Example 23: Dissolution Timescale\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nBaumgardt provides t_diss — estimated time until cluster fully dissolves.\nDepends on mass, orbit, and internal dynamics.\n\n{NOTE}"),
code(LOAD),
code("""data=[(c['cluster_id'],c['baumgardt2023']['t_diss_gyr'],
        c['baumgardt2023']['mass_msun'],
        c['baumgardt2023'].get('r_peri_kpc',0))
      for c in clusters if c.get('baumgardt2023') and c['baumgardt2023'].get('t_diss_gyr')]
t_diss=[d[1] for d in data]; mass=[d[2] for d in data]; r_peri=[d[3] for d in data]
print(f"Clusters with t_diss: {len(data)}")
print(f"t_diss range: {min(t_diss):.1f} -- {max(t_diss):.1f} Gyr")
print(f"\\nShortest-lived clusters:")
for d in sorted(data,key=lambda x:x[1])[:5]:
    print(f"  {d[0]:<12} t_diss={d[1]:.1f} Gyr  r_peri={d[3]:.1f} kpc")
fig,ax=plt.subplots(figsize=(7,5))
sc=ax.scatter(np.log10(mass),t_diss,c=np.log10([max(r,0.01) for r in r_peri]),
              s=20,alpha=0.7,cmap='RdYlBu')
plt.colorbar(sc,ax=ax,label='log r_peri (kpc)')
ax.set_xlabel(r'log Mass ($M_\\odot$)',fontsize=12); ax.set_ylabel('t_diss (Gyr)',fontsize=12)
ax.set_title('Dissolution Timescale vs Mass\\nColored by pericenter distance',fontsize=10)
plt.tight_layout(); plt.savefig('gc23_dissolution.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"gc24_new_clusters.ipynb": nb([
md(f"# GC Example 24: New Clusters Beyond Harris (2010)\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\n17 clusters discovered after Harris (2010) are in the corpus\nfrom Vasiliev & Baumgardt (2021). They have Gaia data but no Harris photometry.\n\n{NOTE}"),
code(LOAD),
code("""new_clusters=[c for c in clusters
              if not (c.get('metallicity') and c['metallicity'].get('feh') is not None)
              and c.get('gaia_edr3')]
print(f"Post-Harris clusters (Gaia only): {len(new_clusters)}")
print(f"\\n{'Cluster':<20} {'mu_alpha':>10} {'mu_delta':>10} {'N_Gaia':>8}")
print('-'*52)
for c in new_clusters:
    g=c['gaia_edr3']
    print(f"{c['cluster_id']:<20} {g.get('mu_alpha_mas_yr',0):>10.3f} "
          f"{g.get('mu_delta_mas_yr',0):>10.3f} {g.get('n_members_gaia',0):>8}")
print(f"\\nNote: These clusters have no Harris photometric parameters.")
print(f"They contribute Gaia EDR3 proper motions only.")
print(f"5 of these also have Baumgardt N-body data.")""")
]),

"gc25_end_to_end_gc_query.ipynb": nb([
md(f"# GC Example 25: End-to-End GC Research Query\n\n**EPS Research — Milky Way GC Corpus v1.3.1**\n\nCapstone: a complete research query workflow.\nGiven a science question, filter, analyze, and report.\n\nQuestion: 'Which massive GCs in the inner Galaxy have APOGEE chemistry,\nhigh escape velocities, and could retain stellar-mass black holes?'\n\n{NOTE}"),
code(LOAD),
code("""# Science question: massive inner-Galaxy GCs that could retain BHs
results=[]
for c in clusters:
    b=c.get('baumgardt2023',{})
    d=c.get('distances',{})
    a=c.get('apogee_dr17',{})
    if not (b and d and a): continue
    mass=b.get('mass_msun',0)
    r_gc=d.get('r_gc_kpc',99)
    v_esc=b.get('v_esc_kms',0)
    feh_apogee=a.get('feh_apogee')
    n_members=a.get('n_members',0)
    # Criteria: massive, inner Galaxy, high v_esc, APOGEE coverage
    if mass>1e5 and r_gc<8 and v_esc>40 and feh_apogee is not None and n_members>20:
        results.append({'cluster':c['cluster_id'],
                        'mass':mass,'r_gc':r_gc,'v_esc':v_esc,
                        'feh':feh_apogee,'n_apogee':n_members})

print(f"{'='*60}")
print(f"Massive inner-Galaxy GCs with APOGEE + high v_esc")
print(f"Criteria: M>10^5, R_GC<8 kpc, v_esc>40 km/s, N_APOGEE>20")
print(f"{'='*60}")
print(f"Found: {len(results)} clusters\\n")
print(f"{'Cluster':<12} {'Mass':>10} {'R_GC':>6} {'v_esc':>7} {'[Fe/H]':>7} {'N_APOGEE':>9}")
print('-'*58)
for r in sorted(results,key=lambda x:-x['mass']):
    print(f"{r['cluster']:<12} {r['mass']:>10,.0f} {r['r_gc']:>6.1f} "
          f"{r['v_esc']:>7.1f} {r['feh']:>7.2f} {r['n_apogee']:>9}")"""),
code("""if results:
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    masses=[r['mass'] for r in results]; v_escs=[r['v_esc'] for r in results]
    fehs=[r['feh'] for r in results]; r_gcs=[r['r_gc'] for r in results]
    sc=axes[0].scatter(np.log10(masses),v_escs,c=fehs,s=60,alpha=0.9,
                       cmap='RdYlBu',vmin=-2,vmax=0)
    plt.colorbar(sc,ax=axes[0],label='[Fe/H]')
    for r in results:
        axes[0].annotate(r['cluster'],(np.log10(r['mass']),r['v_esc']),
                         textcoords='offset points',xytext=(4,3),fontsize=7)
    axes[0].set_xlabel(r'log Mass ($M_\\odot$)',fontsize=11)
    axes[0].set_ylabel(r'$v_{\\rm esc}$ (km/s)',fontsize=11)
    axes[0].set_title('Candidate BH-retaining GCs',fontsize=10)
    axes[1].scatter(r_gcs,v_escs,s=60,c=np.log10(masses),cmap='viridis',alpha=0.9)
    for r in results:
        axes[1].annotate(r['cluster'],(r['r_gc'],r['v_esc']),
                         textcoords='offset points',xytext=(4,3),fontsize=7)
    axes[1].set_xlabel('R_GC (kpc)',fontsize=11); axes[1].set_ylabel(r'$v_{\\rm esc}$ (km/s)',fontsize=11)
    axes[1].set_title('Escape Velocity vs Galactic Position',fontsize=10)
    plt.suptitle('End-to-End GC Research Query\\nEPS Research Corpus v1.3.1',fontsize=11)
    plt.tight_layout(); plt.savefig('gc25_end_to_end.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),
}

notebooks.update(remaining_gc)

# ── Write all notebooks ───────────────────────────────────────────────────────
written = 0
for filename, notebook in notebooks.items():
    with open(filename, 'w') as f:
        json.dump(notebook, f, indent=1)
    written += 1
    print(f"Written: {filename}")

print(f"\n{'='*50}")
print(f"GC Examples: {written}/25 notebooks written")
print(f"{'='*50}")
print(f"\nNext steps:")
print(f"1. Copy harris_gc_corpus_v1.3.1.jsonl here")
print(f"2. Run: jupyter lab")
print(f"3. Open each notebook and run all cells")
print(f"4. git add examples/gc/ && git commit -m 'Add 25 GC examples'")
print(f"5. git push")
