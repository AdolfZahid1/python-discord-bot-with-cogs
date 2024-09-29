import asyncio
import logging
import random
from discord.ext import commands


class Games(commands.Cog):

    """A simple roll command"""

    @commands.command(name="roll", brief="Rolls a number from 0 to n. By default 0-100")
    async def roll(self, ctx,arg:int):
        ctx.send(f"{ctx.mention} rolled {random.randrange(0,arg)}")

    @roll.error
    async def roll_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            ctx.send(f"{ctx.mention} rolled {random.randrange(0,100)}")
        elif isinstance(error,commands.ConversionError):
            ctx.send(f"{ctx.mention} number is not int!")

    """Flip a coin command"""

    @commands.command(name="coin", brief="Flip a coin!")
    async def coin(self,ctx):
        coinres = random.randrange(0, 2)
        await ctx.message.delete()
        await ctx.send(f"```{ctx.author.mention} подкинул монетку!```")
        await asyncio.sleep(5)
        if coinres == 1:
            await ctx.send("`Решка!`")
        else:
            await ctx.send("`Орёл!`")

    @coin.error
    async def coin_error(ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            logging.error(error)

async def setup(bot):
    await bot.add_cog(Games(bot))