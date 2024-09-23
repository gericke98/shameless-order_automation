import requests
from lxml import etree
import os
from datetime import datetime, timezone, timedelta
from SHOPIFY import limpiar_string
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load environment variables from .env file
load_dotenv()

# Aqui vamos a guardar el ID definido para no hacer una request todo el rato
URL_DEV_LOGIN = os.getenv('TIPSA_URL_DEV_LOGIN')
URL_DEV_ACTION = os.getenv('TIPSA_URL_DEV_ACTION')
URL_PROD_LOGIN = os.getenv('TIPSA_URL_PROD_LOGIN')
URL_PROD_ACTION = os.getenv('TIPSA_URL_PROD_ACTION')
AGENCIA = os.getenv('AGENCIA')
CLIENTE = os.getenv('CLIENTE')
CONTRASENA = os.getenv('CONSTRASENA')

def login_request():
    url = URL_PROD_LOGIN
    headers = {
        'Content-Type': 'application/xml',
    }
    soap_body = f"""
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <LoginWSService___LoginCli2 xmlns="http://tempuri.org/">
        <strCodAge>{AGENCIA}</strCodAge>
        <strCod>{CLIENTE}</strCod>
        <strPass>{CONTRASENA}</strPass>
        <strIdioma>ES</strIdioma>
        </LoginWSService___LoginCli2>
    </soap:Body>
    </soap:Envelope>
    """

    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error sending SOAP request: {e}')
        return None

def parse_login_response(response_content):
    try:
        root = etree.fromstring(response_content)
        namespaces = {
            'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
            'urn': 'urn:DinaPaq'
        }
        # Find the ID element in the SOAP header
        id_element = root.find('.//soapenv:Header//urn:ID', namespaces)
        if id_element is not None:
            return id_element.text
        else:
            return 'No ID found in the response'
    except etree.XMLSyntaxError as e:
        print(f'Error parsing SOAP response: {e}')
        return None
    
