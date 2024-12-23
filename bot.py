import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
APPS_SCRIPT_URL = os.getenv('APPS_SCRIPT_WEB_APP_URL')

# Crear directorio de logs si no existe
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configurar el logging
log_filename = f'logs/bot_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()  # Mantener los logs en consola también
    ]
)

logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
telebot.logger.setLevel(logging.DEBUG)

# Store user transaction data
user_data = {}

def clear_user_data(chat_id):
    """Clear user data for a specific chat_id"""
    if chat_id in user_data:
        user_data.pop(chat_id)
        logger.debug(f"Cleared user data for chat_id {chat_id}")

def create_category_keyboard(transaction_type):
    markup = InlineKeyboardMarkup(row_width=2)
    categories = {
        'income': ['💰 Salary', '💼 Commissions', '💵 Loans', '🎁 Bonus', '💸 Payments'],
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
                '🏦 Scotiabank', '🏦 Davivienda', '💵 Cash', '💸 Payments']
    buttons = [InlineKeyboardButton(acc, callback_data=f"acc_{acc}") 
               for acc in accounts]
    markup.add(*buttons)
    return markup

def create_savings_goal_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    goals = ['💰 Emergency Fund', '💻 Technology', '📈 Investment', '📚 Study']
    buttons = [InlineKeyboardButton(goal, callback_data=f"goal_{goal}") 
               for goal in goals]
    markup.add(*buttons)
    return markup

def create_currency_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    currencies = ['🇨🇴 COP', '🇺🇸 USD']
    buttons = [InlineKeyboardButton(curr, callback_data=f"curr_{curr}") 
               for curr in currencies]
    markup.add(*buttons)
    return markup

def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("💰 Income", callback_data="menu_income"),
        InlineKeyboardButton("💸 Expense", callback_data="menu_expense"),
        InlineKeyboardButton("🎯 Savings", callback_data="menu_savings"),
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
    elif action == 'savings':
        user_data[chat_id] = {'type': 'savings'}
        bot.edit_message_text(
            "Please select a savings goal:",
            chat_id,
            call.message.message_id,
            reply_markup=create_savings_goal_keyboard()
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('goal_'))
def handle_savings_goal(call):
    chat_id = call.message.chat.id
    goal = call.data.replace('goal_', '')
    
    if chat_id in user_data:
        user_data[chat_id]['goal'] = goal
        bot.edit_message_text(
            f"Goal selected: {goal}\n\n"
            "Now, select the currency:",
            chat_id,
            call.message.message_id,
            reply_markup=create_currency_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('curr_'))
def handle_savings_currency(call):
    chat_id = call.message.chat.id
    currency = call.data.replace('curr_', '')
    
    if chat_id in user_data:
        user_data[chat_id]['currency'] = currency
        bot.edit_message_text(
            f"Currency selected: {currency}\n\n"
            "Now, please enter the amount:\n\n"
            "💡 Use whole numbers only, without decimals or commas\n"
            "✅ Correct: 50000\n"
            "❌ Incorrect: 50,000 or 50.000",
            chat_id,
            call.message.message_id
        )

