This module makes the ``Archive`` action on document pages require a
mandatory reason: instead of archiving in one click, a wizard asks the user
for a reason. The reason is stored on the document and logged in its chatter
(who, when, why). Unarchiving stays the standard, one-click action.

Useful for environments with audit or traceability requirements
(GMP, ISO, regulated industries), where archiving a controlled document
must be justified.

Behavior:

* Archiving opens a modal wizard requesting the ``Reason`` text. The reason
  is mandatory.
* On confirm, the reason is stored on each document (field ``Archive
  Reason``) and posted as an internal note in its chatter, then the documents
  are archived through the standard archive action.
* Archiving a selection that already contains archived documents is rejected
  with a ``UserError`` listing them, so a single reason is never recorded
  against the wrong set.
* Unarchiving is the standard, direct Odoo action: it reactivates the
  document and clears the stored archive reason, while the change is recorded
  automatically through the tracked ``active`` field. Past archive reasons
  remain visible in the chatter history.
