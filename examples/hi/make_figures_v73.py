#!/usr/bin/env python3
"""
make_figures_v73.py -- figures for Flynn, Astron. Comput. 58 (2027) 101179 (as corrected),
generated from the Unified Galaxy Rotation Curve Corpus v7.3.

Usage:  python make_figures_v73.py rotation_curve_corpus_v7.json [output_dir]

Fig 1  DDO 161: V_obs with errors; V_bar from Eq. 1 at Upsilon = 1; V_obs - R*omega with omega from Eq. 6 of
       Flynn & Cannaliato (2025) in km s^-1 kpc^-1; expected-Kepler baseline.
Fig 2  WALLABY J165901-601241: WKAPP optimised rotation curve (WALLABY DR2) with e_Vrot.
Fig 3  (a) V_rot,max histogram by survey, 0-400 km/s; (b) M_bar vs V by quality tier.
Fig 4  M_bar vs V for all four surveys with the McGaugh (2012) calibration line.

Velocity V (Figs 3b, 4): SPARC = velocity at the outermost ring (Vobs); THINGS, LITTLE THINGS, WALLABY = peak
per-ring velocity. These are the definitions used in the published figures.
M_bar  SPARC: (Vgas^2 + Y_disk*Vdisk^2 + Vbul^2) * R_out / G at the outermost ring (spherical approximation),
       Y_disk = corpus m2l_disk (maximum-disk value), Y_bul = 1; SPARC Vgas already includes the 1.33 helium
       factor (Lelli et al. 2016), so no further factor is applied.
       THINGS / LITTLE THINGS / WALLABY: V^4 proxy, log M = 4 log V + log 47 (McGaugh 2012). These points lie on
       the calibration line by construction and do not test the BTFR.
Requires: numpy, matplotlib.
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

G_KPC = 4.302e-6
L47 = np.log10(47.0)
SURV = ('SPARC', 'THINGS', 'LITTLE_THINGS', 'WALLABY')
COL = {'SPARC': '#2166AC', 'THINGS': '#D6604D', 'LITTLE_THINGS': '#4393C3', 'WALLABY': '#B2182B'}
MRK = {'SPARC': 'o', 'THINGS': 's', 'LITTLE_THINGS': '^', 'WALLABY': 'D'}
VLAB = r'$\log_{10} V$ (km s$^{-1}$): SPARC outermost ring; others peak'
plt.rcParams.update({'font.family': 'serif', 'font.size': 11, 'axes.linewidth': 0.8,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'figure.dpi': 150})

def vel(p): return p['Vobs'] if 'Vobs' in p else p['Vrot']
def vrot_max(g):
    d = g.get('data') or []
    return max(float(vel(p)) for p in d) if d else None
def v_pub(g):
    d = g.get('data') or []
    if not d: return None
    if g['survey'] == 'SPARC':
        rmax = max(p['Rad'] for p in d); return float(np.mean([vel(p) for p in d if p['Rad'] == rmax]))
    return vrot_max(g)
def sparc_logm(g):
    m2l, d = g.get('m2l_disk'), g.get('data')
    if not m2l or not d: return None
    r = max(d, key=lambda p: p['Rad']); R = float(r['Rad'])
    M = (max(float(r.get('Vgas', 0)), 0)**2 + float(m2l)*float(r.get('Vdisk', 0))**2 + float(r.get('Vbul', 0))**2) * R / G_KPC
    return np.log10(M) if M > 0 else None
def mass_points(galaxies):
    pts = []
    for g in galaxies:
        s = g.get('survey'); v = v_pub(g)
        if s not in SURV or not v or v <= 0: continue
        m = sparc_logm(g) if s == 'SPARC' else 4*np.log10(v) + L47
        if m is not None: pts.append(dict(galaxy=g['galaxy'], survey=s, tier=g.get('quality_tier'), v=v, logm=m))
    return pts
def vbar_eq1(Vgas, Vdisk, Vbul, Y=1.0):
    s = Vgas*np.abs(Vgas) + Y*Vdisk*np.abs(Vdisk) + Vbul*np.abs(Vbul)
    return np.sign(s)*np.sqrt(np.abs(s))
def omega_eq6(R, V): return V[-1]/R[-1] - (V[0]/R[0])*(R[0]/R[-1])**1.5
def save(fig, out, name):
    for ext, kw in (('png', {'dpi': 300}), ('pdf', {})): fig.savefig(os.path.join(out, f"{name}.{ext}"), bbox_inches='tight', **kw)
    plt.close(fig)

def main(path, out):
    os.makedirs(out, exist_ok=True)
    C = json.load(open(path, encoding='utf-8')); G = C['galaxies']
    man = {'corpus': os.path.basename(path), 'corpus_version': C.get('metadata', {}).get('version')}
    g = next(x for x in G if x['galaxy'] == 'DDO161' and x['survey'] == 'SPARC'); d = g['data']
    R, Vobs, errV, Vg, Vd, Vb = (np.array([p[k] for p in d], float) for k in ('Rad', 'Vobs', 'errV', 'Vgas', 'Vdisk', 'Vbul'))
    Vbar = vbar_eq1(Vg, Vd, Vb); w = omega_eq6(R, Vobs); VKe = Vobs[0]*(R/R[0])*np.sqrt((R[0]/R)**3)
    f, a = plt.subplots(figsize=(7, 4.5))
    a.errorbar(R, Vobs, yerr=errV, fmt='o', ms=4, color='#2166AC', ecolor='#AAAAAA', elinewidth=0.8, capsize=2, label=r'$V_{\rm obs}$ (SPARC)')
    a.plot(R, Vbar, 's-', ms=3, color='#B2182B', lw=1.2, label=r'$V_{\rm bar}$ (Eq. 1, $\Upsilon=1$)')
    a.plot(R, Vobs - R*w, '^-', ms=3, color='#4DAF4A', lw=1.2, label=rf'$V_{{\rm obs}}-R\omega$ ($\omega={w:.2f}$ km s$^{{-1}}$ kpc$^{{-1}}$)')
    a.plot(R, VKe, '--', color='#FF7F00', lw=1.0, alpha=0.7, label='Expected Kepler (Eq. 5)')
    a.set(xlabel='Radius (kpc)', ylabel='Velocity (km/s)', xlim=(0, R.max()*1.05), ylim=(0, None))
    a.set_title('DDO 161 (SPARC Tier 1), corpus v7.3'); a.legend(fontsize=8.5, loc='lower right'); a.grid(alpha=0.2)
    save(f, out, 'fig1_ddo161'); man['fig1'] = dict(omega_kms_kpc=round(w, 6), omega_rad_gyr=round(w*1.0227, 4), n=len(R))
    wal = next(x for x in G if x['galaxy'] == 'WALLABY_J165901-601241'); rc = sorted(wal['data'], key=lambda p: p['Rad'])
    Rw = np.array([p['Rad'] for p in rc]); Vw = np.array([p['Vrot'] for p in rc]); Ew = np.array([p.get('e_Vrot', 0) or 0 for p in rc])
    f, a = plt.subplots(figsize=(7, 4.5))
    a.errorbar(Rw, Vw, yerr=Ew, fmt='o-', ms=4, color='#B2182B', ecolor='#E0A0A0', lw=1.2, capsize=2, label=r'$V_{\rm rot}$ (WKAPP, DR2) $\pm\,e_{V}$')
    a.axhspan(0, 50, color='#FFEEEE', alpha=0.5); a.axhline(50, color='#CC0000', lw=0.6, ls=':', alpha=0.5)
    a.text(0.03, 0.95, f"D = {wal['distance_mpc']:.1f} Mpc\ninc = {wal['inc_deg']:.1f} deg\n{len(rc)} rings",
           transform=a.transAxes, fontsize=9, va='top', bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
    a.set(xlabel='Radius (kpc)', ylabel='Velocity (km/s)', xlim=(0, Rw.max()*1.05), ylim=(0, None))
    a.set_title('WALLABY J165901-601241 (Tier 2), corpus v7.3'); a.legend(fontsize=9, loc='lower right'); a.grid(alpha=0.2)
    save(f, out, 'fig2_wallaby'); man['fig2'] = dict(rings=len(rc), r_max=round(float(Rw.max()), 2), vmax=round(float(Vw.max()), 2), e_vrot_median=round(float(np.median(Ew)), 2))
    vmax = {s: [vrot_max(x) for x in G if x['survey'] == s and x.get('data')] for s in SURV}; P = mass_points(G)
    f, (a3, b3) = plt.subplots(1, 2, figsize=(12, 4.5)); bins = np.arange(0, 410, 10); bottom = np.zeros(len(bins)-1)
    for s in SURV:
        c, _ = np.histogram(vmax[s], bins=bins)
        a3.bar(bins[:-1], c, width=10, bottom=bottom, align='edge', color=COL[s], alpha=0.8, label=f"{s.replace('_', ' ')} ({len(vmax[s])})", edgecolor='white', lw=0.3); bottom += c
    a3.set(xlabel=r'$V_{\rm rot,max}$ (km/s)', ylabel='Number of galaxies', xlim=(0, 400)); a3.set_title('(a) Peak rotation velocity distribution'); a3.legend(fontsize=8); a3.grid(alpha=0.2, axis='y')
    for t, c, lab in ((1, '#333333', 'Tier 1'), (2, '#D6604D', 'Tier 2')):
        q = [p for p in P if p['tier'] == t]
        b3.scatter([np.log10(p['v']) for p in q], [p['logm'] for p in q], s=12, c=c, alpha=0.6, edgecolors='none', label=f"{lab} ({len(q)})")
    b3.set(xlabel=VLAB, ylabel=r'$\log_{10} M_{\rm bar}$ ($M_\odot$)'); b3.set_title('(b) Baryonic mass vs. velocity by tier'); b3.legend(fontsize=9, loc='upper left'); b3.grid(alpha=0.2)
    save(f, out, 'fig3_population')
    allv = [v for s in SURV for v in vmax[s]]
    man['fig3'] = dict(n_hist=len(allv), n_above_350=int(sum(v > 350 for v in allv)), vmax_range=[round(min(allv), 2), round(max(allv), 2)], tiers={t: sum(p['tier'] == t for p in P) for t in (1, 2)})
    f, a = plt.subplots(figsize=(8, 6))
    lab = {'SPARC': r'SPARC: $M_{\rm bar}$ from decomposition', 'THINGS': r'THINGS: $V^4$ proxy', 'LITTLE_THINGS': r'LITTLE THINGS: $V^4$ proxy', 'WALLABY': r'WALLABY DR2: $V^4$ proxy'}
    for s in SURV:
        q = [p for p in P if p['survey'] == s]
        a.scatter([np.log10(p['v']) for p in q], [p['logm'] for p in q], s=22, alpha=0.7, edgecolors='none', color=COL[s], marker=MRK[s], label=f"{lab[s]} (n={len(q)})")
    x = np.linspace(0.9, 2.8, 100); a.plot(x, 4*x + L47, 'k--', lw=1.1, alpha=0.55, label='McGaugh (2012) calibration')
    a.set(xlabel=VLAB, ylabel=r'$\log_{10} M_{\rm bar}$ ($M_\odot$)', xlim=(0.9, 2.8), ylim=(5.5, 12.5)); a.set_title('Baryonic mass vs. velocity, corpus v7.3'); a.legend(fontsize=8.5); a.grid(alpha=0.2)
    save(f, out, 'fig4_btfr')
    vis = sum(1 for p in P if 0.9 <= np.log10(p['v']) <= 2.8 and 5.5 <= p["logm"] <= 12.5)
    man['fig4'] = {**{s: sum(p['survey'] == s for p in P) for s in SURV}, 'points_inside_axes': vis, 'points_total': len(P)}
    json.dump(man, open(os.path.join(out, 'figures_manifest.json'), 'w'), indent=2); print(json.dumps(man, indent=2))

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '.')
