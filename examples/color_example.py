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

# Tests functionality of light element
import time
import traceback

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_color import *

import utils

logger = Logger()

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init(color_name):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : color_name, "type": PlezmoElementType.COLOR}]
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
def main(color_name):
    # Init bluetooth communication
    success = init(color_name)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    # Register event handlers
    try:
        # Event handler to call when color sensor detects GREEN color
        Color.onColorChange(color_name, green_handler, ColorSensorColor.GREEN)
        # Event handler to call when color sensor detects RED color
        Color.onColorChange(color_name, red_handler, ColorSensorColor.RED)
        logger.info("Event handlers for color detection registered. Take the Color sensor in front of RED/GREEN color to see the event handlers working.")
        time.sleep(10)
        # Event handler to call when color sensor detects darkness
        Color.onLightEvent(color_name, darkness_handler, ColorSensorLightState.DARK)
        # Event handler to call when color sensor detects brightness
        Color.onLightEvent(color_name, brightness_handler, ColorSensorLightState.BRIGHT)
        logger.info("Event handlers darkness/brightness detection registered. Take the Color sensor to dark/bright locations to see the event handlers working.")
        time.sleep(10)

        comp = Color.getLightValueLux(color_name)
        logger.info("Light lux value is {}".format(comp))
        comp = Color.getLightComponentValueInLux(color_name, LightComponent.GREEN)
        logger.info("Green component is {}".format(comp))
        light = Color.getLightValuePercent(color_name)
        logger.info("Detected light value in percent is {}".format(light))
        logger.info("Checking getColor() functionality. Keep the color sensor facing any basic color")
        time.sleep(5)
        color = Color.getColor(color_name)
        logger.info("Detected color is {}".format(color))
        

        logger.info("Waiting for color change, change color in front of color element to different colors")
        Color.waitForColorChange(color_name)
        logger.info("Color changed")
        logger.info("Waiting for color to change to RED. Bring RED color in front of color element.")
        Color.waitForColorToChangeTo(color_name, ColorSensorColor.RED)
        logger.info("Color changed to RED")
        time.sleep(5)
        logger.info("Waiting for DARK. Take color element to dark location.")
        Color.waitForLightEvent(color_name, ColorSensorLightState.DARK)
        logger.info("It is dark")
        time.sleep(2)
    except Exception as e:
        logger.error("Failed to run Color commands {}, ex {}".format(color_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(color_name)
        time.sleep(1)
        plezmoApi.close()

# Event handler whenever color sensor detects GREEN color
@PlezmoEventHandler
def green_handler():
    logger.info("Got green color change event")

# Event handler whenever color sensor detects RED color
@PlezmoEventHandler
def red_handler():
    logger.info("Got red color change event")

# Event handler whenever color sensor detects darkness
@PlezmoEventHandler
def darkness_handler():
    logger.info("Got darkness event")

# Event handler whenever color sensor detects brightness
@PlezmoEventHandler
def brightness_handler():
    logger.info("Got brightness event")

# Program starts here
if __name__ == "__main__":
    color_name = utils.extract_element_name()
    if color_name == None:
        logger.error("Color element name is mandatory, e.g. # python color_example.py Color")
    else:
        main(color_name)