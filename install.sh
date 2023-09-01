#! /bin/bash
apt install firefox -y
apt install python3-pip -y
apt install ffmpeg -y

pip3 install --no-cache-dir -r requirements.txt

python3 scrapper3.py
