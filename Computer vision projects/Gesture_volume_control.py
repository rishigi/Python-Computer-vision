# MODULES
import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEnd

#####################################################################################################

# SOLUTION APIS
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
#####################################################################################################

# VOLUME CONTROL LIBRARY USAGE      rishi

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol , maxVol , volBar, volPer= volRange[0] , volRange[1], 400, 0
#######################################################################################################

# WEBCAM SETUP
wCam, hCam = 1920, 1080
cam = cv2.VideoCapture(0)
cam.set(3,wCam)
cam.set(4,hCam)
######################################################################################################

# MEDIAPIPE HANDS LANDMARKS MODEL
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.05,
    min_tracking_confidence=0.05) as hands:

  while cam.isOpened():
    success, image = cam.read()

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
            )

    # MULTI_HAND_LANDMARKS METHOD FOR FINGING POSITION OF HANDS LANDMARKS      
    lmList = []
    if results.multi_hand_landmarks:
      myHand = results.multi_hand_landmarks[0]
      for id, lm in enumerate(myHand.landmark):
        h, w, c = image.shape
        cx, cy = int(lm.x * w), int(lm.y * h)
        lmList.append([id, cx, cy])          

    # ASSINGING VARIABLE FOR THUMMB AND INDEX FINDER POSITION
    if len(lmList) != 0:
      x1, y1 = lmList[4][1], lmList[4][2]
      x2, y2 = lmList[8][1], lmList[8][2]

      # MARKING THUMB AND INDEX FINGER
      cv2.circle(image, (x1,y1),15,(255,10,100))  
      cv2.circle(image, (x2,y2),15,(255,10,100))   
      cv2.line(image,(x1,y1),(x2,y2),(255,10,100),3)
      length = math.hypot(x2-x1,y2-y1)
      if length < 50:
        cv2.line(image,(x1,y1),(x2,y2),(0,0,255),3)

      vol = np.interp(length, [50, 220], [minVol, maxVol])
      volume.SetMasterVolumeLevel(vol, None)
      volBar = np.interp(length, [50, 220], [400, 150])
      volPer = np.interp(length, [50, 220], [0, 100])

      # VOLUME
      cv2.rectangle(image, (50, 150), (85, 400), (0, 0, 0), 3)
      cv2.rectangle(image, (50, int(volBar)), (85, 400), (255, 255, 0), cv2.FILLED)
      cv2.putText(image, f'{int(volPer)} %', (40, 450), cv2.FONT_ITALIC,
                1, (0, 0, 0), 3)
    
    cv2.imshow('Gesture_Volume_Control', image) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
cam.release()