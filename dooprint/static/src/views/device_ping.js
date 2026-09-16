import { Component, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

// Time the device gets to answer the ping before the form reads its status again.
const ANSWER_DELAY = 2500;

/**
 * Pings the device when its form opens and reloads the record shortly after, so the status is
 * current instead of depending on the last heartbeat. It renders nothing.
 */
export class DooprintDevicePing extends Component {
    static template = "dooprint.DevicePing";
    static props = { ...standardWidgetProps };

    setup() {
        this.orm = useService("orm");
        onMounted(() => this.ping());
        onWillUnmount(() => clearTimeout(this.timeout));
    }

    async ping() {
        const { record } = this.props;
        if (!record.resId || record.data.state === "revoked") {
            return;
        }
        await this.orm.call("dooprint.device", "action_ping", [record.resId]);
        this.timeout = setTimeout(() => {
            if (!record.dirty) {
                record.load();
            }
        }, ANSWER_DELAY);
    }
}

registry.category("view_widgets").add("dooprint_device_ping", { component: DooprintDevicePing });
