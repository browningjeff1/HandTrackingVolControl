import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

##################################
wCam, hCam, fps = 640, 480, 30
##################################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(5, fps)
pTime = 0
detector = htm.handDetector(detectionCon=0.75, trackCon=0.75)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

volumeBar = 400
volPercent = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if lmList and lmList[4] and lmList[8]:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        len = math.hypot(x2 - x1, y2 - y1)

        # Hand Range 50 - 300
        # VolRange -65.0 - 0.0
        vol = np.interp(len, [50, 300], [minVol, maxVol])
        volumeBar = np.interp(len, [50, 300], [400, 150])
        volPercent = np.interp(len, [50, 300], [0, 100])
        print(vol)

        if len < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        volume.SetMasterVolumeLevel(vol, None)



    cv2.rectangle(img, (50,150), (85, 400), (0,255,0, 3))
    cv2.rectangle(img, (50, int(volumeBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Vol: {int(volPercent)}%', (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

    cv2.imshow("Image", img)
    cv2.waitKey(1)
