* Scanned PDFs (images only) and other PDFs without extractable text yield no
  indexed text, so their content is not matched.
* Copy-protected PDFs are indexed like any other PDF: ``pdfminer.six`` ignores
  their copy protection, so the search finds the words of such a file.
* The search is meant for internal users; access to the documents from the
  portal is out of scope.
* Files embedded in a document before this module is installed are kept with
  the document only once its content is saved again, or after the
  post-migration linking of the usage section; a file that belongs to no record
  is anchored by the save of its uploader or of a system administrator. Both
  recognise ``/web/content/<id>`` and ``/web/image/<id>`` links only: a file
  whose link another module rewrote in the stored content, such as a
  download-tracking link, is not kept.
* A file of another document linked in the content, such as an image copied
  from another document or a file of the document this one was duplicated
  from, is not kept by this document: it belongs to the other document, goes
  when that document is deleted, and leaves a broken link here.
* The text of the versions stays editable through the API by a document editor,
  as the access rights of the ``document_page`` module allow: this module keeps
  the files of the content, not the text that links them.
