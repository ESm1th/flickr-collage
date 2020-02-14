import asyncio
from copy import copy
from types import SimpleNamespace

from aiohttp import request


METHODS = {
    'search': 'flickr.photos.search',
    'sizes': 'flickr.photos.getSizes'
}


class ImageFetcher:

    endpoint = 'https://www.flickr.com/services/rest/'
    params = {
        'format': 'json',
        'nojsoncallback': 1
    }
    methods = SimpleNamespace(**METHODS)

    def __init__(
        self,
        api_key: str,
        search_text: str,
        quantity: int
    ) -> None:
        self.params.update({'api_key': api_key, 'per_page': quantity})
        self.search_text = search_text
        self.quantity = quantity

    async def make_request(self, payload: dict, format='json') -> dict:
        """
        Send request with passed payload and return `json` data of response.
        """
        async with request('get', self.endpoint, params=payload) as response:
            data = await asyncio.create_task(response.json())
            return data

    async def search_photos(self, urls_queue: 'AutoProxy[Queue]') -> None:
        """
        Create and send request to get photos from `flickr` with specified
        parameters. Process received photos and create tasks to fetch urls for
        each photo.
        """
        payload = copy(self.params)
        payload.update(
            {
                'method': self.methods.search,
                'text': self.search_text
            }
        )
        data = await asyncio.create_task(self.make_request(payload))
        photos = data['photos']['photo']
        photos_ids = [
            photo['id'] for photo in photos
            if photo['ispublic'] == 1  # only public images
        ]
        await asyncio.create_task(self.get_photos_urls(photos_ids, urls_queue))

    async def get_photo_sizes(
        self, payload: dict, urls_queue: 'asyncio.queues.Queue'
    ) -> None:
        """
        Send request to get response with photo sizes and put `json` data
        of this request to queue for further processing.
        """
        response_data = await asyncio.create_task(self.make_request(payload))
        await asyncio.create_task(urls_queue.put(response_data))

    async def get_photos_urls(
        self, photos_ids: list, urls_queue: 'asyncio.queues.Queue'
    ) -> None:
        """
        For each photo in `photo_ids` argument create task to send request
        with appropriate payload.
        """
        tasks = []

        for photo_id in photos_ids:
            payload = copy(self.params)
            payload.update(
                {
                    'method': self.methods.sizes,
                    'photo_id': photo_id
                }
            )
            task = asyncio.create_task(
                self.get_photo_sizes(payload, urls_queue)
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
        await asyncio.create_task(urls_queue.put(None))

    async def get_photo(
        self, url: str, image_queue: 'AutoProxy[Queue]'
    ) -> None:
        """
        Send request to get response with image and put received image to
        `image_queue` as bytes.
        """
        async with request('get', url) as response:
            image = await asyncio.create_task(response.read())
            image_queue.put(image)

    async def download_photos(
        self, urls_queue: 'asyncio.queues.Queue',
        image_queue: 'AutoProxy[Queue]'
    ) -> None:
        """
        Get photo data from `urls_queue`, parse it and create task to download
        photo file.
        """
        while True:
            photo = await asyncio.create_task(urls_queue.get())

            if photo is None:
                image_queue.put(None)
                break

            url = photo['sizes']['size'][-1]['source']
            task = asyncio.create_task(self.get_photo(url, image_queue))
            await task

    async def fetch(self, images_queue: 'AutoProxy[Queue]'):
        """
        Main method to run in `asyncio.run`. Create two main tasks: one for
        searching and getting urls for downloading images and second - to check
        queue with urls for downloading images and use them to download images.
        """
        urls = asyncio.Queue()
        await asyncio.create_task(self.search_photos(urls))
        await asyncio.create_task(self.download_photos(urls, images_queue))
