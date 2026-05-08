import sys
import numpy as np
import scipy
import wave
import matplotlib.pyplot as plt
import matplotlib
import sklearn as sk
import seaborn as sns

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


# Don't know how to calculate Fundamental Frequencies so going to ignore this for now.
'''
def FundamentalFrequencies(f, threshold, sample_rate):
    where = np.argwhere(np.abs(f) > threshold)[:, 1]
    a = where * f.shape[0] / sample_rate 
    return a

def Harmonicity():
    pass
'''

def main():
    params, audio = load_sound(sys.argv[1])

    feature_tensor = []

    for x, f in blockify_sound(params, audio, params['sample_rate']):
        feature_vector = np.array([*Amplitude(x), *SpectralWidth(f, 1100), *LowFrequencyPower(f, 100), *HighFrequencyPower(f, 1000)])
        #feature_vector = np.array([*SpectralWidth(f, 1100), *LowFrequencyPower(f, 100), *HighFrequencyPower(f, 1000)])
        feature_tensor.append(feature_vector)

    feature_tensor = np.array(feature_tensor)
    print(feature_tensor, feature_tensor.shape, feature_tensor.dtype)

    scaler = sk.preprocessing.StandardScaler()
    x_scaled = scaler.fit_transform(feature_tensor)
    pca = sk.decomposition.PCA(n_components=2)
    x_pca = pca.fit_transform(x_scaled)

    print('PCA shape: ', x_pca.shape)

    # Sklearn thingburger
    kmeans = sk.cluster.KMeans(n_clusters=5, random_state=0, n_init="auto").fit(x_pca)
    cats = kmeans.predict(x_pca)
    print(cats)

    #print(kmeans.labels_)
    #print(kmeans.cluster_centers_)

    sns.scatterplot(x=x_pca.T[0], y=x_pca.T[1], hue=cats)
    plt.title('Wit Loundness Information')
    plt.savefig('soundPCM.png')

if __name__ == '__main__':
    matplotlib.use('WebAgg')
    print(plt.rcParams['backend'])
    
    main()
