"""
Notebook for streaming data from a microphone in realtime
audio is captured using pyaudio
then converted from binary data to ints using struct
then displayed using matplotlib
if you don't have pyaudio, then run
>>> pip install pyaudio
note: with 2048 samples per chunk, I'm getting 20FPS
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
from scipy import signal

# use this backend to display in separate Tk window
56

# VARS CONSTS:
_VARS = {'window': False,
         'stream': False,
         'audioData': np.array([])}

def butter_lowpass(cutoff, fs, order=9):
    return signal.butter(order, cutoff, fs=fs, btype='low', analog=False)

def lowpassfilter(data, cutoff, fs, order=9):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y =  signal.lfilter(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=3):
    return signal.butter(order, [lowcut, highcut], fs=fs, btype='band')

def bandpassfilter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    b, a = signal.normalize(b,a)
    y = signal.lfilter(b, a, data)
    return y


def getpyaudio():
    CHUNK = 1024 * 2                # samples per frame
    FORMAT = pyaudio.paInt16        # audio format (bytes per sample?)
    CHANNELS = 1                    # single channel for microphone
    RATE = 44100                    # samples per second

    # pyaudio class instance
    p = pyaudio.PyAudio()

    # get list of availble inputs
    info = p.get_host_api_info_by_index(0)
    inputdevice = 0
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            if p.get_device_info_by_host_api_device_index(0, i).get('name') == "Line (AudioBox Go)":
                inputdevice = i


    # stream object to get data from microphone (currently using line in connected to midi controller)
    stream = p.open(
        input_device_index=int(inputdevice),
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK
    )
    return stream

def runpyplot():
    # constants
    CHUNK = 1024 * 2                # samples per frame
    RATE = 44100                    # samples per second

    # create matplotlib figure and axes
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1, figsize=(15, 7))

    # pyaudio class instance
    stream = getpyaudio()

    # variable for plotting
    x = np.arange(0, 4 * CHUNK, 4)

    # create a line object with random data
    line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    line2, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    line3, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    line4, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)

    # basic formatting for the axes
    ax.set_title('AUDIO WAVEFORM')
    ax.set_xlabel('samples')
    ax.set_ylabel('volume')
    ax.set_ylim(-128, 383)
    ax.set_xlim(0, 4 * CHUNK)
    plt.setp(ax, xticks=[0, CHUNK*2, 4 * CHUNK], yticks=[-128, 0, 128, 383])

    # show the plot
    plt.show(block=False)

    print('stream started')

    # for measuring frame rate
    frame_count = 0
    start_time = time.time()
    fig.patch.set_visible(False)

    while True:
        BASE = 64
        # binary data
        data = stream.read(CHUNK)
        
        data_np = np.frombuffer(data, dtype=np.int16)/500
        
        # semi-arbitrary decision for filters
        bandpass1 = bandpassfilter(data_np*2, 10,450, RATE)*3
        bandpass2 = bandpassfilter(data_np*2, 450, 700, RATE)*4
        bandpass3 = bandpassfilter(data_np*2, 700, 1500, RATE)*5
        bandpass4 = bandpassfilter(data_np*2, 2000, 5000, RATE)*6

        #Offsets for drawing to the screen
        bandpass1 -= BASE
        bandpass2 += BASE
        bandpass3 += BASE*2
        bandpass4 += BASE*4

        # add data to lines to draw them
        line.set_ydata(bandpass1)
        line2.set_ydata(bandpass2)
        line3.set_ydata(bandpass3)
        line4.set_ydata(bandpass4)

        # update figure canvas
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
            frame_count += 1

        except TclError:

            # calculate average frame rate
            frame_rate = frame_count / (time.time() - start_time)

            print('stream stopped')
            print('average frame rate = {:.0f} FPS'.format(frame_rate))
            break

runpyplot()