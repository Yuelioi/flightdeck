# Prepare the alpha.8 release

## Outcome

The remote base is current and all public release metadata consistently describes alpha.8.

## Current

The remote base is freshly fetched, fast-forward ancestry is proven, all version surfaces identify
alpha.8, the changelog entry is dated 2026-08-02, and pre-commit release gates pass. The prepared
tree remains uncommitted.

## Next

Create the release commit.

## Verification

- [x] The fetched remote base is an ancestor of local `main`.
- [x] All version surfaces identify alpha.8.
- [x] The changelog has a dated alpha.8 entry and no duplicate release content under Unreleased.
- [ ] The release commit is clean and ready for full verification.
