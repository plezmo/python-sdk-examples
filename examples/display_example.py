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

# Tests functionality of display element.
# Test needs 1 display element
import time
import traceback

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_display import *
from plezmo.elements.plezmo_element import *

import utils

logger = Logger()

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init(display_name):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : display_name, "type": PlezmoElementType.DISPLAY}]
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
def main(display_name):
    # Init bluetooth communication
    success = init(display_name)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    # Register event handlers and call methods of display sensor
    try:
        # setup double tap and flip event handlers
        Display.onDoubleTap(display_name, double_tap_handler)
        Display.onFlipEvent(display_name, flip_up_handler, Flip.UP)
        Display.onFlipEvent(display_name, flip_down_handler, Flip.DOWN)
        logger.info("Registered double tap and flip event handlers. Double tap on display element or flip it up/down to see th event handlers in action")
        time.sleep(10)
        # show INBOX image on display
        logger.info("Showing INBOX image")
        Display.showImage(display_name, DisplayImage.INBOX)
        time.sleep(5)
        # clear display
        logger.info("Clearing display")
        Display.clearDisplay(display_name)
        time.sleep(2)
        # Show text on display
        logger.info("Showing text on display line 2 and alignment center")
        Display.showText(display_name, DisplayLine.TWO, TextAlignment.CENTER, "Hola!")
        time.sleep(5)
        # clear display
        logger.info("Clearing display")
        Display.clearDisplay(display_name)
        time.sleep(2)
        # set font size, text color
        Display.setFontSize(display_name, FontSize.MEDIUM)
        Display.setTextColor(display_name, DisplayBackground.RED)
        logger.info("Set font size to MEDIUM, text color to RED")
        Display.showText(display_name, DisplayLine.TWO, TextAlignment.CENTER, "RED!")
        time.sleep(5)
        # Set display background color
        logger.info("Painting background color to BLUE")
        Display.paintBackgroundColor(display_name, DisplayBackground.BLUE)
        time.sleep(5)
    except Exception as e:
        logger.error("Failed to run display commands {}, ex {}".format(display_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(display_name)
        time.sleep(1)
        plezmoApi.close()

@PlezmoEventHandler
def double_tap_handler():
    logger.info("Got double tap event")

@PlezmoEventHandler
def flip_up_handler():
    logger.info("Got flip up event")

@PlezmoEventHandler
def flip_down_handler():
    logger.info("Got flip down event")

# Program starts here
if __name__ == "__main__":
    display_name = utils.extract_element_name()
    if display_name == None:
        logger.error("Display element name is mandatory, e.g. # python display_example.py Display")
    else:
        main(display_name)
    quit()