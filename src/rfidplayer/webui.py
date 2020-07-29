#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
from threading import Thread
from flask import Flask

app = Flask(__name__)
latest_chip_id = None
main_thread = None


@app.route('/')
def index():
    global latest_chip_id
    return "Hello, World! " +str(latest_chip_id)

def set_latest_chip(id):
    global latest_chip_id
    print("set latest chip to " +id)
    latest_chip_id = id

def webui_main():
    global app
    app.run(debug=True, use_reloader=False, port=8080, host="0.0.0.0")


def start():
    global main_thread
    print("Starting web ui " +__name__)
    main_thread = Thread(target=webui_main)
    # make it a deamon, so the main thread will not wait for this thread to end
    main_thread.setDaemon(True)
    main_thread.start()

def stop():
    print("Stopping web ui")


start()
time.sleep(10)
stop()