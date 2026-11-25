Makes the editable files of ``document_page_editable_file`` follow the change
requests of ``document_page_approval``:

* The files of a change request reach whoever the change request reaches: its
  author while it is a draft, and the approvers too once it is sent for
  approval. Every editor sees those of the version the document shows.
* Where a document requires approval, the files of a version change only while
  it is a draft change request, as its content does. Where it does not, they
  change while it is a draft change request too, and while the document shows
  it, as without approval.
