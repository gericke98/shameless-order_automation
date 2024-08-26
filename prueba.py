from TIPSA import login_request,parse_login_response,create_label_request,parse_label_response,create_label_request_int
from SHOPIFY import main,fulfillid,main_location,fulfillorder,extract_products
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

AGENCIA = os.getenv('AGENCIA')
CLIENTE = os.getenv('CLIENTE')
path_csv_orders = os.getenv('PATH_CSV')
tracking_url = os.getenv('TRACKING_URL')
transport_company = os.getenv('TRACKING_COMPANY')

#Encuento el location del almacén para fulfillear
location_id = main_location()['locations'][0]['id']

resp = main()

for order in resp['orders']:
    if((order['fulfillment_status'] != 'fulfilled')):
        if((order['shipping_address']['country'] == 'Spain') & (order['name'] == '#33881')):
            print(order['name'])
            final_products = extract_products(order)
            print(final_products)