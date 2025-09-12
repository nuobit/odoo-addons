### Odoo Python Classes

Use UpperCamelCase

```python
class AccountInvoice(models.Model):
    ...
```

If a class uses `_inherit`, its Python class name should be the same as the parent
class it inherits from. For example, if you inherit from `account.move`
(whose class is `AccountMove`), your class should also be named `AccountMove`.