@bot.message_handler(func=lambda message: (
    message.chat.id in user_data and 
    (('goal' in user_data[message.chat.id] and 'currency' in user_data[message.chat.id]) or 'description' in user_data[message.chat.id]) and 
    'amount' not in user_data[message.chat.id] and 
    not message.from_user.is_bot and
    message.text.replace(',', '').replace('.', '').isdigit()
))
def handle_amount(message):
    chat_id = message.chat.id
    try:
        amount = int(message.text.replace(',', '').replace('.', ''))
        
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        transaction_data = user_data[chat_id].copy()
        transaction_data['amount'] = amount

        # Preparar datos según el tipo de transacción - sin emojis para Apps Script
        if transaction_data['type'] == 'savings':
            data = {
                'function': 'addSaving',
                'goalName': transaction_data['goal'].split(' ', 1)[1] if ' ' in transaction_data['goal'] else transaction_data['goal'],
                'currency': transaction_data['currency'].split(' ', 1)[1] if ' ' in transaction_data['currency'] else transaction_data['currency'],
                'amount': str(amount)
            }
        else:
            data = {
                'function': 'addIncome' if transaction_data['type'] == 'income' else 'addExpense',
                'category': transaction_data['category'].split(' ', 1)[1] if ' ' in transaction_data['category'] else transaction_data['category'],
                'account': transaction_data['account'].split(' ', 1)[1] if ' ' in transaction_data['account'] else transaction_data['account'],
                'description': transaction_data['description'],
                'amount': str(amount)
            }

        logger.info("\n=== SENDING REQUEST ===")
        logger.info(f"URL: {APPS_SCRIPT_URL}")
        logger.info(f"Headers: {{'Content-Type': 'application/json'}}")
        logger.info(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(
            APPS_SCRIPT_URL,
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        logger.info("\n=== RECEIVED RESPONSE ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        logger.info("=== END OF REQUEST ===\n")

        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == 'success':
                    # Mensaje de éxito con emojis y formato de moneda
                    success_message = "✅ Transaction added successfully!\n\n"
                    if transaction_data['type'] == 'savings':
                        success_message += f"🎯 Goal: {transaction_data['goal']}\n"
                        success_message += f"💱 Currency: {transaction_data['currency']}\n"
                        # Formato de moneda según el tipo
                        currency_symbol = "USD $" if "USD" in transaction_data['currency'] else "COP $"
                        success_message += f"💵 Amount: {currency_symbol}{amount:,}"
                    else:
                        success_message += f"📂 Category: {transaction_data['category']}\n"
                        success_message += f"🏦 Account: {transaction_data['account']}\n"
                        success_message += f"📝 Description: {transaction_data['description']}\n"
                        success_message += f"💵 Amount: COP ${amount:,}"
                    
                    bot.reply_to(message, success_message)
                    clear_user_data(chat_id)
                else:
                    error_message = f"❌ Error: {result.get('message', 'Unknown error')}"
                    bot.reply_to(message, error_message)
                    logger.error(f"API Error: {error_message}")
            except json.JSONDecodeError as e:
                error_message = "❌ Error: Invalid response from server"
                bot.reply_to(message, error_message)
                logger.error(f"JSON Decode Error: {str(e)}\nResponse content: {response.text}")
        else:
            error_message = f"❌ Server Error (Status Code: {response.status_code})"
            if response.text:
                error_message += f"\nDetails: {response.text}"
            bot.reply_to(message, error_message)
            logger.error(f"HTTP Error: {error_message}")

    except ValueError as e:
        error_message = (
            "❌ Invalid Amount\n\n"
            "Please enter a valid positive number:\n"
            "✅ Correct: 50000\n"
            "❌ Incorrect: -50000, 0, or non-numeric values"
        )
        bot.reply_to(message, error_message)
        logger.error(f"ValueError for chat_id {chat_id}: {str(e)}")
    except Exception as e:
        error_message = f"❌ Unexpected Error: {str(e)}"
        bot.reply_to(message, error_message)
        logger.error(f"Unexpected error for chat_id {chat_id}: {str(e)}")
        logger.exception("Full traceback:")

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

@bot.message_handler(commands=['recurring'])
def manage_recurring(message):
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("📱 Add Monthly Subscription", callback_data="recurring_add"),
        InlineKeyboardButton("📋 View Recurring Expenses", callback_data="recurring_view"),
        InlineKeyboardButton("✏️ Edit Recurring", callback_data="recurring_edit")
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Manage Recurring Expenses:", reply_markup=markup)

# Al inicio del bot
logger.info("=== BOT STARTED ===")
logger.info(f"Logging to file: {log_filename}")

print("Bot is running...")
bot.infinity_polling()

# Al final del archivo
if __name__ == "__main__":
    logger.info("Starting bot polling...")
    bot.polling(none_stop=True)
