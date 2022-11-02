# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
import logging

from requests import Session

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.registry import Registry

from odoo.addons.l10n_es_aeat_sii_oca.models.account_move import (
    SII_STATES,
    SII_VERSION,
    round_by_keys,
)

_logger = logging.getLogger(__name__)
try:
    from zeep import Client
    from zeep.plugins import HistoryPlugin
    from zeep.transports import Transport
except (ImportError, IOError) as err:
    _logger.debug(err)

try:
    pass
except ImportError:
    _logger.debug("Can not `import queue_job`.")


class AssetProrateRegularization(models.Model):
    _inherit = "capital.asset.prorate.regularization"

    sii_state = fields.Selection(
        selection=SII_STATES,
        string="SII send state",
        default="not_sent",
        readonly=True,
        copy=False,
        help="Indicates the state of this invoice in relation with the "
        "presentation at the SII",
    )
    sii_csv = fields.Char(
        string="SII CSV",
        copy=False,
        readonly=True,
    )
    sii_return = fields.Text(
        string="SII Return",
        copy=False,
        readonly=True,
    )
    sii_header_sent = fields.Text(
        string="SII last header sent",
        copy=False,
        readonly=True,
    )
    sii_content_sent = fields.Text(
        string="SII last content sent",
        copy=False,
        readonly=True,
    )
    sii_send_error = fields.Text(
        string="SII Send Error",
        copy=False,
        readonly=True,
    )
    sii_send_failed = fields.Boolean(
        string="SII send failed",
        copy=False,
        help="Indicates that the last attempt to communicate this invoice to "
        "the SII has failed. See SII return for details",
    )

    sii_account_registration_date = fields.Date(
        string="SII account registration date",
        readonly=True,
        copy=False,
        help="Indicates the account registration date set at the SII, which "
        "must be the date when the invoice is recorded in the system and "
        "is independent of the date of the accounting entry of the "
        "invoice",
    )
    asset_prorate_line_job_ids = fields.Many2many(
        comodel_name="queue.job",
        column1="asset_prorate_line_id",
        column2="job_id",
        # TODO: remove this comment.Nom relation Massa llarg?
        relation="capital_asset_prorate_regularization_queue_job_rel",
        string="Connector Jobs",
        copy=False,
    )
    sii_enabled = fields.Boolean(string="Enable SII", compute="_compute_sii_enabled")

    def _compute_sii_enabled(self):
        """Compute if the asset is enabled for the SII"""
        for line in self:
            if line.asset_id.company_id.sii_enabled:
                asset_invoice = self.asset_id.invoice_move_line_id.move_id
                self.sii_enabled = (
                    asset_invoice.fiscal_position_id
                    and asset_invoice.fiscal_position_id.sii_active
                ) or not asset_invoice.fiscal_position_id
            else:
                self.sii_enabled = False

    def _get_account_registration_date(self):
        """Hook method to allow the setting of the account registration date
        of each supplier invoice. The SII recommends to set the send date as
        the default value (point 9.3 of the document
        SII_Descripcion_ServicioWeb_v0.7.pdf), so by default we return
        the current date or, if exists, the stored
        sii_account_registration_date
        :return String date in the format %Y-%m-%d"""
        self.ensure_one()
        return self.sii_account_registration_date or fields.Date.today()

    def confirm_one_capital_asset_prorate_line(self):
        self.sudo()._send_asset_to_sii()

    def cancel_one_capital_asset_prorate_line(self):
        self.sudo()._cancel_asset_to_sii()

    def _process_asset_for_sii_send(self):
        """Process invoices for sending to the SII. Adds general checks from
        configuration parameters and invoice availability for SII. If the
        invoice is to be sent the decides the send method: direct send or
        via connector depending on 'Use connector' configuration"""
        # TODO: descomentar
        queue_obj = self.env["queue.job"].sudo()
        for asset_line in self:
            company = asset_line.asset_id.company_id
            if not company.capital_asset_use_connector:
                asset_line._send_asset_to_sii()
            # TODO:descomentar cuando esten los jobs
            else:
                eta = company._get_sii_eta_capital_assets()
                new_delay = (
                    asset_line.sudo()
                    .with_context(company_id=company.id)
                    .with_delay(eta=eta if not asset_line.sii_send_failed else False)
                    .confirm_one_capital_asset_prorate_line()
                )
                job = queue_obj.search([("uuid", "=", new_delay.uuid)], limit=1)
                asset_line.sudo().asset_prorate_line_job_ids |= job

    def send_asset_sii(self):
        if (
            self.mod303_id
            and self.mod303_id.move_prorate_capital_asset_id.state == "draft"
            or (self.mod303_id and not self.mod303_id.move_prorate_capital_asset_id)
        ):
            raise ValidationError(
                _(
                    "Please, post capital asset prorate regularization move before send "
                    "capital asset prorate regularization to SII"
                )
            )
        if not self._cancel_asset_jobs():
            self._process_asset_for_sii_send()

    def _send_asset_to_sii(self):
        serv = self._connect_sii("capital_asset")
        if self.sii_state == "not_sent":
            tipo_comunicacion = "A0"
        else:
            tipo_comunicacion = "A1"
        header = self._get_sii_header(tipo_comunicacion)
        asset_line_vals = {
            "sii_header_sent": json.dumps(header, indent=4),
        }
        try:
            asset_dict = self._get_sii_asset_dict()
            asset_line_vals["sii_content_sent"] = json.dumps(asset_dict, indent=4)
            res = serv.SuministroLRBienesInversion(header, asset_dict)
            res_line = res["RespuestaLinea"][0]
            if res["EstadoEnvio"] == "Correcto":
                asset_line_vals.update(
                    {
                        "sii_state": "sent",
                        "sii_csv": res["CSV"],
                        "sii_send_failed": False,
                    }
                )
            elif (
                res["EstadoEnvio"] == "ParcialmenteCorrecto"
                and res_line["EstadoRegistro"] == "AceptadoConErrores"
            ):
                asset_line_vals.update(
                    {
                        "sii_state": "sent_w_errors",
                        "sii_csv": res["CSV"],
                        "sii_send_failed": True,
                    }
                )
            else:
                asset_line_vals["sii_send_failed"] = True
            if (
                "sii_state" in asset_line_vals
                and not self.sii_account_registration_date
            ):
                asset_line_vals[
                    "sii_account_registration_date"
                ] = self._get_account_registration_date()
            asset_line_vals["sii_return"] = res
            send_error = False
            if res_line["CodigoErrorRegistro"]:
                send_error = "{} | {}".format(
                    str(res_line["CodigoErrorRegistro"]),
                    str(res_line["DescripcionErrorRegistro"])[:60],
                )
            asset_line_vals["sii_send_error"] = send_error
            self.write(asset_line_vals)

        except Exception as fault:
            new_cr = Registry(self.env.cr.dbname).cursor()
            env = api.Environment(new_cr, self.env.uid, self.env.context)
            asset_line = env["capital.asset.prorate.regularization"].browse(self.id)
            asset_line_vals.update(
                {
                    "sii_send_failed": True,
                    "sii_send_error": repr(fault)[:60],
                    "sii_return": repr(fault),
                }
            )
            asset_line.write(asset_line_vals)
            new_cr.commit()
            new_cr.close()
            raise

    def cancel_asset_sii(self):
        if not self._cancel_asset_jobs():
            queue_obj = self.env["queue.job"]
            for asset_line in self:
                company = self.asset_id.company_id
                if not company.capital_asset_use_connector:
                    self._cancel_asset_to_sii()
                else:
                    eta = company._get_sii_eta_capital_assets()
                    new_delay = (
                        self.sudo()
                        .with_context(company_id=company.id)
                        .with_delay(eta=eta)
                        .cancel_one_capital_asset_prorate_line()
                    )
                    job = queue_obj.search([("uuid", "=", new_delay.uuid)], limit=1)
                    asset_line.sudo().asset_prorate_line_job_ids |= job

    def _cancel_asset_to_sii(self):
        serv = self._connect_sii("capital_asset")
        header = self._get_sii_header(cancellation=True)
        asset_line_vals = {
            "sii_send_failed": True,
            "sii_send_error": False,
        }
        try:
            asset_dict = self._get_cancel_sii_asset_dict()
            res = serv.AnulacionLRBienesInversion(header, asset_dict)
            asset_line_vals["sii_return"] = res
            if res["EstadoEnvio"] == "Correcto":
                asset_line_vals.update(
                    {
                        "sii_state": "cancelled",
                        "sii_csv": res["CSV"],
                        "sii_send_failed": False,
                    }
                )
            res_line = res["RespuestaLinea"][0]

            if res_line["CodigoErrorRegistro"]:
                asset_line_vals["sii_send_error"] = "{} | {}".format(
                    str(res_line["CodigoErrorRegistro"]),
                    str(res_line["DescripcionErrorRegistro"])[:60],
                )
            self.write(asset_line_vals)
        except Exception as fault:
            new_cr = Registry(self.env.cr.dbname).cursor()
            env = api.Environment(new_cr, self.env.uid, self.env.context)
            asset_line = env["capital.asset.prorate.regularization"].browse(self.id)
            asset_line_vals.update(
                {
                    "sii_send_failed": True,
                    "sii_send_error": repr(fault)[:60],
                    "sii_return": repr(fault),
                }
            )
            asset_line.write(asset_line_vals)
            new_cr.commit()
            new_cr.close()
            raise

    def _get_cancel_sii_asset_dict(self):
        self.ensure_one()
        self._sii_check_exceptions()
        return self._get_sii_asset_dict(cancel=True)

    def _cancel_asset_jobs(self):
        job_started = False
        for queue in self.sudo().mapped("asset_prorate_line_job_ids"):
            if queue.state == "started":
                job_started = True
            elif queue.state in ("pending", "enqueued", "failed"):
                queue.unlink()
        return job_started

    def _connect_sii(self, mapping_key):
        self.ensure_one()
        public_crt, private_key = self.env["l10n.es.aeat.certificate"].get_certificates(
            company=self.asset_id.company_id
        )
        params = self._connect_params_sii(mapping_key)
        session = Session()
        session.cert = (public_crt, private_key)
        transport = Transport(session=session)
        history = HistoryPlugin()
        client = Client(wsdl=params["wsdl"], transport=transport, plugins=[history])
        return self._bind_sii(client, params["port_name"], params["address"])

    def _bind_sii(self, client, port_name, address=None):
        self.ensure_one()
        service = client._get_service("siiService")
        port = client._get_port(service, port_name)
        address = address or port.binding_options["address"]
        return client.create_service(port.binding.name, address)

    def _connect_params_sii(self, mapping_key):
        self.ensure_one()
        agency = self.asset_id.company_id.tax_agency_id
        if not agency:
            # We use spanish agency by default to keep old behavior with
            # ir.config parameters. In the future it might be good to reinforce
            # to explicitly set a tax agency in the company by raising an error
            # here.
            agency = self.env.ref("l10n_es_aeat.aeat_tax_agency_spain")
        return agency._connect_params_sii(mapping_key, self.asset_id.company_id)

    def _get_sii_header(self, tipo_comunicacion=False, cancellation=False):
        """Builds SII send header

        :param tipo_comunicacion String 'A0': new reg, 'A1': modification
        :param cancellation Bool True when the communitacion es for invoice
            cancellation
        :return Dict with header data depending on cancellation
        """
        self.ensure_one()
        company = self.asset_id.company_id
        if not company.vat:
            raise exceptions.UserError(
                _("No VAT configured for the company '{}'").format(company.name)
            )
        header = {
            "IDVersionSii": SII_VERSION,
            "Titular": {
                "NombreRazon": self.asset_id.company_id.name[0:120],
                "NIF": self.asset_id.company_id.vat[2:],
            },
        }
        if not cancellation:
            header.update({"TipoComunicacion": tipo_comunicacion})
        return header

    def _get_sii_identifier(self):
        """Get the SII structure for a partner identifier depending on the
        conditions of the invoice.
        """
        self.ensure_one()
        gen_type = self._get_sii_gen_type()
        (
            country_code,
            identifier_type,
            identifier,
        ) = self._sii_get_partner()._parse_aeat_vat_info()
        # Limpiar alfanum
        if identifier:
            identifier = "".join(e for e in identifier if e.isalnum()).upper()
        else:
            identifier = "NO_DISPONIBLE"
            identifier_type = "06"
        if gen_type == 1:
            if "1117" in (self.sii_send_error or ""):
                return {
                    "IDOtro": {
                        "CodigoPais": country_code,
                        "IDType": "07",
                        "ID": identifier,
                    }
                }
            else:
                if identifier_type == "":
                    return {"NIF": identifier}
                return {
                    "IDOtro": {
                        "CodigoPais": country_code,
                        "IDType": identifier_type,
                        "ID": identifier,
                    },
                }
        elif gen_type == 2:
            return {"IDOtro": {"IDType": "02", "ID": country_code + identifier}}
        elif gen_type == 3 and identifier_type:
            return {
                "IDOtro": {
                    "CodigoPais": country_code,
                    "IDType": identifier_type,
                    "ID": identifier,
                },
            }
        elif gen_type == 3:
            return {"NIF": identifier}

    def _get_sii_gen_type(self):
        """Make a choice for general invoice type

        Returns:
            int: 1 (National), 2 (Intracom), 3 (Export)
        """
        self.ensure_one()
        partner_ident = self.asset_id.partner_id.property_account_position_id
        partner_ident_type = partner_ident.sii_partner_identification_type
        if partner_ident_type:
            res = int(partner_ident_type)
        elif partner_ident.name == "Régimen Intracomunitario":
            res = 2
        elif partner_ident.name == "Régimen Extracomunitario":
            res = 3
        else:
            res = 1
        return res

    def _get_sii_body(self, cancel=False):
        body = {
            "PeriodoLiquidacion": {"Ejercicio": self.year, "Periodo": "0A"},
            "IDFactura": {
                "IDEmisorFactura": {
                    "NombreRazon": self.asset_id.partner_id.name[0:120],
                    # "NIF": self.asset_id.partner_id.vat[2:],
                    **self._get_sii_identifier(),
                },
                "NumSerieFacturaEmisor": (self.asset_id.invoice_ref or "")[0:60],
                "FechaExpedicionFacturaEmisor": self._change_date_format(
                    self.asset_id.invoice_date
                ),
            },
        }
        if cancel:
            body["IdentificacionBien"] = self.asset_id.name.replace("\n", " ")[0:40]
        else:
            body["BienesInversion"] = {
                "IdentificacionBien": self.asset_id.name.replace("\n", " ")[0:40],
                "FechaInicioUtilizacion": self._change_date_format(
                    self.asset_id.date_start
                ),
                "ProrrataAnualDefinitiva": self.prorate_percent,
                # OPCIONALES
                "RegularizacionAnualDeduccion": self.amount,
                # "IdentificacionEntrega": None,
                # RegularizacionDeduccionEfectuada is used when asset is sold. Not implemented
                # "RegularizacionDeduccionEfectuada": self.asset_id.final_deductible_tax_amount,
                # "RefExterna": (self.asset_id.invoice_ref or "")[0:60],
                # "NumRegistroAcuerdoFacturacion": None,
                # "EntidadSucedida": {
                #     "NombreRazon": self.asset_id.partner_id.name[0:120],
                #     "NIF": self.asset_id.partner_id.vat[2:],
                # },
            }
        return body

    def _get_sii_asset_dict(self, cancel=False):
        self._sii_check_exceptions()
        asset_dict = self._get_sii_body(cancel)
        round_by_keys(
            asset_dict,
            [
                "ProrrataAnualDefinitiva",
                "RegularizacionAnualDeduccion",
                "RegularizacionDeduccionEfectuada",
            ],
        )
        return asset_dict

    def _change_date_format(self, date):
        datetimeobject = fields.Date.to_date(date)
        new_date = datetimeobject.strftime("%d-%m-%Y")
        return new_date

    def _check_fiscal_position(self):
        partner_fiscal_position = self.asset_id.partner_id.property_account_position_id
        asset_invoice = self.asset_id.invoice_move_line_id.move_id
        if asset_invoice:
            if asset_invoice.fiscal_position_id != partner_fiscal_position:
                raise ValidationError(
                    _(
                        "The fiscal position of the partner and of the invoice is different."
                        "Please review asset: {%i} %s"
                    )
                    % (self.asset_id.id, self.asset_id.name)
                )

    def _get_sii_country_code(self):
        self.ensure_one()
        return self._sii_get_partner()._parse_aeat_vat_info()[0]

    def _sii_get_partner(self):
        return self.asset_id.partner_id

    def _is_sii_simplified_invoice(self):
        """Inheritable method to allow control when an
        invoice are simplified or normal"""
        partner = self._sii_get_partner()
        is_simplified = partner.sii_simplified_invoice
        return is_simplified

    def _sii_check_exceptions(self):
        """Inheritable method for exceptions control when sending SII invoices."""
        self.ensure_one()
        self._check_fiscal_position()
        gen_type = self._get_sii_gen_type()
        # invoice_move_line
        partner = self._sii_get_partner()
        country_code = self._get_sii_country_code()
        if (gen_type != 3 or country_code == "ES") and not partner.vat:
            raise exceptions.UserError(_("The partner has not a VAT configured."))
        if not self.asset_id.company_id.chart_template_id:
            raise exceptions.UserError(
                _("You have to select what account chart template use this company.")
            )
        if not self.asset_id.company_id.sii_enabled:
            raise exceptions.UserError(_("This company doesn't have SII enabled."))

    def unlink(self):
        for rec in self:
            if rec.sii_state != "not_sent":
                raise ValidationError(
                    _(
                        "You can't delete a capital asset prorate "
                        "regularization line if it has been previously sent"
                    )
                )
        super(AssetProrateRegularization, self).unlink()
