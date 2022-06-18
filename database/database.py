from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from .local_setting import db_lotto
from pathlib import Path
import logging
import os

logPath = r'D:\Learning\Python\LottoPrediction\log'
Path(logPath).mkdir(parents=True, exist_ok=True)
file1 = logPath + '\Db-Info.log'
file2 = logPath + '\Db-Debug.log'
if Path(file1).is_file():
    os.remove(file1)
if Path(file2).is_file():
    os.remove(file2)

formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
HandlerInfo = logging.FileHandler('log/Db-Info.log')
HandlerInfo.setLevel(logging.INFO)
HandlerInfo.setFormatter(formatter)

HandlerDebug = logging.FileHandler('log/Db-Debug.log')
HandlerDebug.setLevel(logging.DEBUG)
HandlerDebug.setFormatter(formatter)

Logger = logging.getLogger('sqlalchemy')
Logger.addHandler(HandlerInfo)
Logger.addHandler(HandlerDebug)
Logger.setLevel(logging.DEBUG)


def get_engine(user, password, host, port, db):
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    db_engine = create_engine(url)
    return db_engine


engine = get_engine(db_lotto["user"],
                    db_lotto["password"],
                    db_lotto["host"],
                    db_lotto["port"],
                    db_lotto["db"])

local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
