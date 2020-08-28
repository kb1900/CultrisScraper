import discord
import tools, database
from discord.ext import commands


class Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="stats",
        aliases=["rank", "stat"],
        help="Look up a players Cultris stats by username, user id, or profile url!",
    )
    async def stats(self, ctx, *, query: tools.player_query = None):
        if query == None:
            query = tools.player_query(
                ctx.message.author.nick or ctx.message.author.name
            )

        if not query:
            await ctx.send("The query returned no result :(")
            return

        player = query[0]

        # TODO: change win rate to past 14 days using player_DB
        # TODO: NET score over last 7 days using player_DB
        peak_rank = database.calculate_peak(
            database.select_player_by_id(
                database.create_connection("playerDB.db"), query[0]["UserId"]
            )
        )
        recent_mins = database.calculate_week_playtime(
            database.select_player_by_id(
                database.create_connection("playerDB.db"), query[0]["UserId"]
            )
        )
        if not peak_rank:
            peak_rank = "Coming soon!"

        embed = discord.Embed(
            title=player["Name"], color=0x11806A, url=tools.player_url(query[0])
        )
        embed.add_field(name="Rank", value=player["Rank"], inline=True)
        embed.add_field(name="Score", value=f"{player['Score']:.1f}", inline=True)
        embed.add_field(name="Peak", value=peak_rank, inline=True)
        embed.add_field(name="Best Combo", value=player["MaxCombo"], inline=True)
        embed.add_field(
            name="Max BPM", value=round(player["MAXRoundBpm"], 1), inline=True
        )
        embed.add_field(
            name="Avg BPM", value=round(player["AVGRoundBpm"], 1), inline=True
        )
        embed.add_field(name="Games", value=player["PlayedRounds"], inline=True)
        embed.add_field(name="Wins", value=player["Wins"], inline=True)
        embed.add_field(
            name="Win Rate",
            value=str(round((player["Wins"] / player["PlayedRounds"] * 100), 1)) + "%",
            inline=True,
        )
        embed.add_field(
            name="Total Hours", value=f"{player['Playedmin']/60:.1f}", inline=True
        )
        embed.add_field(
            name="Last 7 Days", value=str(recent_mins) + " mins", inline=True
        )

        await ctx.send(embed=embed)

    @commands.command(
        name="rankings",
        aliases=["ranks", "leaderboard", "ranking"],
        help="Display a page of the leaderboard",
        usage="",
    )
    async def rankings(self, ctx, page=1):
        player_dict = tools.rankings_query(page)
        description = ""
        for i in player_dict:
            description += f"{i['Rank']}. [{i['Name']}]({tools.player_url(i)}) ({i['Score']:.2f})\n"
            print(f"{i['Name']} {i['Score']:.2f}")
        await ctx.send(
            embed=discord.Embed(
                title="Rankings",
                color=0x11806A,
                url="https://gewaltig.net/stats.aspx",
                description=description,
            )
        )

    @commands.command(
        name="online",
        aliases=["active", "ffa"],
        help="See who is currently online right now!!",
    )
    async def online(self, ctx):
        info = tools.show_online_players()
        ffa = ", ".join(info[0])
        rookie = ", ".join(info[1])
        cheese = ", ".join(info[2])
        other = ", ".join(info[3])
        team = ", ".join(info[4])
        afk = ", ".join(info[-1])

        embedVar = discord.Embed(
            title="Players Online", color=0x11806A, url="https://gewaltig.net/"
        )
        if len(ffa):
            embedVar.add_field(name="FFA", value=ffa, inline=True)
        if len(rookie):
            embedVar.add_field(name="Rookie Playground", value=rookie, inline=True)
        if len(cheese):
            embedVar.add_field(name="Cheese Factory", value=cheese, inline=True)
        if len(team):
            embedVar.add_field(name="Teams", value=team, inline=True)
        if len(other):
            embedVar.add_field(name="Other", value=other, inline=True)
        if len(afk):
            embedVar.add_field(name="AFK", value=afk, inline=True)
        await ctx.send(embed=embedVar)
