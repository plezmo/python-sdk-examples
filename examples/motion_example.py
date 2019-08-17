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

# Test motion sensor functionality
import time
import traceback

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_motion import *

import utils

logger = Logger()

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init(motion_name):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : motion_name, "type": PlezmoElementType.MOTION}]
    connectedElements = []
    try:
        # connect to elements one by one
        for e in elementList:
            plezmoApi.connect(e["name"], e["type"])
            # keep track of connected elements
            connectedElements.append(e["name"])
        return True
    except Exception as e:
        # Disconnect and stop program if connection to element fails
        logger.error("Failed to connect to element, ex {}".format(e))
        traceback.print_exc()
        # Disconnect already connected elements
        for e in connectedElements:
            plezmoApi.disconnect(e["name"])
        return False

# Main logic of the program
def main(motion_name):
    # Init bluetooth communication
    success = init(motion_name)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    # Register event handlers
    try:
        # set event handlers for left/right/front/back/flat tilt
        Motion.onTilt(motion_name, l_tilt_handler, Tilt.LEFT)
        Motion.onTilt(motion_name, r_tilt_handler, Tilt.RIGHT)
        Motion.onTilt(motion_name, f_tilt_handler, Tilt.FRONT)
        Motion.onTilt(motion_name, b_tilt_handler, Tilt.BACK)
        Motion.onFlat(motion_name, flat_handler)
        logger.info("Registered event handlers for BACK/FRONT/LEFT/RIGHT/FLAT tilts.")
        logger.info("Tilt the motion element in different directions to see the event handlers working.")
        time.sleep(20)

        Motion.onMotion(motion_name, move_handler, Movement.START)
        Motion.onMotion(motion_name, stop_handler, Movement.STOP)
        logger.info("Registered event handlers for START_MOVE/STOP_MOVE. Move the motion to see the event handlers working.")
        time.sleep(20)
        logger.info("Trying getAngle functionality. Tilt or move motion element to see the detected angle")
        time.sleep(5)
        for i in range(3):
            # Get detected angle
            logger.info("Please tilt the motion element...")
            a1 = Motion.getAngle(motion_name, Axis.LEFT_TO_RIGHT)
            logger.info("Angle for LEFT_TO_RIGHT axis is {}".format(a1))
            a2 = Motion.getAngle(motion_name, Axis.FRONT_TO_BACK)
            logger.info("Angle for FRONT_TO_BACK axis is {}".format(a2))
            time.sleep(2)

        # Get acceleration
        try:
            accl = Motion.getAccelerometerData(motion_name, Acceleration.X)
            logger.info("Accelerometer data for X axis is {}. This will work only if motion element has 3.4 version.".format(accl))
        except:
            logger.error("getAccelerometerData failed. Make sure that motion element has version 3.4.")

        logger.info("Waiting for BACK tilt event. Tilt the motion sensor back")
        Motion.waitForTilt(motion_name, Tilt.BACK)
        logger.info("Got tilt back wait event")
        time.sleep(2)

        logger.info("Waiting for start movement event. Move the motion sensor")
        Motion.waitForMotion(motion_name, Movement.START)
        logger.info("Got start event")
        time.sleep(2)

        logger.info("Waiting for flat event. Make the motion sensor flat")
        Motion.waitForFlat(motion_name)
        logger.info("Got flat event")
        time.sleep(2)
    except Exception as e:
        logger.error("Failed to run motion commands {}, ex {}".format(motion_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(motion_name)
        time.sleep(1)
        plezmoApi.close()

@PlezmoEventHandler
def l_tilt_handler():
    logger.info("Left tilt event handler:: Got left tilt event")

@PlezmoEventHandler
def r_tilt_handler():
    logger.info("Right tilt event handler:: Got right tilt event")

@PlezmoEventHandler
def f_tilt_handler():
    logger.info("Front tilt event handler:: Got front tilt event")

@PlezmoEventHandler
def b_tilt_handler():
    logger.info("Back tilt event handler:: Got back tilt event")

@PlezmoEventHandler
def flat_handler():
    logger.info("Flat event handler:: Got flat event")

@PlezmoEventHandler
def move_handler():
    logger.info("Move event handler:: Got move event")

@PlezmoEventHandler
def stop_handler():
    logger.info("Stop event handler:: Got stop event")

# Program starts here
if __name__ == "__main__":
    motion_name = utils.extract_element_name()
    if motion_name == None:
        logger.error("Motion element name is mandatory, e.g. # python motion_example.py Motion")
    else:
        main(motion_name)