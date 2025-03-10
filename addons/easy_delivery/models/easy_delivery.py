from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class BaseContact(models.AbstractModel):
    _name = 'easy.delivery'
    _description = 'Easy delivery base contact'

    name = fields.Char(string='Nom', required=True)
    destinatory = fields.Char(string='À l\'attention de')
    streetnumber = fields.Char(string='Numéro de rue', size=20)
    street = fields.Char(string='Adresse détaillée', required=True)
    country = fields.Char(string='Code du pays', size=2, required=True)
    postal_code = fields.Char(string='Code postal', required=True)
    city = fields.Char(string='Ville', required=True)
    tel = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')

    @api.constrains('email')
    def _check_email(self):
        """
        Valider le format de l'adresse e-mail.
        """
        for record in self:
            if record.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError("L'adresse e-mail du partenaire n'est pas valide.")


class Shipper(models.Model):
    _name = 'easy.delivery.shipper'
    _description = 'Shipper Information'
    _inherit = 'easy.delivery'


class Recipient(models.Model):
    _name = 'easy.delivery.recipient'
    _description = 'Recipient Information'
    _inherit = 'easy.delivery'

class Parcel(models.Model):
    _name = 'easy.delivery.parcel'
    _description = 'Informations sur les colis de l\'expédition'

    shipper_reference = fields.Char(string='Référence de l\'expéditeur')
    comment = fields.Char(string='Commentaire sur la livraison')
    ispallet = fields.Boolean(string='Est une palette', default=False)
    weight = fields.Float(string='Poids (kg)', required=True, digits=(10, 3))
    against_reimbursement = fields.Float(string='Contre remboursement (€)', digits=(10, 2))
    value = fields.Float(string='Valeur du colis (€)', digits=(10, 2), help="Valeur du colis en euros pour l'assurance.")
    delivery_type = fields.Selection(
        string='Type de livraison',
        selection=[('normal', 'Normal'), ('fast', 'Rapide'), ('date', 'Date spécifique')],
        default='normal',
        help="Type de livraison demandé. 'Normal' par défaut, 'Rapide' pour une livraison express, ou une date spécifique au format YYYY-MM-DD."
    )
    order_id = fields.Many2one('easy.delivery.order', string="Order")

    @api.constrains('value')
    def _check_value_format(self):
        for record in self:
            if record.value:
                # Convertir la valeur en chaîne pour vérifier le format
                value_str = str(record.value)
                # Vérifier que la chaîne contient uniquement des chiffres et un point
                if not all(char.isdigit() or char == '.' for char in value_str):
                    raise ValidationError("La valeur du colis doit être un nombre décimal avec un point comme séparateur (par exemple 123.45).")


class DeliveryOrder(models.Model):
    _name = 'easy.delivery.order'
    _description = 'Easy delivery order'

    shipper_id = fields.Many2one('easy.delivery.shipper', string='Shipper', required=True)
    recipient_id = fields.Many2one('easy.delivery.recipient', string='Recipient', required=True)
    parcels_id = fields.One2many('easy.delivery.parcel','order_id', string='Parcels')
    
    addswap = fields.Boolean(string='Ajouter un colis de swap', default=False, help="Si activé, ajoute un colis de swap.")
    printtype = fields.Selection(
        string='Type de format d\'étiquette',
        selection=[
            ('zpl', 'ZPL'),
            ('pdf_a4', 'PDF A4 (jusqu\'à 2 étiquettes par page)'),
            ('pdf_a6', 'PDF A6'),
            ('pdf_a6_combine', 'PDF A4 avec étiquettes A6 (jusqu\'à 4 étiquettes par page)')
        ],
        default='zpl',
        help="Type de format de l’étiquette. Par défaut, l’étiquette sera au format ZPL."
    )
