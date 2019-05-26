#! /usr/bin/env python3
import argparse
import logging.config


logger = None


def create_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="subcommand"
    )

    display = subparsers.add_parser("display")

    display.add_argument(
        "--camera_input",
        default=1,
        type=int,
        help="Which camera to use."
    )
    display.add_argument(
        "--rotate",
        action='store_true',
        default=False,
        help="Whether to rotate the image."
    )
    display.add_argument(
        "--fullscreen",
        action='store_true',
        default=False,
        help="Whether to display the generated image fullscreen."
    )
    display.add_argument(
        "--remote",
        action='store_true',
        default=False,
        help="Whether to use a remote rpc or run everything locally."
    )
    display.add_argument(
        "--host",
        default="127.0.0.1",
        help="The remote host IP adress."
    )
    display.add_argument(
        "--port",
        default=5000,
        type=int,
        help="The remote port."
    )

    backend = subparsers.add_parser("server")

    # add common commands
    for p in [display, backend]:
        p.add_argument(
            "--stack_size",
            default=10,
            type=int,
            help="The number of images to merge together."
        )
        p.add_argument(
            "--pool_size",
            default=4,
            type=int,
            help="The number of parallel processes to use."
        )
        p.add_argument(
            "--image_dir",
            default="images",
            help="The directory where the images should be saved."
        )

    portrait = subparsers.add_parser("portrait")

    portrait.add_argument(
        "--input_dir",
        default="images",
        help="The directory with the images to be merged."
    )
    portrait.add_argument(
        "--output_file",
        default=None,
        help="The filename of the output image (jpg)."
    )
    portrait.add_argument(
        "--pool_size",
        default=4,
        type=int,
        help="The number of parallel processes to use."
    )

    genvideo = subparsers.add_parser("genvideo")

    genvideo.add_argument(
        "--input_dir",
        default="images",
        help="The directory with the images to be merged."
    )
    genvideo.add_argument(
        "--output_file",
        default=None,
        help="The filename of the output image (jpg)."
    )
    genvideo.add_argument(
        "--pool_size",
        default=4,
        type=int,
        help="The number of parallel processes to use."
    )
    genvideo.add_argument(
        "--stack_size",
        default=10,
        type=int,
        help="The number of images to merge together."
    )
    genvideo.add_argument(
        "--loop",
        action='store_true',
        default=False,
        help="If the video should look like a loop or not."
    )

    return parser


def run_display(args):
    from artsci2019.display import InteractiveDisplay
    if args.remote:
        from artsci2019.displaybackend.rpc.client import RemoteBackend
        processing_backend = RemoteBackend(args.host, args.port)
    else:
        from artsci2019.displaybackend.backend import Backend
        processing_backend = Backend(args.stack_size, args.pool_size, [], args.image_dir)  # TODO stable points
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
    app = create_app(args.stack_size, args.pool_size, [], args.image_dir)  # TODO stable points
    app.run(debug=True)


def run_portrait(args):
    from artsci2019.imagegen import run_portrait
    run_portrait(args.input_dir, args.pool_size, args.output_file)


def run_genvideo(args):
    from artsci2019.imagegen import run_genanimation
    run_genanimation(args.input_dir,
                     "temp",
                     args.output_file,
                     args.stack_size,
                     args.pool_size,
                     args.loop)


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
                'level': 'DEBUG',
                'propagate': True
            }
        }
    })


def main():
    parser = create_parser()
    args = parser.parse_args()
    logger.info("Args: {}".format(args))
    if args.subcommand == "display":
        run_display(args)
    elif args.subcommand == "server":
        run_backend(args)
    elif args.subcommand == "portrait":
        run_portrait(args)
    elif args.subcommand == "genvideo":
        run_genvideo(args)


if __name__ == "__main__":
    init_logging()
    logger = logging.getLogger(__name__)
    main()
