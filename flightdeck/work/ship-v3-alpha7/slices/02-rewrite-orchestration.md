# Rewrite the Flightdeck orchestration contract

## Outcome

The shipped skill, progressively loaded branches, and templates implement the accepted Work, Plan,
Slice, recovery, save, lifecycle, output-routing, Wayfinding, and upgrade semantics.

## Current

Complete. One orchestration skill now progressively loads start, continue, save, finish/stop,
output-routing, Wayfinding, and upgrade guidance. Its Deck, Work, Context, Plan, and Slice templates
implement the accepted recovery and ownership model.

## Next

None.

## Verification

- Skill structure validation passes.
- Plugin manifest validation passes with the expanded skill tree.
