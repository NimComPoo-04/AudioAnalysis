# We want to reduce noise on a shitstain

# Wideband Audio is 50–7,000 
# We are going to reduce everything thats not in that range

import numpy as np
import matplotlib.pyplot as plt
import wave

class Audio:
    def __init__(self, nchannels, fps, samplewidth, frames):
        self.nchannels = nchannels
        self.samplewidth = samplewidth
        self.fps = fps

        if samplewidth == 2:
            self.frames = np.frombuffer(frames, dtype=np.int16)
        elif samplewidth == 1:
            self.frames = np.frombuffer(frames, dtype=np.int8)
        else:
            raise ValueError("Incompatible Bullshit Man")


    def filter(self):
        fft = np.fft.fft(self.frames)
        freq = np.fft.fftfreq(len(self.frames), d = 1 / self.fps)

        # I don't fucking know man
        fft[(50 > np.abs(freq)) & (np.abs(freq) > 7000)] = 0

        self.frames = np.array(np.fft.ifft(fft).real, dtype=self.frames.dtype)


    def write(self, name):
        with wave.open(name, 'wb') as data:
            data.setnchannels(self.nchannels)
            data.setsampwidth(self.samplewidth)
            data.setframerate(self.fps)
            data.setnframes(len(self.frames))
            data.writeframes(self.frames)

    # we want to generate a spectrogram
    def draw_spectorgram(self, name):
        plt.show()

    def __repr__(self):
        return f'Audio Data: {self.nchannels} {self.samplewidth} {self.fps}';


def load_audio(name):
    with wave.open(name, 'rb') as data:
        n = data.getnchannels()
        f = data.getframerate()
        s = data.getsampwidth()
        d = data.readframes(data.getnframes())

        return Audio(n, f, s, d)
