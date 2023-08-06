# !usr/bin/env python
# coding=gbk
import pylab as pl
import matplotlib.pyplot as plt
import pylab
import numpy as np
from numpy.lib import stride_tricks
import wave
# PLOTTING FUNCTIONS for RP_EXTRACT features and Audio Waveforms
def plotmatrix(features, xlabel=None, ylabel=None):
    pylab.figure()
    pylab.imshow(features, origin='lower', aspect='auto', interpolation='nearest')
    if xlabel: plt.xlabel(xlabel)
    if ylabel: pylab.ylabel(ylabel)
    pylab.show()


def plotrp(features, reshape=True, rows=24, cols=60):
    if reshape:
        features = features.reshape(rows, cols, order='F')
    plotmatrix(features, 'Modulation Frequency Index', 'Frequency Band [Bark]')


def plotssd(features, reshape=True, rows=24, cols=7):
    if reshape:
        features = features.reshape(rows, cols, order='F')

    pylab.figure()
    pylab.imshow(features, origin='lower', aspect='auto', interpolation='nearest')
    pylab.xticks(range(0, cols), ['mean', 'var', 'skew', 'kurt', 'median', 'min', 'max'])
    pylab.ylabel('Frequency [Bark]')
    pylab.show()


def plotrh(hist, showbpm=True):
    xrange = range(0, hist.shape[0])
    plt.bar(xrange, hist)  # 50, normed=1, facecolor='g', alpha=0.75)

    # plt.ylabel('Probability')
    plt.title('Rhythm Histogram')
    if showbpm:
        mod_freq_res = 1.0 / (2 ** 18 / 44100.0)
        # print type(xrange)
        plotrange = range(1, hist.shape[0] + 1, 5)  # 5 = step
        bpm = np.around(np.array(plotrange) * mod_freq_res * 60.0, 0)
        pylab.xticks(plotrange, bpm)
        plt.xlabel('bpm')
    else:
        plt.xlabel('Mod. Frequency Index')
    plt.show()


def plotmono_waveform(samples, plot_width=6, plot_height=4):
    fig = plt.figure(num=None, figsize=(plot_width, plot_height), dpi=72, facecolor='w', edgecolor='k')

    if len(samples.shape) > 1:
        # if we have more than 1 channel, build the average
        samples_to_plot = samples.copy().mean(axis=1)
    else:
        samples_to_plot = samples

    channel_1 = fig.add_subplot(111)
    channel_1.set_ylabel('Channel 1')
    # channel_1.set_xlim(0,song_length) # todo
    channel_1.set_ylim(-1, 1)

    channel_1.plot(samples_to_plot)

    plt.show();
    plt.clf();


def plotstereo_waveform(samples, plot_width=6, plot_height=5):
    fig = plt.figure(num=None, figsize=(plot_width, plot_height), dpi=72, facecolor='w', edgecolor='k')

    channel_1 = fig.add_subplot(211)
    channel_1.set_ylabel('Channel 1')
    # channel_1.set_xlim(0,song_length) # todo
    channel_1.set_ylim(-1, 1)
    channel_1.plot(samples[:, 0])

    channel_2 = fig.add_subplot(212)
    channel_2.set_ylabel('Channel 2')
    channel_2.set_xlabel('Time (s)')
    channel_2.set_ylim(-1, 1)
    # channel_2.set_xlim(0,song_length) # todo
    channel_2.plot(samples[:, 1])

    plt.show();
    plt.clf();


def plot_waveform(samples, plot_width=6, plot_height=4):
    # mono wave data is either only 1dim in shape or has a 2dim shape with 1 channel only
    if (len(samples.shape) == 1) or (samples.shape[1] == 1):
        print "Plotting Mono"
        plotmono_waveform(samples, plot_width, plot_height)
    else:
        print "Plotting Stereo"
        plotstereo_waveform(samples, plot_width, plot_height)


""" scale frequency axis logarithmically """


def logscale_spec(spec, sr=44100, factor=20.):
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins - 1) / max(scale)
    scale = np.unique(np.round(scale))

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = np.sum(spec[:, scale[i]:], axis=1)
        else:
            newspec[:, i] = np.sum(spec[:, scale[i]:scale[i + 1]], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [np.mean(allfreqs[scale[i]:])]
        else:
            freqs += [np.mean(allfreqs[scale[i]:scale[i + 1]])]

    return newspec, freqs


def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(np.floor(frameSize / 2.0)), sig)
    # cols for windowing
    cols = np.ceil((len(samples) - frameSize) / float(hopSize)) + 1
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))

    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize),
                                      strides=(samples.strides[0] * hopSize, samples.strides[0])).copy()
    frames *= win

    return np.fft.rfft(frames)


def plotstft(samples, samplerate, binsize=2 ** 10, plotpath=None, colormap="jet", ax=None, fig=None, plot_width=6,
             plot_height=4, ignore=False):
    if ignore:
        import warnings

        warnings.filterwarnings('ignore')

    s = stft(samples, binsize)

    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel

    timebins, freqbins = np.shape(ims)

    if ax is None:
        fig, ax = plt.subplots(1, 1, sharey=True, figsize=(plot_width, plot_height))

    # ax.figure(figsize=(15, 7.5))
    cax = ax.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    # cbar = fig.colorbar(cax, ticks=[-1, 0, 1], cax=ax)
    # ax.set_colorbar()

    ax.set_xlabel("time (s)")
    ax.set_ylabel("frequency (hz)")
    ax.set_xlim([0, timebins - 1])
    ax.set_ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins - 1, 5))
    ax.set_xticks(xlocs, ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate])
    ylocs = np.int16(np.round(np.linspace(0, freqbins - 1, 10)))
    ax.set_yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()

    # plt.clf();
    b = ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate]
    return xlocs, b, timebins


def plotMonoWav(mono_wav_path):
    # -*- coding: utf-8 -*-

    # ��WAV�ĵ�
    f = wave.open(mono_wav_path, "rb")
    # ��ȡ��ʽ��Ϣ
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print nchannels, sampwidth, framerate, nframes
    # ��ȡ��������
    str_data = f.readframes(nframes)
    f.close()
    # ����������ת��Ϊ����
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, nchannels
    wave_data = wave_data.T
    time = np.arange(0, nframes) * (1.0 / framerate)
    # ���Ʋ���
    # pl.subplot(211)
    pl.plot(time, wave_data[0])
    # pl.subplot(212)
    # pl.plot(time, wave_data[1], c="g")
    pl.xlabel("time (seconds)")
    pl.show()

    return 0


def plotDuralWav(dural_wav_path):
    # ��WAV�ĵ�
    f = wave.open(dural_wav_path, "rb")
    # ��ȡ��ʽ��Ϣ
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print nchannels, sampwidth, framerate, nframes
    # ��ȡ��������
    str_data = f.readframes(nframes)
    f.close()
    # ����������ת��Ϊ����
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, nchannels
    wave_data = wave_data.T
    time = np.arange(0, nframes) * (1.0 / framerate)
    # ���Ʋ���
    pl.subplot(211)
    pl.plot(time, wave_data[0])
    pl.subplot(212)
    pl.plot(time, wave_data[1], c="g")
    pl.xlabel("time (seconds)")
    pl.show()

    return 0
