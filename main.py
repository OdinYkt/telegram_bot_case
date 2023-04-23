from telebot.async_telebot import AsyncTeleBot
from telebot import types
from sql_work import get_list_of_categories, get_columns_with_filter
import asyncio


def get_config():
    config = {}
    with open('config', 'r') as cfg:
        for line in cfg:
            tmp = line.strip().split('=')
            config[tmp[0]] = tmp[1]
    return config

TOKEN = get_config()['TOKEN']
bot = AsyncTeleBot(TOKEN, parse_mode=None)
users = {}
empty_user = {
    'filter': {
        'domen': '',
        'technology': '',
        'func_group': '',
        'metod': ''}

    }

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    users[message.chat.id] = empty_user.copy()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Начать поиск')
    btn2 = types.KeyboardButton('Инструкция')
    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, f'Здравствуйте, {message.chat.first_name}', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Начать поиск')
async def get_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('Домен')
    btn2 = types.KeyboardButton('Функциональная группа')
    btn3 = types.KeyboardButton('Технология')
    markup.add(btn1, btn2, btn3)
    await bot.send_message(message.chat.id, 'Выберите по какому параметру будем фильтровать', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Инструкция')
async def get_message(message):
    #прописать вывод инструкции
    await bot.send_message(message.chat.id, 'Инструкция')


@bot.message_handler(func=lambda message: message.text in ('Домен', 'Функциональная группа', 'Технология'))
async def get_message(message):
    answer = 'Что-то пошло не так.'
    if message.text == 'Домен':
        order = 'domen'
        answer = 'Выберите интересующий вас домен:'
    elif message.text == 'Функциональная группа':
        order = 'func_group'
        answer = 'Выберите интересующую вас функциональную группу:'
    elif message.text == 'Технология':
        order = 'technology'
        answer = 'Выберите интересующую вас технологию:'

    btns = get_list_of_categories(order, users.get(message.chat.id).get('filter'))
    print(btns)
    keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"button_{i}")] for i in range(len(btns))]
    markup = types.InlineKeyboardMarkup(keyboard)
    await bot.send_message(message.chat.id, answer, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
async def handle_callback_query(call):
    await bot.send_message(call.message.chat.id, call.data)



if __name__ == '__main__':
    asyncio.run(bot.polling())
