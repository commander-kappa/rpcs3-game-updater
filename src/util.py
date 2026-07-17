import os
import requests
import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#INFO: I initially tried to invoke a request with the built in certificate verification. Due to it being a self signed cert by SCIE, which additionally uses a vulnarable hashing algorithm, Python always throws a SSL trust ERROR. I designed this workaround to atleast have some 3rd party verification, based upon the certificate I downloaded personally.
import ssl
import xml, xml.etree.ElementTree as ET

import hashing, exceptions as exc

HOSTNAME = 'a0.ww.np.dl.playstation.net'

CURSOR_UP = "\033[1A"
CLEAR = "\x1b[2K"

def get_host_cert() -> str:
    return ssl.get_server_certificate((HOSTNAME, 443))

def cert_to_binary(cert:str) -> bytes: 
    cert = cert.replace('\n', '')
    cert = cert.replace("-----BEGIN CERTIFICATE-----", '')
    cert = cert.replace("-----END CERTIFICATE-----", '')
    return cert.encode()


def request_update_xml(serial:str) -> ET: 
    response = requests.request(
        method = 'GET',
        url = f"https://{HOSTNAME}/tpl/np/{serial}/{serial}-ver.xml",
        verify = False
    )
    #TODO: validation
    return ET.fromstring(response.content) 

#TODO: OOP?
def get_update_urls(xml_object:ET) -> list:
    #TODO: No more recursion
    updates = []

    if xml_object.tag == 'package':
        updates.append({
            'version':  f"{xml_object.attrib['version']}",
            'sha1sum':  f"{xml_object.attrib['sha1sum']}",
            'url':      f"{xml_object.attrib['url']}"
        })

    for child in xml_object:
        updates += (get_update_urls(child))
    
    return updates

def download_update(
        update:dict,
        output_path:os.PathLike,
        use_buffer:bool = True,
        chunk_size:int = 8192
) -> None:
    response = requests.get(
            update['url'],
            timeout=10, 
            stream=True
    )
    response.raise_for_status()
    
    file_name = update['url'].split('/')[-1]
    output_path = os.path.join(output_path, file_name)
    file_size = int(response.headers.get('content-length', 0))
    
    print(f"Downloading {update['version']}: {file_name}\n")
    
    if use_buffer:
        download_size = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

                    download_size += len(chunk)
                    percent = (download_size / file_size * 100)
                    progress_bars = int(percent / 5)
                    print(f"{CURSOR_UP}{CLEAR}Download {percent:.0f}% [ {'='*progress_bars}{'.'*(20-progress_bars)} ]")
        print('\n')
    else:
        with open(output_path, 'wb') as f:
            f.write(response.content)

    #INFO: https://psx-place.com/threads/sha1sum-not-normal-sha1sum-of-update-packages-solved.22717/    
    with open(output_path, 'rb') as f:
        #TODO: buffered hashing
        sha1sum = hashing.calc_with(f.read()[:-32], 'sha1')
        if sha1sum != update['sha1sum']:
            raise exc.HashDoesNotMatch(update['sha1sum'], sha1sum, 'Package File')

def start(
    serial: str,
    cert_path:os.PathLike,
    output_path:os.PathLike
    ) -> int:
    
    if not serial[:4].isalpha() or not serial[4:-1].isdigit():
        raise exc.SerialNumberError(serial)

    if not os.path.exists(cert_path):
        raise exc.CertNotFound(cert_path)

    local_cert = '' 

    with open(cert_path) as f:
        local_cert = f.read()

    host_hash  = hashing.calc_with(cert_to_binary(get_host_cert()), 'sha256')
    local_hash = hashing.calc_with(cert_to_binary(local_cert), 'sha256')
    
    if host_hash != local_hash:
        raise exc.HashDoesNotMatch(local_hash, host_hash, 'Certificate')

    for update in get_update_urls(request_update_xml(serial)):
        try:
            download_update(update, output_path)
        except exc.HashDoesNotMatch as e:
            print(e.message)
            file_name = update['url'].split('/')[-1]
            os.remove(os.path.join(output_path, file_name))           

    return 0
