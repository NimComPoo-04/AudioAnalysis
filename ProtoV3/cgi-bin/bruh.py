#!/home/nimcompoo/Code/AudioAnalysis/env/bin/python

import sys
import cgi
import cgitb
import os
import io
import tempfile
import json

import numpy as np
import librosa

cgitb.enable()

print('Content-Type: text/plain\n')

form = cgi.FieldStorage()

if 'filename' in form:
    file_item = form.getlist('filename')
    data = file_item[0]

    with tempfile.NamedTemporaryFile() as file:
        file.write(data)
        audio_data, sr = librosa.load(file.name, sr=16000)

        mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=12)

        print(json.dumps(mfcc.tolist()), sep='\n')
