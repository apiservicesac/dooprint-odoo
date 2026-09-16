import { SelfOrder } from "@pos_self_order/app/services/self_order_service";
import { DooprintSelfOrderPrinter } from "@dooprint_pos_self_order/app/utils/printer/dooprint_self_order_printer";
import { patch } from "@web/core/utils/patch";

patch(SelfOrder.prototype, {
    async setup() {
        await super.setup(...arguments);
        if (this.config.raw.dooprint_printer_id) {
            this.printer.setPrinter(
                this.createDooprintPrinter(this.config.raw.dooprint_printer_id, this.config.dooprint_url)
            );
        }
    },

    /**
     * Preparation printers of type dooprint.
     * @override
     */
    createPrinter(printer) {
        if (printer.printer_type === "dooprint") {
            return this.createDooprintPrinter(printer.raw.dooprint_printer_id, printer.dooprint_url);
        }
        return super.createPrinter(...arguments);
    },

    createDooprintPrinter(printerId, url) {
        // A phone is not on the printer network: its orders always go through Odoo.
        const delivery =
            this.config.self_ordering_mode === "kiosk" ? this.config.dooprint_delivery : "server";
        return new DooprintSelfOrderPrinter({ selfOrder: this, printerId, url, delivery });
    },
});
