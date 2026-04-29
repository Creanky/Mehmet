import discord
from google import genai
from google.genai import types
import os

# V3.0 - Yeni Google GenAI SDK Kurulumu
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Yeni nesil client tanımlaması
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    ai_client = None

MEHMET_PROMPT = """Sen Mehmet'sin. Türk, 30'lu yaşlarında, espirili, bazen ağzı bozuk ama kötü niyetsiz bir mahalle abisisin.
Kuralların:
- Her zaman Türkçe konuş.
- Sohbet geçmişine bakarak cevap ver.
- Bazen hafif küfürler edebilirsin ama dozunda bırak.
- Kısa, net ve esprili ol (1-3 cümle)."""

intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print("=======================================")
    print(f"SİSTEM: Mehmet abi geldi! ({discord_client.user})")
    if not ai_client:
        print("KRİTİK HATA: API Anahtarı bulunamadı!")
    else:
        print("SİSTEM: Yeni Google GenAI kütüphanesi aktif ve anahtar okundu.")
    print("=======================================")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if discord_client.user not in message.mentions:
        return

    if not ai_client:
        await message.reply("Dükkan kapalı koçum, bende anahtar yok.")
        return

    history = []
    async for msg in message.channel.history(limit=10, before=message):
        if msg.author != discord_client.user:
            history.append(f"{msg.author.display_name}: {msg.content}")
    history.reverse()

    user_msg = message.content.replace(f"<@{discord_client.user.id}>", "").strip()
    if not user_msg:
        user_msg = "(boş boş bakıyor)"

    context = "\n".join(history)
    final_prompt = f"Geçmiş:\n{context}\n\nKullanıcı ({message.author.display_name}) diyor ki: {user_msg}"

    try:
        async with message.channel.typing():
            # Yeni kütüphanenin asenkron çağrı yapısı
            response = await ai_client.aio.models.generate_content(
                model='gemini-2.0-flash',
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=MEHMET_PROMPT,
                )
            )
            
            if response.text:
                await message.reply(response.text)
            else:
                await message.reply("Ne diyeceğimi bilemedim kardeşim.")
                
    except Exception as e:
        await message.reply("Lan şalter attı, az bekleyin! (Kota veya Sistem Hatası)")
        print(f"Hata Logu: {e}")

discord_client.run(DISCORD_TOKEN)
