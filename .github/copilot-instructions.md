## General Review Expectations

* Enforce [OCA Coding Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst).
* Always use **English for everything: code, comments, and commit messages** (except `.po` translations, obviously).

## Modules

* Use of the singular form in module name (or use "multi"),
  except when compound of module name or object Odoo
  that is already in the plural (i.e. `mrp_operations_...`).
* If your module's purpose is to serve as a base for other modules, prefix its
  name with `base_`. I.e. `base_location_nuts`.
* When creating a localization module, prefix its name with `l10n_CC_`, where
  `CC` is its country code. I.e. `l10n_es_pos`.
* When extending an Odoo module, prefix yours with that module's name. I.e.
  `mail_forward`.

## File naming

For `models`, `views` and `data` declarations, split files by the model
involved, either created or inherited. When they are XML files, a suffix should
be included with its category. For example, demo data for res.partner should go
in a file named `demo/res_partner_demo.xml` and a view for partner should go in
a file named `views/res_partner_views.xml`.

For model named `<main_model>` the following files may be created:

* `models/<main_model>.py`
* `data/<main_model>_data.xml`
* `demo/<main_model>_demo.xml`
* `templates/<main_model>_template.xml`
* `views/<main_model>_views.xml`

For `controller`, if there is only one file it should be named `main.py`.
If there are several controller classes or functions you can split them into
several files.

For `static files`, the name pattern is `<module_name>.ext` (i.e.
`static/js/im_chat.js`, `static/css/im_chat.css`, `static/xml/im_chat.xml`,
...). Don't link data (image, libraries) outside Odoo: don't use an url to an
image but copy it in our codebase instead.

## Manifest Requirements

* Do not include `installable=True` it's the default
* Only include `application=True` if the module is a full application
* Only include `auto_install=True` if it's really needed

## Installation hooks

When **`pre_init_hook`**, **`post_init_hook`**, **`uninstall_hook`**
and **`post_load`** are
used, they should be placed in **`hooks.py`** located at the root of module
directory structure and keys in the manifest file keeps the same as the
following

```python
{
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'post_load': 'post_load',
}
```

Remember to add into the **`__init__.py`** the following imports as
needed. For example:

```python
from .hooks import pre_init_hook, post_init_hook, uninstall_hook, post_load
```

For applying monkey patches use post_load hook.
In order to apply them just if the module is installed.

## Complete structure

The complete tree should look like this:

```
addons/<my_module_name>/
|-- controllers/
|   |-- __init__.py
|   `-- main.py
|-- data/
|   `-- <main_model>.xml
|-- demo/
|   `-- <inherited_model>.xml
|-- examples/
|   `-- my_example.csv
|-- i18n/
|   |-- en_GB.po
|   |-- es.po
|   `-- module_name.pot
|-- migrations/
|   `-- 16.0.x.y.z/
|       |-- pre-migration.py
|       `-- post-migration.py
|-- models/
|   |-- __init__.py
|   |-- <main_model>.py
|   `-- <inherited_model>.py
|-- readme/
|   |-- CONTRIBUTORS.rst
|   |-- DESCRIPTION.rst
|   `-- USAGE.rst
|-- reports/
|   |-- __init__.py
|   |-- reports.xml
|   |-- <bi_reporting_model>.py
|   |-- report_<rml_report_name>.rml
|   |-- report_<rml_report_name>.py
|   `-- <webkit_report_name>.mako
|-- security/
|   |-- ir.model.access.csv
|   `-- <main_model>_security.xml
|-- static/
|   |-- img/
|   |   |-- my_little_kitten.png
|   |   `-- troll.jpg
|   |-- lib/
|   |   `-- external_lib/
|   `-- src/
|       |-- js/
|       |   `-- <my_module_name>.js
|       |-- css/
|       |   `-- <my_module_name>.css
|       |-- less/
|       |   `-- <my_module_name>.less
|       `-- xml/
|           `-- <my_module_name>.xml
|-- templates/
|   |-- <main_model>.xml
|   `-- <inherited_main_model>.xml
|-- tests/
|   |-- __init__.py
|   |-- <test_file>.py
|   `-- <test_file>.yml
|-- views/
|   |-- <main_model>_views.xml
|   |-- <inherited_main_model>_views.xml
|   `-- report_<qweb_report>.xml
|-- wizards/
|   |-- __init__.py
|   |-- <wizard_model>.py
|   `-- <wizard_model>.xml
|-- README.rst
|-- __init__.py
|-- __manifest__.py
|-- exceptions.py
`-- hooks.py
```

Filenames should use only `[a-z0-9_]`

## README

If your module uses extra dependencies of python or binaries, please explain
how to install them in the `README.rst` file in the section `Installation`.

