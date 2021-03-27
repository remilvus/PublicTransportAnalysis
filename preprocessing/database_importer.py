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

    def create_table(self, tableName, myColList):
        sqlString = "CREATE TABLE " + tableName + " ("
        for colIdx in range(0, len(myColList)):
            sqlString += myColList[colIdx]
            if(colIdx != len(myColList) - 1):
                sqlString += ", "
        sqlString += ");"
        #self.con.execute(self, sqlString)
        return sqlString

    def insert_to_table(self, tableName, nameValuePairs):
        sqlString = "INSERT INTO " + tableName + " ("
        insertValues = " VALUES ("
        for nVP in range(0, len(nameValuePairs)):
            sqlString += nameValuePairs[nVP][0]
            insertValues += nameValuePairs[nVP][1]
            if(nVP != len(nameValuePairs)-1):
                sqlString += ", "
                insertValues += ", "
        sqlString += ")"
        insertValues += ");"
        sqlString += insertValues
        #self.con.execute(self, sqlString)
        return sqlString

connection = Connection()
toCreate = ["ID INT PRIMARY KEY NOT NULL", "SOMEPHRASE CHAR(50)"]
toInsert = [["ID", "1"], ["NAME", "PIOTR"]]
print(connection.create_table("MYTABLE", toCreate))
print(connection.insert_to_table("PEOPLE", toInsert))
connection.close()