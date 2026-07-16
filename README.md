# RPCS3 Game Updater
A simple lightweight Python CLI tool to download PS3 game update files for RPCS3 by entering the serialnumber 

## Features
- Call official PS3 update API and retrieve relevant package metadata
- Integrated SSL verification 
- Automatic download of all update files
- SHA1 Verification of downloaded files 
- Verbose exception handling

## Stack
- **PS3 Emulator:** [RPCS3](https://rpcs3.net/download)
- **Language**: [![Python](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](https://www.python.org/)  
- **Recommended Build/Package Manager**: [UV](https://docs.astral.sh/uv/) 


## Project Structure
```
rpcs3-game-updater/
├── get_ver_xml_url.sh                  # Independent bash script to generate API URL
├── pyproject.toml                      # UV project dependencies
├── res
│   └── ww-np-dl-playstation-net.pem    # SCIE self-signed certificate
└─ src
    └── main.py                         # Main executable

```

## Installation
1. Clone the repo:
```bash
https://codeberg.org/kappa-dev/rpcs3-game-updater.git
```

2. Activate the virtual environment and install dependencies with [UV Python project manager](https://docs.astral.sh/uv/):
```bash
uv sync
```

## Usage 
1. Find game serialnumber in RPCS3 launcher
2. Run main.py and pass serialnumber as an argument
```bash
uv run src/main.py <serialnumber>

```
Example: [WipEout HD Fury](https://wiki.rpcs3.net/index.php?curid=960)
```bash
uv run src/main.py BCES00664

Downloading 02.10: EP9000-BCES00664_00-WHDPATCH21000000-A0210-V0100-PE.pkg
Download 100% [ ==================== ]


Downloading 02.30: EP9000-BCES00664_00-WHDPATCH23000000-A0230-V0101-PE.pkg
Download 100% [ ==================== ]


Downloading 02.50: EP9000-BCES00664_00-WHDPATCH25000000-A0250-V0101-PE.pkg
Download 100% [ ==================== ]


Downloading 02.51: EP9000-BCES00664_00-WHDPATCH25100000-A0251-V0100-PE.pkg
Download 100% [ ==================== ]


Download sucessful!
```
3. Import .pkg files to RPCS3

## Legal Disclaimer
This tool is intended only to fetch official update files from the official playstation.net API. It does not and must not attempt to bypass authentication or DRM. Only download updates for software you own and in compliance with applicable laws and service agreements. Do not use this tool to distribute copyrighted content.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bug reports and feature suggestions.

## License
This repository is provided under the GPL3.0 License. See the `LICENSE` file for details.

## Contact
Maintained by kappa-dev — codeberg@kappa-dev.de
