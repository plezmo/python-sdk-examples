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

# This is an example program about how to use plezmo python API
# This program connects to a Plezmo Color Sensor, a Plezmo Motor.
# It sets up event handlers so that henever the color sensor detects
# GREEN color, the motor will be started. Whenever the colro sensor
# detects RED color, the motor will be stopped. The event handlers
# will get called repeatedly as long as the color sensor detects
# RED and GREEN colors

import time
import traceback
import sys

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_motor import MotorDirection, MotorRotation, MotorSpeed
from plezmo.elements.plezmo_color import ColorSensorColor

logger = Logger()

# All unhandled exceptions from event handlers will be directed to this handler
def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

motor_name = None

# Init bluetooth communication
def init(element_names):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : element_names["color"], "type": PlezmoElementType.COLOR},
    {"name": element_names["motor"], "type": PlezmoElementType.MOTOR}]

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
def main(element_names):
    global motor_name
    # Init bluetooth communication and connect to elements
    success = init(element_names)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    color_name = element_names["color"]
    motor_name = element_names["motor"]
    # Register event handlers
    try:
        # Event handler to call when color sensor detects GREEN color
        Color.onColorChange(color_name, green_handler, ColorSensorColor.GREEN)
        # Event handler to call when color sensor detects RED color
        Color.onColorChange(color_name, red_handler, ColorSensorColor.RED)
        # If this sleep is not added, program will terminate before events can be generated
        logger.info("Event handlers registered. Bring the RED/GREEN colors in front of the color element to see the motor start and stop.")
        time.sleep(20)
    except Exception as e:
        logger.error("Failed to run color commands {}, ex {}".format(color_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(color_name)
        time.sleep(1)
        plezmoApi.disconnect(motor_name)
        time.sleep(1)
        plezmoApi.close()

# Event handler whenever color sensor detects GREEN color
# Start motor when GREEN color is detected
@PlezmoEventHandler
def green_handler():
    global motor_name
    logger.info("Got green color change event, starting motor")
    Motor.start(motor_name, MotorSpeed.HIGH, MotorDirection.CLOCKWISE)

# Event handler whenever color sensor detects RED color
# Start motor when RED color is detected
@PlezmoEventHandler
def red_handler():
    global motor_name
    logger.info("Got red color change event, stopping motor")
    Motor.stop(motor_name)

def extract_element_names():
    motor_name = None
    color_name = None
    if len(sys.argv) < 3:
        return None
    else:
        motor_name = sys.argv[1]
        color_name = sys.argv[2]
        return {"motor": motor_name, "color": color_name}

# Program starts here
if __name__ == "__main__":
    element_names = extract_element_names()
    if element_names == None:
        logger.error("Motor and color element name is mandatory, e.g. # python motor_start_on_color_change_example.py Motor-A Color")
    else:
        main(element_names)