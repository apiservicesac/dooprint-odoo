import { HardwareProxy } from "@point_of_sale/app/hardware_proxy/hardware_proxy_service";
import { patch } from "@web/core/utils/patch";

patch(HardwareProxy.prototype, {
    /**
     * The cash drawer hangs from the dooprint receipt printer, which is not an IoT Box connection.
     * @override
     */
    async openCashbox(action = false) {
        const config = this.pos.config;
        if (!config.raw.dooprint_printer_id || !this.printer) {
            return super.openCashbox(...arguments);
        }
        if (config.iface_cashdrawer) {
            this.printer.openCashbox();
            if (action) {
                this.pos.logEmployeeMessage(action, "CASH_DRAWER_ACTION");
            }
        }
    },
});
