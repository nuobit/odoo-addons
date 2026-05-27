This module makes the ``Archive`` action on document pages require a
mandatory reason: instead of archiving in one click, a wizard asks the user
for a reason, which is then logged in the document chatter (who, when, why).
Unarchiving stays a direct, one-click action.

Useful for environments with audit or traceability requirements
(GMP, ISO, regulated industries), where archiving a controlled document
must be justified.

Behavior:

* Archiving opens a modal wizard requesting the ``Reason`` text. The reason
  is mandatory.
* On confirm, the documents are archived and the wizard posts an internal
  note in each document's chatter with the reason.
* Unarchiving is performed directly, without a reason. The change is still
  recorded automatically through the tracked ``active`` field.
* Both actions reject a selection that contains documents already in the
  target state: a ``UserError`` lists the offending documents (archiving
  rejects already archived documents, unarchiving rejects already active
  ones).
* A context flag ``archive_reason_provided=True`` lets programmatic callers
  archive directly, bypassing the wizard when they take responsibility for
  posting their own audit entry.
