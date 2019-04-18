import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import configparser
import logging


def create_bot(cfg_file: str = 'settings.config', section: str = 'SETTINGS'):
    """ Загрузка ключей api и запуск бота """

    config = configparser.ConfigParser()
    config.read(cfg_file)
    
    telegram_token = config.get(section, 'telegram-token')
    mapquest_key = config.get(section, 'mapquest-key')

    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('tune', tune))
    dp.add_handler(CommandHandler('hide', hide_keyboard))

    updater.start_polling()
    updater.idle()


def start(bot, update):
    """ 'Приветствие' - сообщение после команды /start """

    lines = ['Привет! Это бот для поиска точек притяжения в шаговой доступности.',
                '/tune - настроить список предпочитаемых мест',
                '/get [min] - получить список мест в [min] минутах ходьбы']

    start_text = '\n'.join(lines)

    bot.message.reply_text(start_text)


def tune(bot, update):
    reply_keyboard = [['Всё'], ['Coffee Shops'], ['Кафе'], ['Рестораны'], ['Музеи'], ['Памятники'], ['Пляжи']]
    markup_keyboard = telegram.ReplyKeyboardMarkup(reply_keyboard)
    bot.message.reply_text("/hide - убрать список категорий", reply_markup=markup_keyboard)


def hide_keyboard(bot, update):
    pass