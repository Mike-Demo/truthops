# TruthOps — 28 Claims: Full Pipeline Trace

Each claim runs through: **Sniff** (Cloudflare Clef) → **Decompose** → **Evidence** (fixtures + GPTZero + Alexandria) → **Evaluate** → **Contrarian** → **Verdict**

| # | Claim | Sniff | Evidence | GPTZero | Alexandria | Contrarian | Verdict | Score | Conf | Trace |
|---|-------|-------|----------|---------|------------|------------|---------|-------|------|-------|
| 1 | Photographs circulating online show New York  | clef-flash | 3 | — | 2 srcs | agree | **PANTS ON FIRE** | 3 | 0.97 | `397aeb68` |
| 2 | President Trump initiated an internal audit o | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.95 | `ba8138a8` |
| 3 | President Trump ended eight wars. | clef-flash | 4 | — | 2 srcs | agree | **MOSTLY FALSE** | 34 | 0.95 | `bb8671e9` |
| 4 | Gasoline is now below $2.30 a gallon in most  | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `b9b283a3` |
| 5 | Zohran Mamdani is the mayor of New York City. | clef-flash | 3 | — | 2 srcs | agree | **TRUE** | 99 | 0.97 | `a8a6cbfc` |
| 6 | President Donald Trump has deported 'over 13, | clef-flash | 3 | — | 2 srcs | agree | **MOSTLY TRUE** | 78 | 0.93 | `503a07c5` |
| 7 | Immigration agents 'are not getting the tradi | clef-flash | 3 | — | 2 srcs | agree | **MOSTLY TRUE** | 88 | 0.94 | `17feeedf` |
| 8 | Florida is '49th in avoidable hospital costs. | clef-flash | 3 | — | 2 srcs | agree | **MOSTLY TRUE** | 90 | 0.93 | `e8437ec3` |
| 9 | Grocery prices were 'down' and 'WAY DOWN' in  | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `44bdadc3` |
| 10 | The enterprise customer decline was 93%. | clef-flash | 4 | 1 flagged | 2 srcs | agree | **FALSE** | 10 | 0.97 | `57006cfd` |
| 11 | Gas prices had fallen to $1.98 per gallon in  | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `16bcdcd3` |
| 12 | There was no inflation during Trump's first p | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `15e989cd` |
| 13 | The Biden administration had the highest infl | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `16556380` |
| 14 | The price of bacon quadrupled during Biden's  | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `e7aea798` |
| 15 | The price of apples doubled during Biden's pr | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `59d25f8e` |
| 16 | The United States was losing $2 trillion a ye | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `552f626c` |
| 17 | The United States had a $350 billion trade de | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `3d4092d7` |
| 18 | It has been claimed that Ukraine started the  | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `d15eee0d` |
| 19 | The United States had provided $350 billion i | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `fd937909` |
| 20 | Europe had provided $200 billion less in aid  | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `dd43d0c8` |
| 21 | The enterprise customer decline was 4%. | clef-flash | 4 | 1 flagged | 2 srcs | agree | **FALSE** | 10 | 0.97 | `dc6c55f4` |
| 22 | More Americans are working in the United Stat | clef-flash | 4 | — | 2 srcs | agree | **MOSTLY FALSE** | 35 | 0.97 | `57b18bfd` |
| 23 | The stock market had set 74 all-time highs si | clef-flash | 4 | — | 2 srcs | agree | **MOSTLY FALSE** | 35 | 0.97 | `0539d697` |
| 24 | Manufacturing was booming and American manufa | clef-flash | 4 | — | 2 srcs | agree | **MOSTLY FALSE** | 35 | 0.97 | `a36b345e` |
| 25 | The United States has the largest amount of o | clef-flash | 4 | — | 2 srcs | agree | **MOSTLY FALSE** | 35 | 0.97 | `99cae079` |
| 26 | It has been claimed that China is operating t | clef-flash | 3 | — | 2 srcs | agree | **FALSE** | 10 | 0.97 | `4c7bc5a8` |
| 27 | The United States spent more money than ever  | clef-flash | 4 | — | 2 srcs | agree | **MOSTLY FALSE** | 35 | 0.97 | `4a2c7205` |
| 28 | Trump won the 2024 U.S. popular vote by milli | clef-flash | 3 | — | 2 srcs | agree | **TRUE** | 99 | 0.97 | `1a77a6e2` |

## Pipeline stages

| Stage | What happens | Adapter |
|-------|--------------|---------|
| Sniff | $0.02 gate: is this coherent and investigable? | Cloudflare Clef-flash |
| Decompose | Break allegation into atomic checkable claims | claim_analyst.py |
| Evidence | Gather + score sources (fixtures, live search) | Alexandria, GPTZero |
| GPTZero | Screen secondary sources for AI text; discount reliability | gptzero_adapter.py |
| Evaluate | Weight evidence → verdict on Truth-O-Meter scale | evidence_agent.py |
| Contrarian | Adversarial review tries to break the verdict | contrarian.py |
| Report | JSON + Markdown + PDF with audit trail | __main__.py |
