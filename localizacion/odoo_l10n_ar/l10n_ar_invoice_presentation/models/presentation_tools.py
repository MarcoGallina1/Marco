# coding: utf-8
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################


class PresentationTools:
    def __init__(self):
        pass

    @staticmethod
    def format_date(d):
        # type: (str) -> str
        """
        Formatea la fecha para su presentacion en ventas compras.
        :param d: La fecha a formatear.
        :type d: str
        :return: La fecha formateada.
        :rtype: str
        """
        if not isinstance(d, str):
            d = str(d)
        return d.replace("-", "")

    @staticmethod
    def get_currency_rate_from_move(invoice):
        """
        Obtiene la currency de la factura, a partir de las lineas del asiento.
        :param invoice: record, factura
        :return: float, currency. ej: 15.32
        """

        # Traemos todas las lineas del asiento que tengan esa cuenta
        move_line = invoice.line_ids.filtered(lambda x: x.account_id.user_type_id.type in ('receivable', 'payable'))[0]

        # Traemos el monto de la linea, si es de debito o credito
        amount = move_line.credit or move_line.debit
        amount_currency = abs(move_line.amount_currency)
        # El rate sera el monto dividido la currency si es distinto de cero, sino se divide por si mismo
        currency_rate = float(amount) / float(amount_currency or amount)

        return currency_rate

    @staticmethod
    def format_amount(amount, dp=2):
        # type: (float, int) -> str
        """
        Formatea el numero con la cantidad de decimales que se le pase, o dos decimales por defecto.
        :param amount: El numero a formatear.
        :type amount: float
        :param dp: La precision decimal, a.k.a. la cantidad de decimales.
        :type dp: int
        :return: El numero formateado a string.
        :rtype: str
        """
        amount = str("{0:.{1}f}".format(amount, dp))
        amount = amount.replace(".", "").replace(",", "")
        return amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
