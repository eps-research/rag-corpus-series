# Example Library

**EPS Research Astro-RAG Platform**

Executable Jupyter notebooks demonstrating corpus usage across all four corpora. All examples load directly from corpus JSON/CSV files with no external preprocessing, using only Python 3, numpy, and matplotlib.

## Structure

```
examples/
├── hi/           SPARC / Unified HI examples (~25 planned)
├── dwarfs/       Dwarf/Irregular examples (~25 planned)
├── gc/           Globular Cluster examples (~25 planned)
├── highz/        High-z Z1 examples (3 available now)
└── highschool/   High-School Exploration Track (~10 planned)
```

## Available Now

### High-z Examples (Silo 2)
| Notebook | Description | Status |
|----------|-------------|--------|
| `highz/hz_nb1_rotator_kinematics.ipynb` | J0817 [CII] rotation curve | ✅ Ready |
| `highz/hz_nb2_population_diversity.ipynb` | ALPINE population statistics | ✅ Ready |
| `highz/hz_nb3_eps_omega_bridge.ipynb` | Cross-corpus omega application | ✅ Ready |

## Coming Soon

### SPARC / HI Examples
| Example | Description |
|---------|-------------|
| `hi/ex01_ddo161_baryonic.ipynb` | DDO161 multi-component baryonic plot |
| `hi/ex02_wallaby_tier2.ipynb` | WALLABY Tier 2 rotation curve with caution zone |
| `hi/ex03_parameter_space.ipynb` | Corpus-level parameter space exploration |
| `hi/ex04_omega_correction.ipynb` | Omega correction applied to SPARC sample |
| `hi/ex05_sparc_vs_things.ipynb` | Cross-survey comparison |
| ... | ~20 more planned |

### Dwarf / Irregular Examples
| Example | Description |
|---------|-------------|
| `dwarfs/ex01_ddo154_omega.ipynb` | DDO154 omega computation |
| `dwarfs/ex02_omega_ready_sample.ipynb` | All 24 omega-ready LITTLE THINGS galaxies |
| `dwarfs/ex03_outer_gap_analysis.ipynb` | Outer gap distribution across 129 galaxies |
| ... | ~22 more planned |

### Globular Cluster Examples
| Example | Description |
|---------|-------------|
| `gc/ex01_ngc104_full_record.ipynb` | 47 Tuc four-survey record |
| `gc/ex02_proper_motion_query.ipynb` | Gaia EDR3 proper motion filtering |
| `gc/ex03_mass_metallicity.ipynb` | Baumgardt mass vs Harris [Fe/H] |
| ... | ~22 more planned |

### High-School Exploration Track
| Notebook | Description |
|----------|-------------|
| `highschool/hs01_what_is_a_galaxy.ipynb` | Introduction to galaxies |
| `highschool/hs02_rotation_curves.ipynb` | What is a rotation curve? |
| `highschool/hs03_dark_matter.ipynb` | The dark matter problem |
| `highschool/hs04_your_first_plot.ipynb` | Plot a real galaxy rotation curve |
| ... | ~6 more planned |

## Setup

```bash
pip install numpy matplotlib jupyter
jupyter lab
```

Download the relevant corpus JSON from Zenodo and place it in the same directory as the notebook before running.

---
*Part of the [EPS Research Astro-RAG Platform](../README.md)*
