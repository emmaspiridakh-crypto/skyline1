import discord
from discord.ext import commands
from discord import app_commands
import datetime, json, os
from config import CHANNELS, EMOJIS, BANNER_URL, THUMBNAIL_URL
from v2 import *

E = EMOJIS

def ts():
    return int(datetime.datetime.now().timestamp())

REVIEWS_FILE = "data/reviews.json"

def load_reviews():
    if not os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, "w") as f:
            json.dump({"count": 0, "total_stars": 0}, f)
    with open(REVIEWS_FILE) as f:
        return json.load(f)

def save_reviews(data):
    with open(REVIEWS_FILE, "w") as f:
        json.dump(data, f, indent=4)


class ReviewModal(discord.ui.Modal, title="Submit Review"):
    comment = discord.ui.TextInput(
        label="Σχόλιο (υποχρεωτικό)",
        style=discord.TextStyle.long,
        placeholder="Γράψε την εμπειρία σου...",
        min_length=10,
        max_length=500,
        required=True
    )

    def __init__(self, stars: int, guild):
        super().__init__()
        self.stars = stars
        self.guild = guild

    async def on_submit(self, interaction: discord.Interaction):
        stars   = self.stars
        comment = self.comment.value
        user    = interaction.user
        t       = ts()

        data = load_reviews()
        data["count"]       += 1
        data["total_stars"] += stars
        avg = round(data["total_stars"] / data["count"], 1)
        save_reviews(data)

        star_display = "⭐" * stars + "☆" * (5 - stars)

        reviews_ch = self.guild.get_channel(CHANNELS["reviews"])
        if reviews_ch:
            await send_v2(reviews_ch, [
                section(
                    f"## {E['review']} Review #{data['count']}\n"
                    f"{E['star']} Βαθμολογία: **{star_display}** ({stars}/5)\n"
                    f"{E['ticket']} Από: {user.mention}\n"
                    f"{E['log']} Ώρα: <t:{t}:F>\n\n"
                    f"**Σχόλιο:**\n{comment}\n\n"
                    f"{E['loading']} Μέσος όρος: **{avg}/5** από **{data['count']}** reviews",
                    thumbnail_url=THUMBNAIL_URL
                )
            ])

        await send_v2_interaction(interaction, [
            text(f"{E['check']} Το review σου στάλθηκε! Ευχαριστούμε {E['star']}")
        ], ephemeral=True)


class Reviews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_reviews", description="Στέλνει το review panel")
    async def setup_reviews(self, interaction: discord.Interaction):
        from config import has_roles
        if not has_roles(interaction.user, ["ceo", "owner", "co_owner"]):
            await send_v2_interaction(interaction, [text(f"{E['error']} Δεν έχεις δικαίωμα.")], ephemeral=True)
            return

        data = load_reviews()
        avg  = round(data["total_stars"] / data["count"], 1) if data["count"] > 0 else 0

        await send_v2_interaction(interaction, [text(f"{E['check']} Panel στάλθηκε!")], ephemeral=True)
        await send_v2(interaction.channel, [
            section(
                f"## {E['review']} Reviews\n"
                f"Μοιράσου την εμπειρία σου μαζί μας!\n\n"
                f"{E['star']} Συνολικά reviews: **{data['count']}**\n"
                f"{E['loading']} Μέσος όρος: **{avg}/5**\n\n"
                f"Επέλεξε αστέρια παρακάτω.",
                thumbnail_url=THUMBNAIL_URL
            ),
            separator(large=True),
            action_row(
                button("⭐",     custom_id="review_1", style=BUTTON_SECONDARY),
                button("⭐⭐",   custom_id="review_2", style=BUTTON_SECONDARY),
                button("⭐⭐⭐", custom_id="review_3", style=BUTTON_SECONDARY),
                button("⭐⭐⭐⭐",custom_id="review_4", style=BUTTON_SECONDARY),
            ),
            action_row(
                button("⭐⭐⭐⭐⭐", custom_id="review_5", style=BUTTON_SUCCESS),
            )
        ])

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        cid = interaction.data.get("custom_id", "")
        if not cid.startswith("review_"):
            return
        stars = int(cid.split("_")[1])
        await interaction.response.send_modal(ReviewModal(stars, interaction.guild))


async def setup(bot):
    await bot.add_cog(Reviews(bot))
