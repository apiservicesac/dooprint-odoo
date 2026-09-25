import { DooprintPrinter } from "@dooprint_pos/app/utils/printer/dooprint_printer";
import { rpc } from "@web/core/network/rpc";

/**
 * dooprint printer for the kiosk and phone orders: the ticket goes through the public self order
 * route, which checks the order before queueing it.
 */
export class DooprintSelfOrderPrinter extends DooprintPrinter {
    setup({ models, accessToken, kiosk }) {
        super.setup(...arguments);
        this.models = models;
        this.accessToken = accessToken;
        // A phone is not on the printer network: its orders always go through Odoo.
        if (!kiosk) {
            this.delivery = "server";
            this.use_lna = false;
        }
    }

    sendThroughOdoo(payload) {
        const order = this.models["pos.order"].getAll().findLast((o) => o.id && o.access_token);
        return rpc("/dooprint_pos/self_order/print", {
            access_token: this.accessToken,
            printer_id: this.printerId,
            payload,
            order_id: order?.id,
            order_access_token: order?.access_token,
        });
    }
}
