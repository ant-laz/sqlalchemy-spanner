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

# fetch environment variables to tell SQLAlchemy where to find our DB
instanceid = os.environ["SPANNER_INSTANCE_ID"]
databaseid = os.environ["SPANNER_DATABASE_ID"]
projectid = os.environ["PROJECT_ID"]

import os
from sqlalchemy import (
    Table, Column, 
    Integer, Date, Boolean, Numeric, String, DateTime,
    Engine, create_engine, MetaData,
)

# The start of any SQLAlchemy application is an object called the Engine. 
# This object acts as a central source of connections to a particular database
# echo=True instructs the Engine to log all of the SQL it emits to a Python logger that will write to sout
engine: Engine = create_engine(
    f"spanner+spanner:///projects/{projectid}/instances/{instanceid}/databases/{databaseid}",
    echo=True
)

# Database metadata refers to objects that represnt Tables & Columns
# MetaData is a collection (e.g. py dict) that stores Tables
metadata: MetaData = MetaData()

asset = Table(
    "Asset",
    metadata,
    Column("AccountId", String(1024), primary_key=True),
    Column("CreatedDate", Date),
    Column("SystemModstamp", DateTime),
    Column("OBE_Duration_c", Numeric),
    Column("isDeleted", Boolean),
)

# Once we have a MetaData object, we can declare some Table objects
metadata.create_all(engine)