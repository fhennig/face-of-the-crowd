from artsci2019.lib.portrait import gen_portrait
from artsci2019.lib.image_storage import read_recognized_frames, write_image
import logging
import cv2
import os
import subprocess


logger = logging.getLogger(__name__)


def gen_portraits(rfs, stack_size, pool_size, loop, stable_points):
    """Takes a sequence of recognized frames,
    the stack size (how many pictures to stack per portrait),
    the pool size (how many threads to use),
    and if the video should loop or not."""
    if loop:
        rfs = rfs + rfs[:stack_size - 1]
    frame_count = len(rfs) - stack_size
    logger.info("Generating frames.  Frames to generate: {}.".format(frame_count))
    frames = []
    for i in range(frame_count):
        logger.info("Generating frame {}/{}.".format(i + 1, frame_count))
        portrait = gen_portrait(rfs[i:i + stack_size], pool_size, stable_points)
        frames.append(portrait)
    return frames


def write_intermediate_files(portraits, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, p in enumerate(portraits):
        path = os.path.join(output_dir, "{:06d}.png".format(i))
        logger.debug("Writing portrait {} to {}".format(i, path))
        cv2.imwrite(path, p)


def generate_video(input_dir, output_file):
    subprocess.call([
        'ffmpeg',
        '-r', '10',
        '-i', input_dir + "/%06d.png",
        output_file
    ])


def run_genanimation(input_dir, intermediate_dir, output_file, stack_size, pool_size, loop, stable_points):
    logger.info("Reading frames from {} ...".format(input_dir))
    rfs = read_recognized_frames(input_dir)
    logger.info("Generating portraits ...")
    portraits = gen_portraits(rfs, stack_size, pool_size, loop, stable_points)
    logger.info("Writing portraits ...")
    write_intermediate_files(portraits, intermediate_dir)
    logger.info("Generating video ...")
    generate_video(intermediate_dir, output_file)


def run_portrait(input_dir, pool_size, output_file, stable_points):
    logger.info("Reading frames ...")
    rfs = read_recognized_frames(input_dir)
    # rfs = [rf.cropped(1080, 1773 - 333, 0, 333) for rf in rfs]
    logger.info("Generating Portrait ...")
    f = gen_portrait(rfs, pool_size, stable_points)
    logger.info("Writing output file ...")
    if not output_file:
        output_file = input_dir + ".png"
    write_image(f, output_file)
    logger.info("Done.")
