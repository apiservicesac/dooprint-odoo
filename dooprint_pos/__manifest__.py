{
    'name': "Dooprint for Point of Sale",
    'summary': "Print POS receipts and order tickets on dooprint printers, with or without the browser",

    'description': """
Use the printers of a dooprint device in the Point of Sale: the receipt printer, the cash drawer
and the preparation printers of the kitchen or the bar.

Each point of sale chooses how its tickets reach the printer:

- Through Odoo: the POS sends the ticket to Odoo, which queues it for the device. It works from
  any network, also when Odoo runs on a remote server, because the device picks up its jobs.
- From the browser: the POS sends the ticket straight to the device over the local network.
  The browser must be on the same network and allow Local Network Access.
    """,

    'author': "API SERVICE S.A.C",
    'category': 'Sales/Point of Sale',
    'version': '1.0.0',

    'depends': [
        'point_of_sale',
        'dooprint',
    ],

    'data': [
        'views/pos_printer_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dooprint_pos/static/src/backend/**/*',
        ],
        'point_of_sale._assets_pos': [
            'dooprint_pos/static/src/app/**/*',
        ],
    },
    'installable': True,
    'license': 'OPL-1',
}
