# dooprint for Odoo

<a href="https://apiservicesac.com"><img src="dooprint/static/description/logo-api-service-sac.png" alt="API SERVICE S.A.C." height="48" align="right"></a>

Built and maintained by **[Josue Salazar](https://github.com/Josuesp1620)** ([@Josuesp1620](https://github.com/Josuesp1620)) and **[API SERVICE S.A.C.](https://apiservicesac.com)** · Lima, Perú

Odoo 20 modules for [dooprint](https://github.com/apiservicesac/dooprint), the print service that
runs on a computer next to the printers. With them Odoo prints on USB and network receipt printers,
even when Odoo runs on a remote server and nobody has a browser open.

This is the `20.0` branch. The modules for Odoo 19 live on the `19.0` branch.

| Module | Depends on | What it does |
|---|---|---|
| `dooprint` | `base_setup`, `bus` | Devices, printers, the print job queue and remote commands. Other modules print through it. |
| `dooprint_pos` | `point_of_sale`, `dooprint` | Receipt and preparation printers of the Point of Sale. |
| `dooprint_pos_self_order` | `dooprint_pos`, `pos_self_order` | Kiosk and mobile self orders. Installs itself when both are present. |

## Status on Odoo 20

| Module | Version | Ready to use |
|---|---|---|
| `dooprint` | `20.0.1.0.0` | **Yes.** Migrated, installed and verified on Odoo 20. |
| `dooprint_pos` | `20.0.1.0.0` | **Yes.** |
| `dooprint_pos_self_order` | `20.0.1.0.0` | **Yes.** |

**Upgrading from the 19.0 branch is not a drop-in.** On Odoo 19 the receipt printer was a field of
the point of sale (`pos.config.dooprint_printer_id`) and the delivery mode lived there too. On
Odoo 20 both moved to `pos.printer`, so those settings have to be created again as printers.

## How a job reaches the printer

Each device pairs in one of two modes:

| Mode | When | How |
|---|---|---|
| **Agent** | Odoo is outside the printers network (cloud, VPS) | The device keeps the Odoo bus open. When a job is queued, Odoo wakes it up and the device picks it up right away. No open ports or tunnels. |
| **Local** | Odoo is on the same network | Odoo sends each job straight to the device. |

Jobs are taken with `FOR UPDATE SKIP LOCKED`, so two workers never hand over the same ticket twice.

## Point of Sale

On Odoo 20 every printer of the point of sale is a `pos.printer`, so a dooprint printer is created
in **Point of Sale › Configuration › Printers** with the type **Use a dooprint printer**, and then
picked as a receipt or a preparation printer of the point of sale. The same printer type serves the
Point of Sale and the self order.

Each printer chooses how its tickets travel:

- **Through Odoo**: the POS sends the rendered ticket to Odoo, which queues it for the device. It
  works from any network, also with Odoo in the cloud and the POS on a tablet outside the shop
  network.
- **From the browser**: the POS sends the ticket straight to the device over the local network,
  the same way Odoo talks to an Epson ePOS printer. The browser must be on the device network, and
  from an HTTPS page it must allow Local Network Access (Chromium based browsers).

The cash drawer is Odoo's own **Link Cashdrawer** on the receipt printer: dooprint printers open it
the same way Epson ePOS printers do, so no extra setting is needed.

The kiosk prints its receipts and the order tickets itself. On Odoo 20 orders placed from a phone
do not print from the phone: the Point of Sale prints them. The public self order route only prints
for an existing order of that point of sale.

## Printing any report

Any Odoo report can print on a dooprint printer. In **dooprint › Configuration › Report Printers**,
create a printer with the type **Dooprint**, pick the dooprint printer and link the reports. When
someone prints one of them, Odoo asks for the printer, renders the report and queues it for the
device, so it prints from any network. Receipt printers take PDF reports, printed as an image;
label printers take ZPL reports.

This relies on the report printers that Odoo added in version 20, so it only exists from Odoo 20
on. The `19.0` branch does not have it.

## Using it from another module

Queue a print job on a printer. The payload is an ePOS-Print request, or ZPL for label printers:

```python
job = self.env['dooprint.job']._enqueue(printer, payload, origin=record)
```

`dooprint.render` turns a QWeb template into an ePOS-Print raster image:

```python
payload = self.env['dooprint.render'].epos_from_template('my_module.ticket_template', values)
```

When `origin` defines `_dooprint_job_done(job)`, it is called every time the job changes state.

A device can also make HTTP requests on its own network, to reach equipment Odoo cannot see:

```python
command = device._http_request('http://192.168.1.20/api/status', method='GET', origin=record)
```

The answer lands in `command.result` as JSON with `status` and `body`, and `origin` may define
`_dooprint_command_done(command)` to receive it.

## Device status

A device in agent mode sends a heartbeat every 30 seconds and is shown offline after 2 minutes
without one. Opening its form pings it: an agent answers through the bus within a second, and for
a local device Odoo checks its web interface.

## Installation

Add this repository to the addons path and install `dooprint`. Then open **dooprint › Devices**, click **Connect** and paste the pairing token into the
device web interface.

## Translations

Every module ships a `.pot` template and Spanish (`es.po`). To refresh a template:

```bash
odoo i18n export -c odoo.conf -d <database> -o dooprint_pos/i18n/dooprint_pos.pot dooprint_pos
```

## Who builds it

**[Josue Salazar](https://github.com/Josuesp1620)** ([@Josuesp1620](https://github.com/Josuesp1620)) — author and maintainer.

[API SERVICE S.A.C.](https://apiservicesac.com) — Odoo development, implementation and
infrastructure. Lima, Perú.

- Dooprint: [dooprint.apiservicesac.com](https://dooprint.apiservicesac.com)
- The print service: [github.com/apiservicesac/dooprint](https://github.com/apiservicesac/dooprint)
- Write to us: info@apiservicesac.com

## License

AGPL-3. See [LICENSE](LICENSE). Copyright API SERVICE S.A.C.
