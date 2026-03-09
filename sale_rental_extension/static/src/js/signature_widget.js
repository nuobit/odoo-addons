/** @odoo-module */
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {SignatureDialog} from "@web/core/signature/signature_dialog";
import {SignatureWidget} from "@web/views/widgets/signature/signature";
import {patch} from "web.utils";

patch(SignatureWidget.prototype, "sale_rental_extension.SignatureWidget", {
    async onClickSignature() {
        const {record} = this.props;
        const isRental =
            record.resModel === "stock.picking" && record.data.is_rental_picking;
        if (!isRental) {
            return this._super(...arguments);
        }
        const companyId = record.data.company_id && record.data.company_id[0];
        let rentalTerms = "";
        if (companyId) {
            const result = await this.orm.read(
                "res.company",
                [companyId],
                ["rental_signature_terms"]
            );
            if (result.length && result[0].rental_signature_terms) {
                rentalTerms = owl.markup(result[0].rental_signature_terms);
            }
        }
        const nameAndSignatureProps = {
            mode: "draw",
            displaySignatureRatio: 3,
            signatureType: "signature",
            noInputName: true,
        };
        const {fullName} = this.props;
        let defaultName = "";
        if (fullName) {
            let signName = null;
            const fullNameData = record.data[fullName];
            if (record.fields[fullName].type === "many2one") {
                signName = fullNameData && fullNameData[1];
            } else {
                signName = fullNameData;
            }
            defaultName = signName === "" ? undefined : signName;
        }
        nameAndSignatureProps.defaultFont = this.props.defaultFont;
        const dialogProps = {
            defaultName,
            nameAndSignatureProps,
            uploadSignature: (data) => this.uploadSignature(data),
            isRental: true,
            rentalTerms,
        };
        this.dialogService.add(SignatureDialog, dialogProps);
    },
});

patch(SignatureDialog.prototype, "sale_rental_extension.SignatureDialog", {
    setup() {
        this._super(...arguments);
        if (this.props.isRental) {
            this.title = this.env._t("Delivery Signature");
        }
    },
});
