#    Copyright 2025 Google LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

###############################################################################
# Note on python package & module structure 
# main.py is within the directory app
# because the directory app has a emtpy __init__.py file it is a Python package called "app"
# because of this, main.py is a "Python module" of "Python package" app. It is reffered to via app.main
#
# you can execute this module by running python -m app.main
###############################################################################

import datetime
import os
import uuid
from typing import List
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import Integer
from sqlalchemy import Date
from sqlalchemy import Boolean
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# fetch environment variables to tell SQLAlchemy where to find our DB
instanceid = os.environ["SPANNER_INSTANCE_ID"]
databaseid = os.environ["SPANNER_DATABASE_ID"]
projectid = os.environ["PROJECT_ID"]

# The start of any SQLAlchemy application is an object called the Engine. 
# This object acts as a central source of connections to a particular database
# echo=True instructs the Engine to log all of the SQL it emits to a Python logger that will write to sout
engine: Engine = create_engine(
    f"spanner+spanner:///projects/{projectid}/instances/{instanceid}/databases/{databaseid}",
    echo=True
)

# The DeclarativeBase class is used to generate a new base class 
# from which new classes to be mapped may inherit from
# The Declarative Base refers to a MetaData collection that is created for us automatically
# Base.metadata
class Base(DeclarativeBase):
    pass

# Create some tables in spanner based on these great examples
# https://github.com/googleapis/python-spanner-sqlalchemy/blob/main/samples/model.py

class Singer(Base):
    __tablename__ = "singers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(200), nullable=True)
    last_name: Mapped[str] = mapped_column(String(200), nullable=False)
    birthdate: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    albums: Mapped[List["Album"]] = relationship( back_populates="singer", cascade="all, delete-orphan" )
    concerts: Mapped[List["Concert"]] = relationship( back_populates="singer")

class Album(Base):
    __tablename__ = "albums"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    release_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    singer_id: Mapped[str] = mapped_column(ForeignKey("singers.id"))
    singer: Mapped["Singer"] = relationship(back_populates="albums")

class Concert(Base):
    __tablename__ = "concerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    venue_name: Mapped[str] = mapped_column(String(10), primary_key=True  )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    singer_id: Mapped[str] = mapped_column( String(36), ForeignKey("singers.id") )
    singer: Mapped["Singer"] = relationship(back_populates="concerts")

Base.metadata.create_all(engine)

# Write some data into these tables

with Session(engine) as session:
    singer = Singer(
        id=str(uuid.uuid4()),
        first_name="John",
        last_name="Smith",
        albums=[
            Album(
                id=str(uuid.uuid4()),
                title="Rainforest",
            ),
            Album(
                id=str(uuid.uuid4()),
                title="Butterflies",
            ),
        ],
    )
    concert = Concert(
        id=str(uuid.uuid4()),
        venue_name="O2Arena",
        title="the comeback tour",
        singer = singer
    )
    session.add(singer)
    session.add(concert)
    session.commit()