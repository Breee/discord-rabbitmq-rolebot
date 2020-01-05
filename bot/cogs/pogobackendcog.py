from discord.ext import commands
import asyncio
import config as config
from rabbitmq_management.rabbitmq_manager import RabbitMQManager, RoleAssignment
from typing import List
from discord import Guild, Role
from utility.globals import LOGGER


class PogoBackendCog(commands.Cog, name="pogobackend"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rabbitmq_manager = RabbitMQManager(bot=self)
        self.rabbitmq_manager.declare_consumer_queue(config.RABBITMQ_CONSUMER_QUEUE)
        self.rabbitmq_manager.declare_sender_queue(config.RABBITMQ_FEEDBACK_QUEUE)
        self.rabbitmq_manager.define_consumer(config.RABBITMQ_CONSUMER_QUEUE,
                                              self.rabbitmq_manager.handle_pogobackend_message)
        self.rabbitmq_manager.start_consumer()

        # create the background task and run it in the background
        self.bg_task = self.bot.loop.create_task(self.process_messages())

    async def on_ready(self):
        for guild in self.bot.guilds:
            await guild.fetch_roles()

    async def process_messages(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(config.LOGGING_CHANNEL_ID)
        while not self.bot.is_closed():
            LOGGER.info('Processing messages')
            messages: List[RoleAssignment] = self.rabbitmq_manager.fetch_messages()
            logging_messages = []
            for message in messages:
                guild: Guild = self.bot.get_guild(message.guild_id)
                role: Role = guild.get_role(message.role_id)
                for uid in message.give_role:
                    member = guild.get_member(uid)
                    if member is not None:
                        await member.add_roles(role)
                        logging_messages.append(f'Gave {member.name} role {role}')
                        LOGGER.info(f'Gave {member.name} role {role}')

                for uid in message.take_role:
                    member = guild.get_member(uid)
                    if member is not None:
                        await member.remove_roles(role)
                        logging_messages.append(f'Took {member.name} role {role}')
                        LOGGER.info(f'Took {member.name} role {role}')
            logs = "\n".join(logging_messages)
            if logs:
                await channel.send(f'```\n{logs}\n```')
            await asyncio.sleep(60)
