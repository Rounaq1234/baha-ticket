import discord
from discord.ext import commands
from discord import app_commands
import json

class Panel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_json("config.json")

    def load_json(self, path):
        with open(path, "r", encoding="utf8") as f:
            return json.load(f)

    @app_commands.command(
        name="setup-exchange-panel",
        description="Post the exchange panel in this channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_exchange_panel(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Exchange panel placed!", ephemeral=True)

        panel_cfg = self.config.get("panel", {})
        embed = discord.Embed(
            title=panel_cfg.get("title", "Exchange Menu"),
            description=panel_cfg.get("description", "Select an option below."),
            color=int(self.config.get("embed_color", "0x2f3136"), 16)
        )

        flow_cog = self.bot.get_cog("ExchangeFlow")
        if not flow_cog:
            await interaction.followup.send("❌ ERROR: `ExchangeFlow` cog not loaded.", ephemeral=True)
            return

        view = flow_cog.get_panel_view()
        await interaction.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Panel(bot))
