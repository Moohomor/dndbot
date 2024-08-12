import logging
import asyncio
import json

import aiohttp
import requests

logger = logging.getLogger('disnake')


class Text2ImageAPI:

    def __init__(self, api_key, secret_key):
        self.URL = 'https://api-key.fusionbrain.ai/'
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    async def check_generation(self, request_id, attempts=90, delay=50):
        while attempts > 0:
            logger.info(f'FusionBrain attempts left: {attempts}')
            async with aiohttp.ClientSession() as session:
                async with session.get(self.URL + 'key/api/v1/text2image/status/' + request_id,
                                       headers=self.AUTH_HEADERS) as response:
                    data = await response.json()
                    if data['status'] == 'DONE':
                        return data['images']

            attempts -= 1
            await asyncio.sleep(delay)
