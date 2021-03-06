import configparser


def load_settings(file: str = 'settings.config', section: str = 'SETTINGS') -> dict:
    """ Возвращает словарь настроек из файла. Если нет данной секции - пустой словарь """
    
    settings = configparser.ConfigParser()
    settings.read(file)

    if section in settings.sections():
        return dict(settings[section])
    return dict()


def default_settings(settings_file: str = 'settings.config', section: str = 'SETTINGS') -> None:
    """ Установка стандартных полей и значений в настройках """
    
    settings = configparser.ConfigParser()

    default_keys = ['кафе',
                    'рестораны',
                    'памятники',
                    'музеи',
                    'библиотеки',
                    'ипподромы',
                    'парки развлечений',
                    'зоопарки']
    default_values = [False for x in range(len(default_keys))]
    settings[section] = dict(zip(default_keys, default_values))

    with open(settings_file, 'w+') as file:
        settings.write(file)
