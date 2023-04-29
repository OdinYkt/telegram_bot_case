# -*- coding: utf-8 -*-
import copy

from telebot.async_telebot import AsyncTeleBot
from telebot import types
from sql_work import get_list_of_categories, get_columns_with_filter
from fuzzywuzzy import fuzz
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
    },
    'for_info': [],
    'last_mes': '',
    'username': ''
    }

guide0 = """Добро пожаловать в бота поиска проектов."""

guide1 = """Для начала работы, нажмите кнопку <b>Начать поиск</b>. Затем вы можете использовать кнопки <b>Домен</b>, <b>Функциональная группа</b>, <b>Технологии</b> и <b>Методы</b>, чтобы установить фильтры поиска.\nПросто выберите нужную категорию и используйте стрелочки ⬅ ➡ для навигации по спискам.
"""
guide2 = """Вы также можете комбинировать различные фильтры. Используйте кнопки <b>Фильтры</b> и <b>Сбросить</b>, чтобы увидеть текущие фильтры или сбросить их.\nКогда вы закончите установку фильтров, нажмите <b>Показать</b>, чтобы увидеть список проектов."""
guide3 = """Если вы знаете, что ищете, вы можете воспользоваться командой <b>/search <i>[запрос]</i></b> или <i>просто написать ваш запрос в чат</i>. Эту команду также можно комбинировать с фильтрами (первыми выберите фильтры)"""
guide4 = """Выберите интересующий вас проект, чтобы получить информацию о нём.\nНадеемся, что вам понравится навигация по базе данных, с помощью нашего бота.\nЕсли у вас возникли какие-либо предложения, идеи или вы просто хотите поблагодарить автора, смело пишите нам! Ссылка в описании бота."""
guide5 = """Чтобы вызвать инструкцию заново введите <b>/guide</b>"""
guide = (guide0, guide1, guide2, guide3, guide4, guide5)

info_users = []

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    if users.get(message.chat.id) is None:
        info_users.append(str(message.chat.username))

    users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''
    users.get(message.chat.id)['username'] = str(message.chat.username)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Начать поиск')
    btn2 = types.KeyboardButton('Инструкция 📍', )
    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, f'Здравствуйте, {message.chat.first_name}', reply_markup=markup)

@bot.message_handler(commands=['guide'])
async def send_welcome(message):
    for _guide in guide:
        await bot.send_message(message.chat.id, _guide, parse_mode='HTML')

@bot.message_handler(commands=['admin_info'])
async def get_admin_info(message):
    if message.chat.username == 'Odinykt':
        await bot.send_message(message.chat.id, str(len(users)), parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, 'Нет доступа.', parse_mode='HTML')


@bot.message_handler(commands=['admin_save'])
async def save_users(message):
    if message.chat.username == 'Odinykt':
        await bot.send_message(message.chat.id, ', '.join(info_users), parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, 'Нет доступа.', parse_mode='HTML')


@bot.message_handler(commands=['search'])
async def search_command(message):
    if users.get(message.chat.id) is None:
        users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''

    percent = 50
    order = 'name'
    cur_user = users.get(message.chat.id)
    text = message.text[7:]
    filters = cur_user.get('filter')
    if len(text) > 3:
        names = get_columns_with_filter(where=filters, for_search=True)
        print(len(names[0]))
        str_for_search = [column[1]+' '+column[2]+' '+column[3]+' '+column[4]+' '+column[5]+' '+column[6]+' '+column[7]
                          + ' '+column[10]+' '+column[12]+' '+column[14]+' '+column[15]+' '+column[16]+' '+column[17]
                          + ' '+column[18]+' '+column[19] for column in names]
        result = []
        for i in range(len(str_for_search)):
            rating = fuzz.WRatio(str_for_search[i].lower(), text.lower())
            if rating > percent:
                result.append([names[i][1], rating])
        sorted_result = sorted(result, key=lambda x: x[1], reverse=True)
        if sorted_result:
            sorted_result = [x[0] for x in sorted_result]
            cur_user.get('sql_answer')[order] = [sorted_result[i:i + 10] for i in range(0, len(sorted_result), 10)]
            page, pages = 0, len(cur_user.get('sql_answer')[order])
            cur_user.get('for_button')[order] = [page, pages]

            default = [[types.InlineKeyboardButton(text='⬅', callback_data=f'{order}-page_down'),
                        types.InlineKeyboardButton(text=f'Стр. {page + 1}/{pages}', callback_data='none-none-none'),
                        types.InlineKeyboardButton(text='➡', callback_data=f'{order}-page_up')]]
            btns = cur_user.get('sql_answer')[order][page]

            keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                        for i in range(len(btns))]
            default.extend(keyboard)
            back = [types.InlineKeyboardButton(text='❌   Отменить выбор   ❌', callback_data=f'back')]
            default.append(back)
            markup = types.InlineKeyboardMarkup(default)
            await bot.send_message(message.chat.id, 'Результаты поиска по вашему запросу:', reply_markup=markup,
                                   parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, 'К сожалению, ничего не удалось найти. Попробуйте изменить ваш запрос',
                                   parse_mode='HTML')
    elif text == '':
        await bot.send_message(message.chat.id, 'Пожалуйста используйте <b>/search <i>[ваш запрос]</i></b>\n'
                                                'Например, <b>/search <i>чат-бот</i></b>',
                                                parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, 'Запрос должен быть длинее <b>3 символов</b>', parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == 'Начать поиск')
