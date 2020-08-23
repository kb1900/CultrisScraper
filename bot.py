# bot.py
import os, random
from tools import *

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='stats', help='look up a users cultris stats!')
async def stats(ctx, player_name: str):
    ### Load saved df and pass it to function below
    df = pd.read_pickle("Player_Dump")
    info = player_stats_by_name(player_name, df)

    embedVar = discord.Embed(title=info[0]['Name'], color=0x11806a)
    embedVar.add_field(name="Rank", value=info[0]['Rank'], inline=True)
    embedVar.add_field(name="Score", value=str(round(info[0]['Score'],1)), inline=True)
    embedVar.add_field(name="Max Combo", value=info[0]['MaxCombo'], inline=True)

    embedVar.add_field(name="Total Hours", value=str(round(int(info[0]['Playedmin'])/60, 1)), inline=True)
    embedVar.add_field(name="Total Games", value=info[0]['PlayedRounds'], inline=True)
    embedVar.add_field(name="Wins", value=info[0]['Wins'], inline=True)

    embedVar.add_field(name="Peak Rank", value="Coming soon!", inline=True)
    embedVar.add_field(name="Hours (last 7 days)", value="Coming soon!", inline=True)

    await ctx.send(embed=embedVar)

@bot.command(name='online', help='check out whose online!')
async def stats(ctx):
    ### Load saved df and pass it to function below
    df = pd.read_pickle("Player_Dump")
    info = show_online_players()
    ffa = ', '.join(info[0])
    rookie = ', '.join(info[1])
    cheese = ', '.join(info[2])
    other = ', '.join(info[3])
    team = ', '.join(info[4])
    afk = ', '.join(info[-1])


    embedVar = discord.Embed(title='Players Online', color=0x11806a)
    if len(ffa) > 0:
        embedVar.add_field(name="FFA", value=ffa, inline=True)
    if len(rookie) > 0:
        embedVar.add_field(name="Rookie Playground", value=rookie, inline=True)
    if len(cheese) > 0:
        embedVar.add_field(name="Cheese Factory", value=cheese, inline=True)
    if len(team) > 0:
        embedVar.add_field(name="Teams", value=team, inline=True)
    if len(other) > 0:
        embedVar.add_field(name="Other", value=other, inline=True)
    if len(afk) > 0:
        embedVar.add_field(name="AFK", value=afk, inline=True)

    await ctx.send(embed=embedVar)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)
