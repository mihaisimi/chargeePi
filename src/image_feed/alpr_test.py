import cv2
import json
from openalpr import Alpr

cap= cv2.VideoCapture(0)

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
            if (len(bestResult['plate']) > 6 and len(bestResult['plate']) < 9):
                print("-------------------------------")
                print("plate:"+bestResult['plate'])
                print("confidence:"+str(bestResult['confidence']))
                print("-------------------------------")
        
    if cv2.waitKey(1) == 13:
            break
alpr.unload()
cap.release()
cv2.destroyAllWindows()