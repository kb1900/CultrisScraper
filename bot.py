# bot.py
import discord
import os
from discord.ext import commands
from lookup import Lookup

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.add_cog(Lookup(bot))

bot.run('MjQzODQwNzA2MDc2OTk5Njgw.WBukWg.B1fzwDLzru6oEFbN88gZeSBO9dQ')
