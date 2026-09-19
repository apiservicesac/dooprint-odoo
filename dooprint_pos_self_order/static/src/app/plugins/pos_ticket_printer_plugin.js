import { PosTicketPrinterPlugin } from "@point_of_sale/app/plugins/pos_ticket_printer_plugin";
import { DooprintSelfOrderPrinter } from "@dooprint_pos_self_order/app/utils/printer/dooprint_self_order_printer";
import { patch } from "@web/core/utils/patch";

patch(PosTicketPrinterPlugin.prototype, {
    /**
     * In the kiosk and on a phone the ticket goes through the public self order route, and only
     * the kiosk may talk to the device from the browser: a phone is not on its network.
     * @override
     */
    async createPrinterInstance(printer) {
        if (printer.printer_type === "dooprint") {
            return new DooprintSelfOrderPrinter({
                printer,
                models: this.data.models,
                accessToken: odoo.access_token,
                kiosk: this.config.self_ordering_mode === "kiosk",
            });
        }
        return super.createPrinterInstance(...arguments);
    },
});
