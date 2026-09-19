import { Component, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { getLNATargetAddressSpace, initLNA } from "@point_of_sale/app/utils/init_lna";

/**
 * Test button of the printer form. It prints the way the POS will: through Odoo, or from this
 * browser straight to the device when the delivery is "From the browser".
 */
export class DooprintPosTest extends Component {
    static template = "dooprint_pos.TestButton";
    props = useProps(standardWidgetProps);

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    async onClick() {
        const data = this.props.record.data;
        const printerId = data.dooprint_printer_id?.id;
        if (!printerId) {
            return this.notify(false, _t("Select a printer first."));
        }
        if (data.dooprint_delivery !== "browser") {
            const result = await this.orm.call("pos.config", "dooprint_test_print", [printerId]);
            return this.notify(result.result, result.message);
        }
        const { url, payload } = await this.orm.call("pos.config", "dooprint_test_info", [printerId]);
        if (!url) {
            return this.notify(false, _t("The Dooprint device has not reported its address."));
        }
        // Same Local Network Access check as Odoo's Epson test button.
        let lnaStatus = "pending";
        await initLNA(this.notification, (status) => (lnaStatus = status));
        if (lnaStatus === "danger") {
            return;
        }
        const address = `${url}/cgi-bin/epos/service.cgi`;
        try {
            const response = await fetch(address, {
                method: "POST",
                body: payload,
                signal: AbortSignal.timeout(15000),
                targetAddressSpace: getLNATargetAddressSpace(address),
            });
            const xml = new DOMParser().parseFromString(await response.text(), "application/xml");
            const answer = xml.querySelector("response");
            if (answer?.getAttribute("success") === "true") {
                return this.notify(true, _t("Test page printed from this browser."));
            }
            return this.notify(false, _t("The device answered with error %s.", answer?.getAttribute("code") || "?"));
        } catch {
            return this.notify(
                false,
                _t(
                    "This browser cannot reach the Dooprint device at %s. Check that it is on the same network and that Local Network Access is allowed.",
                    url
                )
            );
        }
    }

    notify(success, message) {
        this.notification.add(message, { type: success ? "success" : "danger" });
    }
}

registry.category("view_widgets").add("dooprint_pos_test", { component: DooprintPosTest });
