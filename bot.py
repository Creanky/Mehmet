import discord
import google.generativeai as genai
import os

# V2.1 - Temiz Kurulum (Bu yorum satırı Railway'in güncellemeyi fark etmesini sağlar)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Prompt biraz daha sadeleştirildi
MEHMET_PROMPT = """Sen Mehmet'sin. Türk, 30'lu yaşlarında, espirili, bazen ağzı bozuk ama kötü niyetsiz bir mahalle abisisin.
Kuralların:
- Her zaman Türkçe konuş.
- Sohbet geçmişine bakarak cevap ver.
- Bazen hafif küfürler edebilirsin ama dozunda bırak.
- Kısa, net ve esprili ol (1-3 cümle)."""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    system_instruction=MEHMET_PROMPT
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("=======================================")
    print(f"SİSTEM: Mehmet abi geldi! ({client.user})")
    
    if not GEMINI_API_KEY:
        print("KRİTİK HATA: API Anahtarı bulunamadı!")
    else:
        print("SİSTEM: API Anahtarı başarıyla okundu.")
    print("=======================================")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user not in message.mentions:
        return

    history = []
    async for msg in message.channel.history(limit=10, before=message):
        if msg.author != client.user:
            history.append(f"{msg.author.display_name}: {msg.content}")
    history.reverse()

    user_msg = message.content.replace(f"<@{client.user.id}>", "").strip()
    if not user_msg:
        user_msg = "(boş boş bakıyor)"

    context = "\n".join(history)
    final_prompt = f"Geçmiş:\n{context}\n\nKullanıcı ({message.author.display_name}) diyor ki: {user_msg}"

    try:
        async with message.channel.typing():
            response = await model.generate_content_async(final_prompt)
            if response.text:
                await message.reply(response.text)
            else:
                await message.reply("Ne diyeceğimi bilemedim kardeşim.")
                
    except Exception as e:
        await message.reply("Lan şalter attı, az bekleyin! (Sistem Hatası)")
        print(f"Hata Logu: {e}")

client.run(DISCORD_TOKEN)
