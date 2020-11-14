#!/usr/bin/python3

# TODO : Findings:
# So far it seems that 500, -50 is the sweet spot. But I believe we should
# thinking about training a network which given the audio bytes or a representation
# of the audio bites will give the best segmentation parameters.
# Here the best is parameters that result in the lowest number of sentenceless segments


import sys
import time
import os
import shutil

import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent

from play_sequence import play_seq
from yt_dl import dl_yt_wav


pad = True

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    """ Normalize given audio chunk """
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)


def chunk_audio(m=500, t=-50, raw=False):
    aud_chunks = split_on_silence(sound_file, min_silence_len=m, silence_thresh=t, seek_step=1)
    out_chunks = [] 

    for c in aud_chunks:
        if pad:
            # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
            s = AudioSegment.silent(duration=500) # TODO : How should this value change?
            # Add the padding chunk to beginning and end of the entire chunk.
            tot = s + c + s
        else:
            tot = c
        
        # Normalize the entire chunk.
        if pad:
            norm: AudioSegment = match_target_amplitude(tot, -20.0)
        else:
            norm: AudioSegment = match_target_amplitude(tot, 0)

        if raw:
            out_chunks.append(norm.raw_data)
        else:
            out_chunks.append(norm)

    return out_chunks


if __name__ == '__main__':
    start = time.time()

    if len(sys.argv) > 1:
        sound_file = AudioSegment.from_wav(sys.argv[1])
    else:
        sound_file = AudioSegment.from_wav(dl_yt_wav("https://www.youtube.com/watch?v=p-XCC0y8eeY"))
    print(sound_file)

    # chks = chunk_audio(raw=True)
    # print(chks)

    # end = time.time()
    # print(end - start)
    # exit(0)

    # TODO: Make sure the variance of non-silent parts is NOT zero
    # dev = list()
    # test_params = range(1, 20)
    # for params in test_params:
    #     # Core params are min_silence + silence_thresh
    #     min_slc_len = params * 100  # TODO : 500 is pretty good
    #     # For the thresh param we also have to consider background noise
    #     slc_thresh = -50  # TODO : -50 is pretty good

    #     silent_seq = detect_nonsilent(sound_file, min_silence_len=min_slc_len, silence_thresh=slc_thresh, seek_step=1)
    #     mid = time.time()

    #     graphable = list()
    #     for seq in silent_seq:
    #         graphable.append(seq[1] - seq[0])

    #     variance = np.var(graphable)
    #     dev.append(variance)
    #     # print("time: %6.4f,\tmin: %6.4f,\tthresh: %6.4f,\tvariance: %6.4f" % (mid - start, min_slc_len, slc_thresh,
    #     # variance)) plt.bar(x=range(len(graphable)), height=graphable) plt.show() exit(1)

    # plt.plot(range(len(silent_seq)), graphable)
    # assert len(test_params) == len(dev)
    # plt.bar(x=test_params, height=dev)
    # plt.show()

    # Core params are min_silence + silence_thresh
    min_sentence_slc_len = 500
    min_word_slc_len = 100  # TODO : 500 is pretty good
    # For the thresh param we also have to consider background noise
    setnence_paragraph_slc_thresh = -50  # TODO : -50 is pretty good
    word_slc_thresh = -25

    min_slc_len = min_sentence_slc_len
    slc_thresh = setnence_paragraph_slc_thresh

    audio_chunks = split_on_silence(sound_file,
                                    # must be silent for at least half a second
                                    min_silence_len=min_slc_len,  # TODO : 500 is pretty good

                                    # consider it silent if quieter than -16 dBFS
                                    silence_thresh=slc_thresh  # TODO : -36 is pretty good
                                    )

    mid = time.time()
    print(mid - start)

    # Create dir splitAudio
    if os.path.exists("splitAudio"):
        shutil.rmtree("splitAudio")
    os.mkdir("splitAudio")

    for i, chunk in enumerate(audio_chunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk

        # Normalize the entire chunk.
        normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

        out_file = "splitAudio/chunk{:05d}.wav".format(i)
        print("exporting", out_file)
        normalized_chunk.export(out_file, format="wav")

    end = time.time()
    print(end - start)
    if pad:
        print("Padding is ON")
    # play_seq("splitAudio")
