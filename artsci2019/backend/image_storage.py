import cv2
import datetime
import os
import json
import logging


logger = logging.getLogger(__name__)


class ImageStorage:

    def __init__(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.dir = directory

    def update(self, recognized_frames):
        logger.info("Writing recognized frames.")
        for rf in recognized_frames:
            current_date = datetime.datetime.now()
            date_str = current_date.strftime("%Y-%m-%d-%H-%M-%S-%f")
            img_filename = os.path.join(self.dir, date_str + ".png")
            cv2.imwrite(img_filename, rf.frame)
            json_filename = os.path.join(self.dir, date_str + ".json")
            info = {
                "date": date_str,
                "landmarks": rf.face_landmarks
            }
            with open(json_filename, "w") as f:
                json.dump(info, f)