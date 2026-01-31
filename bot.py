import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "7181622243:AAHVIIms4gDUAt6VveuH7eJANl72agXQlBY"
bot = telebot.TeleBot(TOKEN)

WEB_APP_URL = "https://not-a-null.github.io/telegram-mini-app/"

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    
    web_app_btn = InlineKeyboardButton(
        text="🕯️ Открыть магазин",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id,
        "🕯️ *Магазин свечей*\n\n"
        "Добро пожаловать! Нажмите кнопку ниже, чтобы открыть магазин.",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    try:
        data = json.loads(message.web_app_data.data)
        user = message.from_user
        
        order_text = f"""
🕯️ *Новый заказ!*

*Покупатель:* {user.first_name or ''}
*Заказ:* {data['order']['id']}
*Сумма:* {data['order']['total']} ₽

*Состав заказа:*
"""
        
        for item in data['order']['items']:
            order_text += f"\n• {item['name']} - {item['quantity']} шт."
        
        # Отправляем подтверждение пользователю
        bot.send_message(
            message.chat.id,
            f"✅ *Заказ оформлен!*\n\n"
            f"Номер заказа: {data['order']['id']}\n"
            f"Сумма: {data['order']['total']} ₽\n\n"
            f"Мы свяжемся с вами для уточнения деталей.",
            parse_mode="Markdown"
        )
        
        # Логируем заказ
        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write(order_text + "\n\n")
        
        print(f"Заказ от {user.id}: {data['order']['total']} ₽")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "⚠️ Ошибка при оформлении заказа")

if __name__ == '__main__':
    print("🕯️ Бот запущен!")
    bot.infinity_polling()
