import configparser


def load_config(cfg_file: str = 'tokens.config', section: str = 'TOKENS') -> dict:
    """ Загрузка токенов из файла """

    config = configparser.ConfigParser()
    config.read(cfg_file)
    return dict(config[section])
