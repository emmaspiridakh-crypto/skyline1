import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import CHANNELS, EMOJIS, THUMBNAIL_URL, is_staff
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())

async def punishment_log(guild, action, target, moderator, reason, duration=None):
    ch = guild.get_channel(CHANNELS["punishments_logs"])
    if not ch:
        return
    emap = {"Ban": E["ban"], "Unban": E["unban"], "Kick": E["kick"],
            "Timeout": E["timeout"], "Clear": E["clear"]}
    e = emap.get(action, E["punishment"])
    txt = (
        f"## {e} {action}\n"
        f"{E['ticket']} Χρήστης: {target.mention if hasattr(target,'mention') else str(target)}\n"
        f"{E['crown']} Moderator: {moderator.mention}\n"
        f"{E['log']} Λόγος: **{reason}**\n"
    )
    if duration:
        txt += f"{E['timeout']} Διάρκεια: **{duration}**\n"
    txt += f"{E['loading']} Ώρα: <t:{ts()}:F>"
    await send_v2(ch, [section(txt, thumbnail_url=THUMBNAIL_URL)])


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban χρήστη")
    @app_commands.describe(user="Ο χρήστης", reason="Λόγος (υποχρεωτικό)")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return
        await user.ban(reason=reason)
        await send_v2_interaction(interaction, [text(f"{E['ban']} **{user}** έγινε ban.\n{E['log']} Λόγος: {reason}")])
        await punishment_log(interaction.guild, "Ban", user, interaction.user, reason)

    @app_commands.command(name="unban", description="Unban χρήστη με ID")
    @app_commands.describe(user_id="ID χρήστη", reason="Λόγος (υποχρεωτικό)")
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=reason)
            await send_v2_interaction(interaction, [text(f"{E['unban']} **{user}** έγινε unban.\n{E['log']} Λόγος: {reason}")])
            await punishment_log(interaction.guild, "Unban", user, interaction.user, reason)
        except:
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν βρέθηκε χρήστης.")], ephemeral=True)

    @app_commands.command(name="kick", description="Kick χρήστη")
    @app_commands.describe(user="Ο χρήστης", reason="Λόγος (υποχρεωτικό)")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return
        await user.kick(reason=reason)
        await send_v2_interaction(interaction, [text(f"{E['kick']} **{user}** έγινε kick.\n{E['log']} Λόγος: {reason}")])
        await punishment_log(interaction.guild, "Kick", user, interaction.user, reason)

    @app_commands.command(name="timeout", description="Timeout χρήστη")
    @app_commands.describe(user="Ο χρήστης", minutes="Λεπτά", reason="Λόγος (υποχρεωτικό)")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return
        await user.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        await send_v2_interaction(interaction, [text(f"{E['timeout']} **{user}** timeout για **{minutes} λεπτά**.\n{E['log']} Λόγος: {reason}")])
        await punishment_log(interaction.guild, "Timeout", user, interaction.user, reason, f"{minutes} λεπτά")

    @app_commands.command(name="clear", description="Διαγραφή μηνυμάτων")
    @app_commands.describe(amount="Πόσα (max 100)", reason="Λόγος (υποχρεωτικό)")
    async def clear(self, interaction: discord.Interaction, amount: int, reason: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return
        deleted = await interaction.channel.purge(limit=min(amount, 100))
        await send_v2_interaction(interaction, [text(f"{E['clear']} Διαγράφηκαν **{len(deleted)}** μηνύματα.\n{E['log']} Λόγος: {reason}")], ephemeral=True)
        await punishment_log(interaction.guild, "Clear", interaction.channel, interaction.user, reason)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
