# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import unicodedata

from odoo import _, api, fields, models, re
from odoo.exceptions import UserError, ValidationError


class PartnerDocumentType(models.Model):
    _name = "partner.document.type"
    _description = "Partner Document Type"
    _order = "sequence"

    name = fields.Char(
        translate=True,
        required=True,
    )
    # code = fields.Char(string="Code")
    description = fields.Text()
    sequence = fields.Integer(
        required=True,
        default=1,
    )
    template_id = fields.Many2one(comodel_name="partner.document.template")
    no_expiration = fields.Boolean(
        default=False,
        help="Check this if the document type does not require an expiration date.",
    )
    classification_ids = fields.Many2many(
        comodel_name="partner.classification",
        relation="partner_classification_document_type_rel",
        column1="document_type_id",
        column2="classification_id",
        readonly=True,
    )
    partner_count = fields.Integer(
        compute="_compute_partner_count",
        help="Number of distinct partners with documents of this type.",
    )

    def _compute_partner_count(self):
        for record in self:
            record.partner_count = self.env["res.partner"].search_count(
                [("document_ids.document_type_id", "=", record.id)]
            )

    @api.model
    def _normalize(self, s):
        # heuristic normalization of a string to create a slug
        # all lowercase and strip spaces
        s = s.lower().strip()
        # remove accents and diacritics, convert to ASCII
        s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
        # remove duplicated simbols or spaces
        s = re.sub(r"(.)\1+", r"\1", s)
        # special susbtitutions
        s = s.replace(" de ", " ")
        # remove spaces
        s = s.replace(" ", "")
        return s

    @api.model
    def _get_others_by_lang(self, langs):
        all_doct_d = {}
        for doct in self.with_context(active_test=False).search([]):
            for lang in langs:
                all_doct_d.setdefault(lang, {})
                slug = self._normalize(doct.name)
                all_doct_d[lang].setdefault(slug, self.env[self._name])
                all_doct_d[lang][slug] |= doct
        return all_doct_d

    def _check_name_duplicated(self, name, lang, all_doct_d):
        for rec in self:
            slug = self._normalize(name)
            if slug in all_doct_d:
                others = all_doct_d[slug] - rec
                if others:
                    others_l = ["[%i] '%s'" % (x.id, x.name) for x in others]
                    raise ValidationError(
                        _(
                            "The document type name '%(name)s' is not unique. "
                            "It has other %(others_num)i documents type with similar "
                            "name in language '%(lang)s': %(others)s. Please choose a "
                            "different name."
                        )
                        % {
                            "name": name,
                            "lang": lang,
                            "others_num": len(others),
                            "others": ", ".join(others_l),
                        }
                    )

    @api.constrains("name")
    def _check_name(self):
        all_doct_d = self._get_others_by_lang([self.env.lang])[self.env.lang]
        self._check_name_duplicated(self.name, self.env.lang, all_doct_d)

    def update_field_translations(self, field_name, translations):
        # Check for name uniqueness across languages
        if field_name == "name":
            translations_other = dict(translations)
            translations_other.pop(self.env.lang, None)
            all_doct_lang_d = self._get_others_by_lang(translations_other.keys())
            for lang, new_name in translations_other.items():
                all_doct_d = all_doct_lang_d[lang]
                self._check_name_duplicated(new_name, lang, all_doct_d)
        return super().update_field_translations(field_name, translations)

    @api.constrains("template_id")
    def _check_template_id(self):
        for rec in self:
            if rec.template_id:
                if not rec.template_id.file_ids.filtered(lambda x: x.default):
                    raise ValidationError(
                        _("To assign a template, you must first set a default file.")
                    )

    def write(self, vals):
        for rec in self:
            if "no_expiration" in vals and vals["no_expiration"] is False:
                docs_without_exp = self.env["partner.document"].search(
                    [("document_type_id", "=", rec.id), ("expiration_date", "=", False)]
                )
                if docs_without_exp:
                    raise ValidationError(
                        _(
                            "Cant 'uncheck 'No Expiration' due to docs without expiration date"
                        )
                    )
        return super().write(vals)

    def unlink(self):
        records = self.env["partner.classification"].search(
            [("document_type_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        records = self.env["partner.document"].search(
            [("document_type_id", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super(PartnerDocumentType, self).unlink()
