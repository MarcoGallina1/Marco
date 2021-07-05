# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pytz
from odoo import models, fields
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from l10n_ar_api.afip_webservices import wsaa
from odoo.exceptions import ValidationError
from odoo import SUPERUSER_ID


class WsaaToken(models.Model):

    _name = 'wsaa.token'
    _description = 'Token wsaa'

    name = fields.Char('Servicio', required=True)
    expiration_time = fields.Datetime('Fecha de expiracion')
    token = fields.Text('Token', readonly=True)
    sign = fields.Text('Sign', readonly=True)
    wsaa_configuration_id = fields.Many2one(
        'wsaa.configuration',
        'Configuracion',
        required=True,
        check_company=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        related='wsaa_configuration_id.company_id',
        store=True,
        readonly=True,
        related_sudo=False
    )

    def get_access_token(self):
        """
        Crea el objeto de ticket de acceso para utilizar en el los webervices
        :return: instancia de AcessToken
        """
        self.ensure_one()

        self.action_renew()
        access_token = wsaa.tokens.AccessToken()
        access_token.sign = self.sign
        access_token.token = self.token

        return access_token

    def action_renew(self, context=None, delta_time_for_expiration=10):
        """ Renueva o crea el ticket de acceso si esta vencido o no creado """

        for token in self:

            renew = True
            if token.expiration_time:

                # Si faltan mas de X minutos para que el ticket expire no se lo renueva
                if datetime.now() + timedelta(minutes=delta_time_for_expiration) < token.expiration_time:
                    renew = False

            if renew:
                token._renew_ticket()

    def _renew_ticket(self):
        """ Renueva o crea el ticket de acceso si esta vencido o no creado """

        if not (self.wsaa_configuration_id.certificate and self.wsaa_configuration_id.private_key):
            raise ValidationError("Falta configurar certificado o clave privada")

        # Traemos el timezone
        user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) if user.partner_id.tz else pytz.utc

        # Creamos el token nuevo para el servicio especificado y lo firmamos con la clave y certificado
        token = wsaa.tokens.AccessRequerimentToken(self.name, tz)
        homologation = False if self.wsaa_configuration_id.type == 'production' else True
        try:
            signed_tra = token.sign_tra(self.wsaa_configuration_id.private_key, self.wsaa_configuration_id.certificate)
            # Hacemos el logeo y obtenemos sus datos
            login_fault = wsaa.wsaa.Wsaa(homologation).login(signed_tra)
        except Exception as e:
            raise ValidationError(e.args)

        access_token = wsaa.tokens.AccessToken()
        access_token.create_token_from_login(login_fault)

        # Pegamos los datos del acceso al ticket
        self.sudo().write({
            'expiration_time': isoparse(access_token.expiration_time).replace(tzinfo=None),
            'token': access_token.token,
            'sign': access_token.sign,
        })

    _sql_constraints = [('unique_token_service', 'unique(name, company_id)', 'Ya existe un token para este servicio')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
