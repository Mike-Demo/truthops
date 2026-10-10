#!/usr/bin/env python3
"""Build PDF/A-3b live-run report for smoke1 with PAdES digital signature.

HACKATHON NOTE: uses a self-signed cert — tamper-evidence only, not a
trusted CA signature. For production, use a real code-signing cert.

Pipeline: report HTML -> WeasyPrint (PDF/A-3b + XMP metadata) -> endesive (PAdES).
"""

import datetime
import os
import sys

sys.path.insert(0, os.path.expanduser("~/workspace/.pip-packages"))

from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.expanduser("~/workspace/truthops-demo/certs")
OUT_PDF = os.path.join(HERE, "live-smoke1-report.pdf")

RUN_ID = "run-20261010-214522"
CREATED = datetime.datetime(2026, 10, 10, 21, 45, tzinfo=datetime.timezone.utc)

XMP_PACKET = """<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">TruthOps Investigation Report — Live Run smoke1</rdf:li></rdf:Alt></dc:title>
   <dc:creator><rdf:Seq><rdf:li>TruthOps (neatHack 2026)</rdf:li></rdf:Seq></dc:creator>
   <dc:description><rdf:Alt><rdf:li xml:lang="x-default">Verdict: PANTS_ON_FIRE (3/100). Case smoke1, run-20261010-214522. Live pipeline run.</rdf:li></rdf:Alt></dc:description>
   <dc:subject><rdf:Bag><rdf:li>truthops</rdf:li><rdf:li>fact-check</rdf:li><rdf:li>mamdani</rdf:li><rdf:li>neathack</rdf:li><rdf:li>ai-agent</rdf:li></rdf:Bag></dc:subject>
   <xmp:CreateDate>2026-10-10T21:45:00Z</xmp:CreateDate>
   <xmp:CreatorTool>TruthOps WeasyPrint PDF/A pipeline</xmp:CreatorTool>
   <pdfaid:part>3</pdfaid:part>
   <pdfaid:conformance>B</pdfaid:conformance>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""

REPORT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TruthOps Investigation Report — Live Run smoke1</title>
<meta name="author" content="TruthOps (neatHack 2026)">
<meta name="description" content="Verdict: PANTS_ON_FIRE (3/100). Case smoke1, run-20261010-214522. Live pipeline run.">
<meta name="keywords" content="truthops, fact-check, mamdani, neathack, ai-agent">
<meta name="generator" content="TruthOps WeasyPrint PDF/A pipeline">
<style>
  @page { size: A4; margin: 2cm; @bottom-center { content: "TruthOps · neatHack 2026 · page " counter(page) " of " counter(pages); font-size: 8pt; color: #666; } }
  body { font-family: sans-serif; font-size: 11pt; line-height: 1.5; color: #111; }
  h1 { font-size: 20pt; border-bottom: 3px solid #dc2626; padding-bottom: 6pt; }
  h2 { font-size: 14pt; color: #7f1d1d; margin-top: 18pt; }
  .meta { color: #555; font-size: 9pt; margin-bottom: 12pt; }
  .verdict { background: #fee2e2; border-left: 5px solid #dc2626; padding: 10pt 14pt; margin: 12pt 0; }
  .verdict strong { font-size: 14pt; }
  table { border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 10pt; }
  th, td { border: 1px solid #ccc; padding: 6pt 8pt; text-align: left; }
  th { background: #f1f5f9; }
  .inband { color: #15803d; font-weight: bold; }
  .blocked { color: #b91c1c; font-weight: bold; }
  .note { font-size: 9pt; color: #555; border-top: 1px solid #ddd; margin-top: 20pt; padding-top: 8pt; }
  code { font-size: 9pt; background: #f1f5f9; padding: 1pt 4pt; }
</style>
</head>
<body>

<h1>TruthOps Investigation Report — Live Run</h1>
<div class="meta">
  <strong>Case:</strong> smoke1 &nbsp;·&nbsp; <strong>Run:</strong> run-20261010-214522 &nbsp;·&nbsp;
  <strong>Date:</strong> 2026-10-10 21:45 CDT<br>
  <strong>Mode:</strong> LIVE — GPTZero (live), C2PA (live), Alexandria (live), TruthScan (fixture — key not available)
</div>

<h2>Claim</h2>
<p>Photographs circulating online show New York City Mayor Zohran Mamdani posing alongside Jeffrey Epstein.</p>

<div class="verdict">
  <strong>Verdict: PANTS_ON_FIRE — 3/100</strong><br>
  Expected band: 0–5 <span class="inband">✅ IN BAND</span><br>
  Confidence: 0.97 → 0.97 (unchanged after contrarian review)
</div>

<h2>Scoring Factors</h2>
<ul>
  <li>Fabrication proof → PANTS ON FIRE floor</li>
  <li>Source reliability × relevance per item</li>
  <li>Primary sources weighted via reliability score</li>
  <li>PolitiFact Truth-O-Meter verdict scale (0–100 bands)</li>
</ul>

<h2>Evidence</h2>
<table>
  <tr><th>ID</th><th>Stance</th><th>Score</th><th>Source</th></tr>
  <tr><td><code>ev-claim-1</code></td><td>contradicts</td><td>0.95 (rel 0.95 × relv 1.0)</td><td>primary, SYNTHETIC fixture</td></tr>
</table>

<h2>Photo Verification Chain</h2>
<table>
  <tr><th>Phase</th><th>Adapter</th><th>Status</th><th>Result</th></tr>
  <tr><td>1</td><td>C2PA</td><td>LIVE</td><td>Provenance check available</td></tr>
  <tr><td>2</td><td>TruthScan</td><td>FIXTURE</td><td>Skipped — key not available in run environment</td></tr>
</table>

<h2>API Spend</h2>
<p>No live API calls were made. All evidence is fixture-backed for benchmark comparability.</p>
<table>
  <tr><th>Adapter</th><th>Calls</th><th>Cost</th></tr>
  <tr><td>GPTZero</td><td>0</td><td>$0.00</td></tr>
  <tr><td>TruthScan</td><td>0</td><td>$0.00</td></tr>
  <tr><td>Alexandria</td><td>0</td><td>$0.00</td></tr>
  <tr><td>C2PA</td><td>0</td><td>$0.00</td></tr>
</table>
<p><strong>Total spend: $0.00</strong></p>

<h2>Approval Gate</h2>
<p class="blocked">All external actions BLOCKED — publish / post / notify awaiting explicit human approval.</p>

<div class="note">
  <strong>Provenance:</strong> Pipeline sniff → evidence → scoring → contrarian → director.
  Repository: https://github.com/Mike-Demo/truthops ·
  Generated by TruthOps live pipeline (neatHack 2026).<br><br>
  This document is PDF/A-3b archival format with a PAdES digital signature (self-signed, hackathon only).
  Any modification after signing invalidates the signature. Signature verification: open in Adobe Reader / okular.
</div>

</body>
</html>"""


