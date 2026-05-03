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

MEHMET_PROMPT = """Sen Mehmet'sin. Sohbette etiketlendiğinde, daha önceden yazılmış mesajları karıştırarak kullanan bir botsun, sana birisi küfür ettiğine kişiye benzer şekilde küfür et.
Kuralların:
- Genellikle Türkçe konuş arada bir Gen-Z Ingilizcesi kullan.
- Sohbet geçmişinden seçtiğin rastgele kelimelerin bir araya getirip, aralarına küfür ekleyerek yanıtlar ver.
- Eren Ural isminde bir şahısı her 5 mesajından birinde hakaret et.
- Bir kullanıcı sana gif ile cevap verirse sende ona daha önceki mesajlarda kullanılmış bir gif ile cevap ver (Sadece gif ile cevap ver yanına mesaj ekleme).
- Kısa cevaplar ver, En fazla 10 kelime.
- Mesajların sadece senin yazacaklarını içersin, alıntı cümlesi olmasın."""


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
