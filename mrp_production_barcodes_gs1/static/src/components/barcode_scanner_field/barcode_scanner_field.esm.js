/** @odoo-module **/

/* Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

import {CharField, charField} from "@web/views/fields/char/char_field";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class BarcodeScannerField extends CharField {
    static template = "mrp_production_barcodes_gs1.BarcodeScannerField";
    static props = {
        ...CharField.props,
        lotField: {type: String, optional: true},
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    async onChange(ev) {
        const raw_barcode = ev.target.value;
        if (raw_barcode) {
            await this.props.record.update({[this.props.name]: ""});
            if (this.props.record.isDirty) {
                await this.props.record.save();
            }
            const production_id = this.props.record.resId;
            const lot_field = this.props.lotField;
            if (lot_field) {
                const lot = this.props.record.data[lot_field];
                await this.orm.call(
                    "mrp.production",
                    "action_process_barcode_byproducts",
                    [production_id, raw_barcode, lot[1]],
                    {allow_duplicate_moves: true}
                );
            } else {
                await this.orm.call(
                    "mrp.production",
                    "action_process_barcode_components",
                    [production_id, raw_barcode]
                );
            }
            await this.props.record.load();
        }
    }
}

export const barcodeScannerField = {
    ...charField,
    component: BarcodeScannerField,
    displayName: _t("Barcode Scanner"),
    supportedOptions: [
        ...(charField.supportedOptions || []),
        {
            label: _t("Lot field name"),
            name: "lot_field",
            type: "string",
            help: _t("Field name in the record that holds the lot value."),
        },
    ],
    extractProps: ({attrs, options}) => ({
        ...charField.extractProps({attrs, options}),
        lotField: options.lot_field || "",
    }),
};

registry.category("fields").add("barcode_scanner_field", barcodeScannerField);
