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

from plezmo import *
from plezmo.utils.logger import Logger

logger = Logger()

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init():
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)

# Main logic of the program
def main():
    # Init bluetooth communication
    init()
    elementList = plezmoApi.getDiscoveredElements(5)
    #logger.info("Got elements {}".format(elementList))
    if elementList != None and len(elementList) > 0:
        e = elementList[0]
        logger.info("connecting to first element {}".format(e))
        plezmoApi.connectByMac(e["mac"], e["type"])
        connected_elements = plezmoApi.getConnectedElements()
        logger.info("connected elements {}".format(connected_elements))
        plezmoApi.disconnect(e["name"])
        time.sleep(1)
    plezmoApi.close()

# Program starts here
if __name__ == "__main__":
    main()
    quit()