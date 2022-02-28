"""Main script to run pose classification and pose estimation."""
import sys
import time
import signal

import cv2
from ml import Movenet

TESTING = False

def signal_handler(sig, frame):
  cap.release()
  sys.exit()

def run(estimation_model: str, tracker_type: str, classification_model: str,
        label_file: str, camera_id: int, width: int, height: int) -> None:
  global cap

  if estimation_model in ['movenet_lightning', 'movenet_thunder']:
    pose_detector = Movenet(estimation_model)
  else:
    sys.exit('ERROR: Model is not supported.')

  # Variables to calculate FPS
  fps_avg_frame_count = 10
  counter, fps = 0, 0
  start_time = time.time()

  # Start capturing video input from the camera
  cap = cv2.VideoCapture(camera_id)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)


  # Continuously capture images from the camera and run inference
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      sys.exit(
          'ERROR: Unable to read from webcam. Please verify your webcam settings.'
      )

    counter += 1
    image = cv2.flip(image, 1)

    if estimation_model == 'movenet_multipose':
      list_persons = pose_detector.detect(image)
    else:
      list_persons = [pose_detector.detect(image)]


    # Calculate the FPS
    if counter % fps_avg_frame_count == 0:
      end_time = time.time()
      fps = fps_avg_frame_count / (end_time - start_time)
      start_time = time.time()

    # Show the FPS
    fps_text = 'FPS = ' + str(int(fps))
    if (TESTING):
        print(fps_text)

    # Main Logic
    person = list_persons[0]
    torso_confidence = sum(list(map(lambda x: person.keypoints[x].score, [5, 6, 11, 12]))) / 4
    midpoint_x = sum(list(map(lambda x: person.keypoints[x].coordinate.x, [5, 6, 11, 12]))) / 4
    dist_x = (midpoint_x - 320) / 320
    torso_size = person.keypoints[11].coordinate.y + person.keypoints[12].coordinate.y - person.keypoints[5].coordinate.y - person.keypoints[6].coordinate.y
    dist_y = torso_size / 2 / 480

    # Return Detection
    if (torso_confidence < .5):
      print("NO PERSON")
    elif (dist_y > .28):
      print("CLOSE")
    elif (dist_y < .22):
      print("FAR")
    else:
      if (dist_x > .3):
        print("LEFT")
      elif (dist_x < -.3):
        print("RIGHT")
      else:
        print("CENTER")

    if (TESTING):
      print("Confidence: {}, dist_x: {}, dist_y: {}".format(torso_confidence, dist_x, dist_y))


def main():
  run("movenet_lightning", None, None, None, 0, 640, 480)


if __name__ == '__main__':
  main()
