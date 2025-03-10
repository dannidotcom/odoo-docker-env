from odoo import http
from odoo.http import request, Response
import json
from ..services.delivery_service import DeliveryOrderService, Data
import logging
from odoo.exceptions import AccessDenied
from ..utils.decorator import auth_required 


class AuthController(http.Controller):
    
    @http.route('/api/token', type='http', auth="none", methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self):
        try:
            # Récupérer les données de la requête
            byte_string = request.httprequest.data
            data = json.loads(byte_string.decode('utf-8'))

            # Valider les données
            if not data.get("login") or not data.get("password"):
                return json.dumps({
                    "error": "Login and password are required",
                    "code": 400
                })

            # Authentifier l'utilisateur
            username = data['login']
            password = data['password']
            user_id = request.session.authenticate(request.db, username, password)

            if not user_id:
                return json.dumps({
                    "error": "Invalid username or password",
                    "code": 401
                })

            # Générer un token sécurisé (exemple avec JWT)
            env = request.env(user=request.env.user.browse(user_id))
            env['res.users.apikeys.description'].check_access_make_key()
            token = env['res.users.apikeys']._generate("API Key", username)

            # Retourner la réponse
            return json.dumps({
                "data": {
                    "user_id": user_id,
                    "login": username,
                    "token": token  # Ne pas inclure le mot de passe dans la réponse
                },
                "responsedetail": {
                    "messages": "User validated",
                    "messagestype": 1,
                    "code": 200
                }
            })

        except json.JSONDecodeError:
            return json.dumps({
                "error": "Invalid JSON input",
                "code": 400
            })
        except AccessDenied:
            return json.dumps({
                "error": "Access denied",
                "code": 403
            })
        except Exception as e:
            return json.dumps({
                "status":"failure",
                "error": str(e),
                "code": 500
            })
    
class DeliveryOrderController(http.Controller):

    @http.route('/api/order', type='json', auth='public', methods=['POST'], csrf=False)
    @auth_required
    def create_delivery_order(self, **post):
        try:
            # Récupérer les données JSON de la requête
            data = json.loads(request.httprequest.data)
            
            
            # Valider les données
            if not data.get('data'):
                return Response(json.dumps({"error": "Missing 'data' in request"}), status=400)

            shipper_data = data['data'].get('shipper', {})
            recipient_data = data['data'].get('recipient', {})
            parcels_data = data['data'].get('parcels', [])
            addswap = data['data'].get('addswap', False)
            printtype = data['data'].get('printtype', 'zpl')

            # Créer la commande en utilisant le service
            order_data = DeliveryOrderService.create_order(shipper_data, recipient_data, parcels_data, addswap, printtype)
            if not order_data:
                logging.info("Incoming request input data: %s", order_data)
            # Retourner la réponse JSON
            return Response(json.dumps({"data": order_data.to_dict()}), status=200)

        except Exception as e:
            # Gérer les erreurs
            error_data = Data(
                success="Failure",
                error=str(e),
                message="An error occurred while creating the delivery order",
            )
            return Response(json.dumps(error_data.to_json()), status=500)
    
    
    @http.route('/api/delivery_order', type='http', auth='public', methods=['GET'], csrf=False)
    @auth_required
    def get_delivery_order(self, **kwargs):
        try:
            # Récupérer les paramètres de la requête GET
            order_id = kwargs.get('order_id')  

            if not order_id:
                return Response(json.dumps({"error": "Missing 'order_id' parameter"}), status=400)

            # Rechercher la commande dans la base de données
            order = request.env['easy.delivery.order'].sudo().browse(int(order_id))
            if not order.exists():
                return Response(json.dumps({"error": "Order not found"}), status=404)

            # Préparer les données à retourner
            order_data = {
                "id": order.id,
                "shipper": {
                    "name": order.shipper_id.name,
                    "street": order.shipper_id.street,
                    "city": order.shipper_id.city,
                    "country": order.shipper_id.country,
                    "postal_code": order.shipper_id.postal_code,
                    "tel": order.shipper_id.tel,
                    "email": order.shipper_id.email,
                },
                "recipient": {
                    "name": order.recipient_id.name,
                    "street": order.recipient_id.street,
                    "city": order.recipient_id.city,
                    "country": order.recipient_id.country,
                    "postal_code": order.recipient_id.postal_code,
                    "tel": order.recipient_id.tel,
                    "email": order.recipient_id.email,
                },
                "parcels": [
                    {
                        "shipper_reference": parcel.shipper_reference,
                        "weight": parcel.weight,
                        "delivery_type": parcel.delivery_type,
                    }
                    for parcel in order.parcels_id
                ],
            }

            # Retourner les données en JSON
            return Response(json.dumps({"data": order_data}), status=200)

        except Exception as e:
            # Gérer les erreurs
            error_data = {
                "success": "Failure",
                "error": str(e),
                "message": "An error occurred while fetching the delivery order",
            }
            return Response(json.dumps(error_data), status=500)