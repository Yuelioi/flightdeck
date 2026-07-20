---
status: accepted
---

# Work page is the recovery root

The Work page is authoritative for Goal, lifecycle Status, Current, Next, and the current execution
pointer. The Plan owns only ordered completion, Work context owns stable meaning, and Slice pages
own local execution detail; temporary rules may appear on the Work page when every recovery must
see them. This bounded authority removes duplicated `Outcome` and `Current stage` sections from the
Plan without turning the Work page into a universal override layer.
