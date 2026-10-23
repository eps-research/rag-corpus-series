"""Consistency between FAISS index text and the corpus records it describes.

Each index stores, next to its vectors, the text that was embedded for each
record (``<stem>_texts.json``). If a corpus is corrected but its index is not
rebuilt, semantic search ranks objects by *superseded* values while
``get_object`` serves the corrected record. The server therefore compares,
for every record, the numeric values written in the index text with the
values in the loaded record, and refuses semantic search on a corpus whose
index text disagrees (state ``stale``).

The same specifications drive the v7 text refresh in
``build_scripts/build_faiss_indexes.py``, so the check and the rebuild cannot
drift apart.
"""

from __future__ import annotations

import math
import re
from typing import Any, Callable, Optional

Getter = Callable[[dict], Any]


def _nested(*path: str) -> Getter:
    def get(r: dict) -> Any:
        cur: Any = r
        for p in path:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(p)
        return cur
    return get


def _z1_omega(r: dict) -> Any:
    om = r.get("omega") or {}
    return om.get("omega_value_rad_gyr") if om.get("omega_available") is True else None


# (label, regex with one value group, getter). The regex value group captures
# a number or the literal None; "None" in the text must match a null field.
_NUM = r"(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?|None)"

CONSISTENCY: dict[str, list[tuple[str, str, Getter]]] = {
    "v7": [
        ("distance_mpc", rf"\. distance {_NUM} Mpc", _nested("distance_mpc")),
        ("inc_deg", rf"\. inclination {_NUM} deg", _nested("inc_deg")),
        ("vrot_max_kms", rf"\. max rotation velocity {_NUM} km/s", _nested("vrot_max_kms")),
        ("vrot_mean_kms", rf"\. mean rotation velocity {_NUM} km/s", _nested("vrot_mean_kms")),
        ("r_min_kpc", rf"\. radial extent {_NUM} to", _nested("r_min_kpc")),
        ("r_max_kpc", rf"\. radial extent \S+ to {_NUM} kpc", _nested("r_max_kpc")),
        ("n_points", rf"\. n points {_NUM}\.", _nested("n_points")),
    ],
    "dwarf": [
        ("distance_mpc", rf"\. distance {_NUM} Mpc", _nested("distance_mpc")),
        ("inc_deg", rf"\. inclination {_NUM} deg", _nested("inc_deg")),
        ("vrot_max_kms", rf"\. max rotation velocity {_NUM} km/s", _nested("vrot_max_kms")),
        ("vrot_mean_kms", rf"\. mean rotation velocity {_NUM} km/s", _nested("vrot_mean_kms")),
    ],
    "gc": [
        ("metallicity.feh", rf"\[Fe/H\]={_NUM}", _nested("metallicity", "feh")),
        ("kinematics.v_r_kms", rf"radial velocity {_NUM} km/s", _nested("kinematics", "v_r_kms")),
        ("kinematics.sig_v_kms", rf"velocity dispersion {_NUM} km/s", _nested("kinematics", "sig_v_kms")),
    ],
    "intz": [
        ("redshift.z_spec", rf"redshift z={_NUM}", _nested("redshift", "z_spec")),
    ],
    "z1": [
        ("redshift", rf"redshift z={_NUM}", _nested("redshift")),
        ("omega.omega_value_rad_gyr", rf"\. omega {_NUM} rad/Gyr", _z1_omega),
    ],
}

# Fields the v7 refresh rewrites in the legacy grammar (the WALLABY and
# LITTLE THINGS corrections of HI corpus v7.2/v7.3 changed exactly these).
V7_REFRESH = [c for c in CONSISTENCY["v7"]]


def _as_number(v: Any) -> Optional[float]:
    if v is None or isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _same(text_val: str, rec_val: Any) -> bool:
    rv = _as_number(rec_val)
    if text_val == "None":
        return rv is None
    tv = float(text_val)
    if rv is None:
        return False
    return abs(tv - rv) <= 1e-6 * max(1.0, abs(rv))


KNOWN_ISSUES_MARK = ". known issues "
V7_CAVEAT_FIELDS = ("known_issues", "quality_notes", "notes", "correction_note")


def v7_caveats(record: dict) -> list[str]:
    """Current caveats of a v7 record, in a fixed order, for the index text.

    HI v7.3 keeps them in known_issues (list) and quality_notes, notes and
    correction_note (strings). The legacy index text listed caveats that v7.3
    corrected (e.g. SPARC 'thermal pressure', WALLABY 'H0=75'), so the
    rebuilt text takes them from the record instead.
    """
    out: list[str] = []
    for f in V7_CAVEAT_FIELDS:
        v = record.get(f)
        if isinstance(v, list):
            out.extend(str(x) for x in v if x)
        elif v:
            out.append(str(v))
    return out


def check_text(corpus: str, record: dict, text: str) -> list[str]:
    """Return the labels of fields whose value in ``text`` disagrees with ``record``.

    A field absent from the text is not checked (the text grammar varies by
    survey); a field present in the text must equal the record value.
    """
    bad = []
    for label, pattern, get in CONSISTENCY.get(corpus, []):
        m = re.search(pattern, text)
        if m and not _same(m.group(1), get(record)):
            bad.append(label)
    if corpus == "v7" and _V7_UNTRACEABLE.search(text):
        bad.append("omega_ready")
    if corpus == "v7" and KNOWN_ISSUES_MARK in text:
        if text.split(KNOWN_ISSUES_MARK, 1)[1] != str(v7_caveats(record)):
            bad.append("caveats")
    return bad


def format_value(v: Any, integer: bool = False) -> str:
    """Format a record value the way the legacy serializer did (Python str())."""
    if v is None or isinstance(v, bool):
        return str(v)
    if integer and float(v).is_integer():
        return str(int(v))
    return str(v)


# v7 legacy text asserted 'omega ready True/False' from a rule that was not
# preserved; HI v7.3 records carry no omega-readiness field, so the claim
# cannot be traced to the record and is removed from rebuilt text.
_V7_UNTRACEABLE = re.compile(r"\. omega ready (?:True|False|None)")


def refresh_v7_text(text: str, record: dict) -> str:
    """Rewrite the corrected numeric values of a legacy v7 text in place.

    The value groups of the V7_REFRESH patterns are replaced and the caveat
    list after 'known issues' is regenerated from the record (v7_caveats);
    every other character of the legacy text is preserved.
    """
    out = text
    for _label, pattern, get in V7_REFRESH:
        m = re.search(pattern, out)
        if not m:
            continue
        new = format_value(get(record), integer=(_label == "n_points"))
        if _same(m.group(1), get(record)):
            continue
        out = out[:m.start(1)] + new + out[m.end(1):]
    out = _V7_UNTRACEABLE.sub("", out)
    if KNOWN_ISSUES_MARK in out:
        out = out.split(KNOWN_ISSUES_MARK, 1)[0] + KNOWN_ISSUES_MARK + str(v7_caveats(record))
    return out