## XML Format

When declaring a record in XML:

* Indent using four spaces
* Place `id` attribute before `model`
* For field declarations, the `name` attribute is first. Then place the `value`
  either in the `field` tag, either in the `eval` attribute, and finally other
  attributes (widget, options, ...) ordered by importance.
* Try to group the records by model. In case of dependencies between
  action/menu/views, the convention may not be applicable.
* Use naming convention defined at the next point
* The tag `<data>` is only used to set not-updatable data with `noupdate=1`
  when your data file contains a mix of "noupdate" data. Otherwise, you should
  use one of these:

  - `<odoo>`: for `noupdate=0` or demo data (demo data is non-updatable by default)
  - `<odoo noupdate='1'>`

* Do not prefix the xmlid by the current module's name
  (`<record id="view_id"...`, not `<record id="current_module.view_id"...`)

```xml
<record id="view_id" model="ir.ui.view">
    <field name="name">view.name</field>
    <field name="model">object_name</field>
    <field name="priority" eval="16"/>
    <field name="arch" type="xml">
        <tree>
            <field name="my_field_1"/>
            <field name="my_field_2" string="My Label" widget="statusbar" statusbar_visible="draft,sent,progress,done" statusbar_colors='{"invoice_except":"red","waiting_date":"blue"}' />
        </tree>
    </field>
</record>
```

## XML records

* For records of model `ir.filters` use explicit `user_id` field.

```xml
<record id="filter_id" model="ir.filters">
    <field name="name">Filter name</field>
    <field name="model_id">filter.model</field>
    <field name="user_id" eval="False"/>
</record>
```

## Naming xml_id

### Data Records

Use the followng pattern, where `<model_name>` is the name of the model that
the record is an instance of: `<model_name>_<record_name>`

```xml
<record id="res_users_important_person" model="res.users">
    ...
</record>
```

### Security, View and Action

Use the following patterns, where `<model_name>` is the name of the model that
the menu, view, etc. belongs to (e.g. for a `res.users` form view, the name
would be `res_users_view_form`):

* For a menu: `<model_name>_menu`
* For a view: `<model_name>_view_<view_type>`, where `view_type` is kanban,
  form, tree, search, ...
* For an action: the main action respects `<model_name>_action`. Others are
  suffixed with `_<detail>`, where `detail` is an underscore lowercase string
  explaining the action (should not be long). This is used only if
  multiple actions are declared for the model.
* For a group: `<model_name>_group_<group_name>` where `group_name` is the
  name of the group, generally 'user', 'manager', ...
* For a rule: `<model_name>_rule_<concerned_group>` where `concerned_group` is
  the short name of the concerned group ('user' for the
  'model_name_group_user', 'public' for public user, 'company' for
  multi-company rules, ...).

```xml
<!-- views and menus -->
<record id="model_name_menu" model="ir.ui.menu">
    ...
</record>

<record id="model_name_view_form" model="ir.ui.view">
    ...
</record>

<record id="model_name_view_kanban" model="ir.ui.view">
    ...
</record>

<!-- actions -->
<record id="model_name_action" model="ir.actions.act_window">
    ...
</record>

<record id="model_name_action_child_list" model="ir.actions.act_window">
    ...
</record>

<!-- security -->
<record id="model_name_group_user" model="res.groups">
    ...
</record>

<record id="model_name_rule_public" model="ir.rule">
    ...
</record>

<record id="model_name_rule_company" model="ir.rule">
    ...
</record>
```

### Inherited XML

A module can extend a view only one time.

The naming rules should be followed even when a view is inherited, the module
name prevents xid conflicts. In the case where an inherited view has a name
which does not follow the guidelines set above, prefer naming the inherited
view after the original over using a name which follows the guidelines. This
eases looking up the original view and other inheritance if they all have the
same name.

```xml
<record id="original_id" model="ir.ui.view">
    <field name="inherit_id" ref="original_module.original_id"/>
    ...
</record>
```
Use of `<... position="replace">` is not recommended because
could show the error `Element ... cannot be located in parent view`
from other inherited views with this field.

If you need to use this option, it must have an explicit comment
explaining why it is absolutely necessary and also use a
high value in its `priority` (greater than 100 is recommended) to avoid the error.

```xml
<record id="view_id" model="ir.ui.view">
    <field name="name">view.name</field>
    <field name="model">object_name</field>
    <field name="priority">110</field> <!--Priority greater than 100-->
    <field name="arch" type="xml">
        <!-- It is necessary because...-->
        <xpath expr="//field[@name='my_field_1']" position="replace"/>
    </field>
</record>
```

Also, we can hide an element from the view using `invisible="1"`.

### Demo Records

