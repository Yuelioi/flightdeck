# Keep installed skills self-contained

A skill may work in its authoring repository while failing after installation if its links reach
dogfood data, contributor notes, or files excluded from the plugin.

Every relative link in canonical skill prose should resolve inside the installed skill package.
Bundle the referenced instructions and templates, then validate links from the installed plugin
layout rather than only from the source tree. Repository-specific examples may remain outside the
package, but the skill must not depend on them to operate.
