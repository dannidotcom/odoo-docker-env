from odoo import http
from odoo.http import request
from functools import wraps
import json
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Récupérer le token depuis l'en-tête Authorization
        if 'Authorization' in request.httprequest.headers:
            auth_header = request.httprequest.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return json.dumps({
                "error": "Token is missing",
                "responsecode": 401
            })

        env = request.env()
        user = env['res.users.apikeys']._check_credentials(scope='user', key=token)
        if not user:
            return json.dumps({
                "error": "Invalid token",
                "responsecode": 401
            })

        request.user = user
        return f(*args, **kwargs)

    return decorated