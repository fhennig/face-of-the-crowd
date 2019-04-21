#! /usr/bin/env python3
import argparse

from artsci2019.app import Application
from artsci2019.portrait import PortraitGen
from artsci2019.backend_facade import ProcessingBackend


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--camera_input",
        default=1,
        type=int,
        help="Which camera to use."
    )
    parser.add_argument(
        "--rotate",
        action='store_true',
        default=False,
        help="Whether to rotate the image."
    )
    parser.add_argument(
        "--fullscreen",
        action='store_true',
        default=False,
        help="Whether to display the generated image fullscreen."
    )
    parser.add_argument(
        "--pool_size",
        default=4,
        type=int,
        help="The number of parallel processes to use."
    )
    parser.add_argument(
        "--remote",
        action='store_true',
        default=False,
        help="Whether to use a remote backend or run everything locally."
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

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    if args.remote:
        processing_backend = ProcessingBackend(args.host, args.port)
    else:
        processing_backend = PortraitGen(5, args.pool_size)
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


if __name__ == "__main__":
    main()
