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
  are archived through the standard archive action. The chatter shows both:
  the note with the reason and the change of the tracked ``active`` field.
* Archiving a selection that already contains archived documents is rejected
  with a ``UserError`` listing them, so a single reason is never recorded
  against the wrong set.
* A document cannot be archived without a reason, whatever the way. A write
  that archives documents (an automated action, an RPC call) must write their
  ``Archive Reason`` too, or it is rejected with a ``ValidationError`` listing
  them. The reason cannot be imported (the field is read-only), so an import
  that archives documents is always rejected: archive them with the
  ``Archive`` action instead.
* A copy of an archived document starts active, without the archive reason
  of the original.
* Unarchiving is the standard, direct Odoo action: it reactivates the
  document and clears the stored archive reason, while the change is recorded
  automatically through the tracked ``active`` field. Past archive reasons
  remain visible in the chatter history.
