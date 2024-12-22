import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
APPS_SCRIPT_URL = os.getenv('APPS_SCRIPT_WEB_APP_URL')

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
telebot.logger.setLevel(logging.DEBUG)

# Store user transaction data
user_data = {}

def create_category_keyboard(transaction_type):
    markup = InlineKeyboardMarkup(row_width=2)
    categories = {
        'income': ['Salary', 'Commissions', 'Loans', 'Bonus'],
        'expense': ['🍪 Cravings', '💳 Debt Paid Off', '🎁 Gifts', '🎭 Going Out', 
                   '🛒 Groceries', '📈 Growth', '⚕️ Health', '🏠 House Expenses',
                   '🤷 Incidential', '💰 Loans', '🧴 Personal Care', '🍽️ Restaurants',
                   '🛍️ Shopping', '📱 Subscriptions', '💱 Transfer', '🚗 Transport']
    }
    buttons = [InlineKeyboardButton(cat, callback_data=f"cat_{cat}") 
               for cat in categories[transaction_type]]
    markup.add(*buttons)
    return markup

def create_account_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    accounts = ['🏦 Bancolombia', '📱 Nequi', '📱 Daviplata', '💱 Binance', 
                '🏦 Scotiabank', '🏦 Davivienda', '💵 Cash']
    buttons = [InlineKeyboardButton(acc, callback_data=f"acc_{acc}") 
               for acc in accounts]
    markup.add(*buttons)
    return markup

def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("💰 Income", callback_data="menu_income"),
        InlineKeyboardButton("💸 Expense", callback_data="menu_expense"),
        InlineKeyboardButton("📊 Statistics", callback_data="menu_stats"),
        InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")
    ]
    markup.add(*buttons)
    bot.send_message(chat_id, "What would you like to do?", reply_markup=markup)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = """Welcome to your Personal Finance Bot! 📊

I'll help you record your transactions step by step.
Just click the buttons below to get started!"""
    show_main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_menu(call):
    chat_id = call.message.chat.id
    action = call.data.replace('menu_', '')
    
    if action in ['income', 'expense']:
        user_data[chat_id] = {'type': action}
        bot.edit_message_text(
            f"Please select a {action} category:",
            chat_id,
            call.message.message_id,
            reply_markup=create_category_keyboard(action)
        )
    elif action == 'stats':
        bot.answer_callback_query(call.id, "Statistics feature coming soon!")
    elif action == 'settings':
        bot.answer_callback_query(call.id, "Settings feature coming soon!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def handle_category(call):
    chat_id = call.message.chat.id
    category = call.data.replace('cat_', '')
    
    if chat_id in user_data:
        user_data[chat_id]['category'] = category
        bot.edit_message_text(
            f"Category selected: {category}\nNow select the account:",
            chat_id,
            call.message.message_id,
            reply_markup=create_account_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('acc_'))
def handle_account(call):
    chat_id = call.message.chat.id
    account = call.data.replace('acc_', '')
    
    if chat_id in user_data:
        user_data[chat_id]['account'] = account
        bot.edit_message_text(
            f"Account selected: {account}\n\nNow, please enter a description:",
            chat_id,
            call.message.message_id
        )

@bot.message_handler(func=lambda message: (
    message.chat.id in user_data and 
    'account' in user_data[message.chat.id] and 
    'description' not in user_data[message.chat.id]
))
def handle_description(message):
    chat_id = message.chat.id
    print(f"\n=== DESCRIPTION HANDLER ===")
    print(f"Chat ID: {chat_id}")
    print(f"Message: {message.text}")
    
    user_data[chat_id]['description'] = message.text
    bot.reply_to(
        message, 
        "Now, please enter the amount:\n\n"
        "💡 Use whole numbers only, without decimals or commas\n"
        "✅ Correct: 50000\n"
        "❌ Incorrect: 50,000 or 50.000"
    )

@bot.message_handler(func=lambda message: (
    message.chat.id in user_data and 
    'description' in user_data[message.chat.id] and 
    'amount' not in user_data[message.chat.id] and 
    not message.from_user.is_bot and
    message.text.replace(',', '').replace('.', '').isdigit()  # Verificar que sea número
))
def handle_amount(message):
    chat_id = message.chat.id
    print(f"\n=== AMOUNT HANDLER ===")
    print(f"Chat ID: {chat_id}")
    print(f"Amount input: {message.text}")
    print(f"Current user_data: {user_data[chat_id]}")
    
    try:
        # Convertir a entero
        amount = int(message.text.replace(',', '').replace('.', ''))
        
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # Preparar datos
        transaction_data = user_data[chat_id].copy()  # Hacer una copia
        transaction_data['amount'] = amount

        # Enviar a Google Sheets
        data = {
            'function': 'addIncome' if transaction_data['type'] == 'income' else 'addExpense',
            'category': transaction_data['category'],
            'account': transaction_data['account'],
            'description': transaction_data['description'],
            'amount': amount,
            'dateInput': 'today'
        }

        print(f"Sending to Sheets: {data}")
        response = requests.post(APPS_SCRIPT_URL, data=data)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            summary = (f"✅ Transaction recorded successfully!\n\n"
                      f"Type: {transaction_data['type'].title()}\n"
                      f"Category: {transaction_data['category']}\n"
                      f"Account: {transaction_data['account']}\n"
                      f"Description: {transaction_data['description']}\n"
                      f"Amount: ${amount:,}")
            
            # Importante: Primero limpiar datos, luego enviar mensajes
            del user_data[chat_id]
            print("User data cleared")
            
            bot.reply_to(message, summary)
            show_main_menu(chat_id)
        else:
            del user_data[chat_id]
            bot.reply_to(message, "❌ Error adding transaction. Please try again with /income or /expense")
            show_main_menu(chat_id)

    except ValueError as e:
        print(f"ValueError: {str(e)}")
        bot.reply_to(
            message,
            "❌ Invalid amount. Please enter a valid number greater than 0."
        )
        del user_data[chat_id]
        show_main_menu(chat_id)

# Handler de fallback para mensajes que no son números en el paso de amount
@bot.message_handler(func=lambda message: (
    message.chat.id in user_data and 
    'description' in user_data[message.chat.id] and 
    'amount' not in user_data[message.chat.id] and 
    not message.from_user.is_bot
))
def handle_invalid_amount(message):
    chat_id = message.chat.id
    print(f"\n=== INVALID AMOUNT HANDLER ===")
    print(f"Invalid input: {message.text}")
    
    bot.reply_to(
        message,
        "❌ Invalid amount format.\n\n"
        "Please enter only numbers:\n"
        "✅ Correct: 50000\n"
        "❌ Incorrect: 50.000 or $50,000 or 50k"
    )

# Debug handler modificado también
@bot.message_handler(func=lambda message: True)
def debug_messages(message):
    if not message.from_user.is_bot:  # Solo debuggear mensajes de usuarios
        print(f"\n=== DEBUG MESSAGE ===")
        print(f"From User: {message.from_user.username}")
        print(f"Message ID: {message.message_id}")
        print(f"Chat ID: {message.chat.id}")
        print(f"Text: {message.text}")
        print(f"Current user_data: {user_data}")
        print("=== DEBUG END ===\n")

print("Bot is running...")
bot.infinity_polling()
