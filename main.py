import logging
import os

import disnake

from disnake.ext import commands
from dotenv import dotenv_values

# os.system('set G4F_PROXY=116.104.2.81:1080')

logger = logging.getLogger('disnake')
logger.setLevel(logging.DEBUG)
logging_handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
logging_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s:%(name)s:%(message)s'))
logger.addHandler(logging_handler)

SECRETS_ENV = dotenv_values('secrets.env')
DISCORD_TOKEN = SECRETS_ENV.get('DISCORD_TOKEN')

bot = commands.InteractionBot(reload=True)


@bot.event
async def on_ready():
    print('Ready to use')


@bot.slash_command()
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.send(f'pong! latency: {round(bot.latency * 1000)} ms')


@bot.listen('on_slash_command_error')
async def on_error(ctx: disnake.ApplicationCommandInteraction, error: commands.CommandError):
    await ctx.send(embed=disnake.Embed(title='Ой... Случилась ошибка :(',
                                       description=error,
                                       color=disnake.Colour.yellow()))
    logger.error(error)

logger.info('Loading cogs')
bot.load_extension('cogs.dnd')
logger.info('Launching bot')
bot.run(DISCORD_TOKEN)
