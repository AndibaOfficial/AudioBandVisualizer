import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
from matplotlib.patches import Ellipse
from scipy import signal
import sys

# use this backend to display in separate Tk window
56
CHUNK = 1024 * 2                # samples per frame
FORMAT = pyaudio.paInt16        # audio format (bytes per sample?)
CHANNELS = 1                    # single channel for microphone
RATE = 44100                    # samples per second
BASE = 64

FREQUENCY_MAP = {   "LOW":55,
                    "LOWMID":20,
                    "MID":10,
                    "HIGH":55}

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
    numdevices = info.get('deviceCount')
    if testing:
        for i in range(0, numdevices):
            if p.get_device_info_by_host_api_device_index(0, i).get('name') == "Line (AudioBox Go)" and testing:
                inputdevice = i
                break
    else:
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

def getscalar(data, FREQ):
    global CHUNK, FORMAT, CHANNELS, RATE, BASE, FREQUENCY_MAP
    scalar = np.max(data) if np.max(data) > FREQUENCY_MAP[FREQ] else 0
    return scalar

def getlowfreqellipses(data):
    global CHUNK, FORMAT, CHANNELS, RATE, BASE
    color = 'r'
    SCALE = 5
    scalar = getscalar(data,"LOW")
    return Ellipse(( CHUNK, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color), Ellipse(( CHUNK*7, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color)

def getlowmidfreqellipses(data):
    global CHUNK, FORMAT, CHANNELS, RATE, BASE
    color = 'b'
    SCALE = 7
    scalar = getscalar(data,"LOWMID")
    return Ellipse(( CHUNK*2, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color), Ellipse(( CHUNK*6, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color)

def getmidfreqellipses(data):
    global CHUNK, FORMAT, CHANNELS, RATE, BASE
    color = 'w'
    SCALE = 5
    scalar = getscalar(data,"MID")
    return Ellipse(( CHUNK*3, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color), Ellipse(( CHUNK*5, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color)

def gethighfreqellipses(data):
    global CHUNK, FORMAT, CHANNELS, RATE, BASE
    color = 'g'
    SCALE = 3
    scalar = getscalar(data,"HIGH")
    return Ellipse(( CHUNK*4, BASE*2), scalar*SCALE,scalar*SCALE, fc=color, ec=color)

def runpyplot(testing, mode="frequency"):
    global CHUNK, FORMAT, CHANNELS, RATE, BASE
    TICK = 128
    # create matplotlib figure and axes
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1, figsize=(15, 5))
    
    # showing only the subplot
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

    # pyaudio class instance
    stream = getpyaudio(testing)

    # variable for plotting
    x = np.arange(0, 8 * CHUNK, 4)
    line = None
    line2 = None
    line3 = None
    line4 = None

    if mode == "frequency":
        # create a line object with random data
        line, = ax.plot(x, np.random.rand(CHUNK*2), '-', lw=.5)
        line2, = ax.plot(x, np.random.rand(CHUNK*2), '-', lw=.5)
        line3, = ax.plot(x, np.random.rand(CHUNK*2), '-', lw=.5)
        line4, = ax.plot(x, np.random.rand(CHUNK*2), '-', lw=.5)
    
    # basic formatting for the axes
    ax.set_ylim(-128, 383)
    ax.set_xlim(0, 8 * CHUNK)
    plt.setp(ax, xticks=[0, CHUNK*2, 4 * CHUNK,8 * CHUNK], yticks=[-TICK*2,-TICK, TICK*0, TICK*1, TICK*2, TICK*4])

    # show the plot
    plt.show(block=False)

    print('stream started')

    # for measuring frame rate
    frame_count = 0
    start_time = time.time()
    fig.patch.set_visible(False)

    while True:
        # binary data
        data = stream.read(CHUNK)
        data2 = stream.read(CHUNK)
        
        data_np = np.concatenate((np.frombuffer(data, dtype=np.int16)/500,
                                    np.frombuffer(data2, dtype=np.int16)/500))

        # semi-arbitrary decision for filters
        bandpass1 = bandpassfilter(data_np*2, 10,350, RATE)*3
        bandpass2 = bandpassfilter(data_np*2, 450, 700, RATE)*3
        bandpass3 = bandpassfilter(data_np*2, 800, 1500, RATE)*4
        bandpass4 = bandpassfilter(data_np*2, 1750, 5000, RATE)*5

        e1,e2,e3,e4,e5,e6,e7 = None,None,None,None,None,None,None

        if mode == "visual":
            e1, e2 = getlowfreqellipses(bandpass1)
            ax.add_patch(e1)
            ax.add_patch(e2)

            e3, e4 = getlowmidfreqellipses(bandpass2)
            ax.add_patch(e3)
            ax.add_patch(e4)

            e5, e6 = getmidfreqellipses(bandpass3)
            ax.add_patch(e5)
            ax.add_patch(e6)

            e7= gethighfreqellipses(bandpass4)
            ax.add_patch(e7)

        if mode == "frequency":
            #Offsets for drawing to the screen
            bandpass1 -= BASE
            bandpass2 += BASE
            bandpass3 += BASE*3
            bandpass4 += BASE*5
            data_np = (data_np*5) + BASE*6

            # add data to lines to draw them
            line.set_ydata(bandpass1)
            line2.set_ydata(bandpass2)
            line3.set_ydata(bandpass3)
            line4.set_ydata(bandpass4)


        # update figure canvas
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
            if mode == "visual":
                e1.remove()
                e2.remove()
                e3.remove()
                e4.remove()
                e5.remove()
                e6.remove()
                e7.remove()

            frame_count += 1

        except TclError:

            # calculate average frame rate
            frame_rate = frame_count / (time.time() - start_time)

            print('stream stopped')
            print('average frame rate = {:.0f} FPS'.format(frame_rate))
            break


if __name__=="__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if not mode:
        raise Exception("""Must Select a mode! re-run and prpvide either 'frequency' or 'visual' as the second CLI Argument.
        for example: py realtimeaudiovisualizer.py frequency""")
    testing = sys.argv[2] if len(sys.argv) > 2 else None
    if testing:
        print(f"Running in Test Mode. Mode Selected: {mode}")
    else:
        print(f"Mode Selected: {mode}")
    runpyplot(testing, mode)