import os

import librosa
import numpy as np
import pandas as pd

# -- Read all the horns --

DatasetLocation = 'env/dataset/Dataset'
DatasetLocation_Train = 'env/dataset/hornbase_train.csv'
DatasetLocation_Test = 'env/dataset/hornbase_test.csv'

df_train = pd.read_csv(DatasetLocation_Train)
#print(df_train)

for k in range(len(df_train)):
    path = os.path.join(DatasetLocation, df_train.iloc[k]['file'])
    df_train.loc[k, 'path'] = path

audio = librosa.load(df_train.loc[0, 'path'])
print(audio)

stft = librosa.stft(audio, n_fft = 256
print(stft)

