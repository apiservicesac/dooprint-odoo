import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Prints a report on a dooprint printer of Odoo's report printers. Instead of sending the report
 * to an IP from this browser, Odoo renders it and queues it for the device, so it prints from any
 * network.
 */
async function dooprintPrint(printer, _duplex, jobs, { orm, notification }) {
    const job = jobs.find((job) => job.type === "dooprint");
    if (!job) {
        return;
    }
    await orm.call("printer.printer", "dooprint_print_report", [
        [printer.id],
        job.report_id,
        job.docids,
        job.data,
    ]);
    notification.add(_t("Sent to %s.", printer.name), { type: "success" });
}

registry.category("printer.type.handlers").add("dooprint", dooprintPrint);
