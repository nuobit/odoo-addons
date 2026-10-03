# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.modules import get_module_resource


def _has_po_file(module_name, lang):
    """Tell whether the translation loader finds a PO file of the module for the
    language: ``<iso code>.po``, or ``<base code>.po`` for a regional language,
    in ``i18n/`` or ``i18n_extra/`` (``ir.translation._load_module_terms``)."""
    iso_code = tools.get_iso_codes(lang)
    return any(
        get_module_resource(module_name, folder, name + ".po")
        for folder in ("i18n", "i18n_extra")
        for name in {iso_code, iso_code.split("_")[0]}
    )


class MgmtsystemHazardRiskComputation(models.Model):
    _inherit = "mgmtsystem.hazard.risk.computation"

    # The OCA base module (mgmtsystem_hazard_risk) defines ``description`` as a
    # plain, non-translatable Text field, so the risk-formula descriptions can
    # only ever be shown in English. Redeclaring the field as translatable lets
    # those descriptions be presented in the user's language; the Spanish and
    # Catalan values ship in this module's i18n_extra/ files, the folder for
    # hand-written translations: they translate records of the base module,
    # which an export of this module cannot produce.
    description = fields.Text(translate=True)

    def _delete_description_translations(self, module_name):
        """Delete the description translations of these formulas in every
        installed language that a PO file of ``module_name`` translates."""
        langs = [
            code
            for code, _name in self.env["res.lang"].get_installed()
            if _has_po_file(module_name, code)
        ]
        self.env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
                ("res_id", "in", self.ids),
                ("lang", "in", langs),
            ]
        ).unlink()

    def _reload_description_translations(self, module_name):
        """Give these formulas the description translations of ``module_name``.

        ``self`` must hold only formulas that every PO file of ``module_name``
        carries: in each installed language for which the module has a PO file
        (``es.po`` also covers ``es_MX``), the stored description translations
        of these formulas are deleted and only that file's entries come back.
        The PO files are loaded as a module install does, if the module is
        installed, being installed or being upgraded: a module that is not
        installed or is being uninstalled loads nothing.

        The importer never updates an existing translation of a ``noupdate``
        record, not even with overwrite: hence the delete before the load. It
        writes through SQL, behind the ORM cache: hence the invalidation after
        it, for every formula: the load covers every formula the PO files
        carry, not only these.
        """
        module = self.env["ir.module.module"].search([("name", "=", module_name)])
        module.ensure_one()
        self._delete_description_translations(module_name)
        module._update_translations()
        self.invalidate_cache(["description"])
