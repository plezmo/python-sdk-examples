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

# Elements needed: 1 distance sensor
# Python packages: matplotlib
# Captures distance observed from distance sensor evenry two seconds for 5 times and plots it using matplotlib

import matplotlib.pyplot as plt
import time

from plezmo import *
from plezmo.elements.element_types import PlezmoElementType
from plezmo.utils.logger import Logger

import utils

logger = Logger()

def main(distance_name):
    try:
        plezmoApi.connect(distance_name, PlezmoElementType.DISTANCE)
    except:
        logger.error("Failed to connect to element")
        quit()

    ydata = []
    xdata = []

    # Number of intervals for which distance value is captured
    INTERVALS = 5
    t = 0
    logger.info("Move the distance element closer/away from any surface to record different distances. These values will be plotted using matplotlib.")
    # Capture distance value every 2 seconds
    for x in range(0, INTERVALS):
        d = Distance.getDistanceCM(distance_name)
        logger.info("Got distance {}".format(d))
        ydata.append(d)
        xdata.append(t)
        t += 2
        time.sleep(2)

    # Disconnect elements and close. Don't forget this for proper deinit.
    plezmoApi.disconnect(distance_name)
    plezmoApi.close()

    # Plot the data
    plt.plot(xdata, ydata)
    plt.ylabel('Distance in CM')
    plt.xlabel('Time in seconds')
    plt.show()

# Program starts here
if __name__ == "__main__":
    distance_name = utils.extract_element_name()
    if distance_name == None:
        logger.error("Distance element name is mandatory, e.g. # python distance_plot_example.py Distance")
    else:
        main(distance_name)