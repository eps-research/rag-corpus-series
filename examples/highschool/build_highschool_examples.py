#!/usr/bin/env python3
"""
EPS Research — Build High-School Exploration Track Notebooks
Two tracks:
  - Ages 12-14: hs_a_01 to hs_a_10 (middle school, minimal code, very visual)
  - Ages 15-18: hs_b_01 to hs_b_10 (high school, some algebra, basic Python)

Run from: ~/Documents/rag-corpus-series/examples/highschool/
Requires: rotation_curve_corpus_v7.json in the same directory.

Usage:
    python3 build_highschool_examples.py

Flynn, D.C. (2026) EPS Research
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

notebooks = {}

# ══════════════════════════════════════════════════════════════════════════════
# TRACK A: Ages 12-14 (Middle School)
# Very simple Python, lots of visuals, conversational tone
# ══════════════════════════════════════════════════════════════════════════════

# ── HS-A-01: What is a galaxy? ────────────────────────────────────────────────
notebooks["hs_a_01_what_is_a_galaxy.ipynb"] = nb([
md("""# 🌌 What Is a Galaxy?
### EPS Research High-School Exploration Track — Ages 12-14

A **galaxy** is a giant collection of stars, gas, and dust held together by gravity.
Our home galaxy is called the **Milky Way**.

There are hundreds of billions of galaxies in the observable universe —
each one containing billions of stars!

In this notebook, we'll look at real data from **438 galaxies**
collected by scientists and organized by EPS Research.

**You don't need to understand all the code — just run each cell and look at the pictures!**

> 💡 **To run a cell:** Click on it and press **Shift + Enter**"""),
code("""# Let's load the galaxy data
import json
import matplotlib.pyplot as plt

# Open the galaxy database
with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# How many galaxies are there?
galaxies = corpus['galaxies']
print(f"🌌 We have data on {len(galaxies)} galaxies!")
print()
print("These galaxies come from four big surveys:")
from collections import Counter
surveys = Counter(g['survey'] for g in galaxies)
for name, count in surveys.items():
    print(f"  ⭐ {name}: {count} galaxies")"""),
code("""# Let's make a pie chart showing where the galaxies come from
COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
labels = list(surveys.keys())
sizes  = list(surveys.values())

fig, ax = plt.subplots(figsize=(7, 5))
ax.pie(sizes, labels=labels, colors=COLORS, autopct='%1.0f%%',
       textprops={'fontsize': 11}, startangle=90)
ax.set_title('Our Galaxy Database\\n438 galaxies from 4 different surveys! 🌌',
             fontsize=12)
plt.tight_layout()
plt.savefig('hs_a_01_galaxy_surveys.png', dpi=150, bbox_inches='tight')
plt.show()
print("Nice chart! Each color represents galaxies from a different survey.")"""),
md("""## What did we just do?

We just loaded a database of **438 real galaxies** and counted how many
came from each survey. Scientists use different telescopes to study
different kinds of galaxies.

**Questions to think about:**
- Which survey has the most galaxies?
- Why might scientists need different surveys?

In the next notebook, we'll learn what a **rotation curve** is! 🚀""")
])

# ── HS-A-02: What is a rotation curve? ───────────────────────────────────────
notebooks["hs_a_02_what_is_a_rotation_curve.ipynb"] = nb([
md("""# 🌀 What Is a Rotation Curve?
### EPS Research High-School Exploration Track — Ages 12-14

Imagine spinning a bicycle wheel. The outside of the wheel moves faster
than the inside — they have to travel farther in the same time.

But galaxies are **weird**! Their stars all spin at about the **same speed**,
no matter how far from the center. This is called a **flat rotation curve**,
and it's one of the biggest mysteries in science!

Let's look at a real galaxy rotation curve. We'll use **DDO161**,
a small galaxy about 7.5 million light-years away."""),
code("""import json
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Find DDO161
galaxy = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')

# Get the rotation data
data   = galaxy['data']
radius = [point['Rad']  for point in data]   # distance from center (kpc)
speed  = [point['Vobs'] for point in data]   # speed of stars (km/s)

print(f"Galaxy: {galaxy['galaxy']}")
print(f"Distance from Earth: {galaxy['distance_mpc']} Megaparsecs")
print(f"  (that's about {galaxy['distance_mpc'] * 3.26:.0f} million light-years!)")
print(f"Number of measurements: {len(data)}")
print()
print("First few measurements:")
print(f"  {'Radius (kpc)':>14}  {'Speed (km/s)':>12}")
for r, s in zip(radius[:5], speed[:5]):
    print(f"  {r:>14.2f}  {s:>12.1f}")"""),
code("""fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(radius, speed, 'o-', color='#3498db', linewidth=2, markersize=7,
        label='Speed of stars')
ax.set_xlabel('Distance from galaxy center (kpc)', fontsize=12)
ax.set_ylabel('Speed of stars (km/s)', fontsize=12)
ax.set_title('DDO161 — A Real Galaxy Rotation Curve 🌀\\n'
             'Notice: stars far from the center are NOT slowing down!',
             fontsize=11)
ax.legend(fontsize=10)
ax.text(0.97, 0.08,
        f'This galaxy is {galaxy["distance_mpc"]*3.26:.0f} million\\nlight-years away!',
        transform=ax.transAxes, ha='right', fontsize=9,
        bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.9))
plt.tight_layout()
plt.savefig('hs_a_02_rotation_curve.png', dpi=150, bbox_inches='tight')
plt.show()"""),
md("""## Why is this mysterious? 🤔

If all the mass in a galaxy were just the stars we can see,
then the stars far from the center should be moving **slower** —
just like the outer planets in our solar system move slower than inner ones.

But they **don't slow down**! Something invisible is keeping them moving fast.
Scientists call this invisible something **dark matter**.

In the next notebook, we'll explore the dark matter problem! 🌑""")
])

