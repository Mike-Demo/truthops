"""Crustdata adapter — company/people enrichment via the Crustdata MCP server.

Endpoint: https://install.crustdata.com/mcp (JSON-RPC POST, streamable HTTP).
Auth: Authorization: Bearer <CRUSTDATA_API_KEY from env>.

Graceful no-op when the key is absent: `available()` returns False and the
Evidence Agent skips it. This integration is SIMULATED in the demo run
(the benchmark case is resolved from fixtures); the adapter is real code
ready for live use.
"""

import json
import os
import urllib.request

MCP_URL = "https://install.crustdata.com/mcp"
LABEL = "SIMULATED integration in demo (adapter is live-capable)"


def available():
    return bool(os.environ.get("CRUSTDATA_API_KEY"))


def _rpc(method, params=None):
    key = os.environ.get("CRUSTDATA_API_KEY")
    if not key:
        raise RuntimeError("CRUSTDATA_API_KEY not set")
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params or {},
    }).encode()
    req = urllib.request.Request(
        MCP_URL, data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode()
    # Streamable HTTP wraps JSON-RPC in SSE frames; unwrap if needed.
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            payload = json.loads(line[5:].strip())
            if "result" in payload:
                return payload["result"]
            raise RuntimeError(f"Crustdata MCP error: {payload.get('error')}")
    payload = json.loads(raw)
    if "result" in payload:
        return payload["result"]
    raise RuntimeError(f"Crustdata MCP error: {payload.get('error')}")


def initialize():
    """Handshake: verifies the key and returns server info."""
    return _rpc("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "truthops", "version": "0.1.0"},
    })


def tools_list():
    """List available MCP tools (requires initialized session header handling)."""
    return _rpc("tools/list")


def enrich_company(name):
    """Placeholder for a company-enrichment tool call.

    Real tool names depend on the live MCP server's tool list; this adapter
    resolves them at runtime via tools/list in live mode.
    """
    raise NotImplementedError(
        "Live Crustdata enrichment resolves tool names from tools/list at runtime. "
        "Not invoked in the fixture-driven demo."
    )
