import config # bot config
import settings # user settings
import requests

import telebot
from telebot.types import Message


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
    pass


def run_bot():
    bot.polling()
