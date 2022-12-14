# Real Time Audio Frequency Band Visualizer
### Project Description
This application allows you to take an input and separate the audio into pre-selected frequency bands:
- 10-350hz (Bottom Waveform)
- 450-700hz (2nd Waveform from Bottom)
- 800-1500hz (3rd Waveform from Bottom)
- 1750-5000hz (Top Waveform)

**As of now, you will need an input device feeding the data, such as an audio card or a microphone in order for this to work**

This is the first step in this project.

Now that we have processed the audio and have the relevant metadata, the next steps will be to use the information from the different frequency to control visual elements to make preset visuals react in real time to the audio being fed to the system

### Frequency Mode
<img src="https://media.giphy.com/media/Ne4ZFyWwZqDR2KBqQr/giphy.gif" width="800" height="500" /><br>

#### Youtube Clip
[See it On YouTube](https://youtu.be/WPhGKLTHv-c)

### Visual Mode
<img src="https://media.giphy.com/media/lafIYfHJZObd2d77kJ/giphy.gif" width="800" height="500" />

#### Youtube Clip
[See It On YouTube](https://youtu.be/QM9XnN9dogA)

# How to run
## Download Python and PIP
- [Python 3](https://www.python.org/downloads/)
- [Pip 3](https://pip.pypa.io/en/stable/installing/)
## Install Dependencies
```
pip3 install -r requirements
``` 
## Run script
```
python realtimeaudiovisualizer.py [mode=frequency,visual]
```
Once you start the script, it will advise you to pick the input you want to analyze:
```
Input Device id  0  -  Microsoft Sound Mapper - Input
Input Device id  1  -  Wave Link Stream (2- Elgato Wav
Input Device id  2  -  Digital Audio Interface (USB Di
Input Device id  3  -  Wave Link Monitor (2- Elgato Wa
Input Device id  4  -  Headset Microphone (4- Wireless
Input Device id  5  -  Line (AudioBox Go)
Input Device id  6  -  Mic In (2- Elgato Wave:3)
Input Device id  7  -  Wave Link MicrophoneFX (2- Elga
Enter in the device you want to use:
```
Enter in the number of the input device you want to analyze and then the window will pop up with the visualization