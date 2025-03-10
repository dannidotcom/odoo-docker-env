from odoo.http import request
import json
import logging

class Data:
    """Modèle pour encapsuler les données et les convertir en JSON."""
    def __init__(self, **kwargs):
        # Store all keyword arguments as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convert the object to a dictionary."""
        # Return all attributes as a dictionary
        return self.__dict__

    def to_json(self):
        """Convert the object to JSON."""
        return json.dumps(self.to_dict())

class ShipperService:
    """Service pour créer un shipper."""
    @staticmethod
    def create_shipper(data):
        return Data(
            name=data.get('name'),
            destinatory=data.get('destinatory'),
            streetnumber=data.get('streetnumber'),
            street=data.get('street'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            city=data.get('city'),
            tel=data.get('tel'),
            email=data.get('email'),
        )


class RecipientService:
    """Service pour créer un recipient."""
    @staticmethod
    def create_recipient(data):
        return Data(
            name=data.get('name'),
            destinatory=data.get('destinatory'),
            streetnumber=data.get('streetnumber'),
            street=data.get('street'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            city=data.get('city'),
            tel=data.get('tel'),
            email=data.get('email'),
        )


class ParcelService:
    """Service pour créer un parcel."""
    @staticmethod
    def create_parcel(data):
        return Data(
            shipper_reference=data.get('shipper_reference'),
            comment=data.get('comment'),
            ispallet=data.get('ispallet', False),
            weight=data.get('weight'),
            against_reimbursement=data.get('against_reimbursement'),
            value=data.get('value'),
            delivery_type=data.get('delivery_type', 'normal'),
        )


class DeliveryOrderService:
    """Service pour créer une commande de livraison."""
    @staticmethod
    def create_order(shipper_data, recipient_data, parcels_data, addswap=False, printtype='zpl'):
        # Créer le shipper
        shipper = request.env['easy.delivery.shipper'].sudo().create(ShipperService.create_shipper(shipper_data).to_json())
        logging.info("Order Data: %s", shipper_data)
        # Créer le recipient
        recipient = request.env['easy.delivery.recipient'].sudo().create(RecipientService.create_recipient(recipient_data).to_json())

        # Créer la commande
        order = request.env['easy.delivery.order'].sudo().create({
            'shipper_id': shipper.id,
            'recipient_id': recipient.id,
            'addswap': addswap,
            'printtype': printtype,
        })

        # Créer les colis
        for parcel_data in parcels_data:
            parcel_vals = ParcelService.create_parcel(parcel_data).to_json()
            parcel_vals['order_id'] = order.id
            request.env['easy.delivery.parcel'].create(parcel_vals)

        # Retourner les données de la commande
        return Data(
            shipper=shipper,
            recipient=recipient,
            parcels=[ParcelService.create_parcel(parcel_data).to_json() for parcel_data in parcels_data],
            addswap=addswap,
            printtype=printtype,
        )
        