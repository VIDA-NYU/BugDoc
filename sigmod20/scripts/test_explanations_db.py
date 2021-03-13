from helpers import *
import psycopg2
import traceback


dbconf = {}
with open("../experiments/db.conf") as conffile:
    for line in conffile:
        name, var = line.partition("=")[::2]
        dbconf[name.strip()] = var.strip()

db = psycopg2.connect(dbname=dbconf['dbname'], user=dbconf['user'], password=dbconf['pass'])
cur = db.cursor()

sql = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
if exc(db, cur, sql):
    for row in cur:
        print(str(row))
cur.close()
db.close()