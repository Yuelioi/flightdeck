# Security policy

## Supported versions

| Release line | Security fixes |
| --- | --- |
| `3.x` pre-release line | Supported |
| Abandoned internal v4/v5 previews | Unsupported |

## Report privately

Do not open a public issue for an unpatched vulnerability. Use GitHub private vulnerability
reporting when available, or email `yuelioi1210@gmail.com` with subject `Flightdeck security report`.
Do not include credentials or real private repository contents.

Include the affected version, host, operating system, minimal synthetic repository, expected and
observed behavior, and whether data crossed the repository boundary.

Flightdeck v3 alpha has no executable runtime. Relevant risks include unsafe instructions, unintended
file scope, disclosure of private reference material in durable documents, plugin packaging drift,
and host-level path or permission behavior. Host file and Git tools retain their own security
boundaries.
