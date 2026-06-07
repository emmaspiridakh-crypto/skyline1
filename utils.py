import discord
from discord.ext import commands
import datetime
from config import ROLES, CHANNELS, EMOJIS
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        join_to_create = CHANNELS.get("join_to_create")
        voice_category = CHANNELS.get("voice_category")

        # Create temp channel
        if after.channel and after.channel.id == join_to_create:
            category = guild.get_channel(voice_category)
            new_ch = await guild.create_voice_channel(
                name=f"{E['voice']} {member.display_name}",
                category=category,
                user_limit=10
            )
            self.temp_channels[new_ch.id] = member.id
            await member.move_to(new_ch)

            log_ch = guild.get_channel(CHANNELS["voice_logs"])
            if log_ch:
                await send_v2(log_ch, [text(
                    f"## {E['voice_join']} Temp Voice Δημιουργήθηκε\n"
                    f"{E['ticket']} Από: {member.mention}\n"
                    f"{E['voice']} Channel: **{new_ch.name}**\n"
                    f"{E['loading']} Ώρα: <t:{ts()}:F>"
                )])

            notify_ch = guild.get_channel(CHANNELS["staff_notify"])
            if notify_ch:
                staff_r   = guild.get_role(ROLES["staff"])
                manager_r = guild.get_role(ROLES["manager"])
                ping = f"{staff_r.mention} {manager_r.mention}" if staff_r and manager_r else ""
                await send_v2(notify_ch, [text(
                    f"{E['voice']} **{member.mention}** μπήκε σε Support Voice!\n"
                    f"Channel: **{new_ch.name}**"
                )], content=ping)

        # Delete temp channel when empty
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                ch_name = before.channel.name
                del self.temp_channels[before.channel.id]
                try:
                    await before.channel.delete()
                except:
                    pass

                log_ch = guild.get_channel(CHANNELS["voice_logs"])
                if log_ch:
                    await send_v2(log_ch, [text(
                        f"## {E['voice_leave']} Temp Voice Διαγράφηκε\n"
                        f"{E['voice']} Channel: **{ch_name}**\n"
                        f"{E['loading']} Ώρα: <t:{ts()}:F>"
                    )])


async def setup(bot):
    await bot.add_cog(Voice(bot))
