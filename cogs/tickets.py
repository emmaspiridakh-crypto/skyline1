import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import ROLES, CHANNELS, EMOJIS, BANNER_URL, THUMBNAIL_URL, SELLERS, is_staff, has_roles
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())

STAFF_IDS = ["ceo", "owner", "co_owner", "manager", "staff", "administrator"]

def can_control(member):
    return has_roles(member, STAFF_IDS)

async def ticket_log(guild, user, channel, ttype, action, closed_by=None):
    ch = guild.get_channel(CHANNELS["ticket_logs"])
    if not ch:
        return
    emoji = E["check"] if action == "opened" else E["close"]
    txt = (
        f"## {emoji} Ticket {action.capitalize()}\n"
        f"{E['ticket']} Channel: #{channel.name}\n"
        f"{E['support']} Τύπος: **{ttype.capitalize()}**\n"
        f"{E['log']} Χρήστης: {user.mention if user else 'Unknown'}\n"
    )
    if closed_by:
        txt += f"{E['close']} Έκλεισε από: {closed_by.mention}\n"
    txt += f"{E['loading']} Ώρα: <t:{ts()}:F>"
    color = COLOR_GREEN if action == "opened" else COLOR_RED
    await send_v2(ch, [panel(txt, thumbnail_url=THUMBNAIL_URL, color=color)])

