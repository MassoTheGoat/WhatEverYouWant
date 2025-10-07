import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import sys

# 🔹 Carica variabili da .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

API_BASKET_KEY = os.getenv("SPORT_API_KEY")
API_BASKET_HOST = os.getenv("API_BASKET_HOST") 

if not TOKEN or ":" not in TOKEN:
    print("❌ ERRORE: TELEGRAM_TOKEN non trovato o non valido.")
    sys.exit(1)

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

from datetime import datetime

async def sport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa: /sport calcio | basket | volley")
        return
    
    sport_type = context.args[0].lower()
    current_year = datetime.now().year

    # --- Calcio → TheSportsDB ---
    if sport_type == "calcio":
        league_id = 4332  # Serie A
        sport_name = "Serie A (Calcio)"
        await update.message.reply_text(f"📡 Recupero dati per {sport_name}...")

        try:
            # Classifica
            table_url = f"https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l={league_id}"
            table_res = requests.get(table_url).json()
            table = table_res.get("table", [])

            msg = f"🏆 *{sport_name} - Classifica*\n\n"
            if table:
                for team in table[:10]:
                    msg += f"{team.get('intRank','N/D')}. {team.get('strTeam','N/D')} - {team.get('intPoints',0)} pt\n"
            else:
                msg += "⚠️ Classifica non disponibile.\n"

            # Prossime partite
            next_url = f"https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id={league_id}"
            next_res = requests.get(next_url).json()
            events = next_res.get("events", [])

            msg += "\n📅 *Prossime partite:*\n"
            if events:
                for e in events[:5]:
                    home = e.get("strHomeTeam", "N/D")
                    away = e.get("strAwayTeam", "N/D")
                    date = e.get("dateEvent", "N/D")
                    time = e.get("strTime", "")
                    msg += f"• {home} vs {away} — {date} {time}\n"
            else:
                msg += "⚠️ Nessuna partita trovata.\n"

            await update.message.reply_text(msg, parse_mode="Markdown")

        except Exception as e:
            await update.message.reply_text(f"❌ Errore nel recupero dati: {e}")

    # --- Basket o Volley → API-Basketball ---
    elif sport_type in ["basket", "volley"]:
        league_ids = {
            "basket": 12,  # NBA esempio
            "volley": 20   # Lega Volley esempio
        }
        league_id = league_ids[sport_type]
        sport_name = sport_type.capitalize()
        await update.message.reply_text(f"📡 Recupero dati per {sport_name}...")

        headers = {
            "X-RapidAPI-Key": API_BASKET_KEY,
            "X-RapidAPI-Host": API_BASKET_HOST
        }

        try:
            # Calcola stagione in formato YYYY
            season = current_year

            # Classifica
            standings_url = f"https://api-basketball.p.rapidapi.com/standings?league={league_id}&season={season}"
            r = requests.get(standings_url, headers=headers).json()
            standings = r.get("response", [])

            msg = f"🏆 *{sport_name} - Classifica*\n\n"
            if standings:
                for team in standings[:10]:
                    team_name = team["team"]["name"]
                    rank = team.get("rank", "N/D")
                    points = team.get("points", "N/D")
                    msg += f"{rank}. {team_name} - {points} pt\n"
            else:
                msg += "⚠️ Classifica non disponibile.\n"

            # Prossime partite
            games_url = f"https://api-basketball.p.rapidapi.com/games?league={league_id}&season={season}&next=5"
            r2 = requests.get(games_url, headers=headers).json()
            games = r2.get("response", [])

            msg += "\n📅 *Prossime partite:*\n"
            if games:
                for g in games:
                    home = g["teams"]["home"]["name"]
                    away = g["teams"]["away"]["name"]
                    date = g["date"].split("T")[0]
                    time = g["date"].split("T")[1][:5]
                    msg += f"• {home} vs {away} — {date} {time}\n"
            else:
                msg += "⚠️ Nessuna partita trovata.\n"

            await update.message.reply_text(msg, parse_mode="Markdown")

        except Exception as e:
            await update.message.reply_text(f"❌ Errore nel recupero dati: {e}")

    else:
        await update.message.reply_text("⚠️ Sport non riconosciuto! Usa: /sport calcio | basket | volley")

# --- Avvio del bot ---
print("✅ Avvio del bot in corso...")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("meteo", meteo))
app.add_handler(CommandHandler("sport", sport))
app.run_polling()
