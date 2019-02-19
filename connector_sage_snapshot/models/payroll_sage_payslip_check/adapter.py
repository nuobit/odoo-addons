# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component

import sqlite3
import logging

import datetime

_logger = logging.getLogger(__name__)


class PayslipCheckAdapter(Component):
    _inherit = 'sage.payroll.sage.payslip.check.adapter'

    def _exec_query(self, filters=None, fields=None, as_dict=True):
        snapshot_ids = self.env['connector.sage.snapshot.database'].search([
            ('company_id', '=', self.backend_record.company_id.id),
            ('year', '=', filters.get('Año')),
            ('month', '=', filters.get('MesD')),
        ])
        if snapshot_ids:
            attachment_id = self.env['ir.attachment'].search([
                ('id', '!=', False),
                ('res_id', '=', snapshot_ids.id),
                ('res_model', '=', snapshot_ids._name),
                ('res_field', '=', 'datas'),
            ])
            dbfile = attachment_id._full_path(attachment_id.store_fname)

            conn = sqlite3.connect(dbfile)

            c = conn.cursor()

            sql = """SELECT ec.CodigoEmpresa, ec.CodigoEmpleado, sum(ec.ImporteFijo) as ImporteFijo
                     FROM EmpleadoCobro ec
                     WHERE ec.CodigoFormaCobro = 'TAL' AND
                           ec.ImporteFijo !=0 AND
                           ec.CodigoEmpresa = :CodigoEmpresa AND
                           (:CodigoEmpleado is null or ec.CodigoEmpleado=:CodigoEmpleado) and
                           exists (
                              SELECT 1
                              FROM Historico h, ConvenioConcepto c
                              WHERE h.Año = :Año AND
                                    h.MesD = :MesD AND
                                    h.TotalFichaHistorica IN ('TD1', 'TR1') AND
                                    h.CodigoConceptoNom = c.CodigoConceptoNom AND
                                    h.CodigoEmpresa = c.CodigoEmpresa AND
                                    h.FechaCobro = :FechaCobro AND
                                    c.Codigoconvenio = :CodigoConvenio AND
                                    c.FechaRegistroCV = :FechaRegistroCV AND
                                    h.CodigoEmpresa = ec.Codigoempresa AND
                                    h.IdEmpleado = ec.IdEmpleado AND
                                    h.CodigoEmpleado = ec.CodigoEmpleado
                           )
                     group by ec.CodigoEmpresa, ec.CodigoEmpleado
            """

            params_d = {}
            for p in self._id:
                if p in filters:
                    v = filters[p]
                    if isinstance(v, (datetime.date, datetime.datetime)):
                        v = v.strftime('%Y-%m-%d %H:%M:%S')
                    params_d[p] = v
                else:
                    params_d[p] = None

            c.execute(sql, params_d)

            res = []
            headers = [desc[0] for desc in c.description]
            for row in c:
                row_d = dict(zip(headers, row))
                for f in filters:
                    if f not in row_d:
                        row_d[f] = filters[f]
                res.append(row_d)

            c.close()
            conn.close()

            ### cmprovem que la clau primaria sigui unica
            if self._id and set(self._id).issubset(set(filters)):
                self._check_uniq(res)

            return res
        else:
            return super()._exec_query(filters=filters, fields=fields, as_dict=as_dict)
