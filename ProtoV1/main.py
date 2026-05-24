from rich import print

import librosa
import soundfile as sf
import tensorflow as tf
import kagglehub
import scipy
import pandas as pd
import numpy as np
import pyaudio
import seaborn as sns

import os
import sys

yamnet_model = None
yamnet_classes = None

audio_dataframe = None
audio_embeddings = None

def load_yamnet_model():
    global yamnet_model, yamnet_classes
    path = kagglehub.model_download("google/yamnet/tensorFlow2/yamnet")
    yamnet_model = tf.saved_model.load(path)
    class_map_path = f'{path}/assets/yamnet_class_map.csv'
    yamnet_classes = pd.read_csv(class_map_path)['display_name'].tolist()

def load_csv_file(file):
    return pd.read_csv(file)

def load_audio_file(audio_file):
    audio, _ = librosa.load(audio_file, sr=16000, mono=True)
    intervals = librosa.effects.split(y=audio, top_db=5)
    nospace = np.concat([ audio[a:b] for a, b in intervals ])
    return nospace

def execute_model(audio):
    score, embeddings, _ = yamnet_model(audio)
    return score, embeddings

if __name__ == '__main__':
    load_yamnet_model()
    audio_dataframe = load_csv_file('labels.csv')
    audio_dataframe['File Name'] = 'audios/'+audio_dataframe['File Name']
    audio_dataframe['Audio'] = pd.Series([load_audio_file(f) for f in audio_dataframe['File Name']])

    audio_embeddings = pd.DataFrame(columns=['Label', 'Scores', 'Embeddings'])

    for i in range(len(audio_dataframe)):
        audio = audio_dataframe.loc[i, 'Audio']
        label = audio_dataframe.loc[i, 'Label']

        score, embeddings = execute_model(audio)
        audio_embeddings = pd.concat([audio_embeddings, pd.DataFrame(embeddings)])

    #segments = load_audio()
    #print(segments)
