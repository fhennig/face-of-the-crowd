#! /usr/bin/env python3
import argparse

from artsci2019.app import Application


def create_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="subcommand"
    )

    run = subparsers.add_parser("run")

    run.add_argument(
        "--camera_input",
        default=1,
        type=int,
        help="Which camera to use."
    )
    run.add_argument(
        "--rotate",
        action='store_true',
        default=False,
        help="Whether to rotate the image."
    )
    run.add_argument(
        "--fullscreen",
        action='store_true',
        default=False,
        help="Whether to display the generated image fullscreen."
    )
    run.add_argument(
        "--remote",
        action='store_true',
        default=False,
        help="Whether to use a remote rpc or run everything locally."
    )
    run.add_argument(
        "--host",
        default="127.0.0.1",
        help="The remote host IP adress."
    )
    run.add_argument(
        "--port",
        default=5000,
        type=int,
        help="The remote port."
    )

    backend = subparsers.add_parser("server")

    # add common commands
    for p in [run, backend]:
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

    return parser


def init_logging():
    import logging.config
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


def run(args):
    if args.remote:
        from artsci2019.rpc.client import RemoteBackend
        processing_backend = RemoteBackend(args.host, args.port)
    else:
        from artsci2019.backend.backend import Backend
        processing_backend = Backend(args.stack_size, args.pool_size, args.image_dir)
    a = Application(args.camera_input,
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
    from artsci2019.rpc.server import create_app
    app = create_app(args.stack_size, args.pool_size, args.image_dir)
    app.run(debug=True)


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    init_logging()
    if args.subcommand == "run":
        run(args)
    elif args.subcommand == "server":
        run_backend(args)


if __name__ == "__main__":
    main()
