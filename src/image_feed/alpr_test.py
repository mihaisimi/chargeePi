import cv2
import json
from openalpr import Alpr
from datetime import datetime
import re
import io
import os
import random
from threading import Thread
from time import sleep


cap= cv2.VideoCapture(0)

last_seen = 0
last_plate_detected = ''
charging = False
tickThread = ''

charging_on_pin = 21

def is_raspberrypi():
    if os.name != 'posix':
        return False
    chips = ('BCM2708','BCM2709','BCM2711','BCM2835','BCM2836')
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    _, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value in chips:
                        return True
    except Exception:
        pass
    return False

def raspiInit():
    if (is_raspberrypi()):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(charging_on_pin, GPIO.OUT)


def enable_charging():
    global charging
    charging = True
    print("CHARGIN ENABLED")
    tickThread = Thread(target=chargingTick)
    tickThread.start()
    if (is_raspberrypi()):
        import RPi.GPIO as GPIO
        GPIO.output(charging_on_pin, GPIO.HIGH)
        print("change gpio")

def disabled_charging():
    global charging
    charging = False
    print("DISABLE_CHARGING")
    if (is_raspberrypi()):
        import RPi.GPIO as GPIO
        GPIO.output(charging_on_pin, GPIO.LOW)
        print("change gpio")



def checkJudet(str):
    judete=["B", "AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ", "CJ", "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL", "GR", "HD", "HR", "IF", "IL", "IS", "MH", "MM", "MS", "NT", "OT", "PH", "SB", "SJ", "SM", "SV", "TL", "TM", "TR", "VL", "VN", "VS"]
    for j in judete:
        if (str.startswith(j)):
            return True
    return False

def chargingTick():
    print("charging tick started")
    while True:
        sleep(1) 
        power_kWh = random.random() * 45
        print("charging tick - power: "+str(power_kWh)+" kWh")
        global charging
        if (not charging):
            break
    print("charging tick ended")

alpr = Alpr("eu", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
if not alpr.is_loaded():
    print("Error loading OpenALPR")
    sys.exit(1)
while True:
    ret, frame= cap.read()    
    cv2.imshow('Cars', frame)
    ret,enc = cv2.imencode("*.bmp", frame)
    results = alpr.recognize_array(bytes(bytearray(enc)))
    #print(json.dumps(results, indent=4))
    now = datetime.now().timestamp() * 1000
    if (len(results['results'])>0):
        bestResult = results['results'][0]
        if (bestResult['confidence'] > 84):
            plateMatch = re.search("[A-Z][A-Z][0-9][0-9][A-Z][A-Z][A-Z]",bestResult['plate'])

            if (plateMatch and len(bestResult['plate']) > 6 and len(bestResult['plate']) < 9 and checkJudet(bestResult['plate'].upper())):
                if (last_plate_detected != bestResult['plate'] and not charging):
                    print("-------------------------------")
                    print("detected plate:"+bestResult['plate'])
                    print("confidence:"+str(bestResult['confidence']))
                    last_plate_detected = bestResult['plate']
                    print("-------------------------------")
                    last_seen = now
                    enable_charging()
                else:
                    last_seen = now

    else:
        if (len(last_plate_detected) > 0):
            last_seen_dif = now - last_seen
            if ( (last_seen_dif) > 10000):
                print("licence lost: "+last_plate_detected)
                last_plate_detected=""
                disabled_charging()
        
    if cv2.waitKey(1) == 13:
            break
alpr.unload()
cap.release()
cv2.destroyAllWindows()