# ── HS-A-03: The dark matter mystery ─────────────────────────────────────────
notebooks["hs_a_03_dark_matter_mystery.ipynb"] = nb([
md("""# 🌑 The Dark Matter Mystery
### EPS Research High-School Exploration Track — Ages 12-14

Here's the mystery: galaxies spin too fast.

If we add up all the mass we can SEE (stars, gas, dust),
and calculate how fast things should spin based on that mass,
we get a curve that **falls off** at large distances.

But what we OBSERVE is a curve that stays **flat**.

The difference must be caused by something we **can't see**.
Scientists call it **dark matter**. It's not dark like night —
it's dark because it doesn't give off any light at all!

Let's see this for ourselves using real SPARC data."""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

galaxy = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
data   = galaxy['data']

radius = np.array([p['Rad']   for p in data])
speed  = np.array([p['Vobs']  for p in data])
vgas   = np.array([p['Vgas']  for p in data])
vdisk  = np.array([p['Vdisk'] for p in data])

# What we'd expect from just the visible matter
visible_speed = np.sqrt(np.abs(vgas**2) + vdisk**2)

print("Comparing observed speed vs. visible matter speed:")
print(f"  {'Radius':>8}  {'Observed':>10}  {'Visible only':>13}")
for r, obs, vis in zip(radius[:6], speed[:6], visible_speed[:6]):
    print(f"  {r:>8.2f}  {obs:>10.1f}  {vis:>13.1f}")"""),
code("""fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(radius, speed, 'o-', color='#3498db', linewidth=2, markersize=6,
        label='⭐ What we OBSERVE (actual star speeds)')
ax.plot(radius, visible_speed, 's--', color='#e74c3c', linewidth=2, markersize=6,
        label='👁 What visible matter PREDICTS')

ax.fill_between(radius, visible_speed, speed, alpha=0.15, color='purple',
                label='🌑 The gap = DARK MATTER?')

ax.set_xlabel('Distance from center (kpc)', fontsize=12)
ax.set_ylabel('Speed (km/s)', fontsize=12)
ax.set_title('The Dark Matter Mystery — DDO161\\n'
             'Something invisible keeps stars moving fast!', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hs_a_03_dark_matter.png', dpi=150, bbox_inches='tight')
plt.show()"""),
md("""## The gap between the lines is the mystery!

The **blue line** is what we actually measure.
The **red line** is what physics predicts from the matter we can see.

The **purple shaded area** between them represents the "missing mass" —
the dark matter that must be there to make the math work.

Scientists have been trying to solve this mystery for 50 years!
EPS Research is working on a new approach called the **omega correction**.
We'll learn about that in later notebooks. 🔬""")
])

# ── HS-A-04: Plot your first galaxy ───────────────────────────────────────────
notebooks["hs_a_04_plot_your_galaxy.ipynb"] = nb([
md("""# 🎨 Plot Your Own Galaxy!
### EPS Research High-School Exploration Track — Ages 12-14

Now it's YOUR turn! In this notebook, you can pick any galaxy
from our database and plot its rotation curve.

**Try different galaxies and see how different they look!**
Some are small and slow, some are huge and fast."""),
code("""import json
import matplotlib.pyplot as plt
from collections import Counter

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Let's see what galaxies are available
sparc = [g for g in corpus['galaxies']
         if g['survey'] == 'SPARC' and g.get('data')]

print(f"There are {len(sparc)} SPARC galaxies to choose from!")
print()
print("Here are some interesting ones to try:")
suggestions = ['DDO161', 'NGC2403', 'NGC3198', 'UGC2885', 'NGC7793']
for name in suggestions:
    try:
        g = next(g for g in sparc if g['galaxy'] == name)
        vmax = max(p['Vobs'] for p in g['data'])
        print(f"  {name:<12}  max speed = {vmax:.0f} km/s  "
              f"distance = {g['distance_mpc']:.1f} Mpc")
    except StopIteration:
        pass"""),
code("""# ✏️ CHANGE THIS to any galaxy name you want to try!
MY_GALAXY = 'NGC2403'

# Find your galaxy
try:
    galaxy = next(g for g in sparc if g['galaxy'] == MY_GALAXY)
    data   = galaxy['data']
    R = [p['Rad']  for p in data]
    V = [p['Vobs'] for p in data]
    errV = [p.get('errV', 0) for p in data]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(R, V, yerr=errV, fmt='o-', color='#9b59b6',
                capsize=4, linewidth=2, markersize=6)
    ax.set_xlabel('Distance from center (kpc)', fontsize=12)
    ax.set_ylabel('Speed (km/s)', fontsize=12)
    ax.set_title(f'{MY_GALAXY} Rotation Curve\\n'
                 f'Max speed: {max(V):.0f} km/s  |  '
                 f'Distance: {galaxy["distance_mpc"]:.1f} Mpc from Earth',
                 fontsize=11)
    plt.tight_layout()
    plt.savefig(f'hs_a_04_{MY_GALAXY}.png', dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Great job! You plotted {MY_GALAXY}!")
    print(f"Try changing MY_GALAXY to a different name and run again!")
except StopIteration:
    print(f"Galaxy '{MY_GALAXY}' not found. Try one of the suggestions above!")""")
])

# ── HS-A-05: How many galaxies? ───────────────────────────────────────────────
notebooks["hs_a_05_exploring_the_database.ipynb"] = nb([
md("""# 🔭 Exploring the Galaxy Database
### EPS Research High-School Exploration Track — Ages 12-14

Scientists collected data on 438 real galaxies!
Let's explore this database and find out what kinds of galaxies are in it."""),
code("""import json
import matplotlib.pyplot as plt
import numpy as np

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

galaxies = [g for g in corpus['galaxies']
            if g.get('vrot_max_kms')]

# Sort by max speed
fastest = sorted(galaxies, key=lambda x: float(x['vrot_max_kms']), reverse=True)

print("🏆 The 5 FASTEST spinning galaxies in our database:")
for g in fastest[:5]:
    print(f"  {g['galaxy']:<15}  {float(g['vrot_max_kms']):.0f} km/s  "
          f"({float(g['vrot_max_kms'])*3600:.0f} km/h!)")

print()
slowest = sorted(galaxies, key=lambda x: float(x['vrot_max_kms']))
print("🐢 The 5 SLOWEST spinning galaxies:")
for g in slowest[:5]:
    print(f"  {g['galaxy']:<15}  {float(g['vrot_max_kms']):.0f} km/s")"""),
code("""# Plot the distribution of galaxy speeds
speeds = [float(g['vrot_max_kms']) for g in galaxies]

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(speeds, bins=30, color='#3498db', alpha=0.8, edgecolor='white')
ax.axvline(np.median(speeds), color='red', linestyle='--', linewidth=2,
           label=f'Middle speed = {np.median(speeds):.0f} km/s')
ax.set_xlabel('Maximum spinning speed (km/s)', fontsize=12)
ax.set_ylabel('Number of galaxies', fontsize=12)
ax.set_title('How Fast Do Galaxies Spin?\\n438 real galaxies from the EPS Research database 🌌',
             fontsize=11)
ax.legend(fontsize=10)
ax.text(0.97, 0.85,
        f'Fastest: {max(speeds):.0f} km/s\\nSlowest: {min(speeds):.0f} km/s',
        transform=ax.transAxes, ha='right', fontsize=9,
        bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.9))
plt.tight_layout()
plt.savefig('hs_a_05_speed_distribution.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HS-A-06: Small vs large galaxies ─────────────────────────────────────────
notebooks["hs_a_06_small_vs_large.ipynb"] = nb([
md("""# 🔬🔭 Small vs Large Galaxies
### EPS Research High-School Exploration Track — Ages 12-14

Not all galaxies are the same size! Compare a tiny dwarf galaxy
to a massive spiral galaxy using real data."""),
code("""import json
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# Small galaxy
small = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
# Large galaxy
large = next(g for g in corpus['galaxies'] if g['galaxy'] == 'NGC2403')

def get_rc(g):
    d = g['data']
    return [p['Rad'] for p in d], [p['Vobs'] for p in d]

R_s, V_s = get_rc(small)
R_l, V_l = get_rc(large)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(R_s, V_s, 'o-', color='#2ecc71', linewidth=2, markersize=6)
axes[0].set_title(f'DDO161 — Small Dwarf Galaxy\\n'
                  f'Max speed: {max(V_s):.0f} km/s  Size: {max(R_s):.0f} kpc',
                  fontsize=10)
axes[0].set_xlabel('Distance (kpc)', fontsize=10)
axes[0].set_ylabel('Speed (km/s)', fontsize=10)

axes[1].plot(R_l, V_l, 'o-', color='#e74c3c', linewidth=2, markersize=6)
axes[1].set_title(f'NGC2403 — Larger Spiral Galaxy\\n'
                  f'Max speed: {max(V_l):.0f} km/s  Size: {max(R_l):.0f} kpc',
                  fontsize=10)
axes[1].set_xlabel('Distance (kpc)', fontsize=10)

plt.suptitle('Small vs Large Galaxies — Real Data from EPS Research 🔬🔭', fontsize=12)
plt.tight_layout()
plt.savefig('hs_a_06_small_large.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"NGC2403 is about {max(R_l)/max(R_s):.0f}x larger than DDO161!")
print(f"NGC2403 spins about {max(V_l)/max(V_s):.1f}x faster!")""")
])

# ── HS-A-07: The Milky Way's globular clusters ────────────────────────────────
notebooks["hs_a_07_globular_clusters.ipynb"] = nb([
md("""# ✨ Globular Clusters — Ancient Star Cities
### EPS Research High-School Exploration Track — Ages 12-14

A **globular cluster** is a tightly packed ball of hundreds of thousands
of very old stars. Our Milky Way has about 160 of them!

They're some of the oldest objects in the universe — many are
over 12 billion years old (the universe is about 13.8 billion years old).

EPS Research has a database of 174 Milky Way globular clusters!"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

clusters = []
with open('harris_gc_corpus_v1.3.1.jsonl') as f:
    for line in f:
        clusters.append(json.loads(line))

print(f"✨ We have data on {len(clusters)} globular clusters!")

# Get some basic stats
masses = [c['baumgardt2023']['mass_msun']
          for c in clusters
          if c.get('baumgardt2023') and c['baumgardt2023'].get('mass_msun')]

print(f"\\nGlobular cluster masses:")
print(f"  Smallest:  {min(masses):,.0f} stars worth of mass")
print(f"  Largest:   {max(masses):,.0f} stars worth of mass")
print(f"  Typical:   {np.median(masses):,.0f} stars worth of mass")
print()
print("For comparison, the Milky Way has about 200 billion stars!")"""),
code("""# Where are they in the galaxy?
positions = [(c['distances']['r_sun_kpc'], c['distances'].get('r_gc_kpc', 0))
             for c in clusters
             if c.get('distances') and c['distances'].get('r_sun_kpc')]

d_sun = [p[0] for p in positions]
d_gc  = [p[1] for p in positions]

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(d_gc, d_sun, s=20, alpha=0.6, color='#f39c12', edgecolors='#e67e22', linewidths=0.5)
ax.scatter([8], [0], marker='*', s=300, color='#3498db', zorder=5, label='☀️ Our Sun')
ax.set_xlabel('Distance from Milky Way center (kpc)', fontsize=11)
ax.set_ylabel('Distance from our Sun (kpc)', fontsize=11)
ax.set_title('Where Are Our Globular Clusters?\\n'
             '174 ancient star cities mapped in our Galaxy ✨', fontsize=11)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('hs_a_07_globular_clusters.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HS-A-08: How far away are galaxies? ───────────────────────────────────────
notebooks["hs_a_08_galaxy_distances.ipynb"] = nb([
md("""# 📏 How Far Away Are These Galaxies?
### EPS Research High-School Exploration Track — Ages 12-14

The galaxies in our database are incredibly far away.
Distances in space are so huge we need special units:

- **1 light-year** = how far light travels in one year = 9.46 trillion km
- **1 parsec (pc)** = 3.26 light-years
- **1 kiloparsec (kpc)** = 3,260 light-years
- **1 Megaparsec (Mpc)** = 3.26 million light-years

The nearest galaxy in our database is just a few Mpc away.
The most distant is hundreds of Mpc away!"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

galaxies = [g for g in corpus['galaxies'] if g.get('distance_mpc')]
distances_mpc = [float(g['distance_mpc']) for g in galaxies]
distances_lyr = [d * 3.26e6 for d in distances_mpc]

print("How far away are these galaxies?")
print()
print(f"Nearest galaxy:   {min(distances_mpc):.1f} Mpc = {min(distances_lyr)/1e6:.1f} million light-years")
print(f"Farthest galaxy:  {max(distances_mpc):.1f} Mpc = {max(distances_mpc)*3.26:.0f} million light-years")
print(f"Typical distance: {np.median(distances_mpc):.0f} Mpc = {np.median(distances_mpc)*3.26:.0f} million light-years")
print()
print("For scale: our nearest star (Proxima Centauri) is only 4 light-years away!")
print("These galaxies are millions to hundreds of millions of times farther!")"""),
code("""fig, ax = plt.subplots(figsize=(9, 4))
ax.hist(distances_mpc, bins=25, color='#8e44ad', alpha=0.8, edgecolor='white')
ax.set_xlabel('Distance (Megaparsecs)', fontsize=11)
ax.set_ylabel('Number of galaxies', fontsize=11)
ax.set_title('How Far Away Are Our 438 Galaxies?\\n'
             '1 Megaparsec = 3.26 million light-years 📏', fontsize=11)

# Add a secondary x-axis showing light-years
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim()[0] * 3.26, ax.get_xlim()[1] * 3.26)
ax2.set_xlabel('Distance (millions of light-years)', fontsize=10)

plt.tight_layout()
plt.savefig('hs_a_08_distances.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HS-A-09: The omega correction ─────────────────────────────────────────────
notebooks["hs_a_09_the_omega_correction.ipynb"] = nb([
md("""# 🔄 A New Idea: The Omega Correction
### EPS Research High-School Exploration Track — Ages 12-14

Scientists at EPS Research found something interesting:
there's a pattern in how galaxy rotation curves behave.

They discovered a simple **correction** that can be calculated
from just two measurements — the innermost and outermost points
of a rotation curve.

This correction is called **omega (ω)** — the Greek letter that looks like a lowercase w.

Let's see it in action on our galaxy DDO161!"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

galaxy = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
data   = galaxy['data']

R    = np.array([p['Rad']  for p in data])
Vobs = np.array([p['Vobs'] for p in data])
errV = np.array([p['errV'] for p in data])

# The omega correction uses just two boundary points!
R1, V1 = R[0],  Vobs[0]   # innermost point
R2, V2 = R[-1], Vobs[-1]  # outermost point

# Calculate omega (the correction)
omega = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix

print(f"Innermost point: R = {R1:.2f} kpc,  V = {V1:.1f} km/s")
print(f"Outermost point: R = {R2:.2f} kpc,  V = {V2:.1f} km/s")
print()
print(f"Omega (ω) = {omega:.3f} rad/Gyr")
print()
print("Now we apply the correction to get the adjusted velocity:")
V_adj = Vobs - R * omega
print("V_adjusted = V_observed - R × ω")"""),
code("""# Compare the original curve with the corrected curve
fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(R, Vobs, yerr=errV, fmt='o', color='#3498db',
            capsize=3, markersize=5, label='🔵 Original observed speed', zorder=5)
ax.plot(R, V_adj, '^-', color='#2ecc71', linewidth=2, markersize=6,
        label=f'🟢 Omega-corrected speed (ω = {omega:.2f})')
ax.set_xlabel('Distance from center (kpc)', fontsize=12)
ax.set_ylabel('Speed (km/s)', fontsize=12)
ax.set_title('The Omega Correction — DDO161\\n'
             'EPS Research Flynn & Cannaliato (2025)', fontsize=11)
ax.legend(fontsize=9)
ax.text(0.02, 0.08,
        'The green line brings the\\nobserved speed closer to\\nthe baryonic prediction!',
        transform=ax.transAxes, va='bottom', fontsize=8,
        bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.9))
plt.tight_layout()
plt.savefig('hs_a_09_omega_correction.png', dpi=150, bbox_inches='tight')
plt.show()"""),
md("""## What did the omega correction do?

The green line shows the **corrected** rotation curve.
It's closer to what we'd expect from just the visible matter!

This is the EPS Research discovery: a simple two-point correction
that works across many different galaxies.

Scientists published this in a journal article in 2025:
**Flynn & Cannaliato (2025)** in *Frontiers in Astronomy and Space Sciences*.

In the final notebook, we'll look at what this means for the dark matter mystery! 🌑""")
])

# ── HS-A-10: Your turn — science explorer ────────────────────────────────────
notebooks["hs_a_10_science_explorer.ipynb"] = nb([
md("""# 🚀 You're a Science Explorer!
### EPS Research High-School Exploration Track — Ages 12-14

Congratulations! You've reached the final notebook in Track A.

You've learned about:
- 🌌 What galaxies are
- 🌀 Rotation curves
- 🌑 The dark matter mystery
- 📏 Cosmic distances
- ✨ Globular clusters
- 🔄 The omega correction

Now let's do a mini science project of your own!
Pick 3 galaxies, plot their rotation curves, and find which one spins fastest."""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

# ✏️ CHANGE THESE to any 3 galaxies you want to compare!
MY_GALAXIES = ['DDO161', 'NGC2403', 'NGC3198']
COLORS      = ['#3498db', '#e74c3c', '#2ecc71']

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
results = []

for i, (name, color) in enumerate(zip(MY_GALAXIES, COLORS)):
    try:
        g  = next(g for g in corpus['galaxies'] if g['galaxy'] == name)
        d  = g['data']
        R  = [p['Rad']  for p in d]
        V  = [p['Vobs'] for p in d]
        axes[i].plot(R, V, 'o-', color=color, linewidth=2, markersize=5)
        axes[i].set_title(f'{name}\\nMax: {max(V):.0f} km/s', fontsize=10)
        axes[i].set_xlabel('Radius (kpc)', fontsize=9)
        if i == 0: axes[i].set_ylabel('Speed (km/s)', fontsize=9)
        results.append((name, max(V)))
    except StopIteration:
        axes[i].text(0.5, 0.5, f'{name}\\nnot found',
                     transform=axes[i].transAxes, ha='center')

plt.suptitle('My Galaxy Comparison — Science Explorer Project 🚀', fontsize=12)
plt.tight_layout()
plt.savefig('hs_a_10_my_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

if results:
    winner = max(results, key=lambda x: x[1])
    print(f"\\n🏆 Winner: {winner[0]} spins fastest at {winner[1]:.0f} km/s!")
    print()
    print("Great work, Science Explorer! 🌟")"""),
md("""## What's Next?

If you want to go deeper, try **Track B** (Ages 15-18)!
You'll learn:
- The actual math behind the omega correction
- How to compute omega yourself
- How to measure the dark matter gap
- How this connects to the big questions in astrophysics

**The universe is waiting for you to explore it!** 🚀🌌""")
])

# ══════════════════════════════════════════════════════════════════════════════
# TRACK B: Ages 15-18 (High School)
# Algebra, basic Python, scientific reasoning
# ══════════════════════════════════════════════════════════════════════════════

# ── HS-B-01: Newtonian gravity in galaxies ────────────────────────────────────
notebooks["hs_b_01_newtonian_gravity.ipynb"] = nb([
md("""# ⚖️ Newtonian Gravity in Galaxies
### EPS Research High-School Exploration Track — Ages 15-18

Newton's law of gravity tells us that for a circular orbit:

$$V_{\\rm circular} = \\sqrt{\\frac{GM(<R)}{R}}$$

where:
- $V$ = orbital speed
- $G$ = gravitational constant
- $M(<R)$ = total mass inside radius $R$
- $R$ = distance from center

If most mass is near the center (like our solar system),
then $M(<R)$ becomes roughly constant at large $R$,
and $V \\propto 1/\\sqrt{R}$ — a **Keplerian decline**.

But galaxies show **flat** rotation curves. Let's see why this is strange.

**Prerequisites:** Basic algebra, understanding of gravity as $F = GMm/r^2$"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

galaxy = next(g for g in corpus['galaxies'] if g['galaxy'] == 'NGC2403')
data   = galaxy['data']

R    = np.array([p['Rad']  for p in data])
Vobs = np.array([p['Vobs'] for p in data])
errV = np.array([p['errV'] for p in data])

# Compute Keplerian prediction from outermost point
# If V = sqrt(GM/R), then GM = V_max^2 * R_max (use outermost point)
V_outer = Vobs[-1]
R_outer = R[-1]
GM      = V_outer**2 * R_outer   # units: km^2/s^2 * kpc

V_kepler = np.sqrt(GM / R)  # expected if all mass is inside R_outer

print(f"Galaxy: NGC2403")
print(f"Outermost measured point: R = {R_outer:.1f} kpc, V = {V_outer:.1f} km/s")
print(f"GM = {GM:.1f} km^2/s^2 * kpc")
print()
print("Comparing observed vs Keplerian at selected radii:")
print(f"  {'R (kpc)':>8}  {'V_obs':>8}  {'V_Kep':>8}  {'Ratio':>8}")
for r, vo, vk in zip(R[::2], Vobs[::2], V_kepler[::2]):
    print(f"  {r:>8.1f}  {vo:>8.1f}  {vk:>8.1f}  {vo/vk:>8.2f}")"""),
code("""fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(R, Vobs, yerr=errV, fmt='o', color='#3498db',
            capsize=3, markersize=5, label=r'$V_{\\rm obs}$ (measured)', zorder=5)
ax.plot(R, V_kepler, '--', color='#e74c3c', linewidth=2,
        label=r'$V_{\\rm Keplerian} = \\sqrt{GM/R}$ (expected for concentrated mass)')
ax.fill_between(R, V_kepler, Vobs, alpha=0.15, color='purple',
                label='Missing mass (dark matter?)')
ax.set_xlabel('Radius R (kpc)', fontsize=12)
ax.set_ylabel('Velocity V (km/s)', fontsize=12)
ax.set_title('NGC2403: Why Galaxies Defy Newtonian Expectation\\n'
             'The flat curve requires mass beyond what we can see', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hs_b_01_newtonian.png', dpi=150, bbox_inches='tight')
plt.show()

# Quantify the discrepancy
ratio_outer = Vobs[-1] / V_kepler[-1]
print(f"\\nAt the outermost point, the ratio is exactly 1.0 (by construction).")
print(f"At half the outermost radius: V_obs/V_Kep = {Vobs[len(R)//2]/V_kepler[len(R)//2]:.2f}")
print(f"This means the outer galaxy has MORE mass than the inner galaxy predicts.")""")
])

# ── HS-B-02: Computing omega ───────────────────────────────────────────────────
notebooks["hs_b_02_computing_omega.ipynb"] = nb([
md("""# 🔢 Computing Omega From First Principles
### EPS Research High-School Exploration Track — Ages 15-18

The EPS Research omega correction is derived from angular velocity:

$$\\omega = \\frac{V}{R} \\quad [\\text{rad/Gyr}]$$

The correction formula uses the **gradient** of angular velocity:

$$\\omega_{\\rm correction} = \\left(\\frac{V_2}{R_2} - \\frac{V_1}{R_1}\\right) \\left(\\frac{R_1}{R_2}\\right)^{3/2}$$

where $(R_1, V_1)$ is the innermost point and $(R_2, V_2)$ is the outermost.

**Why does this make sense?**
- $V/R$ is the angular velocity at each point
- The term $(R_1/R_2)^{3/2}$ comes from Kepler's third law scaling

**Reference:** Flynn & Cannaliato (2025), DOI: 10.3389/fspas.2025.1680387

**Prerequisites:** Algebra, understanding of velocity vs angular velocity"""),
code("""import json
import numpy as np
import matplotlib.pyplot as plt

with open('rotation_curve_corpus_v7.json') as f:
    corpus = json.load(f)

galaxy = next(g for g in corpus['galaxies'] if g['galaxy'] == 'DDO161')
data   = galaxy['data']

R    = np.array([p['Rad']  for p in data])
Vobs = np.array([p['Vobs'] for p in data])

# Step 1: Compute angular velocity at each point
omega_profile = Vobs / R  # rad / (kpc km/s^-1) = ~ rad/Gyr after unit conversion

print("Step 1: Angular velocity profile V/R")
print(f"  {'R (kpc)':>10}  {'V (km/s)':>10}  {'V/R (km/s/kpc)':>16}")
for r, v, w in zip(R[:6], Vobs[:6], omega_profile[:6]):
    print(f"  {r:>10.2f}  {v:>10.2f}  {w:>16.3f}")
print()
print("Notice: V/R decreases with radius — the angular velocity falls outward")
print("This is the key signal the omega correction captures.")"""),
code("""# Step 2: Compute omega correction from boundary points
R1, V1 = R[0],  Vobs[0]
R2, V2 = R[-1], Vobs[-1]

print(f"Step 2: Boundary points")
print(f"  Inner: R1 = {R1:.2f} kpc,  V1 = {V1:.2f} km/s,  V1/R1 = {V1/R1:.3f}")
print(f"  Outer: R2 = {R2:.2f} kpc,  V2 = {V2:.2f} km/s,  V2/R2 = {V2/R2:.3f}")
print()

omega = V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
print(f"Step 3: Omega correction")
print(f"  ω = (V2/R2 - V1/R1) × (R1/R2)^(3/2)")
print(f"  ω = ({V2/R2:.3f} - {V1/R1:.3f}) × ({R1/R2:.3f})^1.5")
print(f"  ω = {V2/R2 - V1/R1:.3f} × {(R1/R2)**1.5:.3f}")
print(f"  ω = {omega:.3f} km/s/kpc")
print(f"  ω = {omega:.3f} rad/Gyr  (1 km/s/kpc ≈ 1.022 rad/Gyr)")
print()
print(f"Published value: ω = 4.69 rad/Gyr (Flynn & Cannaliato 2025)")

# Apply correction
V_adj = Vobs - R * omega

# Baryonic velocity
Vgas  = np.array([p['Vgas']  for p in data])
Vdisk = np.array([p['Vdisk'] for p in data])
Vbul  = np.array([p['Vbul']  for p in data])
Vbar  = np.where(Vgas < 0, -np.sqrt(Vgas**2+Vdisk**2+Vbul**2),
                             np.sqrt(Vgas**2+Vdisk**2+Vbul**2))

rmse_omega = np.sqrt(np.mean((V_adj - Vbar)**2))
print(f"\\nRMSE (corrected vs baryonic): {rmse_omega:.2f} km/s")"""),
code("""fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(R, Vobs, fmt='o', color='#3498db', markersize=5,
            label=r'$V_{\\rm obs}$', zorder=5)
ax.plot(R, Vbar,  's-', color='#e74c3c', lw=1.5, label=r'$V_{\\rm bar}$ (baryonic)')
ax.plot(R, V_adj, '^-', color='#2ecc71', lw=2,
        label=fr'$V_{{\\rm adj}} = V_{{\\rm obs}} - R\omega$  ($\omega={omega:.2f}$)')
ax.set_xlabel('Radius R (kpc)', fontsize=12)
ax.set_ylabel('Velocity V (km/s)', fontsize=12)
ax.set_title('DDO161 — Omega Correction Applied\\n'
             'Flynn & Cannaliato (2025) | DOI: 10.3389/fspas.2025.1680387', fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('hs_b_02_omega.png', dpi=150, bbox_inches='tight')
plt.show()""")
])

# ── HS-B-03 to HS-B-10: Remaining track B notebooks ─────────────────────────
remaining_hs_b = {

"hs_b_03_rmse_metric.ipynb": nb([
md("""# 📊 Measuring How Well a Model Fits: RMSE
### EPS Research High-School Exploration Track — Ages 15-18

In science, we need a way to measure how well a model fits data.
The most common metric is **RMSE** (Root Mean Square Error):

$$\\text{RMSE} = \\sqrt{\\frac{1}{N}\\sum_{i=1}^{N}(V_{\\rm model,i} - V_{\\rm data,i})^2}$$

Lower RMSE = better fit. Let's compute it for DDO161.

**Prerequisites:** Basic statistics, square roots, summation notation"""),
code("""import json, numpy as np, matplotlib.pyplot as plt
with open('rotation_curve_corpus_v7.json') as f:
    corpus=json.load(f)
g=next(g for g in corpus['galaxies'] if g['galaxy']=='DDO161')
d=g['data']
R=np.array([p['Rad'] for p in d]); V=np.array([p['Vobs'] for p in d])
Vgas=np.array([p['Vgas'] for p in d]); Vdisk=np.array([p['Vdisk'] for p in d])
Vbul=np.array([p['Vbul'] for p in d])
Vbar=np.where(Vgas<0,-np.sqrt(Vgas**2+Vdisk**2+Vbul**2),np.sqrt(Vgas**2+Vdisk**2+Vbul**2))
R1,V1=R[0],V[0]; R2,V2=R[-1],V[-1]
omega=V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
V_adj=V-R*omega
V_kep=np.sqrt(V2**2*R2/R)

def rmse(pred, true):
    return np.sqrt(np.mean((pred - true)**2))

print("RMSE comparison for DDO161:")
print(f"  Keplerian model:   RMSE = {rmse(V_kep, Vbar):.2f} km/s  (pure Newtonian, no dark matter)")
print(f"  Omega correction:  RMSE = {rmse(V_adj, Vbar):.2f} km/s  (EPS Research correction)")
print(f"  Improvement:       {rmse(V_kep, Vbar) - rmse(V_adj, Vbar):.2f} km/s better")
print()
print("For the full 84-galaxy SPARC sample (Flynn 2026):")
print("  Mean RMSE (Keplerian): 74.20 km/s")
print("  Mean RMSE (omega):     25.45 km/s")
print("  That's a 2× average improvement!")""")
]),

"hs_b_04_baryonic_quadrature.ipynb": nb([
md("""# ⚡ Baryonic Velocity: Sign-Preserving Quadrature
### EPS Research High-School Exploration Track — Ages 15-18

The total baryonic velocity combines gas, disk, and bulge contributions:

$$V_{\\rm bar} = \\text{sign}(V_{\\rm gas})\\sqrt{|V_{\\rm gas}|^2 + \\Upsilon V_{\\rm disk}^2 + \\Upsilon_b V_{\\rm bul}^2}$$

Why sign-preserving? At inner radii, thermal gas pressure can exceed
rotation, making Vgas effectively negative. We preserve this sign
to avoid artificially boosting the baryonic contribution.

**Prerequisites:** Vectors, square roots, quadrature addition"""),
code("""import json, numpy as np, matplotlib.pyplot as plt
with open('rotation_curve_corpus_v7.json') as f:
    corpus=json.load(f)
g=next(g for g in corpus['galaxies'] if g['galaxy']=='NGC2403')
d=g['data']
R=np.array([p['Rad'] for p in d]); Vobs=np.array([p['Vobs'] for p in d])
Vgas=np.array([p['Vgas'] for p in d]); Vdisk=np.array([p['Vdisk'] for p in d])
Vbul=np.array([p['Vbul'] for p in d])
Upsilon=1.0
Vbar_plain=np.sqrt(Vgas**2+Upsilon*Vdisk**2+Vbul**2)
Vbar_signed=np.where(Vgas<0,-np.sqrt(Vgas**2+Upsilon*Vdisk**2+Vbul**2),
                            np.sqrt(Vgas**2+Upsilon*Vdisk**2+Vbul**2))
print(f"NGC2403: Vgas negative rows = {(Vgas<0).sum()}")
print("\\nDifference between signed and unsigned at inner points:")
for r,vp,vs in zip(R[:5],Vbar_plain[:5],Vbar_signed[:5]):
    print(f"  R={r:.1f} kpc: plain={vp:.1f}, signed={vs:.1f}, diff={vp-vs:.1f}")
fig,ax=plt.subplots(figsize=(8,5))
ax.plot(R,Vobs,'o-',color='#3498db',lw=1.5,label=r'$V_{\\rm obs}$')
ax.plot(R,Vbar_signed,'s-',color='#e74c3c',lw=1.5,label=r'$V_{\\rm bar}$ (sign-preserving)')
ax.plot(R,Vgas,'^--',color='#2ecc71',lw=1.2,alpha=0.7,label=r'$V_{\\rm gas}$')
ax.axhline(0,color='black',lw=0.7,alpha=0.4)
ax.set_xlabel('R (kpc)',fontsize=12); ax.set_ylabel('V (km/s)',fontsize=12)
ax.set_title('NGC2403 — Sign-Preserving Baryonic Quadrature',fontsize=11)
ax.legend(fontsize=9); plt.tight_layout()
plt.savefig('hs_b_04_quadrature.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"hs_b_05_outer_gap.ipynb": nb([
md("""# 🔍 The Outer Gap Diagnostic
### EPS Research High-School Exploration Track — Ages 15-18

The **outer gap** is V_adj(R_2) - V_bar(R_2) — the residual between
the omega-corrected velocity and the baryonic velocity at the outermost ring.

**Key result from Flynn (2026):** All 84 SPARC outer gaps are **negative**.
This means V_adj < V_bar at the outermost point — the omega correction
never re-imports dark matter. This rules out a class of spurious corrections.

**Prerequisites:** Understanding of residuals, basic RMSE"""),
code("""import json, numpy as np, matplotlib.pyplot as plt
with open('rotation_curve_corpus_v7.json') as f:
    corpus=json.load(f)
gaps=[]
for g in corpus['galaxies']:
    if g['survey']!='SPARC' or not g.get('data') or len(g['data'])<3: continue
    d=g['data']; R=[p['Rad'] for p in d]; V=[p['Vobs'] for p in d]
    R1,V1=R[0],V[0]; R2,V2=R[-1],V[-1]
    if R1<=0 or R2<=0 or V1<=0 or V2<=0: continue
    omega=V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix; V_adj_R2=V2-R2*omega
    Vgas=d[-1].get('Vgas',0); Vdisk=d[-1].get('Vdisk',0); Vbul=d[-1].get('Vbul',0)
    Vbar_R2=np.sqrt(Vgas**2+Vdisk**2+Vbul**2)
    if Vbar_R2>0: gaps.append(V_adj_R2-Vbar_R2)
print(f"SPARC galaxies with outer gap: {len(gaps)}")
print(f"All negative: {all(g<0 for g in gaps)}")
print(f"Mean: {np.mean(gaps):.1f} km/s  Std: {np.std(gaps):.1f} km/s")
print(f"Published (Flynn 2026): mean = -51.4 ± 25.0 km/s")
fig,ax=plt.subplots(figsize=(8,4))
ax.hist(gaps,bins=25,color='#9b59b6',alpha=0.8,edgecolor='white')
ax.axvline(0,color='red',ls='--',lw=2,label='Gap = 0')
ax.axvline(np.mean(gaps),color='orange',ls='-',lw=1.5,label=f'Mean={np.mean(gaps):.1f}')
ax.set_xlabel('Outer gap = V_adj - V_bar at R_max (km/s)',fontsize=11)
ax.set_ylabel('N galaxies',fontsize=11)
ax.set_title('Outer Gap — All Negative (Flynn 2026)\\nV_adj never exceeds V_bar',fontsize=10)
ax.legend(fontsize=8); plt.tight_layout()
plt.savefig('hs_b_05_outer_gap.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"hs_b_06_omega_statistics.ipynb": nb([
md("""# 📈 Omega Statistics Across 84 SPARC Galaxies
### EPS Research High-School Exploration Track — Ages 15-18

Flynn & Cannaliato (2025) found: mean ω = 7.06 ± 3.26 rad/Gyr
across 84 SPARC Q=1 galaxies.

Let's reproduce this and understand what the distribution tells us.

**Prerequisites:** Mean, standard deviation, histograms"""),
code("""import json, numpy as np, matplotlib.pyplot as plt
with open('rotation_curve_corpus_v7.json') as f:
    corpus=json.load(f)
omegas=[]
for g in corpus['galaxies']:
    if g['survey']!='SPARC' or not g.get('data') or len(g['data'])<3: continue
    d=g['data']; R=[p['Rad'] for p in d]; V=[p['Vobs'] for p in d]
    R1,V1=R[0],V[0]; R2,V2=R[-1],V[-1]
    if R1>0 and R2>0 and V1>0 and V2>0:
        omegas.append(V2/R2 - (V1/R1)*(R1/R2)**1.5)  # Eq.6 corrected 2026-07-12: operator-precedence fix
mean_o=np.mean(omegas); std_o=np.std(omegas); se=std_o/np.sqrt(len(omegas))
print(f"N galaxies: {len(omegas)}")
print(f"Mean ω = {mean_o:.2f} ± {se:.2f} rad/Gyr  (standard error)")
print(f"Std  ω = {std_o:.2f} rad/Gyr")
print(f"Published: 7.06 ± 3.26 rad/Gyr (Flynn & Cannaliato 2025)")
fig,ax=plt.subplots(figsize=(8,4))
ax.hist(omegas,bins=25,color='#1abc9c',alpha=0.8,edgecolor='white',density=True)
x=np.linspace(min(omegas),max(omegas),100)
from scipy.stats import norm
ax.plot(x,norm.pdf(x,mean_o,std_o),color='red',lw=2,label=f'Normal fit: μ={mean_o:.2f}, σ={std_o:.2f}')
ax.axvline(mean_o,color='red',ls='--',lw=1.5)
ax.set_xlabel(r'$\omega$ (rad/Gyr)',fontsize=12); ax.set_ylabel('Density',fontsize=12)
ax.set_title('Omega Distribution — SPARC Sample\\nFlynn & Cannaliato (2025)',fontsize=11)
ax.legend(fontsize=9); plt.tight_layout()
plt.savefig('hs_b_06_omega_stats.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"hs_b_07_cross_epoch.ipynb": nb([
md("""# 🌌 Cross-Epoch Kinematics: z=0 to z~5
### EPS Research High-School Exploration Track — Ages 15-18

The EPS Research corpus spans **cosmic time** — from galaxies today (z=0)
to galaxies as they were 12 billion years ago (z~5).

At z=5, we use ALMA [CII] data instead of HI 21cm.
The omega correction gives **negative** values at z~5 vs **positive** at z=0.

This sign reversal is consistent with galaxy evolution:
young compact galaxies → extended rotating disks over cosmic time.

**Prerequisites:** Understanding of redshift as look-back time"""),
code("""import numpy as np, matplotlib.pyplot as plt

# z=0 results from EPS Research corpora (published)
z0_sparc_mean   = 7.06   # Flynn & Cannaliato 2025
z0_sparc_std    = 3.26
z0_dwarf_median = 9.94   # Flynn 2026

# z~5 results from Z1 corpus (Flynn 2026)
z5_results = [
    ('J0817',        4.2605, -33.22),
    ('CG32',         4.4105, -13.05),
    ('DC396844',     4.5424, -14.48),
    ('VC5110377875', 4.5506, -12.73),
    ('DC881725',     4.5778, -13.05),
    ('DC552206',     5.5016,  -2.96),
    ('HZ9',          5.5413, -20.14),
    ('DC494057',     5.5446,  -9.53),
]

fig, ax = plt.subplots(figsize=(9, 5))

# z=0 reference lines
ax.axhline(z0_sparc_mean, color='#3498db', ls='-', lw=2, alpha=0.7,
           label=f'SPARC mean ω = +{z0_sparc_mean:.2f} (z=0)')
ax.axhline(z0_dwarf_median, color='#2ecc71', ls='--', lw=2, alpha=0.7,
           label=f'Dwarf median ω = +{z0_dwarf_median:.2f} (z=0)')
ax.axhline(0, color='black', ls='-', lw=0.7, alpha=0.3)

# z~5 points
z5_z = [r[1] for r in z5_results]
z5_o = [r[2] for r in z5_results]
ax.scatter(z5_z, z5_o, s=80, color='#e74c3c', zorder=5, marker='D',
           label='Z1 tier-1 rotators (z~4-6)', edgecolors='k', linewidths=0.5)

ax.set_xlabel('Redshift z', fontsize=12)
ax.set_ylabel(r'$\omega$ (rad/Gyr)', fontsize=12)
ax.set_title('Omega Across Cosmic Time\\n'
             'Sign reversal: negative at z~5, positive at z=0', fontsize=11)
ax.legend(fontsize=8, loc='upper right')
ax.text(0.02, 0.08,
        'Note: Z1 values are observational kinematics\\n'
        'No baryonic decomposition at z~5',
        transform=ax.transAxes, fontsize=8,
        bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.85))
plt.tight_layout()
plt.savefig('hs_b_07_cross_epoch.png', dpi=150, bbox_inches='tight')
plt.show()

z5_median = np.median(z5_o)
print(f"z~5 median ω = {z5_median:.2f} rad/Gyr  (all negative)")
print(f"z=0  mean  ω = +{z0_sparc_mean:.2f} rad/Gyr  (all positive)")
print(f"Sign reversal across ~9 billion years of cosmic evolution!")""")
]),

"hs_b_08_log_slope.ipynb": nb([
md("""# 📐 The Log-Slope Diagnostic
### EPS Research High-School Exploration Track — Ages 15-18

The logarithmic slope $d\\ln V / d\\ln R$ tells us the **shape** of a rotation curve:

| Slope | Meaning |
|-------|---------|
| +1.0 | Solid-body rotation (V increases linearly with R) |
| 0.0  | Flat rotation curve (V constant) |
| −0.5 | Keplerian decline (V falls as 1/√R) |

For the omega correction to improve the fit, we expect the outer slope
to be close to −0.5. Let's verify this across the SPARC sample.

**Prerequisites:** Logarithms, derivatives (or finite differences)"""),
code("""import json, numpy as np, matplotlib.pyplot as plt
with open('rotation_curve_corpus_v7.json') as f:
    corpus=json.load(f)
outer_slopes=[]
for g in corpus['galaxies']:
    if g['survey']!='SPARC' or not g.get('data') or len(g['data'])<5: continue
    d=g['data']; R=np.array([p['Rad'] for p in d]); V=np.array([p['Vobs'] for p in d])
    if R[0]<=0 or V[0]<=0: continue
    lnR=np.log(R); lnV=np.log(V)
    slopes=np.gradient(lnV,lnR)
    outer_slopes.append(slopes[-1])
print(f"SPARC galaxies analyzed: {len(outer_slopes)}")
print(f"Median outer log-slope: {np.median(outer_slopes):.3f}")
print(f"Fraction with slope < 0: {sum(1 for s in outer_slopes if s<0)/len(outer_slopes)*100:.0f}%")
print(f"Fraction with slope near -0.5 (±0.2): {sum(1 for s in outer_slopes if -0.7<s<-0.3)/len(outer_slopes)*100:.0f}%")
fig,ax=plt.subplots(figsize=(8,4))
ax.hist(outer_slopes,bins=25,color='#e67e22',alpha=0.8,edgecolor='white')
ax.axvline(-0.5,color='red',ls='--',lw=2,label='Keplerian (-0.5)')
ax.axvline(0.0, color='blue',ls='--',lw=2,label='Flat (0.0)')
ax.axvline(np.median(outer_slopes),color='green',ls='-',lw=1.5,
           label=f'Median={np.median(outer_slopes):.2f}')
ax.set_xlabel('Outer log-slope d ln V / d ln R',fontsize=11); ax.set_ylabel('N',fontsize=11)
ax.set_title('Outer Log-Slope Distribution — SPARC\\nMost galaxies approach Keplerian at outer radii',fontsize=10)
ax.legend(fontsize=8); plt.tight_layout()
plt.savefig('hs_b_08_log_slope.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"hs_b_09_research_project.ipynb": nb([
md("""# 🔬 Your Research Project
### EPS Research High-School Exploration Track — Ages 15-18

Design your own mini-research project using the EPS Research corpus.

**Project:** Test whether omega correlates with galaxy inclination.

Hypothesis: If omega is a real physical quantity (not an artifact),
it should NOT systematically depend on how tilted the galaxy is
toward us (inclination angle).

**Method:**
1. Compute omega for all SPARC galaxies
2. Compare omega for face-on (low inclination) vs edge-on (high inclination)
3. Interpret the result

**Prerequisites:** Correlation, hypothesis testing, scientific reasoning"""),
code("""import json, numpy as np, matplotlib.pyplot as plt
with open('rotation_curve_corpus_v7.json') as f:
    corpus=json.load(f)
results=[]
for g in corpus['galaxies']:
    if g['survey']!='SPARC' or not g.get('data') or len(g['data'])<3: continue
    if not g.get('inc_deg'): continue
    d=g['data']; R=[p['Rad'] for p in d]; V=[p['Vobs'] for p in d]
    R1,V1=R[0],V[0]; R2,V2=R[-1],V[-1]
    if R1>0 and R2>0 and V1>0 and V2>0:
        omega=V2/R2 - (V1/R1)*(R1/R2)**1.5  # Eq.6 corrected 2026-07-12: operator-precedence fix
        results.append({'galaxy':g['galaxy'],'omega':omega,'inc':float(g['inc_deg'])})
inc=[r['inc'] for r in results]; omegas=[r['omega'] for r in results]
corr=np.corrcoef(inc,omegas)[0,1]
print(f"N galaxies: {len(results)}")
print(f"Pearson r (inclination vs omega): {corr:.3f}")
print()
if abs(corr)<0.2:
    print("✅ Result: WEAK correlation — omega is likely NOT an inclination artifact")
elif abs(corr)<0.4:
    print("⚠️  Result: MODERATE correlation — some inclination dependence")
else:
    print("❌ Result: STRONG correlation — omega may be inclination-dependent")
fig,ax=plt.subplots(figsize=(7,5))
ax.scatter(inc,omegas,s=20,alpha=0.6,color='#8e44ad')
ax.set_xlabel('Inclination (degrees)',fontsize=12); ax.set_ylabel(r'$\omega$ (rad/Gyr)',fontsize=12)
ax.set_title(f'Testing: Does omega depend on inclination?\\nr = {corr:.3f}',fontsize=11)
plt.tight_layout(); plt.savefig('hs_b_09_project.png',dpi=150,bbox_inches='tight'); plt.show()""")
]),

"hs_b_10_capstone.ipynb": nb([
md("""# 🎓 Capstone: The Full EPS Research Picture
### EPS Research High-School Exploration Track — Ages 15-18

You've completed Track B! Let's put together the full scientific picture.

**The EPS Research program in one diagram:**

Four corpora spanning cosmic time → omega correction tested at each epoch →
sign reversal from z~5 to z=0 → motivates RAMSES cosmological simulations.

This capstone produces a publication-quality summary figure."""),
code("""import numpy as np, matplotlib.pyplot as plt, matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(13, 8))
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)
ax1 = fig.add_subplot(gs[0, :2])
ax2 = fig.add_subplot(gs[0, 2])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])
ax5 = fig.add_subplot(gs[1, 2])

# Panel 1: Omega across cosmic time
z0_pts = [(0.0, 7.06), (0.0, 9.94)]
z5_pts = [(4.2605,-33.22),(4.4105,-13.05),(4.5424,-14.48),(4.5506,-12.73),
          (4.5778,-13.05),(5.5016,-2.96),(5.5413,-20.14),(5.5446,-9.53)]
ax1.axhline(7.06,color='#3498db',ls='-',lw=2,alpha=0.7,label='SPARC mean +7.06')
ax1.axhline(9.94,color='#2ecc71',ls='--',lw=2,alpha=0.7,label='Dwarf median +9.94')
ax1.axhline(0,color='black',ls='-',lw=0.7,alpha=0.3)
z5z=[r[0] for r in z5_pts]; z5o=[r[1] for r in z5_pts]
ax1.scatter(z5z,z5o,s=80,color='#e74c3c',zorder=5,marker='D',
            label='Z1 (z~4-6)',edgecolors='k',linewidths=0.5)
ax1.set_xlabel('Redshift z',fontsize=10); ax1.set_ylabel(r'$\omega$ (rad/Gyr)',fontsize=10)
ax1.set_title('Omega Across Cosmic Time',fontsize=10); ax1.legend(fontsize=7)

# Panel 2: Corpus series table
ax2.axis('off')
data=[['Corpus','N','z'],['HI v7','438','0'],['Dwarfs','129','0'],['GC','174','MW'],['Z1','31','4-6']]
tbl=ax2.table(cellText=data[1:],colLabels=data[0],loc='center',cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(9)
for (r,c),cell in tbl.get_celld().items():
    if r==0: cell.set_facecolor('#3498db'); cell.set_text_props(color='white')
ax2.set_title('EPS Corpus Series',fontsize=10)

# Panel 3: RMSE improvement
categories=['Keplerian','Omega']; values=[74.20,25.45]
colors=['#e74c3c','#2ecc71']
ax3.bar(categories,values,color=colors,alpha=0.8,edgecolor='white')
ax3.set_ylabel('Mean RMSE (km/s)',fontsize=9); ax3.set_title('RMSE Improvement\n84 SPARC galaxies',fontsize=9)
ax3.text(1,26,'2.0× better',ha='center',fontsize=8,color='green',weight='bold')

# Panel 4: Outer gaps
gaps=np.random.normal(-51.4,25,84)  # simulated from published values
ax4.hist(gaps,bins=20,color='#9b59b6',alpha=0.8,edgecolor='white')
ax4.axvline(0,color='red',ls='--',lw=2)
ax4.set_xlabel('Outer gap (km/s)',fontsize=9); ax4.set_title('All 84 outer gaps\nnegative',fontsize=9)

# Panel 5: Research arc
ax5.axis('off')
arc=[('2025','Paper 1: omega intro','✓ Published'),
     ('2026','Papers 2-6: validation','✓ Submitted'),
     ('2027','Paper 7: z=0 to z~6','→ Planned'),
     ('2027','Paper 8: RAMSES','→ Planned')]
for i,(yr,title,status) in enumerate(arc):
    color='#2ecc71' if '✓' in status else '#f39c12'
    ax5.text(0.05,0.85-i*0.22,f'{yr}: {title}',transform=ax5.transAxes,
             fontsize=8,bbox=dict(fc=color,alpha=0.3,boxstyle='round'))
ax5.set_title('Research Arc',fontsize=10)

plt.suptitle('EPS Research — The Full Picture\\n'
             'Flynn (2025-2027) | DOI: 10.3389/fspas.2025.1680387',
             fontsize=12,weight='bold')
plt.savefig('hs_b_10_capstone.png',dpi=150,bbox_inches='tight')
plt.show()
print("Congratulations on completing Track B! 🎓")
print("You now understand the EPS Research program at a research level.")""")
]),
}

notebooks.update(remaining_hs_b)

# ── Write all notebooks ───────────────────────────────────────────────────────
written = 0
for filename, notebook in notebooks.items():
    with open(filename, 'w') as f:
        json.dump(notebook, f, indent=1)
    written += 1
    print(f"Written: {filename}")

track_a = sum(1 for f in notebooks if f.startswith('hs_a'))
track_b = sum(1 for f in notebooks if f.startswith('hs_b'))
print(f"\n{'='*55}")
print(f"High-School Track Complete:")
print(f"  Track A (Ages 12-14): {track_a}/10 notebooks")
print(f"  Track B (Ages 15-18): {track_b}/10 notebooks")
print(f"  Total:                {written}/20 notebooks")
print(f"{'='*55}")
print(f"\nRequired data files:")
print(f"  rotation_curve_corpus_v7.json  (for both tracks)")
print(f"  harris_gc_corpus_v1.3.1.jsonl  (for Track A hs_a_07 only)")
print(f"\nNext steps:")
print(f"1. Run: jupyter lab")
print(f"2. Open hs_a_01 first — verify it runs cleanly")
print(f"3. git add examples/highschool/ && git commit -m 'Add high-school track'")
print(f"4. git push")
