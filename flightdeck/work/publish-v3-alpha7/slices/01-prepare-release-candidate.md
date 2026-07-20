# Prepare the alpha.7 release candidate input

## Outcome

The current remote base, exact feature tree, release surfaces, and cleanup targets are known before
the one-commit candidate is created.

## Current

`origin/main` was freshly fetched at `7e0f7a8199adfa883b6f36bda13a050a6986a0bd`. The complete
feature tree is present on `feat/launch-recorded-config`, all pre-candidate gates pass, and the
alpha.7 changelog is dated 2026-07-20. The authorized cleanup set is the five local
`feat/*`/`backup/*` branches and one `refs/flightdeck/checkpoints/*` ref inventoried during this
Slice; `main`, historical release tags, remote refs, and Git objects are outside that set.

## Next

None.

## Verification

- [x] `origin/main` is freshly fetched and recorded.
- [x] The complete feature tree and release surfaces are identified.
- [x] Cleanup targets are explicit and limited to the ADR-authorized local refs.
- [x] Pre-candidate validation passes.
