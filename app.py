#! /usr/bin/env python3
import argparse
import logging.config
import os
import json


logger = None


def create_parser():
    parser = argparse.ArgumentParser(description="The face of the crowd!  Choose a command to run.\n" +
                                                 "Most likely try 'display' first.")

    parser.add_argument(
        "command",
        choices=["display", "server", "genportrait", "gengif"],
        help="""
display: Runs the interactive installation.
         Switches:  camera_input, rotate, fullscreen, remote, host, port, stack_size, pool_size, image_dir.
backend: Runs a processing backend that the display can connect to.
         Switches:  stack_size, pool_size, image_dir.
genportrait: Generates a merged portrait from all the images in the image dir.
             Switches: image_dir, output_file, pool_size.
gengif: Generates a gif from the images in the image dir.
        Switches: image_dir, output_file, pool_size, stack_size, loop.
        """
    )

    parser.add_argument(
        "--camera_input",
        default=1,
        type=int,
        help="Which camera to use (integer: 0, 1, ...)."
    )
    parser.add_argument(
        "--rotate",
        action='store_true',
        default=False,
        help="Whether to rotate the image received from the camera input.\n" +
             "Useful if the camera has been rotated to portrait mode."
    )
    parser.add_argument(
        "--fullscreen",
        action='store_true',
        default=False,
        help="Whether to display the generated image fullscreen."
    )
    parser.add_argument(
        "--remote",
        action='store_true',
        default=False,
        help="Whether to use a remote rpc or run everything locally.\n" +
             "Use --host and --port to specify the remote processing backend.\n" +
             "If this switch is omitted, processing is done locally."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="The remote host IP adress."
    )
    parser.add_argument(
        "--port",
        default=5000,
        type=int,
        help="The remote port."
    )
    parser.add_argument(
        "--stack_size",
        default=10,
        type=int,
        help="The number of images to merge together.\n" +
             "The display does not merge all the images together, only the last k,\n" +
             "where k is the stack_size."
    )
    parser.add_argument(
        "--pool_size",
        default=4,
        type=int,
        help="The number of parallel processes to use."
    )
    parser.add_argument(
        "--image_dir",
        default="images",
        help="The directory where the images taken in interactive mode should be saved.\n" +
             "It is also input directory for the image generation commands."
    )
    parser.add_argument(
        "--output_file",
        default=None,
        help="The path where to output the generated image or gif."
    )
    parser.add_argument(
        "--loop",
        action='store_true',
        default=False,
        help="For the generated gif, if it should loop."
    )
    parser.add_argument(
        "--stable_points",
        default="[]",
        help="A list of points that are stable in each image.\n" +
             "Can also be a file.  The format is [[x1, y1], [x2, y2], ...]"
    )

    return parser


def run_display(args):
    from artsci2019.display import InteractiveDisplay
    if args.remote:
        from artsci2019.displaybackend.rpc.client import RemoteBackend
        processing_backend = RemoteBackend(args.host, args.port)
    else:
        from artsci2019.displaybackend.backend import Backend
        processing_backend = Backend(args.stack_size, args.pool_size, args.stable_points, args.image_dir)
    a = InteractiveDisplay(args.camera_input,
                           args.rotate,
                           args.fullscreen,
                           processing_backend)
    init_successful = a.init()
    if not init_successful:
        print("Error in init.")
        return
    a.start()
    a.teardown()


def run_backend(args):
    from artsci2019.displaybackend.rpc.server import create_app
    app = create_app(args.stack_size, args.pool_size, args.stable_points, args.image_dir)
    app.run(debug=True)


def run_portrait(args):
    from artsci2019.imagegen import run_portrait
    run_portrait(args.image_dir, args.pool_size, args.output_file, args.stable_points)


def run_genvideo(args):
    from artsci2019.imagegen import run_genanimation
    run_genanimation(args.image_dir,
                     "temp",
                     args.output_file,
                     args.stack_size,
                     args.pool_size,
                     args.loop,
                     args.stable_points)


def init_logging():
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'default': {
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stderr',
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            }
        }
    })


def parse_stable_points(args):
    if os.path.exists(args.stable_points):
        with open(args.stable_points, "r") as f:
            args.stable_points = f.read()
    try:
        l = json.loads(args.stable_points)
        if not isinstance(l, list):
            raise ValueError()
        l = [tuple(e) for e in l]
        args.stable_points = l
    except:
        logger.error("Error parsing the stable points.")
        args.stable_points = []


def main():
    parser = create_parser()
    args = parser.parse_args()
    parse_stable_points(args)
    if args.command == "display":
        run_display(args)
    elif args.command == "server":
        run_backend(args)
    elif args.command == "genportrait":
        run_portrait(args)
    elif args.command == "gengif":
        run_genvideo(args)


if __name__ == "__main__":
    init_logging()
    logger = logging.getLogger(__name__)
    main()
