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
