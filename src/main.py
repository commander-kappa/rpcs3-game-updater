import sys
import os.path
import hashlib
import requests
import socket
import ssl
import xml
import xml.etree.ElementTree as ET
import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#INFO: I initially tried to invoke a request with the built in certificate verification. Due to it being a self signed cert by SCIE, which additionally uses a vulnarable hashing algorithm, Python always throws a SSL trust ERROR. I designed this workaround to atleast have some 3rd party verification, based upon the certificate I downloaded personally.

HOSTNAME = 'a0.ww.np.dl.playstation.net'
WORKING_DIR = os.getcwd()
CURSOR_UP = "\033[1A"
CLEAR = "\x1b[2K"

class HashDoesNotMatch(Exception):
    def __init__(self, expected_hash, calculated_hash):
        self.message = f"Hashes do not match!\nExpected:  {expected_hash}\nCalculated: {calculated_hash}"
        super().__init__(self.message)

def cert_to_hash(cert:str) -> str:
    return hashlib.sha256(cert.rstrip('\n').encode()).hexdigest()

def get_file_hash(file_path) -> str:
    buffer = ''
    with open(file_path, 'r') as f:
        buffer = f.read()
    return cert_to_hash(buffer)

def request_update_xml(serial:str) -> ET: 
    #TODO: Serial validation
    response = requests.request(
        method = 'GET',
        url = f"https://{HOSTNAME}/tpl/np/{serial}/{serial}-ver.xml",
        verify = False
    )
    
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
    file_path = os.path.join(WORKING_DIR, file_name)
    file_size = int(response.headers.get('content-length', 0))
    
    print(f"Downloading {update['version']}: {file_name}\n")
    
    if use_buffer:
        download_size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

                    download_size += len(chunk)
                    percent = (download_size / file_size * 100)
                    progress_bars = int(percent / 5)
                    print(f"{CURSOR_UP}{CLEAR}Download {percent:.0f}% [ {'='*progress_bars}{'.'*(20-progress_bars)} ]")
        print('\n')
    else:
        with open(file_path, 'wb') as f:
            f.write(response.content)

#INFO: https://psx-place.com/threads/sha1sum-not-normal-sha1sum-of-update-packages-solved.22717/    
    with open(file_path, 'rb') as f:
        #TODO: buffered hashing
        content = f.read()[:-32]
        sha1sum = hashlib.sha1(content).hexdigest() 
        if sha1sum != update['sha1sum']:
            raise HashDoesNotMatch(update['sha1sum'], sha1sum)

def main():
    arg = ''
    try:
        arg = sys.argv[1]
    except:
        print("No Arguments given")
        sys.exit(1)

    cert = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res', 'ww-np-dl-playstation-net.pem') 
    if not os.path.exists(cert):
        print("local certificate file not found")
        sys.exit(2)

    online_hash = ''
    try:
        online_hash = cert_to_hash(ssl.get_server_certificate((HOSTNAME, 443)))
    except:
        print(f"Could not retrieve {HOSTNAME} SSL certificate")
        sys.exit(3)

    #TODO: ignore cert argument 
    local_hash = get_file_hash(cert)

    if online_hash != local_hash:
        print('Warning: Local certificate does not match server certificate!')
        sys.exit(4)

    for update in get_update_urls(request_update_xml(arg)):
        try:
            download_update(update)
        except HashDoesNotMatch as e:
            print(e.message)
            file_name = update['url'].split('/')[-1]
            os.remove(os.path.join(WORKING_DIR, file_name))           

    print("Download sucessful!"); sys.exit(0)

if __name__ == "__main__":
    main()
