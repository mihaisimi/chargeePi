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

class carDetector:
    last_seen = 0
    last_plate_detected = ''
    charging = False
    tickThread = ''
    charging_on_pin = 21
    onChargingUpdate = None

    def is_raspberrypi(self):
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

    def raspiInit(self):
        if (self.is_raspberrypi()):
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.charging_on_pin, GPIO.OUT)


    def enable_charging(self, onStartCharging, onUpdate):
        global charging
        charging = True
        self.onChargingUpdate = onUpdate
        print("CHARGIN ENABLED")
        tickThread = Thread(target=self.chargingTick)
        tickThread.start()
        if (self.is_raspberrypi()):
            import RPi.GPIO as GPIO
            GPIO.output(self.charging_on_pin, GPIO.HIGH)
            print("change gpio")
        onStartCharging()

    def disabled_charging(self, onStopCharging):
        global charging
        charging = False
        print("DISABLE_CHARGING")
        if (self.is_raspberrypi()):
            import RPi.GPIO as GPIO
            GPIO.output(self.charging_on_pin, GPIO.LOW)
            print("change gpio")
        onStopCharging()



    def checkJudet(self, str):
        judete=["B", "AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ", "CJ", "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL", "GR", "HD", "HR", "IF", "IL", "IS", "MH", "MM", "MS", "NT", "OT", "PH", "SB", "SJ", "SM", "SV", "TL", "TM", "TR", "VL", "VN", "VS"]
        for j in judete:
            if (str.startswith(j)):
                return True
        return False

    def chargingTick(self):
        print("charging tick started")
        while True:
            sleep(1) 
            power_kWh = random.random() * 45
            #print("charging tick - power: "+str(power_kWh)+" kWh")
            if (self.onChargingUpdate):
                self.onChargingUpdate(power_kWh)
            global charging
            if (not charging):
                break
        print("charging tick ended")


    def initalizeDetector(self):
        print("Detector init")
        self.raspiInit()
        self.alpr = Alpr("eu", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
        if not self.alpr.is_loaded():
            print("Error loading OpenALPR")
            sys.exit(1)

    def processFrame(self, cap, onCarDetected, onCarLost, onStartCharging, onStopCharging, onChargingUpdate):
        ret, frame= cap.read()    
        cv2.imshow('Cars', frame)
        ret,enc = cv2.imencode("*.bmp", frame)
        results = self.alpr.recognize_array(bytes(bytearray(enc)))
        #print(json.dumps(results, indent=4))
        now = datetime.now().timestamp() * 1000
        if (len(results['results'])>0):
            bestResult = results['results'][0]
            if (bestResult['confidence'] > 84):
                normalPlateMatch = re.search("[A-Z][A-Z][0-9][0-9][A-Z][A-Z][A-Z]",bestResult['plate'])
                redPlateMatch = re.search("[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]",bestResult['plate'])

                if ((normalPlateMatch or redPlateMatch) and len(bestResult['plate']) > 6 and len(bestResult['plate']) < 9 and self.checkJudet(bestResult['plate'].upper())):
                    if (self.last_plate_detected != bestResult['plate'] and not self.charging):
                        print("-------------------------------")
                        print("detected plate:"+bestResult['plate'])
                        print("confidence:"+str(bestResult['confidence']))
                        self.last_plate_detected = bestResult['plate']
                        print("-------------------------------")
                        self.last_seen = now
                        if onCarDetected:
                            onCarDetected(self.last_plate_detected)
                        self.enable_charging(onStartCharging, onChargingUpdate)
                    else:
                        self.last_seen = now

        else:
            if (len(self.last_plate_detected) > 0):
                last_seen_dif = now - self.last_seen
                if ( (last_seen_dif) > 5000):
                    print("licence lost: "+self.last_plate_detected)
                    self.last_plate_detected=""
                    self.disabled_charging(onStopCharging)



    def releaseDetector(self):
        self.alpr.unload()
        cv2.destroyAllWindows()