#!/usr/bin/env python3
"""
make_figures_v3.py
Corrected figure generation for RAG08 R2 submission.
Flynn, D.C. (2026) — Rotation Curve Corpus v7.0

Figures:
  Fig 1: DDO161 SPARC Tier 1 — unchanged, correct as submitted
  Fig 2: WALLABY J165901-601241 — beam-smearing caution annotated by
          spatial resolution (30 arcsec beam at galaxy distance), not
          by a fixed Vrot threshold on the Y-axis
  Fig 3: Corpus population overview — panel (a) stacked Vrot histogram
          (all 4 surveys), panel (b) log Mbar proxy vs Vrot_max scatter
          (baryonic mass on X-axis as requested by R1)
  Fig 4: Four-survey BTFR — already corrected as ex19; regenerated here
          for consistency

Run from the directory containing /home/david/Downloads/rotation_curve_corpus_v7.json
or update CORPUS_PATH below.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Config ─────────────────────────────────────────────────────────
CORPUS_PATH = '/home/david/Downloads/rotation_curve_corpus_v7.json'
OUT_DIR     = './'          # change if you want output elsewhere
DPI         = 300

# ── Style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':      'serif',
    'font.size':        11,
    'axes.linewidth':   0.8,
    'xtick.direction':  'in',
    'ytick.direction':  'in',
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'figure.dpi':       150,
})

C_OBS    = '#2166AC'
C_BAR    = '#B2182B'
C_OMEGA  = '#4DAF4A'
C_KEPLER = '#FF7F00'
C_SPARC  = '#2166AC'
C_THINGS = '#D6604D'
C_LT     = '#4393C3'
C_WAL    = '#B2182B'
C_T1     = '#333333'
C_T2     = '#D6604D'
G_KPC    = 4.302e-6   # kpc (km/s)^2 Msun^-1

# ── Load corpus ─────────────────────────────────────────────────────
print("Loading corpus...")
with open(CORPUS_PATH) as f:
    corpus = json.load(f)
galaxies = corpus['galaxies']
print(f"  {len(galaxies)} galaxies loaded.")


# ══════════════════════════════════════════════════════════════════════
# FIGURE 1: DDO161 — SPARC Tier 1  (unchanged from v7.0)
# ══════════════════════════════════════════════════════════════════════
print("Figure 1...")

g1   = next(g for g in galaxies if g['galaxy'] == 'DDO161')
d    = g1['data']
R    = np.array([p['Rad']   for p in d])
Vobs = np.array([p['Vobs']  for p in d])
errV = np.array([p['errV']  for p in d])
Vgas = np.array([p['Vgas']  for p in d])
Vdisk= np.array([p['Vdisk'] for p in d])
Vbul = np.array([p['Vbul']  for p in d])

Vbar = np.where(Vgas < 0,
                -np.sqrt(Vgas**2 + Vdisk**2 + Vbul**2),
                 np.sqrt(Vgas**2 + Vdisk**2 + Vbul**2))
omega = 4.6904
V_adj = Vobs - R * omega
R1, V1 = R[0], Vobs[0]
VKe = V1 * (R / R1) * np.sqrt((R1 / R)**3)

fig1, ax1 = plt.subplots(figsize=(7, 4.5))
ax1.errorbar(R, Vobs, yerr=errV, fmt='o', ms=4, color=C_OBS,
             ecolor='#AAAAAA', elinewidth=0.8, capsize=2,
             label=r'$V_{\rm obs}$ (SPARC)', zorder=3)
ax1.plot(R, Vbar,  's-', ms=3, color=C_BAR,    lw=1.2,
         label=r'$V_{\rm bar}$ (quadrature, $\Upsilon=1$)', zorder=2)
ax1.plot(R, V_adj, '^-', ms=3, color=C_OMEGA,  lw=1.2,
         label=r'$V_{\rm obs}-R\omega$ ($\omega=4.69$)', zorder=2)
ax1.plot(R, VKe,   '--',       color=C_KEPLER, lw=1.0, alpha=0.7,
         label=r'Expected Kepler', zorder=1)
ax1.set_xlabel('Radius (kpc)')
ax1.set_ylabel('Velocity (km/s)')
ax1.set_title('DDO 161 — SPARC Tier 1, loaded from corpus JSON',
              fontsize=12, fontweight='bold')
ax1.legend(fontsize=9, loc='lower right', framealpha=0.9)
ax1.set_xlim(0, R.max() * 1.05)
ax1.set_ylim(0, None)
ax1.grid(True, alpha=0.2)
fig1.tight_layout()
fig1.savefig(OUT_DIR + 'fig1_ddo161.png', dpi=DPI, bbox_inches='tight')
print("  fig1_ddo161.png saved.")


# ══════════════════════════════════════════════════════════════════════
# FIGURE 2: WALLABY J165901-601241 — Tier 2
# CORRECTED: beam-smearing caution shown as minimum resolved radius
# (R_beam = beam_arcsec * distance_mpc * 1000 * pi/648000 / 2)
# rather than a fixed Vrot < 50 km/s threshold on the Y-axis.
# ══════════════════════════════════════════════════════════════════════
print("Figure 2...")

g2  = next(g for g in galaxies if g['galaxy'] == 'WALLABY_J165901-601241')
rc  = g2['rotation_curve']
R_w = np.array([p['rad_kpc']   for p in rc])
V_w = np.array([p['vrot_kms']  for p in rc])

D_mpc      = float(g2['distance_mpc'])
beam_arcsec = float(g2.get('beam_arcsec', 30.0))   # ASKAP FWHM = 30"
# Beam radius in kpc: half the beam FWHM
R_beam_kpc = 0.5 * beam_arcsec * D_mpc * 1000.0 * np.pi / 648000.0

fig2, ax2 = plt.subplots(figsize=(7, 4.5))
ax2.plot(R_w, V_w, 'o-', ms=4, color=C_WAL, lw=1.2,
         label=r'$V_{\rm rot}$ (3DBarolo)', zorder=3)

# Shade the beam-smearing affected zone: R < R_beam
ax2.axvspan(0, R_beam_kpc, color='#FFDDDD', alpha=0.5, zorder=0)
ax2.axvline(R_beam_kpc, color='#CC0000', lw=0.8, ls='--', alpha=0.7, zorder=1)
ax2.text(R_beam_kpc * 1.05, V_w.max() * 0.92,
         f'Beam radius\n({beam_arcsec:.0f}$^{{\\prime\\prime}}$ FWHM)\n'
         f'$R_{{\\rm beam}}={R_beam_kpc:.1f}$ kpc',
         fontsize=8, color='#CC0000', alpha=0.9, va='top')

# Also note Vrot < 50 km/s caution as a horizontal reference line
ax2.axhline(50, color='#888888', lw=0.7, ls=':', alpha=0.5, zorder=1)
ax2.text(R_w.max() * 0.97, 52,
         r'$V_{\rm rot}=50$ km/s (beam-smearing caution)',
         fontsize=7.5, color='#888888', ha='right', alpha=0.8)

ax2.text(0.03, 0.95,
         f"D = {D_mpc:.1f} Mpc\n"
         f"inc = {g2['inc_deg']:.1f}$^{{\\circ}}$\n"
         f"{len(rc)} rings",
         transform=ax2.transAxes, fontsize=9, va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

ax2.set_xlabel('Radius (kpc)')
ax2.set_ylabel('Velocity (km/s)')
ax2.set_title('WALLABY J165901$-$601241 — Tier 2, loaded from corpus JSON',
              fontsize=12, fontweight='bold')
ax2.legend(fontsize=9, loc='lower right', framealpha=0.9)
ax2.set_xlim(0, R_w.max() * 1.05)
ax2.set_ylim(0, V_w.max() * 1.2)
ax2.grid(True, alpha=0.2)
fig2.tight_layout()
fig2.savefig(OUT_DIR + 'fig2_wallaby.png', dpi=DPI, bbox_inches='tight')
print("  fig2_wallaby.png saved.")


# ══════════════════════════════════════════════════════════════════════
# FIGURE 3: Corpus Population Overview
# CORRECTED: panel (b) shows log(Mbar proxy) vs Vrot_max
# (baryonic mass on X-axis as requested by Reviewer 1)
# ══════════════════════════════════════════════════════════════════════
print("Figure 3...")

def sparc_logmbar(g):
    """log10(Mbar/Msun) from SPARC decomposition at outermost ring."""
    m2l = g.get('m2l_disk')
    if not m2l or not g.get('data'):
        return None
    m2l = float(m2l)
    ring  = g['data'][-1]
    R     = ring.get('Rad');   Vobs = ring.get('Vobs')
    Vgas  = float(ring.get('Vgas',  0))
    Vdisk = float(ring.get('Vdisk', 0))
    Vbul  = float(ring.get('Vbul',  0))
    if not R or not Vobs:
        return None
    R = float(R)
    Mgas  = 1.33 * max(Vgas, 0)**2 * R / G_KPC
    Mstar = m2l  * Vdisk**2         * R / G_KPC
    Mbul  =        Vbul**2          * R / G_KPC
    Mbar  = Mgas + Mstar + Mbul
    return np.log10(Mbar) if Mbar > 0 else None

def get_vmax(g):
    v = g.get('vrot_max_kms') or g.get('Vobs_max_kms')
    if v:
        try: return float(v)
        except: pass
    if g.get('data'):
        vcol = 'Vrot' if 'Vrot' in (g.get('columns') or {}) else 'Vobs'
        vals = [float(r[vcol]) for r in g['data'] if r.get(vcol)]
        if vals: return max(vals)
    if g.get('rotation_curve'):
        vals = [float(r['vrot_kms']) for r in g['rotation_curve'] if r.get('vrot_kms')]
        if vals: return max(vals)
    return None

vmax_by_survey = {s: [] for s in ('SPARC','THINGS','LITTLE_THINGS','WALLABY')}
logmbar_list, vmax_list, tier_list = [], [], []

for g in galaxies:
    s = g['survey']
    pts = g.get('data') or g.get('rotation_curve')
    if not pts:
        continue
    vmax = get_vmax(g)
    if not vmax or vmax <= 0:
        continue
    vmax_by_survey.setdefault(s, []).append(vmax)
    # Mbar proxy
    if s == 'SPARC':
        lm = sparc_logmbar(g)
    else:
        lm = 4.0 * np.log10(vmax) + np.log10(47.0)
    if lm is None:
        continue
    logmbar_list.append(lm)
    vmax_list.append(vmax)
    tier_list.append(g.get('quality_tier', 2))

logmbar_arr = np.array(logmbar_list)
vmax_arr    = np.array(vmax_list)
tier_arr    = np.array(tier_list)

fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 4.5))

# Panel (a): stacked Vrot_max histogram — all 4 surveys
bins   = np.linspace(0, 350, 36)
bottom = np.zeros(len(bins) - 1)
for s_name, color in [('SPARC', C_SPARC), ('THINGS', C_THINGS),
                       ('LITTLE_THINGS', C_LT), ('WALLABY', C_WAL)]:
    vals = vmax_by_survey.get(s_name, [])
    if not vals:
        continue
    counts, _ = np.histogram(vals, bins=bins)
    label = s_name.replace('_', ' ') + f' ({len(vals)})'
    ax3a.bar(bins[:-1], counts, width=np.diff(bins), bottom=bottom,
             color=color, alpha=0.85, label=label,
             edgecolor='white', linewidth=0.3)
    bottom += counts
ax3a.set_xlabel(r'$V_{\rm rot,max}$ (km s$^{-1}$)')
ax3a.set_ylabel('Number of galaxies')
ax3a.set_title('(a) Peak rotation velocity — all four surveys',
               fontsize=11, fontweight='bold')
ax3a.legend(fontsize=8, loc='upper right', framealpha=0.9)
ax3a.set_xlim(0, 350)
ax3a.grid(True, alpha=0.2, axis='y')

# Panel (b): log Mbar vs Vrot_max by tier  [CORRECTED axis]
mask1 = tier_arr == 1
mask2 = tier_arr == 2
ax3b.scatter(np.log10(vmax_arr[mask1]), logmbar_arr[mask1],
             s=15, c=C_T1, alpha=0.6, edgecolors='none', zorder=2,
             label=f'Tier 1 ({mask1.sum()})')
ax3b.scatter(np.log10(vmax_arr[mask2]), logmbar_arr[mask2],
             s=15, c=C_T2, alpha=0.6, edgecolors='none', zorder=2,
             label=f'Tier 2 ({mask2.sum()})')
ax3b.set_xlabel(r'$\log_{10}\,V_{\rm rot,max}$ (km s$^{-1}$)')
ax3b.set_ylabel(r'$\log_{10}\,M_{\rm bar}$ ($M_\odot$)')
ax3b.set_title('(b) Baryonic mass vs rotation velocity by tier',
               fontsize=11, fontweight='bold')
ax3b.legend(fontsize=9, loc='upper left', framealpha=0.9)
ax3b.grid(True, alpha=0.2)
fig3.tight_layout()
fig3.savefig(OUT_DIR + 'fig3_population.png', dpi=DPI, bbox_inches='tight')
print("  fig3_population.png saved.")


# ══════════════════════════════════════════════════════════════════════
# FIGURE 4: Four-survey BTFR  (same as ex19 output)
# ══════════════════════════════════════════════════════════════════════
print("Figure 4...")

results = {s: [] for s in ('SPARC','THINGS','LITTLE_THINGS','WALLABY')}
for g in galaxies:
    s = g['survey']
    if s not in results:
        continue
    if s == 'SPARC':
        lm = sparc_logmbar(g)
        V  = get_vmax(g)
        if lm and V and V > 0:
            results['SPARC'].append((V, lm))
    else:
        vmax = get_vmax(g)
        if not vmax or vmax <= 0:
            continue
        results[s].append((vmax, 4.0 * np.log10(vmax) + np.log10(47.0)))

COLORS4  = {'SPARC':'#1f77b4','THINGS':'#ff7f0e',
            'LITTLE_THINGS':'#2ca02c','WALLABY':'#d62728'}
MARKERS4 = {'SPARC':'o','THINGS':'s','LITTLE_THINGS':'^','WALLABY':'D'}

fig4, ax4 = plt.subplots(figsize=(8, 6))
for s in ('SPARC','THINGS','LITTLE_THINGS','WALLABY'):
    pts = results[s]
    if not pts:
        continue
    vs, ms = zip(*pts)
    label = s.replace('_',' ') + f' (n={len(pts)})'
    ax4.scatter(np.log10(vs), ms, s=25, alpha=0.7, edgecolors='none',
                color=COLORS4[s], marker=MARKERS4[s], label=label)

v_ref = np.logspace(0.8, 2.7, 200)
ax4.plot(np.log10(v_ref), 4*np.log10(v_ref)+np.log10(47),
         'k--', lw=1.2, alpha=0.55, label='McGaugh (2012) calibration')

ax4.set_xlabel(r'$\log_{10}\,V_{\rm flat}$ (km s$^{-1}$)', fontsize=13)
ax4.set_ylabel(r'$\log_{10}\,M_{\rm bar}$ ($M_\odot$)',    fontsize=13)
ax4.set_title('Baryonic Tully–Fisher Relation\n'
              'Unified HI Corpus v7.0 — SPARC · THINGS · LITTLE THINGS · WALLABY DR2',
              fontsize=11)
ax4.legend(fontsize=9, framealpha=0.9)
ax4.set_xlim(0.9, 2.8)
ax4.set_ylim(6.5, 12.5)
ax4.grid(True, alpha=0.2)
fig4.tight_layout()
fig4.savefig(OUT_DIR + 'fig4_btfr.png', dpi=DPI, bbox_inches='tight')
print("  fig4_btfr.png saved.")

print("\nAll figures complete.")
