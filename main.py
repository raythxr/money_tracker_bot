import json
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, API_URL
from telebot import apihelper
apihelper.API_URL = API_URL

bot = telebot.TeleBot(TOKEN)

def load_data():
    try:
        with open("expenses.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data():
    with open("expenses.json", "w", encoding="utf-8") as file:
        json.dump(user_expenses, file, ensure_ascii=False, indent=4)

user_expenses = load_data()

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    btn_add = KeyboardButton('Добавить трату')
    btn_stats = KeyboardButton('Статистика')
    btn_total = KeyboardButton("Сумма трат")
    btn_clear = KeyboardButton("Очистить все траты")

    markup.add(btn_add, btn_stats)
    markup.add(btn_clear, btn_total)
    return markup

@bot.message_handler(commands=['clear'])
def clear_expenses(message):
    user_id = str(message.from_user.id)
    if user_id not in user_expenses:
        bot.send_message(message.chat.id, "Ты еще не записал ни одной траты")
    else:
        user_expenses[user_id] = []
        save_data()
        bot.send_message(message.chat.id, "История трат очищена")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"Привет, {name}!\nВыберите действие:", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "Сумма трат")
def handle_total_button(message):
    check_total(message)

@bot.message_handler(func=lambda message: message.text == "Статистика")
def handle_stats_button(message):
    check_stats(message)

@bot.message_handler(func=lambda message: message.text == "Очистить все траты")
def handle_clear_button(message):
    clear_expenses(message)

@bot.message_handler(func=lambda message: message.text == "Добавить трату")
def handle_add_button(message):
    bot.reply_to(message,"Напиши команду в формате: /add 500 Фастфуд")

@bot.message_handler(commands=['total'])
def check_total(message):
    user_id = str(message.from_user.id)

    if user_id not in user_expenses:
        bot.send_message(message.chat.id, "Ты еще не записал ни одной траты")
    else:
        total = 0
        for expense in user_expenses[user_id]:
            total += expense["amount"]
        bot.send_message(message.chat.id, f"Всего потрачено: {total} руб.")

@bot.message_handler(commands=['stats'])
def check_stats(message):
    user_id = str(message.from_user.id)

    if user_id not in user_expenses or not user_expenses[user_id]:
        bot.send_message(message.chat.id, 'Ты еще не записал ни одной траты')
    else:
        categories = {}
        for expense in user_expenses[user_id]:
            cat = expense["category"]
            amount = expense["amount"]
            if cat not in categories:
                categories[cat] = amount
            else:
                categories[cat] += amount
        result_text = "Твои траты по категориям:\n"
        for cat, amount in categories.items():
            result_text += f"#{cat}: {amount} руб.\n"
        bot.send_message(message.chat.id, result_text)

@bot.message_handler(commands=['add'])
def add_expense(message):
    user_id = str(message.from_user.id)
    clean_message = message.text.replace("/add ","")
    try:
        parts = clean_message.split()
        amount = int(parts[0])
        category = parts[1].capitalize()

        if user_id not in user_expenses:
            user_expenses[user_id] = []

        user_expenses[user_id].append({"amount": amount, "category": category})
        save_data()
        bot.send_message(message.chat.id, f"Записал {amount} руб. на {category}")
    except(IndexError, ValueError):
        bot.send_message(message.chat.id, "Ошибка! Напишите в формате: /add 500 Еда")


print("Бот запущен")

bot.polling(non_stop=True)