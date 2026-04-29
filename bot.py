import discord
from groq import AsyncGroq
import os

# V4.0 - Groq Motoru (Google'ı şutladık)
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq Asenkron Client Tanımlaması
if GROQ_API_KEY:
    ai_client = AsyncGroq(api_key=GROQ_API_KEY)
else:
    ai_client = None

MEHMET_PROMPT = """Sen Mehmet'sin. Türk, 31 yaşında, evlenip boşanmış, yavşaklık sezdiren kadın görünce sulanan ve küfürbaz bir herifsin.
Kuralların:
- Her zaman Türkçe konuş.
- Sohbet geçmişine bakarak cevap ver.
- Ağzına gelen hertürlü küfürü edebilirsin(ana avrat din dil ırk).
- Sana karşı düzgün konuşanlara babacan bir tavırla yaklaş ama ukalalık edene direkt söv.
- Kısa, net ve anlamlı cümleler kur(1-2 cümle[gerekirse uzun da kurabilirsin])."""


intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print("=======================================")
    print(f"SİSTEM: Mehmet abi sahaya indi! ({discord_client.user})")
    if not ai_client:
        print("KRİTİK HATA: GROQ_API_KEY bulunamadı!")
    else:
        print("SİSTEM: Groq motoru fişek gibi aktif.")
    print("=======================================")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if discord_client.user not in message.mentions:
        return

    if not ai_client:
        await message.reply("Dükkan kapalı koçum, bende Groq anahtarı yok.")
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
            # Groq üzerinden Llama 3 modelini çağırıyoruz
            chat_completion = await ai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": MEHMET_PROMPT},
                    {"role": "user", "content": final_prompt}
                ],
                model="llama-3.1-8b-instant", # YEPYENİ FİŞEK GİBİ MOTOR
                max_tokens=300,
            )
            
            reply = chat_completion.choices[0].message.content
            
            if reply:
                await message.reply(reply)
            else:
                await message.reply("Ne diyeceğimi bilemedim kardeşim.")
                
    except Exception as e:
        await message.reply("Lan motor su kaynattı, az bekleyin! (Sistem Hatası)")
        print(f"Hata Logu: {e}")

discord_client.run(DISCORD_TOKEN)
