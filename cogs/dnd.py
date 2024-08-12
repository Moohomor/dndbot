import io
import json

import disnake
from disnake import ButtonStyle
from disnake.ext import commands
from disnake.ui import Button
from disnake.utils import MISSING

import prompt


class Dnd(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.guilds = {}

    @commands.slash_command()
    async def test(self, inter: disnake.ApplicationCommandInteraction, r):
        await inter.response.defer()
        print(self.guilds)
        response = await prompt.gpt(r, inter.guild_id)
        if response is None:
            await inter.send('Sorry... An error occurred :(')
        else:
            await inter.send(response)

    @commands.slash_command()
    async def join(self, inter: disnake.ApplicationCommandInteraction, name):
        await inter.response.defer()
        if inter.guild_id not in self.guilds:
            self.guilds[inter.guild_id] = {'players': {}, 'started': False}
        if self.guilds[inter.guild_id]['started']:
            await inter.send('Игра уже началась')
        elif inter.author.id in self.guilds[inter.guild_id]['players']:
            await inter.send('Вы уже в игре! Чтобы покинуть её, введите /leave')
        elif name in list(self.guilds[inter.guild_id]['players'].values()):
            await inter.send('Это имя уже занято. Пожалуйста, введите эту команду заново с другим именем')
        else:
            self.guilds[inter.guild_id]['players'][inter.author.id] = name
            await inter.send('Вы присоединились к игре под именем ' + name)

    @commands.slash_command()
    async def say(self, inter: disnake.ApplicationCommandInteraction, message: str, image_required: bool = True):
        await inter.response.defer()
        if inter.guild_id not in self.guilds:
            await inter.send('Чтобы начать игру, впишите /start')
            return
        if inter.author.id not in self.guilds[inter.guild_id]["players"]:
            await inter.send('Ты не играешь')
            return
        await inter.send(embed=disnake.Embed(title='Подождите...',
                                             description='Процесс не моментальный, так ещё помимо этого было запрошено '
                                                         'изображение: это может значительно увеличить время генерации'
                                             if image_required else '',
                                             color=disnake.Color.green()))
        response = await prompt.gpt(f'{self.guilds[inter.guild_id]['players'][inter.author.id]} says: {message}',
                                    inter.guild_id)
        if response is None:
            del prompt.chat_history[inter.guild_id][-1]
            raise Exception('Response is empty')
        with open('1.txt', 'w') as f:
            f.write(response)
        while response[0] != '{':
            response = '\n'.join(response.split('\n')[1:])
        while response[-1] != '}':
            response = '\n'.join(response.split('\n')[:-1])
        print(response.strip())
        try:
            json_response = json.loads(response.strip())
        except json.JSONDecodeError as e:
            await inter.send(response)
            del prompt.chat_history[inter.guild_id][-2]
            raise e
        # await inter.send(f'*{json_response['prompt']}*')
        data = await prompt.image(json_response['prompt'])
        await inter.edit_original_response(json_response['resp'], file=(
            MISSING if data is None else disnake.File(io.BytesIO(data), 'illustration.png')))

    @commands.slash_command()
    async def start(self, inter: disnake.ApplicationCommandInteraction):
        if inter.guild_id in self.guilds and self.guilds[inter.guild_id]['started']:
            await inter.send('Игра уже началась')
            return
        await inter.response.defer()
        response = await prompt.gpt('You are dungeon master. Player list: '
                                    f'{', '.join(self.guilds[inter.guild_id]["players"].values())}. '
                                    # 'Твой первый ответ - описание локации.'
                                    # 'Отвечай только и полностью в формате JSON, без примечаний и форматирования:\n'
                                    'Reply in russian using only JSON and nothing more.\nFormat:\n{'
                                    'resp: your reply as dungeon master (only text),\n'
                                    'prompt: a DALL-E prompt to create illustration (only text)\n}',
                                    inter.guild_id, 'system')
        if response is None:
            del prompt.chat_history[inter.guild_id][-1]
            raise Exception('Response is empty')
        with open('1.txt', 'w') as f:
            f.write(response)
        while response[0] != '{':
            response = '\n'.join(response.split('\n')[1:])
        while response[-1] != '}':
            response = '\n'.join(response.split('\n')[:-1])
        print(response.strip())
        try:
            jresp = json.loads(response.strip())
        except json.JSONDecodeError as e:
            del prompt.chat_history[inter.guild_id][-2]
            raise e
        await inter.send(jresp['resp'])
        await inter.send(f'*{jresp['prompt']}*')
        if inter.guild_id in self.guilds:
            self.guilds[inter.guild_id]['started'] = True
            return
        self.guilds[inter.guild_id] = {'players': {}, 'started': False}

    @commands.slash_command()
    async def end(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            'Хотите завершить игру и удалить всю историю сообщений?\n'
            '**Это действие нельзя отменить!**',
            components=[
                Button(label='Да, давай, ура', style=ButtonStyle.danger, custom_id='end'),
                Button(label='Нет, пожалуйста, не надо', custom_id='nothing')
            ]
        )

    @commands.Cog.listener('on_button_click')
    async def button_listener(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        if inter.component.custom_id == 'end':
            self.guilds[inter.guild_id] = {'players': {}, 'started': False}
            prompt.clear_history(inter.guild_id)
            await inter.send('Готово')

    # @commands.Cog.listener('on_message')
    # async def on_message(self, message: disnake.Message):
    #     if message.guild.id in self.guilds and message.author.id in self.players:
    #         await message.reply(f'User {message.author}')


def setup(bot: commands.InteractionBot):
    bot.add_cog(Dnd(bot))
