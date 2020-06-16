#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import requests
from websocket import create_connection
import thread
import os


def play(id, filename):
    print("Starting Volumio for " +id +" - " +filename)
    headers = {"Accept": "application/json"}
    resp = requests.get('http://localhost:3000/api/v1/getState', headers = headers)
    if resp.status_code == 200:
        print("State: " +str(resp.json()))
    ws = create_connection("ws://localhost:3000")
    print("Sending 'Hello, World'...")
    ws.send(json.dumps("getQueue"))
    print("Sent")
    print("Receiving...")
    result =  ws.recv()
    print("Received '%s'" % result)
    ws.close()
    
    resp = requests.get('http://localhost:3000/api/v1/getQueue', headers = headers)
    if resp.status_code == 200:
        print("State: " +str(resp.json()))


def stop():
	print("Stopping Volumio")