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
    'tmp_list': {
        'domen': [],
        'technology': [],
        'func_group': [],
        'metod': []
    },
    'project_menu': {
        'index': 0,
        'names': [],
        'page': 0,
        'pages': 0
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
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True) #, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Домен')
    btn2 = types.KeyboardButton('Функциональная группа')
    btn3 = types.KeyboardButton('Технология')
    btn4 = types.KeyboardButton('Показать выбранные')
    btn5 = types.KeyboardButton('Сбросить')
    # btn6 = types.KeyboardButton('<-')
    # btn7 = types.KeyboardButton('->')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    # markup.add(btn6, btn7)
    await bot.send_message(message.chat.id, 'Выберите по какому параметру будем фильтровать', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Сбросить')
async def get_message(message):
    users[message.chat.id] = copy.deepcopy(empty_user)
    await bot.send_message(message.chat.id, 'Фильтры сброшены. Можете начать заново.')


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

    if users.get(message.chat.id).get('filter')[order]:
        await bot.send_message(message.chat.id, f"Уже выбрано:\n— {users.get(message.chat.id).get('filter')[order]}")
    else:
        btns = get_list_of_categories(order, users.get(message.chat.id).get('filter'))
        users.get(message.chat.id).get('tmp_list')[order] = btns
        keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                    for i in range(len(btns))]
        markup = types.InlineKeyboardMarkup(keyboard)
        # print(users)
        await bot.send_message(message.chat.id, answer, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Показать выбранные')
async def get_projects(message):
    order = 'name'
    answer = 'Список проектов по вашим фильтрам:'
    projects = get_columns_with_filter(where=users.get(message.chat.id).get('filter'))

    project_menu = users.get(message.chat.id).get('project_menu')
    page = project_menu.get('page')

    project_menu['names'] = [projects[i:i+10] for i in range(0, len(projects), 10)]

    pages = len(project_menu['names'])
    project_menu['pages'] = pages

    btns = project_menu.get('names')[page]
    users.get(message.chat.id).get('tmp_list')[order] = btns
    default = [[types.InlineKeyboardButton(text='⬅', callback_data='page_down'),
                types.InlineKeyboardButton(text=f'Страница {page+1} из {pages}', callback_data='None'),
                types.InlineKeyboardButton(text='➡', callback_data='page_up')]]

    keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-name-{i}")]
                for i in range(len(btns))]
    default.extend(keyboard)
    markup = types.InlineKeyboardMarkup(default)
    await bot.send_message(message.chat.id, answer, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split('-')[0] == 'name')
async def handle_callback_query(call):
    order, i = call.data.split('-')[0], int(call.data.split('-')[2])
    project_menu = users.get(call.message.chat.id).get('project_menu')
    page = project_menu.get('page')
    cur_btn = project_menu.get('names')[page][i]
    users.get(call.message.chat.id).get('filter')[order] = cur_btn
    answer = get_columns_with_filter(where=users.get(call.message.chat.id).get('filter'))

    await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    await bot.send_message(call.message.chat.id, f'Выводим инфу по \n❤  {answer[0]}  ❤')


@bot.callback_query_handler(func=lambda call: call.data in ('page_down', 'page_up'))
async def handle_callback_query(call):
    order = 'name'

    projects = get_columns_with_filter(where=users.get(call.message.chat.id).get('filter'))
    project_menu = users.get(call.message.chat.id).get('project_menu')
    page = project_menu.get('page')
    pages = project_menu.get('pages')
    flag = False

    if call.data == 'page_down' and page > 0:
        project_menu['page'] = page - 1
        page = project_menu.get('page')
        flag = True
    elif call.data == 'page_up' and page < pages - 1:
        project_menu['page'] = page + 1
        page = project_menu.get('page')
        flag = True
    if flag:
        btns = project_menu.get('names')[page]
        users.get(call.message.chat.id).get('tmp_list')[order] = btns
        default = [[types.InlineKeyboardButton(text='⬅', callback_data='page_down'),
                    types.InlineKeyboardButton(text=f'Страница {page+1} из {pages}', callback_data='None'),
                    types.InlineKeyboardButton(text='➡', callback_data='page_up')]]

        keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                    for i in range(len(btns))]
        default.extend(keyboard)
        markup = types.InlineKeyboardMarkup(default)
        await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split('-')[1] == 'button')
async def handle_callback_query(call):
    order, i = call.data.split('-')[0], int(call.data.split('-')[2])
    cur_btn = users.get(call.message.chat.id).get('tmp_list').get(order)[i]
    users.get(call.message.chat.id).get('filter')[order] = cur_btn
    number = len(get_columns_with_filter(where=users.get(call.message.chat.id).get('filter')))
    await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    await bot.send_message(call.message.chat.id, f'— {cur_btn}')
    await bot.send_message(call.message.chat.id, f'Выбрано {number} записи')



if __name__ == '__main__':
    asyncio.run(bot.polling())
