# Telegram Bot: Income & Expense Manager

This repository contains a Telegram bot that allows users to record both **income** and **expenses** directly from their chat. The bot integrates with a Google Apps Script web app, sending transaction data to a spreadsheet in real time. This README provides an overview of the project logic, how to set it up, and how to use it.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Project Structure](#project-structure)  
4. [Installation & Configuration](#installation--configuration)  
5. [How It Works](#how-it-works)  
6. [Usage](#usage)  
7. [Spaces for Images](#spaces-for-images)  
8. [License](#license)

---

## Overview

This bot is designed to streamline the process of logging financial transactions by guiding the user step by step. Users can:

- Add **income** transactions with category, account, description, and amount.  
- Add **expense** transactions with category, account, description, amount, and optional date.  
- Interact using inline keyboards (for categories and accounts) or direct text input.

Once data is received, it’s sent to an Apps Script web endpoint (`YOUR_APPS_SCRIPT_WEB_APP_URL`) that appends the record to a Google Sheet.

---

## Features

- **Inline Keyboards**: The bot displays various categories (income or expense) and account types as clickable buttons.
- **Step-by-Step Flow**: After choosing the transaction type, the user is guided through category selection, account selection, description entry, and amount input.
- **Optional Date for Expenses**: Users can specify a date or type “today” to automatically use the current date.
- **Error Handling**: If a user provides invalid input (like non-numeric amounts), the bot sends an error message, preventing incomplete or incorrect records.
- **Flexible Integration**: Sensitive data (bot token and web app URL) is handled via environment variables for security.

---

## Project Structure
. ├── bot.py # Main script containing the Telegram bot logic ├── requirements.txt # Python dependencies (if any) ├── README.md # Project documentation (this file) └── .env # Environment variables (not committed to repo)

- **bot.py**: Core file with all bot commands, handlers, and logic.
- **requirements.txt** (optional): List of libraries (e.g., `pyTelegramBotAPI`, `requests`).
- **.env**: File to store `TELEGRAM_BOT_TOKEN` and `APPS_SCRIPT_WEB_APP_URL`.

---

## Installation & Configuration

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YourUser/YourRepo.git
   cd YourRepo

```

### Income Categories 💰
- Salary
- Commissions
- Loans
- Bonus
- Payments
