import telebot
import json
import os
from datetime import datetime
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo,
    MenuButtonWebApp
)

TOKEN = "7181622243:AAHVIIms4gDUAt6VveuH7eJANl72agXQlBY"
bot = telebot.TeleBot(TOKEN)

# URL вашего мини-приложения
WEB_APP_URL = "https://not-a-null.github.io/telegram-mini-app/"

# Файлы для хранения данных
ORDERS_FILE = "orders.json"
USERS_FILE = "users.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Настройка кнопки меню
@bot.message_handler(commands=['setup'])
def setup_menu_button(message):
    if str(message.from_user.id) == "ВАШ_ID_АДМИНА":  # Замените на ваш ID
        menu_button = MenuButtonWebApp(
            text="🕯️ Открыть магазин",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
        bot.set_chat_menu_button(message.chat.id, menu_button)
        bot.reply_to(message, "✅ Кнопка меню настроена!")

@bot.message_handler(commands=['start', 'shop'])
def start(message):
    markup = InlineKeyboardMarkup()
    
    web_app_btn = InlineKeyboardButton(
        text="🕯️ Открыть магазин свечей",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    # Сохраняем пользователя
    users = load_users()
    user = message.from_user
    
    if str(user.id) not in users:
        users[str(user.id)] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'joined': datetime.now().isoformat(),
            'orders_count': 0,
            'total_spent': 0
        }
        save_users(users)
    
    bot.send_message(
        message.chat.id,
        "🕯️ *Добро пожаловать в магазин свечей!*\n\n"
        "Здесь вы найдете свечи ручной работы из натурального воска.\n"
        "Каждая свеча создается с любовью и вниманием к деталям.\n\n"
        "Нажмите кнопку ниже, чтобы открыть магазин:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    try:
        data = json.loads(message.web_app_data.data)
        user = message.from_user
        
        if data['type'] == 'order':
            # Сохраняем заказ
            orders = load_orders()
            users = load_users()
            
            order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            order = {
                'id': order_id,
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name or ''}",
                'username': user.username,
                'items': data['items'],
                'total': data['total'],
                'timestamp': data['timestamp'],
                'status': 'processing'
            }
            
            orders.append(order)
            save_orders(orders)
            
            # Обновляем статистику пользователя
            if str(user.id) in users:
                users[str(user.id)]['orders_count'] += 1
                users[str(user.id)]['total_spent'] += data['total']
                save_users(users)
            
            # Формируем детали заказа
            order_details = f"🛒 *Новый заказ #{order_id}*\n\n"
            order_details += f"👤 *Покупатель:* {user.first_name} {user.last_name or ''}\n"
            order_details += f"📱 *Username:* @{user.username or 'нет'}\n\n"
            order_details += "*Товары:*\n"
            
            for item in data['items']:
                order_details += f"• {item['name']} - {item['quantity']} шт. × {item['price']} ₽\n"
            
            order_details += f"\n💰 *Итого:* {data['total']} ₽\n"
            order_details += f"⏰ *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            order_details += f"📦 *Статус:* В обработке"
            
            # Отправляем подтверждение пользователю
            bot.send_message(
                message.chat.id,
                f"✅ *Заказ принят!*\n\n"
                f"Спасибо за заказ #{order_id} на сумму *{data['total']} ₽*.\n"
                f"Мы свяжемся с вами в течение 24 часов для уточнения деталей доставки.\n\n"
                f"Вы можете отслеживать статус заказа в разделе *Профиль* в магазине.",
                parse_mode="Markdown"
            )
            
            # Отправляем уведомление администратору (если нужно)
            # bot.send_message(ADMIN_CHAT_ID, order_details, parse_mode="Markdown")
            
            print(f"✅ Новый заказ #{order_id} от {user.id}: {data['total']} ₽")
            
    except Exception as e:
        print(f"❌ Ошибка обработки заказа: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при обработке заказа. Пожалуйста, попробуйте еще раз."
        )

@bot.message_handler(commands=['orders'])
def list_orders(message):
    # Только для админа
    if str(message.from_user.id) != "ВАШ_ID_АДМИНА":  # Замените на ваш ID
        return
    
    orders = load_orders()
    
    if not orders:
        bot.reply_to(message, "Заказов пока нет.")
        return
    
    response = f"📋 *Все заказы ({len(orders)})*\n\n"
    
    for order in orders[-10:]:  # Последние 10 заказов
        order_date = datetime.fromisoformat(order['timestamp']).strftime('%d.%m.%Y')
        response += f"*Заказ #{order['id']}*\n"
        response += f"👤 {order['user_name']} (@{order['username'] or 'нет'})\n"
        response += f"💰 {order['total']} ₽\n"
        response += f"📦 {order['status']}\n"
        response += f"⏰ {order_date}\n"
        response += "━━━━━━━━━━━━━━\n"
    
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(message):
    # Только для админа
    if str(message.from_user.id) != "ВАШ_ID_АДМИНА":
        return
    
    orders = load_orders()
    users = load_users()
    
    total_orders = len(orders)
    total_revenue = sum(order['total'] for order in orders)
    total_users = len(users)
    
    response = f"📊 *Статистика магазина*\n\n"
    response += f"🛒 *Всего заказов:* {total_orders}\n"
    response += f"💰 *Общая выручка:* {total_revenue} ₽\n"
    response += f"👥 *Всего пользователей:* {total_users}\n"
    
    # Средний чек
    if total_orders > 0:
        avg_order = total_revenue / total_orders
        response += f"📈 *Средний чек:* {avg_order:.0f} ₽\n"
    
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🕯️ *Свечной магазин - Помощь*

*Команды для покупателей:*
/start - Открыть магазин
/shop - Открыть магазин

*Команды для администратора:*
/orders - Просмотреть заказы
/stats - Статистика магазина
/setup - Настроить кнопку меню

*Техническая поддержка:*
По всем вопросам обращайтесь к @VoplotiBot
    """
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

# Запуск бота
if __name__ == '__main__':
    print("🕯️ Бот магазина свечей запущен!")
    print(f"🌐 Мини-приложение: {WEB_APP_URL}")
    print("⚡ Используйте /setup для настройки кнопки меню")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
