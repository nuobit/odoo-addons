from odoo.addons.component.core import AbstractComponent


class ConnectorExtensionRecordDirectExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.record.direct.export.deleter"
    _inherit = [
        "connector.extension.record.direct.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.batch.export.deleter"
    _inherit = [
        "connector.extension.batch.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchtDirectExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.batch.direct.export.deleter"
    _inherit = [
        "connector.extension.batch.direct.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchDelayedExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.batch.delayed.export.deleter"
    _inherit = [
        "connector.extension.batch.export.deleter",
        "oxigesti.spms.connector",
    ]
