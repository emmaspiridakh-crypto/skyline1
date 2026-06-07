import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import ROLES, CHANNELS, EMOJIS, BANNER_URL, THUMBNAIL_URL, is_staff
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())

async def send_billing_log(guild, buyer, seller, amount, product, confirmed_by):
    ch = guild.get_channel(CHANNELS["billing_logs"])
    if not ch:
        return
    await send_v2(ch, [panel(
        f"## {E['billing']} Billing Log\n"
        f"{E['ticket']} Αγοραστής: {buyer.mention if buyer else 'Unknown'}\n"
        f"{E['crown']} Πωλητής: {seller.mention if seller else 'Unknown'}\n"
        f"{E['billing']} Προϊόν: **{product}**\n"
        f"{E['pay']} Ποσό: **{amount}€**\n"
        f"{E['check']} Επιβεβαιώθηκε από: {confirmed_by.mention}\n"
        f"{E['log']} Ώρα: <t:{ts()}:F>",
        thumbnail_url=THUMBNAIL_URL,
        color=COLOR_GOLD
    )])


class Billing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending = {}

    @app_commands.command(name="bill", description="Στείλε billing panel σε χρήστη")
    @app_commands.describe(user="Ο αγοραστής", amount="Ποσό σε €", product="Τι αγόρασε")
    async def bill(self, interaction: discord.Interaction, user: discord.Member, amount: float, product: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [simple(f"{E['error']} Δεν έχεις δικαίωμα.", color=COLOR_RED)], ephemeral=True)
            return

        t   = ts()
        cid = f"payment_complete_{user.id}_{t}"
        self.pending[cid] = {
            "amount": amount, "product": product,
            "buyer_id": user.id, "seller_id": interaction.user.id,
        }

        await send_v2_interaction(interaction, [simple(f"{E['check']} Billing panel στάλθηκε!", color=COLOR_GREEN)], ephemeral=True)

        # Πρώτα mention ως κανονικό μήνυμα
        await interaction.channel.send(user.mention)
        await send_v2(interaction.channel, [
            panel_with_buttons(
                f"## {E['billing']} Billing Panel\n"
                f"{E['ticket']} Αγοραστής: {user.mention}\n"
                f"{E['crown']} Πωλητής: {interaction.user.mention}\n"
                f"{E['billing']} Προϊόν: **{product}**\n"
                f"{E['pay']} Ποσό: **{amount}€**\n"
                f"{E['log']} Ημερομηνία: <t:{t}:F>",
                action_row(
                    button("Payment Complete", custom_id=cid, style=BUTTON_SUCCESS, emoji=E["check"])
                ),
                thumbnail_url=THUMBNAIL_URL,
                color=COLOR_GOLD
            )
        ])

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        cid = interaction.data.get("custom_id", "")
        if not cid.startswith("payment_complete_"):
            return

        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [
                simple(f"{E['error']} Μόνο το staff μπορεί.", color=COLOR_RED)
            ], ephemeral=True)
            return

        data = self.pending.get(cid)
        if not data:
            await send_v2_interaction(interaction, [
                simple(f"{E['error']} Δεν βρέθηκε η πληρωμή (ίσως έγινε restart).", color=COLOR_RED)
            ], ephemeral=True)
            return

        guild  = interaction.guild
        buyer  = guild.get_member(data["buyer_id"])
        seller = guild.get_member(data["seller_id"])
        t      = ts()

        await send_v2_interaction(interaction, [
            simple(f"{E['check']} Πληρωμή επιβεβαιώθηκε!", color=COLOR_GREEN)
        ], ephemeral=True)

        await edit_v2(interaction.message, [panel(
            f"## {E['check']} Πληρωμή Ολοκληρώθηκε!\n"
            f"{E['billing']} Προϊόν: **{data['product']}**\n"
            f"{E['pay']} Ποσό: **{data['amount']}€**\n"
            f"{E['ticket']} Αγοραστής: {buyer.mention if buyer else 'Unknown'}\n"
            f"{E['crown']} Πωλητής: {seller.mention if seller else 'Unknown'}\n"
            f"{E['log']} Ώρα: <t:{t}:F>\n\n"
            f"{E['check']} **Επιβεβαιώθηκε από {interaction.user.mention}**",
            thumbnail_url=THUMBNAIL_URL,
            color=COLOR_GREEN
        )])

        await send_billing_log(guild, buyer, seller, data["amount"], data["product"], interaction.user)

        if buyer:
            await send_v2_dm(buyer, [panel(
                f"## {E['check']} Επιβεβαίωση Αγοράς\n"
                f"{E['billing']} Προϊόν: **{data['product']}**\n"
                f"{E['pay']} Ποσό: **{data['amount']}€**\n"
                f"{E['crown']} Πωλητής: {seller.display_name if seller else 'Unknown'}\n"
                f"{E['log']} Ώρα: <t:{t}:F>\n\n"
                f"Ευχαριστούμε για την αγορά σου! {E['check']}",
                thumbnail_url=THUMBNAIL_URL,
                color=COLOR_GOLD
            )])

        del self.pending[cid]


async def setup(bot):
    await bot.add_cog(Billing(bot))
