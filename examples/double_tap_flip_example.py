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

# Demonstrates double tap and flip events handlers. These events are available for all Plezmo
# elements except Motor.

# Test needs 1 light element. You can user any other element also except Motor.
import time
import traceback

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_light import *
from plezmo.elements.plezmo_element import *

import utils

logger = Logger()

light_name = None

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init(light_name):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : light_name, "type": PlezmoElementType.LIGHT}]
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
        # Disconnect already connected elements
        for e in connectedElements:
            plezmoApi.disconnect(e["name"])
        return False

# Main logic of the program
def main(light_name):
    # Init bluetooth communication
    success = init(light_name)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    # Register event handlers and call methods of display sensor
    try:
        # setup double tap and flip event handlers
        Display.onDoubleTap(light_name, double_tap_handler)
        Display.onFlipEvent(light_name, flip_up_handler, Flip.UP)
        Display.onFlipEvent(light_name, flip_down_handler, Flip.DOWN)
        logger.info("Registered double tap and flip event handlers.")
        logger.info("Flip the element DOWN to turn the light off.")
        logger.info("Flip the element UP to turn the light off.")
        logger.info("Double tap on the element to see the colors change.")
        logger.info("Press control-c to stop the program...")
        # turn the light on by default
        Light.turnOn(light_name, LightColor("#FF0000"), Percentage(100))

        # start an infinite loop so that the program runs forever
        while True:
            time.sleep(1000)
    except Exception as e:
        logger.error("Failed to run display commands {}, ex {}".format(light_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(light_name)
        time.sleep(1)
        plezmoApi.close()

@PlezmoEventHandler
def double_tap_handler():
    logger.info("Showing color pattern")
    logger.info("Showing VIOLET color")
    Light.turnOn(light_name, LightColor("#9400D3"), Percentage(100))
    time.sleep(1)
    logger.info("Showing BLUE color")
    Light.turnOn(light_name, LightColor("#0000FF"), Percentage(100))
    time.sleep(1)
    logger.info("Showing GREEN color")
    Light.turnOn(light_name, LightColor("#00FF00"), Percentage(100))
    time.sleep(1)
    logger.info("Showing YELLOW color")
    Light.turnOn(light_name, LightColor("#FFFF00"), Percentage(100))
    time.sleep(1)
    logger.info("Showing ORANGE color")
    Light.turnOn(light_name, LightColor("#FF7F00"), Percentage(100))
    time.sleep(1)
    logger.info("Showing RED color")
    Light.turnOn(light_name, LightColor("#FF0000"), Percentage(100))
    time.sleep(1)

@PlezmoEventHandler
def flip_up_handler():
    logger.info("Turning on the light in RED color")
    Light.turnOn(light_name, LightColor("#FF0000"), Percentage(100))

@PlezmoEventHandler
def flip_down_handler():
    logger.info("Turning off the light")
    Light.setState(light_name, LightState.OFF)

# Program starts here
if __name__ == "__main__":
    light_name = utils.extract_element_name()
    if light_name == None:
        logger.error("Display element name is mandatory, e.g. # python double_tap_flip_example.py Display")
    else:
        main(light_name)
    quit()