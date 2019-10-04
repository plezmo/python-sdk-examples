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

import requests
import json
import time
import sys
import traceback
import logging

from plezmo import *
from plezmo.elements.element_types import PlezmoElementType
from plezmo.elements.plezmo_display import *
from plezmo.elements.plezmo_music import *
from plezmo.elements.plezmo_light import *

MUSIC_NAME = "Music"
DISPLAY_NAME = "Display"
LIGHT_NAME = "Light"

API_KEY="YOUR_KEY"

# Sample API response
#{
#	"coord": {
#		"lon": 145.77,
#		"lat": -16.92
#	},
#	"weather": [{
#		"id": 802,
#		"main": "Clouds",
#		"description": "scattered clouds",
#		"icon": "03n"
#	}],
#	"base": "stations",
#	"main": {
#		"temp": 300.15,
#		"pressure": 1007,
#		"humidity": 74,
#		"temp_min": 300.15,
#		"temp_max": 300.15
#	},
#	"visibility": 10000,
#	"wind": {
#		"speed": 3.6,
#		"deg": 160
#	},
#	"clouds": {
#		"all": 40
#	},
#	"dt": 1485790200,
#	"sys": {
#		"type": 1,
#		"id": 8166,
#		"message": 0.2064,
#		"country": "AU",
#		"sunrise": 1485720272,
#		"sunset": 1485766550
#	},
#	"id": 2172797,
#	"name": "Cairns",
#	"cod": 200
#}
CONST_RAIN = "rain"
CONST_CLOUD = "cloud"

def kelvinToCelcius(temp):
    return round(temp - 273.15, 2)

def fetchWeather(cityName):
    print("Fetching weather for {}".format(cityName))
    url = "http://api.openweathermap.org/data/2.5/weather?APPID=" + API_KEY + "&q=" + cityName
    res = requests.get(url)
    #print("response is {}".format(res.text))
    data = json.loads(res.text)
    weather = data.get("weather")
    temp = data.get("main")
    return { "currentTemp": kelvinToCelcius(temp.get("temp")),
                "maxTemp": kelvinToCelcius(temp.get("temp_min")),
                "minTemp": kelvinToCelcius(temp.get("temp_max")),
                "weather": weather[0].get("main")
            }

def globalExceptionHandler(e):
    pass

# Init bluetooth communication
def init():
    # Register global exception handler
    registerExceptionHandler(globalExceptionHandler)
    print("Connecting to 3 elements...")
    # Elements to connect
    elementList = [{"name" : DISPLAY_NAME, "type": PlezmoElementType.DISPLAY},
                   {"name" : MUSIC_NAME, "type": PlezmoElementType.MUSIC},
                   {"name" : LIGHT_NAME, "type": PlezmoElementType.LIGHT}]
    connectedElements = []
    try:
        # connect to elements one by one
        for e in elementList:
            print("Connecting to element {}".format(e["name"]))
            plezmoApi.connect(e["name"], e["type"], 60)
            # keep track of connected elements
            connectedElements.append(e["name"])
            print("Connection to element {} successful".format(e["name"]))
        print("All connections successful")
        return True
    except Exception as e:
        # Disconnect and stop program if connection to element fails
        print("Failed to connect to one of the elements, restart the script")
        # Disconnect already connected elements
        for e in connectedElements:
            plezmoApi.disconnect(e)
        return False

# Main logic of the program
def main():
    # Init bluetooth communication
    success = init()
    if success != True:
        # Bluetooth communication cannot be enabled, quit.
        plezmoApi.close()
        print("Could not connect to all the required elements")
        return

    Display.setFontSize(DISPLAY_NAME, FontSize.MEDIUM)

    while True:
        # clear display
        Display.clearDisplay(DISPLAY_NAME)
        # turn light off
        Light.setState(LIGHT_NAME, LightState.OFF)
        print("------------------------------------------------")
        cityName = input("To know weather, enter city name: ")

        # fetch weather for city
        data = fetchWeather(cityName)
        if data == None:
            print("Unable to find weather for city " + cityName)
            continue
        try:
            # get temp
            temp = data.get("currentTemp")
            # get overall weather
            weather = data.get("weather")
            lightColor = None
            print("temp is {}, weather is {}".format(temp, weather))
            # turn light on in BLUE color if temeperatur is < 20
            # turn light on in YELLOw color if temeperatur is > 20 but < 30
            # turn light on in RED color if temeperatur is > 30
            if temp < 20:
                lightColor = LightColor("#0000FF")
            elif temp < 30:
                lightColor = LightColor("#FFFF00")
            else:
                lightColor = LightColor("#FF0000")
            Light.turnOn(LIGHT_NAME, lightColor, Percentage(100))

            # Show images on display and play audio on Music based on weather
            if weather.lower().find(CONST_RAIN) >= 0 or weather.lower().find(CONST_CLOUD) >= 0:
                Display.showImage(DISPLAY_NAME, DisplayImage.CLOUDY)
                if weather.lower().find(CONST_RAIN) >= 0:
                    Display.showText(DISPLAY_NAME, DisplayLine.TWO, TextAlignment.CENTER, "Rain!!")
                Music.playAudio(MUSIC_NAME, Audio.RAIN)
            else:
                Display.showImage(DISPLAY_NAME, DisplayImage.SUNNY)
                Music.playAudio(MUSIC_NAME, Audio.BIRDS_CHIRPING)
        except Exception as e:
            pass

# Program starts here
if __name__ == "__main__":
    try:
        main()
    finally:
        # Program completed, disconnect elements and quit
        plezmoApi.disconnect(DISPLAY_NAME)
        plezmoApi.disconnect(MUSIC_NAME)
        plezmoApi.disconnect(LIGHT_NAME)
        time.sleep(1)
        try:
            plezmoApi.close()
        except:
            pass