async def get_message(message):
    if users.get(message.chat.id) is None:
        users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    row1 = ('Домен', 'Технология', 'Метод исп.',  'Функц. группа')
    row2 = ('Фильтры ⚙️', 'Сбросить 🔙')
    row3 = ('Показать 🔎',)
    btns_row1 = [types.KeyboardButton(btn) for btn in row1]
    btns_row2 = [types.KeyboardButton(btn) for btn in row2]
    btns_row3 = [types.KeyboardButton(btn) for btn in row3]
    markup.row(*btns_row1)
    markup.row(*btns_row2)
    markup.row(*btns_row3)
    await bot.send_message(message.chat.id, 'Выберите по какому параметру будем фильтровать', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text[:8] == 'Сбросить')
async def get_drop_filters(message):
    users[message.chat.id] = copy.deepcopy(empty_user)
    await bot.send_message(message.chat.id, 'Фильтры сброшены. Можете начать заново.')

@bot.message_handler(func=lambda message: message.text == 'Первое правило?')
async def get_drop_filters(message):
    await bot.send_message(message.chat.id, 'Никому не рассказывать о бойцовском клубе.')

@bot.message_handler(func=lambda message: message.text == 'О мой бот!')
async def get_drop_filters(message):
    await bot.send_message(message.chat.id, 'О мой бот! - лучшая команда!❤')


@bot.message_handler(func=lambda message: message.text[:7] == 'Фильтры')
async def show_filters(message):
    if users.get(message.chat.id) is None:
        users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''
    filters = users.get(message.chat.id).get('filter')
    empty = 'Текущие фильтры пусты'
    flag = False
    categories = ('domen', 'technology', 'func_group', 'metod')
    categories_rus = ('Домен', 'Функц. группа', 'Технология', 'Метод исп.',)
    answer = ['__Ваши текущие фильтры:__\n']

    for i in range(len(categories)):
        if filters.get(categories[i]):
            answer.append(f'{categories_rus[i]}: {filters.get(categories[i])}\n')
            flag = True
    if flag:
        empty = ''.join(answer)

    await bot.send_message(message.chat.id, f'{empty}')


@bot.message_handler(func=lambda message: message.text[:10] == 'Инструкция')
async def show_guide(message):
    if users.get(message.chat.id) is None:
        users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''
    for _guide in guide:
        await bot.send_message(message.chat.id, _guide, parse_mode='HTML')



@bot.message_handler(func=lambda _message: _message.text.split()[0] in ('Домен', 'Функц.', 'Технология',
                                                           'Метод', 'Показать'))
