import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Вставьте ваш токен от @BotFather
TOKEN = "7181622243:AAHVIIms4gDUAt6VveuH7eJANl72agXQlBY"
bot = telebot.TeleBot(TOKEN)

# URL вашего мини-приложения на GitHub Pages
WEB_APP_URL = "https://not-a-null.github.io/telegram-mini-app/"

# Файл для хранения заказов (просто текстовый файл)
ORDERS_FILE = "orders.txt"

# 🚀 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем кнопку для открытия магазина
    markup = InlineKeyboardMarkup()
    
    web_app_btn = InlineKeyboardButton(
        text="🛍️ Открыть магазин свечей",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id,
        "🕯️ Добро пожаловать в магазин свечей!\n\n"
        "Нажмите кнопку ниже, чтобы открыть каталог:",
        reply_markup=markup
    )

# 📨 Обработка заказов из мини-приложения
@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    try:
        # Получаем данные заказа
        data = json.loads(message.web_app_data.data)
        user = message.from_user
        
        # Формируем сообщение о заказе
        order_text = f"""
        🛒 НОВЫЙ ЗАКАЗ!
        
        👤 Покупатель: {user.first_name} {user.last_name or ''}
        📱 Username: @{user.username or 'нет'}
        
        💰 Сумма: {data['total']} ₽
        💳 Способ оплаты: {data['payment']}
        ⏰ Время: {data['time']}
        
        📦 Состав заказа:"""
        
        # Добавляем товары
        for item in data['cart']:
            order_text += f"\n  • {item['name']} - {item['quantity']} шт. × {item['price']} ₽"
        
        # Сохраняем заказ в файл
        with open(ORDERS_FILE, "a", encoding="utf-8") as f:
            f.write("="*50 + "\n")
            f.write(order_text + "\n")
            f.write("="*50 + "\n\n")
        
        # Отправляем подтверждение пользователю
        bot.send_message(
            message.chat.id,
            f"✅ Спасибо за заказ, {user.first_name}!\n\n"
            f"Заказ на сумму {data['total']} ₽ оформлен.\n"
            f"Мы свяжемся с вами для уточнения деталей.",
            parse_mode="Markdown"
        )
        
        # Отправляем заказ администратору (если указан ADMIN_ID)
        # Если вы админ, можете раскомментировать:
        # if ADMIN_ID:
        #     bot.send_message(ADMIN_ID, order_text)
        
        print(f"Новый заказ от {user.id}: {data['total']} ₽")
        
    except Exception as e:
        print(f"Ошибка обработки заказа: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при обработке заказа")

# 📋 Команда /orders (только для админа)
@bot.message_handler(commands=['orders'])
def show_orders(message):
    # Простая проверка на админа - можно настроить лучше
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = f.read()
        
        if orders:
            # Отправляем последние 2000 символов (ограничение Telegram)
            bot.send_message(message.chat.id, orders[-2000:])
        else:
            bot.send_message(message.chat.id, "Заказов пока нет")
    except:
        bot.send_message(message.chat.id, "Файл с заказами пуст или не создан")

# ❓ Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "🕯️ *Магазин свечей - Бот*\n\n"
        "Команды:\n"
        "/start - открыть магазин\n"
        "/help - эта справка\n\n"
        "Магазин работает через мини-приложение в Telegram.",
        parse_mode="Markdown"
    )

# Запуск бота
if __name__ == '__main__':
    print("🕯️ Бот магазина свечей запущен!")
    print(f"📱 Мини-приложение: {WEB_APP_URL}")
    bot.infinity_polling()
