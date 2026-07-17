import sys, os, socket
import traceback
import exceptions as exc
from util import start

WORKING_DIR = os.getcwd()
MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CERT_PATH = os.path.join(MAIN_DIR, 'res', 'ww-np-dl-playstation-net.pem')

#TODO: ignore-cert CLI argument 
if __name__ == "__main__":
    arg = ''
    try:
        arg = sys.argv[1]
    except:
        print("No serialnumber argument given"); sys.exit(1)
    
    try:
        start(
            serial = arg,
            cert_path = CERT_PATH,
            output_path = WORKING_DIR
    )
    except ValueError as e:
        print(e.message)
        sys.exit(2)
    except FileNotFoundError as e:
        print(e.message)
        sys.exit(3)
    except exc.HashDoesNotMatch as e:
        print(e.message)
        if e.file_type == 'Certificate':
            sys.exit(4)
        elif e.file_type == 'Package File':
            sys.exit(5)
        else:
            sys.exit(255)
    except socket.gaierror as e:
        print(traceback.format_exc())
        print("Network Error")
        sys.exit(6)
    except Exception as e:
        print(traceback.format_exc())
        print('Unexpected Error! Aborting...')
        sys.exit(255)
