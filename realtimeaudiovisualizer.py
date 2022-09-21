import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
from scipy import signal
import sys

# use this backend to display in separate Tk window
56
CHUNK = 1024 * 2                # samples per frame
FORMAT = pyaudio.paInt16        # audio format (bytes per sample?)
CHANNELS = 1                    # single channel for microphone
RATE = 44100                    # samples per second

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

def getpyaudio(testing):
    global CHUNK, FORMAT, CHANNELS, RATE

    # pyaudio class instance
    p = pyaudio.PyAudio()

    # get list of availble inputs
    info = p.get_host_api_info_by_index(0)
    inputdevice = 0
    if testing:
        inputdevice = 5
    else:
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

        inputdevice = input("Enter in the device you want to use:")

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

def runpyplot(testing):
    global CHUNK, FORMAT, CHANNELS, RATE

    # create matplotlib figure and axes
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1, figsize=(10, 5))
    
    # showing only the subplot
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

    # pyaudio class instance
    stream = getpyaudio(testing)

    # variable for plotting
    x = np.arange(0, 8 * CHUNK, 8)

    # create a line object with random data
    line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    line2, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    line3, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    line4, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)
    # line5, = ax.plot(x, np.random.rand(CHUNK), '-', lw=.5)

    # basic formatting for the axes
    ax.set_ylim(-128, 383)
    ax.set_xlim(0, 8 * CHUNK)
    TICK = 128
    plt.setp(ax, xticks=[0, CHUNK*2, 4 * CHUNK,8 * CHUNK], yticks=[-TICK*2,-TICK, TICK*0, TICK*1, TICK*2, TICK*4])

    # show the plot
    plt.show(block=False)

    print('stream started')

    # for measuring frame rate
    frame_count = 0
    start_time = time.time()
    fig.patch.set_visible(False)

    counter = 0
    while True:
        BASE = 64
        # binary data
        data = stream.read(CHUNK)
        
        data_np = np.frombuffer(data, dtype=np.int16)/500

        # semi-arbitrary decision for filters
        bandpass1 = bandpassfilter(data_np*2, 10,450, RATE)*3
        bandpass2 = bandpassfilter(data_np*2, 450, 700, RATE)*4
        bandpass3 = bandpassfilter(data_np*2, 700, 1500, RATE)*5
        bandpass4 = bandpassfilter(data_np*2, 1500, 5000, RATE)*6

        #Offsets for drawing to the screen
        bandpass1 -= BASE
        bandpass2 += BASE
        bandpass3 += BASE*3
        bandpass4 += BASE*5
        # data_np = (data_np*5) + BASE*6

        # add data to lines to draw them
        line.set_ydata(bandpass1)
        line2.set_ydata(bandpass2)
        line3.set_ydata(bandpass3)
        line4.set_ydata(bandpass4)

        # update figure canvas
        try:
            fig.canvas.draw()
            if counter % 2 == 0:
                fig.canvas.flush_events()
            frame_count += 1
            counter+=1

        except TclError:

            # calculate average frame rate
            frame_rate = frame_count / (time.time() - start_time)

            print('stream stopped')
            print('average frame rate = {:.0f} FPS'.format(frame_rate))
            break


if __name__=="__main__":
    testing = True if len(sys.argv) > 1 else False
    runpyplot(testing)