import os
import asyncio
import argparse
from datetime import datetime

from dotenv import load_dotenv
from aiomultiprocess import Process
from aiomultiprocess.core import get_manager

from fetcher import ImageFetcher
from collage import Collage


def create_argument_parser():
    """
    Create argument parser object to parse command line arguments.
    """
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        '-t', '--text', required=True, type=str,
        help='text for searching images'
    )
    args_parser.add_argument(
        '-q', '--quantity', default=100, type=int,
        help='quantity of images for collage'
    )
    args_parser.add_argument(
        '-r', '--rows', default=5, type=int,
        help='rows of images in collage'
    )
    args_parser.add_argument(
        '-c', '--columns', default=5, type=int,
        help='columns of images in collage'
    )
    args_parser.add_argument(
        '-s', '--size', default='240,180', type=str,
        help='size of image as "width,height" form'
    )
    return args_parser


async def fetch_images(
    api_key: str, text: str, quantity: int, images_queue: 'AutoProxy[Queue]'
) -> None:
    """
    Create `ImageFetcher` instance and schedule task to fetch images
    from `Flickr API`.
    """
    fetcher = ImageFetcher(api_key, text, quantity)
    await asyncio.create_task(fetcher.fetch(images_queue))


async def create_collage(
    title: str,
    quantity: int,
    rows: int,
    columns: int,
    size: str,
    image_queue: 'AutoProxy[Queue]'
):
    """
    Create `Collage` instance and schedule task to draw collage from images.
    """
    collage = Collage(
        title=title,
        quantity=quantity,
        rows=rows,
        columns=columns,
        size=size
    )
    await asyncio.create_task(collage.draw(image_queue))


async def main(**kwargs):
    """
    Main function. Create two main processes:
        - to fetch images from `Flickr API`
        - to draw collage from fetched images
    """
    images_queue = get_manager().Queue()
    fetch_process = Process(
        target=fetch_images,
        args=(
            kwargs['api_key'],
            kwargs['text'],
            kwargs['quantity'],
            images_queue
        )
    )
    await fetch_process

    collage_process = Process(
        target=create_collage,
        args=(
            kwargs['title'],
            kwargs['quantity'],
            kwargs['rows'],
            kwargs['columns'],
            kwargs['size'],
            images_queue
        )
    )
    await collage_process


if __name__ == '__main__':
    load_dotenv()

    argument_parser = create_argument_parser()
    args = vars(argument_parser.parse_args())
    args.update({'api_key': os.environ['API_KEY']})

    timestamp = datetime.now()
    title = '{text}_{date}'.format(
        text=args['text'],
        date=str(timestamp)
    )
    args.update({'title': title})

    asyncio.run(main(**args))
