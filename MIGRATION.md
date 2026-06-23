# Migration

This rewrite ships **no automatic migration machinery** — there is no schema, no
version field, and no in-place upgrader. A deck created by an older version is not
auto-upgraded.

To move an older deck forward: create a fresh deck with `/flightdeck:launch`, then
hand-copy your old `cockpit.md` content and any still-relevant knowledge files into
`knowledge/<domain>/`, giving each a routing header (`# <title>` + `SUMMARY:` +
`READ WHEN:`, ended by `---`). Location is state — put in-flight efforts under
`work/`, leave finished ones out.

If a future release changes the deck format, concrete migration steps will be
recorded here.
