import argparse
import glob
import logging
import os
import shutil
import time
import json
from typing import Tuple

from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

def getargs() -> Tuple[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', required=True)
    parser.add_argument('--key', required=True)

    args = parser.parse_args()
    return args.cert, args.key

@app.route('/')
@cross_origin()
def run():
    app.logger.debug('inside /')
    return "call /transcribe"


@app.route('/transcribe_file', methods=['POST'])
@cross_origin()
def transcribe_file():
    app.logger.debug('Request is of type' + request.method)
    try:
        media_byte_buffer = request.data
        app.logger.debug("Read media.")
        corpus_id = "transcript_queue(media_byte_buffer)"
        return make_response(jsonify({
            "corpus_id": corpus_id,
            "queue": 0
        }), 200)
    except Exception as error:
        delete_if_exists("/tmp/transcribe.mp4")
        app.logger.debug("ERROR: " + str(error))
        raise error


@app.route('/get_transcript', methods=['GET'])
@cross_origin()
def get_transcript():
    corpus_id = request.args.get("corpus_id")
    return {
        "complete": "1",
        "queue": 0,
        "corpus_id_ack": corpus_id
    }


@app.route('/cached_transcript', methods=['GET'])
@cross_origin()
def cached_transcript():
    return {
        "complete": "0"
    }


@app.route('/submit_feedback', methods=['POST'])
@cross_origin()
def submit_feedback():
    corpus_id = request.args.get("corpus_id")
    if corpus_id is None:
        corpus_id = ""
    return {}

@app.route('/feedback_iterations', methods=['GET'])
@cross_origin()
def feedback_iterations():
    return {
        "iter": aspire_decoder.model_trainings
    }

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8080, debug=False)

