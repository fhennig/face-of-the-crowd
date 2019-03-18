import face_recognition
import cv2

# initialize window
cv2.namedWindow("preview")
# get webcam
video_capture = cv2.VideoCapture(1)
video_capture.set(3, 1280)
video_capture.set(4, 720)

scaling_factor = 4


face_locations = []
face_landmarks = []
process_this_frame = True

if video_capture.isOpened(): # try to get the first frame
    rval, frame = video_capture.read()
else:
    rval = False

while rval:
    # get a single frame
    rval, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=1/scaling_factor, fy=1/scaling_factor)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_landmarks = face_recognition.face_landmarks(rgb_small_frame)

    process_this_frame = not process_this_frame

    # Display the results
    for top, right, bottom, left in face_locations:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= scaling_factor
        right *= scaling_factor
        bottom *= scaling_factor
        left *= scaling_factor

        # change framesize to portrait crop
        left -= 80
        right += 80
        top -= 200
        bottom += 100

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Display the resulting image
    cv2.imshow("preview", frame)

    # exit on ESC
    key = cv2.waitKey(20)
    if key == 113:  # exit on q
        break
    if key == 102:
        print(face_landmarks)

cv2.destroyWindow("preview")
video_capture.release()
