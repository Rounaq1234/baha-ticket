import discord
from discord.ext import commands
import asyncio
from utils.loader import load_config, load_flows

config = load_config()
flows = load_flows()


class AmountModal(discord.ui.Modal):
    def __init__(self, title, callback_fn):
        super().__init__(title=title)
        self.callback_fn = callback_fn
        self.amount = discord.ui.TextInput(label="Enter Amount", placeholder="Example: 150", required=True)
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback_fn(interaction, self.amount.value)


class MethodSelect(discord.ui.Select):
    def __init__(self, parent, methods):
        self.parent = parent
        options = [discord.SelectOption(label=v.get('label', k), value=k, description="".join([v.get('summary','')])) for k,v in methods.items()]
        super().__init__(placeholder="Choose what you want to exchange...", options=options, min_values=1, max_values=1, custom_id='method_select')

    async def callback(self, interaction: discord.Interaction):
        method_id = self.values[0]
        await self.parent.start_flow(interaction, method_id)


class ExchangePanel(discord.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=None)
        self.add_item(MethodSelect(parent, flows.get('methods', {})))


class ExchangeFlow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_panel_view(self):
        return ExchangePanel(self)

    async def start_flow(self, interaction: discord.Interaction, method_id: str):
        method = flows.get('methods', {}).get(method_id)
        if not method:
            return await interaction.response.send_message('Invalid method selected.', ephemeral=True)

        # reply quickly
        await interaction.response.send_message(f"🔄 Starting **{method.get('label','Exchange')}** exchange...", ephemeral=True)

        fee_rate = float(method.get('fee', 0))

        async def modal_result(modal_inter: discord.Interaction, amount_text):
            try:
                amount = float(amount_text.replace(',', '').strip())
            except:
                return await modal_inter.response.send_message('❌ Invalid number entered.', ephemeral=True)

            fee_amount = round(amount * fee_rate, 2)
            receive = round(amount - fee_amount, 2)

            tickets = modal_inter.client.get_cog('Tickets')
            if not tickets:
                return await modal_inter.followup.send('❌ Ticket system missing.', ephemeral=True)

            await tickets.create_ticket(modal_inter, method, amount, fee_amount, receive)

        modal = AmountModal(f"{method.get('label','Amount')} Amount", modal_result)
        await interaction.followup.send_modal(modal)


async def setup(bot):
    await bot.add_cog(ExchangeFlow(bot))
