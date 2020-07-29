#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
from threading import Thread
from flask import Flask
from flask import render_template
from flask import request
import mapping

app = Flask(__name__)
latest_chip_id = None
main_thread = None


@app.route('/')
def index():
    global latest_chip_id
    map = mapping.get_all_mappings()
    curr_mapping = map.get(latest_chip_id, {})
    print("Render mapping with " +str(len(map)) +" entries")
    return render_template(u'list.html', curr_chip=latest_chip_id, curr_mapping=curr_mapping, all_mappings=map)

@app.route('/changeMapping', methods=['POST'])
def change_mapping():
    chip = request.form.get('chip').encode('utf8', 'replace')
    pattern = request.form.get('pattern').encode('utf8', 'replace')
    comment = request.form.get('comment').encode('utf8', 'replace')
    print("change mapping: " +chip +": " +pattern +" (" +comment +")")
    mapping.set_mapping(chip, pattern, comment)
    if request.accept_mimetypes.accept_json:
        return {}
    else:
        return redirect("/")


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

