# Prepare the alpha.8 release

## Outcome

The remote base is current and all public release metadata consistently describes alpha.8.

## Current

Release commit `34a4e95885588d3bf4b5af55a53f56d81727b181` preserves the two post-alpha.7
functional commits, aligns all version surfaces at alpha.8, and dates the changelog entry
2026-08-02. Its fetched remote base is an ancestor.

## Next

None.

## Verification

- [x] The fetched remote base is an ancestor of local `main`.
- [x] All version surfaces identify alpha.8.
- [x] The changelog has a dated alpha.8 entry and no duplicate release content under Unreleased.
- [x] The release commit is clean and ready for full verification.