Suffix all demo record XML IDs with `demo`. This allows them to be easily
distinguished from regular records, which otherwise requires examining the
source or reinstalling the module with demo data disabled.

```xml
<record id="res_users_not_a_real_user_demo" model="res.users">
    ...
</record>
```

## Idioms

* Prefer `%` over `.format()`, prefer `%(varname)` instead of positional.
  This is better for translation
  `and security <https://github.com/OCA/pylint-odoo/issues/302#issue-758472967>`__.
* Always favor **Readability** over **conciseness** or using the language
  features or idioms.
* Use list comprehension, dict comprehension, and basic manipulation using
  `map`, `filter`, `sum`, ... They make the code more pythonic, easier to read
  and are generally more efficient
* The same applies for recordset methods: use `filtered`, `mapped`, `sorted`,
  ...
* Exceptions: Use `UserError` or find a more appropriate exception
  in `odoo.exceptions.py`
* Document your code

  * Docstring on methods should explain the purpose of a function,
    not a summary of the code
  * Simple comments for parts of code which do things which are not
    immediately obvious
  * Too many comments are usually a sign that the code is unreadable and
    needs to be refactored

* Use meaningful variable/class/method names
* If a function is too long or too indented due to loops, this is a sign
  that it needs to be refactored into smaller functions
* If a function call
  * Dictionary, list or tuple is broken into two lines,
    break it at the opening symbol. This adds a four space indent to the next
    line instead of starting the next line at the opening symbol.
  * Add always a trailing comma to the last element in such cases.
    This makes it so the next element added only changes one line in the
    changeset instead of changing the last element to simply add a comma.
  * Add always the name of the parameter `comodel_name=`, `string=`, ...

  Example:

  ```python
  partner_id = fields.Many2one(
      comodel_name="res.partner",
      string="Partner",
      required=True,
  )
  ```
* In general, when making a comma separated list, dict, tuple, ... with one element per
  line, append a comma to the last element. This makes it so the next element
  added only changes one line in the changeset instead of changing the last
  element to simply add a comma.
* Use English variable names and write comments in English. Strings which need
  to be displayed in other languages should be translated using the translation
  system

## Symbols

### Odoo Python Classes

Use UpperCamelCase

```python
class AccountInvoice(models.Model):
    ...
```

If a class uses `_inherit`, its Python class name should be the same as the parent
class it inherits from. For example, if you inherit from `account.move`
(whose class is `AccountMove`), your class should also be named `AccountMove`.

### Variable names

* Always give your variables a meaningful name. You may know what it's
  referring to now, but you won't in 2 months, and others don't either.
  indices, or perhaps in pure maths expressions (and even there it doesn't hurt
  to use a real name).

  ```python
  # unclear and misleading
  a = {}
  sfields = {}

  # better
  results = {}
  selected_fields = {}
  ```

* Use underscore lowercase notation for common variables (snake_case)
* Since new API works with records or recordsets instead of id lists, don't
  suffix variable names with `_id` or `_ids` if they do not contain an ids or
  lists of ids.

  ```python
  res_partner = self.env['res.partner']
  partners = res_partner.browse(ids)
  partner_id = partners[0].id
  ```

* Use underscore uppercase notation for global variables or constants

  ```python
  CONSTANT_VAR1 = 'Value'
  ...
  class ...
  ...
  ```

Models
======

* Model names

  * Use dot lowercase name for models. Example: `sale.order`
  * Use name in a singular form. `sale.order` instead of `sale.orders`

* Method conventions

  * Compute Field: the compute method pattern is `_compute_<field_name>`
  * Inverse method: the inverse method pattern is `_inverse_<field_name>`
  * Search method: the search method pattern is `_search_<field_name>`
  * Default method: the default method pattern is `_default_<field_name>`
  * Onchange method: the onchange method pattern is `_onchange_<field_name>`
  * Constraint method: the constraint method pattern is
    `_check_<constraint_name>`
  * Action method: an object action method is prefix with `action_`.
    Its decorator is `@api.multi`, but since it use only one record, add
    `self.ensure_one()` at the beginning of the method.
  * Never use `@api.one` method.

* In a Model attribute order should be

  #. Private attributes (`_name`, `_inherit`, `_description`, ...)
  #. Fields declarations
  #. SQL constraints
  #. Default method and `_default_get`
  #. Compute and search methods in the same order than field declaration
  #. Constrains methods (`@api.constrains`) and onchange methods
     (`@api.onchange`)
  #. CRUD methods (ORM overrides)
  #. Action methods
  #. And finally, other business methods.

