"""Published-values anchor for the omega estimator (Reviewer 3, concern 5).

Flynn & Cannaliato (2025, Front. Astron. Space Sci. 12:1680387), Table 2, lists
omega for 84 SPARC galaxies in km/s/kpc, from the innermost and outermost
measured rings. Each must be reproduced to the published precision by the
server's own implementation from the stored v7.3 SPARC rings."""
import pytest
from astro_rag_mcp.omega import omega_kms_kpc
from astro_rag_mcp.server import build_service

PUBLISHED = [
    ("UGC09133", 1.97),
    ("UGC00128", 2.23),
    ("UGC06614", 2.49),
    ("UGC02487", 2.49),
    ("UGC01230", 2.74),
    ("NGC6674", 2.81),
    ("NGC5055", 2.89),
    ("UGC07125", 3.09),
    ("NGC0801", 3.32),
    ("NGC3198", 3.33),
    ("UGC05005", 3.38),
    ("UGC02885", 3.40),
    ("UGC05750", 3.44),
    ("NGC1003", 3.49),
    ("NGC2841", 3.58),
    ("NGC5371", 3.78),
    ("NGC5033", 3.79),
    ("NGC6503", 4.30),
    ("NGC2998", 4.61),
    ("DDO161", 4.69),
    ("NGC7331", 4.90),
    ("NGC4183", 4.92),
    ("F563-1", 5.02),
    ("F583-1", 5.16),
    ("NGC4100", 5.20),
    ("UGC11820", 5.21),
    ("NGC1090", 5.24),
    ("UGC03205", 5.27),
    ("UGC03546", 5.29),
    ("NGC4559", 5.30),
    ("UGC06930", 5.44),
    ("NGC4157", 5.46),
    ("NGC2955", 5.71),
    ("UGC06983", 5.74),
    ("UGC12732", 5.81),
    ("NGC6195", 5.83),
    ("UGC06786", 5.87),
    ("UGC00731", 5.99),
    ("NGC5985", 6.16),
    ("UGC11455", 6.24),
    ("UGC12632", 6.27),
    ("NGC2403", 6.32),
    ("NGC3893", 6.47),
    ("F568-3", 6.54),
    ("F568-V1", 6.55),
    ("NGC6946", 6.83),
    ("UGC08490", 6.95),
    ("NGC4088", 6.98),
    ("NGC2903", 7.01),
    ("NGC3741", 7.03),
    ("UGC06446", 7.11),
    ("F579-V1", 7.13),
    ("UGC07524", 7.15),
    ("ESO563-G021", 7.31),
    ("F574-1", 7.68),
    ("NGC5585", 8.06),
    ("UGC06917", 8.30),
    ("NGC7814", 8.52),
    ("NGC3917", 8.82),
    ("NGC0891", 8.99),
    ("F571-8", 9.17),
    ("IC4202", 9.30),
    ("UGC08550", 9.32),
    ("F583-4", 9.33),
    ("NGC0100", 9.37),
    ("NGC0024", 9.55),
    ("UGC08286", 9.82),
    ("NGC4217", 9.99),
    ("NGC3109", 10.24),
    ("NGC3521", 10.25),
    ("ESO079-G014", 10.37),
    ("F568-1", 10.52),
    ("ESO116-G012", 11.02),
    ("F563-V2", 11.08),
    ("UGC01281", 11.37),
    ("NGC7793", 11.40),
    ("UGC05721", 11.51),
    ("UGC07151", 12.53),
    ("UGC07323", 13.41),
    ("UGC04278", 13.76),
    ("NGC3972", 13.93),
    ("UGC07603", 14.20),
    ("UGC07399", 14.86),
    ("DDO064", 15.35)
]
S = build_service(None, semantic=False)


def test_table_has_84_galaxies():
    assert len(PUBLISHED) == 84


@pytest.mark.parametrize("name,published", PUBLISHED)
def test_published_sparc_omega_reproduces(name, published):
    lc = S.corpora["v7"]
    rows = [x for x in lc.records[lc.by_id[f"SPARC:{name}"]]["data"] if x.get("Vobs") is not None]
    w = omega_kms_kpc(rows[0]["Rad"], rows[0]["Vobs"], rows[-1]["Rad"], rows[-1]["Vobs"])
    # published to two decimals; allow one unit in the last digit
    assert abs(round(w, 2) - published) <= 0.0101, (name, published, w)
