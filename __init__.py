import argparse
import glob
import json
import logging
import os
import shutil
import time
from typing import Tuple

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

# from flask_sqlalchemy import SQLAlchemy
from lib.caching.LRU import LRU
from lib.caching.store import TranscriptCache
from lib.decoder import Decoder
from lib.timed_queue import TimedQueue
from lib.feedback.feedback import FeedbackAgent
from tools.file_io import delete_if_exists

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'

app = Flask(__name__)
CORS(app)
# app.config.from_object("project.config.Config")
# db = SQLAlchemy(app) TODO

lru_policy = LRU(1000)
cache = TranscriptCache(lru_policy)

# Loading Kaldi stuff
start = time.time()
aspire_decoder = Decoder("aspire", 8000)
if not os.path.exists("/workspace/nvidia-examples/aspire/run_benchmark.sh"):
    aspire_decoder.initialize()
# librispeech_decoder = Decoder("librispeech")
# if not os.path.exists("/workspace/nvidia-examples/librispeech/run_benchmark.sh"):
# librispeech_decoder.initialize()
logging.info(time.time() - start, "\t|", "Kaldi loaded!")

# Initialize transcription queue
timedQueue = TimedQueue(aspire_decoder)


def getargs() -> Tuple[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', required=True)
    parser.add_argument('--key', required=True)

    args = parser.parse_args()
    return args.cert, args.key


def transcript_queue(media_buffer: bytes) -> str:
    corpus_id = timedQueue.accept(media_buffer, aspire_decoder)
    return corpus_id


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
        corpus_id = transcript_queue(media_byte_buffer)
        return make_response(jsonify({
            "corpus_id": corpus_id,
            "queue": timedQueue.active
        }), 200)
    except Exception as error:
        delete_if_exists("/tmp/transcribe.mp4")
        app.logger.debug("ERROR: " + str(error))
        raise error


@app.route('/get_transcript', methods=['GET'])
@cross_origin()
def get_transcript():
    corpus_id = request.args.get("corpus_id")
    fingerprint = None
    if "fingerprint" in request.args:
        fingerprint = request.args.get("fingerprint")
        cached = cache.get(fingerprint)
        if cached != {}:
            return cached

    if corpus_id in timedQueue.output:
        tobj = timedQueue.output[corpus_id]
        tobj["quality"] = aspire_decoder.model_trainings
        cache.add(fingerprint, tobj)
        return tobj
    elif corpus_id in timedQueue.corpus_map:
        try:
            tobj = Decoder.fetch_transcript(timedQueue.get_corpus_batch(corpus_id), corpus_id)
            tobj["quality"] = aspire_decoder.model_trainings
            cache.add(fingerprint, tobj)
            return tobj
        except Exception as error:
            app.logger.debug("ERROR: " + str(error))

    return {
        "complete": "0",
        "queue": timedQueue.active
    }


@app.route('/cached_transcript', methods=['GET'])
@cross_origin()
def cached_transcript():
    if "fingerprint" in request.args:
        fingerprint = request.args.get("fingerprint")
        cached = cache.get(fingerprint)
        if cached != {}:
            return cached
    return {
        "complete": "0"
    }


@app.route('/submit_feedback', methods=['POST'])
@cross_origin()
def submit_feedback():
    corpus_id = request.args.get("corpus_id")
    if corpus_id is None:
        corpus_id = ""
    corrections = json.loads(request.data)["corrections"]
    # Get batch id
    fa = FeedbackAgent(timedQueue.get_corpus_batch(corpus_id), corpus_id, corrections)
    aspire_decoder.train_model(fa)
    return {}


@app.route('/feedback_iterations', methods=['GET'])
@cross_origin()
def feedback_iterations():
    return {
        "iter": aspire_decoder.model_trainings
    }


# TODO : TEST
# class User(db.Model):
#     __tablename__ = "users"

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(128), unique=True, nullable=False)
#     active = db.Column(db.Boolean(), default=True, nullable=False)

#     def __init__(self, email):
#         self.email = email./lib/feedback/__pycache__
def media_files(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        input_file = request.files["file"]
        filename = secure_filename(input_file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return []


if __name__ == '__main__':
    timedQueue.start()
    clean = True
    if clean:
        past_data = "/tmp/results/aspire"
        if os.path.exists(past_data) and os.path.isdir(past_data):
            shutil.rmtree(past_data)
        for file in glob.glob(r'/root/audio/batch*'):
            logging.debug("Deleting ", file)
            shutil.rmtree(file)
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8080, debug=False)
