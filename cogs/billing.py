import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import ROLES, CHANNELS, EMOJIS, BANNER_URL, is_staff, has_roles
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())


async def send_billing_log(guild, buyer, seller, amount, product, confirmed_by):
    ch = guild.get_channel(CHANNELS["billing_logs"])
    if not ch:
        return
    await send_v2(ch, [text(
        f"## {E['billing']} Billing Log\n"
        f"{E['ticket']} Αγοραστής: {buyer.mention if buyer else 'Unknown'}\n"
        f"{E['crown']} Πωλητής: {seller.mention if seller else 'Unknown'}\n"
        f"{E['billing']} Προϊόν: **{product}**\n"
        f"{E['pay']} Ποσό: **{amount}€**\n"
        f"{E['check']} Επιβεβαιώθηκε από: {confirmed_by.mention}\n"
        f"{E['log']} Ώρα: <t:{ts()}:F>"
    )])


class Billing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # store pending bills: custom_id -> {amount, product, buyer_id, seller_id}
        self.pending = {}

    @app_commands.command(name="bill", description="Στείλε billing panel σε χρήστη")
    @app_commands.describe(user="Ο αγοραστής", amount="Ποσό σε €", product="Τι αγόρασε")
    async def bill(self, interaction: discord.Interaction, user: discord.Member, amount: float, product: str):
        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return

        t = ts()
        cid = f"payment_complete_{user.id}_{t}"
        self.pending[cid] = {
            "amount": amount,
            "product": product,
            "buyer_id": user.id,
            "seller_id": interaction.user.id,
        }

        await send_v2_interaction(interaction, [text(f"{E['check']} Billing panel στάλθηκε!")], ephemeral=True)
        await send_v2(interaction.channel, [
            banner_container(BANNER_URL),
            separator(),
            text(
                f"## {E['billing']} Billing Panel\n"
                f"{E['ticket']} Αγοραστής: {user.mention}\n"
                f"{E['crown']} Πωλητής: {interaction.user.mention}\n"
                f"{E['billing']} Προϊόν: **{product}**\n"
                f"{E['pay']} Ποσό: **{amount}€**\n"
                f"{E['log']} Ημερομηνία: <t:{t}:F>"
            ),
            separator(large=True),
            action_row(
                button("Payment Complete", custom_id=cid, style=BUTTON_SUCCESS, emoji=E["check"])
            )
        ], content=user.mention)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        cid = interaction.data.get("custom_id", "")
        if not cid.startswith("payment_complete_"):
            return

        if not is_staff(interaction.user):
            await send_v2_interaction(interaction, [
                text(f"{E['error']} Μόνο το staff μπορεί να πατήσει αυτό.")
            ], ephemeral=True)
            return

        data = self.pending.get(cid)
        if not data:
            await send_v2_interaction(interaction, [
                text(f"{E['error']} Δεν βρέθηκε η πληρωμή (ίσως έγινε restart του bot).")
            ], ephemeral=True)
            return

        guild  = interaction.guild
        buyer  = guild.get_member(data["buyer_id"])
        seller = guild.get_member(data["seller_id"])
        t = ts()

        await send_v2_interaction(interaction, [
            text(f"{E['check']} Πληρωμή επιβεβαιώθηκε!")
        ], ephemeral=True)

        await edit_v2(interaction.message, [
            banner_container(BANNER_URL),
            separator(),
            text(
                f"## {E['check']} Πληρωμή Ολοκληρώθηκε!\n"
                f"{E['billing']} Προϊόν: **{data['product']}**\n"
                f"{E['pay']} Ποσό: **{data['amount']}€**\n"
                f"{E['ticket']} Αγοραστής: {buyer.mention if buyer else 'Unknown'}\n"
                f"{E['crown']} Πωλητής: {seller.mention if seller else 'Unknown'}\n"
                f"{E['log']} Ώρα: <t:{t}:F>\n\n"
                f"{E['check']} **Επιβεβαιώθηκε από {interaction.user.mention}**"
            )
        ])

        await send_billing_log(guild, buyer, seller, data["amount"], data["product"], interaction.user)

        if buyer:
            await send_v2_dm(buyer, [text(
                f"## {E['check']} Επιβεβαίωση Αγοράς\n"
                f"{E['billing']} Προϊόν: **{data['product']}**\n"
                f"{E['pay']} Ποσό: **{data['amount']}€**\n"
                f"{E['crown']} Πωλητής: {seller.display_name if seller else 'Unknown'}\n"
                f"{E['log']} Ώρα: <t:{t}:F>\n\n"
                f"Ευχαριστούμε για την αγορά σου! {E['check']}"
            )])

        del self.pending[cid]


async def setup(bot):
    await bot.add_cog(Billing(bot))

