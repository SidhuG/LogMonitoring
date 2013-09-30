#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
from celeryLogReader import logReaderTask

flaskLogStats = Flask(__name__)

#GET method implementation
@flaskLogStats.route('/logs/api/v1.0/stats/<string:filename>/<int:hours>', methods = ['GET'])
def get_tasks(filename, hours):
    try:
        fullFilename = "/var/log/" + filename
        open(fullFilename, 'r')
    except IOError:
        abort(404)
    result = logReaderTask.delay(filename, hours)
    while result.ready() is False:
        continue
    stats = result.get()
    return jsonify( { 'stats': stats } )

#POST method implementation
@flaskLogStats.route('/logs/api/v1.0/stats', methods = ['POST'])
def create_task():
    if not request.json or not 'filename' in request.json or not 'hours' in request.json:
        abort(400)
    try:
        fullFilename = "/var/log/" + request.json['filename']
        open(fullFilename, 'r')
    except IOError:
        abort(404)
    result = logReaderTask.delay(request.json['filename'], request.json['hours'])
    while result.ready() is False:
        continue
    stats = result.get()
    return jsonify( { 'stats': stats } ), 201

@flaskLogStats.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'File not found' } ), 404)

if __name__ == '__main__':
    flaskLogStats.run(debug = True)
