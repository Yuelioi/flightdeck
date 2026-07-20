# Alpha.7 Knowledge library audit

This audit applies the accepted demand-grown project-playbook model to the current library. All
eight documents describe one independently applicable, project-specific recurring practice and
remain useful without reopening the Work that produced them.

| Knowledge | Recurring question it answers | Disposition |
| --- | --- | --- |
| [Keep private reference material out of durable artifacts](../../../knowledge/collaboration/private-reference-material.md) | How should Work use private external design input without publishing identifying detail? | Keep |
| [Change every user-facing surface together](../../../knowledge/documentation/change-all-surfaces.md) | What must be reviewed when a structural product contract changes? | Keep |
| [Test the plugin users actually load](../../../knowledge/plugins/test-installed-copy.md) | How should a plugin change be verified beyond its source tree? | Keep |
| [Split skills by invocation and disclose detail by branch](../../../knowledge/skills/progressive-disclosure.md) | When should capability guidance become another skill versus a lazily loaded branch? | Keep |
| [Keep installed skills self-contained](../../../knowledge/skills/self-contained-packages.md) | How should skill-relative dependencies survive packaging and installation? | Keep |
| [Forward-test skill behavior](../../../knowledge/testing/forward-test-skills.md) | How should behavioral claims about an AI-operated skill be verified? | Keep |
| [Recover interrupted work from observable state](../../../knowledge/work/recover-from-observable-state.md) | How should a fresh session reconcile a stale handoff with the repository? | Keep |
| [Make reusable guidance self-contained](../../../knowledge/writing/self-contained-guidance.md) | How should a Work conclusion be rewritten before promotion into Knowledge? | Keep |

## Result

No current file needs splitting, merging, rewriting, or removal. No missing subject or starter file
is justified by repository evidence. Future additions should originate in a real Work and pass the
verification, reuse, and self-containment threshold recorded in
[ADR-0026](../../../../docs/adr/0026-knowledge-is-a-demand-grown-project-playbook.md).
