import configparser


def load_settings(file: str = 'settings.config', section: str = 'SETTINGS') -> dict:
    settings = configparser.ConfigParser()
    settings.read(file)

    if section in settings.sections():
        return dict(settings[section])
    return dict()


def initialize_settings(settings_file: str = 'settings.config', section: str = 'SETTINGS') -> None:
    settings = configparser.ConfigParser()

    default_keys = ['Кафе',
                    'Рестораны',
                    'Памятники',
                    'Музеи',
                    'Библиотеки',
                    'Ипподромы',
                    'Парки развлечений',
                    'Зоопарки']
    default_values = [False for x in range(len(default_keys))]
    settings[section] = dict(zip(default_keys, default_values))

    with open(settings_file, 'w+') as file:
        settings.write(file)