from odoo.addons.component.core import AbstractComponent


class OxigestiSPMSImportMapper(AbstractComponent):
    _name = "oxigesti.spms.import.mapper"
    _inherit = ["connector.extension.import.mapper", "oxigesti.spms.connector"]


class OxigestiSPMSImportMapChild(AbstractComponent):
    _name = "oxigesti.spms.map.child.import"
    _inherit = ["connector.extension.map.child.import", "oxigesti.spms.connector"]
