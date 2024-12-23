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

        # Preparar datos según el tipo de transacción
        if transaction_data['type'] == 'savings':
            data = {
                'function': 'addSaving',
                'goalName': transaction_data['goal'].split(' ', 1)[1] if ' ' in transaction_data['goal'] else transaction_data['goal'],
                'currency': transaction_data['currency'].split(' ', 1)[1] if ' ' in transaction_data['currency'] else transaction_data['currency'],
                'amount': amount,
                'dateInput': 'today'
            }
        else:
            data = {
                'function': 'addIncome' if transaction_data['type'] == 'income' else 'addExpense',
                'category': transaction_data['category'].split(' ', 1)[1] if ' ' in transaction_data['category'] else transaction_data['category'],
                'account': transaction_data['account'].split(' ', 1)[1] if ' ' in transaction_data['account'] else transaction_data['account'],
                'description': transaction_data['description'],
                'amount': amount,
                'dateInput': 'today'
            }

        try:
            response = requests.post(APPS_SCRIPT_URL, data=data)
            
            if response.status_code == 200:
                if transaction_data['type'] == 'savings':
                    summary = (f"✅ Saving recorded successfully!\n\n"
                              f"Goal: {transaction_data['goal']}\n"
                              f"Currency: {transaction_data['currency']}\n"
                              f"Amount: {amount:,}")
                else:
                    summary = (f"✅ Transaction recorded successfully!\n\n"
                              f"Type: {transaction_data['type'].title()}\n"
                              f"Category: {transaction_data['category']}\n"
                              f"Account: {transaction_data['account']}\n"
                              f"Description: {transaction_data['description']}\n"
                              f"Amount: ${amount:,}")
                
                del user_data[chat_id]
                bot.reply_to(message, summary)
                show_main_menu(chat_id)
            else:
                error_message = f"❌ Error: Could not save the transaction\n\nStatus Code: {response.status_code}"
                
                if response.text:
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            error_message += f"\nDetails: {error_data['error']}"
                    except:
                        error_message += f"\nDetails: {response.text}"
                
                error_message += "\n\nPlease try again or contact support if the problem persists."
                bot.reply_to(message, error_message)
                
        except requests.exceptions.RequestException as e:
            error_message = (
                "❌ Network Error\n\n"
                f"Could not connect to the server: {str(e)}\n\n"
                "Please check your internet connection and try again."
            )
            bot.reply_to(message, error_message)

    except ValueError as e:
        error_message = (
            "❌ Invalid Amount\n\n"
            "Please enter a valid positive number:\n"
            "✅ Correct: 50000\n"
            "❌ Incorrect: -50000, 0, or non-numeric values"
        )
        bot.reply_to(message, error_message)
    except Exception as e:
        error_message = (
            "❌ Unexpected Error\n\n"
            f"An error occurred: {str(e)}\n\n"
            "Please try again or contact support if the problem persists."
        )
        bot.reply_to(message, error_message)
        logging.error(f"Unexpected error for chat_id {chat_id}: {str(e)}")

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

print("Bot is running...")
bot.infinity_polling()
