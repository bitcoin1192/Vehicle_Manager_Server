import sqlite3

def convertSQLRowsToDict(result:sqlite3.Cursor):
    listDictResult = []
    rowNumber = 0
    temp = result.fetchall()
    for row in temp:
        columnNumber = 0
        tempDictResult = dict()
        for columnName in result.description:
            tempDictResult[columnName[0]]= row[columnNumber]
            columnNumber += 1
        listDictResult.append(tempDictResult.copy())
        rowNumber += 1
    return listDictResult