
import cv2
import numpy as np
import os

video_path = input("Enter the video path: ").strip().strip('"')

if not os.path.isfile(video_path):
    print("Video file not found.")
    raise SystemExit

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Could not read the first frame.")
    raise SystemExit

points = []
clone = frame.copy()
window = "Click corners - S save, R reset, Q quit"

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        print(f"Point added: ({x}, {y})")

        display = clone.copy()

        for i, point in enumerate(points):
            cv2.circle(display, tuple(point), 5, (0, 0, 255), -1)
            cv2.putText(
                display, str(i + 1),
                (point[0] + 10, point[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )

        if len(points) > 1:
            cv2.polylines(
                display, [np.array(points, np.int32)],
                False, (255, 0, 0), 2
            )

        cv2.imshow(window, display)

cv2.namedWindow(window)
cv2.setMouseCallback(window, click_event)
cv2.imshow(window, frame)

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        if len(points) < 3:
            print("Click at least three points to form a polygon.")
            continue

        print("\nCopy these coordinates into detect.py:")
        print(f'"polygon": {points}')
        break

    elif key == ord("r"):
        points.clear()
        cv2.imshow(window, clone)
        print("Points reset.")

    elif key == ord("q"):
        break

cv2.destroyAllWindows()
