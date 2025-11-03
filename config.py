from configparser import ConfigParser
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parent

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def config(filename: str = f"{ROOT_DIR}/database.ini", section: str = "postgresql") -> dict:
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("Section {0} is not found in the {1} file.".format(section, filename))
    return db