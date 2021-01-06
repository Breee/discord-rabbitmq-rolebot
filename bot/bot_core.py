from discord.ext import commands
import discord
from _datetime import datetime
import aiohttp
from utility.globals import LOGGER
from cogs.utilscog import UtilsCog
from cogs.pogobackendcog import PogoBackendCog
import traceback
import config as config


class BotBase(commands.Bot):

    def __init__(self, description, intents):
        super().__init__(command_prefix=[config.PREFIX], description=description, pm_help=None,
                         help_attrs=dict(hidden=True), intents=intents)

        self.add_cog(UtilsCog(bot=self))
        self.add_cog(PogoBackendCog(bot=self))
        self.session = aiohttp.ClientSession(loop=self.loop)


    '################ EVENTS ###############'

    async def on_ready(self):
        LOGGER.info('Bot is ready.')
        self.start_time = datetime.utcnow()
        await self.change_presence(activity=discord.Game(name=config.PLAYING))
        # make mentionable.
        self.command_prefix.extend([f'<@!{self.user.id}> ', f'<@{self.user.id}> '])

    def run(self):
        super().run(config.BOT_TOKEN, reconnect=True)

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_resumed(self):
        print('resumed...')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.NotOwner):
            await ctx.author.send('You are not my Master!')
        elif isinstance(error, commands.CommandInvokeError):
            LOGGER.critical(f'In {ctx.command.qualified_name}:')
            traceback.print_tb(error.original.__traceback__)
            LOGGER.critical(f'{error.original.__class__.__name__}: {error.original}')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                    'Sorry. This command is not how this command works, !help <command_name> to display usage')
        else:
            LOGGER.critical(error)
