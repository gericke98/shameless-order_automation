from TIPSA import (login_request,
                   parse_login_response,
                   create_label_request,
                   parse_label_response,
                   create_label_request_int,
                   create_label_request_it,
                   create_label_request_pt)
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

# Encuento el location del almacén para fulfillear
location_id = main_location()['locations'][0]['id']

def perform_fulfillment(order, extracted_id, df_orders, list_new):
    """Handles the order fulfillment process based on country."""
    country = order['shipping_address']['country']
    order_name = order['name']
    print(order_name)
    print(country)
    
    # Extract products
    final_products = extract_products(order)
    
    # Create label request based on country
    if country == 'Spain':
        subsequent_response = create_label_request(extracted_id, order, final_products)
    elif country == 'Germany':
        subsequent_response = create_label_request_int(extracted_id, order, final_products)
    elif country == 'Italy':
        subsequent_response = create_label_request_it(extracted_id, order, final_products)
    elif country == 'Portugal':
        subsequent_response = create_label_request_pt(extracted_id, order, final_products)
    else:
        return
    
    # If label request is successful
    if subsequent_response:
        list_new.append(order_name)
        extracted_albaran = parse_label_response(subsequent_response)
        print(extracted_albaran)
        
        if extracted_albaran:
            # Fulfill the order
            fulfillment_id = fulfillid(order['id'])['fulfillment_orders'][0]['id']
            tracking_number = f"{AGENCIA}{AGENCIA}{extracted_albaran}"
            
            # Define fulfillment payload
            payload = {
                "fulfillment": {
                    "notify_customer": 'true',
                    "location_id": location_id,
                    "tracking_info": {
                        "url": tracking_url,
                        "company": transport_company,
                        "number": tracking_number,
                    },
                    "line_items_by_fulfillment_order": [
                        {"fulfillment_order_id": fulfillment_id}
                    ]
                }
            }
            
            # Make the fulfillment request
            f = fulfillorder(payload)
            if f.status_code == 201:
                print(f"{order_name}: Fulfillment successful!")
            else:
                print(f"{order_name}: Fulfillment encountered an issue.")
            
            # Update CSV
            df_orders_new = pd.DataFrame(list_new, columns=['order_number'])
            df_orders_final = pd.concat([df_orders, df_orders_new]).drop_duplicates(subset='order_number', keep='first').reset_index(drop=True)
            df_orders_final.to_csv(path_csv_orders, index=False)

# Hago la llamada a TIPSA para tener un ID: OJO que dura 10 minutos
print('Haciendo login...')
response_content = login_request()
# Extraigo el ID del response
print('Parseando login...')
extracted_id = parse_login_response(response_content)
# Me aseguro de que tenemos ID
if extracted_id:
    # Extraigo los pedidos de shopify
    shopify_response = main()
    # Leo los pedidos ya enviados para no duplicarlos
    list_new = []
    df_orders = pd.read_csv(path_csv_orders)
    for order in shopify_response['orders']:
        # Solo hago aquellos que no están ya fulfilled y que no están en el CSV
        if((order['fulfillment_status'] != 'fulfilled') & (order['name'] not in df_orders['order_number'].unique())):
            country = order['shipping_address']['country']
            if country in ['Spain', 'Germany', 'Italy', 'Portugal']:
                perform_fulfillment(order, extracted_id, df_orders, list_new)
                if((order['shipping_address']['country'] == 'Germany')| (order['shipping_address']['country'] == 'Italy') | (order['shipping_address']['country'] == 'Portugal')):
                    # Caso de internacional en Germany
                    print(order['name'])
                    final_products = extract_products(order)
                    if(order['shipping_address']['country'] == 'Germany'):
                        subsequent_response = create_label_request_int(extracted_id,order,final_products)
                    elif(order['shipping_address']['country'] == 'Italy'):
                        subsequent_response = create_label_request_it(extracted_id,order,final_products)
                    else:
                        subsequent_response = create_label_request_pt(extracted_id,order,final_products)
                    if subsequent_response:
                        # Agrego la nueva orden al CSV
                        list_new.append(order['name'])
                        extracted_albaran = parse_label_response(subsequent_response)
                        print(extracted_albaran)
                        if extracted_albaran:
                            # Hago el fulfill del order
                            fulfillment_id = fulfillid(order['id'])['fulfillment_orders'][0]['id']
                            tracking_number = str(AGENCIA+AGENCIA+extracted_albaran)
                            #Defino el payload que le va a entrar a la query del fulfill
                            payload = {
                                "fulfillment": 
                                    {            
                                        "notify_customer": 'true',
                                        "location_id": location_id,        
                                        "tracking_info":
                                            {                
                                            "url": tracking_url,
                                            "company": transport_company,
                                            "number": tracking_number,            
                                            },
                                        "line_items_by_fulfillment_order": [
                                            {
                                                "fulfillment_order_id": fulfillment_id
                                            }
                                        ]    
                                    }
                            }
                            #Hago la request de la api
                            f = fulfillorder(payload)
                            if(f.status_code==201):
                                print(order['name'])
                                print('Ha ido bien!!')
                            else:
                                print(order['name'])
                                print('Tenemos algun problemilla')
                            # Transformo pedido a dataframe
                            df_orders_new = pd.DataFrame(list_new, columns = ['order_number'])
                            # Concat de new orders and clean the dataframe
                            df_orders_final = pd.concat([df_orders,df_orders_new])
                            df_orders_final = df_orders_final.drop_duplicates(subset='order_number',keep='first').reset_index(drop=True)
                            df_orders_final.to_csv(path_csv_orders,index=False)

                

