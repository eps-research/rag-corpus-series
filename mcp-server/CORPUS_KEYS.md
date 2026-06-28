# EPS Research Astro-RAG -- Corpus Keys v2.2.0

| Key   | Description                                       | Objects |
|-------|---------------------------------------------------|---------|
| v7    | Unified HI Rotation Curve Corpus v7.0             | ~300    |
| dwarf | Dwarf & Irregular Galaxy HI Corpus v1.0           | ~129    |
| gc    | Milky Way Globular Cluster Corpus v1.3.1          | 174     |
| intz  | IntZ High-z Kinematic Corpus (KROSS + KMOS3D)     | ~800    |
| z1    | High-z ALPINE Kinematic Corpus Z1 (z=4.26-5.68)  | 31      |

## Usage

Pass the key as the corpus parameter in any API call.
Keys are case-sensitive and must be lowercase.

## Example

    GET http://localhost:8080/api/get_object?corpus=v7&object_id=NGC3198
    GET http://localhost:8080/api/list_objects?corpus=gc&limit=25
    GET http://localhost:8080/api/search_metadata?corpus=dwarf&field=survey&value=THINGS

## Citation

Flynn, D.C. (2026). EPS Research Astro-RAG MCP Server v2.2.0.
Zenodo. https://doi.org/10.5281/zenodo.20985225
