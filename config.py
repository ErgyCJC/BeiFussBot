import configparser


def load_config(cfg_file: str = 'settings.config', section: str = 'TOKENS') -> dict:
    config = configparser.ConfigParser()
    config.read(cfg_file)
    return dict(config[section])