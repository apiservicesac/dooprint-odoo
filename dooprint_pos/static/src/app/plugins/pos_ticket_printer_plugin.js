import { PosTicketPrinterPlugin } from "@point_of_sale/app/plugins/pos_ticket_printer_plugin";
import { DooprintPrinter } from "@dooprint_pos/app/utils/printer/dooprint_printer";
import { patch } from "@web/core/utils/patch";

patch(PosTicketPrinterPlugin.prototype, {
    /**
     * Receipt and preparation printers of type dooprint.
     * @override
     */
    async createPrinterInstance(printer) {
        if (printer.printer_type === "dooprint") {
            return new DooprintPrinter({ printer, configId: this.config.id });
        }
        return super.createPrinterInstance(...arguments);
    },
});
