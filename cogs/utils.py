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

    # ── !say ────────────────────────────────────────────────
    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        if not has_roles(ctx.author, ["owner", "co_owner", "ceo"]):
            await ctx.send(f"{E['error']} Δεν έχεις δικαίωμα.")
            return
        await ctx.message.delete()
        await ctx.send(message)

    # ── !say2 ────────────────────────────────────────────────
    @commands.command(name="say2")
    async def say2(self, ctx, *, message: str):
        if not has_roles(ctx.author, ["owner", "co_owner", "ceo"]):
            await ctx.send(f"{E['error']} Δεν έχεις δικαίωμα.")
            return
        await ctx.message.delete()
        await send_v2(ctx.channel, [
            section(
                f"{E['say']} {message}\n\n— {ctx.author.display_name}",
                thumbnail_url=THUMBNAIL_URL
            )
        ])

    # ── !dmall ───────────────────────────────────────────────
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
                    section(
                        f"## {E['dm']} Μήνυμα από **{ctx.guild.name}**\n\n"
                        f"{message}\n\n— {ctx.author.display_name}",
                        thumbnail_url=THUMBNAIL_URL
                    )
                ])
                success += 1
                await asyncio.sleep(1)
            except:
                failed += 1

        await status.edit(content=f"{E['check']} Επιτυχής: **{success}** | {E['error']} Αποτυχία: **{failed}**")

        log_ch = ctx.guild.get_channel(CHANNELS["bot_logs"])
        if log_ch:
            await send_v2(log_ch, [text(
                f"## {E['dm']} DM All\n"
                f"{E['crown']} Από: {ctx.author.mention}\n"
                f"{E['check']} Επιτυχής: **{success}**\n"
                f"{E['error']} Αποτυχία: **{failed}**\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )])

    # ── !addemoji ────────────────────────────────────────────
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
            await send_v2(ctx.channel, [text(
                f"## {E['emoji_add']} Emoji Προστέθηκε\n"
                f"Όνομα: **:{name}:**\n"
                f"Emoji: {emoji}\n"
                f"Animated: **{'Ναι' if emoji.animated else 'Όχι'}**"
            )])
        except Exception as ex:
            await ctx.send(f"{E['error']} Σφάλμα: `{ex}`")

    # ── /suggest ─────────────────────────────────────────────
    @app_commands.command(name="suggest", description="Κάνε μια πρόταση")
    @app_commands.describe(suggestion="Η πρότασή σου")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        await send_v2_interaction(interaction, [
            text(f"{E['check']} Η πρότασή σου στάλθηκε!")
        ], ephemeral=True)

        msg_data = await send_v2(interaction.channel, [
            section(
                f"## {E['suggestion']} Νέα Πρόταση\n"
                f"{E['ticket']} Από: {interaction.user.mention}\n"
                f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                f"**Πρόταση:**\n{suggestion}",
                thumbnail_url=THUMBNAIL_URL
            )
        ])

        # Add reactions via REST
        channel = interaction.channel
        msg_id  = msg_data["id"]
        route_up   = discord.http.Route("PUT", "/channels/{cid}/messages/{mid}/reactions/{emoji}/@me",
                                        cid=channel.id, mid=msg_id, emoji="👍")
        route_down = discord.http.Route("PUT", "/channels/{cid}/messages/{mid}/reactions/{emoji}/@me",
                                        cid=channel.id, mid=msg_id, emoji="👎")
        try:
            await interaction._state.http.request(route_up)
            await asyncio.sleep(0.5)
            await interaction._state.http.request(route_down)
        except:
            pass


async def setup(bot):
    await bot.add_cog(Utils(bot))
