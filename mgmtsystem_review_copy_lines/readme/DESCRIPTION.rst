This module makes duplicating a management system review also duplicate its
review lines.

Out of the box, duplicating a review does not carry over its lines (One2many
fields are not copied by default).

With this module, duplicating a review:

* copies every review line (title, type, linked action or nonconformity and
  decision) as new line records attached to the copy,
* keeps assigning a fresh reference to the copy and starting it in the *Open*
  state, regardless of the state of the source review, as before.

This enables a template-based workflow: keep a review with the standard set of
lines (with empty decisions) and duplicate it whenever a new review with the
same structure is needed, instead of re-creating the lines one by one.
