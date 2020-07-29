#!/bin/bash
if [ -z "$1" ]; then
	echo "Please specify a bluetooth mac address for the output device."
	echo "Example: $0 AC:19:09:10:22:11"
	exit 1
fi

echo "Local config for user with VLC. Store it in ~/.asoundrc"
sed "s/BLUETOOTHMAC/$1/g" ./Config/.asoundrc-RFID

echo "Global config for system that is used by Volumio player. Store it in /etc/asound.conf"
sed "s/BLUETOOTHMAC/$1/g" ./Config/asound.conf-VOLUMIO
