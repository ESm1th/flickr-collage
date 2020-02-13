import re

import cv2
import numpy as np


class Collage:

    def __init__(self, **kwargs):
        self.text = kwargs['text']
        self.quantity = kwargs['quantity']
        self.rows = kwargs['rows']
        self.columns = kwargs['columns']
        self.sizes = self.process_size(kwargs['size'])

    def process_size(self, size: str):
        pattern = r'\d,\d'
        if not re.search(pattern, size):
            raise ValueError(
                '-s/--size argument should be entered in format "int,int"'
            )
        sizes = size.split(',')
        return tuple([int(num) for num in sizes])

    async def read_and_convert_image(self, raw_image: bytes):
        if raw_image:
            image_arr = np.frombuffer(raw_image, np.uint8)
            image = cv2.imdecode(image_arr, cv2.IMREAD_UNCHANGED)
            try:
                if image.shape[2] == 4:
                    image = image[:, :, :3]
            except Exception as error:  # to do
                print(image)
                raise error
            return image
        return None

    def draw(self, images: list):
        # draw empty black canvas
        collage = np.zeros(
            shape=(self.sizes[1] * self.rows, self.sizes[0] * self.columns, 3),
            dtype=np.uint8
        )

        pointer = [0, 0]
        for image in images:
            image = cv2.resize(image, self.sizes)

            # draw image on black canvas
            collage[
                pointer[1]:pointer[1] + self.sizes[1],
                pointer[0]:pointer[0] + self.sizes[0]
            ] = image
            pointer[0] += self.sizes[0]  # increment pointer's `x` position

            if pointer[0] >= self.rows * self.sizes[0]:
                pointer[1] += self.sizes[1]  # increment pointer's `y` position
                pointer[0] = 0

        cv2.imshow('Collage', collage)
        cv2.waitKey(0)
