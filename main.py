import sys
import os.path
import hashlib
import requests
import socket
import ssl
import xml


def main():
    arg = ''
    try:
        arg = sys.argv[1]
    except:
        print("No Arguments given")
        sys.exit(1)
    

    cert = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ww-np-dl-playstation-net-chain.pem') 
    if not os.path.exists(cert):
        print("playstation.pem cert not found")
        sys.exit(2)
    ssl_ctx = create_urllib3_context(ssl_version=ssl.PROTOCOL_TLS_CLIENT)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(cert)

    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            kwargs['ssl_context'] = ssl_ctx
            return super().init_poolmanager(*args, **kwargs)

    session = requests.Session()
    session.mount('https://', SSLAdapter())

    https = session.get(url = f"https://a0.ww.np.dl.playstation.net/tpl/np/{arg}/{arg}-ver.xml")
    
    print(https.content)

if __name__ == "__main__":
    main()



