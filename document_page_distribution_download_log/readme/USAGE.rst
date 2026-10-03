#. Install this module on top of *Document Page Distribution*.
#. Edit a document page and insert the files of the document in its content
   with the editor, as links. Every link to a file is tracked, whatever the
   type of the file and however many links there are; images and links to
   other sites are not.
#. On save, each link to a file is rewritten to a download address of this
   module that carries the version and the file.
#. When a user downloads the file through the link, the download is recorded
   against that exact version and the file is served. Downloading it again adds
   a new record; the first and the last date of the user are kept. The link of
   an old version is always recorded against that old version.
#. In the *Distribution* tab of the document and in the form of every version,
   each recipient shows whether they downloaded the version, with a button that
   opens the detail (date, user, file) next to the sends. The form of every
   version, the list of versions and the *History* tab of the document say in
   *Downloads*, next to *Distribution*, how many recipients downloaded: *3/10*
   means 3 of 10.
