import discord
from discord.ext import commands
import datetime
from config import ROLES, CHANNELS, EMOJIS, THUMBNAIL_URL
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())

async def log(guild, key, txt, thumb=True):
    ch = guild.get_channel(CHANNELS.get(key))
    if not ch:
        return
    comp = [section(txt, thumbnail_url=THUMBNAIL_URL)] if thumb else [text(txt)]
    await send_v2(ch, comp)


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── WELCOME / LEAVE ─────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild

        auto_role = guild.get_role(ROLES["auto_role"])
        if auto_role:
            try:
                await member.add_roles(auto_role)
            except:
                pass

        created = int(member.created_at.timestamp())
        await log(guild, "welcome_logs",
            f"## {E['join']} Νέο Μέλος\n"
            f"{E['welcome']} Χρήστης: {member.mention} ({member})\n"
            f"{E['log']} Δημιουργία λογαριασμού: <t:{created}:F>\n"
            f"{E['loading']} Μπήκε: <t:{ts()}:F>\n"
            f"{E['ticket']} Μέλη: **{guild.member_count}**"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        joined = int(member.joined_at.timestamp()) if member.joined_at else ts()
        await log(guild, "welcome_logs",
            f"## {E['leave']} Έφυγε Μέλος\n"
            f"{E['welcome']} Χρήστης: **{member}**\n"
            f"{E['log']} Μπήκε: <t:{joined}:R>\n"
            f"{E['loading']} Έφυγε: <t:{ts()}:F>\n"
            f"{E['ticket']} Μέλη: **{guild.member_count}**"
        )

    # ── MESSAGE LOGS ────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        content = message.content[:500] if message.content else "Χωρίς κείμενο"
        await log(message.guild, "message_logs",
            f"## {E['delete']} Μήνυμα Διαγράφηκε\n"
            f"{E['ticket']} Χρήστης: {message.author.mention}\n"
            f"{E['log']} Channel: <#{message.channel.id}>\n"
            f"{E['edit']} Περιεχόμενο:\n```\n{content}\n```\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        await log(before.guild, "message_logs",
            f"## {E['edit']} Μήνυμα Επεξεργάστηκε\n"
            f"{E['ticket']} Χρήστης: {before.author.mention}\n"
            f"{E['log']} Channel: <#{before.channel.id}>\n"
            f"{E['delete']} Πριν:\n```\n{before.content[:300]}\n```\n"
            f"{E['edit']} Μετά:\n```\n{after.content[:300]}\n```\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    # ── VOICE LOGS ──────────────────────────────────────────
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        if before.channel is None and after.channel is not None:
            await log(guild, "voice_logs",
                f"## {E['voice_join']} Voice Join\n"
                f"{E['ticket']} Χρήστης: {member.mention}\n"
                f"{E['voice']} Channel: **{after.channel.name}**\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )
        elif before.channel is not None and after.channel is None:
            await log(guild, "voice_logs",
                f"## {E['voice_leave']} Voice Leave\n"
                f"{E['ticket']} Χρήστης: {member.mention}\n"
                f"{E['voice']} Channel: **{before.channel.name}**\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )
        elif before.channel and after.channel and before.channel != after.channel:
            await log(guild, "voice_logs",
                f"## {E['voice']} Voice Switch\n"
                f"{E['ticket']} Χρήστης: {member.mention}\n"
                f"{E['voice_leave']} Από: **{before.channel.name}**\n"
                f"{E['voice_join']} Σε: **{after.channel.name}**\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )

    # ── ROLE LOGS ───────────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        added   = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]
        for role in added:
            await log(after.guild, "role_logs",
                f"## {E['role_add']} Role Προστέθηκε\n"
                f"{E['ticket']} Χρήστης: {after.mention}\n"
                f"{E['crown']} Role: {role.mention}\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )
        for role in removed:
            await log(after.guild, "role_logs",
                f"## {E['role_remove']} Role Αφαιρέθηκε\n"
                f"{E['ticket']} Χρήστης: {after.mention}\n"
                f"{E['crown']} Role: {role.mention}\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )
        # boost check
        if before.premium_since is None and after.premium_since is not None:
            await log(after.guild, "other_logs",
                f"## {E['boost']} Νέο Server Boost!\n"
                f"{E['crown']} Χρήστης: {after.mention}\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )

    # ── CHANNEL LOGS ────────────────────────────────────────
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await log(channel.guild, "channel_logs",
            f"## {E['channel_add']} Channel Δημιουργήθηκε\n"
            f"{E['ticket']} Όνομα: **{channel.name}**\n"
            f"{E['log']} Τύπος: **{str(channel.type).capitalize()}**\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await log(channel.guild, "channel_logs",
            f"## {E['channel_del']} Channel Διαγράφηκε\n"
            f"{E['ticket']} Όνομα: **{channel.name}**\n"
            f"{E['log']} Τύπος: **{str(channel.type).capitalize()}**\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name != after.name:
            await log(after.guild, "channel_logs",
                f"## {E['edit']} Channel Μετονομάστηκε\n"
                f"{E['delete']} Πριν: **{before.name}**\n"
                f"{E['edit']} Μετά: **{after.name}**\n"
                f"{E['loading']} Ώρα: <t:{ts()}:F>"
            )

    # ── REACTION LOGS ───────────────────────────────────────
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or not reaction.message.guild:
            return
        await log(reaction.message.guild, "reaction_logs",
            f"## {E['reaction']} Reaction Προστέθηκε\n"
            f"{E['ticket']} Χρήστης: {user.mention}\n"
            f"{E['reaction']} Emoji: {reaction.emoji}\n"
            f"{E['log']} Channel: <#{reaction.message.channel.id}>\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot or not reaction.message.guild:
            return
        await log(reaction.message.guild, "reaction_logs",
            f"## {E['reaction']} Reaction Αφαιρέθηκε\n"
            f"{E['ticket']} Χρήστης: {user.mention}\n"
            f"{E['reaction']} Emoji: {reaction.emoji}\n"
            f"{E['log']} Channel: <#{reaction.message.channel.id}>\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    # ── INVITE LOGS ─────────────────────────────────────────
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await log(invite.guild, "invite_logs",
            f"## {E['invite']} Invite Δημιουργήθηκε\n"
            f"{E['ticket']} Από: {invite.inviter.mention if invite.inviter else 'Unknown'}\n"
            f"{E['log']} Code: **{invite.code}**\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )

    # ── BOT COMMAND LOGS ────────────────────────────────────
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        if not interaction.guild:
            return
        await log(interaction.guild, "bot_logs",
            f"## {E['log']} Εντολή Χρησιμοποιήθηκε\n"
            f"{E['ticket']} Χρήστης: {interaction.user.mention}\n"
            f"{E['edit']} Εντολή: **/{command.name}**\n"
            f"{E['log']} Channel: <#{interaction.channel.id}>\n"
            f"{E['loading']} Ώρα: <t:{ts()}:F>"
        )


async def setup(bot):
    await bot.add_cog(Logs(bot))
