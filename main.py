import telebot
from telebot import types

# Створюємо екземпляр бота
bot = telebot.TeleBot("7325922710:AAHniC4_Jle8d3NIx8Ry4ezO0M0UJsBRZ8k")

# Ініціалізуємо глобальні змінні для збереження маси атлета та снаряда
athlete_mass = None
equipment_mass = None
repetitions = None
waiting_for_option = True

# Коефіцієнти для розрахунку Wilks
a = -216.0475144
b = 16.2606339
c = -0.002388645
d = -0.00113732
e = 7.01863E-06
f = -1.291E-08


# Функція для розрахунку коефіцієнта Wilks
def calculate_wilks(x, y):
    k = 500 / (a + b * x + c * pow(x, 2) + d * pow(x, 3) + e * pow(x, 4) + f * pow(x, 5))
    wilks = y * k
    return wilks


# Функція для розрахунку предільного максимуму
def calculate_max_weight(weight, reps):
    max_weight_ranges = {
        tuple(range(1, 2)): 100,
        tuple(range(2, 4)): 95,
        tuple(range(4, 6)): 90,
        tuple(range(6, 8)): 85,
        tuple(range(8, 10)): 80,
        tuple(range(10, 12)): 75,
        tuple(range(12, 18)): 70,
        tuple(range(18, 26)): 65,
        tuple(range(26, 30)): 60,
        tuple(range(30, 38)): 55,
        tuple(range(38, 101)): 50
    }

    for range_tuple, percentage in max_weight_ranges.items():
        if reps in range_tuple:
            max_weight = weight / (percentage / 100)
            return max_weight

    # Якщо кількість повторів не потрапляє в жоден з діапазонів
    return None


# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global waiting_for_option
    waiting_for_option = True
    markup = types.InlineKeyboardMarkup()
    wilks_button = types.InlineKeyboardButton("Коефіцієнт: Wilks", callback_data="wilks")
    max_weight_button = types.InlineKeyboardButton("ПМ", callback_data="max_weight")
    markup.add(wilks_button, max_weight_button)
    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=markup)


# Обробник вибору опції
@bot.callback_query_handler(func=lambda call: waiting_for_option)
def handle_option(call):
    global waiting_for_option
    if call.data == "wilks":
        waiting_for_option = False
        bot.send_message(call.message.chat.id, "Введіть масу атлета:")
        bot.register_next_step_handler(call.message, get_athlete_mass)
    elif call.data == "max_weight":
        waiting_for_option = False
        bot.send_message(call.message.chat.id, "Введіть масу снаряда:")
        bot.register_next_step_handler(call.message, get_equipment_mass)


# Обробник повідомлень з масою атлета для Wilks
def get_athlete_mass(message):
    try:
        global athlete_mass
        athlete_mass = float(message.text)
        bot.send_message(message.chat.id, "Тепер введіть масу снаряда:")
        bot.register_next_step_handler(message, get_equipment_mass)
    except ValueError:
        bot.reply_to(message, "Невірний формат введення. Спробуйте ще раз.")


# Обробник повідомлень з масою снаряда
def get_equipment_mass(message):
    try:
        global equipment_mass, athlete_mass, waiting_for_option
        equipment_mass = float(message.text)
        if athlete_mass is not None:
            wilks = calculate_wilks(athlete_mass, equipment_mass)
            bot.send_message(message.chat.id, f"Коефіцієнт Wilks: {wilks:.2f}")
            athlete_mass = None
            equipment_mass = None
            waiting_for_option = True
            send_welcome(message)
        else:
            bot.send_message(message.chat.id, "Тепер введіть кількість повторів:")
            bot.register_next_step_handler(message, get_repetitions)
    except ValueError:
        bot.reply_to(message, "Невірний формат введення. Спробуйте ще раз.")


# Обробник повідомлень з кількістю повторів для ПМ
def get_repetitions(message):
    try:
        global repetitions, equipment_mass, waiting_for_option
        repetitions = int(message.text)
        max_weight = calculate_max_weight(equipment_mass, repetitions)
        if max_weight is not None:
            bot.send_message(message.chat.id, f"Ваш предільний максимум: {max_weight:.8f} кг")
        else:
            bot.send_message(message.chat.id, "Кількість повторів не потрапляє в жоден з діапазонів.")
        repetitions = None
        equipment_mass = None
        waiting_for_option = True
        send_welcome(message)
    except ValueError:
        bot.reply_to(message, "Невірний формат введення. Спробуйте ще раз.")


# Запускаємо бота
bot.polling()

