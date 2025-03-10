from odoo import models, fields

class EasyDeliveryConfig(models.Model):
    _name = 'easy.delivery.config'
    _description = 'Configuration for Easy Delivery API'

    name = fields.Char(string='Name', required=True)
    api_url = fields.Char(string='API URL', required=True)
    api_token = fields.Char(string='API Token', required=True)