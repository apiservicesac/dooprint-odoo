import { DooprintPrinter } from "@dooprint_pos/app/utils/printer/dooprint_printer";
import { rpc } from "@web/core/network/rpc";

/**
 * dooprint printer for the kiosk and phone orders: the ticket goes through the public self order
 * route, which checks the order before queueing it.
 */
export class DooprintSelfOrderPrinter extends DooprintPrinter {
    setup({ selfOrder }) {
        super.setup(...arguments);
        this.selfOrder = selfOrder;
    }

    sendThroughOdoo(payload) {
        const order = this.selfOrder.currentOrder?.id
            ? this.selfOrder.currentOrder
            : this.selfOrder.models["pos.order"].getAll().findLast((o) => o.id && o.access_token);
        return rpc("/dooprint_pos/self_order/print", {
            access_token: this.selfOrder.access_token,
            printer_id: this.printerId,
            payload,
            order_id: order?.id,
            order_access_token: order?.access_token,
        });
    }
}
