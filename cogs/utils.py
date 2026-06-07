import discord
from discord.ext import commands
from discord import app_commands
import datetime, asyncio
from config import ROLES, CHANNELS, EMOJIS, THUMBNAIL_URL, is_staff, has_roles
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        if not has_roles(ctx.author, ["owner", "co_owner", "ceo"]):
            await ctx.send(f"{E['error']} Δεν έχεις δικαίωμα.")
            return
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="say2")
    async def say2(self, ctx, *, message: str):
        if not has_roles(ctx.author, ["owner", "co_owner", "ceo"]):
            await ctx.send(f"{E['error']} Δεν έχεις δικαίωμα.")
            return
        await ctx.message.delete()
        await send_v2(ctx.channel, [
            panel(
                f"{E['say']} {message}\n\n—",
                thumbnail_url=THUMBNAIL_URL,
                color=COLOR_BLUE
            )
        ])

    @commands.command(name="dmall")
    async def dmall(self, ctx, *, message: str):
        if not has_roles(ctx.author, ["ceo"]):
            await ctx.send(f"{E['error']} Μόνο ο CEO μπορεί.")
            return
        await ctx.message.delete()
        success, failed = 0, 0
        status = await ctx.send("⏳ Αποστολή DM...")
        for member in ctx.guild.members:
            if member.bot:
                continue
            try:
                await send_v2_dm(member, [
                    panel(
                        f"## {E['dm']} Μήνυμα από **{ctx.guild.name}**\n\n"
                        f"{message}\n\n",
                        thumbnail_url=THUMBNAIL_URL,
                        color=COLOR_BLUE
                    )
                ])
                success += 1
                await asyncio.sleep(1)
            except:
                failed += 1
        await status.edit(content=f"{E['check']} Επιτυχής: **{success}** | {E['error']} Αποτυχία: **{failed}**")
        log_ch = ctx.guild.get_channel(CHANNELS["bot_logs"])
        if log_ch:
            await send_v2(log_ch, [panel(
                f"## {E['dm']} DM All\n"
                f"{E['crown']} Από: {ctx.author.mention}\n"
                f"{E['check']} Επιτυχής: **{success}**\n"
                f"{E['error']} Αποτυχία: **{failed}**\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>",
                thumbnail_url=THUMBNAIL_URL,
                color=COLOR_BLUE
            )])

    @commands.command(name="addemoji")
    async def addemoji(self, ctx, name: str, url: str):
        if not is_staff(ctx.author):
            await ctx.send(f"{E['error']} Δεν έχεις δικαίωμα.")
            return
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    img = await resp.read()
            emoji = await ctx.guild.create_custom_emoji(name=name, image=img)
            await send_v2(ctx.channel, [panel(
                f"## {E['emoji_add']} Emoji Προστέθηκε\n"
                f"Όνομα: **:{name}:**\n"
                f"Emoji: {emoji}\n"
                f"Animated: **{'Ναι' if emoji.animated else 'Όχι'}**",
                thumbnail_url=THUMBNAIL_URL,
                color=COLOR_GREEN
            )])
        except Exception as ex:
            await ctx.send(f"{E['error']} Σφάλμα: `{ex}`")

    @app_commands.command(name="suggest", description="Κάνε μια πρόταση")
    @app_commands.describe(suggestion="Η πρότασή σου")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        await send_v2_interaction(interaction, [
            simple(f"{E['check']} Η πρότασή σου στάλθηκε!", color=COLOR_GREEN)
        ], ephemeral=True)
        msg_data = await send_v2(interaction.channel, [
            panel(
                f"## {E['suggestion']} Νέα Πρόταση\n"
                f"{E['ticket']} Από: {interaction.user.mention}\n"
                f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                f"**Πρόταση:**\n{suggestion}",
                thumbnail_url=THUMBNAIL_URL,
                color=COLOR_BLUE
            )
        ])
        try:
            msg_id     = msg_data["id"]
            route_up   = discord.http.Route("PUT", "/channels/{cid}/messages/{mid}/reactions/{emoji}/@me",
                                            cid=interaction.channel.id, mid=msg_id, emoji="👍")
            route_down = discord.http.Route("PUT", "/channels/{cid}/messages/{mid}/reactions/{emoji}/@me",
                                            cid=interaction.channel.id, mid=msg_id, emoji="👎")
            await interaction._state.http.request(route_up)
            await asyncio.sleep(0.5)
            await interaction._state.http.request(route_down)
        except:
            pass


async def setup(bot):
    await bot.add_cog(Utils(bot))
