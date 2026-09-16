import { PosStore } from "@point_of_sale/app/services/pos_store";
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
            // Turn on Odoo's Local Network Access handling (permission check, notifications and
            // the status in the menu) as the "point_of_sale.use_lna" parameter does for Epson.
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
     * Address of the first Dooprint device the browser talks to.
     */
    dooprintDeviceUrl() {
        if (this.config.dooprint_url) {
            return this.config.dooprint_url;
        }
        return this.models["pos.printer"].getAll().find((printer) => printer.dooprint_url)?.dooprint_url;
    },

    /**
     * Preparation printers of type dooprint.
     * @override
     */
    createPrinter(config) {
        if (config.printer_type === "dooprint") {
            return this.createDooprintPrinter(config.dooprint_printer_id, config.dooprint_url);
        }
        return super.createPrinter(...arguments);
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
