# 📦 Documentation - Intégration de l'API Easy Delivery dans Odoo

## 1 Introduction
Cette documentation explique l'intégration de l'API du transporteur **Easy Delivery** dans **Odoo v17**. L'objectif est de permettre l'envoi des informations de livraison à Easy Delivery et de récupérer l'étiquette d'expédition au format **ZPL**.

---

## 3 API du Transporteur

### 🔑 **Authentification**
L'API utilise une authentification par **token**. Chaque requête doit inclure l'entête suivante :
```json
{
  "Authorization": "Bearer <API_KEY>",
  "Content-Type": "application/json"
}

## Création de livraison

### Endpoint
**POST** `{BASE_URL}/api/order`

### Corps de la requête (JSON)
```json
{
    "data": {
        "recipient": {
            "name": "Probst",
            "destinatory": "Jane Doe",
            "streetnumber": "30",
            "street": "rue des Joncs",
            "country": "LU",
            "postal_code": "L-1818",
            "city": "Howald",
            "tel": "+3524848301",
            "email": "test@probst.lu"
        },
        "shipper": {
            "name": "Cap logistic",
            "destinatory": "John Doe",
            "streetnumber": "20",
            "street": "rue Marc Seguin",
            "country": "FR",
            "postal_code": "57160",
            "city": "ENNERY",
            "tel": "+33387709140",
            "email": "contact@cap-logistic.com"
        },
        "parcels": [
            {
                "shipper_reference": "B90000001",
                "weight": 1.5,
                "delivery_type": "normal"
            },
            {
                "shipper_reference": "B90000002",
                "weight": 2.0,
                "delivery_type": "fast"
            }
        ],
        "addswap": false,
        "printtype": "zpl"
    }
}
```
