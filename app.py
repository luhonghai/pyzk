# -*- coding: utf-8 -*-
import json, sys, pytz, datetime
from zk import ZK, const
from functools import wraps

from flask import Flask, jsonify, abort, request
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("zk")

attendances = []
last_updated = datetime.datetime.now(pytz.utc)

def create_app():

    settings = {
        'DEBUG': False,
    }

    app = Flask(__name__)
    app.config.update(settings)

    return app

app = create_app()

@app.route('/attendances', methods=['GET'])
def list_attendances():
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())

@app.route('/fetch', methods=['GET'])
def fetch_attendances():
    conn = None
    global attendances
    global last_updated
    zk = ZK('192.168.0.201', port=4370, timeout=5)
    try:
        print 'Connecting to device ...'
        conn = zk.connect()
        print 'Disabling device ...'
        conn.disable_device()
        attendance_data = conn.get_attendance()
        utc_tz = pytz.timezone('UTC')
        local_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        attends = []
        for data in attendance_data:
            attendance = {}
            attendance['user_id'] = data.user_id
            attendance['status'] = data.status
            attendance['timestamp'] = local_tz.localize(data.timestamp).astimezone(utc_tz).isoformat()
            attends.append(attendance)
        attendances = attends
        last_updated = datetime.datetime.now(pytz.utc)
    except Exception, e:
        print "Process terminate : {}".format(e)
    finally:
        print 'Enabling device ...'
        conn.enable_device()
        print 'Disconnect from device ...'
        if conn:
            conn.disconnect()
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
