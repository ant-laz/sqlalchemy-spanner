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
# This file app/db/model.py is inside a sub-package, app/db/, so, it's a submodule: app.db.model
###############################################################################
import datetime
from typing import List
from sqlalchemy import Integer
from sqlalchemy import Date
from sqlalchemy import String
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# The DeclarativeBase class is used to generate a new base class 
# from which new classes to be mapped may inherit from
# The Declarative Base refers to a MetaData collection that is created for us automatically
# Base.metadata
class Base(DeclarativeBase):
    pass


# Define some tables in spanner based on these great examples
# https://github.com/googleapis/python-spanner-sqlalchemy/blob/main/samples/model.py
class Singer(Base):
    __tablename__ = "singers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(200), nullable=True)
    last_name: Mapped[str] = mapped_column(String(200), nullable=False)
    birthdate: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    albums: Mapped[List["Album"]] = relationship( back_populates="singer", cascade="all, delete-orphan" )

    def __repr__(self) -> str:
        return f"Singer(id={self.id!r}, first_name={self.first_name!r}, last_name={self.last_name!r})"

class Album(Base):
    __tablename__ = "albums"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    release_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    singer_id: Mapped[str] = mapped_column(ForeignKey("singers.id"))
    singer: Mapped["Singer"] = relationship(back_populates="albums")
    tracks: Mapped[List["Track"]] = relationship( back_populates="album")
    
    def __repr__(self) -> str:
        return f"Album(id={self.id!r}, title={self.title!r})"

class Track(Base):
    __tablename__ = "tracks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    track_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    album_id: Mapped[str] = mapped_column( String(36), ForeignKey("albums.id"))
    album: Mapped["Album"] = relationship(back_populates="tracks")

    def __repr__(self) -> str:
        return f"Track(id={self.id!r}, title={self.title!r}, track_number={self.track_number!r})"