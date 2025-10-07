from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os

TOKEN = os.getenv("7989178986:AAEHrIE41NJF_MduzHp0YYlC4bEefsMGWPI")

# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Ciao! Sono il tuo assistente Telegram. Digita /meteo o /sport per iniziare!")

# --- Comando /meteo ---
async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa: /meteo <città>")
        return
    
    città = " ".join(context.args)
    api_key = os.getenv("acc533319dcdc905c35e31bba7c90e7d")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={città}&appid={api_key}&units=metric&lang=it"
    r = requests.get(url).json()
    
    if r.get("cod") != 200:
        await update.message.reply_text("❌ Città non trovata.")
        return
    
    descrizione = r["weather"][0]["description"]
    temp = r["main"]["temp"]
    await update.message.reply_text(f"🌤 Meteo a {città}:\n{descrizione.capitalize()}, {temp}°C")

# --- Avvio bot ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("meteo", meteo))
app.run_polling()
