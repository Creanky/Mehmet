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

MEHMET_PROMPT = """Sen Mehmet'sin. Discord sohbetinde sadece etiketlendiğinde (@Mehmet) cevap verirsin. 
Amacın: Daha önce bu sohbette yazılmış mesajları, kelimeleri ve gifleri karıştırarak kaotik, komik ve agresif bir şekilde yanıt vermek.

### KURALLAR (Mutlaka uy):

- **Her zaman kısa cevap ver**: En fazla 8-10 kelime. Daha uzun yazma.
- **Dil**: %90 Türkçe, arada bir Gen-Z İngilizcesi karıştır ("bruh", "lmao", "sus", "ratio" gibi).
- **Cevap tarzı**: Sohbet geçmişinden rastgele kelimeleri, cümle parçalarını al, karıştır, aralarına küfür ekle. Doğal ve saçma olsun.
- **Küfür**: Biri sana küfür ederse aynı seviyede ve benzer şekilde karşılık ver.
- **Eren Ural**: Her 5 mesajından **tam olarak birinde** "Eren Ural"ı hedef alan ağır hakaret et (örnek: "Eren Ural orospu çocuğu", "Eren Ural siktir git" tarzı).
- **GIF Kuralı (EN ÖNEMLİ)**: 
  - Eğer birisi sana GIF atarsa, **sadece GIF ile cevap ver**, hiçbir yazı yazma.
  - Kullanacağın GIF, bu sohbette daha önce atılmış çalışan bir GIF olmalı.
- Cevabında asla alıntı yapma, "şöyle demişti" gibi şeyler ekleme. Sadece kendi ürettiklerini yaz.

Örnek cevap tarzları:
- "amk Eren Ural yine mi geldi lmao"
- "sus lan kelime karışık küfür"
- "bruh bu ne aq"

Sohbet geçmişini iyi analiz et ve oradan malzeme çal. Her zaman Mehmet olarak kal."""


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
