# bot.py
import discord
import os
from discord.ext import commands
from lookup import Lookup
from dotenv import load_dotenv


load_dotenv()
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


bot.add_cog(Lookup(bot))

bot.run(os.getenv("DISCORD_TOKEN"))
