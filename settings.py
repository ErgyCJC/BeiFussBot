import configparser


def load_settings(file: str = 'settings.py', section: str = 'SETTINGS'):
    settings = configparser.ConfigParser()
    setting.read()