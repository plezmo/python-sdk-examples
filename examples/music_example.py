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

# Tests functionality of music element
import time
import traceback

from plezmo import *
from plezmo.utils.logger import Logger
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_music import *

import utils

logger = Logger()

def globalExceptionHandler(e):
    logger.info("###### Got exception {}".format(e))

# Init bluetooth communication
def init(music_name):
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    # Elements to connect
    elementList = [{"name" : music_name, "type": PlezmoElementType.MUSIC}]
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
def main(music_name):
    # Init bluetooth communication
    success = init(music_name)
    if success != True:
        # Bluetooth communication cannobe enabled, quit.
        plezmoApi.close()
        logger.error("Could not connect to all the required elements")
        return

    try:
        # Set volume and play audio
        logger.info("Setting volume to LOW")
        Music.setVolume(music_name, Volume.LOW)
        logger.info("Playing audio PIANO_LOOP_2")
        Music.playAudio(music_name, Audio.PIANO_LOOP_2)
        logger.info("Playing audio PIANO_LOOP_1 asynchronously. This will work only if music element has 3.4 version.")
        try:
            Music.playAudioAndContinue(music_name, Audio.PIANO_LOOP_1, AudioLoop.ONCE)
            time.sleep(5)
        except:
            logger.error("playAudioAndContinue failed. Make sure that the music element is upgraded to 3.4 version.")
        logger.info("Stopping audio")
        Music.stop(music_name)
        time.sleep(2)
        # start and stop buzzing
        logger.info("Starting buzzing")
        Music.startBuzzing(music_name)
        time.sleep(2)
        logger.info("Stopping buzzing")
        Music.stopBuzzing(music_name)
        time.sleep(2)
        # Play a note
        logger.info("Playing note 66 with beats = 1")
        Music.playNote(music_name, Note(66), 1)
        # Set instrument and tempo
        Music.setInstrument(music_name, Instrument.FLUTE)
        Music.setTempo(music_name, Tempo.MEDIUM)
        Music.setVolume(music_name, Volume.HIGH)
        logger.info("Set instrument to FLUTE, tempo to MEDIUM, volume to HIGH")
        i = Music.getInstrument(music_name)
        logger.info("Got instrument {}".format(i))
        t = Music.getTempo(music_name)
        logger.info("Got tempo {}".format(t))
        v = Music.getVolume(music_name)
        logger.info("Got volume {}".format(v))
        logger.info("Playing note 66 with beats = 3")
        Music.playNote(music_name, Note(66), 3)
        time.sleep(5)
    except Exception as e:
        logger.error("Failed to run music commands {}, ex {}".format(music_name, e))
        traceback.print_exc()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(music_name)
        time.sleep(1)
        plezmoApi.close()

# Program starts here
if __name__ == "__main__":
    music_name = utils.extract_element_name()
    if music_name == None:
        logger.error("Music element name is mandatory, e.g. # python music_example.py Music")
    else:
        main(music_name)