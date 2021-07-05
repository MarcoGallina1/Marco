import json

from werkzeug import urls
from lxml import html
from collections import OrderedDict

from odoo import models, tools
from odoo.http import request
from odoo.modules.module import get_resource_path


class WinERPThemeQWeb(models.AbstractModel):
    _name = 'ir.qweb'
    _inherit = 'ir.qweb'

    @tools.ormcache_context('xmlid', 'options.get("lang", "en_US")', keys=("website_id",))
    def _get_asset_content(self, xmlid, options):
        options = dict(options,
                       inherit_branding=False, inherit_branding_auto=False,
                       edit_translations=False, translatable=False,
                       rendering_bundle=True)

        options['website_id'] = self.env.context.get('website_id')
        IrQweb = self.env['ir.qweb'].with_context(options)

        def can_aggregate(url):
            return not urls.url_parse(url).scheme and not urls.url_parse(url).netloc and not url.startswith('/web/content')

        # TODO: This helper can be used by any template that wants to embedd the backend.
        #       It is currently necessary because the ir.ui.view bundle inheritance does not
        #       match the module dependency graph.
        def get_modules_order():
            if request:
                from odoo.addons.web.controllers.main import module_boot
                return json.dumps(module_boot())
            return '[]'

        def get_user_theme():
            user_context = request.session.get_context() if request.session.uid else {}
            return user_context.get('theme', 'blue')
        template = IrQweb.render(
            xmlid, {"get_modules_order": get_modules_order, 'get_user_theme': get_user_theme})

        files = []
        remains = []
        for el in html.fragments_fromstring(template):
            if isinstance(el, html.HtmlElement):
                href = el.get('href', '')
                src = el.get('src', '')
                atype = el.get('type')
                media = el.get('media')

                if can_aggregate(href) and (el.tag == 'style' or (el.tag == 'link' and el.get('rel') == 'stylesheet')):
                    if href.endswith('.sass'):
                        atype = 'text/sass'
                    elif href.endswith('.scss'):
                        atype = 'text/scss'
                    elif href.endswith('.less'):
                        atype = 'text/less'
                    if atype not in ('text/less', 'text/scss', 'text/sass'):
                        atype = 'text/css'
                    path = [segment for segment in href.split('/') if segment]
                    filename = get_resource_path(*path) if path else None
                    files.append(
                        {'atype': atype, 'url': href, 'filename': filename, 'content': el.text, 'media': media})
                elif can_aggregate(src) and el.tag == 'script':
                    atype = 'text/javascript'
                    path = [segment for segment in src.split('/') if segment]
                    filename = get_resource_path(*path) if path else None
                    files.append(
                        {'atype': atype, 'url': src, 'filename': filename, 'content': el.text, 'media': media})
                else:
                    remains.append((el.tag, OrderedDict(el.attrib), el.text))
            else:
                # the other cases are ignored
                pass

        return (files, remains)
