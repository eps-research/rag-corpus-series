#!/usr/bin/env python3
"""
Reproducible FAIR² FAISS builder.

The July 2026 FAISS serializer was not preserved in Git. Four historical
text sidecars are therefore retained as frozen serialization baselines.

Migration policy
----------------
v7:
    preserve legacy retrieval text exactly;
    canonical ID = survey:galaxy.

dwarf:
    preserve legacy retrieval text exactly;
    canonical ID = survey:galaxy.

IntZ:
    preserve KROSS text exactly;
    for KMOS3D replace only the missing "Galaxy ." identifier with the
    canonical identifiers.id value;
    canonical ID = identifiers.survey:(name or id).

Z1:
    preserve legacy text exactly except append canonical omega metadata only
    where omega_available=True and correction_date=2026-08-07;
    canonical ID = survey:galaxy.

GC:
    regenerate retrieval text from corrected v1.4.0 scientific fields because
    the legacy sidecar contains stale Harris-parser values;
    canonical ID = cluster_id.

Embedding:
    sentence-transformers/all-MiniLM-L6-v2
    384 dimensions
    FAISS IndexFlatL2
"""

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "build_scripts" / "faiss_legacy_texts"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

SPECS = {
    "v7": {
        "source": ROOT / "examples/hi/rotation_curve_corpus_v7.json",
        "container": "galaxies",
        "stem": "v7_sparc",
        "count": 438,
    },
    "intz": {
        "source": ROOT / "examples/intz/intz_corpus_v1b.json",
        "container": "galaxies",
        "stem": "intz_corpus",
        "count": 1292,
    },
    "gc": {
        "source": ROOT / "examples/gc/harris_gc_corpus_v1.4.0.json",
        "container": "clusters",
        "stem": "gc_corpus",
        "count": 174,
    },
    "z1": {
        "source": ROOT / "examples/highz/high_z_kinematic_corpus_Z1.json",
        "container": "galaxies",
        "stem": "z1_corpus",
        "count": 31,
    },
    "dwarf": {
        "source": ROOT / "examples/dwarfs/dwarf_irregular_corpus_v1.json",
        "container": "galaxies",
        "stem": "dwarf_corpus",
        "count": 129,
    },
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, obj):
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def canonical_id(kind, r):
    if kind == "gc":
        return str(r["cluster_id"])

    if kind == "intz":
        d = r["identifiers"]
        obj = d.get("name") or d.get("id")
        return f'{d["survey"]}:{obj}'

    return f'{r["survey"]}:{r["galaxy"]}'


def legacy_texts(stem):
    p = BASE / f"{stem}_texts.json"
    if not p.exists():
        raise RuntimeError(f"missing frozen baseline: {p}")
    return load_json(p)


def gc_text(r):
    p = r.get("position") or {}
    m = r.get("metallicity") or {}
    k = r.get("kinematics") or {}
    s = r.get("structure") or {}
    f = r.get("flags") or {}
    b = r.get("baumgardt2023") or {}
    a = r.get("apogee_dr17") or {}

    # Preserve the historical GC text grammar while sourcing values from
    # the corrected v1.4.0 record.
    text = (
        f'Globular cluster {r.get("cluster_id")}. '
        f'alt name {r.get("alt_name")}. '
        f'galactic coordinates l={p.get("l_deg")} b={p.get("b_deg")}. '
        f'metallicity [Fe/H]={m.get("feh")}. '
        f'reddening E(B-V)={m.get("ebv")}. '
        f'radial velocity {k.get("v_r_kms")} km/s. '
        f'velocity dispersion {k.get("sig_v_kms")} km/s. '
        f'core collapsed {s.get("core_collapsed")}. '
        f'king concentration {s.get("king_concentration")}. '
        f'inner galaxy {f.get("inner_galaxy")}. '
        f'sgr stream {f.get("sgr_stream")}'
    )

    if b.get("mass_msun") is not None:
        text += f'. dynamical mass {b.get("mass_msun")} Msun'

    if b.get("r_gc_kpc") is not None:
        text += f'. galactocentric distance {b.get("r_gc_kpc")} kpc'

    if a.get("feh_apogee") is not None:
        text += f'. APOGEE [Fe/H] {a.get("feh_apogee")}'

    return text


