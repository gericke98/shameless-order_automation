import requests
import re
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
shop_url = os.getenv('SHOPIFY_SHOP_URL')
token = os.getenv('SHOPIFY_TOKEN')
# Defino un diccionario para los cambios de nombres --> Transformo el nombre de la web en el nombre del almacén
replacementsName = {
    'WITHOUT SHAME LILAC CREWNECK': '0:LILA',
    'WITHOUT SHAME ORANGE CREWNECK': '1:NARANJA',
    'STARBOY SWEATSHIRT': '2:NEGRO',
    'WITHOUT SHAME SAPPHIRE SWEATSHIRT': '3:MARINO',
    'TWO SIDES ZIPPED HOODIE': '4:GRIS',
    'RIO CREWNECK': '5:AMARILLO',
    'WITHOUT SHAME CREWNECK': '6:MORADO',
    'TOO LATE LONGSLEEVE TEE': '7:BLANCO',
    'BLUE KABUKICHO CREWNECK': '8:AZUL',
    'HOTTER THAN AUGUST ORGANIC TEE': '9:HOTTER', # Escribir al chaval que pidio una cami negra (Pablo Zalbidea)
    'PINK SHIBUYA CREWNECK': '10:ROSA',
    'WORLD TOUR LONGSLEEVE TEE': '11:BLANCO',
    'CIAO AMORE TEE': '12:BLANCO',
    'VERMOUTH ORGANIC TEE':'13:OLIVES',
    'WITHOUT SHAME PURPLE ORGANIC TEE': '14:PEGATINA VERDE',
    'WITHOUT SHAME ORANGE ORGANIC TEE': '15:PEGATINA NARANJA',
    'WITHOUT SHAME BLUE ORGANIC TEE': '16:PEGATINA AZUL',
    'MENTALITY ORGANIC TEE':'17:PEGATINA ROJA',
}

# Defino un diccionario para los cambios de talla
replacementsSize = {
    'SMALL': 'S',
    'MEDIUM': 'M',
    'LARGE': 'L',
    'X-LARGE': 'XL',
    'XLARGE': 'XL',
    'EXTRA LARGE': 'XL'
}
def create_session():
    s = requests.Session()
    s.headers.update({
        "X-Shopify-Access-Token": token,
        "Content-Type": 'application/json'
    })
    return s

#Llamada a la sesión
def main():
    sess = create_session()
    resp = sess.get(shop_url+'/admin/api/2024-04/orders.json?status=open?fulfillment_status=unshipped?limit=100')
    resp = resp.json()
    return resp


#Función para limpiar el nombre
def limpiar_string(x):
    name = x.upper()
    name = re.sub('Á','A',name)
    name = re.sub('É','E',name)
    name = re.sub('Í','I',name)
    name = re.sub('Ó','O',name)
    name = re.sub('Ú','U',name)
    return name

def fulfillid(id_order):
    id_order = str(id_order)
    sess = create_session()
    query = shop_url+'/admin/api/2024-04/orders/'+id_order+'/fulfillment_orders.json'
    resp = sess.get(query)
    resp = resp.json()
    return resp

def fulfillorder(payload):
    sess = create_session()
    resp = sess.post(shop_url+'/admin/api/2024-04/fulfillments.json',json=payload)
    return resp

def main_location():
    sess = create_session()
    resp = sess.get(shop_url+'/admin/api/2024-04/locations.json')
    resp = resp.json()
    return resp

def extract_products(order):
    productos = []
    for item in order['line_items']:
        if(item['current_quantity']>0):
            # Cambio el nombre por el código que hemos creado
            parts = item['name'].split('-')
            # Quito espacios en blanco sobrantes del split
            parts = [part.strip() for part in parts]
            # Hago el cambio del nombre por el replacement que hemos definido antes
            # Cambios adhoc
            if(parts[0] == 'TWO'):
                parts[0] = parts[0] + ' ' + parts[1]
                parts[1] = parts[2]
                parts.pop()
            if parts[0] in replacementsName:
                parts[0] = replacementsName[parts[0]]
            else:
                # En el caso de que no se encuentra remplazo, que salte un error
                raise ValueError(f"Replacement for product '{parts[0]}' not found.")
            # Hago lo mismo con la talla
            # Caso en el que se divide en varios por la talla
            if(len(parts) == 3):
                # Los uno
                parts[1] = parts[1] + parts[2]
                parts.pop()
            if parts[1].upper() in replacementsSize:
                parts[1] = replacementsSize[parts[1].upper()]
            else:
                # En el caso de que no se encuentra remplazo, que salte un error
                raise ValueError(f"Replacement for product '{parts[1]}' not found.")
            # Uno el nombre nuevo a la talla
            new_product = ' - '.join(parts)
            productos.append('('+new_product + ')' +' x '+ str(item['quantity']))
        final_products = '\n'.join(productos)
    return final_products