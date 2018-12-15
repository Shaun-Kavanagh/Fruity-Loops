# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import time
import Adafruit_MPR121.MPR121 as MPR121
import pygame
import pyaudio
import wave
import threading
# loop through stream and append audio chunks to frame array
#for ii in range(0,int((samp_rate/chunk)*record_secs)):
#    data = stream.read(chunk)
#    frames.append(data)


print('Adafruit MPR121 Capacitive Touch Sensor Test')

# Create MPR121 instance.
cap = MPR121.MPR121()

# Initialize communication with MPR121 using default I2C bus of device, and
# default I2C address (0x5A).  On BeagleBone Black will default to I2C bus 0.
if not cap.begin():
    print('Error initializing MPR121.  Check your wiring!')
    sys.exit(1)

# Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
# 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
#cap.begin(address=0x5B)

# Also you can specify an optional I2C bus with the bus keyword parameter.
#cap.begin(busnum=1)

# Main loop to print a message every time a pin is touched.
print('Press Ctrl-C to quit.')
last_touched = cap.touched()
record_state = True
is_recording = [False,False,False,False,False,False,False,False,False,False,False,False]
is_playing = [False,False,False,False,False,False,False,False,False,False,False,False]
my_thread_record = None
my_thread_play = None




def loop_record(x):
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 48000 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 120 # seconds to record
    dev_index = 2 # device index found by p.get_device_info_by_index(ii)
    file_array = ['test0.wav','test1.wav','test2.wav','test3.wav','test4.wav','test5.wav','test6.wav','test7.wav','test8.wav','test9.wav','test10.wav']
    wav_output_filename = file_array[x] # name of .wav file

    audio = pyaudio.PyAudio() # create pyaudio instantiation
    print("recording")
    frames = []

    #create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
    i = 0
    while is_recording[x]:
        print(i)
        data = stream.read(chunk)
        frames.append(data)
        i = i+1
    
    print("finished recording")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

def press_button_record(x):
    global is_recording
    global my_thread_record

    if not is_recording[x]:
        is_recording[x] = True
        my_thread_record = threading.Thread(target=loop_record, args=(x,))
        my_thread_record.start()

def press_button_stop(x):
    global is_recording
    global my_thread_record

    if is_recording[x]:
        is_recording[x] = False
        press_button_play(x)
        
        my_thread_record.join()

def press_button_play(x):
    global is_playing
    global my_thread_play

    if not is_playing[x]:
        is_playing[x] = True
        my_thread_play = threading.Thread(target=loop_play, args=(x,))
        my_thread_play.start()

def press_button_stop_play(x):
    global is_playing
    global my_thread_play

    if is_playing[x]:
        is_playing[x] = False
        my_thread_play.join()

    if (x==11):
        is_playing = [False,False,False,False,False,False,False,False,False,False,False,False]
    
    
       

def loop_play(x):
    while is_playing[x]:
        play_audio(x)
        
def play_audio(x):
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    
    SOUND_MAPPING = {
      0: '/home/pi/Adafruit_Python_MPR121/examples/test0.wav',
      1: '/home/pi/Adafruit_Python_MPR121/examples/test1.wav',
      2: '/home/pi/Adafruit_Python_MPR121/examples/test2.wav',
      3: '/home/pi/Adafruit_Python_MPR121/examples/test3.wav',
      4: '/home/pi/Adafruit_Python_MPR121/examples/test4.wav',
      5: '/home/pi/Adafruit_Python_MPR121/examples/test5.wav',
      6: '/home/pi/Adafruit_Python_MPR121/examples/test6.wav',
      7: '/home/pi/Adafruit_Python_MPR121/examples/test7.wav',
      8: '/home/pi/Adafruit_Python_MPR121/examples/test8.wav',
      9: '/home/pi/Adafruit_Python_MPR121/examples/test9.wav',
      10: '/home/pi/Adafruit_Python_MPR121/examples/test10.wav',
      11: '/home/pi/Adafruit_Python_MPR121/examples/test11.wav',
    }
    sounds = [0,0,0,0,0,0,0,0,0,0,0,0]

    for key,soundfile in SOUND_MAPPING.iteritems():
        sounds[key] =  pygame.mixer.Sound(soundfile)
        sounds[key].set_volume(1);
    global is_playing
    global my_thread_play
    file_array = ['test0.wav','test1.wav','test2.wav','test3.wav','test4.wav','test5.wav','test6.wav','test7.wav','test8.wav','test9.wav','test10.wav']
    print ("playing" + file_array[x])
    while is_playing[x]:
        sounds[x].play()
        #print ("playing" + file_array[x])
    
    



while True:
    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i
        # First check if transitioned from not touched to touched.
        if current_touched & pin_bit and not last_touched & pin_bit:
            print('{0} touched!'.format(i))
            if(i==0):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==1):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==2):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==3):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==4):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==5):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==6):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==7):
                press_button_stop_play(i)
                press_button_record(i)
                press_button_stop_play(i)
            elif(i==11):
                press_button_stop_play(i)
                
        # Next check if transitioned from touched to not touched.
        if not current_touched & pin_bit and last_touched & pin_bit:
            print('{0} released!'.format(i))
            if(i==0):
                press_button_stop(i)
            elif(i==1):
                press_button_stop(i)
            elif(i==2):
                press_button_stop(i)
            elif(i==3):
                press_button_stop(i)
            elif(i==4):
                press_button_stop(i)
            elif(i==5):
                press_button_stop(i)
            elif(i==6):
                press_button_stop(i)
            elif(i==7):
                press_button_stop(i)
    # Update last state and wait a short period before repeating.
    last_touched = current_touched
    time.sleep(0.1)


    # Alternatively, if you only care about checking one or a few pins you can
    # call the is_touched method with a pin number to directly check that pin.
    # This will be a little slower than the above code for checking a lot of pins.
    #if cap.is_touched(0):
    #    print('Pin 0 is being touched!')

    # If you're curious or want to see debug info for each pin, uncomment the
    # following lines:
    #print '\t\t\t\t\t\t\t\t\t\t\t\t\t 0x{0:0X}'.format(cap.touched())
    #filtered = [cap.filtered_data(i) for i in range(12)]
    #print('Filt:', '\t'.join(map(str, filtered)))
    #base = [cap.baseline_data(i) for i in range(12)]
    #print('Base:', '\t'.join(map(str, base)))
