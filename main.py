import copy

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
        'metod': '',
        'name': ''
    },
    'sql_answer': {
        'domen': [],
        'technology': [],
        'func_group': [],
        'metod': [],
        'name': []
    },
    'for_button': {
        'domen': [],
        'technology': [],
        'func_group': [],
        'metod': [],
        'name': []
    }
    }

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    users[message.chat.id] = copy.deepcopy(empty_user)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Начать поиск')
    btn2 = types.KeyboardButton('Инструкция')
    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, f'Здравствуйте, {message.chat.first_name}', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Начать поиск')
async def get_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    row1 = ('Домен', 'Функц. группа', 'Технология', 'Метод исп.')
    row2 = ('Показать', 'Сбросить')
    btns_row1 = [types.KeyboardButton(btn) for btn in row1]
    btns_row2 = [types.KeyboardButton(btn) for btn in row2]
    markup.row(*btns_row1)
    markup.row(*btns_row2)
    await bot.send_message(message.chat.id, 'Выберите по какому параметру будем фильтровать', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Сбросить')
async def get_message(message):
    users[message.chat.id] = copy.deepcopy(empty_user)
    await bot.send_message(message.chat.id, 'Фильтры сброшены. Можете начать заново.')


@bot.message_handler(func=lambda message: message.text == 'Инструкция')
async def get_message(message):
    #прописать вывод инструкции
    await bot.send_message(message.chat.id, 'Инструкция')


@bot.message_handler(func=lambda message: message.text in ('Домен', 'Функц. группа', 'Технология',
                                                           'Метод исп.', 'Показать'))
async def get_message(message):
    answer = 'Что-то пошло не так.'
    if message.text == 'Домен':
        order = 'domen'
        answer = 'Выберите интересующий вас <b>домен</b>:'
    elif message.text == 'Функц. группа':
        order = 'func_group'
        answer = 'Выберите интересующую вас <b>функциональную группу</b>:'
    elif message.text == 'Технология':
        order = 'technology'
        answer = 'Выберите интересующую вас <b>технологию</b>:'
    elif message.text == 'Метод исп.':
        order = 'metod'
        answer = 'Выберите интересующий вас <b>метод использования</b>:'
    elif message.text == 'Показать':
        order = 'name'
        answer = '<b>Список проектов</b> по вашим фильтрам:'

    cur_user = users.get(message.chat.id)

    if cur_user.get('filter')[order]:
        await bot.send_message(message.chat.id, f"Уже выбрано:\n— {cur_user.get('filter')[order]}")

    else:
        sql_answer = get_list_of_categories(order, cur_user.get('filter'))
        cur_user.get('sql_answer')[order] = [sql_answer[i:i+10] for i in range(0, len(sql_answer), 10)]
        page, pages = 0, len(cur_user.get('sql_answer')[order])
        cur_user.get('for_button')[order] = [page, pages]

        default = [[types.InlineKeyboardButton(text='⬅', callback_data=f'{order}-page_down'),
                    types.InlineKeyboardButton(text=f'Стр. {page + 1}/{pages}', callback_data='None'),
                    types.InlineKeyboardButton(text='➡', callback_data=f'{order}-page_up')]]
        btns = cur_user.get('sql_answer')[order][page]

        keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                    for i in range(len(btns))]
        default.extend(keyboard)
        markup = types.InlineKeyboardMarkup(default)
        await bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.split('-')[0] == 'name')
async def handle_callback_query(call):
    order, i = call.data.split('-')[0], int(call.data.split('-')[2])
    cur_user = users.get(call.message.chat.id)
    sql_answer = cur_user.get('sql_answer')
    for_button = cur_user.get('for_button')
    filters = cur_user.get('filter')
    page = for_button[order][0]
    cur_btn = sql_answer.get(order)[page][i]
    filters[order] = cur_btn
    answer = get_columns_with_filter(where=filters, columns=['name', 'description'])[0]

    await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    await bot.send_message(call.message.chat.id, f'{answer[0]}\n\n{answer[1]}')


@bot.callback_query_handler(func=lambda call: call.data.split('-')[1] in ('page_down', 'page_up'))
async def handle_callback_query(call):
    order, cur_call = call.data.split('-')[0], call.data.split('-')[1]

    cur_user = users.get(call.message.chat.id)
    sql_answer = cur_user.get('sql_answer')
    for_button = cur_user.get('for_button')
    page, pages = for_button[order]

    flag = False

    if cur_call == 'page_down' and page > 0:
        page += -1
        flag = True
    elif cur_call == 'page_up' and page < pages - 1:
        page += 1
        flag = True

    if flag:
        for_button[order] = [page, pages]
        btns = sql_answer.get(order)[page]

        default = [[types.InlineKeyboardButton(text='⬅', callback_data=f'{order}-page_down'),
                    types.InlineKeyboardButton(text=f'Стр. {page+1}/{pages}', callback_data='None'),
                    types.InlineKeyboardButton(text='➡', callback_data=f'{order}-page_up')]]

        keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                    for i in range(len(btns))]
        default.extend(keyboard)
        markup = types.InlineKeyboardMarkup(default)
        await bot.edit_message_reply_markup(call.message.chat.id,
                                            message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split('-')[1] == 'button')
async def handle_callback_query(call):
    order, i = call.data.split('-')[0], int(call.data.split('-')[2])
    cur_user = users.get(call.message.chat.id)
    sql_answer = cur_user.get('sql_answer')
    for_button = cur_user.get('for_button')
    filters = cur_user.get('filter')
    page = for_button[order][0]

    btns = sql_answer[order][page]
    filters[order] = btns[i]
    number = len(get_columns_with_filter(where=filters))
    await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    await bot.send_message(call.message.chat.id, f'— {btns[i]}')
    await bot.send_message(call.message.chat.id, f'Выбрано {number} записи')



if __name__ == '__main__':
    asyncio.run(bot.polling())
