#!/usr/bin/python3
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'

import argparse
import json
import logging
import ssl
import sys
import time

from flask import Flask, request, jsonify, make_response

from lib.align import compute_alignment
from lib.audio import prepare_input, audio_hash
from lib.caching.LRU import LRU
from lib.caching.store import TranscriptCache
from lib.decode import Decoder
from lib.segment import Sentence
from lib.word import Word
from tools.file_io import delete_if_exists

app = Flask(__name__)

lru_policy = LRU(50)
cache = TranscriptCache(lru_policy)

# Loading Kaldi stuff
start = time.time()
decoder = Decoder()
print(time.time() - start, "\t|", "Kaldi loaded!")


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', required=True)
    parser.add_argument('--key', required=True)

    args = parser.parse_args()
    return args.cert, args.key


def prep_and_transcribe(input_filename, model_dir=None, debug=False, use_cache=True):
    # TODO : model_dir is not used because of OOP stuff to save RAM.

    mono_wav, duration = prepare_input(input_filename)
    app.logger.debug("Converted to WAV mono.")
    # Get audio hash
    h = audio_hash(mono_wav)
    # Check cache
    if use_cache:
        resolution = cache.get(h)
    else:
        resolution = None
    if resolution is None:
        # TODO : If not in cache, add to DB
        decode_out = decoder.decode(mono_wav)

        if debug:
            print(decode_out["transcript"])
            return 0 # TODO : For perf benching

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
            for segment_idx in range(len(sentence)):
                word = sentence[segment_idx]
                is_punctuation = punctuation[segment_idx] is not None
                # alignment_value = alignment[w_dim + segment_idx][0]
                # TODO : This is an important check, but for now we hack around
                # assert alignment_value in str(word).lower()
                timestamp = alignment[w_dim + segment_idx][1]

                word_obj = Word(word, timestamp)
                word_obj.add_tag("is_punctuated", is_punctuation)
                aligned_sentence.append(word_obj)

            sentence_obj = Sentence(aligned_sentence, 0)
            aligned_sentences.append(sentence_obj)
            w_dim += segment_idx + 1

        for idx in range(len(aligned_sentences)):
            if idx < (len(aligned_sentences) - 1):
                aligned_sentences[idx].length = aligned_sentences[idx + 1].words[0].timestamp
        aligned_sentences[(len(aligned_sentences) - 1)].length = duration
        transcript_out = {"duration": duration, "length": len(alignment), "sentences": aligned_sentences}

        if use_cache:
            evicted = cache.add(h, transcript_out)
            print(evicted)  # TODO : Just for debugging, properly log later
            transcript_out["from_cache"] = "0"
        
        return transcript_out
    else:
        resolution["from_cache"] = h
        return resolution


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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        model = None
        # if len(sys.argv) > 2:
        #    model = sys.argv[2]
        for arg_idx in range(1, len(sys.argv)):
            arg = sys.argv[arg_idx]
            prep_and_transcribe(arg, model, debug=True, use_cache=False)
            # out = prep_and_transcribe(sys.argv[1], model, debug=True, use_cache=False, text_only=True)
            # dump = open("dump.json", "w")
            # json.dump(out, dump, indent=4)
            print(time.time() - start, "\t|", arg)
    else:
        logging.getLogger().setLevel(logging.DEBUG)
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # context.load_cert_chain(
        #     "/etc/letsencrypt/live/capstonecs1.ml/fullchain.pem",
        #     "/etc/letsencrypt/live/capstonecs1.ml/privkey.pem")
        app.run(host='0.0.0.0', port=8080, debug=False)
