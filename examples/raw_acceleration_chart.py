# Copyright (c) 2019 Gunakar Pvt Ltd
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted (subject to the limitations in the disclaimer
# below) provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the Gunakar Pvt Ltd/Plezmo nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

#      * This software must only be used with Plezmo elements manufactured by
#      Gunakar Pvt Ltd.

#      * Any software provided in binary or object form under this license must not be
#      reverse engineered, decompiled, modified and/or disassembled.

# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


# Real-time charting of RAW Acceleration data from Motion sensor.
# This example requires a Python 3.7 setup with some basic libraries setup (see the imports below).
# A Motion sensor needs to be available for the experiment.

# A simple experiment setup to study the pendulum behavior with raw-acceleration data is as follows.
# Tie one end of a 2-3 meter thin thread to a Plezmo adapter such that a Motion sensor attached to
# this adapter will hang up-side-down when suspended by the thread. Our pendulum is ready!
# Tie the other end at a suitable place for a good 15-20 degree free swinging pendulum.
# Now, hold the attachment at a swing angle with the thread taught and start this experiment.
# As soon as the chart shows up, release the attachment (with the attached Motion sensor)
# without any extra jerks or force to start the swinging.

# When you want to end the experiment, press 'q' in the chart window.
# This will exit the program and dump a motion-raw-accel-data.csv data file for the session.

# You can do the same charting with any other acceleration experiments.
# Note that this script charts only the Z-axis and Resultant raw samples.
# You can edit the code below to suit your requirements.
# Note: A motion_inverted configuration variable is set to True in the script below to account for
# the inverted position of the motion element suspended as described above. Depending on how you
# setup your experiment you might want to set that to False.

# This program will connect with the specified Motion sensor
# and fetch a batch of RAW z-axis and resultant acceleration values.
# It will then update a chart with these against time.
# The program will continue fetching and showing these lines as long as 'q' is not pressed in the chart context.

import time
import traceback
import sys
import math
import pandas as pd
import matplotlib.animation as animation
import matplotlib.pyplot as plt

# Generic Plezmo SDK imports.
from plezmo import *
import plezmo.utils.logger as pzLogger
import plezmo as pz
import plezmo.elements.element_types as pzType
from plezmo.elements.plezmo_motion import *

# Configurations.
motion_inverted = True ## Correction for inverted swinging Motion element w.r.t resultant data
cfgsize = (14,6) # inches
width = 100 # data-points across the chart
ani_interval = 1 # msec update interval
OutFile = 'motion-raw-accel-data.csv'

# Globals.
x_data, y_data, y2_data = [], [], []  # x,y,y2 data arrays
g_paused = False
# Global time tracking variables
gTime = 0
rTime = 0

# Functions.
# Init bluetooth communication
def init(element_names):
    # Register global exception handler
    pz.registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [
        {"name" : element_names["motion"], "type": pzType.PlezmoElementType.MOTION},
    ]
    connectedElements = []
    try:
        # connect to elements one by one
        for e in elementList:
            pz.plezmoApi.connect(e["name"], e["type"])
            # keep track of connected elements
            connectedElements.append(e["name"])
        return True
    except Exception as e:
        # Disconnect and stop program if connection to element fails
        print(f'Err! Failed to connect to element, ex {e}')
        #traceback.print_exc()
        # Disconnect already connected elements
        for e in connectedElements:
            pz.plezmoApi.disconnect(e["name"])
        return False

def extract_element_names():
    motion_name = None
    if len(sys.argv) < 2:
        print('Error 1')
        return None
    else:
        motion_name = sys.argv[1]
        return {"motion": motion_name}

# All unhandled exceptions from event handlers will be directed to this handler
def globalExceptionHandler(e):
    print(f'Err! Got exception {e}')

# Generic 'keepalive' function used by all handlers that keep program running.
def mark_time():
    global gTime
    gTime = time.time()
def ref_time(set=False):
    global rTime
    if set is True:
        rTime = time.time()
    else:
        lt = time.time()
        return round((lt - rTime),6) # usec resolution

def keypress(event):
    global g_paused
    print(f'Keypress... {event.key}')
    if event.key == ' ': # SPACE controls pause -- TODO
        g_paused ^= True

def refresh(frame):
    global dataset, width, x_data, y_data, y2_data
    #print(f'Refresh> {dataset.shape}')

    if g_paused:
        print(f'Paused...')
        time.sleep(1) # slowdown animation checks
        return line, line2

   # pzLog.info(f'Fetching Motion Accl data...')
    rows = []
    for i in range(5):
		# For the Pendulum experiment we are looking at the Z-axis and Resultant data
        z = Motion.getAccelerometerData(motion_name, Acceleration.Z)
        r = Motion.getAccelerometerData(motion_name, Acceleration.RESULTANT)
        t = ref_time()
        #print(f' {i:3} {t:10.3f} {z:10} {r:10}')
        row = [ t, -z if motion_inverted else z, r]
        rows.append(row)

    dataset = pd.concat([dataset, pd.DataFrame(rows, columns=['t','z','r'])])
   
    if (dataset.shape[0] < width):
        x_data = list(dataset['t'])
        y_data = list(dataset['z'])
        y2_data = list(dataset['r'])
    else:
        x_data = list(dataset['t'][-width:])
        y_data = list(dataset['z'][-width:])
        y2_data = list(dataset['r'][-width:])

    line.set_data(x_data, y_data)
    line2.set_data(x_data, y2_data)

    fig.gca().relim()
    fig.gca().autoscale_view()
    return line, line2

# Handlers that keep the program running.
@pz.PlezmoEventHandler
def move_handler():
    pzLog.info(f'  {motion_name} moved ...')
    return mark_time()
@pz.PlezmoEventHandler
def stop_handler():
    pzLog.info(f'  {motion_name} STOP received.')
    return mark_time()
@pz.PlezmoEventHandler
def l_tilt_handler():
    pzLog.info(f'  {motion_name} Left tilt')
    return mark_time()
@pz.PlezmoEventHandler
def r_tilt_handler():
    pzLog.info(f'  {motion_name} Right tilt')
    return mark_time()
@pz.PlezmoEventHandler
def f_tilt_handler():
    pzLog.info(f'  {motion_name} Front tilt')
    return mark_time()
@pz.PlezmoEventHandler
def b_tilt_handler():
    pzLog.info(f'  {motion_name} Back tilt')
    return mark_time()
@pz.PlezmoEventHandler
def flat_handler():
    pzLog.info(f'  {motion_name} Flat.')
    return mark_time()

# Main.
pzLog = pzLogger.Logger()
pzLog.info(f'Begin.')
element_names = extract_element_names()
if element_names is None:
    pz.plezmoApi.close()
    print(f'Err! Need one argument <Motion element>')
    exit(1)
pzLog.info(f'Looking for: {element_names}')

# Init bluetooth communication and connect to elements
retval = init(element_names)
if not retval:
    pz.plezmoApi.close()
    print(f'Err! Could not connect to all the required elements!')
    exit(0)

motion_name = element_names["motion"]

# Register event handlers in a try-except-finally form.
try:
    pz.Motion.onMotion(motion_name, move_handler, Movement.START)
    pz.Motion.onMotion(motion_name, stop_handler, Movement.STOP)
    pz.Motion.onTilt(motion_name, l_tilt_handler, Tilt.LEFT)
    pz.Motion.onTilt(motion_name, r_tilt_handler, Tilt.RIGHT)
    pz.Motion.onTilt(motion_name, f_tilt_handler, Tilt.FRONT)
    pz.Motion.onTilt(motion_name, b_tilt_handler, Tilt.BACK)

    dataset = pd.DataFrame(columns=[i for i in range(3)])
    dataset.rename(columns={0:'t',1:'z',2:'r'}, inplace=True)

    # Setup Animated Charting.
    fig = plt.figure(figsize=cfgsize)
    fig.canvas.mpl_connect('key_press_event', keypress)
    line,line2 = plt.plot(x_data, y_data, 'r-',  x_data, y2_data, 'b-',  linewidth=1)
    plt.legend([line,line2], ['z-axis','Resultant'])
    plt.title('Charting RAW Acceleration from Motion sensor')
    plt.xlabel('Time (secs)')
    plt.ylabel('Accel (mm/sq_sec)')
    ref_time(True)
    ani = animation.FuncAnimation(fig, refresh, interval=ani_interval)
    plt.tight_layout()
    plt.show()
    dataset.reset_index(inplace=True, drop=True)
    dataset.to_csv(OutFile, encoding='utf-8')

except Exception as e:
    print(f'Err! Failed to run commands: ex {e}')
    #traceback.print_exc()

finally:
    pzLog.info(f'End.')
    # Program completed, disconnect elements and quit
    pz.plezmoApi.disconnect(motion_name)
    time.sleep(1)
    pz.plezmoApi.close()
    exit(0)
