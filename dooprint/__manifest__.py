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

Other modules queue their jobs here and get the result back; this module prints nothing
on its own.
    """,

    'author': "API SERVICE S.A.C",
    'website': "https://dooprint.apiservicesac.com",
    'support': "info@apiservicesac.com",
    'images': ['static/description/banner.png'],
    'category': 'Productivity',
    'version': '18.0.1.0.0',

    'depends': [
        'base_setup',
        'bus',
    ],

    'data': [
        'security/dooprint_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'wizard/dooprint_pairing_views.xml',
        'views/dooprint_printer_views.xml',
        'views/dooprint_job_views.xml',
        'views/dooprint_command_views.xml',
        'views/dooprint_device_views.xml',
        'views/res_config_settings_views.xml',
        'views/dooprint_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dooprint/static/src/views/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'AGPL-3',
}
