import sys
import os.path
import hashlib
import requests
import socket
import ssl
import xml
import xml.etree.ElementTree as ET

HOSTNAME = 'a0.ww.np.dl.playstation.net'
WORKING_DIR = os.getcwd()

def cert_to_hash(cert):
    return hashlib.sha256(cert.replace('\n', '').encode()).hexdigest()


def get_file_hash(file_path):
    buffer = ''
    with open(file_path, 'r') as f:
        buffer = f.read()
    return cert_to_hash(buffer)

#TODO: Better functions
def download_updates(xml_object, level = 0):
    if xml_object.tag == 'package':
        print(f"{xml_object.attrib['version']}: {xml_object.attrib['url']}")
        download_update(xml_object.attrib['url'])

    for child in xml_object:
        download_updates(child, level + 1)

def download_update(url:str) -> None:
    #TODO: Check integrity of file
    #TODO: Buffered Download

    file_path = f"{WORKING_DIR}/{url.split('/')[-1]}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    with open(file_path, 'wb') as f:
        print(f"Downloaded update.pkg: {file_path}")
        f.write(response.content)
 

def main():
    arg = ''
    try:
        arg = sys.argv[1]
    except:
        print("No Arguments given")
        sys.exit(1)

    cert = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res', 'ww-np-dl-playstation-net-chain.pem') 
    if not os.path.exists(cert):
        print("local certificate file not found")
        sys.exit(2)

    online_hash = ''
    try:
        online_hash = cert_to_hash(ssl.get_server_certificate((HOSTNAME, 443)))
    except:
        print(f"Could not retrieve {HOSTNAME} SSL certificate")
        sys.exit(3)

    
    local_hash = get_file_hash(cert)

#INFO: I initially tried to invoke a request with the built in certificate verification. Due to it being a self signed cert by SCIE, which additionally uses a vulnarable hashing algorithm, Python always throws a SSL trust ERROR. I designed this workaround to atleast have some verification, based upon the certificate I downloaded personally.
    if online_hash != local_hash:
        print('Warning: Local certificate does not match server certificate!')
        sys.exit(4)

    https = requests.request(
        method = 'GET',
        url = f"https://{HOSTNAME}/tpl/np/{arg}/{arg}-ver.xml",
        verify = False
    )
    

    #print(https.content)
    xml_object = ET.fromstring(https.content)   
    download_updates(xml_object)

if __name__ == "__main__":
    main()
