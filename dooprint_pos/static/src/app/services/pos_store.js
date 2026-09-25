import { PosStore } from "@point_of_sale/app/store/pos_store";
import { DooprintPrinter } from "@dooprint_pos/app/utils/printer/dooprint_printer";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        await super.afterProcessServerData(...arguments);
        if (this.config.raw.dooprint_printer_id) {
            this.hardwareProxy.printer = this.createDooprintPrinter(
                this.config.raw.dooprint_printer_id,
                this.config.dooprint_url
            );
        }
        if (this.usesDooprintFromBrowser()) {
            // Turn on Odoo's Local Network Access handling (permission check and notifications)
            // as the "point_of_sale.use_lna" parameter does for Epson.
            odoo.use_lna = true;
        }
    },

    /**
     * True when this POS sends tickets from the browser straight to a Dooprint device.
     */
    usesDooprintFromBrowser() {
        return (
            this.config.dooprint_delivery === "browser" &&
            (Boolean(this.config.raw.dooprint_printer_id) ||
                this.models["pos.printer"].getAll().some((printer) => printer.printer_type === "dooprint"))
        );
    },

    /**
     * Preparation printers of type dooprint.
     * @override
     */
    create_printer(config) {
        if (config.printer_type === "dooprint") {
            // The printer arrives serialized, and a many2one to a model the POS does not load
            // comes as false: read it from the raw record.
            const printerId = this.models["pos.printer"].get(config.id).raw.dooprint_printer_id;
            return this.createDooprintPrinter(printerId, config.dooprint_url);
        }
        return super.create_printer(...arguments);
    },

    createDooprintPrinter(printerId, url) {
        return new DooprintPrinter({
            configId: this.config.id,
            printerId,
            url,
            delivery: this.config.dooprint_delivery,
        });
    },
});
