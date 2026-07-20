# Create the alpha.7 release commit

## Outcome

A release branch based on the fetched `origin/main` contains exactly one squashed
`v3.0.0-alpha.7` commit whose tree equals the accepted feature tree.

## Current

Release commit `e9fd9396ca7b8bb7e3afbd96189dd1e68a11916f` has sole parent
`7e0f7a8199adfa883b6f36bda13a050a6986a0bd`, exact accepted tree
`4f37c59e88304a1217edf0bfc6f9745db49fd1ad`, and subject `v3.0.0-alpha.7`.

## Next

None.

## Verification

- [x] The release commit has `origin/main` as its only parent.
- [x] The commit subject is `v3.0.0-alpha.7`.
- [x] The release commit tree equals the accepted feature tree.
