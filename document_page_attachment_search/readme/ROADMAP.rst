* Scanned PDFs (image-only) yield no extractable text and are not matched.
* A file of another document linked in the content, such as an image copied
  from another document or a file of the document this one was duplicated
  from, is not kept by this document: it belongs to the other document, goes
  when that document is deleted, and leaves a broken link here.
* The text of the versions stays editable through the API by a document editor,
  as the access rights of the ``document_page`` module allow: this module keeps
  the files of the content, not the text that links them.