.. code-block:: python

    class Event(models.Model):
        # Private attributes: model declaration (_name and inherits), _description, ...
        _name = 'event.event'
        _inherit = ['event.event', 'mail.thread']
        _description = 'Event'
        _order = 'name'

        # Fields declaration
        name = fields.Char(default=lambda self: self._default_name())
        seats_reserved = fields.Integer(
            oldname='register_current',
            string='Reserved Seats',
            store=True,
            readonly=True,
            compute='_compute_seats',
        )
        seats_available = fields.Integer(
            oldname='register_avail',
            string='Available Seats',
            store=True,
            readonly=True,
            compute='_compute_seats',
        )
        price = fields.Integer(string='Price')

        # SQL constraints
        _sql_constraints = [
            ('name_uniq', 'unique(name)', 'Name must be unique'),
        ]

        # Default methods
        def _default_name(self):
            ...

        # compute and search fields, in the same order that fields declaration
        @api.multi
        @api.depends('seats_max', 'registration_ids.state')
        def _compute_seats(self):
            ...

        # Constraints and onchanges
        @api.constrains('seats_max', 'seats_available')
        def _check_seats_limit(self):
            ...

        @api.onchange('date_begin')
        def _onchange_date_begin(self):
            ...

        # CRUD methods
        def create(self):
            ...

        # Action methods
        @api.multi
        def action_validate(self):
            self.ensure_one()
            ...

        # Business methods
        def mail_user_confirm(self):
            ...

Fields
======

* `One2Many` and `Many2Many` fields should always have `_ids` as suffix
  (example: sale_order_line_ids)
* `Many2One` fields should have `_id` as suffix
  (example: partner_id, user_id, ...)
* If the technical name of the field (the variable name) is the same to the
  string of the label, don't put `string` parameter for new API fields, because
  it's automatically taken. If your variable name contains "_" in the name,
  they are converted to spaces when creating the automatic string and each word
  is capitalized.
  (example:

      old api `'name': fields.char('Name', ...)`
      new api `'name': fields.Char(...)`)

* Default functions should be declared with a lambda call on self. The reason
  for this is so a default function can be inherited. Assigning a function
  pointer directly to the `default` parameter does not allow for inheritance.

  .. code-block:: python

      a_field(..., default=lambda self: self._default_get())

Exceptions
==========

The `pass` into block except is not a good practice!

By including the `pass` we assume that our algorithm can continue to function
after the exception occurred

If you really need to use the `pass` consider logging that exception

.. code-block:: python

    try:
        sentences
    except Exception:
        _logger.debug('Why the exception is safe....', exc_info=1))


## Git

### Commit Message Rules

- Write a short commit summary (max 50 characters) without prefixing it.
- Use the commit body to specify the impacted part (module, lib, object, …) and a description of the change. Limit lines to 80 characters.
- Commit messages must be in English.
- PR titles follow the same rules: the first line is the summary, the description is the body.
- Always use meaningful and self-explanatory commit messages, including module name and reason for the change.
- Avoid vague terms like "bugfix" or "improvements".
- Only one logical change per commit. Do not add fixup commits such as "pep8", "code review", or "add unittest".
- Avoid commits that impact many unrelated modules. Split into separate commits when possible.
- Use present imperative mood for verbs (e.g. `Fix formatting`, `Remove unused field`), not “Fixes” or “Removes”.
- Keep commit summaries short. If GitHub truncates the PR title with `[...]`, shorten it. The detailed explanation belongs in the body.
- Use tags where appropriate:
  - `[FIX]` – bug fix
  - `[REF]` – refactoring
  - `[ADD]` – add new module
  - `[REM]` – remove code, views, or modules
  - `[REV]` – revert commit
  - `[MOV]` – move files or code (use `git mv`)
  - `[REL]` – release commit
  - `[IMP]` – incremental improvement
  - `[MERGE]` – merge commit (forward port, feature merge)
  - `[CLA]` – CLA signature
  - `[I18N]` – translation changes
  - `[PERF]` – performance optimization
  - `[MIG]` – module migration
- Example of good summary and body:
```text
[FIX] website: remove unused alert div

Fix layout caused by alert div breaking input-group-btn order.
```

```text
[IMP] web: add JS module system

Introduce modular structure to replace global JS usage.
```

## Tests

* Unit tests are expected for bugfixes and new modules
* Avoid depending on demo data
* Use fixed datetime in tests (`freezegun`)
* Avoid external service dependencies unless mocked

## Translations

* Modules **must** have `es.po` if UI strings are present
* If the module uses translatable literals, there **must** be at least an `es.po` file.

## Additional Rules

* Use only lowercase letters, numbers, and underscores in filenames
* Use `o_<module_name>` class prefix in CSS
* Use `use strict;` in JS
* No minified JS libraries in source
* Use `requirements.txt` for Python dependencies, not just `travis.yml`
