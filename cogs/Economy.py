import db
import discord
import logging
import json
from discord.ext import commands

with open('login.json', encoding='utf-8') as jsonfile:
    login = json.load(jsonfile)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=r'/home/pi/Bookshelf/db.log', filemode='a', format=FORMAT)
TYPE = discord.ActivityType.listening


class Guild(commands.Cog):
    """Guild class"""

    def __init__(self, bot):
        """Init function"""
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Add all server members to database """
        logging.warning('Hello World!')
        await self.bot.change_presence(activity=discord.Activity(type=TYPE, name=login["default-activity"]))
        for guild in self.bot.guilds:
            print(f'In {guild.name}')
            async for member in guild.fetch_members(limit=None):
                await db.insert_member(member.id,member.guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await db.insert_member(member.id, member.guild.id)


class Economy(commands.Cog):
    """Economy commands"""

    @commands.command(name="add-balance", brief="adds balance to user")
    async def add_balance(self, ctx, member: discord.Member, arg: int):
        """Add balance command"""
        if await db.add_balance(member.id, arg):
            await ctx.send(f"Added balance to {member.mention}")
        else:
            await ctx.send(f"Failed to add balance to {member.mention}")

    @add_balance.error
    async def add_balance_error(self, ctx, error):
        """Add balance error handle"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument, try help instead")
        elif isinstance(error, commands.ConversionError):
            await ctx.send(f"Conversion error, try other number instead")

    @commands.command(name="remove-balance", brief="removes balance from user")
    async def remove_balance(self, ctx, member: discord.Member, arg: int):
        """Remove balance command"""
        if await db.remove_balance(member.id, arg):
            await ctx.send(f"Removed balance from {member.mention}")
        else:
            await ctx.send(f"Failed to remove balance from {member.mention}")

    @remove_balance.error
    async def remove_balance_error(self, ctx, error):
        """Remove balance command error handle"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument, try help instead")
        elif isinstance(error, commands.ConversionError):
            await ctx.send(f"Conversion error, try other number instead")

    @commands.command(name="set-balance", brief="sets balance users balance to %value%")
    async def set_balance(self, ctx, member: discord.Member, arg: int):
        """Set balance command"""
        if await db.set_balance(member.id, arg):
            await ctx.send(f"Set balance to {member.mention}")
        else:
            await ctx.send(f"Failed to set balance to {member.mention}")

    @set_balance.error
    async def set_balance_error(self, ctx, error):
        """SetBalance command error handle"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument, try help instead")
        elif isinstance(error, commands.ConversionError):
            await ctx.send(f"Conversion error, try other number instead")

    @commands.command(name="bal", brief="SHows balance of user")
    async def bal(self, ctx, member: discord.Member):
        """Get balance command"""
        bank, cash = await db.get_balance(member.id)
        total = bank + cash
        await ctx.send(f"Cash: {cash} Bank: {bank} Total: {total}")

    @commands.command(name="depos", brief="Deposit your cash to bank")
    async def depos(self, ctx):
        """Deposit to bank command"""
        if await db.deposit(ctx.message.author.id):
            await ctx.send("Deposited")
        else:
            await ctx.send("Failed to deposit")

    @commands.command(name="rob", brief="Rob user")
    async def rob(self, ctx, member: discord.Member):
        """Rob someone command"""
        if await db.rob(ctx.message.author.id, member.id):
            await ctx.send(f"You robed {member.mention}")
        else:
            await ctx.send(f"Failed to rob, {member.mention} has nothing to rob")

    @rob.error
    async def rob_error(self, ctx, error):
        """Rob command error handle"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument, try help instead")

    @commands.command(name="withdraw", brief="Withdraw from bank")
    async def withdraw(self, ctx, arg: int):
        """Withdraw from bank command"""
        if await db.withdraw(ctx.message.author.id, arg):
            await ctx.send(f"Withdrawed {arg} from your bank")
        else:
            await ctx.send("Failed to withdraw, not enough money on balance")

    @withdraw.error
    async def withdraw_error(self, ctx, error):
        """Withdraw command error handle"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument, try help instead")
        elif isinstance(error, commands.ConversionError):
            await ctx.send(f"Conversion error, try other number instead")

    @commands.command(name="top", brief="Get top users")
    async def top(self, ctx):
        """Member top command"""
        pre_top = await db.top()
        print(pre_top)
        answer = ''
        for item in pre_top:
            answer = answer + item
        await ctx.send(f"```{answer}```")


async def setup(bot):
    """Init"""
    await bot.add_cog(Guild(bot))
    await bot.add_cog(Economy(bot))
