import numpy as np
import scipy
import wave
import matplotlib.pyplot as plt
import matplotlib

# load the whole sound
def load_sound(name):
    params = {}
    audio = None
    with wave.open(name, "rb") as f:
        params['number_of_channels'] = f.getnchannels()
        b = params['bytes_per_sample'] = f.getsampwidth()
        params['sample_rate'] = f.getframerate()
        n = params['number_of_samples'] = f.getnframes()
        audio = np.frombuffer(f.readframes(n), dtype=f'int{8 * b}')

    return params, audio


# converts the audio into overlapping block
# lets also take the STFT of the signal at this time aswell
def blockify_sound(params, audio, block_size):

    remaining = block_size - len(audio) % block_size
    if remaining != 0:
        audio = np.pad(audio, (0, remaining))

    blocks = audio.reshape((-1,block_size))
    count = len(audio) // block_size

    stft_factory = scipy.signal.ShortTimeFFT(
            scipy.signal.get_window('hann', block_size // 2 + 1),
            block_size // 4,
            params['sample_rate'])
    
    for i in range(count):
        if i % 2 == 0:
            yield blocks[i // 2], stft_factory.stft(blocks[i // 2])
        else:
            first_blk = blocks[i // 2][ block_size // 2 : block_size ]
            secnd_blk = blocks[i // 2 + 1][ : block_size // 2]
            blk = np.concat([first_blk, secnd_blk])
            yield blk, stft_factory.stft(blk)


def AV(x):
    return x.sum() / len(x)

def RSD(x):
    avg = AV(x)
    return np.sqrt(((x - avg) ** 2).sum() / len(x)) / avg

# Returns the power of Avarage amplitudes and Avarage Relative StdDev
def Amplitude(x):
    return AV(np.abs(x)), RSD(np.abs(x))

# Returns the spectral width
def SpectralWidth(f, threshold):
    w = (np.abs(f) > threshold).mean(axis=0)
    return AV(w), RSD(w)

# Low Frequency Power ()
def LowFrequencyPower(f, n):
    net = np.abs(f).sum(axis=0)
    thi = np.abs(f[:n]).sum(axis=0)
    l = thi/net
    return AV(l), RSD(l)

def HighFrequencyPower(f, n):
    net = np.abs(f).sum(axis=0)
    thi = np.abs(f[n:]).sum(axis=0)
    h = thi/net
    return AV(h), RSD(h)

def FundamentalFrequencies(f, threshold, sample_rate):
    where = np.argwhere(np.abs(f) > threshold)[:, 1]
    a = where * f.shape[0] / sample_rate 
    return a

def Harmonicity():
    pass

def main():
    params, audio = load_sound('penopticon.wav')
    for x, f in blockify_sound(params, audio, params['sample_rate']):
        print(Amplitude(x), SpectralWidth(f, 1100), LowFrequencyPower(f, 100), FundamentalFrequencies(f, 2000000, params['sample_rate']))

    #plt.plot(audio)
    #plt.show()

if __name__ == '__main__':
    matplotlib.use('WebAgg')
    print(plt.rcParams['backend'])
    
    main()
