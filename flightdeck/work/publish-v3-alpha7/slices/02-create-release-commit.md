# Create the alpha.7 release commit

## Outcome

A release branch based on the fetched `origin/main` contains exactly one squashed
`v3.0.0-alpha.7` commit whose tree equals the accepted feature tree.

## Current

Not yet started.

## Next

After preparation passes, snapshot the accepted feature tree and create the one-commit release
candidate with `origin/main` as its direct parent.

## Verification

- [ ] The release commit has `origin/main` as its only parent.
- [ ] The commit subject is `v3.0.0-alpha.7`.
- [ ] The release commit tree equals the accepted feature tree.
