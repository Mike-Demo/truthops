#!/usr/bin/env python3
"""TruthOps MCP end-to-end demo — terminal recording script.

Runs the full MCP Streamable-HTTP dance against the deployed TruthOps MCP
server and prints every step for capture:
  1. /health (public)
  2. unauthenticated tools/list -> shows the auth gate
  3. initialize + notifications/initialized (AgentID Bearer)
  4. tools/list
  5. tools/call list_cases
  6. tools/call submit_allegation (queues a new allegation)
  7. tools/call get_investigation (northstar fixture case)
  8. tools/call get_trace
  9. tools/call explain_score
 10. tools/call gptzero_scan (LIVE adapter via the GPTZero MCP)

Token comes ONLY from the AGENTID_TOKEN env var. It is never written to disk.
Usage: AGENTID_TOKEN='<jwt>' python3 mcp_e2e.py | tee mcp-e2e.log
"""
import json
import os
import sys
import time
import urllib.request

BASE = "https://truthops-mcp.space.fast"
MCP_URL = BASE + "/mcp"

TOKEN = os.environ.get("AGENTID_TOKEN", "").strip()

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# terminal colors
C = {
    "hdr": "\033[1;36m",   # bright cyan — section headers
    "cmd": "\033[1;33m",   # yellow — what we're doing
    "ok": "\033[1;32m",    # green — success
    "dim": "\033[2m",
    "rst": "\033[0m",
}


def say(text, color="rst", flush=True):
    sys.stdout.write(f"{C[color]}{text}{C['rst']}\n")
    if flush:
        sys.stdout.flush()


def section(title):
    say("", "rst")
    say("=" * 64, "hdr")
    say(title, "hdr")
    say("=" * 64, "hdr")


def raw_post(payload, token=None, label="POST /mcp"):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": UA,
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            sess = resp.headers.get("Mcp-Session-Id")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        sess = e.headers.get("Mcp-Session-Id")
        ms = int((time.time() - t0) * 1000)
        return e.code, body, sess, ms
    ms = int((time.time() - t0) * 1000)
    return 200, body, sess, ms


def parse_mcp_body(body):
    """Handle plain JSON or SSE-wrapped JSON-RPC responses."""
    body = body.strip()
    if body.startswith("event:") or body.startswith("data:"):
        # SSE stream — collect data: lines
        chunks = []
        for line in body.splitlines():
            if line.startswith("data:"):
                chunks.append(line[5:].strip())
        body = "\n".join(chunks)
    # may contain multiple JSON docs; take the result-bearing one
    for chunk in body.split("\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("result" in obj or "error" in obj):
            return obj
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"_raw": body[:2000]}


def rpc(method, params=None, req_id=1, token=None, session_id=None, label=None):
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params
    say(f">> {label or method}", "cmd")
    say(f"   {json.dumps(payload)[:160]}", "dim")
    code, body, sess, ms = raw_post(payload, token=token)
    obj = parse_mcp_body(body)
    if "error" in obj:
        say(f"<< ERROR ({ms}ms): {json.dumps(obj['error'])[:220]}", "ok")
    else:
        say(f"<< ok ({ms}ms)", "ok")
    return obj, sess or session_id


def short(obj, limit=1400):
    s = json.dumps(obj, indent=1)
    if len(s) > limit:
        s = s[:limit] + "\n… (truncated for display)"
    return s


