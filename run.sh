#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install wheel
pip install -r requirements.txt
pyinstaller sonix-flasher.spec
./dist/sonix-flasher/sonix-flasher
