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

    def __init__(self, api_key: str, search_text: str, quantity: int = 100):
        self.params.update({'api_key': api_key, 'per_page': quantity})
        self.search_text = search_text
        self.quantity = quantity

    async def make_request(self, payload: dict, format='json'):
        async with request('get', self.endpoint, params=payload) as response:
            data = await asyncio.create_task(response.json())
            return data

    async def search_photos(self, urls_queue):
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
            if photo['ispublic'] == 1
        ]
        await asyncio.create_task(self.get_photos_urls(photos_ids, urls_queue))

    async def get_photo_sizes(self, payload, urls_queue):
        response_data = await asyncio.create_task(self.make_request(payload))
        await asyncio.create_task(urls_queue.put(response_data))

    async def get_photos_urls(self, photos_ids, urls_queue):
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

    async def get_photo(self, url, image_queue):
        async with request('get', url) as response:
            image = await asyncio.create_task(response.read())
            await asyncio.create_task(image_queue.put(image))

    async def download_photos(self, urls_queue, image_queue):
        while True:
            photo = await asyncio.create_task(urls_queue.get())

            if photo is None:
                await asyncio.create_task(image_queue.put(None))
                break

            url = photo['sizes']['size'][-1]['source']
            task = asyncio.create_task(self.get_photo(url, image_queue))
            await task

    async def fetch(self):
        urls = asyncio.Queue()
        images = asyncio.Queue()
        await asyncio.create_task(self.search_photos(urls))
        await asyncio.create_task(self.download_photos(urls, images))


if __name__ == '__main__':
    from time import time

    start = time()
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.environ['API_KEY']
    fetcher = ImageFetcher(api_key, 'love', quantity=20)
    asyncio.run(fetcher.fetch())
    end = time()
    print(end - start)