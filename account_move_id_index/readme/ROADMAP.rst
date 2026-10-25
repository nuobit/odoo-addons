* Odoo does not record which module an index belongs to, so uninstalling the
  module drops both indexes even if they existed before it was installed or
  another installed module also declares them. Such a module creates its index
  again at its next update.
