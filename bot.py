import config # bot config
import settings # user settings

import requests
import configparser
import telebot
from telebot.types import (Message,
                            InlineKeyboardButton,
                            InlineKeyboardMarkup)


tokens = config.load_config()
bot = telebot.TeleBot(tokens['telegram-token'])


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
                '/go [count] - найти места в [count] минутах ходьбы']

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


def run_bot():
    if len(settings.load_settings().items()) == 0:
        settings.initialize_settings()

    bot.polling(none_stop=True, timeout=20)
