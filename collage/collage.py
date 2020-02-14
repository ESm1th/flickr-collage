import re
import asyncio

import cv2
import numpy as np


class Collage:

    """Draw collage of images and save it to working directory."""

    def __init__(self, **kwargs):
        self.title = kwargs['title']
        self.quantity = kwargs['quantity']
        self.rows = kwargs['rows']
        self.columns = kwargs['columns']
        self.sizes = self.process_size(kwargs['size'])

    def process_size(self, size: str):
        """
        Check size for appropriate regex pattern and return splitted
        values as list.
        """
        pattern = r'\d,\d'
        if not re.search(pattern, size):
            raise ValueError(
                '-s/--size argument should be entered in format "int,int"'
            )
        sizes = size.split(',')
        return tuple([int(num) for num in sizes])

    async def read_and_convert_image(self, raw_image: bytes):
        """Return image, created from decoded array."""
        if raw_image:
            image_arr = np.frombuffer(raw_image, np.uint8)
            image = cv2.imdecode(image_arr, cv2.IMREAD_UNCHANGED)

            if image is not None:  # can be NoneType! big file? to do..
                if len(image.shape) == 3:

                    if image.shape[2] >= 4:
                        # reshape to get appropriate channel
                        image = image[:, :, :3]

                    return image if image.shape[2] != 0 else None

    async def resize_image(self, image):
        """Resize image."""
        return cv2.resize(image, self.sizes)

    async def process_image(self, raw_image):
        """Creates tasks for reading, converting and resizing passed image."""
        image = await asyncio.create_task(
            self.read_and_convert_image(raw_image)
        )
        if image is not None:
            image = await asyncio.create_task(
                self.resize_image(image)
            )
            if len(image.shape) == 3 and image.shape[2] != 0:
                return image

    async def draw(self, images_queue):
        """
        Processes images from `images_queue` and draw collage from them.
        Ready collage saves in working directory.
        """
        rows = []
        columns = []

        while True:
            raw_image = images_queue.get()

            if raw_image is None:
                break

            image = await asyncio.create_task(self.process_image(raw_image))

            if image is not None:
                columns.append(image)

                if len(columns) == self.columns:
                    rows.append(np.concatenate(columns, axis=1))

                    if len(rows) == self.rows:
                        break
                    columns = []

        collage = np.concatenate(rows, axis=0)
        cv2.imwrite(f'{self.title}.png', collage)
