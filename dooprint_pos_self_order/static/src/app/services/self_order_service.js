import { SelfOrder } from "@pos_self_order/app/self_order_service";
import { DooprintSelfOrderPrinter } from "@dooprint_pos_self_order/app/utils/printer/dooprint_self_order_printer";
import { initLNA } from "@point_of_sale/app/utils/init_lna";
import { patch } from "@web/core/utils/patch";

patch(SelfOrder.prototype, {
    async setup() {
        await super.setup(...arguments);
        if (this.config.raw.dooprint_printer_id) {
            this.printer.setPrinter(
                this.createDooprintPrinter(this.config.raw.dooprint_printer_id, this.config.dooprint_url)
            );
        }
        if (this.dooprintDelivery() === "browser" && !odoo.use_lna) {
            // The kiosk talks to the device from the browser: check Local Network Access as Odoo
            // does for Epson printers when "point_of_sale.use_lna" is set.
            odoo.use_lna = true;
            initLNA(this.notification);
        }
    },

    dooprintDelivery() {
        // A phone is not on the printer network: its orders always go through Odoo.
        return this.config.self_ordering_mode === "kiosk" ? this.config.dooprint_delivery : "server";
    },

    /**
     * Preparation printers of type dooprint.
     * @override
     */
    create_printer(printer) {
        if (printer.printer_type === "dooprint") {
            return this.createDooprintPrinter(printer.raw.dooprint_printer_id, printer.dooprint_url);
        }
        return super.create_printer(...arguments);
    },

    createDooprintPrinter(printerId, url) {
        return new DooprintSelfOrderPrinter({
            selfOrder: this,
            printerId,
            url,
            delivery: this.dooprintDelivery(),
        });
    },
});
