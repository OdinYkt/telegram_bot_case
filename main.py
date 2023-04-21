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

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    users[message.chat.id] = []
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Начать поиск')
    btn2 = types.KeyboardButton('Очистить')
    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, f'Здравствуйте, {message.chat.first_name}', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Начать поиск')
async def get_message(message):
    users.get(message.chat.id).append(message.chat.first_name)
    await bot.send_message(message.chat.id, users[message.chat.id])


@bot.message_handler(func=lambda message: message.text == 'Инструкция')
async def get_message(message):
    users[message.chat.id] = []
    await bot.send_message(message.chat.id, 'Очищено.')

if __name__ == '__main__':
    asyncio.run(bot.polling())
