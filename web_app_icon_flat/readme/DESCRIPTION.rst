This module makes Odoo 16 show the flat app icons that Odoo uses since
version 17, instead of the Odoo 16 ones, in:

* the app menu (for example the one of ``web_responsive``) and the command
  palette;
* the Apps list, in the kanban view and in the module form;
* the Settings sidebar.

Its glue modules, which install by themselves with the module they need, do
the same elsewhere: ``mail_app_icon_flat`` in the activities and messages
menus, ``website_app_icon_flat`` on the website's Editor button and
``note_app_icon_flat`` where the activities menu adds a note.

A module that brings the flat icon of another app ships it as
``static/img/<module>/<file>`` and adds its own name to
``ir.module.module._get_flat_icon_addons()``; the icon then shows while that
module is installed.

Only Odoo's own icons change: the ones of its apps, and the default one that
the Apps list shows for a module without an icon of its own. A module that
brings its own icon keeps it.

The module writes no data: it replaces the icons when the web client reads
them, so uninstalling it brings the Odoo 16 icons back at once.
