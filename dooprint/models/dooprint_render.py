import base64

from io import BytesIO

from PIL import Image, ImageOps

from odoo import api, models

# 576 dots is the printable width of 80 mm paper.
PAPER_WIDTH = 576
EPOS_TEMPLATE = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">
            <image width="%s" height="%s" align="center">%s</image>
            <cut type="feed" />
        </epos-print>
    </s:Body>
</s:Envelope>"""


class DooprintRender(models.AbstractModel):
    """Turns ticket HTML into an ePOS-Print request.

    The ticket is printed as an image: it looks the same on any printer, with accents and any
    font size, regardless of the printer code page.
    """
    _name = 'dooprint.render'
    _description = 'dooprint ePOS Renderer'

    @api.model
    def epos_from_html(self, html, width=PAPER_WIDTH):
        image = self.env['ir.actions.report']._run_image_engine('wkhtmltopdf', [html], width, 0)[0]
        img = Image.open(BytesIO(image)).convert('L')
        height = int(img.height * width / img.width)
        img = (
            ImageOps.invert(img)
            .resize((width, height), Image.Resampling.LANCZOS)
            .convert('1', dither=Image.Dither.FLOYDSTEINBERG)
        )
        return EPOS_TEMPLATE % (width, height, base64.b64encode(img.tobytes()).decode())

    @api.model
    def epos_from_template(self, template, values, width=PAPER_WIDTH):
        return self.epos_from_html(self.env['ir.qweb']._render(template, values), width)
