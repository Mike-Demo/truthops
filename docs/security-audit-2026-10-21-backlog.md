# Security audit triage — 2026-10-21

Parent: https://github.com/Mike-Demo/truthops/issues/1

This is the ready-to-file fallback because this session has no issue-creation
tool. No child issues have been filed and no finding has been fixed.
The supplied audit used the Cloudflare security-audit skill, quick profile,
with static source inspection only: no code execution or deployed-endpoint
probing. The leads below remain unconfirmed.

## Prioritized confirmed backlog

Both findings retain the audit's **medium** severity. They have distinct root
causes and need separate issues; the image-size finding and the SSRF lead share
a download path, not a root cause.

| Order | Finding | Real-world risk and reachability | Fix size and safety |
| --- | --- | --- | --- |
| 1 | Unbounded live image download | A lower-trust image server can exhaust operator memory when its URL is selected from search results in live photo acquisition. No package-publishing control is required. Fixture images take precedence, limiting exposure to the remote-download path. | Small, localized bounded-read change; preserve the current minimum, maximum, and graceful failure behavior. |
| 2 | Unpinned Alexandria CLI | A malicious future package release can execute with operator privileges and inherited provider credentials. Potential impact is broader than memory exhaustion, but exploitation requires control of a release resolved by `firecrawl-cli@latest` and an operator invocation, rather than merely hosting an image. No malicious release or credential theft is established. | An integrity-verified committed install can preserve the CLI interface but adds dependency-management work. Reusing the existing REST adapter avoids runtime package execution but requires compatibility checks. |

Reachability determines the order at equal severity; the smaller, safer image
fix reinforces it. If package compromise is established, reassess the CLI
finding's priority.

## Ready-to-file issue 1

### Title

[security][medium] Bound live photo downloads before buffering

### Body

Parent audit: https://github.com/Mike-Demo/truthops/issues/1

**Status:** Confirmed by static inspection; medium; priority 1 of 2.
**Fingerprint:** `truthops/live-photo-download-unbounded-read`

**Evidence:** In `/home/runner/work/truthops/truthops/truthops/evidence_agent.py`,
`_acquire_claim_image` selects direct image URLs from search results
(lines 350–369), opens the selected URL with a 15-second timeout
(lines 380–383), and checks Content-Type before calling `resp.read()` without
a size argument (lines 384–387). The 1,024-byte minimum and
`50 * 1024 * 1024`-byte maximum are checked only afterward (lines 388–390).
There is no Content-Length pre-check or streaming cap on this path.

**Impact and reachability:** An untrusted server serving an accepted
search-result image URL can make a live photo acquisition allocate far beyond
the stated 50 MB ceiling, potentially exhausting the operator process.
The fixture-image path takes precedence. The socket timeout applies to
blocking reads, not total response size; no deployed exhaustion was tested.

**Root cause:** The limit is a post-buffer validation, not an enforced
download bound.

**Smallest fix:** In `_acquire_claim_image`, reject early when a declared
Content-Length exceeds `50 * 1024 * 1024` bytes. Read into a bytearray in
bounded chunks, limiting each read to the remaining allowance plus one byte
to detect overflow, and abort immediately on exceeding the cap. Enforce the
streamed limit even when Content-Length is absent, malformed, or understates
the body. Preserve Content-Type checks, the 1,024-byte minimum, the bytes
return type, response closure, and graceful `(None, None)` failure.

**Acceptance criteria for the remediation PR:**

- [ ] Mock responses verify acceptance at 1,024 bytes and exactly the cap,
  and rejection below the minimum or above the cap.
- [ ] An oversized declared Content-Length is rejected without reading the body.
- [ ] Missing, malformed, or understated Content-Length cannot bypass the cap;
  no unbounded `read()` is used.
- [ ] Oversized streams stop after at most the cap plus one byte is consumed;
  responses close on rejection and existing fixture behavior is unchanged.

## Ready-to-file issue 2

### Title

[security][medium] Remove unpinned Alexandria CLI execution

### Body

Parent audit: https://github.com/Mike-Demo/truthops/issues/1

**Status:** Confirmed by static inspection; medium; priority 2 of 2.
**Fingerprint:** `truthops/alexandria-npx-unpinned-latest`

