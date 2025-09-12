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
