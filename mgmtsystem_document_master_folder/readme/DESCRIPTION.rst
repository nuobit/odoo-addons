This module gives each company its own master folders for the four document
menus of the management system: *Procedures*, *Environmental Aspects*, *Work
Instructions* and *Manuals*.

* A document category can be the *Master Folder Of* one of the four menus.
  Each company has at most one master folder per menu, plus at most one
  without company.
* A menu that follows its master folders lists their pages in the active
  companies.
* Its *Create* button files the new page in the master folder of the selected
  company, or in the one without company when the selected company has none.
  When there is neither, it says so.

Each menu follows its master folders through a module of its own, installed
automatically with the OCA module of the menu:
``document_page_procedure_master_folder``,
``document_page_environmental_aspect_master_folder``,
``document_page_work_instruction_master_folder`` and
``mgmtsystem_manual_master_folder``.
