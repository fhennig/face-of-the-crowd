import cv2
import datetime
import os
import json
import logging
from artsci2019.lib.util import RecognizedFrame


logger = logging.getLogger(__name__)


def write_image(frame, filename):
    cv2.imwrite(filename, frame)


def write_recognized_frame(dir, rf):
    current_date = datetime.datetime.now()
    date_str = current_date.strftime("%Y-%m-%d-%H-%M-%S-%f")
    img_filename = os.path.join(dir, date_str + ".png")
    cv2.imwrite(img_filename, rf.frame)
    json_filename = os.path.join(dir, date_str + ".json")
    info = {
        "date": date_str,
        "landmarks": rf.face_landmarks
    }
    with open(json_filename, "w") as f:
        json.dump(info, f)


def write_recognized_frames(target_dir, rfs):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    logger.info("Writing recognized frames.")
    for rf in rfs:
        write_recognized_frame(target_dir, rf)


def read_recognized_frames(source_directory):
    rfs = []
    img_files = [source_directory + "/" + f
                 for f in os.listdir(source_directory)
                 if f.endswith(".png")]
    img_files.sort()
    for img_file in img_files:
        img = cv2.imread(img_file)
        json_file = img_file[:-4] + ".json"
        with open(json_file, "r") as f:
            jdir = json.load(f)
        rf = RecognizedFrame(img, [tuple(lm) for lm in jdir["landmarks"]])
        rfs.append(rf)
    return rfs
