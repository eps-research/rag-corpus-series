"""EPS Research Astro-RAG MCP Server.

One process serves the same corpus service over three interfaces:

* ``/mcp``    Model Context Protocol (Streamable HTTP, JSON-RPC 2.0), or stdio
* ``/api/*``  REST endpoints with OpenAPI documentation at ``/docs``
* ``/``       browser query interface

All seven operations are implemented once, in :mod:`astro_rag_mcp.corpus_service`,
and every interface calls that implementation, so MCP and REST results are
identical by construction (and checked by ``tests/test_parity.py``).
"""

__version__ = "2.4.1"
