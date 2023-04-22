from telebot.async_telebot import AsyncTeleBot
from telebot import types

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
        'domen': '',
        'tech': '',
        'func_group': ''
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
    answer = ''
    if message.text == 'Домен':
        answer = 'Список доменов'
    elif message.text == 'Функциональная группа':
        answer = 'Список функ'
    else:
        answer = 'Список технологий'
    # markup = types.InlineKeyboardMarkup(row_width=1)
    # btns = [types.InlineKeyboardMarkup(str(i)) for i in range(10)]
    # markup.add(btns)
    btns = ['Button 1', 'Button 2', 'Button 3']
    keyboard = [[types.InlineKeyboardButton(text=button, callback_data=button)] for button in btns]
    markup = types.InlineKeyboardMarkup(keyboard)
    await bot.send_message(message.chat.id, answer, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
async def handle_callback_query(call):
    await bot.send_message(call.message.chat.id, call.data)



if __name__ == '__main__':
    asyncio.run(bot.polling())