def create_label_request(id_value,order,products):
    url = URL_PROD_ACTION+'GrabaEnvio24'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }
    if(order['shipping_address']['address2'] != None):
        direccion = order['shipping_address']['address1'] + ';'+ order['shipping_address']['address2']
    else:
        direccion = order['shipping_address']['address1']
    soap_body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
       <soapenv:Header>
          <tem:ROClientIDHeader>
             <tem:ID>{id_value}</tem:ID>
          </tem:ROClientIDHeader>
       </soapenv:Header>
       <soapenv:Body>
          <tem:WebServService___GrabaEnvio24>
             <tem:strCodAgeCargo>{AGENCIA}</tem:strCodAgeCargo>
             <tem:strCodAgeOri>{AGENCIA}</tem:strCodAgeOri>
             <tem:strCodCli>{CLIENTE}</tem:strCodCli>
             <tem:dtFecha>{datetime.now(timezone(timedelta(hours=1))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+01:00"}</tem:dtFecha>
             <tem:strCodTipoServ>48</tem:strCodTipoServ>
             <tem:strCPDes>{order['shipping_address']['zip']}</tem:strCPDes>
             <tem:strPobDes>{order['shipping_address']['city']}</tem:strPobDes>
             <tem:strNomDes>{limpiar_string(order['shipping_address']['name'])}</tem:strNomDes>
             <tem:strDirDes>{direccion}</tem:strDirDes>
             <tem:strCPOri>28232</tem:strCPOri>
             <tem:strPobOri>Las Rozas de Madrid</tem:strPobOri>
             <tem:strNomOri>CORISA TEXTIL S.L. (SHAMELESS)</tem:strNomOri>
             <tem:strDirOri>Calle Bristol, 14b</tem:strDirOri>
             <tem:dPesoOri>0</tem:dPesoOri>
             <tem:intPaq>1</tem:intPaq>
             <tem:boInsert>1</tem:boInsert>
             <strObs><![CDATA[{products}]]></strObs>
             <tem:strTlfDes>{order['shipping_address']['phone']}</tem:strTlfDes>
          </tem:WebServService___GrabaEnvio24>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error sending SOAP request: {e}')
        return None

def create_label_request_int(id_value,order,products):
    url = URL_PROD_ACTION+'GrabaEnvio24'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }
    if(order['shipping_address']['address2'] != None):
        direccion = order['shipping_address']['address1'] + ';'+ order['shipping_address']['address2']
    else:
        direccion = order['shipping_address']['address1']
    soap_body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
       <soapenv:Header>
          <tem:ROClientIDHeader>
             <tem:ID>{id_value}</tem:ID>
          </tem:ROClientIDHeader>
       </soapenv:Header>
       <soapenv:Body>
          <tem:WebServService___GrabaEnvio24>
             <tem:strCodAgeCargo>{AGENCIA}</tem:strCodAgeCargo>
             <tem:strCodAgeOri>{AGENCIA}</tem:strCodAgeOri>
             <tem:strCodCli>{CLIENTE}</tem:strCodCli>
             <tem:dtFecha>{datetime.now(timezone(timedelta(hours=1))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+01:00"}</tem:dtFecha>
             <tem:strCodTipoServ>92</tem:strCodTipoServ>
             <tem:strCPDes>{order['shipping_address']['zip']}</tem:strCPDes>
             <tem:strPobDes>{order['shipping_address']['city']}</tem:strPobDes>
             <tem:strNomDes>{limpiar_string(order['shipping_address']['name'])}</tem:strNomDes>
             <tem:strDirDes>{direccion}</tem:strDirDes>
             <tem:strCPOri>28232</tem:strCPOri>
             <tem:strPobOri>Las Rozas de Madrid</tem:strPobOri>
             <tem:strNomOri>CORISA TEXTIL S.L. (SHAMELESS)</tem:strNomOri>
             <tem:strDirOri>Calle Bristol, 14b</tem:strDirOri>
             <tem:dPesoOri>0</tem:dPesoOri>
             <tem:intPaq>1</tem:intPaq>
             <tem:boInsert>1</tem:boInsert>
             <strObs><![CDATA[{products}]]></strObs>
             <tem:strContenido>Prenda textil de 100% algodon</tem:strContenido>
             <tem:dAltoOri>0</tem:dAltoOri>
             <tem:dAnchoOri>35</tem:dAnchoOri>
             <tem:dLargoOri>45</tem:dLargoOri>
             <tem:strCodPais>DE</tem:strCodPais>
             <tem:strTlfDes>{order['shipping_address']['phone']}</tem:strTlfDes>
          </tem:WebServService___GrabaEnvio24>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error sending SOAP request: {e}')
        return None
    
def create_label_request_it(id_value,order,products):
    url = URL_PROD_ACTION+'GrabaEnvio24'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }
    if(order['shipping_address']['address2'] != None):
        direccion = order['shipping_address']['address1'] + ';'+ order['shipping_address']['address2']
    else:
        direccion = order['shipping_address']['address1']
    soap_body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
       <soapenv:Header>
          <tem:ROClientIDHeader>
             <tem:ID>{id_value}</tem:ID>
          </tem:ROClientIDHeader>
       </soapenv:Header>
       <soapenv:Body>
          <tem:WebServService___GrabaEnvio24>
             <tem:strCodAgeCargo>{AGENCIA}</tem:strCodAgeCargo>
             <tem:strCodAgeOri>{AGENCIA}</tem:strCodAgeOri>
             <tem:strCodCli>{CLIENTE}</tem:strCodCli>
             <tem:dtFecha>{datetime.now(timezone(timedelta(hours=1))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+01:00"}</tem:dtFecha>
             <tem:strCodTipoServ>92</tem:strCodTipoServ>
             <tem:strCPDes>{order['shipping_address']['zip']}</tem:strCPDes>
             <tem:strPobDes>{order['shipping_address']['city']}</tem:strPobDes>
             <tem:strNomDes>{limpiar_string(order['shipping_address']['name'])}</tem:strNomDes>
             <tem:strDirDes>{direccion}</tem:strDirDes>
             <tem:strCPOri>28232</tem:strCPOri>
             <tem:strPobOri>Las Rozas de Madrid</tem:strPobOri>
             <tem:strNomOri>CORISA TEXTIL S.L. (SHAMELESS)</tem:strNomOri>
             <tem:strDirOri>Calle Bristol, 14b</tem:strDirOri>
             <tem:dPesoOri>0</tem:dPesoOri>
             <tem:intPaq>1</tem:intPaq>
             <tem:boInsert>1</tem:boInsert>
             <strObs><![CDATA[{products}]]></strObs>
             <tem:strContenido>Prenda textil de 100% algodon</tem:strContenido>
             <tem:dAltoOri>0</tem:dAltoOri>
             <tem:dAnchoOri>35</tem:dAnchoOri>
             <tem:dLargoOri>45</tem:dLargoOri>
             <tem:strCodPais>IT</tem:strCodPais>
             <tem:strTlfDes>{order['shipping_address']['phone']}</tem:strTlfDes>
          </tem:WebServService___GrabaEnvio24>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error sending SOAP request: {e}')
        return None
    
def parse_label_response(response_content):
    try:
        root = etree.fromstring(response_content)
        namespaces = {
            'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
            'v1': 'http://tempuri.org/'
        }
        albaran_element = root.find('.//v1:strAlbaranOut', namespaces)
        if albaran_element is not None:
            return albaran_element.text
        else:
            return 'No Albaran found in the response'
    except etree.XMLSyntaxError as e:
        print(f'Error parsing SOAP response: {e}')
        return None
    
def estado_envio_request(id_value,albaran_value):
    url = URL_PROD_ACTION+'ConsEnvEstados'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }
    soap_body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
       <soapenv:Header>
          <tem:ROClientIDHeader>
             <tem:ID>{id_value}</tem:ID>
          </tem:ROClientIDHeader>
       </soapenv:Header>
       <soapenv:Body>
          <tem:WebServService___ConsEnvEstados>
             <tem:strCodAgeCargo>{AGENCIA}</tem:strCodAgeCargo>
             <tem:strCodAgeOri>{AGENCIA}</tem:strCodAgeOri>
             <tem:strAlbaran>{albaran_value}</tem:strAlbaran>
          </tem:WebServService___ConsEnvEstados>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error sending SOAP request: {e}')
        return None

def estado_envios_fecha_request(id_value,fecha):
    url = URL_PROD_ACTION+'ConsUltimoEnvEstadosFecha::'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }
    soap_body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
       <soapenv:Header>
          <tem:ROClientIDHeader>
             <tem:ID>{id_value}</tem:ID>
          </tem:ROClientIDHeader>
       </soapenv:Header>
       <soapenv:Body>
          <tem:WebServService___ConsUltimoEnvEstadosFecha>
             <tem:strCodAgeCargo>{AGENCIA}</tem:strCodAgeCargo>
             <tem:strCodAgeOri>{AGENCIA}</tem:strCodAgeOri>
             <tem:dtFecha>{fecha}</tem:dtFecha>
          </tem:WebServService___ConsUltimoEnvEstadosFecha>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error sending SOAP request: {e}')
        return None
    
def parse_estado_envio_request(response_content):
    # Parse the XML
    root = ET.fromstring(response_content)

    # Extract the embedded XML within strEnvEstados
    embedded_xml = root.find('.//{http://tempuri.org/}strEnvEstados').text

    # Replace HTML-like entities with actual characters
    embedded_xml = embedded_xml.replace('&lt;', '<').replace('&gt;', '>')

    # Parse the embedded XML
    embedded_root = ET.fromstring(embedded_xml)

    # Extract the required elements
    results = []
    for env_estado in embedded_root.findall('.//ENV_ESTADOS'):
        tipo_est = env_estado.get('V_COD_TIPO_EST')
        fec_hora_alta = env_estado.get('D_FEC_HORA_ALTA')
        results.append({
            "V_COD_TIPO_EST": tipo_est,
            "D_FEC_HORA_ALTA": fec_hora_alta
        })

    return results

def save_id_to_file(id_value):
    with open(ID_FILE_PATH, 'w') as file:
        file.write(id_value)

def read_id_from_file():
    if os.path.exists(ID_FILE_PATH):
        with open(ID_FILE_PATH, 'r') as file:
            return file.read()
    return None


if __name__ == "__main__":
    saved_id = read_id_from_file()
    if saved_id:
        print("Using saved ID:")
        print(saved_id)
    else:
        response_content = login_request()
        if response_content:
            extracted_id = parse_login_response(response_content)
            if extracted_id and extracted_id != 'No ID found in the response':
                save_id_to_file(extracted_id)
                print("Extracted and Saved ID:")
                print(extracted_id)
                saved_id = extracted_id
            else:
                print(extracted_id)
    if saved_id:
        # new_response = estado_envios_fecha_request(saved_id,'2024-07-29')
        # print(new_response)
        subsequent_response = create_label_request(saved_id)
        if subsequent_response:
            print("Subsequent Response:")
            extracted_albaran = parse_label_response(subsequent_response)
            print("Extracted Albaran:")
            print(extracted_albaran)
            saved_albaran = extracted_albaran
            # if saved_albaran:
            #     estado_Envio_response = estado_envio_request(saved_id,saved_albaran)
            #     print(estado_Envio_response)