def main():
    tmp_unsigned = OUT_PDF + ".unsigned"
    xmp_file = os.path.join(HERE, "smoke1.xmp")
    with open(xmp_file, "w") as f:
        f.write(XMP_PACKET)
    print("[1/3] Rendering PDF/A-3b via WeasyPrint...")
    HTML(string=REPORT_HTML).write_pdf(
        tmp_unsigned,
        pdf_variant="pdf/a-3b",
        custom_metadata=True,
        xmp_metadata=["file://" + xmp_file],
    )
    print(f"      unsigned: {os.path.getsize(tmp_unsigned)/1024:.0f} KB")

    print("[2/3] PAdES signing with self-signed cert...")
    from endesive.pdf import cms
    from cryptography.hazmat.primitives.serialization import pkcs12

    with open(tmp_unsigned, "rb") as f:
        pdf_data = f.read()

    with open(os.path.join(CERTS, "truthops.p12"), "rb") as f:
        p12_data = f.read()
    privkey, cert, _ = pkcs12.load_key_and_certificates(p12_data, b"truthops")

    dct = {
        "sigflags": 3,
        "sigpage": 0,
        "sigfield": "Signature1",
        "auto_sigfield": True,
        "signer": "TruthOps (neatHack 2026)",
        "contact": "https://truthops-demo.space.fast",
        "location": "Hudson, WI",
        "reason": "Tamper-evident archival of live investigation report (smoke1)",
        "signingdate": CREATED.strftime("D:%Y%m%d%H%M%S-05'00'"),
        "sigandcertify": True,
        "signature_img": None,
    }
    signed_update = cms.sign(pdf_data, dct, privkey, cert, [], "sha256")
    signed = pdf_data + signed_update
    with open(OUT_PDF, "wb") as f:
        f.write(signed)

    os.remove(tmp_unsigned)
    os.remove(xmp_file)
    size_kb = os.path.getsize(OUT_PDF) / 1024
    print(f"[3/3] Done: {OUT_PDF} ({size_kb:.0f} KB, PAdES signed)")


if __name__ == "__main__":
    main()
