# Finish or stop work

Use a terminal state only when the Work is no longer Open.

1. Inspect the final repository state and run verification proportional to the change.
2. Set Status to `Finished` only when the Goal and applicable acceptance checks are satisfied. Set
   Status to `Stopped` when an unsatisfied Goal is deliberately cancelled, superseded, or no longer
   valuable, and record the reason under Current.
3. Set Next to `None`, keep concise final outcomes under Progress, update stable context, and
   complete only the Plan items actually delivered.
4. Remove the terminal Work from the deck's Open Work list. If Open Work remains, preserve a valid
   Focus or choose the clearest next Work; when ambiguous, ask the user. An empty list has no Focus.
5. Keep the Work page, context, Plan, Slices, and useful References in the same directory. Do not
   archive, move, rename, or delete them as lifecycle ceremony.
6. Report the outcome, verification, reason for stopping when applicable, and residual risk.

A blocker does not make Work terminal. Record the blocking condition in Current and leave Status
`Open` with one concrete Next action that could resolve or recheck it.
