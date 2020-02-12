import os
import time
import asyncio
from copy import deepcopy
from types import SimpleNamespace

import aiohttp
import requests
from dotenv import load_dotenv


METHODS = {
    'search': 'flickr.photos.search',
    'info': 'flickr.photos.getInfo'
}


class FlickrAPI:

    endpoint = 'https://www.flickr.com/services/rest/'
    params = {
        'format': 'json',
        'nojsoncallback': 1
    }
    methods = SimpleNamespace(**METHODS)

    def __init__(self, api_key: str, search_text: str, quantity: int = 100):
        self.params.update({'api_key': api_key, 'perpage': quantity})
        self.search_text = search_text

    async def get_photo_info(self, session, payload):
        async with session.get(self.endpoint, params=payload) as response:
            if response.status == 200:
                print(await response.json())

    async def get_photos_urls(self, session, photos_data):
        payload = deepcopy(self.params)
        payload.update({'method': self.methods.info})

        tasks = []
        for photo in photos_data:
            payload.update({'photo_id': photo['id']})  # secret?
            task = asyncio.create_task(self.get_photo_info(session, payload))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def fetch(self):
        async with aiohttp.ClientSession() as session:
            payload = deepcopy(self.params)
            payload.update(
                {'method': self.methods.search, 'text': self.search_text}
            )
            async with session.get(self.endpoint, params=payload) as response:
                data = await response.json()
                photos = data['photos']['photo']
                photos_data = [
                    {'id': photo['id'], 'secret': photo['secret']}
                    for photo in photos if photo['ispublic'] == 1
                ]
                await self.get_photos_urls(session, photos_data)



if __name__ == '__main__':
    start_time = time.time()
    load_dotenv()
    API_KEY = os.environ['API_KEY']
    api = FlickrAPI(API_KEY, 'love')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(api.fetch())
    end_time = time.time()
    print(end_time - start_time)
