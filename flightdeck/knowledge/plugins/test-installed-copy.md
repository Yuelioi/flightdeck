# Test the plugin users actually load

The working tree is an input; the installed plugin is the product boundary. A mutable development
cache can hide missing files, stale manifests, invalid relative links, and installation behavior.

For a local plugin change:

1. Validate the source skill and plugin manifest.
2. Apply the host's supported local cachebuster or version update.
3. Reinstall through the configured marketplace or loader.
4. Inspect the installed file tree and version.
5. Start a fresh host session and exercise the public behavior.

Keep temporary installation metadata out of canonical source unless it is the host's required local
development convention.
