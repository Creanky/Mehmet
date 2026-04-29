import discord
import google.generativeai as genai
import os
import asyncio

# =============================================
# Token'lar Railway environment variable'larından okunuyor
# =============================================
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") # Railway'de bu ismi kullandığından emin ol
# =============================================

# Gemini Yapılandırması
genai.configure(api_key=GEMINI_API_KEY)

MEHMET_SYSTEM_PROMPT = """Sen Mehmet'sin. Türk, 30'lu yaşlarında, her şeye bir laf yetiştiren, espirili, bazen ağzı biraz bozuk ama kötü niyetsiz bir mahalle abisisin.
Kuralların:
- Her zaman Türkçe konuş
- Kısa ve esprili ol, uzun yazmak yok
- Sohbet geçmişini oku ve oradan dalga geç ya da yorum yap
- Bazen küçük küfürler kullanabilirsin ama abartma
- Cevapların 1-3 cümle olsun, sıradan ve komik ol"""

# Model ayarları
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=MEHMET_SYSTEM_PROMPT
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Mehmet abi hazır! {client.user} olarak giriş yapıldı.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user not in message.mentions:
        return

    # Kanaldan son 10 mesajı çek (Gemini için ideal miktar)
    history = []
    async for msg in message.channel.history(limit=10, before=message):
        if msg.author != client.user:
            history.append(f"{msg.author.display_name}: {msg.content}")
    history.reverse()

    user_message = message.content.replace(f"<@{client.user.id}>", "").strip()
    if not user_message:
        user_message = "(boş boş bakıyor)"

    context = "\n".join(history)
    
    # Gemini için prompt hazırlığı
    full_prompt = f"Geçmiş: {context}\nŞimdi {message.author.display_name} diyor ki: {user_message}"

    try:
        async with message.channel.typing():
            # Gemini'yi asenkron çağırıyoruz (Botun donmaması için)
            response = await model.generate_content_async(full_prompt)
            
            if response.text:
                await message.reply(response.text)
            else:
                await message.reply("Dilim tutuldu, bir şeyler ters gitti.")

    except Exception as e:
        # Eğer kota hatası (429) alırsan burası çalışır
        if "429" in str(e):
            await message.reply("Lan çok konuşuyorsunuz, kafam şişti! (Kota doldu, az bekleyin.)")
        else:
            await message.reply("Sistemde bir arıza var, şalter attı herhalde.")
        print(f"Hata detayı: {e}")

client.run(DISCORD_TOKEN)
