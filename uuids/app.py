import flask
import uuid
import os
import socket
import logging


app = flask.Flask(__name__)


@app.route('/uuids', methods=['GET'])
def get_uuids():
    node_name = os.getenv('NODE_NAME', socket.gethostname())
    generated_uuid = uuid.uuid1()
    app.logger.info('Node: [%s] UUID: [%s]', node_name, generated_uuid)
    rsp = flask.jsonify(uuid=generated_uuid, node=node_name)
    rsp.status_code = 200
    rsp.headers['Content-Type'] = 'application/json'
    return rsp
