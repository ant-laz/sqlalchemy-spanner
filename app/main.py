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


import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.model import Base
from app.db.model import Singer
from app.db.model import Album
from app.db.model import Track
from app.db.model import Discography

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

def create_tables(engine: Engine):
    Base.metadata.create_all(engine)

def write_data_to_tables(engine: Engine):
    with Session(engine) as session:
        singer1 = Singer(
            id=str(uuid.uuid4()),
            first_name="Daft",
            last_name="Punk",
            albums=[
                Album(
                    id=str(uuid.uuid4()),
                    title="Random Access Memories",
                    tracks=[
                        Track(id=str(uuid.uuid4()), track_number=1, title="Give Life Back to Music"),
                        Track(id=str(uuid.uuid4()), track_number=2, title="The Game of Love"),
                    ]
                ),
                Album(
                    id=str(uuid.uuid4()),
                    title="Human After All",
                    tracks=[
                        Track(id=str(uuid.uuid4()), track_number=1, title="Human After All"),
                        Track(id=str(uuid.uuid4()), track_number=2, title="The prime Time of Your Life"),
                    ]
                ),
            ],
        )
        singer2 = Singer(
            id=str(uuid.uuid4()),
            first_name="George",
            last_name="Ezra",
            albums=[
                Album(
                    id=str(uuid.uuid4()),
                    title="Gold Rush Kid",
                    tracks=[
                        Track(id=str(uuid.uuid4()), track_number=1, title="Anyone for You (Tiger Lily)"),
                        Track(id=str(uuid.uuid4()), track_number=2, title="Green Green Grass"),
                    ]
                ),
                Album(
                    id=str(uuid.uuid4()),
                    title="Staying at Tamara's",
                    tracks=[
                        Track(id=str(uuid.uuid4()), track_number=1, title="Pretty Shining People"),
                        Track(id=str(uuid.uuid4()), track_number=2, title="Don't Matter Now"),
                    ]
                ),
            ],
        )

        session.add(singer1)
        session.add(singer2)

        session.commit()

def query_singer_album_tracks(engine: Engine):
    stmt = (
        select(Singer)
        .join(Singer.albums)
        .join(Album.tracks)
        .add_columns(Album, Track)
    )
    with Session(engine) as session:
        for row in session.execute(stmt):
            print(row)

def create_view_singer_album_tracks(engine: Engine):
    view_definition = (
    "CREATE OR REPLACE VIEW discography "
    "SQL SECURITY INVOKER " 
    "AS SELECT "
    "singers.id as singer_id, "
    "singers.first_name, "
    "singers.last_name, "
    "singers.birthdate, "
    "albums.id AS album_id, "
    "albums.title AS album_title, "
    "albums.release_date, "
    "tracks.id AS track_id, "
    "tracks.track_number, "
    "tracks.title AS track_title, "
    "FROM "
    "singers "
    "JOIN albums "
    "ON singers.id = albums.singer_id "
    "JOIN tracks "
    "ON albums.id = tracks.album_id; "
    )
    with engine.connect() as conn:
        conn.execute(text(view_definition))
        conn.commit()

def read_view_singer_album_tracks(engine: Engine):
    stmt = (
        select(Discography)
    )
    with Session(engine) as session:
        for row in session.execute(stmt):
            print(row)

#create_tables(engine)
#write_data_to_tables(engine)
#query_singer_album_tracks(engine)
create_view_singer_album_tracks(engine)
#read_view_singer_album_tracks(engine)