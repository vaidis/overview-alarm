#! /usr/bin/env python3.7

import os
import sys
import json
import asyncio
import aiohttp
import aiohttp_cors
import subprocess
from aiohttp import web
from gtts import gTTS

# ----- Edit variable values --------------
url = "http://10.0.31.222:7777/alarm"
pin = 21
lang = "el"
voice_dir = "/opt/overview-alarm/sounds/"
voice_start_single = "Προσοχή το host"
voice_stop_single = "είναι down"
voice_start_multi = "Προσοχή κάποια host"
voice_stop_multi = "είναι down"
# -----------------------------------------

file_expo = "/sys/class/gpio/export"
file_unexpo = "/sys/class/gpio/unexport"
file_direction = "/sys/class/gpio/gpio" + str(pin) + "/direction"
file_value = "/sys/class/gpio/gpio" + str(pin) + "/value"

cmd_export = "echo " + str(pin) + " > " + file_expo
cmd_unexport = "echo " + str(pin) + " > " + file_unexpo
cmd_dicrection = "echo out > " + file_direction
cmd_value = lambda value: "echo " + str(value) + " > /sys/class/gpio/gpio" + str(pin) + "/value"

working = False
mkdir -p "voice_dir"

# INIT GPIO PIN
def gpio(cmd):
    response = subprocess.run(cmd, shell=True)
    if response.returncode == 0:
        return True
    else:
        return False

exists = os.path.isfile(file_value)
if exists:
    if not gpio(cmd_dicrection):
        print("cmd_dicrection false")
        sys.exit()
else:
    if gpio(cmd_export):
        exists = os.path.isfile(file_direction)
        if exists:
            if gpio(cmd_dicrection):
                if not gpio(cmd_value(1)):
                    print("set GPIO port " + str(pin) + " failed")
                    sys.exit()
    else:
        print("export GPIO port " + str(pin) + " failed")
        sys.exit()


# ALARMS
async def alarm_light():
    gpio(cmd_value(0))
    await asyncio.sleep(9)
    gpio(cmd_value(1))

async def play(msg):
    proc = await asyncio.create_subprocess_shell("mpg321 "+ msg, stdout=asyncio.subprocess.PIPE, shell=True)
    await proc.communicate()

async def alarm_speak(alarms):
    global voice_dir
    global working
    working = True
    number = len(alarms)
    if number == 1:
        for k, v in alarms.items():
            address = str(k)
            host = str(v)

        exists = os.path.isfile(host)
        if exists:
            msg = voice_dir + "voice_start_single " + voice_dir + host + " " + voice_dir + "voice_stop_single"
            await play(msg)
        else:
            tts = gTTS(host, lang)
            tts.save(voice_dir + host)
            msg = voice_dir + "voice_start_single " + voice_dir + host + " " + voice_dir + "voice_stop_single"
            await play(msg)

    else:
        msg = voice_dir + "voice_start_multi " + voice_dir + "voice_stop_multi"
        await play(msg)
    working = False

# MAIN
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()


async def main(loop):
    b = {}
    alarms = {}
    global working
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                alarms.clear()
                response = await fetch(session, url)
                a = response['hosts']
                status = response['status']
                if status == True:
                    if bool(b):
                        print("a: " + str(a))
                        print("b: " + str(b))
                        for k, v in a.items():
                            if not k in b.keys():
                                if working == False:
                                    alarms[k] = v
                                    print("alarms: " + str( alarms))
                                    asyncio.ensure_future(alarm_light(), loop=loop)
                                    asyncio.ensure_future(alarm_speak(alarms), loop=loop)

                b = response['hosts'].copy()
            except:
                print("fetch failed " + str(url))
            await asyncio.sleep(4)


# VOICE MESSAGES
def create_voice(file, message):
    tts = gTTS(message, lang)
    try:
        tts.save(file)
    except ValueError as e:
        print(e)
        sys.exit()

if not os.path.isfile(voice_dir + "voice_start_single"):
    create_voice(str(voice_dir + "voice_start_single"), voice_start_single)

if not os.path.isfile(voice_dir + "voice_stop_single"):
    create_voice(str(voice_dir + "voice_stop_single"), voice_stop_single)

if not os.path.isfile(voice_dir + "voice_start_multi"):
    create_voice(str(voice_dir + "voice_start_multi"), voice_start_multi)    

if not os.path.isfile(voice_dir + "voice_stop_multi"):
    create_voice(str(voice_dir + "voice_stop_multi"), voice_stop_multi)


# LOOP
loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main(loop))
    loop.run_forever()

except KeyboardInterrupt:
    loop.stop()
    loop.close()
    subprocess.run(cmd_unexport, shell=True)

finally:
    print("Closing Loop")
    loop.stop()
    loop.close()
    subprocess.run(cmd_unexport, shell=True)
