import sqlite3

from utilities.constants import RAW_DATA_PATH, DATABASE_PATH, ALERTS_DB_PATH, \
    GTFS_DB_PATH, UPDATES_DB_PATH, POSITIONS_DB_PATH

class Connection:
    def __init__(self):
        if not DATABASE_PATH.exists():
            DATABASE_PATH.mkdir()
        self.con = sqlite3.connect(str(DATABASE_PATH.joinpath(UPDATES_DB_PATH)))

    def close(self):
        self.con.close()


connection = Connection()
connection.close()