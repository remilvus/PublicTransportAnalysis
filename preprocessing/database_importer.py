import sqlite3

from utilities.constants import RAW_DATA_PATH, DATABASE_PATH, ALERTS_DB_PATH, \
    GTFS_DB_PATH, UPDATES_DB_PATH, POSITIONS_DB_PATH

if not DATABASE_PATH.exists():
    DATABASE_PATH.mkdir()

con = sqlite3.connect(DATABASE_PATH.joinpath(UPDATES_DB_PATH))
con.close()
