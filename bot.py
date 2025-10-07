from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# --- INSERISCI QUI LE TUE CHIAVI DIRETTAMENTE ---
TOKEN = "7989178986:AAEHrIE41NJF_MduzHp0YYlC4bEefsMGWPI"      # <-- Inserisci qui il tuo token del BotFather
OPENWEATHER_KEY = "acc533319dcdc905c35e31bba7c90e7d"             # <-- Inserisci qui la tua API key OpenWeatherMap
# --------------------------------------------------

# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Ciao! Sono il tuo assistente Telegram. Digita /meteo <città> per iniziare!")

# --- Comando /meteo ---
async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa: /meteo <città>")
        return
    
    città = " ".join(context.args)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={città}&appid={OPENWEATHER_KEY}&units=metric&lang=it"
    r = requests.get(url).json()
    
    if r.get("cod") != 200:
        await update.message.reply_text("❌ Città non trovata.")
        return
    
    descrizione = r["weather"][0]["description"]
    temp = r["main"]["temp"]
    await update.message.reply_text(f"🌤 Meteo a {città}:\n{descrizione.capitalize()}, {temp}°C")

# --- Avvio del bot ---
print("✅ Avvio del bot in corso...")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("meteo", meteo))
app.run_polling()
