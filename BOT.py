import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

FOOTBALL_API_KEY = "1d24e786410749a49e3fbb6404f2a067"

TEAMS_AR = {
    "Real Madrid CF": "ريال مدريد",
    "FC Barcelona": "برشلونة",
    "Atletico Madrid": "أتلتيكو مدريد",
    "Real Sociedad de Fútbol": "ريال سوسيداد",
    "Villarreal CF": "فياريال",
    "Manchester City FC": "مانشستر سيتي",
    "Arsenal FC": "أرسنال",
    "Liverpool FC": "ليفربول",
    "Manchester United FC": "مانشستر يونايتد",
    "Chelsea FC": "تشيلسي",
    "Tottenham Hotspur FC": "توتنهام هوتسبير",
    "AC Milan": "ميلان",
    "Juventus FC": "يوفنتوس",
    "Paris Saint-Germain FC": "باريس سان جيرمان",
    "FC Bayern München": "بايرن ميونخ"
}

def get_ar_name(name):
    return TEAMS_AR.get(name, name)

LEAGUES = {
    "CL": "🇪🇺 دوري أبطال أوروبا",
    "PL": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 الدوري الإنجليزي",
    "PD": "🇪🇸 الدوري الإسباني",
    "SA": "🇮🇹 الدوري الإيطالي",
    "FL1": "🇫🇷 الدوري الفرنسي",
    "BL1": "🇩🇪 الدوري الألماني"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت كرة القدم الشامل! ⚽🏆\n\n"
        "أنا مساعدك الرياضي لجلب جدول مباريات الدوريات الكبرى وترجمة أسماء الفرق للعربية.\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "• /matches - لعرض قائمة البطولات واختيار الدوري.\n"
        "• /start - لعرض رسالة الترحيب.\n\n"
        "اضغط على /matches وابدأ التصفح الآن!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def matches_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=code)] for code, name in LEAGUES.items()]
    await update.message.reply_text("🏆 **اختر الدوري الذي تريد عرض مبارياته:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    league_code = query.data
    league_name = LEAGUES.get(league_code, "البطولة")
    
    url = f"https://api.football-data.org/v4/competitions/{league_code}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    try:
        response = requests.get(url, headers=headers).json()
        matches = response.get("matches", [])
        
        if not matches:
            await query.edit_message_text(text=f"❌ لا توجد مباريات مجدولة حالياً لـ {league_name}.")
            return

        text = f"📅 **مباريات {league_name} القادمة:**\n\n"
        for m in matches[:5]:
            home = get_ar_name(m['homeTeam']['name'])
            away = get_ar_name(m['awayTeam']['name'])
            utc_date = m['utcDate'].replace('T', ' ').split('Z')[0]
            text += f"⚽ {home} vs {away}\n⏰ {utc_date}\n\n"
            
        await query.edit_message_text(text=text, parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(text="⚠️ حدث خطأ أثناء جلب البيانات.")

def main():
    TELEGRAM_TOKEN = "تم حجب بسبب رفعها في جيت هوب لأسباب أمنية"
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("matches", matches_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("البوت يعمل الآن بدون أخطاء...")
    app.run_polling()

if __name__ == "__main__":
    main()