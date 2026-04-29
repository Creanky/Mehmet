import discord
import google.generativeai as genai
import os
import asyncio

# =============================================
# Token'lar Railway environment variable'larından okunuyor
# =============================================
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")[cite: 3]
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")[cite: 3]
# =============================================

# Gemini Yapılandırması
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)[cite: 3]

MEHMET_SYSTEM_PROMPT = """Sen Mehmet'sin. Türk, 30'lu yaşlarında, her şeye bir laf yetiştiren, espirili, bazen ağzı biraz bozuk ama kötü niyetsiz bir mahalle abisisin.
Kuralların:
- Her zaman Türkçe konuş
- Kısa ve esprili ol, uzun yazmak yok
- Sohbet geçmişini oku ve oradan dalga geç ya da yorum yap
- Bazen küçük küfürler kullanabilirsin ama abartma
- Cevapların 1-3 cümle olsun, sıradan ve komik ol"""[cite: 3]

# Model ayarları
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",[cite: 3]
    system_instruction=MEHMET_SYSTEM_PROMPT[cite: 3]
)

intents = discord.Intents.default()[cite: 3]
intents.message_content = True[cite: 3]
client = discord.Client(intents=intents)[cite: 3]

@client.event
async def on_ready():
    print("---------------------------------------")
    print(f"Mehmet abi hazır! {client.user} olarak giriş yapıldı.")[cite: 3]
    
    # API Key Kontrolü (Hata varsa burada yazar)
    if not GEMINI_API_KEY:
        print("KRİTİK HATA: GEMINI_API_KEY bulunamadı! Railway variables kısmını kontrol et.")
    else:
        print(f"Sistem: API Anahtarı yüklendi. Başlangıcı: {GEMINI_API_KEY[:5]}...")
    print("---------------------------------------")

@client.event
async def on_message(message):
    if message.author == client.user:[cite: 3]
        return

    if client.user not in message.mentions:[cite: 3]
        return

    # Kanaldan son 10 mesajı çek
    history = []
    async for msg in message.channel.history(limit=10, before=message):[cite: 3]
        if msg.author != client.user:
            history.append(f"{msg.author.display_name}: {msg.content}")[cite: 3]
    history.reverse()

    user_message = message.content.replace(f"<@{client.user.id}>", "").strip()[cite: 3]
    if not user_message:
        user_message = "(boş boş bakıyor)"

    context = "\n".join(history)
    full_prompt = f"Geçmiş: {context}\nŞimdi {message.author.display_name} diyor ki: {user_message}"[cite: 3]

    try:
        async with message.channel.typing():[cite: 3]
            response = await model.generate_content_async(full_prompt)[cite: 3]
            
            if response.text:
                await message.reply(response.text)[cite: 3]
            else:
                await message.reply("Dilim tutuldu, bir şeyler ters gitti.")[cite: 3]

    except Exception as e:
        if "429" in str(e):
            await message.reply("Lan çok konuşuyorsunuz, kafam şişti! (Kota doldu, az bekleyin.)")[cite: 3]
        else:
            await message.reply("Sistemde bir arıza var, şalter attı herhalde.")[cite: 3]
        print(f"Hata detayı: {e}")[cite: 3]

client.run(DISCORD_TOKEN)[cite: 3]
