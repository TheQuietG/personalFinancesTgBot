import logging
import json
import telebot
import os
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load sensitive data from environment variables for security
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUR_APPS_SCRIPT_WEB_APP_URL = os.getenv("APPS_SCRIPT_WEB_APP_URL")

# Initialize the bot with the token
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

# Define messages to guide users on income and expense commands
income_msg = "💰 For Income, provide the details as follows:\n\n" + \
             "📊 Category:\n" + \
             "• Salary\n" + \
             "• Commissions\n" + \
             "• Loans\n" + \
             "• Bonus\n\n" + \
             "💳 Account:\n" + \
             "• 🏦 Bancolombia\n" + \
             "• 📱 Nequi\n" + \
             "• 📱 Daviplata\n" + \
             "• 💱 Binance\n" + \
             "• 🏦 Scotiabank\n" + \
             "• 🏦 Davivienda\n" + \
             "• 💵 Cash\n\n" + \
             "📝 Description\n" + \
             "💲 Amount"
expenses_msg = "💸 For Expenses, provide the details as follows:\n\n" + \
               "📊 Category:\n" + \
               "• 🍪 Cravings\n" + \
               "• 💳 Debt Paid Off\n" + \
               "• 🎁 Gifts\n" + \
               "• 🎭 Going Out\n" + \
               "• 🛒 Groceries\n" + \
               "• 📈 Growth\n" + \
               "• ⚕️ Health\n" + \
               "• 🏠 House Expenses\n" + \
               "• 🤷 Incidential Expenses\n" + \
               "• 💰 Loans\n" + \
               "• 🧴 Personal Care\n" + \
               "• 🍽️ Restaurants\n" + \
               "• 🛍️ Shopping\n" + \
               "• 📱 Subscriptions\n" + \
               "• 💱 Transfer\n" + \
               "• 🚗 Transportation\n" + \
               "• 🔧 Utilities\n\n" + \
               "💳 Account:\n" + \
               "• 🏦 Bancolombia\n" + \
               "• 📱 Nequi\n" + \
               "• 📱 Daviplata\n" + \
               "• 💱 Binance\n" + \
               "• 🏦 Scotiabank\n" + \
               "• 🏦 Davivienda\n" + \
               "• 💵 Cash\n\n" + \
               "📝 Description\n" + \
               "💲 Amount\n" + \
               "📅 Date (optional, type 'today' for today's date)"

def create_category_keyboard(transaction_type):
    """Creates category keyboard based on transaction type"""
    markup = InlineKeyboardMarkup(row_width=2)
    categories = {
        'income': ['Salary', 'Commissions', 'Loans', 'Bonus'],
        'expenses': ['🍪 Cravings', '💳 Debt Paid Off', '🎁 Gifts', '🎭 Going Out', 
                    '🛒 Groceries', '📈 Growth', '⚕️ Health', '🏠 House Expenses']
    }
    buttons = [InlineKeyboardButton(cat, callback_data=f"cat_{cat}") 
               for cat in categories[transaction_type]]
    markup.add(*buttons)
    return markup

def create_account_keyboard():
    """Creates account selection keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    accounts = ['🏦 Bancolombia', '📱 Nequi', '📱 Daviplata', '💱 Binance', 
                '🏦 Scotiabank', '🏦 Davivienda', '💵 Cash']
    buttons = [InlineKeyboardButton(acc, callback_data=f"acc_{acc}") 
               for acc in accounts]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
    Handles the /start and /help commands to provide initial guidance to users.
    """
    bot.reply_to(message, "To start adding records to your Spreadsheet, please select /income or /expenses")

@bot.message_handler(commands=['income'])
def handle_income(message):
    """
    Handles the /income command by explaining the required format and preparing for user input.
    """
    bot.reply_to(message, income_msg)
    markup = telebot.types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Please provide your income details in the specified format (comma-separated):\nCategory, Account, Description, Amount",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_income_details)

def process_income_details(message):
    """
    Processes the income details provided by the user and sends them to the Apps Script web app.
    """
    try:
        details = message.text.split(',')
        if len(details) != 4:
            raise ValueError("Incorrect number of values provided.")
        category = details[0].strip()
        account = details[1].strip()
        description = details[2].strip()
        amount = float(details[3].strip())

        # Prepare data to send to the Apps Script web app
        data = {
            'function': 'addIncome',
            'category': category,
            'account': account,
            'description': description,
            'amount': amount
        }

        response = requests.post(YOUR_APPS_SCRIPT_WEB_APP_URL, data=data)

        if response.status_code == 200:
            bot.reply_to(message, "Income record added successfully!")
        else:
            bot.reply_to(message, f"Error adding income record. Status code: {response.status_code}")

    except (IndexError, ValueError) as e:
        bot.reply_to(message, f"Invalid input format. Please provide the details as follows: Category, Account, Description, Amount\nError: {e}")

@bot.message_handler(commands=['expenses'])
def handle_expenses(message):
    """
    Handles the /expenses command by explaining the required format and preparing for user input.
    """
    bot.reply_to(message, expenses_msg)
    markup = telebot.types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Please provide your expense details in the specified format (comma-separated):\nCategory, Account, Description, Amount, Date (optional)",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_expense_details)

def process_expense_details(message):
    """
    Processes the expense details provided by the user and sends them to the Apps Script web app.
    """
    try:
        details = message.text.split(',')
        if len(details) < 4 or len(details) > 5:
            raise ValueError("Incorrect number of values provided.")
        category = details[0].strip()
        account = details[1].strip()
        description = details[2].strip()
        amount = float(details[3].strip())
        dateInput = details[4].strip() if len(details) == 5 else ''

        # Prepare data to send to the Apps Script web app
        data = {
            'function': 'addExpense',
            'category': category,
            'account': account,
            'description': description,
            'amount': amount,
            'dateInput': dateInput
        }

        response = requests.post(YOUR_APPS_SCRIPT_WEB_APP_URL, data=data)

        if response.status_code == 200:
            bot.reply_to(message, "Expense record added successfully!")
        else:
            bot.reply_to(message, f"Error adding expense record. Status code: {response.status_code}")

    except (IndexError, ValueError) as e:
        bot.reply_to(message, f"Invalid input format. Please provide the details as follows: Category, Account, Description, Amount, Date (optional)\nError: {e}")

# Start polling for incoming messages
bot.infinity_polling()