def build_texts(kind, rows):
    stem = SPECS[kind]["stem"]

    if kind == "gc":
        return [gc_text(r) for r in rows]

    old = legacy_texts(stem)

    if len(old) != len(rows):
        raise RuntimeError(
            f"{kind}: baseline count {len(old)} != corpus count {len(rows)}"
        )

    if kind in ("v7", "dwarf"):
        return list(old)

    if kind == "intz":
        out = []
        changed = 0

        for i, (r, text) in enumerate(zip(rows, old)):
            d = r["identifiers"]
            survey = d["survey"]

            if survey == "KROSS":
                out.append(text)
                continue

            if survey != "KMOS3D":
                raise RuntimeError(
                    f"intz row {i}: unexpected survey {survey!r}"
                )

            obj = d.get("name") or d.get("id")
            if not obj:
                raise RuntimeError(
                    f"intz row {i}: missing canonical object identifier"
                )

            prefix = "Galaxy ."
            if not text.startswith(prefix):
                raise RuntimeError(
                    f"intz row {i}: expected legacy missing-name prefix"
                )

            new = f"Galaxy {obj}." + text[len(prefix):]

            if new != text:
                changed += 1

            out.append(new)

        if changed != 706:
            raise RuntimeError(
                f"intz: expected 706 text corrections, found {changed}"
            )

        return out

    if kind == "z1":
        out = []
        changed = 0

        for i, (r, text) in enumerate(zip(rows, old)):
            omg = r.get("omega") or {}

            available = omg.get("omega_available") is True
            date = omg.get("correction_date")

            if not available:
                out.append(text)
                continue

            if date != "2026-08-07":
                raise RuntimeError(
                    f"z1 row {i}: available omega lacks expected "
                    f"2026-08-07 correction date"
                )

            value = omg.get("omega_value_rad_gyr")
            quality = omg.get("omega_quality")
            formula = omg.get("formula_version")

            if value is None or not quality or not formula:
                raise RuntimeError(
                    f"z1 row {i}: incomplete canonical omega metadata"
                )

            suffix = (
                f". omega {value} rad/Gyr"
                f". omega quality {quality}"
                f". omega formula {formula}"
            )

            new = text + suffix

            if new != text:
                changed += 1

            out.append(new)

        if changed != 8:
            raise RuntimeError(
                f"z1: expected 8 corrected omega texts, found {changed}"
            )

        return out

    raise RuntimeError(f"unknown corpus kind: {kind}")


def prepare(kind):
    spec = SPECS[kind]
    doc = load_json(spec["source"])
    rows = doc[spec["container"]]

    if len(rows) != spec["count"]:
        raise RuntimeError(
            f'{kind}: expected {spec["count"]} records, found {len(rows)}'
        )

    ids = [canonical_id(kind, r) for r in rows]
    texts = build_texts(kind, rows)

    if len(ids) != len(texts):
        raise RuntimeError(f"{kind}: ID/text length mismatch")

    if len(ids) != len(set(ids)):
        raise RuntimeError(f"{kind}: duplicate canonical IDs")

    bad = [
        x for x in ids
        if not str(x).strip()
        or str(x).endswith(":None")
        or re.fullmatch(r"\d+", str(x))
    ]
    if bad:
        raise RuntimeError(f"{kind}: invalid IDs: {bad[:10]}")

    if any(not isinstance(t, str) or not t.strip() for t in texts):
        raise RuntimeError(f"{kind}: invalid blank text")

    return rows, ids, texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--only",
        default="all",
        choices=["all", *SPECS.keys()],
    )
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--text-only", action="store_true")
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    kinds = list(SPECS) if args.only == "all" else [args.only]
    prepared = {}

    for kind in kinds:
        rows, ids, texts = prepare(kind)
        stem = SPECS[kind]["stem"]

        write_json(out / f"{stem}_ids.json", ids)
        write_json(out / f"{stem}_texts.json", texts)

        prepared[kind] = (rows, ids, texts)

        print(
            f"{kind:6s}: rows={len(ids):4d} "
            f"unique={len(set(ids)):4d}"
        )

    if args.text_only:
        print("text-only build: PASS")
        return

    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL, local_files_only=True)

    try:
        dim = model.get_embedding_dimension()
    except AttributeError:
        dim = model.get_sentence_embedding_dimension()

    if dim != 384:
        raise RuntimeError(f"embedding dimension {dim}, expected 384")

    for kind in kinds:
        _, ids, texts = prepared[kind]
        stem = SPECS[kind]["stem"]

        vec = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=False,
        ).astype("float32", copy=False)

        if vec.shape != (len(texts), 384):
            raise RuntimeError(
                f"{kind}: unexpected vector shape {vec.shape}"
            )

        if not np.isfinite(vec).all():
            raise RuntimeError(f"{kind}: non-finite embeddings")

        index = faiss.IndexFlatL2(384)
        index.add(vec)

        if index.ntotal != len(texts):
            raise RuntimeError(
                f"{kind}: ntotal={index.ntotal}, expected {len(texts)}"
            )

        path = out / f"{stem}.faiss"
        faiss.write_index(index, str(path))

        reread = faiss.read_index(str(path))

        if reread.ntotal != len(texts):
            raise RuntimeError(f"{kind}: reread ntotal failure")

        if reread.d != 384:
            raise RuntimeError(f"{kind}: reread dimension failure")

        print(
            f"{kind:6s}: FAISS ntotal={reread.ntotal} "
            f"dim={reread.d}"
        )

    total = sum(len(prepared[k][1]) for k in kinds)

    if args.only == "all" and total != 2064:
        raise RuntimeError(
            f"expected 2064 vectors, found {total}"
        )

    print(f"vector total: {total}")

    if args.install:
        dest = ROOT / "faiss"

        for kind in kinds:
            stem = SPECS[kind]["stem"]

            for suffix in (
                ".faiss",
                "_ids.json",
                "_texts.json",
            ):
                src = out / f"{stem}{suffix}"
                dst = dest / f"{stem}{suffix}"
                tmp = Path(str(dst) + ".new")

                shutil.copy2(src, tmp)
                tmp.replace(dst)

        print("install: PASS")


if __name__ == "__main__":
    main()
