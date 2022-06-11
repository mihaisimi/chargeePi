import cv2
import json
from openalpr import Alpr

cap= cv2.VideoCapture(0)

last_plate_detected = ''

def checkJudet(str):
    judete=["B", "AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ", "CJ", "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL", "GR", "HD", "HR", "IF", "IL", "IS", "MH", "MM", "MS", "NT", "OT", "PH", "SB", "SJ", "SM", "SV", "TL", "TM", "TR", "VL", "VN", "VS"]
    for j in judete:
        if (str.startswith(j)):
            return True
    return False


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
    if (len(results['results'])>0):
        bestResult = results['results'][0]
        if (bestResult['confidence'] > 88):
            if (len(bestResult['plate']) > 6 and len(bestResult['plate']) < 9 and checkJudet(bestResult['plate'].upper())):
                if (last_plate_detected != bestResult['plate']):
                    print("-------------------------------")
                    print("detected plate:"+bestResult['plate'])
                    print("confidence:"+str(bestResult['confidence']))
                    last_plate_detected = bestResult['plate']
                    print("-------------------------------")
    else:
        if (len(last_plate_detected) > 0):
            print("licence lost: "+last_plate_detected)
            last_plate_detected=""
        
    if cv2.waitKey(1) == 13:
            break
alpr.unload()
cap.release()
cv2.destroyAllWindows()