async def filter_buttons(message):
    if users.get(message.chat.id) is None:
        users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''
    answer = 'Что-то пошло не так.'
    order = 'name'
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
    elif message.text == 'Показать 🔎':
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
                    types.InlineKeyboardButton(text=f'Стр. {page + 1}/{pages}', callback_data='none-none-none'),
                    types.InlineKeyboardButton(text='➡', callback_data=f'{order}-page_up')]]
        btns = cur_user.get('sql_answer')[order][page]

        keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                    for i in range(len(btns))]
        default.extend(keyboard)
        back = [types.InlineKeyboardButton(text='❌   Отменить выбор   ❌', callback_data=f'back')]
        default.append(back)
        markup = types.InlineKeyboardMarkup(default)
        await bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda message:True)
async def search_text(message):
    if users.get(message.chat.id) is None:
        users[message.chat.id] = copy.deepcopy(empty_user)
    users.get(message.chat.id)['last_mes'] = ''
    percent = 50
    order = 'name'
    cur_user = users.get(message.chat.id)
    text = message.text
    filters = cur_user.get('filter')
    if len(text) > 3:
        names = get_columns_with_filter(where=filters, for_search=True)
        str_for_search = [column[1]+' '+column[2]+' '+column[3]+' '+column[4]+' '+column[5]+' '+column[6]+' '+column[7]
                          + ' '+column[10]+' '+column[12]+' '+column[14]+' '+column[15]+' '+column[16]+' '+column[17]
                          + ' '+column[18]+' '+column[19] for column in names]
        result = []
        for i in range(len(str_for_search)):
            rating = fuzz.WRatio(str_for_search[i].lower(), text.lower())
            if rating > percent:
                result.append([names[i][1], rating])
        sorted_result = sorted(result, key=lambda x: x[1], reverse=True)
        if sorted_result:
            sorted_result = [x[0] for x in sorted_result]
            cur_user.get('sql_answer')[order] = [sorted_result[i:i + 10] for i in range(0, len(sorted_result), 10)]
            page, pages = 0, len(cur_user.get('sql_answer')[order])
            cur_user.get('for_button')[order] = [page, pages]

            default = [[types.InlineKeyboardButton(text='⬅', callback_data=f'{order}-page_down'),
                        types.InlineKeyboardButton(text=f'Стр. {page + 1}/{pages}', callback_data='none-none-none'),
                        types.InlineKeyboardButton(text='➡', callback_data=f'{order}-page_up')]]
            btns = cur_user.get('sql_answer')[order][page]

            keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                        for i in range(len(btns))]
            default.extend(keyboard)
            back = [types.InlineKeyboardButton(text='❌   Отменить выбор   ❌', callback_data=f'back')]
            default.append(back)
            markup = types.InlineKeyboardMarkup(default)
            await bot.send_message(message.chat.id, 'Результаты поиска по вашему запросу:', reply_markup=markup,
                                   parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, 'К сожалению, ничего не удалось найти. Попробуйте изменить ваш запрос',
                                   parse_mode='HTML')
    elif text == '':
        await bot.send_message(message.chat.id, 'Пожалуйста используйте <b>/search <i>[ваш запрос]</i></b>\n'
                                                'Например, <b>/search <i>чат-бот</i></b>',
                                                parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, 'Запрос должен быть длинее <b>3 символов</b>', parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'back')
async def back_button(call):
    users.get(call.message.chat.id)['last_mes'] = ''
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        message_id=call.message.message_id, reply_markup=None)
    await bot.send_message(call.message.chat.id, text='Выбор отменён')


@bot.callback_query_handler(func=lambda call: call.data == 'info')
async def dop_info(call):
    info = users.get(call.message.chat.id).get('for_info')
    info = list(info)
    for i in range(len(info)):
        temp = info[i].strip().split('\n')
        temp = list(filter(bool, temp))
        new_temp = [f'{i+1}. {x}' for i, x in enumerate(temp)]
        info[i] = '\n'.join(new_temp)

    answer = f'<b>Наименование | Бенчмаркинг (внешний рынок)</b>:\n{info[0]}\n\n' \
             f'<b>Описание | Бенчмаркинг (внешний рынок)</b>:\n{info[1]}\n\n' \
             f'<b>Компания | Бенчмаркинг (внешний рынок)</b>:\n{info[2]}\n\n' \
             f'______________________________________\n' \
             f'<b>Название проекта в ГПН | НИОКР</b>:\n{info[3]}\n\n' \
             f'<b>Описание проекта в ГПН | НИОКР</b>:\n{info[4]}\n\n' \
             f'______________________________________\n' \
             f'<b>Название проекта | Проекты ЦТ</b>:\n{info[5]}'
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        message_id=call.message.message_id, reply_markup=None)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=call.message.text+'\n'*2+answer, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.split('-')[0] == 'name'
                                              and call.data.split('-')[1] == 'button')
