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

import time
import traceback
import sys

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_motor import MotorDirection, MotorRotation, MotorSpeed
from plezmo.elements.plezmo_color import ColorSensorColor

import utils

logger = Logger()

# All unhandled exceptions from event handlers will be directed to this handler
def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

motor_name = None

# Init bluetooth communication
def init(motor_name):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name": motor_name, "type": PlezmoElementType.MOTOR}]

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
def main(motor_name):
    # Init bluetooth communication and connect to elements
    success = init(motor_name)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    # Register event handlers
    try:
        # Event handler to call when motor stalls
        Motor.onStall(motor_name, stall_handler)
        logger.info("Starting motor with 50 RPM in CLOCKWISE direction")
        Motor.startWithRPM(motor_name, 50, MotorDirection.CLOCKWISE)
        time.sleep(5)
        logger.info("Stopping motor")
        Motor.stop(motor_name)
        time.sleep(2)
        logger.info("Starting motor with 50 RPM in ANTICLOCKWISE direction")
        Motor.startWithRPM(motor_name, 50, MotorDirection.ANTICLOCKWISE)
        time.sleep(5)
        # Rotate motor one turn in clockwise direction
        logger.info("Rotating motor finite rotations (ONE turn) in CLOCKWISE direction")
        Motor.rotate(motor_name, MotorRotation.ONE, MotorDirection.CLOCKWISE)
        time.sleep(2)
        # Start motor at HIGH speed in clockwise direction, let it run for 5 seconds then stop
        logger.info("Starting motor at HIGH speed in CLOCKWISE direction")
        Motor.start(motor_name, MotorSpeed.HIGH, MotorDirection.CLOCKWISE)
        time.sleep(5)
        logger.info("Stopping motor")
        Motor.stop(motor_name)
    except Exception as e:
        logger.error("Failed to run motor commands {}, ex {}".format(motor_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(motor_name)
        time.sleep(1)
        plezmoApi.close()

# Event handler whenever motor stalls
@PlezmoEventHandler
def stall_handler():
    logger.info("Got motor stall event")

# Program starts here
if __name__ == "__main__":
    motor_name = utils.extract_element_name()
    if motor_name == None:
        logger.error("Motor element name is mandatory, e.g. # python motor_example.py Motor-Kit11A")
    else:
        main(motor_name)