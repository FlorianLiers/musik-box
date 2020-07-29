#!/bin/bash
#
# Bases on https://forum.volumio.org/volumio-bluez-alsa-a2dp-bluetooth-support-t6130.html
#       and https://forum.volumio.org/bluetooth-speaker-plugin-t7432-100.html
#

echo "Installing Bluetooth Dependencies"
sudo apt-get update
sudo apt-get install -y libasound2-dev dh-autoreconf libortp-dev 'bluez=5.23-2+rpi2' 'pi-bluetooth=0.1.3+1' 'bluez-tools=0.2.0~20140808-3' libbluetooth-dev libusb-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libsbc1 libsbc-dev

echo "Cloning Bluez-Alsa repo"
cd /tmp
git clone -b v1.4.0 --single-branch https://github.com/Arkq/bluez-alsa.git

echo "Building Bluez-Alsa"
cd bluez-alsa
autoreconf --install
mkdir build && cd build
../configure --disable-hcitop --with-alsaplugindir=/usr/lib/arm-linux-gnueabihf/alsa-lib
make

echo "Installing Bluez-Alsa"
sudo make install

echo "Enable Bluez-Alsa as service in systemd"

# the folloging is a 
#    cat > /lib/systemd/system/bluezalsa.service
# just with root permissions
sudo rm /lib/systemd/system/bluezalsa.service
sudo tee -a /lib/systemd/system/bluezalsa.service > /dev/null <<EOC
[Unit]
Description=BluezAlsa proxy
Requires=bluetooth.service
After=bluetooth.service

[Service]
Type=simple
User=root
Group=audio
ExecStart=/usr/bin/bluealsa

[Install]
WantedBy=multi-user.target
EOC

sudo systemctl daemon-reload
sudo systemctl enable bluezalsa.service

echo "Installation ended"
echo "IMPORTANT: Please reboot your system in order to take over the changes!"