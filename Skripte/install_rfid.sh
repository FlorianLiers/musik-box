#!/bin/bash
# Bases on http://www.instructables.com/id/Raspberry-Pi-3-Model-B-MIFARE-RC522-RFID-Tag-Readi/

echo "Install basic software components"
sudo apt-get update
sudo apt-get install -y raspi-config=20170705 # Für Aktivierungs-GUI für SPI
sudo apt-get install -y gcc # für Compile von SPI-Py
sudo apt-get install -y python-pip # für Installation von Python Libs
sudo apt-get install -y python2.7-dev # nötig für RPi.GPIO
sudo pip install 'RPi.GPIO==0.7.0' # für Ansteuerung der Pins

echo "Install SPI-Py"
git clone https://github.com/lthiery/SPI-Py.git # Stand vom 20. Feb 2019
cd SPI-Py
sudo python setup.py install
cd ..

echo "Install MFCR522"
# Originally, the repo https://github.com/mxgxw/MFRC522-python.git was used.
# However, SPI-Py change their API and the version from mxgxw does not reflect that.
# There are some other user, who updates the lib und made it compatible with the new SPI-Py version
git clone https://github.com/noamnelke/MFRC522-python.git -b new_spi_pi # Stand vom 09. April 2019

echo "finished"

echo "Test the installation by running:"
echo "   python MFRC522-python/Read.py"