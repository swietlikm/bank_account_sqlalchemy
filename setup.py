import configparser
import pathlib
import sys
import sqlalchemy

SCRIPT_PATH = pathlib.Path(__file__).resolve().parent

CONFIG_FILE_NAME = "config.ini"
CONFIG_PATH = SCRIPT_PATH / CONFIG_FILE_NAME
DEFAULT_CONFIG = {
    "db_driver": "mysql",
    "db_name": "bank",
    "db_username": "",
    "db_password": "",
    "db_host": "localhost",
    "db_port": "3306",
}

config = configparser.ConfigParser()


def _create_raw_config_file() -> None:
    """
    Create raw config.ini file in the script directory if does not exists
    """
    config["Settings"] = DEFAULT_CONFIG
    try:
        CONFIG_PATH.touch()
        with open(CONFIG_PATH, "w", encoding="UTF-8") as configfile:
            config.write(configfile)
    except:
        pass

    # Output message to user
    print("--- Created config.ini file in the script directory")
    print("--- Please update the config.ini with the paths to the proper folders\n")
    input("--- PRESS ENTER TO EXIT ")
    sys.exit()


def _get_config_data() -> dict:
    """
    Read the config file and return the values for marposs and kogame.
    If the file doesn't exist, create a raw file and close the program.
    """
    config_data: dict = {}
    # Try to read config file. If file do not exists -> Create raw file and close the program
    try:
        with open(CONFIG_PATH, "r", encoding="UTF-8"):
            config.read(CONFIG_PATH)
        config_data = config["Settings"]
    except FileNotFoundError:
        print("config.ini not found")
        _create_raw_config_file()
    except configparser.Error:
        raise ValueError("Error in config.ini")
    if not config_data:
        raise ValueError("Error in config.ini")
    return config_data


def create_engine() -> None:
    config_data = _get_config_data()
    db_driver = config_data["db_driver"]
    db_name = config_data["db_name"]
    db_username = config_data["db_username"]
    db_password = config_data["db_password"]
    db_host = config_data["db_host"]
    db_port = config_data["db_port"]

    connection_string = (
        f"{db_driver}://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    return sqlalchemy.create_engine(connection_string)