async def show_projects(call):
    flag = False
    order, i = call.data.split('-')[0], int(call.data.split('-')[2])
    cur_user = users.get(call.message.chat.id)
    sql_answer = cur_user.get('sql_answer')
    for_button = cur_user.get('for_button')
    filters = cur_user.get('filter')
    page = for_button[order][0]
    cur_btn = sql_answer.get(order)[page][i]
    filters[order] = cur_btn
    answer = get_columns_with_filter(where=filters, columns=['name', 'description'])[0]
    dop_info = get_columns_with_filter(where=filters, columns=['Benchmarking',
                                                               'Benchmarking_description',
                                                               'Benchmarking_company', 'name_project_gpn',
                                                               'description_project',
                                                               'name_project'])[0]
    # users[call.message.chat.id] = copy.deepcopy(empty_user)
    if users.get(call.message.chat.id).get('last_mes'):
        flag = True
        users.get(call.message.chat.id)['for_info'] = dop_info
    else:
        users.get(call.message.chat.id)['for_info'] = dop_info

    show_info = [[types.InlineKeyboardButton(text='Доп. инфо', callback_data='info')]]
    markup = types.InlineKeyboardMarkup(show_info)
    filters[order] = ''
    if flag:
        users.get(call.message.chat.id)['last_mes'] = await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                                  message_id=users.get(call.message.chat.id).get('last_mes').id,
                                    text=f'Название:\n'
                           f'   <b>{answer[0]}</b>\n'
                           f'\n'
                           f'Описание:\n'
                           f'   {answer[1]}\n'
                           f'Место для дашборда:\n'
                           f'   [dashboard.png]', reply_markup=markup, parse_mode='HTML')
    # await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    else:
        users.get(call.message.chat.id)['last_mes'] = await bot.send_message(call.message.chat.id,
                           f'Название:\n'
                           f'   <b>{answer[0]}</b>\n'
                           f'\n'
                           f'Описание:\n'
                           f'   {answer[1]}\n'
                           f'Место для дашборда:\n'
                           f'   [dashboard.png]',
                           reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.split('-')[1] in ('page_down', 'page_up'))
async def navigation_buttons(call):
    order, cur_call = call.data.split('-')[0], call.data.split('-')[1]

    cur_user = users.get(call.message.chat.id)
    sql_answer = cur_user.get('sql_answer')
    for_button = cur_user.get('for_button')
    page, pages = for_button[order]

    flag = False

    if cur_call == 'page_down' and page > 0:
        page += -1
        flag = True
    elif cur_call == 'page_up' and page < pages-1:
        page += 1
        flag = True

    if flag:
        for_button[order] = [page, pages]
        btns = sql_answer.get(order)[page]

        default = [[types.InlineKeyboardButton(text='⬅', callback_data=f'{order}-page_down'),
                    types.InlineKeyboardButton(text=f'Стр. {page+1}/{pages}', callback_data='none-none-none'),
                    types.InlineKeyboardButton(text='➡', callback_data=f'{order}-page_up')]]

        keyboard = [[types.InlineKeyboardButton(text=btns[i], callback_data=f"{order}-button-{i}")]
                    for i in range(len(btns))]
        default.extend(keyboard)
        back = [types.InlineKeyboardButton(text='❌   Отменить выбор   ❌', callback_data=f'back')]
        default.append(back)
        markup = types.InlineKeyboardMarkup(default)
        await bot.edit_message_reply_markup(call.message.chat.id,
                                            message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split('-')[1] == 'button')
async def show_categories(call):
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
    await bot.set_chat_menu_button(call.message.chat.id, )
    await bot.send_message(call.message.chat.id, f'— {btns[i]}')
    await bot.send_message(call.message.chat.id, f'Выбрано {number} записи')



if __name__ == '__main__':
    while True:
        try:
            asyncio.run(bot.polling())
        except:
            continue
