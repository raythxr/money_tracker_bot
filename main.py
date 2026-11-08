import json
import telebot
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
    bot.send_message(message.chat.id, f"Привет {name}! Я твой финансовый трекер.\nМои комманды:\n/add - Записать новую трату \n (Например: 1000 Фастфуд)\n/stats - посмотреть статистику трат \n/total - посмотреть все траты\n/clear - очистить историю трат")

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