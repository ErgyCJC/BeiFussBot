import config # bot config
import settings # user settings
import phrases

import requests
import random
import configparser
import telebot
from telebot.types import (Message,
                            InlineKeyboardButton,
                            InlineKeyboardMarkup,
                            KeyboardButton,
                            ReplyKeyboardMarkup)

"""
Объект с дополнительной информацией нужен, т.к. геолокацию
можно запросить только отдельным сообщением от пользователя
и требуется передать в обработчик геолокации информацию из сообщения-команды
"""
class GoCommandInfo:
    minutes = None
    obj_count = None

tokens = config.load_config()
bot = telebot.TeleBot(tokens['telegram-token'])

# {chat_id : go_command_info_obj}
go_info = dict()


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    """ Сообщение при старте бота """

    lines = ('Привет! Это бот для поиска интересных мест в шаговой доступности',
                '/tune - настройка интересов',
                '/go [count] - найти места в [count] минутах ходьбы')

    welcome_line = '\n'.join(lines)
    bot.send_message(message.chat.id, welcome_line)


@bot.message_handler(commands=['help'])
def help(message: Message):
    """ Сообщение на команду /help """

    commands = ('/tune - настройка интересов',
                '/go [minutes] <places> - найти <places> мест в [minutes] минутах ходьбы (кол-во мест не обязательно)')

    commands_line = '\n'.join(commands)
    bot.send_message(message.chat.id, commands_line)


@bot.message_handler(commands=['tune'])
def tune(message: Message):
    """ Настройка списка интересующих мест по команде /tune """

    # Набор кнопок, отождествляемых с категориями мест
    keyboard = InlineKeyboardMarkup()

    user_settings = settings.load_settings(section=str(message.chat.id))

    # Если настройки для данного chat.id ещё не инициализированы,
    # то записать их по умолчанию
    if len(list(user_settings)) == 0:
        settings.default_settings(section=message.chat.id)
        user_settings = settings.load_settings(section=str(message.chat.id))

    # Создание кнопок для каждой категории
    categories = user_settings.keys()
    for category in categories:
        button_text = category[:1].upper() + category[1:]
        callback_msg = category + ',' + str(message.chat.id)
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=callback_msg))

    bot.send_message(message.chat.id, RusPhrases.choose_places, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """ Обработка переключения отслеживания категории мест """

    if type(call.data) == type(str()):
        section_name = call.data.split(',')[1]
        user_settings = settings.load_settings(section=section_name)
        
        update_value = 'False'
        place_category = call.data.split(',')[0]
        if user_settings[place_category] == 'False':
            update_value = 'True'
        user_settings[place_category] = update_value

        storing_config = configparser.ConfigParser()
        storing_config[section_name] = user_settings
        with open('settings.config', 'w+') as storing_file:
            storing_config.write(storing_file)

        insertion = ''
        if user_settings[place_category] == 'False':
            insertion = RusPhrases.negative_prefix
        msg = RusPhrases.following.format(place_category[:1].upper(), place_category[1:], insertion)
        bot.send_message(call.message.chat.id, msg)


@bot.message_handler(commands=['go'])
def go(message: Message):
    """ Команда поиска мест """

    go_info[message.chat.id] = GoCommandInfo()

    # У команды нет аргументов
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, RusPhrases.go_cmd_no_args)
        return

    minutes_count = int(message.text.split()[1])
    go_info[message.chat.id].minutes = minutes_count

    # Максимальное кол-во позиций в выборке
    places_count = 15
    if len(message.text.split()) > 2:
        try:
            places_count = int(message.text.split()[2])
        except Exception:
            pass
    go_info[message.chat.id].obj_count = places_count

    # Клавиатура запроса геолокации
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton(text=RusPhrases.sending_geolocation, request_location=True))
    keyboard.add(KeyboardButton(text=RusPhrases.no_answer))
    last_msg = bot.send_message(message.chat.id, RusPhrases.geolocation_request, reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def location(message: Message):
    """ Получение широты и долготы из геолокации и запуск поиска мест """

    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude

        send_places_list(latitude, longitude, message)

@bot.message_handler(func=lambda x: True)
def answer_handler(message: Message):
    """ Обработка постороннних сообщений """

    bot.send_message(message.chat.id, RusPhrases.undefined_cmd)
    help(message)


def send_places_list(latitude, longitude, message:Message):
    """ Поиск и 'вывод' подходящих мест """

    # работа с Mapquest
    base_url = 'http://www.mapquestapi.com/search/v2/radius?key={}'.format(tokens['mapquest-key'])
    
    url_options = dict()
    url_options['radius'] = '&radius={}'.format(go_info[message.chat.id].minutes)
    url_options['units'] = '&units=wmin'
    url_options['obj_count'] = '&maxMatches={}'.format(go_info[message.chat.id].obj_count)
    url_options['origin'] = '&origin={},{}'.format(latitude, longitude)

    codes_config = configparser.ConfigParser()
    codes_file = 'places_codes.config'
    section = 'CODES'
    codes_config.read(codes_file)

    places = list()

    user_settings = settings.load_settings(section=str(message.chat.id))

    # Запрос по каждой категории мест
    for category, code in dict(codes_config[section]).items():
        # Категория не отслеживается для данного пользователя
        if user_settings[category] == 'False':
            continue

        code_option = '&hostedData=mqap.ntpois|group_sic_code=?|{}'.format(code)

        request_url = base_url + ''.join(url_options.values()) + code_option
        request = requests.get(request_url)
        data = dict(request.json())

        if 'searchResults' in data.keys():
            for place in data['searchResults']:
                places.append({'name' : place['name'], 'adress' : place['fields']['address']})

    random.shuffle(places)
    result_msg = ''
    
    # Ограничение кол-ва мест в выдаче и формирование текста сообщения
    for index in range(min(go_info[message.chat.id].obj_count, len(places))):
        place = places[index]
        result_msg += 'Название: {}\nАдрес: {}\n\n'.format(place['name'], place['adress'])

    if result_msg == '':
        result_msg = RusPhrases.no_places_found
    bot.send_message(message.chat.id, result_msg)


def run_bot():
    """ Запуск бота """

    bot.polling(none_stop=True, timeout=20)
