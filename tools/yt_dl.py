#!/usr/local/bin/python3
from pytube import YouTube
import sys
import subprocess
import os
import shutil


def dl_yt_wav(link: str):
    yt = YouTube(link)

    # Title of video
    print("Title: ", yt.title) # Number of views of video
    print("Number of views: " ,yt.views) # Length of the video
    print("Length of video: " ,yt.length, "seconds") # Description of video
    print("Description: ", yt.description) #Rating
    print("Ratings: ", yt.rating)

    audio_streams = yt.streams.filter(only_audio=True)
    mp4_audio = audio_streams.filter(mime_type="audio/mp4")[0]
    in_audio = audio_streams.filter(mime_type="audio/webm")[0]

    if in_audio is None:
        in_audio = mp4_audio

    dl_dir = "youtube_dl"
    if os.path.exists(dl_dir):
        shutil.rmtree(dl_dir)

    in_audio.download(dl_dir)
    input_fname = os.path.join(dl_dir, os.listdir(dl_dir)[0])
    output_fname = os.path.basename(input_fname).replace(" ", "_").replace(".webm", "").replace(".mp4", "") + ".wav"
    if os.path.exists(output_fname):
        os.remove(output_fname)

    command = ['ffmpeg', '-nostats', '-loglevel', '0', '-i', input_fname, '-ac', '1', '-f', 'wav', output_fname]
    subprocess.run(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)

    shutil.rmtree(dl_dir)

    return os.path.abspath(output_fname)

# dl_yt_wav(sys.argv[1])