**Evidence:** `/home/runner/work/truthops/truthops/truthops/evidence/alexandria_adapter.py:21`
defines `CLI = ["npx", "-y", "firecrawl-cli@latest"]`.
`available()` (lines 28–30), `search_primary_sources()` (lines 42–45),
and `scrape_source()` (lines 92–95) invoke it through `subprocess.run`
without `env=`, inheriting the operator environment. There is no committed
version/integrity-verified install for this invocation. Sibling adapters read
provider credentials from that environment:
`/home/runner/work/truthops/truthops/truthops/evidence/firecrawl_adapter.py:20–27`
and `/home/runner/work/truthops/truthops/truthops/evidence/sightengine_adapter.py:18–19`.
The existing REST search and scrape methods are in
`/home/runner/work/truthops/truthops/truthops/evidence/firecrawl_adapter.py:50–57`.

**Impact and reachability:** A future malicious registry publish selected by
the mutable `latest` tag can execute under the operator account with access
to inherited credentials. Auto-confirmation permits installation without
review, including during the availability probe. This requires control of
the resolved package release and an operator invocation; search-result
control alone does not establish exploitation. No compromised package or
credential theft is claimed.

**Root cause:** Runtime execution of an automatically accepted, mutable
package with no repository-controlled version or integrity verification,
combined with inherited operator credentials.

**Smallest fix:** Replace the mutable runtime install with an exact
`firecrawl-cli` version installed from a committed, integrity-verified
dependency lock and invoke that installed CLI without a download fallback.
An exact version string alone does not satisfy the integrity requirement.
Alternatively, remove the CLI and reuse the existing Firecrawl REST adapter,
preserving Alexandria's result contract and graceful failure behavior.
If retaining a subprocess, restrict its environment to required variables
and Firecrawl credentials rather than unrelated provider secrets as
defense in depth; environment filtering alone does not fix mutable execution.

**Acceptance criteria for the remediation PR:**

- [ ] Availability, search, and scrape no longer execute `npx -y firecrawl-cli@latest`
  or any unverified runtime package download.
- [ ] The CLI option has an exact version and committed integrity-verified
  install; the REST option removes runtime CLI execution entirely.
- [ ] Mocked tests preserve availability, normalized search results, scrape
  output, and graceful behavior for missing credentials/tools or provider errors.
- [ ] If a subprocess remains, tests verify unrelated provider credentials
  are not inherited.

## Ready-to-file validation checklist issue

### Title

[security][needs-validation] Audit leads to validate

### Body

Parent audit: https://github.com/Mike-Demo/truthops/issues/1

These are unconfirmed leads, not confirmed findings. No severity is assigned.
Record the missing facts and supporting evidence before promoting or rejecting
either lead. Do not copy passwords, private keys, or sensitive service details
into this issue; use redacted evidence or access-controlled references.
Deployment checks require operator authorization; none were performed in
the static audit or this triage.

- [ ] **PKCS#12 password for the report-signing key is a literal in five committed scripts**
  - Fingerprint: `truthops/hardcoded-p12-signing-password`
  - Claimed root cause: Committed scripts call
    `pkcs12.load_key_and_certificates` with a hard-coded literal password
    rather than an environment or secret-store value, and the keypair may
    not have been rotated.
  - **Exact missing fact:** Whether the truthops.p12 key file (stored outside the repo under ~/workspace/truthops-demo/certs) is obtainable by anyone other than the operator (backups, shared workspace copies, other commits/repos), and whether that keypair is still used to sign published reports or has been rotated.
  - Validation record: Obtain operator confirmation of key-file access and
    distribution, current report-signing use, and rotation status. Record
    evidence and disposition without disclosing the password or key.

- [ ] **Live photo acquisition fetches search-result URLs with no SSRF controls**
  - Fingerprint: `truthops/live-photo-fetch-ssrf-no-url-validation`
  - Claimed root cause: The download path performs no scheme/host/IP/redirect
    validation before `urllib.request.urlopen` fetches a URL selected from
    untrusted search results. Its news-domain substring denylist is not an
    SSRF boundary, and Content-Type is checked only after the request.
  - **Exact missing fact:** Whether hosts running --live have any reachable internal/loopback/link-local HTTP service (including cloud metadata at 169.254.169.254) from the operator process, and whether egress/proxy controls in that deployment block private-IP destinations and redirects to them.
  - Validation record: Obtain operator-approved deployment/network evidence
    for both direct destinations and redirect handling from the actual
    process context. Record evidence and disposition; do not infer deployment
    reachability from the source alone.

**Excluded candidates:** The parent audit rejected
`truthops/case-id-path-traversal`,
`truthops/live-evidence-markdown-injection`, and
`truthops/pdf-builder-unescaped-report-html`.
Do not reopen or file them without new evidence.
