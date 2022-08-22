# sample/types.py
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
    f"cubrid+cubrid://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
)

from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

t1 = Table(
    "table1",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("data", String),
)

t1.create(engine)

from sqlalchemy_cubrid import VARCHAR

t2 = Table(
    "table2",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("data", VARCHAR),
)

t2.create(engine)
