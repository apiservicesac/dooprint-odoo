{
    'name': "Dooprint",
    'summary': "Print devices for Odoo: pairing, printers and a job queue",

    'description': """
Manage the computers that print for Odoo through dooprint, and their printers.

A device pairs with a one-time token: it registers itself and reports the USB and
network printers it finds, so nobody types identifiers by hand.

Depending on where Odoo runs, a job travels in one of two ways:

- Local: Odoo reaches the device over the network and sends it the ePOS request.
- Agent: the device, inside the customer network, picks up its jobs and reports the result.
  Odoo wakes it up through the bus, so it prints right away without open ports or tunnels.

Any report can print on a dooprint printer: add it in Settings › Printers with the type
Dooprint and link it to the report. Odoo renders the report and queues it for the device, so it
prints from any network. Other modules queue their own jobs here and get the result back.
    """,

    'author': "API SERVICE S.A.C",
    'website': "https://dooprint.apiservicesac.com",
    'support': "info@apiservicesac.com",
    'images': ['static/description/banner.png'],
    'category': 'Productivity',
    'version': '20.0.1.0.0',

    'depends': [
        'base_setup',
        'bus',
        'printer',
    ],

    'data': [
        'security/dooprint_security.xml',
        'security/ir.access.csv',
        'data/ir_cron_data.xml',
        'wizard/dooprint_pairing_views.xml',
        'views/dooprint_printer_views.xml',
        'views/dooprint_job_views.xml',
        'views/dooprint_command_views.xml',
        'views/dooprint_device_views.xml',
        'views/printer_views.xml',
        'views/res_config_settings_views.xml',
        'views/dooprint_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dooprint/static/src/views/**/*',
            'dooprint/static/src/printer/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'AGPL-3',
}
