# Alpha.7 ADR implementation review

## Verdict

ADR-0001 through ADR-0025 and the root `CONTEXT.md` form one coherent target architecture. No
directional contradiction remains: ADR-0010 is explicitly superseded by ADR-0011, ADR-0013 defines
the supported routing boundary, and ADR-0025 resolves the concurrency limitation identified by the
Wayfinder research.

The repository has implementation drift, not decision drift. Its current plugin and public surfaces
still describe the finished v5 redesign that preceded the accepted alpha.7 decisions.

## Implementation delta

| Area | Current repository | Accepted alpha.7 target |
| --- | --- | --- |
| Lifecycle | `Active`, `Paused`, `Finished` | `Open`, `Finished`, `Stopped`; blocking stays in Current |
| Focus | A separate Focus section with no Open Work rollup | One Open Work list with exactly one Focus marker when non-empty |
| Execution detail | Flat Plan; Slices forbidden | Plan-linked Decision and Delivery Slices for durable detail |
| Immediate recovery | Separate `Read now` section | Up to three required local links embedded directly in Next |
| Output routing | Specialist outputs default to natural locations | Supported Work-scoped documents route into the owning Work; fallbacks stay natural and are linked |
| Recovery | Index, context, Plan stage, `Read now`, Git | Selected Work page, context, low-resolution Plan, Next links, Git |
| Save | Rewrites a compact handoff | Updates only documents whose recovery meaning materially changed |
| Upgrade | Fixed migration from a v4 preview into v5 | AI judgment over actual semantic roles; no compatibility contract |
| Product identity | `5.0.0-alpha.1` | Continue the published Version 3 line as `3.0.0-alpha.7` |
| Operation | No explicit session boundary | One top-level session per repository; coordinated child agents are allowed |
| Repository activation | No root `AGENTS.md` | A short provider-neutral Flightdeck instruction on first durable Work |

## Old Work disposition

`flightdeck/work/flightdeck-redesign` is complete, unreferenced elsewhere, and defines the
superseded v5 model, including no Slices, `Read now`, natural-location-first routing, and Version 5.
Retaining it in the live Work tree would expose a contradictory recovery contract. It is deleted
from the working tree while ordinary Git history remains the recoverable historical record.
