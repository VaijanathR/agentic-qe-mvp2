# CP-MVP2-01 Discovery Evidence (Historical)

**source_type:** `historical_discovery` — lowest-but-one authority tier (see `knowledge/lib/schema.py`). Never authoritative over `requirements/MVP2_SRS_v1.0_APPROVED.md`.

This directory holds the actual artifacts produced during the CP-MVP2-01 stateful browser discovery session (2026-09-11), copied verbatim from that session's working scratchpad after confirming they were still present on disk. Nothing here was reconstructed from memory — see `MANIFEST.json` for per-file hashes and the explicit list of what was deliberately excluded (PNG screenshots, npm/tooling directories) versus what would have been a genuine gap if it hadn't been found.

- `scripts/` — the Playwright probe scripts (`discover.js`, `probe.js`–`probe6.js`, `wishlist_sweep.js`, `wishlist_confirm.js`) that produced the evidence cited throughout the Approved SRS's "Evidence Basis" columns.
- `results/` — the JSON results and run logs each script produced.
- `captures/` — raw HTML page captures (checkout steps, cart states, guest-checkout interstitial, wishlist confirmation).

These files exist to satisfy provenance/traceability questions ("what actually backs REQ-WISH-01?"), not to be re-derived as requirements. Any conflict between this evidence and the Approved SRS is resolved in the Approved SRS's favor, per the CP-MVP2-02 authority model.
