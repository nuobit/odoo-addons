Where a document requires approval, its editable files change only in a draft
change request, and the *Editables* tab of the document is read-only:

#. Change the content of the document and save it: this makes a change request,
   sent for approval.
#. Open the change request with the document's *Change Requests* button, press
   *Cancel* and then *Back to draft*: *Back to draft* alone refuses a change
   request that was sent for approval.
#. Change its editable files on its *Editables* tab, save, and send it for
   approval.

A change request created from *Change Requests* starts as a draft: save it
first, since its *Editables* tab stays read-only until it is saved. Once
approved, a change request is the version the document shows, with its files;
it is a new version even when only its editable files changed.

Where a document does not require approval, the usage of
``document_page_editable_file`` holds.
