# sample/create_engine.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
import os
from os.path import join, dirname
from dotenv import load_dotenv
from sqlalchemy import create_engine


dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")
DBNAME = os.environ.get("DBNAME")

engine = create_engine(
    f"cubrid://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
)
connection = engine.connect()

try:
    result = connection.execute("select * from test_cubrid")

    for row in result:
        print(row)
finally:
    connection.close()
    engine.dispose()
