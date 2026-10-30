# Corpus keys (server 2.4.x)

| Key | Corpus | Objects | ID format |
|---|---|---|---|
| `v7` | Unified HI Rotation Curve Corpus v7.3 | 438 | `SPARC:NGC0024`, `THINGS:NGC3198`, `LITTLE_THINGS:DDO_210`, `WALLABY:...` |
| `dwarf` | Dwarf/Irregular HI Corpus v1.0 | 129 | `LVHIS:NGC55`, `VLA_ANGST:DDO6` |
| `gc` | Milky Way Globular Cluster Corpus v1.4.0 | 174 | `NGC 104` |
| `intz` | IntZ Kinematic Corpus v1.0 (KROSS + KMOS3D) | 1,292 | `KROSS:C-HiZ_z1_111` |
| `z1` | High-z ALPINE Kinematic Corpus Z1 v3 | 31 | `ALPINE:CG32` |
| | **Total** | **2,064** | |

Keys are lowercase. `semantic_search` also accepts `all`. Bare names
(`NGC0024`, `NGC 24`, `CG32`) work when unique within the corpus.

Examples (local server):

    GET http://127.0.0.1:8080/api/get_object?corpus=v7&object_id=NGC0024
    GET http://127.0.0.1:8080/api/list_objects?corpus=gc&limit=25
    GET http://127.0.0.1:8080/api/search_metadata?corpus=dwarf&field=survey&value=LVHIS
    GET http://127.0.0.1:8080/api/filter_objects?corpus=intz&field=z_spec&min=0.5&max=1.0
    GET http://127.0.0.1:8080/api/semantic_search?corpus=z1&query=confirmed%20rotator&top_k=5
