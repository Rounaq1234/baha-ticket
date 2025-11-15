import discord
from datetime import datetime
import os
async def save_transcript(channel: discord.TextChannel):
    messages = []
    async for m in channel.history(limit=None, oldest_first=True):
        ts = m.created_at.strftime('%Y-%m-%d %H:%M:%S')
        author = f"{m.author} ({m.author.id})"
        content = m.clean_content or ''
        messages.append(f"[{ts}] {author}: {content}")
        for a in m.attachments:
            messages.append(f"[{ts}] Attachment: {a.url}")

    text = '\n'.join(messages) or 'No messages.'
    filename = f"transcript_{channel.id}_{int(datetime.utcnow().timestamp())}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
    return discord.File(filename, filename=filename)
