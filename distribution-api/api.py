import flask
import random
import collections

app = flask.Flask(__name__)


@app.route('/healthz', methods=['GET'])
def health_check():
    rsp = flask.jsonify(status='OK')
    rsp.status_code = 200
    rsp.headers['Content-Type'] = 'application/json'
    return rsp


@app.route('/random', methods=['GET'])
def api_random():
    rnd = random.randrange(0,100)
    rsp = flask.jsonify(random=rnd)
    rsp.status_code = 200
    rsp.headers['Content-Type'] = 'application/json'
    return rsp


@app.route('/normal', methods=['GET'])
def api_normal():
    rnd_dict = {}
    for i in range(10000):
        rnd = round(random.normalvariate(100,5), 0)
        if rnd in rnd_dict:
            rnd_dict[rnd] += 1
        else:
            rnd_dict[rnd] = 1
    ordered_rnd_dict = collections.OrderedDict(sorted(rnd_dict.items()))
    rsp = flask.make_response(flask.render_template('output.j2', random_dict=ordered_rnd_dict))
    rsp.status_code = 200
    rsp.headers['Content-Type'] = 'text/plain'
    return rsp