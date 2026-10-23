"""Corpus registry and data-location rules.

Nothing here touches the network. The server reads corpus JSON files and FAISS
artifacts from a local data directory, located in this order:

1. ``--data-dir`` on the command line, or the ``ASTRO_RAG_DATA_DIR`` variable;
2. ``<mcp-server>/data``  (layout of the release ZIP and the Docker image);
3. the repository layout (``<repo>/examples/...`` and ``<repo>/faiss``).

Layout 2 is ``data/corpora/<file>`` and ``data/faiss/<stem>{.faiss,_ids.json,_texts.json}``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PACKAGE_DIR = Path(__file__).resolve().parent
SERVER_ROOT = PACKAGE_DIR.parent            # .../mcp-server
REPO_ROOT = SERVER_ROOT.parent              # .../rag-corpus-series (repo layout only)

EMBEDDING_MODEL = os.getenv(
    "ASTRO_RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
# Optional Hugging Face revision (commit hash) for the embedding model.
EMBEDDING_REVISION = os.getenv("ASTRO_RAG_EMBED_REVISION") or None
EMBEDDING_DIM = 384


@dataclass(frozen=True)
class CorpusSpec:
    key: str
    name: str
    description: str
    object_type: str
    redshift_range: str
    tracer: str
    zenodo_doi: str
    filename: str          # corpus JSON file name
    repo_subdir: str       # where the file lives in the repository (under examples/)
    container: str         # top-level list key in the JSON file
    faiss_stem: str        # FAISS artifact stem
    expected_records: int
    release_label: str     # fallback version label if the file carries none


CORPORA: dict[str, CorpusSpec] = {
    "v7": CorpusSpec(
        key="v7",
        name="Unified HI Rotation Curve Corpus",
        description="HI 21cm rotation curves from SPARC, THINGS, LITTLE THINGS and WALLABY DR2. Local universe.",
        object_type="galaxy",
        redshift_range="z ~ 0",
        tracer="HI 21cm (SPARC includes H-alpha)",
        zenodo_doi="10.5281/zenodo.23442703",
        filename="rotation_curve_corpus_v7.json",
        repo_subdir="hi",
        container="galaxies",
        faiss_stem="v7_sparc",
        expected_records=438,
        release_label="7.3",
    ),
    "dwarf": CorpusSpec(
        key="dwarf",
        name="Dwarf/Irregular HI Corpus",
        description="Dwarf and irregular galaxies; Local Volume HI 21cm kinematics.",
        object_type="galaxy",
        redshift_range="z ~ 0",
        tracer="HI 21cm",
        zenodo_doi="10.5281/zenodo.20320362",
        filename="dwarf_irregular_corpus_v1.json",
        repo_subdir="dwarfs",
        container="galaxies",
        faiss_stem="dwarf_corpus",
        expected_records=129,
        release_label="1.0",
    ),
    "gc": CorpusSpec(
        key="gc",
        name="Milky Way Globular Cluster Corpus",
        description="Milky Way globular clusters; Harris catalogue merged with Gaia EDR3, Baumgardt N-body and APOGEE DR17 parameters.",
        object_type="cluster",
        redshift_range="Milky Way",
        tracer="Multi-survey",
        zenodo_doi="10.5281/zenodo.22077426",
        filename="harris_gc_corpus_v1.4.0.json",
        repo_subdir="gc",
        container="clusters",
        faiss_stem="gc_corpus",
        expected_records=174,
        release_label="1.4.0",
    ),
    "intz": CorpusSpec(
        key="intz",
        name="IntZ Kinematic Corpus",
        description="KROSS and KMOS3D galaxies at intermediate redshift; H-alpha kinematics. Omega values withdrawn (omega_available=false).",
        object_type="galaxy",
        redshift_range="z ~ 0.38-2.68",
        tracer="H-alpha / [O III]",
        zenodo_doi="10.5281/zenodo.21841382",
        filename="intz_corpus_v1b.json",
        repo_subdir="intz",
        container="galaxies",
        faiss_stem="intz_corpus",
        expected_records=1292,
        release_label="1.0",
    ),
    "z1": CorpusSpec(
        key="z1",
        name="High-z ALPINE Kinematic Corpus Z1",
        description="ALPINE star-forming galaxies; ALMA [CII] 158um morpho-kinematics. Omega recomputed with canonical Eq. 6 (August 2026).",
        object_type="galaxy",
        redshift_range="z = 4.26-5.68",
        tracer="ALMA [CII] 158um",
        zenodo_doi="10.5281/zenodo.21834678",
        filename="high_z_kinematic_corpus_Z1.json",
        repo_subdir="highz",
        container="galaxies",
        faiss_stem="z1_corpus",
        expected_records=31,
        release_label="Z1 v3",
    ),
}

CORPUS_KEYS = list(CORPORA)
EXPECTED_TOTAL = sum(s.expected_records for s in CORPORA.values())   # 2064

CORRECTIONS_URL = "https://github.com/eps-research/rag-corpus-series/blob/main/CORRECTIONS.md"

# Scientific status notes attached to responses from the affected corpora so a
# client (human or LLM) cannot read a withdrawn value without seeing its status.
CORRECTION_NOTICES: dict[str, str] = {
    "v7": (
        "HI corpus v7.3 (2026-10-15) supersedes v7.0-v7.2: LITTLE THINGS model rows removed "
        "(v7.2) and WALLABY curves, geometry and distances re-sourced to the DR2 kinematic "
        "catalogue (v7.3). See CORRECTIONS.md (also in the release)."
    ),
    "dwarf": (
        "Dwarf/Irregular v1.0 LITTLE THINGS curves (26 galaxies, including all 24 omega-ready "
        "ones) contain Oh et al. (2015) pseudo-isothermal MODEL rows interleaved with the "
        "observed rows and stored as Vrot; summary fields of those records derive from the "
        "combined rows. The observed-only curves are the LITTLE_THINGS records of corpus v7 "
        "(HI v7.3). A corrected Dwarf release is pending. See CORRECTIONS.md (2 October 2026)."
    ),
    "intz": (
        "All 166 IntZ omega values were withdrawn in August 2026 (formula-implementation "
        "discrepancy and template-derived boundary points). Every record has "
        "omega.omega_available=false. Fields named legacy_omega_* hold the withdrawn "
        "values for provenance only and must not be used as measurements. "
        "See CORRECTIONS.md (also in the release)."
    ),
    "z1": (
        "Z1 omega values were recomputed with the canonical Eq. 6 on 2026-08-07; earlier "
        "negative values are withdrawn. Use omega.omega_value_rad_gyr only where "
        "omega.omega_available=true. See CORRECTIONS.md (also in the release)."
    ),
    "gc": (
        "GC v1.4.0 replaces releases v1.0-v1.3.3, which carried a fixed-width parsing "
        "defect (127 of 174 records changed). See CORRECTIONS.md (also in the release)."
    ),
}


@dataclass(frozen=True)
class DataLayout:
    root: Path
    kind: str  # "explicit", "release" or "repository"

    def corpus_path(self, spec: CorpusSpec) -> Path:
        if self.kind == "repository":
            return self.root / "examples" / spec.repo_subdir / spec.filename
        return self.root / "corpora" / spec.filename

    def faiss_dir(self) -> Path:
        return self.root / "faiss"

    def checksum_file(self) -> Path:
        return self.root / "SHA256SUMS"


def _is_release_dir(p: Path) -> bool:
    return (p / "corpora").is_dir() and (p / "faiss").is_dir()


def resolve_data_layout(data_dir: Optional[str] = None) -> DataLayout:
    """Find the local data directory. Raises FileNotFoundError with guidance."""
    explicit = data_dir or os.getenv("ASTRO_RAG_DATA_DIR")
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if _is_release_dir(p):
            return DataLayout(p, "explicit")
        if (p / "examples").is_dir() and (p / "faiss").is_dir():
            return DataLayout(p, "repository")
        raise FileNotFoundError(
            f"Data directory {p} must contain corpora/ and faiss/ subfolders "
            f"(or be a rag-corpus-series repository checkout)."
        )
    bundled = SERVER_ROOT / "data"
    if _is_release_dir(bundled):
        return DataLayout(bundled, "release")
    if (REPO_ROOT / "examples").is_dir() and (REPO_ROOT / "faiss").is_dir():
        return DataLayout(REPO_ROOT, "repository")
    raise FileNotFoundError(
        "No corpus data found. Expected either mcp-server/data/ (release ZIP) or a full "
        "clone of github.com/eps-research/rag-corpus-series. Run the server from inside the "
        "extracted release or the cloned repository, or pass --data-dir."
    )
