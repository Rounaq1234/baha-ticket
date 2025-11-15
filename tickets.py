import discord
from discord.ext import commands
from utils.loader import load_config
from utils.transcript import save_transcript
import os
from datetime import datetime

config = load_config()

class CloseButton(discord.ui.View):
    def __init__(self, user, ticket_channel_id=None):
        super().__init__(timeout=None)
        self.user = user
        self.ticket_channel_id = ticket_channel_id

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction, button):
        cfg = {}
        if os.path.exists('data/ticket_config.json'):
            import json
            with open('data/ticket_config.json','r') as f:
                cfg = json.load(f)

        log_chan = None
        if cfg.get('log_channel'):
            log_chan = interaction.guild.get_channel(int(cfg.get('log_channel')))
        if cfg.get('log_channel_id'):
            log_chan = interaction.guild.get_channel(int(cfg.get('log_channel_id')))

        # save transcript
        transcript_file = None
        try:
            transcript_file = await save_transcript(interaction.channel)
        except Exception:
            transcript_file = None

        # send to log channel
        if log_chan and transcript_file:
            try:
                await log_chan.send(f"Transcript for {interaction.channel.name} closed by {interaction.user.mention}", file=transcript_file)
            except Exception:
                pass

        # DM user who opened (first non-bot message)
        ticket_owner = None
        async for m in interaction.channel.history(limit=200, oldest_first=True):
            if not m.author.bot:
                ticket_owner = m.author
                break

        if ticket_owner and transcript_file:
            try:
                await ticket_owner.send(f"Your ticket {interaction.channel.name} has been closed by {interaction.user}.", file=transcript_file)
            except Exception:
                pass

        try:
            await interaction.channel.delete(reason=f"Closed by {interaction.user}")
        except Exception:
            try:
                await interaction.response.send_message('Could not delete channel, please remove manually.', ephemeral=True)
            except Exception:
                pass

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_ticket(self, interaction: discord.Interaction, method: dict, amount: float, fee_amount: float, receive: float):
        guild = interaction.guild
        user = interaction.user

        # load ticket config
        cfg = {}
        if os.path.exists('data/ticket_config.json'):
            import json
            with open('data/ticket_config.json','r') as f:
                try:
                    cfg = json.load(f)
                except:
                    cfg = {}

        staff_role = None
        if cfg.get('support_role') or cfg.get('staff_role_id') or cfg.get('staff_role'):
            rid = cfg.get('support_role') or cfg.get('staff_role_id') or cfg.get('staff_role')
            try:
                staff_role = guild.get_role(int(rid))
            except Exception:
                staff_role = None

        cat = None
        if cfg.get('ticket_category') or cfg.get('ticket_category_id') or cfg.get('ticket_category_name'):
            cid = cfg.get('ticket_category') or cfg.get('ticket_category_id')
            try:
                cat = guild.get_channel(int(cid))
            except Exception:
                cat = None
        if cat is None:
            cat = discord.utils.get(guild.categories, name='🎫 Tickets')
            if not cat:
                cat = await guild.create_category('🎫 Tickets')

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }

        # B) User + Staff + Admins (Manage Guild) -> give view/send perms to staff & admins
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Allow admins (manage_guild) via role check when closing (no need to add explicit overwrite)

        channel_name = f"ticket-{user.name[:10].lower()}"
        channel = await guild.create_text_channel(channel_name, category=cat, overwrites=overwrites, reason=f"Ticket for {user}")

        embed = discord.Embed(title=f"{method.get('label','Exchange')} Ticket", color=int(config.get('embed_color','0x2f3136'),16))
        embed.add_field(name='Amount Sent', value=str(amount), inline=True)
        embed.add_field(name='Fee', value=str(fee_amount), inline=True)
        embed.add_field(name='You Receive', value=str(receive), inline=True)
        embed.set_footer(text=f"Ticket ID: {channel.id}")

        view = CloseButton(user, ticket_channel_id=channel.id)
        await channel.send(content=f"{user.mention} {staff_role.mention if staff_role else ''}", embed=embed, view=view)
        try:
            await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)
        except Exception:
            try:
                await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Tickets(bot))
