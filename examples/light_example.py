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
from plezmo.elements.plezmo_light import *

import utils

logger = Logger()

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
        traceback.print_exc()
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

    # Register event handlers
    try:
        # turn light ON
        logger.info("Turning on light in red color and 100 percent brightness")
        Light.turnOn(light_name, LightColor("#FF0000"), Percentage(100))
        time.sleep(5)
        # turn light OFF
        logger.info("Turning light off")
        Light.setState(light_name, LightState.OFF)
        time.sleep(2)
        # set light color, brightness and turn it on
        logger.info("Set color to blue, brightness to 10, and turning light on")
        Light.setColor(light_name, LightColor("#0000FF"))
        Light.setBrightness(light_name, Percentage(10))
        Light.setState(light_name, LightState.ON)
        time.sleep(5)
        logger.info("Fading in light with 100 percent brightness, red color.")
        # Fade in
        Light.fadeIn(light_name, Percentage(100), LightColor("#FF0000"), LightFadeSpeed.FAST)
        time.sleep(2)
        # Fade out
        logger.info("Fading out the light slowly")
        Light.fadeOut(light_name, LightFadeSpeed.SLOW)
        time.sleep(2)
        # Get brightness detected
        b = Light.getBrightness(light_name)
        logger.info("Brightness {}".format(b))
        # Get color detected
        c = Light.getColor(light_name)
        logger.info("Color {}".format(c))
        # Get state (ON/OFF)
        s = Light.getState(light_name)
        logger.info("State {}".format(s))
    except Exception as e:
        logger.error("Failed to run Light commands {}, ex {}".format(light_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(light_name)
        time.sleep(1)
        plezmoApi.close()

# Program starts here
if __name__ == "__main__":
    light_name = utils.extract_element_name()
    if light_name == None:
        logger.error("Light element name is mandatory, e.g. # python light_example.py Light")
    else:
        main(light_name)