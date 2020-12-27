from lib.timed_queue import TimedQueue
import os
import argparse
import json
import logging
import sys
import time
# import ssl

from werkzeug.utils import secure_filename
from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    make_response
)
from flask_sqlalchemy import SQLAlchemy

from lib.audio import prepare_input, audio_hash
from lib.caching.LRU import LRU
from lib.caching.store import TranscriptCache
from lib.decoder import Decoder
from lib.segment import Sentence
from lib.word import Word
from tools.file_io import delete_if_exists


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)

lru_policy = LRU(50)
cache = TranscriptCache(lru_policy)

# Loading Kaldi stuff
start = time.time()
aspire_decoder = Decoder("aspire")
aspire_decoder.initalize()
librispeech_decoder = Decoder("librispeech")
librispeech_decoder.initalize()
print(time.time() - start, "\t|", "Kaldi loaded!")

timedQueue = TimedQueue()

def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', required=True)
    parser.add_argument('--key', required=True)

    args = parser.parse_args()
    return args.cert, args.key


def transcript_queue(input_filename):
    timedQueue.accept(input_filename)

    sentences = Sentence.segment(decode_out["transcript"])
    symbols = decode_out["alignment"][0]
    offsets = decode_out["alignment"][1]
    lengths = decode_out["alignment"][2]
    alignment = compute_alignment(symbols, offsets, lengths, duration)

    w_dim = 0
    aligned_sentences = list()
    for s in sentences:
        sentence = s[0]
        punctuation = s[1]
        segment_idx = 0
        aligned_sentence = list()
        for segment_idx in enumerate(sentence):
            word = sentence[segment_idx]
            is_punctuation = punctuation[segment_idx] is not None
            # This is an important check, but for now we hack around
            timestamp = alignment[w_dim + segment_idx][1]

            word_obj = Word(word, timestamp)
            word_obj.add_tag("is_punctuated", is_punctuation)
            aligned_sentence.append(word_obj)

        sentence_obj = Sentence(aligned_sentence, 0)
        aligned_sentences.append(sentence_obj)
        w_dim += segment_idx  + 1

    for idx in enumerate(aligned_sentences):
        if idx < (len(aligned_sentences) - 1):
            aligned_sentences[idx].length = aligned_sentences[idx + 1].words[0].timestamp
    aligned_sentences[(len(aligned_sentences) - 1)].length = duration
    transcript_out = {"duration": duration, "length": len(alignment), "sentences": aligned_sentences}

    if use_cache:
        evicted = cache.add(h, transcript_out)
        print(evicted)  # Just for debugging, properly log later
        transcript_out["from_cache"] = "0"
    return transcript_out

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

        dict_obj = prep_and_transcribe(input_filename)
        delete_if_exists(input_filename)
        return make_response(jsonify(dict_obj), 200)
    except Exception as error:
        delete_if_exists("/tmp/transcribe.mp4")
        app.logger.debug("ERROR: " + str(error))


# TODO : TEST
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

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
    if len(sys.argv) > 1:
        model = None
        for arg_idx in range(1, len(sys.argv)):
            arg = sys.argv[arg_idx]
            out = prep_and_transcribe(sys.argv[1], model)
            base = os.path.basename(arg)
            sub_name = os.path.splitext(base)[0]
            transcript_path = "/home/raynor106/speech/transcripts/" + sub_name
            transcript_path += "_transcript_dump.json"
            dump = open(transcript_path, "w")
            print(json.dumps(out, indent=4), file=dump)
            print(time.time() - start, "\t|", arg)
            print(transcript_path)
    else:
        logging.getLogger().setLevel(logging.DEBUG)
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # context.load_cert_chain(
        #     "/etc/letsencrypt/live/capstonecs1.ml/fullchain.pem",
        #     "/etc/letsencrypt/live/capstonecs1.ml/privkey.pem")
        app.run(host='0.0.0.0', port=8080, debug=False)
