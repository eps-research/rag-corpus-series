"""Documentation links and release packaging rules."""

import sys

from .conftest import SERVER_ROOT

sys.path.insert(0, str(SERVER_ROOT / "tools"))
from build_release import REPO_FILES, broken_links, program_files  # noqa: E402


def test_no_broken_relative_links_in_repository_docs():
    assert broken_links(SERVER_ROOT) == []


def test_manifest_lists_every_program_file_and_they_exist():
    files = program_files()
    assert "CITATION.cff" in files and "launch.py" in files
    assert all((SERVER_ROOT / f).is_file() for f in files)


def test_bundled_repository_files_exist():
    """Repository layout: one level up. Release layout: bundled next to the code."""
    for f in REPO_FILES:
        assert (SERVER_ROOT / f).is_file() or (SERVER_ROOT.parent / f).is_file(), f
