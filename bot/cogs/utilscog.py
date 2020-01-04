from discord.ext import commands
import time


class UtilsCog(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(help="Ping the bot, if he does not answer you're fucked.")
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command(help="Return how long the bot is operational.")
    async def uptime(self, ctx):
        seconds = time.time() - self.start_time
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        await ctx.send('Online for %.3f seconds (that are %.3f minutes or %.3f hours or %.3f days)' % (
            seconds, minutes, hours, days))

    @commands.command(help="Show all servers (owner only)")
    @commands.is_owner()
    async def servers(self, ctx):
        guilds = []
        async for guild in self.bot.fetch_guilds(limit=150):
            guilds.append("- %s (%s)" % (guild.name, guild.id))
        await ctx.send("__**Servers**__\n%s" % "\n".join(guilds))

    @commands.command(help="Leave a server (owner only)")
    @commands.is_owner()
    async def leave(self, ctx, id):
        guild = self.bot.get_guild(int(id))
        channel = ctx.channel
        await ctx.send("Are you sure you want to leave Server %s?" % guild)

        def check(m):
            return m.channel == channel

        msg = await self.bot.wait_for('message', check=check, timeout=10)
        if msg.content == "yes":
            await ctx.send("you said yes, leaving")
            await guild.leave()
        elif msg.content == "no":
            await ctx.send("you said no")
        else:
            await ctx.send("No valid answer")
