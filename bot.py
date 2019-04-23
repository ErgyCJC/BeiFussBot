import config # bot config
import settings # user settings

import requests
import configparser
import telebot
from telebot.types import (Message,
                            InlineKeyboardButton,
                            InlineKeyboardMarkup,
                            KeyboardButton,
                            ReplyKeyboardMarkup)


tokens = config.load_config()
bot = telebot.TeleBot(tokens['telegram-token'])
state_info = {'getting_places' : False, 'walk_minutes' : None, 'obj_count' : None}


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    lines = ['Привет! Это бот для поиска интересных мест в шаговой доступности',
                '/tune - настройка интересов',
                '/go [count] - найти места в [count] минутах ходьбы']

    welcome_line = '\n'.join(lines)
    bot.send_message(message.chat.id, welcome_line)


@bot.message_handler(commands=['help'])
def help(message: Message):
    commands = ['/tune - настройка интересов',
                '/go [minutes] <places> - найти <places> мест в [minutes] минутах ходьбы (кол-во мест не обязательно)']

    commands_line = '\n'.join(commands)
    bot.send_message(message.chat.id, commands_line)


@bot.message_handler(commands=['tune'])
def tune(message: Message):
    keyboard = InlineKeyboardMarkup()

    user_settings = settings.load_settings()
    categories = user_settings.keys()
    for place in categories:
        button_text = place[:1].upper() + place[1:]
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=place))

    bot.send_message(message.chat.id, 'Выберите интересные для вас места:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if type(call.data) == type(str()):
        section = 'SETTINGS'
        file = 'settings.config'
        user_settings = settings.load_settings(file, section)
        
        update_value = 'False'
        if user_settings[call.data] == 'False':
            update_value = 'True'
        user_settings[call.data] = update_value

        storing_config = configparser.ConfigParser()
        storing_config[section] = user_settings
        with open(file, 'w+') as storing_file:
            storing_config.write(storing_file)

        insertion = ''
        if user_settings[call.data] == 'False':
            insertion = 'не '
        msg = call.data[:1].upper() + call.data[1:] + ' теперь {}отслеживаются.'.format(insertion)
        bot.send_message(call.message.chat.id, msg)


@bot.message_handler(commands=['go'])
def go(message: Message):
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, 'Нужно ввести хотя бы кол-во минут для этой комманды')
        return

    minutes_count = int(message.text.split()[1])
    state_info['walk_minutes'] = minutes_count

    places_count = 15
    if len(message.text.split()) > 2:
        places_count = message.text.split()[2]
    state_info['']

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton(text='Конечно! Отправляю свою геолокацию.', request_location=True))
    keyboard.add(KeyboardButton(text='Нет.'))
    last_msg = bot.send_message(message.chat.id, 'Поделитесь своим местоположением?', reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        state_info['getting_places'] = True
        latitude = message.location.latitude
        longitude = message.location.longitude

        send_places_list()

@bot.message_handler(content_types=['text'])
def answer_handler(message: Message):
    if message.text == 'Конечно! Отправляю свою геолокацию.':
        if message.location is None:
            bot.send_message(message.chat.id, 'Что-то не то, просто так геолокация не нужна.')
        else:
            print(message.location.latitude, message.location.longitude)
    elif message.text == 'Нет.':
        bot.send_message(message.chat.id, 'Жаль. В таком случае, ничем не могу помочь.')

def run_bot():
    if len(settings.load_settings().items()) == 0:
        settings.initialize_settings()

    bot.polling(none_stop=True, timeout=20)


def send_places_list():
    base_url = 'http://www.mapquestapi.com/search/v2/radius?key={}'.format(tokens[' = xurAgU3ftOkUyxAkxne0XteyCWBCsQfzw'])
    radius = '&radius={}wmin'.format(state_info['walk_minutes'])
    obj_count = '&maxMatches={}'
