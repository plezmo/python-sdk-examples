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

# This example is implementation of "Magic Wand" tutorial from plezmo app. Refer to this tutorial
# to create magic wand and lamp using story kits. Place the motion sensor in the wand and light in element
# in the lamp as indicated and start the example.
import sys
import time
import traceback

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_motion import *
from plezmo.elements.plezmo_light import *

import utils

logger = Logger()

light_name = None

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init(element_names):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : element_names["motion"], "type": PlezmoElementType.MOTION},
    {"name": element_names["light"], "type": PlezmoElementType.LIGHT}]

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
        #traceback.print_exc()
        # Disconnect already connected elements
        for e in connectedElements:
            plezmoApi.disconnect(e["name"])
        return False

# Main logic of the program
def main(element_names):
    global light_name
    # Init bluetooth communication
    success = init(element_names)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    motion_name = element_names["motion"]
    light_name = element_names["light"]
    # Register event handlers
    try:
        # set event handlers for left/right/front/back/flat tilt
        Motion.onTilt(motion_name, lelf_tilt_handler, Tilt.LEFT)
        Motion.onTilt(motion_name, right_tilt_handler, Tilt.RIGHT)
        Motion.onTilt(motion_name, front_tilt_handler, Tilt.FRONT)
        Motion.onTilt(motion_name, back_tilt_handler, Tilt.BACK)
        Motion.onFlat(motion_name, flat_handler)
        logger.info("Registered event handlers for BACK/FRONT/LEFT/RIGHT/FLAT tilts.")
        logger.info("Tilt the motion element in different directions to see the light element changes.")
        logger.info("Press control-c to stop the program...")

        # start an infinite loop so that the program runs forever
        while True:
            time.sleep(1000)

    finally:
        logger.info("Stopping the program...")
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(motion_name)
        time.sleep(1)
        plezmoApi.disconnect(light_name)
        time.sleep(1)
        plezmoApi.close()

@PlezmoEventHandler
def lelf_tilt_handler():
    logger.info("Turning on the light in RED color")
    Light.turnOn(light_name, LightColor("#FF0000"), Percentage(100))

@PlezmoEventHandler
def right_tilt_handler():
    logger.info("Turning on the light in GREEN color")
    Light.turnOn(light_name, LightColor("#00FF00"), Percentage(100))

@PlezmoEventHandler
def front_tilt_handler():
    logger.info("Turning on the light in BLUE color")
    Light.turnOn(light_name, LightColor("#0000FF"), Percentage(100))

@PlezmoEventHandler
def back_tilt_handler():
    logger.info("Turning on the light in YELLOW color")
    Light.turnOn(light_name, LightColor("#FFFF00"), Percentage(100))

@PlezmoEventHandler
def flat_handler():
    logger.info("Turning off the light")
    Light.setState(light_name, LightState.OFF)

def extract_element_names():
    motion_name = None
    light_name = None
    if len(sys.argv) < 3:
        return None
    else:
        motion_name = sys.argv[1]
        light_name = sys.argv[2]
        return {"motion": motion_name, "light": light_name}

# Program starts here
if __name__ == "__main__":
    element_names = extract_element_names()
    if element_names == None:
        logger.error("Motion and light element name is mandatory, e.g. # python magic_wand.py Motion Light")
    else:
        main(element_names)