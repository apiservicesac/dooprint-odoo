import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
import { getLNATargetAddressSpace } from "@point_of_sale/app/utils/init_lna";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    /**
     * The "Local Network Access" button of the menu reaches the Dooprint device, so the browser
     * asks for the permission if it has not yet, without printing anything.
     * @override
     */
    async openLnaPopup() {
        const url = this.pos.usesDooprintFromBrowser() && this.pos.dooprintDeviceUrl();
        if (!url) {
            return super.openLnaPopup(...arguments);
        }
        let reachable = true;
        try {
            await fetch(url.replace(/\/p\/[^/]+$/, "/"), {
                signal: AbortSignal.timeout(5000),
                targetAddressSpace: getLNATargetAddressSpace(url),
            });
        } catch {
            reachable = false;
        }
        this.dialog.add(AlertDialog, {
            title: _t("LNA Permission status"),
            body: reachable
                ? this.pos.lnaState.message
                : _t(
                      "%s\nThe Dooprint device at %s cannot be reached from this browser.",
                      this.pos.lnaState.message,
                      url
                  ),
        });
    },
});
