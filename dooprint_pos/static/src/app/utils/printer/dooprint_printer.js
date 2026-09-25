import { EpsonPrinter } from "@point_of_sale/app/utils/printer/epson_printer";
import { getLNATargetAddressSpace } from "@point_of_sale/app/utils/init_lna";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

/**
 * Printer of a Dooprint device. The device speaks ePOS, so the ticket is rendered exactly like
 * for an Epson printer; only the way it travels changes:
 *
 * - "server": the ticket goes to Odoo, which queues it for the device. Works from any network.
 * - "browser": the ticket goes straight to the device over the local network.
 */
export class DooprintPrinter extends EpsonPrinter {
    setup({ printer, configId }) {
        // The device serves plain HTTP on the local network: from an HTTPS page the browser only
        // allows it through Local Network Access. The address getter needs the url already.
        this.url = printer.dooprint_url;
        super.setup(...arguments);
        this.configId = configId;
        this.printerId = printer.raw?.dooprint_printer_id ?? printer.dooprint_printer_id?.id;
        this.delivery = printer.dooprint_delivery;
        // Odoo only sends the Local Network Access hint when use_lna is set; from the browser the
        // device needs it whatever the checkbox says.
        this.use_lna = this.delivery === "browser";
        this.lnaTargetAddressSpace = getLNATargetAddressSpace(this.address);
    }

    /**
     * @override
     * The device exposes the ePOS service of the printer it holds.
     */
    get address() {
        return `${this.url}/cgi-bin/epos/service.cgi`;
    }

    /**
     * @override
     */
    async sendPrintingJob(payload) {
        if (this.delivery === "browser") {
            if (!this.url) {
                return this.notReachable(_t("The Dooprint device has not reported its address."));
            }
            const result = await super.sendPrintingJob(payload);
            if (result.errorCode === "PRINTER_NOT_REACHABLE") {
                result.message = _t(
                    "The Dooprint device at %s cannot be reached. Check that this browser is on the same network and allows Local Network Access.",
                    this.url
                );
            }
            return result;
        }
        try {
            return await this.sendThroughOdoo(payload);
        } catch {
            return this.notReachable(_t("Odoo could not queue the ticket. Check your connection."));
        }
    }

    sendThroughOdoo(payload) {
        return rpc("/dooprint_pos/print", {
            config_id: this.configId,
            printer_id: this.printerId,
            payload,
        });
    }

    notReachable(message) {
        return { result: false, canRetry: true, errorCode: "PRINTER_NOT_REACHABLE", message };
    }

    /**
     * @override
     * Odoo explains why a job failed; show that instead of the Epson error codes.
     */
    getResultsError(printResult) {
        const error = super.getResultsError(printResult);
        if (printResult?.message) {
            error.message.body = printResult.message;
        }
        return error;
    }
}
