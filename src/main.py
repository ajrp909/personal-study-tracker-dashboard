import os
import psycopg2
from psycopg2 import sql
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TABLE_NAME = "question"
DATABASE_URL = os.environ['DATABASE_URL']
DB_CONN = f"{DATABASE_URL}"

table_name = TABLE_NAME
query = "select * from {} order by question_id;"
conn = psycopg2.connect(DB_CONN)
cur = conn.cursor()
cur.execute(sql.SQL(query).format(sql.Identifier(table_name)))
columns = [column[0] for column in cur.description]
rows = cur.fetchall()
cur.close()
conn.close()

df = pd.DataFrame(rows, columns=columns)

print