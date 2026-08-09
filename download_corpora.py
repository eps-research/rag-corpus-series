#!/usr/bin/env python3
"""
EPS Research Astro-RAG Platform — Corpus Downloader
Downloads all four EPS Research corpora from Zenodo.

Usage:
    python download_corpora.py              # download all
    python download_corpora.py --corpus hi  # download one corpus

Flynn, D.C. (2026) | github.com/eps-research/rag-corpus-series
"""

import os
import sys
import urllib.request
import argparse

CORPORA = {
    'hi': {
        'name': 'Unified HI Rotation Curve Corpus v7.1',
        'doi': '10.5281/zenodo.19563417',
        'files': [
            ('https://zenodo.org/records/19563417/files/rotation_curve_corpus_v7.json',
             'rotation_curve_corpus_v7.json'),
            ('https://zenodo.org/records/19563417/files/rotation_curve_corpus_v7.1_flat.csv',
             'rotation_curve_corpus_v7.1_flat.csv'),
        ],
        'dest': 'examples/hi/'
    },
    'dwarfs': {
        'name': 'Dwarf/Irregular HI Corpus v1.0',
        'doi': '10.5281/zenodo.20320362',
        'files': [
            ('https://zenodo.org/records/20320362/files/dwarf_irregular_corpus_v1.json',
             'dwarf_irregular_corpus_v1.json'),
            ('https://zenodo.org/records/20320362/files/dwarf_irregular_corpus_v1_flat.csv',
             'dwarf_irregular_corpus_v1_flat.csv'),
        ],
        'dest': 'examples/dwarfs/'
    },
    'gc': {
        'name': 'Milky Way Globular Cluster Corpus v1.3.1',
        'doi': '10.5281/zenodo.19907766',
        'files': [
            ('https://zenodo.org/records/19907766/files/harris_gc_corpus_v1.3.1.jsonl',
             'harris_gc_corpus_v1.3.1.jsonl'),
        ],
        'dest': 'examples/gc/'
    },
    'intz': {
        'name': 'EPS Research Intermediate-z Kinematic Corpus v1.0 (IntZ_v1)',
        'doi': '10.5281/zenodo.21841382',  # corrected v2 — omega nulled Aug 2026
        'files': [
            ('https://zenodo.org/records/21841382/files/intz_corpus_v1b.json',
             'intz_corpus_v1b.json'),
            ('https://zenodo.org/records/21841382/files/intz_corpus_v1b_flat.csv',
             'intz_corpus_v1b_flat.csv'),
            ('https://zenodo.org/records/21841382/files/intz_corpus_v1b.jsonl',
             'intz_corpus_v1b.jsonl'),
        ],
        'dest': 'examples/intz/'
    },
    'highz': {
        'name': 'High-z Kinematic Corpus Z1',
        'doi': '10.5281/zenodo.21834678',  # corrected v3 — Aug 2026
        'files': [
            ('https://zenodo.org/records/21834678/files/high_z_kinematic_corpus_Z1.json',
             'high_z_kinematic_corpus_Z1.json'),
        ],
        'dest': 'examples/highz/'
    }
}

# QuickStart needs all four in root directory too
QUICKSTART_FILES = [
    ('hi',     'rotation_curve_corpus_v7.json',        '.'),
    ('dwarfs', 'dwarf_irregular_corpus_v1.json',       '.'),
    ('gc',     'harris_gc_corpus_v1.3.1.jsonl',        '.'),
    ('highz',  'high_z_kinematic_corpus_Z1.json',      '.'),
]

def download_file(url, dest_path, force=False):
    if os.path.exists(dest_path) and not force:
        print(f'  Already exists: {dest_path} (use --force to overwrite)')
        return True
    if os.path.exists(dest_path) and force:
        print(f'  Overwriting: {dest_path}')
    print(f'  Downloading {os.path.basename(dest_path)}...')
    try:
        urllib.request.urlretrieve(url, dest_path)
        size = os.path.getsize(dest_path) / 1024 / 1024
        print(f'  Done: {dest_path} ({size:.1f} MB)')
        return True
    except Exception as e:
        print(f'  FAILED: {e}')
        return False

def download_corpus(key, force=False):
    corpus = CORPORA[key]
    print(f'\n{corpus["name"]}')
    print(f'DOI: {corpus["doi"]}')
    os.makedirs(corpus['dest'], exist_ok=True)
    for url, filename in corpus['files']:
        dest = os.path.join(corpus['dest'], filename)
        download_file(url, dest, force=force)

def main():
    parser = argparse.ArgumentParser(description='Download EPS Research corpora')
    parser.add_argument('--corpus', choices=list(CORPORA.keys()) + ['all'],
                        default='all', help='Which corpus to download')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing files (always use for remediation-sensitive corpora)')
    parser.add_argument('--quickstart', action='store_true',
                        help='Also copy files to root for QuickStart.ipynb')
    args = parser.parse_args()

    print('EPS Research Astro-RAG Platform — Corpus Downloader')
    print('=' * 55)

    if args.corpus == 'all':
        for key in CORPORA:
            download_corpus(key, force=args.force)
    else:
        download_corpus(args.corpus)

    if args.quickstart or args.corpus == 'all':
        print('\nCopying files for QuickStart.ipynb...')
        for corpus_key, filename, dest_dir in QUICKSTART_FILES:
            src = os.path.join(CORPORA[corpus_key]['dest'], filename)
            dst = os.path.join(dest_dir, filename)
            if os.path.exists(src):
                import shutil
                shutil.copy2(src, dst)
                print(f'  Copied: {filename}')

    print('\nDone. Launch JupyterLab and open QuickStart.ipynb to begin.')

if __name__ == '__main__':
    main()
