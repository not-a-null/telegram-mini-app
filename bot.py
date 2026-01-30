import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# 🔑 Вставьте сюда токен от @BotFather
TOKEN = "7181622243:AAHVIIms4gDUAt6VveuH7eJANl72agXQlBY"
bot = telebot.TeleBot(TOKEN)

# 🚀 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем кнопку для мини-приложения
    markup = InlineKeyboardMarkup()
    
    # 🖱️ Кнопка открывает мини-приложение на GitHub Pages
    web_app_btn = InlineKeyboardButton(
        text="🎮 Открыть игру",
        web_app=WebAppInfo(url="https://not-a-null.github.io/telegram-mini-app/")
    )
    
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я простой бот с мини-приложением.\n\n"
        "Нажми кнопку ниже, чтобы открыть мини-игру:",
        reply_markup=markup
    )

# 📨 Получаем данные из мини-приложения
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    data = message.web_app_data.data
    user = message.from_user
    
    # Отправляем ответ пользователю
    bot.send_message(
        message.chat.id,
        f"✅ {user.first_name}, ты отправил: *{data}*",
        parse_mode="Markdown"
    )
    
    # Логируем в консоль
    print(f"Пользователь {user.id} отправил: {data}")

# ❓ Помощь
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Простой бот с мини-приложением.\n\n"
        "Команды:\n"
        "/start - начать работу\n"
        "/help - эта справка\n\n"
        "Мини-приложение отправит данные обратно в бота."
    )

# 🎯 Запуск бота
print("🤖 Бот запущен! Нажми Ctrl+C для остановки.")
bot.infinity_polling()
