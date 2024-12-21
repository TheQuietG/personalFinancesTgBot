import logging
import telebot
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

# Define help messages
INCOME_MSG = """💰 Income Categories:
• Salary
• Commissions
• Loans
• Bonus

💳 Available Accounts:
• 🏦 Bancolombia
• 📱 Nequi
• 📱 Daviplata
• 💱 Binance
• 🏦 Scotiabank
• 🏦 Davivienda
• 💵 Cash"""

EXPENSES_MSG = """💸 Expense Categories:
• 🍪 Cravings
• 💳 Debt Paid Off
• 🎁 Gifts
• 🎭 Going Out
• 🛒 Groceries
• 📈 Growth
• ⚕️ Health
• 🏠 House Expenses
• 🤷 Incidential Expenses
• 💰 Loans
• 🧴 Personal Care
• 🍽️ Restaurants
• 🛍️ Shopping
• 📱 Subscriptions
• 💱 Transfer
• 🚗 Transportation
• 🔧 Utilities"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = """Welcome! 📊
Use /income or /expense to record a transaction.

Format: Category, Account, Description, Amount
Example: Salary, Bancolombia, January salary, 1000000"""
    bot.reply_to(message, welcome_msg)

@bot.message_handler(commands=['income'])
def handle_income(message):
    bot.reply_to(message, INCOME_MSG)
    markup = telebot.types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Please provide your income details (comma-separated):\nCategory, Account, Description, Amount",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_income)

@bot.message_handler(commands=['expense'])
def handle_expense(message):
    bot.reply_to(message, EXPENSES_MSG)
    markup = telebot.types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Please provide your expense details (comma-separated):\nCategory, Account, Description, Amount",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_expense)

def process_income(message):
    try:
        # Parse the income details
        details = message.text.split(',')
        if len(details) != 4:
            raise ValueError("Incorrect number of values. Please provide: Category, Account, Description, Amount")
        
        category = details[0].strip()
        account = details[1].strip()
        description = details[2].strip()
        amount = int(float(details[3].strip().replace(',', '').replace('.', '')))

        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # Send to Google Sheets
        data = {
            'function': 'addIncome',
            'category': category,
            'account': account,
            'description': description,
            'amount': amount
        }

        response = requests.post(APPS_SCRIPT_URL, data=data)

        if response.status_code == 200:
            summary = (f"✅ Income recorded successfully!\n\n"
                      f"Category: {category}\n"
                      f"Account: {account}\n"
                      f"Description: {description}\n"
                      f"Amount: ${amount}")
            bot.reply_to(message, summary)
        else:
            bot.reply_to(message, f"❌ Error adding income. Status code: {response.status_code}")

    except ValueError as e:
        bot.reply_to(message, f"❌ Error: {str(e)}\nPlease try again with /income")

def process_expense(message):
    try:
        # Parse the expense details
        details = message.text.split(',')
        if len(details) != 4:
            raise ValueError("Incorrect number of values. Please provide: Category, Account, Description, Amount")
        
        category = details[0].strip()
        account = details[1].strip()
        description = details[2].strip()
        amount = int(float(details[3].strip().replace(',', '').replace('.', '')))

        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # Send to Google Sheets
        data = {
            'function': 'addExpense',
            'category': category,
            'account': account,
            'description': description,
            'amount': amount,
            'dateInput': 'today'
        }

        response = requests.post(APPS_SCRIPT_URL, data=data)

        if response.status_code == 200:
            summary = (f"✅ Expense recorded successfully!\n\n"
                      f"Category: {category}\n"
                      f"Account: {account}\n"
                      f"Description: {description}\n"
                      f"Amount: ${amount}")
            bot.reply_to(message, summary)
        else:
            bot.reply_to(message, f"❌ Error adding expense. Status code: {response.status_code}")

    except ValueError as e:
        bot.reply_to(message, f"❌ Error: {str(e)}\nPlease try again with /expense")

print("Bot is running...")
bot.infinity_polling()