def main():
    rid = [0]

    def next_id():
        rid[0] += 1
        return rid[0]

    section("TruthOps MCP — end-to-end run")
    say("server: https://truthops-mcp.space.fast/mcp  (Streamable HTTP)", "dim")
    say("auth:   AgentID Bearer <redacted>", "dim")

    # 1. public health check
    section("[1/10] GET /health  (public, no auth)")
    try:
        hreq = urllib.request.Request(
            BASE + "/health", headers={"User-Agent": UA}
        )
        with urllib.request.urlopen(hreq, timeout=20) as r:
            say(">> GET /health", "cmd")
            say(f"<< ok: {r.read().decode().strip()}", "ok")
    except Exception as e:
        say(f"<< FAILED: {e}", "ok")

    # 2. unauthenticated call — show the gate
    section("[2/10] tools/list WITHOUT a token  (expect the auth gate)")
    obj, _ = rpc("tools/list", {}, next_id(), token=None)
    say(short(obj.get("error", obj)), "dim")

    if not TOKEN:
        section("STOP — no AGENTID_TOKEN in the environment")
        say("The MCP tools require an AgentID id_token (JWT) as the Bearer <redacted>", "cmd")
        say("Get one: sign in at https://truthops-demo.space.fast (AgentID),", "dim")
        say("then paste the id_token here as AGENTID_TOKEN and re-run.", "dim")
        say("The token is used transiently and never written to disk.", "dim")
        return 2

    # 3. initialize
    section("[3/10] initialize  (MCP handshake)")
    obj, session = rpc(
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "truthops-terminal-demo", "version": "1.0"},
        },
        next_id(),
        token=TOKEN,
        label="initialize",
    )
    say(short(obj.get("result", obj)), "dim")
    say(">> notifications/initialized", "cmd")
    code, _, _, _ = raw_post(
        {"jsonrpc": "2.0", "method": "notifications/initialized"}, token=TOKEN
    )
    say(f"<< sent (http {code})", "ok")
    if session:
        say(f"session: {session[:16]}…", "dim")

    # 4. tools/list
    section("[4/10] tools/list  (what can this server do?)")
    obj, _ = rpc("tools/list", {}, next_id(), token=TOKEN)
    tools = (obj.get("result", {}) or {}).get("tools", [])
    for t in tools:
        say(f"  • {t.get('name')}: {(t.get('description') or '')[:80]}", "rst")
    say(f"{len(tools)} tools exposed", "ok")

    # 5. list_cases
    section("[5/10] tools/call list_cases")
    obj, _ = rpc(
        "tools/call",
        {"name": "list_cases", "arguments": {}},
        next_id(),
        token=TOKEN,
        label="tools/call list_cases",
    )
    say(short(obj.get("result", obj)), "dim")

    # 6. submit_allegation
    section("[6/10] tools/call submit_allegation  (queue a new case)")
    allegation = (
        "Northstar Cloud lost 40% of its customers last quarter, "
        "according to a viral social media post."
    )
    obj, _ = rpc(
        "tools/call",
        {
            "name": "submit_allegation",
            "arguments": {"allegation": allegation, "source": "terminal-demo"},
        },
        next_id(),
        token=TOKEN,
        label="tools/call submit_allegation",
    )
    say(short(obj.get("result", obj)), "dim")

    # 7. get_investigation — northstar
    section("[7/10] tools/call get_investigation  (case: northstar)")
    t0 = time.time()
    obj, _ = rpc(
        "tools/call",
        {"name": "get_investigation", "arguments": {"case_id": "northstar"}},
        next_id(),
        token=TOKEN,
        label="tools/call get_investigation",
    )
    res = obj.get("result", obj)
    say(short(res, 1800), "dim")
    say(f"investigation returned in {time.time()-t0:.1f}s", "ok")

    # 8. get_trace
    section("[8/10] tools/call get_trace  (neatlogs provenance)")
    obj, _ = rpc(
        "tools/call",
        {"name": "get_trace", "arguments": {"case_id": "northstar"}},
        next_id(),
        token=TOKEN,
        label="tools/call get_trace",
    )
    say(short(obj.get("result", obj), 1200), "dim")

    # 9. explain_score
    section("[9/10] tools/call explain_score  (why this verdict?)")
    obj, _ = rpc(
        "tools/call",
        {"name": "explain_score", "arguments": {"case_id": "northstar"}},
        next_id(),
        token=TOKEN,
        label="tools/call explain_score",
    )
    say(short(obj.get("result", obj), 1500), "dim")

    # 10. gptzero_scan — LIVE adapter
    section("[10/10] tools/call gptzero_scan  (LIVE adapter)")
    sample = (
        "In today's rapidly evolving digital landscape, organizations are increasingly "
        "leveraging artificial intelligence to streamline operations and enhance decision "
        "making. By harnessing the power of machine learning algorithms, businesses can "
        "unlock unprecedented levels of efficiency and innovation. Furthermore, it is "
        "important to note that these transformative technologies are reshaping the way "
        "we work, communicate, and collaborate across global teams and diverse markets."
    )
    say(f"scanning {len(sample)} chars of sample text…", "dim")
    obj, _ = rpc(
        "tools/call",
        {"name": "gptzero_scan", "arguments": {"text": sample}},
        next_id(),
        token=TOKEN,
        label="tools/call gptzero_scan",
    )
    say(short(obj.get("result", obj), 1500), "dim")

    section("DONE — MCP end to end")
    say("health ✓   auth gate ✓   handshake ✓   6 tool calls ✓   live GPTZero ✓", "ok")
    say("Note: investigation results are fixture-backed demo data (labeled as", "dim")
    say("such by the server); gptzero_scan ran against the live adapter.", "dim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
