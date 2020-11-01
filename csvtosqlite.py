import csv
import sqlite3


def _get_col_datatypes(fin):
    dr = csv.DictReader(fin) # comma is default delimiter
    fieldTypes = {}
    for entry in dr:
        feildslLeft = [f for f in dr.fieldnames if f not in fieldTypes.keys()]
        if not feildslLeft: break # We're done
        for field in feildslLeft:
            data = entry[field]

            # Need data to decide
            if len(data) == 0:
                continue

            if data.isdigit():
                fieldTypes[field] = "INTEGER"
            else:
                fieldTypes[field] = "TEXT"
        # TODO: Currently there's no support for DATE in sqllite

    if len(feildslLeft) > 0:
        raise Exception("Failed to find all the columns data types - Maybe some are empty?")

    return fieldTypes


def escapingGenerator(f):
    for line in f:
        yield line.encode("ascii", "xmlcharrefreplace").decode("ascii")


def csvToDb(csvFile,dbFile,tablename, outputToFile = False):

    # TODO: implement output to file

    with open(csvFile,mode='r', encoding="ISO-8859-1") as fin:
        dt = _get_col_datatypes(fin)

        fin.seek(0)

        reader = csv.DictReader(fin)

        # Keep the order of the columns name just as in the CSV
        fields = reader.fieldnames
        cols = []

        # Set field and type
        for f in fields:
            cols.append("\"%s\" %s" % (f, dt[f]))

        # Generate create table statement:
        stmt = "create table if not exists \"" + tablename + "\" (%s)" % ",".join(cols)
        print(stmt)
        con = sqlite3.connect(dbFile)
        cur = con.cursor()
        cur.execute(stmt)

        fin.seek(0)


        reader = csv.reader(escapingGenerator(fin))

        # Generate insert statement:
        stmt = "INSERT INTO \"" + tablename + "\" VALUES(%s);" % ','.join('?' * len(cols))

        cur.executemany(stmt, reader)
        con.commit()
        con.close()





csvToDb('data/category.csv', "db.sqlite3", 'api_Category')
