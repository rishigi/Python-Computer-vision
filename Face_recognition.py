import cv2
import mediapipe as mp
mp_face_mesh=mp.solutions.face_mesh
mp_drawing=mp.solutions.drawing_utils
mp_drawing_styles=mp.solutions.drawing_styles
mphands=mp.solutions.hands
########################
wCam, hCam = 1920, 1080
########################
webcam=cv2.VideoCapture(0)
webcam.set(3,wCam)
webcam.set(4,hCam)
while webcam.isOpened():
    success,img=webcam.read()

#applying face mesh module using mediapipe
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    results=mp_face_mesh.FaceMesh(refine_landmarks=True).process(img)

#draw annotations on the image
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks:
        for face_landmrks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmrks,
                connections = mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec =None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style()
            )

            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmrks,
                connections=mp_face_mesh.FACEMESH_FACE_OVAL,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )

            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmrks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )

    cv2.imshow("FIRST ML",img)
    if cv2.waitKey(20) & 0xff == ord("q"):
        break

webcam.release()
cv2.destroyAllWindows()
