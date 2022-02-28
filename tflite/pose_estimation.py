"""Main script to run pose classification and pose estimation."""
import sys
import time

import cv2
from tflite.ml import Movenet

TESTING = False

class Messenger:

  def __init__(self):
    self.pose_detector = Movenet('movenet_lightning')

    # Variables to calculate FPS
    self.fps_avg_frame_count = 10
    self.counter, self.fps = 0, 0
    self.start_time = time.time()

    # Start capturing video input from the camera
    self.cap = cv2.VideoCapture(0)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


  def close(self):
    self.cap.release()

  def get_message(self):
    # Continuously capture images from the camera and run inference
    if self.cap.isOpened():
      success, image = self.cap.read()
      if not success:
        sys.exit(
            'ERROR: Unable to read from webcam. Please verify your webcam settings.'
        )

      self.counter += 1
      image = cv2.flip(image, 1)

      person = self.pose_detector.detect(image)

      # Calculate the FPS
      if self.counter % self.fps_avg_frame_count == 0:
        end_time = time.time()
        self.fps = self.fps_avg_frame_count / (end_time - self.start_time)
        self.start_time = time.time()

      # Show the FPS
      fps_text = 'FPS = ' + str(int(self.fps))
      if (TESTING):
          print(fps_text)

      # Main Logic
      torso_confidence = sum(list(map(lambda x: person.keypoints[x].score, [5, 6, 11, 12]))) / 4
      midpoint_x = sum(list(map(lambda x: person.keypoints[x].coordinate.x, [5, 6, 11, 12]))) / 4
      dist_x = (midpoint_x - 320) / 320
      torso_size = person.keypoints[11].coordinate.y + person.keypoints[12].coordinate.y - person.keypoints[5].coordinate.y - person.keypoints[6].coordinate.y
      dist_y = torso_size / 2 / 480

      if (TESTING):
        print("Confidence: {}, dist_x: {}, dist_y: {}".format(torso_confidence, dist_x, dist_y))

      # Return Detection
      if (torso_confidence < .5):
        return "NO PERSON"
      elif (dist_y > .28):
        return "CLOSE"
      elif (dist_y < .22):
        return "FAR"
      else:
        if (dist_x > .3):
          return "LEFT"
        elif (dist_x < -.3):
          return "RIGHT"
        else:
          return "CENTER"

    return "CAMERA CLOSED"
