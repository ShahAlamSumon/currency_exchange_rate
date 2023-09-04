import logging
import requests
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CurrencyExchangeRateWizard(models.TransientModel):
    _name = 'currency.exchange.rate.wizard'
    _rec_name = 'name'

    name = fields.Char(string='Name', default="Exchange Rate")
    amount_in = fields.Float(string='Amount', default=1, digits=(8, 4))
    amount_converted = fields.Float(string='Converted Amount', digits=(8, 4))
    current_rate = fields.Float(string='Current Rate', digits=(8, 4))
    currency_from = fields.Many2one('res.currency', string='From Currency', required=True)
    currency_to = fields.Many2one('res.currency', string='To Currency', required=True)
    show_res = fields.Boolean(default=False)

    def action_convert(self):
        if not self.currency_to or not self.currency_from:
            raise UserError(_("Internal user error. Please refresh or contact to admin"))
        url = 'https://api.exchangerate-api.com/v4/latest/{}'.format(self.currency_from.name)
        try:
            data = requests.get(url).json()
        except Exception as msg:
            raise UserError(_("Server Error: \n %s \n Please try again after sometime.", msg))
        rate = data['rates'][self.currency_to.name]
        self.current_rate = round(rate, 4)
        self.amount_converted = round(rate * self.amount_in, 4)
        self.show_res = True
        return True

    def action_switch(self):
        currency_from = self.currency_from
        currency_to = self.currency_to
        self.currency_from = currency_to
        self.currency_to = currency_from
        self.action_convert()
        return True

    def action_refresh(self):
        return {
            'name': 'Exchange Currency',
            'view_mode': 'form',
            'res_model': 'currency.exchange.rate.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'tag': 'reload'
        }

