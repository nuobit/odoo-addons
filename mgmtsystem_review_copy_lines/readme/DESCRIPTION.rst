This module makes duplicating a management system review also duplicate its
review lines, and makes every duplicate start as an open review.

Out of the box, duplicating a review yields an almost empty copy: the review
lines are not carried over (One2many fields are not copied by default) and the
state of the source review is kept, so duplicating a closed review produces a
copy that is already closed and read-only.

With this module, duplicating a review:

* copies every review line (title, type, linked action or nonconformity and
  decision) as new line records attached to the copy,
* always starts the copy in the *Open* state, regardless of the state of the
  source review,
* keeps assigning a fresh reference to the copy, as before.

This enables a template-based workflow: keep a review with the standard set of
lines (with empty decisions) and duplicate it whenever a new review with the
same structure is needed, instead of re-creating the lines one by one.

The faithful copy of the lines is intentional: it includes the decision text
and the linked action or nonconformity of every line. When duplicating a
review that has already been filled in — instead of a template — the copied
lines carry that content over, and it must be reviewed and cleared by hand
where it does not apply to the new review.
