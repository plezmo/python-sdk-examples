# Introduction 
This package provides python interface for connecting to and programming Plezmo elements. This package requires python 3.7. SDK does not yet support element administration (upgrades, rename, custom file transfer). Users are advised to use Plezmo app for such purposes. For more information about Plezmo, visit https://www.plezmo.com.

# Requirements
+ Plezmo Wireless Adapter
+ Plezmo Elements
+ Python 3.7

# Supported Operating Systems
+ Windows 7 and 10
+ MacOS

# Installation

## Install plezmo

```python
pip install plezmo
```

Verify that the package is installed by running 'pip show plezmo'. It should show package information.

# Running examples

1. Clone repository https://github.com/plezmo/python-sdk-examples
2. Examples are present in directory 'examples'
2. All examples accept Plezmo element name as command line input.
3. Examples can be run as 'python test_display.py Display'
4. Before running the example make sure that the elements are woken up and Plezmo wireless adapter is plugged in.
5. This will print commands getting executed and corresponding actions can be seen on Plezmo elements.

Complete API documentation is available at https://plezmo.com/pythonsdk.

# Using plezmo package

New functionality for Color, Music and Motion element is available only with firmware version 3.4. Elements can be upgraded using Plezmo App. If the elements are not upgraded, following functions will fail.

Motion.getAccelerometerData()
Music.playAudioAndContinue()
Color.getLightComponentValueInLux()

If the elements are not upgraded, these functions need to be commnted out from the examples.

## Importing package

```python
import plezmo
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_color import *
```

First line results in importing plezmo package. It also initializes BLE communication. 'plezmo' package requires Plezmo Wireless Adapter to be plugged in. When importing if the adapter is not plugged in following error is displayed

*2019-08-09 11:35:18,473 2864 ERROR Plezmo wireless adapter not found*

If you see this error, make sure that Plezmo Wireless Adapter is plugged in. Also, make sure that the Plezmo app is not running on the same machine as it will otherwise own the adapter and open will fail.

Remaining two lines in the code are needed to connect to specific Plezmo element.

## Connecting to elements

```python
try:
    # connect to the element
    plezmoApi.connect("Color", PlezmoElementType.COLOR)
    return True
except Exception as e:
    logger.error("Failed to connect to element, ex {}".format(e))
    return False
```
plezmoApi object is available as part of plezmo package. 

First argument to **connect()** function is the element name. You can change it appropriately if your element name is different.

Second argument is the type of element to connect to. Available element types are present in enum PlezmoElementType.

Element connection can fail due to various reasons

1. Element is not woken up
2. Element name is incorrect
3. Element type is incorrect
4. Element is already connected to some other instance of SDK or Plezmo app itself.
5. Element is not in BLE range of the adapter.

In such cases **connect()** function will raise an exception. This exception needs to be handled appropriately.

## Interacting with the elements

### Sending commands to the element

Example of a command for Color element is "Get color in front of the element". This command can be used the the program as

```python
col = Color.getColor("Color") # Change element name if needed
print("Color detected is {}".format(col))
```

Color.getColor() command returns the detected color in hex format. Sample output of above two lines can be as follows

*Color detected is #FF0000*

### Handling events from the element

Example of events for Color element are "Change in deteted color", "Change in detected brightness". These events are generated by the element as and when the changes are detected. If such events are to be tapped, an event handler needes to be provided. Event handler is a normal python function. Example event handler that is executed when the Color element element detects **Red**  color is as follows

```python
# Event handler whenever color sensor detects RED color
@PlezmoEventHandler
def red_handler():
    logger.info("Got red color change event")

try:
    # Event handler to call when color sensor detects RED color
    Color.onColorChange("Color", red_handler, ColorSensorColor.RED)
except Exception as e:
    logger.error("Failed to run color commands {}, ex {}".format("Color", e))
```

At a time different events handlers can be registered for different venets of an element. For more details about how events handlers can be used, you can take a look at example **test_motor_start_on_color_change.py**.

It is a good practice to enclose plezmo commands within a try...except block for better error handling.

# Disconnecting the element

Elements can be disconnected using **disconnect()** method

```python
plezmoApi.disconnect("Color") # Change element name if needed
```
# Uninitializing plezmo
When the user programs terminates, it is important to unintialize BLE communication. This is done by calling **close()** function.

```python
plezmoApi.close()
```

# Complete program
Following python program uses two elements, a **Color** and a **Motor** element. The program handles events where Color sensor detects *red* and *green* color. When green is detected the Motor is started, when Red color is detected, the motor is stopped.

```python
# This is an example program about how to use plezmo python API
# This program connects to a Plezmo Color Sensor, a Plezmo Motor.
# It sets up event handlers so that henever the color sensor detects
# GREEN color, the motor will be started. Whenever the color sensor
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

# Init bluetooth communication
def init():
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : "Color", "type": PlezmoElementType.COLOR},
    {"name": "Motor-A", "type": PlezmoElementType.MOTOR}]

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
def main():
    # Init bluetooth communication and connect to elements
    success = init()
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    # Register event handlers
    try:
        # Event handler to call when color sensor detects GREEN color
        Color.onColorChange("Color", green_handler, ColorSensorColor.GREEN)
        # Event handler to call when color sensor detects RED color
        Color.onColorChange("Color", red_handler, ColorSensorColor.RED)
        # If this sleep is not added, program will terminate before events can be generated
        time.sleep(20)
    except Exception as e:
        logger.error("Failed to run color commands {}, ex {}".format("Color", e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect("Color")
        time.sleep(1)
        plezmoApi.disconnect("Motor-A")
        time.sleep(1)
        plezmoApi.close()

# Event handler whenever color sensor detects GREEN color
# Start motor when GREEN color is detected
@PlezmoEventHandler
def green_handler():
    logger.info("Got green color change event")
    Motor.start("Motor-A", MotorSpeed.HIGH, MotorDirection.CLOCKWISE)

# Event handler whenever color sensor detects RED color
# Start motor when RED color is detected
@PlezmoEventHandler
def red_handler():
    logger.info("Got red color change event")
    Motor.stop("Motor-A")

# Program starts here
if __name__ == "__main__":
    main()
```
