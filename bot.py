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


@bot.command(name='stats', aliases=['rank', 'stat'], help='Look up a players Cultris stats by username, user id, or profile url!')
async def stats(ctx, *, query: player_query=None):
    if query == None:
        query = player_query(ctx.message.author.nick or ctx.message.author.name)

    if not query:
        await ctx.send("The query returned no result :(")
        return
    else:
        embedVar = discord.Embed(title=query[0]['Name'], color=0x11806a, url=f"http://gewaltig.net/ProfileView.aspx?userid={query[0]['UserId']}")
        embedVar.add_field(name="Rank", value=query[0]['Rank'], inline=True)
        embedVar.add_field(name="Score", value=str(round(query[0]['Score'],1)), inline=True)
        embedVar.add_field(name="Max Combo", value=query[0]['MaxCombo'], inline=True)

        embedVar.add_field(name="Total Hours", value=str(round(int(query[0]['Playedmin'])/60, 1)), inline=True)
        embedVar.add_field(name="Total Games", value=query[0]['PlayedRounds'], inline=True)
        embedVar.add_field(name="Wins", value=query[0]['Wins'], inline=True)

        embedVar.add_field(name="Peak Rank", value="Coming soon!", inline=True)
        embedVar.add_field(name="Hours (last 7 days)", value="Coming soon!", inline=True)

        await ctx.send(embed=embedVar)

@bot.command(name='rankings', aliases=['ranks', 'leaderboard'], help='Display a page of the leaderboard', usage="")
async def rankings(ctx, page=1):


    player_dict = rankings_query(~-page*20, page*20)

    description = ""
    for i in player_dict:
        player_url = f"http://gewaltig.net/ProfileView.aspx?userid={i['UserId']}"
        description += str(i['Rank']) + ".  " + "[" + i['Name'] + "]" + ("(" + player_url + ")")+ "  (" + str(round(i['Score'], 2)) + ")" + "\n"
        print(i['Name'], round(i['Score'], 2))

    embedVar = discord.Embed(title="Rankings", color=0x11806a, url="https://gewaltig.net/stats.aspx", description=description)

    await ctx.send(embed=embedVar)

@bot.command(name='online', aliases=['active', 'ffa'], help='See who is currently online right now!!')
async def online(ctx):
    ### Load saved df and pass it to function below
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
