* Always use UpperCamelCase for Python class names.
* The class name must match the `_name`, `_inherit`, or `_inherits` attribute in
UpperCamelCase. For example, for the model `res.partner`, the class should be named `ResPartner`.
* If a class uses `_inherit`, its Python class name should be the same as the parent
class it inherits from. For example, if you inherit from `account.move`
(whose class is `AccountMove`), your class should also be named `AccountMove`.
* In python, having a string on one line and another string in the line below is
considered a bad practice. USe always parenthesis to wrap multi-line strings.
* All the `.po` or `.pot` files should have a blank line at the end of the file.
* A commit should contain only one Odoo module.
* The name of the python file should be the same as the name of the model it using underscores.
  For example, if the model is `res.partner`, the file should be named `res_partner.py`.
* Only one model per file.
* The XML view files should be named using the following pattern:
  `<model>_views.xml`. For example, if the model is `res.partner`, the file should be
named `res_partner_views.xml`.
* In Python code, there should be exactly 2 line between the copyright/license header
and imports and also 2 lines between the imports and the start of the code.
* There should not be a copyright/license header in `__init__.py` files.
* Every python file should have a copyright/license header with this format:
  ```
  # Copyright 2025 Company name - Name1 Lastname1 <email1>
  # Copyright Company name - Name2 Lastname2 <email2>
  # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
  ```
  the year can be optional.
* The summary/description on `__manifest__.py` should be consistent with the `readme/DESCRIPTION.md`
* There should be always a readme folder on the root of each module.
* Everything except the `.po` files should be in English.