async def open_ticket(interaction, name_prefix, ttype, extra_roles, ticket_text):
    guild = interaction.guild
    user  = interaction.user

    for ch in guild.channels:
        if ch.name == f"{name_prefix}-{user.name.lower()}":
            await send_v2_interaction(interaction, [
                panel(f"{E['error']} Έχεις ήδη ανοιχτό ticket: <#{ch.id}>", color=COLOR_RED)
            ], ephemeral=True)
            return

    category = guild.get_channel(CHANNELS["ticket_category"])
    ow = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    for rid in extra_roles:
        r = guild.get_role(rid)
        if r:
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    channel = await guild.create_text_channel(
        name=f"{name_prefix}-{user.name.lower()}",
        category=category,
        overwrites=ow,
        topic=f"{ttype} ticket | user:{user.id}"
    )

    await send_v2_interaction(interaction, [
        panel(f"{E['check']} Ticket ανοίχτηκε: <#{channel.id}>", color=COLOR_GREEN)
    ], ephemeral=True)

    await send_v2(channel, [
        panel_with_buttons(
            ticket_text,
            action_row(
                button("Close Ticket", custom_id=f"close_{channel.id}",  style=BUTTON_DANGER,    emoji=E["close"]),
                button("Notify User",  custom_id=f"notify_{channel.id}", style=BUTTON_SECONDARY, emoji=E["notify"]),
            ),
            thumbnail_url=BANNER_URL,
            color=COLOR_BLUE
        )
    ], content=user.mention)

    await ticket_log(guild, user, channel, ttype, "opened")

    notify_ch = guild.get_channel(CHANNELS["staff_notify"])
    if notify_ch:
        staff_r   = guild.get_role(ROLES["staff"])
        manager_r = guild.get_role(ROLES["manager"])
        ping = f"{staff_r.mention} {manager_r.mention}" if staff_r and manager_r else ""
        await send_v2(notify_ch, [panel(
            f"{E['notify']} **Νέο {ttype.capitalize()} Ticket!**\n"
            f"Χρήστης: {user.mention}\n"
            f"Channel: <#{channel.id}>",
            thumbnail_url=THUMBNAIL_URL,
            color=COLOR_BLUE
        )], content=ping)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_tickets", description="Στέλνει το support ticket panel")
    async def setup_tickets(self, interaction: discord.Interaction):
        if not has_roles(interaction.user, ["ceo", "owner", "co_owner"]):
            await send_v2_interaction(interaction, [panel(f"{E['error']} Δεν έχεις δικαίωμα.", color=COLOR_RED)], ephemeral=True)
            return
        await send_v2_interaction(interaction, [panel(f"{E['check']} Panel στάλθηκε!", color=COLOR_GREEN)], ephemeral=True)
        await send_v2(interaction.channel, [
            panel_with_buttons(
                f"## {E['support']} Support Tickets\n"
                f"Επέλεξε κατηγορία παρακάτω.\n\n"
                f"{E['ticket']} **Administrator** — Θέματα με administrators\n"
                f"{E['support']} **Staff** — Γενική υποστήριξη\n"
                f"{E['crown']} **Managers** — Θέματα με managers",
                action_row(
                    button("Administrator", custom_id="open_ticket_admin",   style=BUTTON_DANGER,    emoji=E["ticket"]),
                    button("Staff",         custom_id="open_ticket_staff",   style=BUTTON_PRIMARY,   emoji=E["support"]),
                    button("Managers",      custom_id="open_ticket_manager", style=BUTTON_SECONDARY, emoji=E["crown"]),
                ),
                thumbnail_url=BANNER_URL,
                color=COLOR_BLUE
            )
        ])

    @app_commands.command(name="setup_buy", description="Στέλνει το buy ticket panel")
    async def setup_buy(self, interaction: discord.Interaction):
        if not has_roles(interaction.user, ["ceo", "owner", "co_owner"]):
            await send_v2_interaction(interaction, [panel(f"{E['error']} Δεν έχεις δικαίωμα.", color=COLOR_RED)], ephemeral=True)
            return
        await send_v2_interaction(interaction, [panel(f"{E['check']} Panel στάλθηκε!", color=COLOR_GREEN)], ephemeral=True)
        options     = [select_option(s["name"], str(i)) for i, s in enumerate(SELLERS)]
        seller_list = "\n".join([f"{E['buy']} **{s['name']}**" for s in SELLERS])
        await send_v2(interaction.channel, [
            panel(
                f"## {E['buy']} Buy Ticket\n"
                f"Επέλεξε seller από το dropdown.\n\n"
                f"**Διαθέσιμοι Sellers:**\n{seller_list}",
                thumbnail_url=BANNER_URL,
                color=COLOR_GOLD
            ),
            select_menu("buy_seller_select", f"{E['buy']} Επέλεξε seller...", options)
        ])

    @app_commands.command(name="setup_donate", description="Στέλνει το donate panel")
    async def setup_donate(self, interaction: discord.Interaction):
        if not has_roles(interaction.user, ["ceo", "owner", "co_owner"]):
            await send_v2_interaction(interaction, [panel(f"{E['error']} Δεν έχεις δικαίωμα.", color=COLOR_RED)], ephemeral=True)
            return
        await send_v2_interaction(interaction, [panel(f"{E['check']} Panel στάλθηκε!", color=COLOR_GREEN)], ephemeral=True)
        await send_v2(interaction.channel, [
            panel_with_buttons(
                f"## {E['donate']} Donate\n"
                f"Θέλεις να υποστηρίξεις τον server μας;\n"
                f"Πάτα το κουμπί και ένας donate manager θα σε εξυπηρετήσει!",
                action_row(
                    button("Make a Donate", custom_id="open_ticket_donate", style=BUTTON_SUCCESS, emoji=E["donate"])
                ),
                thumbnail_url=BANNER_URL,
                color=COLOR_PINK
            )
        ])

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        cid   = interaction.data.get("custom_id", "")
        guild = interaction.guild
        user  = interaction.user

        if cid == "open_ticket_admin":
            roles = [ROLES["administrator"], ROLES["ceo"], ROLES["owner"], ROLES["co_owner"]]
            await open_ticket(interaction, "support", "administrator", roles,
                f"## {E['support']} Support Ticket — Administrator\n"
                f"{E['ticket']} Από: {user.mention}\n"
                f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                f"Γεια σου {user.mention}! Περίμενε να σε εξυπηρετήσουμε."
            )

        elif cid == "open_ticket_staff":
            roles = [ROLES["staff"], ROLES["manager"], ROLES["administrator"], ROLES["ceo"], ROLES["owner"], ROLES["co_owner"]]
            await open_ticket(interaction, "support", "staff", roles,
                f"## {E['support']} Support Ticket — Staff\n"
                f"{E['ticket']} Από: {user.mention}\n"
                f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                f"Γεια σου {user.mention}! Περίμενε να σε εξυπηρετήσουμε."
            )

        elif cid == "open_ticket_manager":
            roles = [ROLES["manager"], ROLES["administrator"], ROLES["ceo"], ROLES["owner"], ROLES["co_owner"]]
            await open_ticket(interaction, "support", "manager", roles,
                f"## {E['support']} Support Ticket — Manager\n"
                f"{E['ticket']} Από: {user.mention}\n"
                f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                f"Γεια σου {user.mention}! Περίμενε να σε εξυπηρετήσουμε."
            )

        elif cid == "open_ticket_donate":
            roles = [ROLES["donate_manager"], ROLES["ceo"], ROLES["owner"], ROLES["co_owner"]]
            await open_ticket(interaction, "donate", "donate", roles,
                f"## {E['donate']} Donate Ticket\n"
                f"{E['ticket']} Από: {user.mention}\n"
                f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                f"Γεια σου {user.mention}! Ευχαριστούμε για το ενδιαφέρον σου!"
            )

        elif cid == "buy_seller_select":
            idx         = int(interaction.data["values"][0])
            seller      = SELLERS[idx]
            seller_role = guild.get_role(seller["role_id"])
            extra_roles = [seller["role_id"], ROLES["ceo"], ROLES["owner"], ROLES["co_owner"]]

            for ch in guild.channels:
                if ch.name == f"buy-{user.name.lower()}":
                    await send_v2_interaction(interaction, [
                        panel(f"{E['error']} Έχεις ήδη ανοιχτό buy ticket: <#{ch.id}>", color=COLOR_RED)
                    ], ephemeral=True)
                    return

            category = guild.get_channel(CHANNELS["ticket_category"])
            ow = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }
            for rid in extra_roles:
                r = guild.get_role(rid)
                if r:
                    ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

            channel = await guild.create_text_channel(
                name=f"buy-{user.name.lower()}",
                category=category,
                overwrites=ow,
                topic=f"buy ticket | user:{user.id} | seller:{seller['name']}"
            )

            await send_v2_interaction(interaction, [
                panel(f"{E['check']} Buy ticket ανοίχτηκε: <#{channel.id}>", color=COLOR_GREEN)
            ], ephemeral=True)

            await send_v2(channel, [
                panel_with_buttons(
                    f"## {E['buy']} Buy Ticket\n"
                    f"{E['ticket']} Αγοραστής: {user.mention}\n"
                    f"{E['crown']} Seller: **{seller['name']}** {seller_role.mention if seller_role else ''}\n"
                    f"{E['log']} Ώρα: <t:{ts()}:F>\n\n"
                    f"Γεια σου {user.mention}! Ο seller θα σε εξυπηρετήσει σύντομα.",
                    action_row(
                        button("Close Ticket", custom_id=f"close_{channel.id}",  style=BUTTON_DANGER,    emoji=E["close"]),
                        button("Notify User",  custom_id=f"notify_{channel.id}", style=BUTTON_SECONDARY, emoji=E["notify"]),
                    ),
                    thumbnail_url=BANNER_URL,
                    color=COLOR_GOLD
                )
            ], content=user.mention)

            await ticket_log(guild, user, channel, "buy", "opened")

            notify_ch = guild.get_channel(CHANNELS["staff_notify"])
            if notify_ch and seller_role:
                await send_v2(notify_ch, [panel(
                    f"{E['notify']} **Νέο Buy Ticket!**\n"
                    f"Αγοραστής: {user.mention}\n"
                    f"Seller: {seller_role.mention}\n"
                    f"Channel: <#{channel.id}>",
                    thumbnail_url=THUMBNAIL_URL,
                    color=COLOR_GOLD
                )], content=seller_role.mention)

        elif cid.startswith("close_"):
            if not can_control(user):
                await send_v2_interaction(interaction, [
                    panel(f"{E['error']} Δεν έχεις δικαίωμα.", color=COLOR_RED)
                ], ephemeral=True)
                return

            channel   = interaction.channel
            topic     = channel.topic or ""
            opener_id = None
            for part in topic.split("|"):
                part = part.strip()
                if part.startswith("user:"):
                    try:
                        opener_id = int(part.split(":")[1])
                    except:
                        pass

            opener = guild.get_member(opener_id) if opener_id else None
            await send_v2_interaction(interaction, [
                panel(f"{E['close']} Ticket κλείνει... Διαγράφεται σε 5 δευτερόλεπτα.", color=COLOR_RED)
            ])
            await ticket_log(guild, opener, channel, "ticket", "closed", closed_by=user)
            import asyncio
            await asyncio.sleep(5)
            await channel.delete()

        elif cid.startswith("notify_"):
            if not can_control(user):
                await send_v2_interaction(interaction, [
                    panel(f"{E['error']} Δεν έχεις δικαίωμα.", color=COLOR_RED)
                ], ephemeral=True)
                return

            channel   = interaction.channel
            topic     = channel.topic or ""
            opener_id = None
            for part in topic.split("|"):
                part = part.strip()
                if part.startswith("user:"):
                    try:
                        opener_id = int(part.split(":")[1])
                    except:
                        pass

            opener = guild.get_member(opener_id) if opener_id else None
            if opener:
                await send_v2_dm(opener, [panel(
                    f"## {E['notify']} Ειδοποίηση Ticket\n"
                    f"Η ομάδα του **{guild.name}** σε καλεί πίσω στο ticket σου!\n"
                    f"Channel: <#{channel.id}>",
                    thumbnail_url=THUMBNAIL_URL,
                    color=COLOR_BLUE
                )])
                await send_v2_interaction(interaction, [
                    panel(f"{E['check']} Ο χρήστης ειδοποιήθηκε!", color=COLOR_GREEN)
                ], ephemeral=True)
            else:
                await send_v2_interaction(interaction, [
                    panel(f"{E['error']} Δεν βρέθηκε ο χρήστης.", color=COLOR_RED)
                ], ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))


