import base64
import logging

import g4f
from dotenv import dotenv_values

from text2image_api import Text2ImageAPI

SECRETS_ENV = dotenv_values('secrets.env')
logger = logging.getLogger('disnake')
chat_history = {}


def trim_history(history, max_length=16384):
    current_length = sum(len(message["content"]) for message in history)
    # while history and current_length > max_length:
    #     removed_message = history.pop([idx for idx, i in enumerate(history) if i['role'] == 'assistant'][0])
    #     current_length -= len(removed_message["content"])
    while history and current_length > max_length:
        removed_message = history.pop(1)
        current_length -= len(removed_message["content"])
    return history


def clear_history(chat_id):
    if chat_id in chat_history:
        chat_history[chat_id] = []


async def gpt(prompt, chat_id, role='user'):
    try:
        if chat_id not in chat_history:
            chat_history[chat_id] = []
        chat_history[chat_id] += [{"role": role, "content": prompt}]
        chat_history[chat_id] = trim_history(chat_history[chat_id])
        logger.info('Trying to access GPT')
        print(chat_history[chat_id])
        response = await g4f.ChatCompletion.create_async(
            response_format={'type': 'json_object'},
            provider=g4f.Provider.You,
            model=g4f.models.default,
            # model='gpt-3.5-turbo',
            messages=(chat_history[chat_id] if chat_id else prompt)
        )
        if not response:
            del chat_history[chat_id][-1]
            raise Exception("Response is empty")
        chat_history[chat_id] += [{"role": "assistant", "content": response}]
        return response  # .choices[0].message.content
    except Exception as e:
        logger.error(e)
        return


async def image(prompt):
    logger.info('Trying to access image generator')
    # g4f.cookies.set_cookies('gemini.google.com', {
    #     '__Secure-1PSID': SECRETS_ENV['__Secure-1PSID'],
    #     '__Secure-1PSIDCC': SECRETS_ENV['__Secure-1PSIDCC'],
    #     '__Secure-1PSIDTS': SECRETS_ENV['__Secure-1PSIDTS']
    # })
    # response = g4f.client.Client(image_provider=g4f.Provider.Gemini).images.generate(
    #     model='gemini',
    #     prompt=prompt,
    #     no_sandbox=True
    # )
    # g4f.cookies.set_cookies('.bing.com', {
    #     '_U': SECRETS_ENV['_U']
    # })
    # response = g4f.client.Client(image_provider=g4f.Provider.Bing).images.generate(
    #     model='dall-e-3',
    #     prompt=prompt,
    #     # patch_provider=g4f.Provider.bing.create_images.patch_provider,
    #     no_sandbox=True
    # )
    api = Text2ImageAPI(SECRETS_ENV["K_KEY"], SECRETS_ENV["K_SECRET"])
    model_id = api.get_model()
    uuid = api.generate(prompt, model_id)
    response = await api.check_generation(uuid)
    return base64.b64decode(response[0])  # .data[0]
