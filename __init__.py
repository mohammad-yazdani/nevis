import argparse
import glob
import logging
import os
import shutil
import time
import json
from typing import Tuple

from deepsegment import DeepSegment
from flask import Flask, jsonify, make_response, request, send_from_directory
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
# app.config.from_object("project.config.Config")
# db = SQLAlchemy(app) TODO

lru_policy = LRU(50)
cache = TranscriptCache(lru_policy)

# Load LSTM segmenter model
lstm_segmenter = DeepSegment("en", tf_serving=False)

# Loading Kaldi stuff
start = time.time()
aspire_decoder = Decoder("aspire", 8000, lstm_segmenter)
if not os.path.exists("/workspace/nvidia-examples/aspire/run_benchmark.sh"):
    aspire_decoder.initalize()
# librispeech_decoder = Decoder("librispeech")
# if not os.path.exists("/workspace/nvidia-examples/librispeech/run_benchmark.sh"):
    # librispeech_decoder.initalize()
print(time.time() - start, "\t|", "Kaldi loaded!")

# Initalize transcription queue
timedQueue = TimedQueue(aspire_decoder)


def getargs() -> Tuple[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', required=True)
    parser.add_argument('--key', required=True)

    args = parser.parse_args()
    return args.cert, args.key


def transcript_queue(input_filename) -> Tuple[int, str]:
    batch_id, batch_offset, corpus_id = timedQueue.accept(input_filename, aspire_decoder)
    return batch_id, batch_offset, corpus_id


@app.route('/')
def run():
    app.logger.debug('inside /')
    return "call /transcribe"


@app.route('/transcribe_file', methods=['POST'])
def transcribe_file():
    app.logger.debug('Request is of type' + request.method)
    try:
        input_filename = "/tmp/transcribe.mp4"
        mp4_byte_buffer = request.data
        mp4 = open(input_filename, "wb")
        mp4.write(mp4_byte_buffer)
        mp4.close()
        app.logger.debug("Read MP4.")
        batch_id, batch_offset, corpus_id = transcript_queue(input_filename)
        return make_response(jsonify({
            "batch_id": batch_id,
            "batch_offset": batch_offset,
            "corpus_id": corpus_id,
            "queue": timedQueue.active
        }), 200)
    except Exception as error:
        delete_if_exists("/tmp/transcribe.mp4")
        app.logger.debug("ERROR: " + str(error))
        print(error.with_traceback())


@app.route('/get_transcript', methods=['GET'])
def get_transcript():
    batch_id = int(request.args.get("batch_id"))
    corpus_id = request.args.get("corpus_id")
    fingerprint = None
    if "fingerprint" in request.args:
        fingerprint = request.args.get("fingerprint")

    if batch_id in timedQueue.output and corpus_id in timedQueue.output[batch_id]:
        tobj = timedQueue.output[batch_id][corpus_id]
        cache.add(fingerprint, tobj)
        return tobj
    else:
        return {
            "complete": "0",
            "queue": timedQueue.active
        }


@app.route('/cached_transcript', methods=['GET'])
def cached_transcript():
    corpus_fingerprint = request.args.get("fingerprint")
    return cache.get(corpus_fingerprint)


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    batch_id = int(request.args.get("batch_id"))
    corpus_id = request.args.get("corpus_id")
    if corpus_id is None:
        corpus_id = ""
    corrections = json.loads(request.data)["corrections"]

    fa = FeedbackAgent(batch_id, corpus_id, corrections)
    aspire_decoder.use_feedback = True
    fa.run()
    return {}

# TODO : TEST
# class User(db.Model):
#     __tablename__ = "users"

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(128), unique=True, nullable=False)
#     active = db.Column(db.Boolean(), default=True, nullable=False)

#     def __init__(self, email):
#         self.email = email


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return []
# TODO : TEST


if __name__ == '__main__':
    timedQueue.start()
    clean = True
    if clean:
        past_data = "/tmp/results/aspire"
        if os.path.exists(past_data) and os.path.isdir(past_data):
            shutil.rmtree(past_data)
        for file in glob.glob(r'/root/audio/batch*'):
            print("Deleting ", file)
            shutil.rmtree(file)
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8080, debug=False)
