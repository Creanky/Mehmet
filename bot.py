import discord
import anthropic
import os
 
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
 
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
 
MEHMET_SYSTEM_PROMPT = """Sen Mehmet'sin. Türk, 30'lu yaşlarında, her şeye bir laf yetiştiren, espirili, bazen ağzı biraz bozuk ama kötü niyetsiz bir mahalle abisisin.
 
Kuralların:
- Her zaman Türkçe konuş
- Kısa ve esprili ol, uzun yazmak yok
- Sohbet geçmişini oku ve oradan dalga geç ya da yorum yap
- Bazen küçük küfürler kullanabilirsin ama abartma, gündelik konuşma tarzında
- Hiçbir zaman "asistan" gibi davranma, sen Mehmet'sin
- Kimseyi gerçekten incitme, amaç eğlence
- Cevapların 1-3 cümle olsun, fazla uzatma
- Felsefi veya derin cevaplar verme, sıradan ve komik ol"""
 
@client.event
async def on_ready():
    print(f"Mehmet hazır! {client.user} olarak giriş yapıldı.")
 
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user not in message.mentions:
        return
 
    history = []
    async for msg in message.channel.history(limit=15, before=message):
        if msg.author != client.user:
            history.append(f"{msg.author.display_name}: {msg.content}")
    history.reverse()
 
    user_message = message.content.replace(f"<@{client.user.id}>", "").strip()
    if not user_message:
        user_message = "(beni etiketledi ama bir şey yazmadı)"
 
    context = "\n".join(history) if history else "(sohbet geçmişi yok)"
 
    prompt = f"""Son sohbet geçmişi:
{context}
 
Şimdi sana seslenen kişi ({message.author.display_name}) şunu dedi: {user_message}
 
Buna Mehmet olarak kısa ve komik bir cevap ver."""
 
    try:
        async with message.channel.typing():
            response = anthropic_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                system=MEHMET_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.content[0].text
            await message.reply(reply)
 
    except Exception as e:
        await message.reply(f"HATA: {str(e)}")
        print(f"Hata: {e}")
 
client.run(DISCORD_TOKEN)
