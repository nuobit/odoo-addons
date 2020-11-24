# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC - Ainara Galdona
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, exceptions, _


class L10nEsAeatMod303Report(models.Model):
    _inherit = 'l10n.es.aeat.mod303.report'

    def button_first_prorrate_regularitzation(self):
        pass

    def button_second_investment_goods_regularitzation(self):
        pass

    def button_second_investment_goods_regularization_send_SII(self):
        pass
