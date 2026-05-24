import os
import sys
import io
import tempfile
import re

import json

import uvicorn

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import numpy as np
import soundfile as sf
import librosa

############################################################

import kagglehub
import tensorflow as tf
from tensorflow.keras import models 
import pandas as pd

# load the yamnet model

yamnet_model_download = kagglehub.model_download('google/yamnet/tensorFlow2/yamnet')
yamnet = tf.saved_model.load(yamnet_model_download)

classes_path = os.path.join(yamnet_model_download, 'assets/yamnet_class_map.csv')
classes = pd.read_csv(classes_path)

############################################################

# Cross-Origin Request change in production

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/mfcc')
async def get_mfcc(file : UploadFile = File()):
    with tempfile.NamedTemporaryFile(suffix='.webm') as foo:
        foo.write(file.file.read())
        foo.flush()

        audio_data, sample_rate = librosa.load(foo.name, sr=16000)
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=12)

        return mfcc.tolist()

def check_pattern(a):
    return bool(re.match('horn|alarm|buzz|siren|music', a.lower()))

@app.post('/recognize')
async def get_predictions(file : UploadFile = File()):
    with tempfile.NamedTemporaryFile(suffix='.webm') as foo:
        foo.write(file.file.read())
        foo.flush()

        audio_data, sample_rate = librosa.load(foo.name, sr=16000)
        scores, embeddings, spectogram = yamnet(audio_data)

        scores = scores.numpy()

        timestamps = pd.DataFrame(np.arange(0, len(embeddings)/2, 0.5))
        top_5_scores = pd.DataFrame(np.sort(scores, axis=1)[:,-5:])
        top_5_labels = pd.DataFrame(scores.argsort(axis=1)[:,-5:]).apply(lambda a: pd.Series([classes.loc[k, 'display_name'] for k in a]), axis=1)
        predicted_horns = pd.DataFrame(np.array([np.vectorize(check_pattern)(top_5_labels[i]) for i in top_5_labels.columns]).any(axis=0))

        val0 = timestamps.to_dict(orient='split')
        val1 = top_5_scores.to_dict(orient='split')
        val2 = top_5_labels.to_dict(orient='split')
        val3 = predicted_horns.to_dict(orient='split')

        return {'timestamps': val0, 'scores' : val1, 'labels' : val2, 'predicted_horns': val3, 'spectogram': spectogram}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)

