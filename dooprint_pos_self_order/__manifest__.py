{
    'name': "Dooprint POS Self Order",
    'summary': "Print kiosk and mobile self orders on dooprint printers",

    'description': """
Bridge between dooprint for Point of Sale and Self Order.

The kiosk prints its receipts and the order tickets for the kitchen on dooprint printers, with the
delivery chosen on the point of sale. Orders placed from a phone always go through Odoo: the
customer is not on the printer network.
    """,

    'author': "Josue Salazar, API SERVICE S.A.C",
    'maintainer': "Josue Salazar, API SERVICE S.A.C",
    'website': "https://dooprint.apiservicesac.com",
    'support': "info@apiservicesac.com",
    'images': ['static/description/banner.png'],
    'category': 'Sales/Point of Sale',
    'version': '20.0.1.0.0',

    'depends': [
        'dooprint_pos',
        'pos_self_order',
    ],
    'auto_install': True,

    'assets': {
        'pos_self_order.assets': [
            'dooprint_pos/static/src/app/utils/printer/dooprint_printer.js',
            'dooprint_pos/static/src/app/plugins/pos_ticket_printer_plugin.js',
            'dooprint_pos_self_order/static/src/app/**/*',
        ],
    },
    'installable': True,
    'license': 'AGPL-3',
}
