This module makes the *Environmental Aspects* menu of the management system
(module ``document_page_environmental_aspect``) follow the master folders of
``mgmtsystem_document_master_folder``: it lists the pages in the master folders
of the active companies, and *Create* files the new page in the master folder
of the selected company.

On installation, the category of ``document_page_environmental_aspect`` becomes
the master folder of the menu, whatever it is called and with the company it
has, so the menu works as before until a company gets its own master folder.

It is installed automatically when ``document_page_environmental_aspect`` and
``mgmtsystem_document_master_folder`` are both installed.
